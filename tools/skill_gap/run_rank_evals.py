"""Golden evals for skill invoke ranking (miss-rate metric).

  py -3.13 -m tools.skill_gap.run_rank_evals --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_DEFAULT_CASES = _REPO / "tools" / "skill_gap" / "evals" / "rank_skills_cases.json"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run rank_skills golden evals")
    p.add_argument("--cases", type=Path, default=_DEFAULT_CASES)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    from tools.skill_gap.metrics import log_invoke_eval, summarize_miss_rate
    from tools.skill_gap.rank_skills import rank_skills_for_invoke

    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    results = []
    hits = 0
    for case in cases:
        ranked = rank_skills_for_invoke(
            user_prompt=case.get("prompt", ""),
            ai_response=case.get("response", ""),
            limit=5,
        )
        top = ranked[0]["name"] if ranked else None
        score = ranked[0]["score"] if ranked else None
        expected = case.get("expect_top1")
        expect_any = case.get("expect_any_of") or ([expected] if expected else [])
        if case.get("expect_skip"):
            hit = not ranked or top is None
        elif expect_any:
            hit = top in expect_any
        else:
            hit = True
        log_invoke_eval(
            case_id=case.get("id", "anon"),
            expected=expected or (expect_any[0] if expect_any else None),
            actual_top=top,
            score=score,
            hit=hit,
        )
        if hit:
            hits += 1
        results.append(
            {
                "id": case.get("id"),
                "hit": hit,
                "expected": expected or expect_any,
                "actual_top": top,
                "score": score,
            }
        )

    summary = {
        "ok": hits == len(results),
        "passed": hits,
        "total": len(results),
        "hit_rate": round(hits / len(results), 3) if results else None,
        "results": results,
        "miss_log": summarize_miss_rate(last_n=100),
    }
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"rank_evals {hits}/{len(results)} hit_rate={summary['hit_rate']}")
        for r in results:
            mark = "OK" if r["hit"] else "MISS"
            print(f"  [{mark}] {r['id']}: got={r['actual_top']} expect={r['expected']}")
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
