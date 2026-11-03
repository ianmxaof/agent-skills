#!/usr/bin/env python3
"""Evidence envelope for powercore-cleanroom-brief (Phase 1).

Locked item fields: id, kind, value, confidence, coverage, limits.
Record carries optional mode (clean|deep). Summary-first: ``summary`` is a short
list of item ids (or thin stubs); full items live in ``items`` and may be paged
by callers via ``page_items``.

Phase 2 adds ``delta(baseline, candidate)`` — not in this module yet.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal, TypedDict

VERSION = "0.1.0"

Confidence = Literal["high", "medium", "low"]
Mode = Literal["clean", "deep"]


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
