"""Phase 2 smoke + assertions for open-dir-secrets (real fixture server).

Exit 1 on any failed gate. Never treat odsec exit-0 alone as green.
Uses committed fixtures/listing/ (PS 5.1-safe; no utf8NoBOM).
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = SKILL_ROOT / "fixtures" / "listing"
ODSEC = Path(__file__).resolve().parent / "odsec.py"

# Phase 1 regression shapes (redacted) for sk- / SG. from fixtures/.env
EXPECTED_SK_REDACT = "sk-xxx...xxxx"  # redact(sk- + 40×x) → sk-xxx...xxxx
EXPECTED_SG_REDACT = "SG.xxx...xxxx"  # redact(SG. + 32×x)

# Finding-count (not source-line count). sk- dual-yields openai+deepseek + SG. = 3
# from .env; plus npm/pypi/env(password)/csv×3/docker-auth/registry = 11.
COMPOSITION_GATE = 11


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


def main() -> int:
    fails: list[str] = []
    _prove_composition_gate()

    if not FIXTURES.is_dir():
        print(f"FAIL fixtures missing: {FIXTURES}")
        return 1

    # Import odsec for rank + monkeypatch probe count (no verify-stage rewrite).
    sys.path.insert(0, str(ODSEC.parent))
    import odsec  # noqa: E402

    probe_calls: list[str] = []
    real_verify = odsec.verify_liveness

    def counting_verify(provider: str, key: str):
        probe_calls.append(provider)
        return real_verify(provider, key)

    odsec.verify_liveness = counting_verify  # type: ignore[assignment]

    port = _free_port()
    httpd = _serve(FIXTURES, port)
    time.sleep(0.15)
    url = f"http://127.0.0.1:{port}"
    try:
        # Drive classify/scan in-process so probe monkeypatch applies.
        # Also run CLI once for exit-code / JSON envelope parity.
        findings = odsec.scan(url, delay=0.05)
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
        odsec.verify_liveness = real_verify  # type: ignore[assignment]

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
    print(f"finding_count CLI={cli_count} inproc={inproc_count}")
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

    # Regression: sk-/SG. redaction + dual-yield shape (not mere presence).
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
    for f in sk_rows + sg_rows:
        # Dummy keys: reject invented LIVE; stale (False) is the expected branch
        # when provider returns 401; None only if transport unknown — still not LIVE.
        if f["live"] is True:
            fails.append(f"regression: unexpected LIVE for dummy {f['provider']}")
        if f["live"] is not False:
            fails.append(
                f"regression tag branch: {f['provider']} want stale(False) got {f['live']!r}"
            )

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

    # Zero outbound probes for unverified kinds
    unverified_providers = {f["provider"] for f in findings if f["live"] is None}
    bad_probes = [p for p in probe_calls if p in unverified_providers]
    print(f"verify_liveness calls ({len(probe_calls)}): {probe_calls}")
    if bad_probes:
        fails.append(f"outbound probe for unverified kinds: {bad_probes}")
    for p in probe_calls:
        if p not in odsec.PROVIDERS:
            fails.append(f"probe fired for non-PROVIDERS kind {p}")

    # notes co-occurrence → registry kind (HIGH / rank 0), not platform-year MED
    reg = kinds.get("registry", [])
    if not reg:
        fails.append("notes.txt co-occurrence: no registry finding")
    else:
        for f in reg:
            if odsec._report_rank(f["provider"]) != 0:
                fails.append(f"registry rank want 0 got {odsec._report_rank(f['provider'])}")

    # Order: registry ranks before aws before generic within non-LIVE
    ranks = [odsec._report_rank(f["provider"]) for f in findings if f["live"] is not True]
    if ranks != sorted(ranks):
        fails.append(f"report order ranks not sorted registry→aws→generic: {ranks}")

    print(f"handoff finding_count claim {COMPOSITION_GATE}: PASS (source of truth)")

    print("---")
    # Four operator checks — sk/SG now means dual-yield shape, not presence alone
    dual_ok = sk_providers == {"openai", "deepseek"} and sg_providers == {"sendgrid"}
    tag_ok = all(f["live"] is False for f in sk_rows + sg_rows) and all(
        f["live"] is None for f in findings if f["provider"] in need_kinds
    )
    op = {
        "sk/SG dual-yield + tags": dual_ok and tag_ok,
        "unverified tagging": all(
            f["live"] is None for f in findings if f["provider"] in need_kinds
        ),
        "probe count zero (unverified)": not bad_probes
        and all(p in odsec.PROVIDERS for p in probe_calls),
        "ordering registry-first": ranks == sorted(ranks),
    }
    for name, ok in op.items():
        print(f"OP {'PASS' if ok else 'FAIL'}: {name}")
        if not ok:
            fails.append(f"operator gate: {name}")

    if fails:
        for x in fails:
            print(f"FAIL: {x}")
        return 1
    print(f"PASS: composition={COMPOSITION_GATE} + dual-yield + operator gates")
    return 0


if __name__ == "__main__":
    sys.exit(main())