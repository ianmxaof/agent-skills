#!/usr/bin/env python3
"""CLI entry: local path or URL → semantic deception scan report.

Examples:
  python semantic_scan.py --json .
  python semantic_scan.py --json C:\\path\\to\\repo
  python semantic_scan.py --json https://github.com/owner/repo
  python semantic_scan.py --json https://gist.github.com/user/abc123
  python semantic_scan.py --json https://pastebin.com/raw/abc123
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

# Allow `python semantic_scan.py` from the scripts/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_target import resolve_scan_root
from scan import VERSION, scan_root


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Semantic deception scan — local path or URL (GitHub, gist, pastebin raw, raw URL)"
    )
    p.add_argument("target", nargs="?", default=".", help="Local directory or supported URL")
    p.add_argument("--json", action="store_true", help="Print JSON report")
    p.add_argument("--max-files", type=int, default=400)
    p.add_argument("--max-bytes", type=int, default=512_000)
    p.add_argument("--self-test", action="store_true", help="Run scanner self-test (local only)")
    args = p.parse_args(argv)

    if args.self_test:
        from scan import main as scan_main

        return scan_main(["--self-test"])

    with resolve_scan_root(args.target) as mat:
        report = scan_root(mat.root, max_files=args.max_files, max_bytes=args.max_bytes)
        payload = asdict(report)
        payload["fetch"] = {
            "source_url": mat.source_url,
            "source_kind": mat.source_kind,
            "scan_root": str(mat.root),
        }
        if args.json:
            print(json.dumps(payload, indent=2))
            return 0 if report.structural_level == "LOW" else 1

        print(f"semantic-deception-detector {VERSION} (CLI)")
        print(f"source: {mat.source_kind} {mat.source_url}")
        print(f"scan_root: {mat.root}")
        print(f"files: {report.files_scanned}  loc~{report.loc_scanned}")
        print(f"structural: {report.structural_score}  {report.structural_level}")
        print(f"total:      {report.risk_score}  {report.risk_level}")
        print(f"categories: {report.summary.get('categories')}")
        print("--- findings ---")
        for f in report.findings:
            loc = f"{f['path']}:{f['line']}" if f.get("line") else f["path"]
            print(f"[{f['category']} conf={f.get('confidence')}] {loc}")
            print(f"  {f['evidence']}")
        return 0 if report.structural_level == "LOW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
