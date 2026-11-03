#!/usr/bin/env python3
"""Classify vendor/incoming dumps and score importance into vendor/sorted + catalog.

Examples:
  py -3.13 scripts/sort.py
  py -3.13 scripts/sort.py --id 2026-09-09_awesome-cursor-skills
  py -3.13 scripts/sort.py --boost prompt-engineering=15
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _lib import (
    REPO_ROOT,
    copy_tree,
    detect_kind,
    existing_library_names,
    iter_candidate_units,
    load_catalog,
    load_config,
    save_catalog,
    score_item,
    slugify,
    strip_batch_prefix,
    utc_now,
)


def sort_batch(item_id: str, boosts: dict[str, int] | None = None) -> list[dict]:
    cfg = load_config()
    catalog = load_catalog(cfg)
    item = catalog["items"].get(item_id)
    if not item:
        raise SystemExit(f"Unknown catalog id: {item_id}")

    incoming = REPO_ROOT / item["incoming_path"]
    if not incoming.exists():
        raise SystemExit(f"Incoming path missing: {incoming}")

    library_names = existing_library_names(cfg)
    boosts = boosts or {}
    units_out: list[dict] = []

    candidates = iter_candidate_units(incoming)
    for unit in candidates:
        kind = detect_kind(unit)
        raw_name = unit.stem if unit.is_file() else unit.name
        name = slugify(strip_batch_prefix(raw_name))
        if name in {"resources", "src", "docs", "tests"} and unit.is_dir() and not (unit / "SKILL.md").exists():
            continue

        op_boost = int(item.get("operator_boost") or 0) + int(boosts.get(name, 0))
        scored = score_item(
            kind=kind,
            path=unit,
            name=name,
            operator_boost=op_boost,
            use_count=int(item.get("use_count") or 0),
            library_names=library_names,
            cfg=cfg,
        )
        name = scored.get("name") or name

        sorted_root = REPO_ROOT / cfg["sorted_dir"] / kind
        sorted_root.mkdir(parents=True, exist_ok=True)
        dest = sorted_root / name
        copy_tree(unit, dest)

        card = {
            "name": name,
            "kind": kind,
            "sorted_path": str(dest.relative_to(REPO_ROOT)).replace("\\", "/"),
            "source_unit": str(unit.relative_to(REPO_ROOT)).replace("\\", "/") if str(unit).startswith(str(REPO_ROOT)) else str(unit),
            "importance": scored,
            "updated_at": utc_now(),
        }
        # write card next to sorted unit
        card_path = dest.with_suffix(dest.suffix + ".card.json") if dest.is_file() else dest / "CARD.json"
        if dest.is_dir():
            (dest / "CARD.json").write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
        else:
            card_path.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")

        units_out.append(card)

    item["units"] = units_out
    item["status"] = "sorted"
    item["sorted_at"] = utc_now()
    # batch score = max unit score
    if units_out:
        best = max(u["importance"]["score"] for u in units_out)
        item["importance"] = {
            "score": best,
            "tier": max(
                (u["importance"]["tier"] for u in units_out),
                key=lambda t: {"park": 0, "review": 1, "promote-candidate": 2}[t],
            ),
            "unit_count": len(units_out),
        }
    catalog["items"][item_id] = item
    save_catalog(catalog, cfg)
    return units_out


def sort_all(boosts: dict[str, int] | None = None, only_id: str | None = None) -> None:
    cfg = load_config()
    catalog = load_catalog(cfg)
    ids = [only_id] if only_id else list(catalog["items"].keys())
    # also pick up unregistered incoming folders
    incoming = REPO_ROOT / cfg["incoming_dir"]
    if incoming.is_dir() and not only_id:
        for child in sorted(incoming.iterdir()):
            if child.is_dir() and child.name != ".gitkeep" and child.name not in catalog["items"]:
                catalog["items"][child.name] = {
                    "id": child.name,
                    "source": "untracked-incoming",
                    "incoming_path": str(child.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "ingested_at": utc_now(),
                    "status": "incoming",
                    "kind": None,
                    "units": [],
                    "operator_boost": 0,
                    "use_count": 0,
                    "importance": None,
                    "notes": "auto-registered by sort.py",
                }
        save_catalog(catalog, cfg)
        ids = list(load_catalog(cfg)["items"].keys())

    total_units = 0
    for item_id in ids:
        if only_id and item_id != only_id:
            continue
        item = load_catalog(cfg)["items"].get(item_id)
        if not item:
            continue
        if item.get("status") == "promoted" and not only_id:
            continue
        units = sort_batch(item_id, boosts=boosts)
        total_units += len(units)
        refreshed = load_catalog(cfg)["items"].get(item_id) or {}
        best = refreshed.get("importance") or {}
        print(f"{item_id}: {len(units)} unit(s)  best={best.get('score')} ({best.get('tier')})")

    print(f"Done. Sorted {total_units} unit(s). Catalog: vendor/catalog.json")
    print("Promote candidates: py -3.13 scripts/promote.py --list")


def parse_boosts(raw: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in raw:
        if "=" not in item:
            raise SystemExit(f"Bad --boost (use name=score): {item}")
        name, val = item.split("=", 1)
        out[slugify(name)] = int(val)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Classify + score vendor/incoming into vendor/sorted")
    ap.add_argument("--id", help="Sort only this incoming batch id")
    ap.add_argument("--boost", action="append", default=[], help="name=points operator boost (repeatable)")
    args = ap.parse_args()
    sort_all(boosts=parse_boosts(args.boost), only_id=args.id)
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
