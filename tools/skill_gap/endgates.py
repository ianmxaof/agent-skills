"""End-of-turn gates: crystallize → skill-gap → rank_skills (≤5 lines out).

  cd agent-skills
  py -3.13 -m tools.skill_gap.endgates --prompt "..." --response "..." --auto --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_TBCC_BACKEND = Path(r"C:\Powercore-repo-main\telegram_bot2\tbcc\backend")

from tools.skill_gap.trivial import is_trivial_ack  # noqa: E402


def _trivial(prompt: str, response: str) -> bool:
    p = (prompt or "").strip()
    r = (response or "").strip()
    if not r:
        return True
    if len(r) < 120 and is_trivial_ack(p):
        return True
    if len(r) < 80 and not re.search(r"[/\\]|\.py|\.mdc|```", r):
        return True
    return False


def _run_crystallize(prompt: str, response: str, *, auto: bool) -> dict[str, Any]:
    script = _TBCC_BACKEND / "scripts" / "run_crystallize_gate.py"
    if not script.is_file():
        return {"ok": False, "error": f"missing {script}"}
    cmd = [
        sys.executable,
        str(script),
        "--source",
        "cursor",
        "--model",
        "cursor-agent",
        "--prompt",
        prompt,
        "--response",
        response,
        "--json",
        "--no-llm-gate",
    ]
    if auto:
        cmd.append("--auto")
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(_TBCC_BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except Exception as e:
        return {"ok": False, "error": str(e)}
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {
            "ok": False,
            "error": "crystallize non-json",
            "stdout": (proc.stdout or "")[:500],
            "stderr": (proc.stderr or "")[:500],
            "exit_code": proc.returncode,
        }


def run_endgates(
    *,
    prompt: str = "",
    response: str = "",
    auto: bool = True,
    rank_limit: int = 3,
) -> dict[str, Any]:
    from tools.skill_gap.gate import evaluate_skill_gap
    from tools.skill_gap.metrics import append_endgates_log, measure_tip_budget
    from tools.skill_gap.rank_skills import rank_skills_for_invoke

    out: dict[str, Any] = {
        "ok": True,
        "skipped": False,
        "lines": [],
        "tip_budget": measure_tip_budget(),
    }

    if _trivial(prompt, response):
        out["skipped"] = True
        out["lines"] = ["endgates: skip (trivial)"]
        append_endgates_log(out)
        return out

    cryst = _run_crystallize(prompt, response, auto=auto)
    out["crystallize"] = cryst
    gate = (cryst or {}).get("gate") or {}
    if cryst.get("crystallize", {}).get("ok"):
        path = cryst["crystallize"].get("path", "")
        out["lines"].append(
            f"Auto-crystallized (NTK {gate.get('score')}, "
            f"{','.join(gate.get('projects') or []) or '-'}) -> {path}"
        )
    elif gate.get("tier") and gate.get("tier") != "skip":
        out["lines"].append(
            f"crystallize: tier={gate.get('tier')} score={gate.get('score')} "
            f"(no write)"
        )

    gap = evaluate_skill_gap(user_prompt=prompt, ai_response=response)
    out["skill_gap"] = gap.to_dict()
    if gap.should_suggest:
        line = gap.suggest_line(plain=True)
        out["lines"].append(line)
        out["suggest_line"] = line

    ranked = rank_skills_for_invoke(
        user_prompt=prompt, ai_response=response, limit=rank_limit
    )
    out["ranked"] = ranked
    if ranked:
        top = ", ".join(f"{r['name']}@{r['score']:.2f}" for r in ranked[:rank_limit])
        out["lines"].append(f"open-skills: {top}")

    if not out["lines"]:
        out["lines"] = ["endgates: ok (silent)"]

    # Cap operator-facing lines
    out["lines"] = out["lines"][:5]
    append_endgates_log(out)
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="End-of-turn gates (crystallize → gap → rank)")
    p.add_argument("--prompt", default="")
    p.add_argument("--response", default="")
    p.add_argument("--file", type=Path, help="Assistant response file")
    p.add_argument("--stdin", action="store_true")
    p.add_argument("--auto", action="store_true", default=True)
    p.add_argument("--no-auto", action="store_true", help="Score crystallize only")
    p.add_argument("--rank-limit", type=int, default=3)
    p.add_argument("--json", action="store_true")
    p.add_argument("--plain", action="store_true", help="Print ≤5 lines only")
    args = p.parse_args(argv)

    response = args.response
    if args.file:
        response = args.file.read_text(encoding="utf-8", errors="replace")
    elif args.stdin:
        response = sys.stdin.read()

    auto = bool(args.auto) and not args.no_auto
    result = run_endgates(
        prompt=args.prompt,
        response=response,
        auto=auto,
        rank_limit=args.rank_limit,
    )

    if args.json and not args.plain:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        for line in result.get("lines") or []:
            print(line)
        budget = result.get("tip_budget") or {}
        if budget.get("total_tok") is not None and not args.plain:
            print(
                f"tip-budget: {budget['total_tok']} tok "
                f"({budget.get('file_count', 0)} alwaysApply tips)"
            )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
