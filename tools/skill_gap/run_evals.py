#!/usr/bin/env python3
"""Run binary evals for a PowerCore skill (Layer-2 self-improve foundation).

  cd agent-skills
  py -3.13 -m tools.skill_gap.run_evals --skill cc-report
  py -3.13 -m tools.skill_gap.run_evals --path .cursor/skills/cc-report/evals/evals.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run binary skill evals")
    parser.add_argument("--skill", help="Skill folder name under .cursor/skills/")
    parser.add_argument("--path", type=Path, help="Direct path to evals.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    from tools.skill_gap.evals_runner import find_evals, run_evals_file

    if args.path:
        path = args.path
    elif args.skill:
        skill_dir = _REPO / ".cursor" / "skills" / args.skill
        found = find_evals(skill_dir)
        if not found:
            print(f"No evals at {skill_dir / 'evals' / 'evals.json'}", file=sys.stderr)
            return 2
        path = found
    else:
        parser.error("provide --skill or --path")
        return 2

    result = run_evals_file(path)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"{result.get('skill')}: {result['score']} ({'PASS' if result['ok'] else 'FAIL'})")
        for case in result.get("cases") or []:
            mark = "ok" if case["ok"] else "FAIL"
            print(f"  [{mark}] {case['id']}")
            for a in case.get("assertions") or []:
                if not a["ok"]:
                    print(f"      - {a['type']}: {a['detail']}")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
