"""Success metrics for tipify / endgates: tip token budget + invoke miss log."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
_METRICS_DIR = _REPO / ".skill-gap" / "metrics"
_ENDGATES_LOG = _METRICS_DIR / "endgates.jsonl"
_MISS_LOG = _METRICS_DIR / "invoke_miss.jsonl"
_BUDGET_CACHE = _METRICS_DIR / "tip_budget.json"

# Soft budgets (chars÷4 ≈ tokens) — endgates tip alone; full alwaysApply is separate
_TIP_SOFT_CAP_SINGLE = 200
_ENDGATES_SOFT_CAP = 200
_ALWAYS_APPLY_SOFT_CAP = 6000

_ALWAYS_RE = re.compile(r"(?m)^alwaysApply:\s*true\s*$")


def _estimate_tok(text: str) -> int:
    return max(0, round(len(text or "") / 4))


def measure_tip_budget(rules_roots: list[Path] | None = None) -> dict[str, Any]:
    """Sum alwaysApply rules; highlight powercore-endgates tip size."""
    roots = rules_roots or [
        _REPO / ".cursor" / "rules",
        Path(r"C:\Powercore-repo-main\telegram_bot2\.cursor\rules"),
        Path(r"C:\Powercore-repo-main\powercore-ops\.cursor\rules"),
    ]
    seen: dict[str, int] = {}
    files: list[dict[str, Any]] = []
    endgates_tok = 0
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.mdc")):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if not _ALWAYS_RE.search(text):
                continue
            if path.name in seen:
                continue
            tok = _estimate_tok(text)
            seen[path.name] = tok
            files.append(
                {
                    "name": path.name,
                    "tok": tok,
                    "over_single": tok > _TIP_SOFT_CAP_SINGLE,
                    "path": str(path),
                }
            )
            if path.name == "powercore-endgates.mdc":
                endgates_tok = tok
    total = sum(seen.values())
    out = {
        "ok": True,
        "total_tok": total,
        "endgates_tip_tok": endgates_tok,
        "file_count": len(files),
        "soft_cap_endgates": _ENDGATES_SOFT_CAP,
        "soft_cap_always_apply": _ALWAYS_APPLY_SOFT_CAP,
        "soft_cap_single": _TIP_SOFT_CAP_SINGLE,
        "over_endgates": endgates_tok > _ENDGATES_SOFT_CAP,
        "over_cumulative": total > _ALWAYS_APPLY_SOFT_CAP,
        "files": sorted(files, key=lambda f: -f["tok"]),
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    try:
        _METRICS_DIR.mkdir(parents=True, exist_ok=True)
        _BUDGET_CACHE.write_text(json.dumps(out, indent=2), encoding="utf-8")
    except OSError:
        pass
    return out


def append_endgates_log(payload: dict[str, Any]) -> None:
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "skipped": bool(payload.get("skipped")),
        "lines": payload.get("lines") or [],
        "ranked_top": (payload.get("ranked") or [{}])[0].get("name")
        if payload.get("ranked")
        else None,
        "crystallize_tier": ((payload.get("crystallize") or {}).get("gate") or {}).get(
            "tier"
        ),
        "skill_gap_suggest": bool(
            (payload.get("skill_gap") or {}).get("should_suggest")
        ),
        "tip_budget_tok": (payload.get("tip_budget") or {}).get("total_tok"),
    }
    gap = payload.get("skill_gap") or {}
    if gap.get("should_suggest"):
        row["proposed_slug"] = gap.get("proposed_name") or None
        row["score"] = gap.get("score")
    try:
        _METRICS_DIR.mkdir(parents=True, exist_ok=True)
        with _ENDGATES_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass


def log_invoke_eval(
    *,
    case_id: str,
    expected: str | None,
    actual_top: str | None,
    score: float | None = None,
    hit: bool | None = None,
) -> dict[str, Any]:
    """Append one golden-eval / miss-rate row."""
    if hit is None:
        if not expected:
            hit = True
        else:
            hit = (actual_top or "").lower() == expected.lower()
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "case_id": case_id,
        "expected": expected,
        "actual_top": actual_top,
        "score": score,
        "hit": hit,
        "miss": not hit,
    }
    try:
        _METRICS_DIR.mkdir(parents=True, exist_ok=True)
        with _MISS_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass
    return row


def summarize_miss_rate(*, last_n: int = 50) -> dict[str, Any]:
    if not _MISS_LOG.is_file():
        return {"ok": True, "n": 0, "hit_rate": None, "misses": []}
    lines = _MISS_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    rows = []
    for line in lines[-max(1, last_n) :]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    hits = sum(1 for r in rows if r.get("hit"))
    n = len(rows)
    return {
        "ok": True,
        "n": n,
        "hits": hits,
        "misses": n - hits,
        "hit_rate": round(hits / n, 3) if n else None,
        "recent_misses": [r for r in rows if r.get("miss")][-10:],
    }
