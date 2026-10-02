"""Pending skill-gap proposals from the endgates log (read-only, suggest-only).

  cd agent-skills
  py -3.13 -m tools.skill_gap.pending [--legacy] [--json] [--last N]

Rows written after the structured-logging change carry `proposed_slug` + `score`.
`--legacy` also recovers older rows by parsing the free-text `lines` field
("Skill gap suggested (N) -> powercore-<slug>"). Never writes skills.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from tools.skill_gap.gate import is_valid_slug  # noqa: E402

_LOG = _REPO / ".skill-gap" / "metrics" / "endgates.jsonl"
_LEGACY_RE = re.compile(r"Skill gap suggested \((\d+)\)\s*->\s*(\S+)")


def _row_proposal(row: dict[str, Any], *, legacy: bool) -> tuple[str, int, str] | None:
    """Return (slug, score, source) for a suggest row, else None."""
    slug = row.get("proposed_slug")
    if slug:
        return str(slug), int(row.get("score") or 0), "structured"
    if legacy and row.get("skill_gap_suggest"):
        for line in row.get("lines") or []:
            m = _LEGACY_RE.search(str(line))
            if m:
                return m.group(2), int(m.group(1)), "legacy"
    return None


def load_pending(
    path: Path | None = None, *, legacy: bool = False, last_n: int = 0
) -> list[dict[str, Any]]:
    path = path or _LOG
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    if last_n > 0:
        rows = rows[-last_n:]
    agg: dict[str, dict[str, Any]] = {}
    for row in rows:
        found = _row_proposal(row, legacy=legacy)
        if not found:
            continue
        slug, score, source = found
        if not is_valid_slug(slug):
            continue
        cur = agg.setdefault(
            slug,
            {"slug": slug, "count": 0, "max_score": 0, "last_seen": "", "sources": set()},
        )
        cur["count"] += 1
        cur["max_score"] = max(cur["max_score"], score)
        cur["last_seen"] = max(cur["last_seen"], str(row.get("ts") or ""))
        cur["sources"].add(source)
    out = []
    for v in agg.values():
        v["sources"] = sorted(v["sources"])
        out.append(v)
    out.sort(key=lambda v: (-v["max_score"], -v["count"], v["slug"]))
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Pending skill-gap proposals (read-only)")
    p.add_argument("--legacy", action="store_true", help="also parse free-text lines of old rows")
    p.add_argument("--last", type=int, default=0, help="only the last N log rows")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    pending = load_pending(legacy=args.legacy, last_n=args.last)
    if args.json:
        print(json.dumps(pending, indent=2))
        return 0
    if not pending:
        print("pending: none")
        return 0
    print(f"{'slug':48} {'n':>3} {'max':>4}  last_seen")
    for v in pending:
        print(f"{v['slug']:48} {v['count']:>3} {v['max_score']:>4}  {v['last_seen'][:19]}")
    print("ACK -> py -3.13 -m tools.skill_gap.scaffold_surfaces --skill <slug> --title ... --description ...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
