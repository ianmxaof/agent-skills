"""Write a dated compaction stub (summarize -> fresh session).

  cd agent-skills
  py -3.13 -m tools.skill_gap.compact --goal "..." --done "a" --done "b" --next "c"

Default out dir: .skill-gap/compacts/ (gitignored). Use --out-dir docs/handoffs
to keep a stub in git. Habit it wires to: tbcc-auto-crystallize (NTK vault
capture) and the *_report.md handoff reports. Never auto-runs; never reads
the session -- the operator/agent fills the fields.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

DEFAULT_DIR = _REPO / ".skill-gap" / "compacts"


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:40] or "session"


def _bullets(items: list[str] | None, empty: str) -> str:
    return "\n".join(f"- {i}" for i in items) if items else f"- {empty}"


def write_compact(
    *,
    goal: str,
    done: list[str] | None = None,
    next_steps: list[str] | None = None,
    decisions: list[str] | None = None,
    open_questions: list[str] | None = None,
    verify: str = "",
    out_dir: Path | None = None,
    now: datetime | None = None,
) -> Path:
    """Write the stub and return its path. Never overwrites an existing file."""
    now = now or datetime.now()
    out_dir = Path(out_dir) if out_dir else DEFAULT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    base = f"{now:%Y-%m-%d_%H%M}_compact_{_slug(goal)}"
    path = out_dir / f"{base}.md"
    n = 2
    while path.exists():
        path = out_dir / f"{base}-{n}.md"
        n += 1
    body = f"""# Compact - {goal or '(goal?)'}

Written {now:%Y-%m-%d %H:%M}. Paste this into a FRESH session instead of the old thread.

## Goal
{goal or 'TODO'}

## Done (with evidence)
{_bullets(done, 'TODO: what landed + commit SHA / command output')}

## Decisions (keep)
{_bullets(decisions, 'none recorded')}

## Next (one vertical slice)
{_bullets(next_steps, 'TODO: one slice')}

## External stop for the next slice
{verify or 'TODO: one command whose output proves it landed'}

## Open / low-confidence
{_bullets(open_questions, 'none')}

## Links
- Crystallize durable facts: `tbcc-auto-crystallize` (`run_crystallize_gate.py --auto`)
- Reverse report: `docs/handoffs/YYYY-MM-DD_*_report.md`
"""
    path.write_text(body, encoding="utf-8", newline="\n")
    return path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Write a dated compaction stub")
    p.add_argument("--goal", required=True)
    p.add_argument("--done", action="append")
    p.add_argument("--next", dest="next_steps", action="append")
    p.add_argument("--decision", dest="decisions", action="append")
    p.add_argument("--open", dest="open_questions", action="append")
    p.add_argument("--verify", default="")
    p.add_argument("--out-dir", type=Path, default=None)
    a = p.parse_args(argv)
    path = write_compact(
        goal=a.goal, done=a.done, next_steps=a.next_steps, decisions=a.decisions,
        open_questions=a.open_questions, verify=a.verify, out_dir=a.out_dir,
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
