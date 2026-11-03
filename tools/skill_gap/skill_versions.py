#!/usr/bin/env python3
"""PowerCore skill version CLI — list / snapshot / pin / rollback.

  py -3.13 -m tools.skill_gap.skill_versions list --skill cc-report
  py -3.13 -m tools.skill_gap.skill_versions snapshot --skill cc-report --note "seed" --score 20/20
  py -3.13 -m tools.skill_gap.skill_versions pin --skill cc-report --id v0001
  py -3.13 -m tools.skill_gap.skill_versions rollback --skill cc-report --id v0001
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _skill_dir(name: str) -> Path:
    return _REPO / ".cursor" / "skills" / name


def _add_skill_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument("--skill", required=True, help="Skill folder name under .cursor/skills/")


def main() -> int:
    parser = argparse.ArgumentParser(description="PowerCore skill version control")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List snapshots")
    _add_skill_arg(p_list)
    p_list.add_argument("--json", action="store_true")

    p_snap = sub.add_parser("snapshot", help="Snapshot current SKILL.md")
    _add_skill_arg(p_snap)
    p_snap.add_argument("--note", default="")
    p_snap.add_argument("--score", default="")
    p_snap.add_argument("--json", action="store_true")

    p_seed = sub.add_parser("seed", help="Create v0001 if none exist")
    _add_skill_arg(p_seed)
    p_seed.add_argument("--score", default="")
    p_seed.add_argument("--json", action="store_true")

    p_pin = sub.add_parser("pin", help="Mark a version as preferred")
    _add_skill_arg(p_pin)
    p_pin.add_argument("--id", required=True)
    p_pin.add_argument("--json", action="store_true")

    p_unpin = sub.add_parser("unpin", help="Clear pin")
    _add_skill_arg(p_unpin)
    p_unpin.add_argument("--id", required=True)

    p_rb = sub.add_parser("rollback", help="Restore snapshot and fork forward")
    _add_skill_arg(p_rb)
    p_rb.add_argument("--id", required=True)
    p_rb.add_argument("--note", default="")
    p_rb.add_argument("--json", action="store_true")

    p_show = sub.add_parser("show", help="Show CURRENT + paths")
    _add_skill_arg(p_show)
    p_show.add_argument("--json", action="store_true")

    args = parser.parse_args()
    skill_dir = _skill_dir(args.skill)
    if not (skill_dir / "SKILL.md").is_file():
        print(f"missing skill: {skill_dir}", file=sys.stderr)
        return 2

    from tools.skill_gap import versions as V

    if args.cmd == "list":
        data = V.list_versions(skill_dir)
        if args.json:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"{data['skill']} current={data['current'] or '(none)'} count={data['count']}")
            for e in data["entries"]:
                marks = []
                if e["id"] == data["current"]:
                    marks.append("CURRENT")
                if e.get("pinned"):
                    marks.append("PINNED")
                tag = f" [{' '.join(marks)}]" if marks else ""
                print(
                    f"  {e['id']}  score={e.get('score') or '-'}  "
                    f"src={e.get('source')}  parent={e.get('parent') or '-'}{tag}"
                )
                if e.get("note"):
                    print(f"      {e['note']}")
        return 0

    if args.cmd == "seed":
        entry = V.ensure_seed(skill_dir, score=args.score)
        if entry is None:
            print("already seeded")
            return 0
        if args.json:
            print(json.dumps(entry.to_dict(), indent=2))
        else:
            print(f"seeded {entry.id}")
        return 0

    if args.cmd == "snapshot":
        entry = V.snapshot(skill_dir, score=args.score, note=args.note, source="manual")
        if args.json:
            print(json.dumps(entry.to_dict(), indent=2))
        else:
            print(f"snapshot {entry.id} -> CURRENT")
        return 0

    if args.cmd == "pin":
        entry = V.pin(skill_dir, args.id)
        if args.json:
            print(json.dumps(entry.to_dict(), indent=2))
        else:
            print(f"pinned {entry.id}")
        return 0

    if args.cmd == "unpin":
        entry = V.unpin(skill_dir, args.id)
        print(f"unpinned {entry.id}")
        return 0

    if args.cmd == "rollback":
        entry = V.rollback(skill_dir, args.id, note=args.note)
        if args.json:
            print(json.dumps(entry.to_dict(), indent=2))
        else:
            print(f"rollback -> new CURRENT {entry.id} (parent={entry.parent})")
        return 0

    if args.cmd == "show":
        data = V.list_versions(skill_dir)
        out = {
            "skill": data["skill"],
            "current": data["current"],
            "versions_dir": str(V.versions_dir(skill_dir)),
            "pinned": data["pinned"],
        }
        print(json.dumps(out, indent=2))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
