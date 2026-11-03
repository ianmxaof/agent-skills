#!/usr/bin/env python3
"""Promote sorted units into the portable library (.cursor/skills or skills/).

Does NOT install to ~/.cursor/skills unless --live is passed.

Examples:
  py -3.13 scripts/promote.py --list
  py -3.13 scripts/promote.py --tier promote-candidate
  py -3.13 scripts/promote.py --name prompt-engineering
  py -3.13 scripts/promote.py --name prompt-engineering --live
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _lib import (
    REPO_ROOT,
    copy_tree,
    expand_user_path,
    load_catalog,
    load_config,
    save_catalog,
    utc_now,
)


def iter_sorted_cards(cfg: dict) -> list[dict]:
    cards: list[dict] = []
    sorted_root = REPO_ROOT / cfg["sorted_dir"]
    if not sorted_root.is_dir():
        return cards
    for kind_dir in sorted_root.iterdir():
        if not kind_dir.is_dir():
            continue
        for child in kind_dir.iterdir():
            card_path = child / "CARD.json" if child.is_dir() else Path(str(child) + ".card.json")
            if child.is_dir() and (child / "CARD.json").exists():
                card = json.loads((child / "CARD.json").read_text(encoding="utf-8"))
                cards.append(card)
            elif child.is_file() and child.name.endswith(".card.json"):
                continue
            elif child.is_file() and Path(str(child) + ".card.json").exists():
                card = json.loads(Path(str(child) + ".card.json").read_text(encoding="utf-8"))
                cards.append(card)
    return cards


def library_dest_for(kind: str, name: str, cfg: dict) -> Path:
    if kind in {"cursor-skill", "claude-skill", "plugin"}:
        return REPO_ROOT / cfg["library_cursor"] / name
    if kind == "warp-skill":
        # keep under skills/imported/
        return REPO_ROOT / cfg["library_warp"] / "imported" / f"{name}.md"
    if kind == "rule":
        return REPO_ROOT / ".cursor" / "rules-imported" / name
    if kind == "command":
        return REPO_ROOT / ".cursor" / "commands-imported" / name
    return REPO_ROOT / "vendor" / "sorted" / "other" / name


def promote_card(card: dict, *, live: bool, dry_run: bool) -> Path | None:
    cfg = load_config()
    src = REPO_ROOT / card["sorted_path"]
    if not src.exists():
        print(f"skip missing: {card['sorted_path']}")
        return None

    # For skill dirs, copy the folder but strip CARD.json from live/library? keep CARD in library for provenance
    dest = library_dest_for(card["kind"], card["name"], cfg)
    print(f"{'[dry] ' if dry_run else ''}promote {card['kind']}:{card['name']} -> {dest.relative_to(REPO_ROOT)}")
    if dry_run:
        return dest

    if card["kind"] == "warp-skill" and src.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy_tree(src, dest)
    elif card["kind"] in {"rule", "command"} and src.is_file():
        dest = dest if dest.suffix else dest.with_suffix(src.suffix)
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy_tree(src, dest if dest.suffix else dest / src.name)
        if not dest.suffix:
            dest = dest / src.name
    else:
        # directory skill
        copy_tree(src, dest)

    if live and card["kind"] in {"cursor-skill", "claude-skill"}:
        live_root = expand_user_path(cfg["live_install"]["cursor_user_skills"])
        live_dest = live_root / card["name"]
        print(f"  live -> {live_dest}")
        copy_tree(src if src.is_dir() else src.parent, live_dest)
        # remove CARD from live install to keep clean
        card_file = live_dest / "CARD.json"
        if card_file.exists():
            card_file.unlink()

    # bump catalog use / status
    catalog = load_catalog(cfg)
    for item in catalog["items"].values():
        for unit in item.get("units") or []:
            if unit.get("name") == card["name"] and unit.get("kind") == card["kind"]:
                unit["promoted_at"] = utc_now()
                unit["promoted_to"] = str(dest.relative_to(REPO_ROOT)).replace("\\", "/")
        if any(u.get("name") == card["name"] for u in item.get("units") or []):
            item["use_count"] = int(item.get("use_count") or 0) + 1
            item["status"] = "promoted"
    save_catalog(catalog, cfg)
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description="Promote sorted vendor units into the portable library")
    ap.add_argument("--list", action="store_true", help="List sorted units by importance")
    ap.add_argument("--tier", choices=["promote-candidate", "review", "park"], help="Promote all in tier")
    ap.add_argument("--name", help="Promote a single unit by name")
    ap.add_argument("--live", action="store_true", help="Also copy into ~/.cursor/skills (makes it active)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    cards = iter_sorted_cards(cfg)
    cards.sort(key=lambda c: c.get("importance", {}).get("score", 0), reverse=True)

    if args.list or (not args.tier and not args.name):
        if not cards:
            print("No sorted cards yet. Run: py -3.13 scripts/sort.py")
            return 0
        print(f"{'SCORE':>6}  {'TIER':<18}  {'KIND':<14}  NAME")
        for c in cards:
            imp = c.get("importance") or {}
            print(f"{imp.get('score', 0):6}  {imp.get('tier', '?'):<18}  {c.get('kind', '?'):<14}  {c.get('name')}")
        if not args.tier and not args.name:
            return 0

    selected = []
    for c in cards:
        if args.name and c["name"] != args.name:
            continue
        if args.tier and (c.get("importance") or {}).get("tier") != args.tier:
            continue
        selected.append(c)

    if not selected:
        print("No matching units.")
        return 1

    for c in selected:
        promote_card(c, live=args.live, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
