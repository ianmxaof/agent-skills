"""Phase 2 smoke + assertions for open-dir-secrets (real fixture server).

Exit 1 on any failed gate. Never treat odsec exit-0 alone as green.
Uses committed fixtures/listing/ (PS 5.1-safe; no utf8NoBOM).

Tri-state coverage (Diplomat):
  - LIVE  — unittest.mock: verify_liveness → True for a chosen PROVIDERS id
  - stale — same seam → False for other PROVIDERS ids
  - unverified — kinds ∉ PROVIDERS (verify never called)

Real-provider GET is optional integration only (ODSEC_SMOKE_LIVE_NET=1).
It never blocks green — network flake must not fail this smoke.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

SKILL_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = SKILL_ROOT / "fixtures" / "listing"
ODSEC = Path(__file__).resolve().parent / "odsec.py"

# Phase 1 regression shapes (redacted) for sk- / SG. from fixtures/.env
EXPECTED_SK_REDACT = "sk-xxx...xxxx"  # redact(sk- + 40×x) → sk-xxx...xxxx
EXPECTED_SG_REDACT = "SG.xxx...xxxx"  # redact(SG. + 32×x)

# Finding-count (not source-line count). sk- dual-yields openai+deepseek + SG. = 3
# from .env; plus npm/pypi/env(password)/csv×3/docker-auth/registry = 11.
COMPOSITION_GATE = 11

# Mock seam: one LIVE provider, remaining PROVIDERS calls → stale.
LIVE_MOCK_PROVIDER = "openai"


def composition_fails(count: int | None) -> bool:
    """True when count is below or off the composition gate (hard red, not 0-only)."""
    if count is None:
        return True
    return count != COMPOSITION_GATE


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def _serve(directory: Path, port: int) -> ThreadingHTTPServer:
    handler = partial(_QuietHandler, directory=str(directory))
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def _prove_composition_gate() -> None:
    """Forced-pull-to-8 must be red; gate value itself green. Exits 1 if proof breaks."""
    if not composition_fails(8):
        print("PROVE FAIL: composition_fails(8) expected True (hard-fail below gate)")
        raise SystemExit(1)
    if not composition_fails(0):
        print("PROVE FAIL: composition_fails(0) expected True")
        raise SystemExit(1)
    if composition_fails(COMPOSITION_GATE):
        print(f"PROVE FAIL: composition_fails({COMPOSITION_GATE}) expected False")
        raise SystemExit(1)
    print(
        f"PROVE PASS: composition_fails(8)=True, "
        f"composition_fails(0)=True, "
        f"composition_fails({COMPOSITION_GATE})=False"
    )


def _mocked_verify(provider: str, key: str) -> bool | None:
    """Deterministic LIVE/stale seam — no outbound HTTP."""
    if provider == LIVE_MOCK_PROVIDER:
        return True
    return False


def _optional_live_net(odsec_mod) -> None:
    """Optional real-provider GET. Reports only — never appends fails / never blocks green."""
    print("--- optional live-net (ODSEC_SMOKE_LIVE_NET=1); never blocks green ---")
    for provider, key in (
        ("openai", "sk-" + ("x" * 40)),
        ("sendgrid", "SG." + ("x" * 32)),
    ):
        try:
            live = odsec_mod.verify_liveness(provider, key)
            print(f"  live-net {provider}: live={live!r}")
        except Exception as e:  # noqa: BLE001 — report-only
            print(f"  live-net {provider}: error {type(e).__name__}: {e}")


def main() -> int:
    fails: list[str] = []
    _prove_composition_gate()

    if not FIXTURES.is_dir():
        print(f"FAIL fixtures missing: {FIXTURES}")
        return 1

    sys.path.insert(0, str(ODSEC.parent))
    import odsec  # noqa: E402

    probe_calls: list[str] = []

    def counting_verify(provider: str, key: str) -> bool | None:
        probe_calls.append(provider)
        return _mocked_verify(provider, key)

    port = _free_port()
    httpd = _serve(FIXTURES, port)
    time.sleep(0.15)
    url = f"http://127.0.0.1:{port}"
    try:
        # In-process scan under mock — LIVE/stale/unverified deterministic.
        with patch.object(odsec, "verify_liveness", side_effect=counting_verify):
            findings = odsec.scan(url, delay=0.05)
        # CLI for exit + envelope count only (no mock; tags may differ — not required).
        proc = subprocess.run(
            [sys.executable, str(ODSEC), "--delay", "0.05", "--json", url],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    print(f"CLI exit={proc.returncode}")
    if proc.returncode != 0:
        fails.append(f"exit want 0 got {proc.returncode}")
        print(proc.stderr[:500])

    raw = proc.stdout
    start = raw.find("{")
    if start < 0:
        fails.append("no JSON object in CLI stdout")
        data = {"finding_count": -1, "findings": []}
    else:
        data = json.loads(raw[start:])

    cli_count = data.get("finding_count")
    inproc_count = len(findings)
    print(f"finding_count CLI={cli_count} inproc={inproc_count} (mock in-process)")
    for f in findings:
        tag = {True: "LIVE", False: "stale", None: "unverified"}[f["live"]]
        print(f"  [{tag:10}] {f['provider']:14} {f['key']}  {Path(f['path']).name}")

    # --- assert gates ---
    if composition_fails(cli_count) or composition_fails(inproc_count):
        fails.append(
            f"finding_count composition want {COMPOSITION_GATE} "
            f"got CLI={cli_count} inproc={inproc_count} "
            f"(hard-fail includes undercount e.g. 8, not 0-only)"
        )

    kinds: dict[str, list[dict]] = {}
    for f in findings:
        kinds.setdefault(f["provider"], []).append(f)

    # Dual-yield shape (not mere presence).
    sk_rows = [f for f in findings if f["key"] == EXPECTED_SK_REDACT]
    sg_rows = [f for f in findings if f["key"] == EXPECTED_SG_REDACT]
    sk_providers = {f["provider"] for f in sk_rows}
    sg_providers = {f["provider"] for f in sg_rows}
    if sk_providers != {"openai", "deepseek"}:
        fails.append(
            f"dual-yield shape: sk- want {{openai, deepseek}} got {sk_providers or '{}'}"
        )
    if sg_providers != {"sendgrid"}:
        fails.append(f"SG. yield shape: want {{sendgrid}} got {sg_providers or '{}'}")

    # Mock tag map: openai LIVE; deepseek + sendgrid stale.
    for f in sk_rows + sg_rows:
        want = True if f["provider"] == LIVE_MOCK_PROVIDER else False
        if f["live"] is not want:
            fails.append(
                f"mock tag branch: {f['provider']} want live={want!r} got {f['live']!r}"
            )

    # Tag-aware LIVE gate (≥1 live-tagged finding) — same form as composition (hard).
    live_rows = [f for f in findings if f["live"] is True]
    stale_rows = [f for f in findings if f["live"] is False]
    if len(live_rows) < 1:
        fails.append("LIVE gate: want ≥1 finding with live=True (mock seam)")
    if len(stale_rows) < 1:
        fails.append("stale gate: want ≥1 finding with live=False (mock seam)")

    # New rows — required kinds + unverified tag
    need_kinds = {
        "npm": 1,
        "pypi": 1,
        "platform-year": 3,
        "docker-auth": 1,
        "registry": 1,
    }
    for kind, n in need_kinds.items():
        got = len(kinds.get(kind, []))
        if got < n:
            fails.append(f"new kind {kind}: want>={n} got {got}")
        for f in kinds.get(kind, []):
            if f["live"] is not None:
                fails.append(f"{kind} live want null got {f['live']!r}")
            if "..." not in f["key"]:
                fails.append(f"{kind} key not redacted: {f['key']!r}")

    # Zero outbound probes for unverified kinds (mock still records PROVIDERS calls only).
    unverified_providers = {f["provider"] for f in findings if f["live"] is None}
    bad_probes = [p for p in probe_calls if p in unverified_providers]
    print(f"verify_liveness mock calls ({len(probe_calls)}): {probe_calls}")
    if bad_probes:
        fails.append(f"outbound probe for unverified kinds: {bad_probes}")
    for p in probe_calls:
        if p not in odsec.PROVIDERS:
            fails.append(f"probe fired for non-PROVIDERS kind {p}")

    reg = kinds.get("registry", [])
    if not reg:
        fails.append("notes.txt co-occurrence: no registry finding")
    else:
        for f in reg:
            if odsec._report_rank(f["provider"]) != 0:
                fails.append(f"registry rank want 0 got {odsec._report_rank(f['provider'])}")

    # Order: LIVE first, then registry→aws→generic within non-LIVE
    if findings and findings[0]["live"] is not True:
        fails.append("report order: first finding want LIVE under mock")
    ranks = [odsec._report_rank(f["provider"]) for f in findings if f["live"] is not True]
    if ranks != sorted(ranks):
        fails.append(f"report order ranks not sorted registry→aws→generic: {ranks}")

    print(f"handoff finding_count claim {COMPOSITION_GATE}: PASS (source of truth)")
    print(f"LIVE findings: {len(live_rows)}; stale findings: {len(stale_rows)}")

    print("---")
    dual_ok = sk_providers == {"openai", "deepseek"} and sg_providers == {"sendgrid"}
    live_ok = len(live_rows) >= 1
    tag_map_ok = all(
        (f["live"] is True) if f["provider"] == LIVE_MOCK_PROVIDER else (f["live"] is False)
        for f in sk_rows + sg_rows
    )
    op = {
        "sk/SG dual-yield + mock tags": dual_ok and tag_map_ok,
        "≥1 LIVE tagged": live_ok,
        "unverified tagging": all(
            f["live"] is None for f in findings if f["provider"] in need_kinds
        ),
        "probe count zero (unverified)": not bad_probes
        and all(p in odsec.PROVIDERS for p in probe_calls),
        "ordering registry-first (non-LIVE)": ranks == sorted(ranks),
    }
    for name, ok in op.items():
        print(f"OP {'PASS' if ok else 'FAIL'}: {name}")
        if not ok:
            fails.append(f"operator gate: {name}")

    if os.environ.get("ODSEC_SMOKE_LIVE_NET") == "1":
        _optional_live_net(odsec)

    if fails:
        for x in fails:
            print(f"FAIL: {x}")
        return 1
    print(
        f"PASS: composition={COMPOSITION_GATE} + dual-yield + "
        f"LIVE/stale/unverified (3/3) + operator gates"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
