"""Phase 1 — evidence envelope load/dump round-trip."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
FIXTURE = SKILL_ROOT / "evals" / "fixtures" / "evidence_baseline.json"

sys.path.insert(0, str(SCRIPTS))

from evidence_envelope import (  # noqa: E402
    dump_record,
    load_record,
    make_record,
    page_items,
    validate_record,
)


def test_fixture_loads() -> None:
    rec = load_record(FIXTURE)
    assert rec["mode"] == "clean"
    assert len(rec["items"]) == 3
    assert rec["summary"] == ["layout-390", "palette-primary", "font-ui"]


def test_round_trip(tmp_path: Path) -> None:
    original = load_record(FIXTURE)
    out = tmp_path / "round.json"
    dump_record(original, out)
    again = load_record(out)
    assert again == original
    # raw JSON also stable for required keys
    raw = json.loads(out.read_text(encoding="utf-8"))
    assert set(raw.keys()) >= {"version", "source", "mode", "summary", "items"}


def test_summary_must_reference_items() -> None:
    with pytest.raises(ValueError, match="summary id"):
        validate_record(
            {
                "version": "0.1.0",
                "source": "x",
                "mode": "clean",
                "summary": ["missing"],
                "items": [
                    {
                        "id": "a",
                        "kind": "k",
                        "value": 1,
                        "confidence": "high",
                        "coverage": "c",
                        "limits": "l",
                    }
                ],
            }
        )


def test_page_items() -> None:
    rec = load_record(FIXTURE)
    page = page_items(rec, offset=1, limit=1)
    assert len(page) == 1
    assert page[0]["id"] == "palette-primary"


def test_make_record_defaults_summary() -> None:
    rec = make_record(
        source="https://example.com",
        mode="deep",
        items=[
            {
                "id": "js-1",
                "kind": "script",
                "value": {"src": "/app.js"},
                "confidence": "low",
                "coverage": "deep mode only",
                "limits": "not executed",
            }
        ],
    )
    assert rec["summary"] == ["js-1"]
    assert rec["mode"] == "deep"
