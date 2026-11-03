#!/usr/bin/env python3
"""Operator CLI hub — dispatch to registered skill scripts.

Do not name this file operator.py — it shadows the stdlib operator module.

Capability-bus v0: `registry.json` (next to this file) is the machine-readable
skill list `list` reads from. Two skill statuses:
  - live: this hub runs the skill's own script directly (semantic-scan, wifi).
  - delegate: forwarded as-is to tbcc_cli.py, which already owns that
    engine (research / llm / slots) — this hub does not reimplement them,
    just adds one discoverable entry point.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = Path(__file__).resolve().parent / "registry.json"
SEMANTIC_SCAN = SKILLS_ROOT / "semantic-deception-detector" / "scripts" / "semantic_scan.py"
REPO_TRUST = SKILLS_ROOT / "powercore-repo-trust" / "scripts" / "repo_trust.py"

_DEFAULT_TBCC_REPO_ROOT = Path(r"C:\Powercore-repo-main\telegram_bot2")

_DELEGATE_COMMANDS = {"research", "llm", "slots"}
_WIFI_ACTIONS = {"focus", "restore", "status"}


def _tbcc_repo_root() -> Path:
    override = (os.environ.get("TBCC_REPO_ROOT") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    if _DEFAULT_TBCC_REPO_ROOT.is_dir():
        return _DEFAULT_TBCC_REPO_ROOT.resolve()
    cwd = Path.cwd()
    for parent in (cwd, *cwd.parents):
        if (parent / "tbcc" / "backend" / "scripts" / "tbcc_cli.py").is_file():
            return parent.resolve()
    return _DEFAULT_TBCC_REPO_ROOT.resolve()


def _tbcc_cli_paths() -> tuple[Path, Path]:
    root = _tbcc_repo_root()
    backend = root / "tbcc" / "backend"
    return backend, backend / "scripts" / "tbcc_cli.py"


def _load_registry() -> list[dict]:
    if not REGISTRY_PATH.is_file():
        return []
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"registry.json unreadable: {e}", file=sys.stderr)
        return []
    return data.get("skills", [])


def _run_script(script: Path, argv: list[str]) -> int:
    if not script.is_file():
        print(f"Missing skill script: {script}", file=sys.stderr)
        return 2
    proc = subprocess.run([sys.executable, str(script), *argv], check=False)
    return int(proc.returncode)


def _wifi_script() -> Path:
    return _tbcc_repo_root() / "tbcc" / "tools" / "wifi-focus.ps1"


def _run_powershell(script: Path, argv: list[str]) -> int:
    if not script.is_file():
        print(f"Missing script: {script}", file=sys.stderr)
        return 2
    system_root = os.environ.get("SystemRoot") or r"C:\Windows"
    ps = Path(system_root) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    exe = str(ps) if ps.is_file() else "powershell"
    proc = subprocess.run(
        [exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), *argv],
        check=False,
    )
    return int(proc.returncode)


def _delegate_to_tbcc_cli(subcommand: str, argv: list[str]) -> int:
    backend, cli = _tbcc_cli_paths()
    if not cli.is_file():
        print(
            f"Missing tbcc_cli.py: {cli} (set TBCC_REPO_ROOT to your telegram_bot2 checkout)",
            file=sys.stderr,
        )
        return 2
    proc = subprocess.run(["py", "-3.13", str(cli), subcommand, *argv], check=False, cwd=str(backend))
    return int(proc.returncode)


def cmd_list(_args: argparse.Namespace) -> int:
    skills = _load_registry()
    if not skills:
        print("No skills registered (registry.json missing or empty).", file=sys.stderr)
        return 1
    for s in skills:
        print(f"{s.get('id', '?'):<16} [{s.get('status', '?'):<8}] {s.get('description', '')}")
        print(f"  entry: {s.get('entry', '')}")
        for c in s.get("corpora") or []:
            print(f"  corpus: {c}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="operator", description="Operator skills CLI")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List registered skills (from registry.json)")

    sem = sub.add_parser("semantic-scan", help="Semantic deception scan (path or URL)")
    sem.add_argument("target", nargs="?", default=".", help="Local path or URL")
    sem.add_argument("--json", action="store_true")
    sem.add_argument("--max-files", type=int, default=400)
    sem.add_argument("--max-bytes", type=int, default=512_000)
    sem.add_argument("--ask", default=None, help="Question-aware claim ledger verify")
    sem.add_argument("--no-readme-claims", action="store_true")
    sem.add_argument("--self-test", action="store_true")

    trust = sub.add_parser("repo-trust", help="Repo trust triage (semantic + install/workflow heuristics)")
    trust.add_argument("target", nargs="?", default=".", help="Local path or URL")
    trust.add_argument("--json", action="store_true")
    trust.add_argument("--max-files", type=int, default=400)
    trust.add_argument("--max-bytes", type=int, default=512_000)
    trust.add_argument("--ask", default=None, help="Question-aware claim ledger verify")
    trust.add_argument("--no-readme-claims", action="store_true")
    trust.add_argument("--deps", action="store_true", help="Opt-in typosquat dep names")
    trust.add_argument("--meta", action="store_true", help="Opt-in local meta heuristics")
    trust.add_argument("--self-test", action="store_true")

    research = sub.add_parser("research", help="RSS/Atom research scanner (delegates to tbcc_cli.py research)")
    research.add_argument("rest", nargs=argparse.REMAINDER, help="Forwarded to tbcc_cli.py research ...")

    llm = sub.add_parser("llm", help="Local LLM provider/model index (delegates to tbcc_cli.py llm)")
    llm.add_argument("rest", nargs=argparse.REMAINDER, help="Forwarded to tbcc_cli.py llm ...")

    slots = sub.add_parser("slots", help="API Pocket slot registry (delegates to tbcc_cli.py slots)")
    slots.add_argument("rest", nargs=argparse.REMAINDER, help="Forwarded to tbcc_cli.py slots ...")

    tui = sub.add_parser(
        "tui", help="Unified operator terminal — models/keys/affiliate-links/semantic-scan (delegates to tbcc_cli.py operator tui)"
    )
    tui.add_argument("rest", nargs=argparse.REMAINDER, help="Forwarded to tbcc_cli.py operator tui ...")

    wifi = sub.add_parser(
        "wifi",
        help="Pause/restore bandwidth hogs (OneDrive, MEGA, Steam, …) and show a WiFi snapshot",
    )
    wifi.add_argument(
        "action",
        nargs="?",
        default="status",
        choices=sorted(_WIFI_ACTIONS),
        help="focus = pause until restore, restore = start again, status = snapshot (default)",
    )
    wifi.add_argument("--dry-run", action="store_true", help="Print what would change; do not pause or restore")
    wifi.add_argument("--json", action="store_true")

    args = p.parse_args(argv)

    if args.command == "list":
        return cmd_list(args)

    if args.command == "semantic-scan":
        forward: list[str] = []
        if args.self_test:
            forward.append("--self-test")
        else:
            if args.json:
                forward.append("--json")
            if args.ask:
                forward.extend(["--ask", args.ask])
            if args.no_readme_claims:
                forward.append("--no-readme-claims")
            forward.extend(["--max-files", str(args.max_files), "--max-bytes", str(args.max_bytes)])
            forward.append(args.target)
        return _run_script(SEMANTIC_SCAN, forward)

    if args.command == "repo-trust":
        forward = []
        if args.self_test:
            forward.append("--self-test")
        else:
            if args.json:
                forward.append("--json")
            if args.ask:
                forward.extend(["--ask", args.ask])
            if args.no_readme_claims:
                forward.append("--no-readme-claims")
            if args.deps:
                forward.append("--deps")
            if args.meta:
                forward.append("--meta")
            forward.extend(["--max-files", str(args.max_files), "--max-bytes", str(args.max_bytes)])
            forward.append(args.target)
        return _run_script(REPO_TRUST, forward)

    if args.command == "wifi":
        forward = ["-Action", args.action]
        if args.dry_run:
            forward.append("-DryRun")
        if args.json:
            forward.append("-Json")
        return _run_powershell(_wifi_script(), forward)

    if args.command == "tui":
        return _delegate_to_tbcc_cli("operator", ["tui", *args.rest])

    if args.command in _DELEGATE_COMMANDS:
        return _delegate_to_tbcc_cli(args.command, args.rest)

    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
