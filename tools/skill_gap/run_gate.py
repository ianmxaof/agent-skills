#!/usr/bin/env python3
"""Score PowerCore skill-gap gate (suggest-only; never auto-writes a skill).

  cd agent-skills
  py -3.13 -m tools.skill_gap.run_gate --prompt "..." --response "..." --json
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
    parser = argparse.ArgumentParser(
        description="PowerCore skill-gap gate → suggest missing skills (no auto-write)"
    )
    parser.add_argument("--prompt", default="", help="User prompt for the turn")
    parser.add_argument("--response", default="", help="Assistant response body")
    parser.add_argument("--file", type=Path, help="Read response from file")
    parser.add_argument("--stdin", action="store_true", help="Read response from stdin")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--root",
        type=Path,
        help="agent-skills repo root (default: auto / POWERCORE_SKILL_GAP_ROOT)",
    )
    args = parser.parse_args()

    response = args.response
    if args.file:
        response = args.file.read_text(encoding="utf-8", errors="replace")
    elif args.stdin:
        response = sys.stdin.read()

    if args.root:
        import os

        os.environ["POWERCORE_SKILL_GAP_ROOT"] = str(args.root.resolve())

    from tools.skill_gap.gate import evaluate_skill_gap

    gate = evaluate_skill_gap(user_prompt=args.prompt, ai_response=response)
    out = {"ok": True, "gate": gate.to_dict(), "suggest_line": gate.suggest_line()}

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    else:
        print(
            f"skill-gap score={gate.score} tier={gate.tier} "
            f"confidence={gate.confidence} corpus={gate.corpus_size}"
        )
        print(f"  {gate.rationale}")
        if gate.should_suggest:
            print(gate.suggest_line())
            print(
                "Do: ask operator to approve create → then "
                "py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-<slug> "
                "(Cursor + Claude twin + GPT paste) + fill bodies + evals/"
            )
            print("Do not: auto-write SKILL.md without explicit operator ACK; do not ship Cursor-only")
        else:
            print("Skip skill-gap suggest")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
