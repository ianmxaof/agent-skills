#!/usr/bin/env python3
"""Evidence envelope + check delta for powercore-cleanroom-brief (Phase 1-2).

Locked item fields: id, kind, value, confidence, coverage, limits.
Record carries optional mode (clean|deep). Summary-first: ``summary`` is a short
list of item ids (or thin stubs); full items live in ``items`` and may be paged
by callers via ``page_items``.

``delta(baseline, candidate)`` is the structural check gate: one result row per
baseline item (``id, pass, note``), plus a row for each candidate-only item.
No pixel/ML similarity — values are compared structurally.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal, TypedDict

VERSION = "0.1.0"

Confidence = Literal["high", "medium", "low"]
Mode = Literal["clean", "deep"]

# One delta row: {"id": str, "pass": bool, "note": str}
DeltaRow = dict[str, Any]


class EvidenceItem(TypedDict):
    id: str
    kind: str
    value: Any
    confidence: Confidence
    coverage: str
    limits: str


class EvidenceRecord(TypedDict):
    """Summary-first evidence envelope."""

    version: str
    source: str
    mode: Mode
    summary: list[str]
    items: list[EvidenceItem]


REQUIRED_ITEM_KEYS = ("id", "kind", "value", "confidence", "coverage", "limits")
REQUIRED_RECORD_KEYS = ("version", "source", "mode", "summary", "items")
_VALID_CONFIDENCE = frozenset({"high", "medium", "low"})
_VALID_MODE = frozenset({"clean", "deep"})


def validate_item(item: dict[str, Any]) -> EvidenceItem:
    missing = [k for k in REQUIRED_ITEM_KEYS if k not in item]
    if missing:
        raise ValueError(f"evidence item missing keys: {missing}")
    conf = item["confidence"]
    if conf not in _VALID_CONFIDENCE:
        raise ValueError(f"invalid confidence: {conf!r}")
    return EvidenceItem(
        id=str(item["id"]),
        kind=str(item["kind"]),
        value=item["value"],
        confidence=conf,  # type: ignore[arg-type]
        coverage=str(item["coverage"]),
        limits=str(item["limits"]),
    )


def validate_record(data: dict[str, Any]) -> EvidenceRecord:
    missing = [k for k in REQUIRED_RECORD_KEYS if k not in data]
    if missing:
        raise ValueError(f"evidence record missing keys: {missing}")
    mode = data["mode"]
    if mode not in _VALID_MODE:
        raise ValueError(f"invalid mode: {mode!r}")
    items = [validate_item(i) for i in data["items"]]
    summary = [str(s) for s in data["summary"]]
    item_ids = {i["id"] for i in items}
    for sid in summary:
        if sid not in item_ids:
            raise ValueError(f"summary id not in items: {sid!r}")
    return EvidenceRecord(
        version=str(data["version"]),
        source=str(data["source"]),
        mode=mode,  # type: ignore[arg-type]
        summary=summary,
        items=items,
    )


def load_record(path: Path | str) -> EvidenceRecord:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("evidence record root must be an object")
    return validate_record(raw)


def dump_record(record: EvidenceRecord, path: Path | str) -> None:
    validated = validate_record(dict(record))
    Path(path).write_text(
        json.dumps(validated, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def page_items(
    record: EvidenceRecord,
    *,
    offset: int = 0,
    limit: int = 10,
) -> list[EvidenceItem]:
    """Page full items after the summary-first read."""
    if offset < 0 or limit < 1:
        raise ValueError("offset must be >= 0 and limit >= 1")
    return list(record["items"][offset : offset + limit])


def make_record(
    *,
    source: str,
    mode: Mode = "clean",
    items: list[EvidenceItem],
    summary: list[str] | None = None,
    version: str = VERSION,
) -> EvidenceRecord:
    if summary is None:
        summary = [i["id"] for i in items]
    return validate_record(
        {
            "version": version,
            "source": source,
            "mode": mode,
            "summary": summary,
            "items": items,
        }
    )


def _is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _diff(a: Any, b: Any, tol: float, path: str = "value") -> str | None:
    """Return first structural difference between a (baseline) and b, or None."""
    if _is_num(a) and _is_num(b):
        return None if abs(a - b) <= tol else f"{path}: {a!r} != {b!r}"
    if isinstance(a, dict) and isinstance(b, dict):
        for k in a:
            if k not in b:
                return f"{path}.{k}: missing in candidate"
        for k in b:
            if k not in a:
                return f"{path}.{k}: unexpected in candidate"
        for k in a:
            d = _diff(a[k], b[k], tol, f"{path}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path}: length {len(a)} != {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            d = _diff(x, y, tol, f"{path}[{i}]")
            if d:
                return d
        return None
    if type(a) is not type(b) or a != b:
        return f"{path}: {a!r} != {b!r}"
    return None


def delta(
    baseline: EvidenceRecord,
    candidate: EvidenceRecord,
    *,
    tolerance: float = 0.0,
) -> list[DeltaRow]:
    """Per-item pass/fail of ``candidate`` against ``baseline``.

    Rows follow baseline item order, then candidate-only items. A baseline item
    passes when the candidate has the same id, the same kind, and a value equal
    under structural comparison (numbers within ``tolerance``). Candidate-only
    items pass with an "extra" note: the check gate only fails on what the
    baseline recorded. Raises ValueError if either record is invalid or the
    baseline is empty (an empty baseline cannot support a pass claim).
    """
    if tolerance < 0:
        raise ValueError("tolerance must be >= 0")
    base = validate_record(dict(baseline))
    cand = validate_record(dict(candidate))
    if not base["items"]:
        raise ValueError("baseline has no items; cannot claim pass")
    cand_by_id = {i["id"]: i for i in cand["items"]}
    base_ids = {i["id"] for i in base["items"]}
    rows: list[DeltaRow] = []
    for b in base["items"]:
        c = cand_by_id.get(b["id"])
        if c is None:
            rows.append({"id": b["id"], "pass": False, "note": "missing in candidate"})
        elif c["kind"] != b["kind"]:
            rows.append(
                {"id": b["id"], "pass": False,
                 "note": f"kind: {b['kind']!r} != {c['kind']!r}"}
            )
        else:
            d = _diff(b["value"], c["value"], tolerance)
            rows.append(
                {"id": b["id"], "pass": d is None, "note": d if d else "match"}
            )
    for c in cand["items"]:
        if c["id"] not in base_ids:
            rows.append({"id": c["id"], "pass": True, "note": "extra in candidate"})
    return rows


def all_pass(rows: list[DeltaRow]) -> bool:
    """True only for a non-empty delta with every row passing."""
    return bool(rows) and all(r["pass"] for r in rows)
