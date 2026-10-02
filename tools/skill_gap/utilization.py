"""Thin endgates utilization view: ranked_top histogram + suggest rate.

  cd agent-skills
  py -3.13 -m tools.skill_gap.utilization [--last N] [--json]

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
    "ranked_top = what endgates RANKED, not skills actually opened "
    "(no opened-skill counter exists)."
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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Endgates ranked_top histogram + suggest rate")
    p.add_argument("--last", type=int, default=50)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
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
