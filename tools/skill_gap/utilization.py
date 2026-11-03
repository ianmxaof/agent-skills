"""Thin endgates utilization view: ranked_top histogram + suggest rate.

  cd agent-skills
  py -3.13 -m tools.skill_gap.utilization [--last N] [--json] [--report [--plain]]

LIMIT: this reads what endgates *ranked/suggested*, not what agents actually
opened. There is no "skill opened" counter; do not read it as usage.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_LOG = _REPO / ".skill-gap" / "metrics" / "endgates.jsonl"
LIMIT_NOTE = (
    "ranked_top = what endgates RANKED, not skills opened "
    "(no opened-skill counter exists)."
)
TIP_NOTE = (
    "Tips = exposure/cost (alwaysApply token estimate, chars/4), "
    "not fires or call counts."
)


def summarize(path: Path | None = None, *, last_n: int = 50) -> dict[str, Any]:
    path = path or _LOG
    rows: list[dict[str, Any]] = []
    if path.is_file():
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                rows.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
    rows = rows[-max(1, last_n):]
    n = len(rows)
    skipped = sum(1 for r in rows if r.get("skipped"))
    suggests = sum(1 for r in rows if r.get("skill_gap_suggest"))
    hist = Counter(r.get("ranked_top") for r in rows if r.get("ranked_top"))
    return {
        "n": n,
        "skipped_trivial": skipped,
        "no_ranked_top": sum(1 for r in rows if not r.get("ranked_top") and not r.get("skipped")),
        "suggest_count": suggests,
        "suggest_rate": round(suggests / n, 3) if n else None,
        "ranked_top_histogram": dict(hist.most_common()),
        "limit": LIMIT_NOTE,
    }


NEVER_TOP_KEY = "never_top_ranked"
NEVER_TOP_LABEL = (
    "never the top pick in the window (catalog skills not ranked_top in last N rows; "
    "NOT 'unused')"
)
_NEVER_TOP_CAP = 20


def never_top_ranked(histogram: dict[str, int], catalog_root: Path | None = None) -> dict[str, Any]:
    """Catalog skills whose name or alias never appears as ranked_top (case-insensitive)."""
    from tools.skill_gap.catalog import load_skill_catalog

    ranked = {str(k).lower() for k in histogram}
    names = sorted(
        e.name
        for e in load_skill_catalog(catalog_root)
        if e.name.lower() not in ranked and not any(a.lower() in ranked for a in e.aliases)
    )
    return {"count": len(names), "shown": min(len(names), _NEVER_TOP_CAP),
            "names": names[:_NEVER_TOP_CAP]}


def build_report(last_n: int = 50, rules_roots: list[Path] | None = None,
                 log_path: Path | None = None,
                 catalog_root: Path | None = None) -> dict[str, Any]:
    """summarize() + measure_tip_budget() joined; `limit` carries both honesty notes."""
    from tools.skill_gap.metrics import measure_tip_budget

    out = summarize(log_path, last_n=last_n)
    budget = measure_tip_budget(rules_roots)
    out["tips"] = [
        {k: f[k] for k in ("name", "tok", "over_single", "path")}
        for f in budget.get("files", [])
    ]
    out["total_tok"] = budget.get("total_tok", 0)
    out["soft_cap_single"] = budget.get("soft_cap_single")
    out[NEVER_TOP_KEY] = never_top_ranked(out["ranked_top_histogram"], catalog_root)
    out["limit"] = f"{LIMIT_NOTE} {TIP_NOTE}"
    return out


def format_report(r: dict[str, Any]) -> str:
    lines = [LIMIT_NOTE, TIP_NOTE, ""]
    rate = r["suggest_rate"]
    lines.append(f"last {r['n']} endgates rows: skipped={r['skipped_trivial']} "
                 f"suggest={r['suggest_count']} (rate={rate})")
    for name, c in r["ranked_top_histogram"].items():
        lines.append(f"  {c:>3}  {name}")
    lines += ["", f"alwaysApply tips, largest first (name | tok | over_single | path; "
                  f"soft cap/tip = {r.get('soft_cap_single')} tok):"]
    for t in r["tips"]:
        lines.append(f"  {t['name']} | {t['tok']} | {t['over_single']} | {t['path']}")
    lines.append(f"total alwaysApply tok: {r['total_tok']}")
    nt = r[NEVER_TOP_KEY]
    lines += ["", f"{NEVER_TOP_LABEL}: {nt['count']} (showing {nt['shown']})"]
    lines += [f"  {n}" for n in nt["names"]]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Endgates ranked_top histogram + suggest rate")
    p.add_argument("--last", type=int, default=50)
    p.add_argument("--json", action="store_true")
    p.add_argument("--report", action="store_true", help="join histogram with tip exposure")
    p.add_argument("--plain", action="store_true", help="plain text output (default)")
    args = p.parse_args(argv)
    if args.report:
        r = build_report(args.last)
        print(json.dumps(r, indent=2) if args.json else format_report(r))
        return 0
    s = summarize(last_n=args.last)
    if args.json:
        print(json.dumps(s, indent=2))
        return 0
    print(f"last {s['n']} endgates rows: skipped={s['skipped_trivial']} "
          f"suggest={s['suggest_count']} (rate={s['suggest_rate']})")
    for name, c in s["ranked_top_histogram"].items():
        print(f"  {c:>3}  {name}")
    print(f"NOTE: {s['limit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
