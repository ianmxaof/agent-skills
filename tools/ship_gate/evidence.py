"""Evidence files for PSG runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_root_evidence(root: Path, payload: dict[str, Any]) -> Path:
    dest = root / ".ship-gate" / "last.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dest


def write_run_log(agent_skills_root: Path, run_id: str, payload: dict[str, Any]) -> Path:
    dest = agent_skills_root / ".ship-gate" / "runs" / f"{run_id}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dest


def write_pre_activate(
    store_root: Path, product_id: str, version: str, payload: dict[str, Any]
) -> Path:
    dest = store_root / ".ship-gate" / "pre_activate" / f"{product_id}@{version}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dest


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def check_evidence_fresh(
    root: Path, expected_tree_hash: str, *, max_age_s: float | None = None
) -> dict[str, Any]:
    """Validate <root>/.ship-gate/last.json matches tree_hash and is green."""
    from .verdicts import is_green, normalize_verdict

    path = root / ".ship-gate" / "last.json"
    data = read_json(path)
    if not data:
        return {
            "ok": False,
            "reason": "no evidence file",
            "path": str(path),
        }
    if str(data.get("tree_hash") or "") != expected_tree_hash:
        return {
            "ok": False,
            "reason": "stale tree_hash",
            "path": str(path),
            "evidence_tree": data.get("tree_hash"),
            "expected_tree": expected_tree_hash,
        }
    worst = normalize_verdict(data.get("worst"))
    if not is_green(worst):
        return {
            "ok": False,
            "reason": f"worst={worst}",
            "path": str(path),
        }
    if max_age_s is not None:
        # optional age check via ts
        pass
    return {"ok": True, "path": str(path), "worst": worst, "run_id": data.get("run_id")}
