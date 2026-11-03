#!/usr/bin/env python3
"""One-shot: ingest a URL/path, then sort + show promote candidates.

Example:
  py -3.13 scripts/pipeline.py https://github.com/spencerpauly/awesome-cursor-skills
  py -3.13 scripts/pipeline.py https://github.com/spencerpauly/awesome-cursor-skills --promote-candidates --dry-run
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run(cmd: list[str]) -> int:
    print("+", " ".join(cmd))
    return subprocess.call(cmd)


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest → sort → list (optional promote)")
    ap.add_argument("source", help="GitHub URL or local path")
    ap.add_argument("--name", help="Override ingest folder name")
    ap.add_argument("--boost", action="append", default=[], help="name=points (passed to sort)")
    ap.add_argument("--promote-candidates", action="store_true")
    ap.add_argument("--live", action="store_true", help="With --promote-candidates, also install live")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    py = sys.executable
    ingest_cmd = [py, str(SCRIPTS / "ingest.py"), args.source]
    if args.name:
        ingest_cmd.extend(["--name", args.name])
    rc = run(ingest_cmd)
    if rc != 0:
        return rc

    sort_cmd = [py, str(SCRIPTS / "sort.py")]
    for b in args.boost:
        sort_cmd.extend(["--boost", b])
    rc = run(sort_cmd)
    if rc != 0:
        return rc

    run([py, str(SCRIPTS / "promote.py"), "--list"])

    if args.promote_candidates:
        promo = [py, str(SCRIPTS / "promote.py"), "--tier", "promote-candidate"]
        if args.live:
            promo.append("--live")
        if args.dry_run:
            promo.append("--dry-run")
        return run(promo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
