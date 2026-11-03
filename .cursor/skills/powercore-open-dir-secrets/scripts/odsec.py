"""odsec - open-dir-secrets: detect and verify credential exposures in open directory listings.

Read-only recon: GET requests only. Probes a host for open directory
listings, inventories config/secret files, classifies keys by provider
prefix, verifies each on the provider's cheapest auth endpoint.
Full key values exist only in memory for the verify call; everything
stored, logged, or printed is redacted.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

VERSION = "0.3"

PROVIDERS = {
    "openai": ("sk-", "https://api.openai.com/v1/models"),
    "deepseek": ("sk-", "https://api.deepseek.com/v1/models"),
    "groq": ("gsk_", "https://api.groq.com/openai/v1/models"),
    "anthropic": ("sk-ant-", "https://api.anthropic.com/v1/models"),
    "stripe": ("sk_live_", "https://api.stripe.com/v1/balance"),
    "firecrawl": ("fc-", "https://api.firecrawl.dev/v1/team/credit-usage"),
    "resend": ("re_", "https://api.resend.com/domains"),
    # Maverick: sendgrid row locked as Artifact 1 — 403 → unverified (other). See POWERCORE_LOG.
    "sendgrid": ("SG.", "https://api.sendgrid.com/v3/scopes"),
    "openrouter": ("sk-or-v1-", "https://openrouter.ai/api/v1/models"),
    "gemini": ("AIza", "https://generativelanguage.googleapis.com/v1beta/models"),
}

ENV_PATTERNS = [
    rb"(?:DB_|MYSQL_|REDIS_|AWS_|S3_|MAIL_|STRIPE_|PAYMENT_|CASINO_)[A-Z_]+[ \t]*=[ \t]*([^\s\"']{8,})",
    rb"(?:password|secret|api_?key|token)[ \t]*[:=][ \t]*[\"']?([A-Za-z0-9_\-.+/]{12,})",
    rb"APP_KEY[ \t]*=[ \t]*base64:([A-Za-z0-9+/=]{32,})",
    rb"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----[\s\S]{40,}?-----END [A-Z ]*PRIVATE KEY-----",
]

# Phase 2 pattern table v2 — (kind, pattern). Same classify yield shape as
# PROVIDERS/ENV: (label, value). Kinds are NOT in PROVIDERS → unverified, no probe.
# Capture group = secret when the match is wider than the token itself.
# Rank for report: registry/package (0) > aws (1) > generic (2).
IDENTIFY_PATTERNS_V2: list[tuple[str, bytes]] = [
    ("basic-auth", rb"(?i)\b([A-Za-z0-9_.-]{2,32}:[A-Za-z0-9+/=]{40,})\b"),
    ("npm", rb"(?i)\b_?authToken[=:]\s*[\"']?([A-Za-z0-9_-]{30,})"),
    ("pypi", rb"(pypi-[A-Za-z0-9\-_]{60,})"),
    ("docker", rb"(dckr_pat_[A-Za-z0-9\-_]{30,})"),
    ("github", rb"(ghp_[A-Za-z0-9]{40,})"),
    # ghcr_ dropped — no such prefix; GHCR push uses ghp_ / github_pat_.
    ("github", rb"(github_pat_[A-Za-z0-9_]{50,})"),
    (
        "registry",
        rb"(?im)(?:artifactory|nexus|harbor|registry)[^\r\n]{0,120}([A-Za-z0-9+/]{44,})",
    ),
    ("docker-auth", rb"\"auth\"\s*:\s*\"([A-Za-z0-9+/=]{40,})\""),
    ("aws", rb"\b((?:AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16})\b"),
    (
        # \r?$ — Windows fixture CRLF must not leave a dangling CR before $.
        "platform-year",
        rb"(?im)^([^,\r\n]{1,64},(?:aws|vault|jira|nexus|artifactory|github|gitlab|jenkins|dso)\d{2,4})\r?$",
    ),
]

_REGISTRY_KINDS = frozenset(
    {"basic-auth", "npm", "pypi", "docker", "github", "registry", "docker-auth"}
)

PROBE_PATHS = [
    "/",
    "/.well-known/",
    "/backup/",
    "/backups/",
    "/.git/",
    "/config/",
    "/storage/",
    "/secrets/",
    "/db/",
    "/dump/",
    "/database/",
    "/.env",
    "/.env.bak",
    "/config.php.bak",
]

LISTING_MARKERS = (
    b"Index of /",
    b"[To Parent Directory]",
    b"Parent Directory",
    b"<title>Directory listing",
    b"Directory listing for",
)
# Maverick: dropped bare `xxxx` — it blocked prefix+x-fill smoke dummies. See POWERCORE_LOG.
PLACEHOLDER = re.compile(rb"YOUR_|changeme|placeholder|example|TODO", re.I)
# Phase 2: .npmrc / .pypirc inventory; csv for platform-year creds rows.
FILE_EXT = re.compile(
    r"\.(env|json|ya?ml|txt|pem|cfg|ini|bak|sql|php|dist|npmrc|pypirc|csv)$",
    re.I,
)
HREF = re.compile(r'href="([^"?]+)"')
# Dot is intentional — spans SendGrid SG.<segment>.<segment> tokens.
_TOKEN_CHARS = re.compile(rb"[A-Za-z0-9_.\-]+")

UA = f"odsec/{VERSION} (+powercore; read-only)"
DELAY = 0.3
MAX_FILES = 40


@dataclass(frozen=True)
class _Resp:
    status_code: int
    content: bytes

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")


def _http_get(url: str, *, headers: dict[str, str] | None = None, timeout: float = 10.0) -> _Resp:
    """GET-only transport (stdlib). Raises URLError/OSError on network failure."""
    hdrs = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return _Resp(int(resp.status), resp.read())
    except urllib.error.HTTPError as e:
        body = b""
        try:
            body = e.read()
        except OSError:
            body = b""
        return _Resp(int(e.code), body)


def is_listing(resp: _Resp) -> bool:
    if resp.status_code != 200:
        return False
    head = resp.content[:8192]
    if any(m in head for m in LISTING_MARKERS):
        return True
    return (
        len(
            re.findall(
                rb'<a\s+href="[^"?]+\.(?:env|json|ya?ml|txt|pem|cfg|ini|bak|sql)"',
                head,
                re.I,
            )
        )
        >= 2
    )


def inventory(html: str, base: str, cap: int) -> list[str]:
    out: list[str] = []
    for href in HREF.findall(html):
        if href.endswith("/") or href.startswith(("?", "#", "javascript:", "mailto:")):
            continue
        if FILE_EXT.search(href) or "." not in href:
            # Maverick: do not use str.lstrip("./") — that strips ALL leading dots
            # and turns ".env" into "env". Trim only an optional "./" prefix.
            rel = href[2:] if href.startswith("./") else href
            out.append(base.rstrip("/") + "/" + rel.lstrip("/"))
        if len(out) >= cap:
            break
    return out


def classify(body: bytes):
    # A bare "sk-" string is tested against every provider sharing the
    # prefix on purpose - verify_liveness disambiguates openai vs deepseek.
    for provider, (prefix, _) in PROVIDERS.items():
        pref = prefix.encode()
        for m in _TOKEN_CHARS.findall(body):
            if len(m) < len(pref):
                continue
            if m.startswith(pref) and not PLACEHOLDER.search(m):
                yield provider, m.decode()
    for pat in ENV_PATTERNS:
        for m in re.findall(pat, body):
            val = m.decode(errors="ignore") if isinstance(m, bytes) else m
            if val and not PLACEHOLDER.search(val.encode()):
                yield "env", val
    for kind, pat in IDENTIFY_PATTERNS_V2:
        for m in re.findall(pat, body):
            val = m.decode(errors="ignore") if isinstance(m, (bytes, bytearray)) else m
            if isinstance(val, tuple):
                val = next((x for x in val if x), "")
                if isinstance(val, (bytes, bytearray)):
                    val = val.decode(errors="ignore")
            if val and not PLACEHOLDER.search(val.encode()):
                yield kind, val


def _report_rank(provider: str) -> int:
    """registry/package (0) > aws (1) > generic / PROVIDERS / env (2)."""
    if provider in _REGISTRY_KINDS:
        return 0
    if provider == "aws":
        return 1
    return 2


def _sort_findings(findings: list[dict]) -> list[dict]:
    # LIVE first (existing), then registry > aws > generic within each live bucket.
    return sorted(
        findings,
        key=lambda x: (x["live"] is not True, _report_rank(x["provider"]), x["provider"]),
    )


def _auth_headers(provider: str, key: str) -> dict[str, str]:
    if provider == "anthropic":
        return {"x-api-key": key, "anthropic-version": "2023-06-01"}
    if provider == "gemini":
        return {}
    return {"Authorization": f"Bearer {key}"}


def verify_liveness(provider: str, key: str) -> bool | None:
    """True = authenticates, False = rejected (401), None = unknown/unsupported."""
    if provider not in PROVIDERS:
        return None
    _, url = PROVIDERS[provider]
    headers = _auth_headers(provider, key)
    if provider == "gemini":
        url = f"{url}?key={key}"
    try:
        r = _http_get(url, headers=headers, timeout=8.0)
    except (urllib.error.URLError, OSError):
        return None
    if r.status_code == 200:
        return True
    if r.status_code == 401:
        return False
    return None


def redact(v: str) -> str:
    if len(v) <= 12:
        return v[:3] + "..."
    return v[:6] + "..." + v[-4:]


def scan(host: str, max_files: int = MAX_FILES, delay: float = DELAY) -> list[dict]:
    host = host.rstrip("/")
    findings: list[dict] = []
    seen: set[str] = set()
    for path in PROBE_PATHS:
        try:
            r = _http_get(host + path, timeout=10.0)
        except (urllib.error.URLError, OSError):
            continue
        if not is_listing(r):
            continue
        for f in inventory(r.text, host + path, max_files):
            if f in seen:
                continue
            seen.add(f)
            time.sleep(delay)
            try:
                body = _http_get(f, timeout=10.0).content
            except (urllib.error.URLError, OSError):
                continue
            for provider, key in classify(body):
                # No PROVIDERS row → unverified; skip verify (no outbound probe).
                live = (
                    verify_liveness(provider, key) if provider in PROVIDERS else None
                )
                findings.append(
                    {
                        "path": f,
                        "provider": provider,
                        "key": redact(key),
                        "live": live,
                    }
                )
    return _sort_findings(findings)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Detect and verify credential exposures in open directory listings"
    )
    ap.add_argument("host", help="base URL, e.g. https://example.com")
    ap.add_argument("--max-files", type=int, default=MAX_FILES)
    ap.add_argument("--delay", type=float, default=DELAY)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args(argv)

    found = scan(a.host, a.max_files, a.delay)
    if a.json:
        # Peer envelope: ok + version + url + payload (feature-scan / website-clone).
        out = {
            "ok": True,
            "version": VERSION,
            "url": a.host.rstrip("/"),
            "finding_count": len(found),
            "findings": found,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
    elif not found:
        print("no findings")
    else:
        for f in found:  # already registry > aws > generic via _sort_findings
            tag = {True: "LIVE", False: "stale", None: "unverified"}[f["live"]]
            print(f"[{tag:10}] {f['provider']:11} {f['key']}  {f['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
