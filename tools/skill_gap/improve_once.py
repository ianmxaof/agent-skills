#!/usr/bin/env python3
"""Score cc-report (or any skill) evals + triggers; append results.jsonl.

  py -3.13 -m tools.skill_gap.improve_once --skill cc-report
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score skill evals (+ triggers); log results (no silent SKILL.md mutate)"
    )
    parser.add_argument("--skill", required=True)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Reserved — v1 refuses auto-mutate; use a deliberate SKILL.md edit",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-log", action="store_true", help="Skip results.jsonl append")
    args = parser.parse_args()

    from tools.skill_gap.evals_runner import find_evals, run_evals_file
    from tools.skill_gap.run_triggers import run_triggers

    skill_dir = _REPO / ".cursor" / "skills" / args.skill
    evals = find_evals(skill_dir)
    if not evals:
        print(f"No evals for skill {args.skill}", file=sys.stderr)
        return 2

    baseline = run_evals_file(evals)
    triggers = run_triggers(skill_dir)
    out = {
        "ok": bool(baseline.get("ok")) and bool(triggers.get("ok")),
        "skill": args.skill,
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "evals": {
            "score": baseline.get("score"),
            "ok": baseline.get("ok"),
            "passed": baseline.get("passed"),
            "total": baseline.get("total"),
        },
        "triggers": {
            "score": triggers.get("score"),
            "ok": triggers.get("ok"),
            "passed": triggers.get("passed"),
            "total": triggers.get("total"),
        },
        "applied": False,
        "note": (
            "Scored fixtures only. Edit SKILL.md deliberately (one change), re-run, "
            "keep if scores rise. See evals/program.md. --apply is refused in v1."
        ),
    }

    if args.apply:
        out["ok"] = False
        out["note"] = "--apply refused in v1 (no auto-mutator)."
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(out["note"])
        return 1

    log_path = skill_dir / "evals" / "results.jsonl"
    if not args.no_log and log_path.parent.is_dir():
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(out, ensure_ascii=False) + "\n")

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(
            f"{args.skill} evals {baseline.get('score')} "
            f"({'PASS' if baseline.get('ok') else 'FAIL'}) | "
            f"triggers {triggers.get('score')} "
            f"({'PASS' if triggers.get('ok') else 'FAIL'})"
        )
        print(out["note"])
        if log_path.is_file() and not args.no_log:
            print(f"Logged → {log_path.relative_to(_REPO)}")
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
