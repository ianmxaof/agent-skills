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


# ---- Phase 2: delta gate ---------------------------------------------------

from evidence_envelope import all_pass, delta  # noqa: E402

CANDIDATE = SKILL_ROOT / "evals" / "fixtures" / "evidence_candidate.json"


def _rows_by_id(rows: list[dict]) -> dict[str, dict]:
    return {r["id"]: r for r in rows}


def test_delta_fixture_known_pass_and_fail() -> None:
    rows = _rows_by_id(delta(load_record(FIXTURE), load_record(CANDIDATE)))
    assert rows["layout-390"]["pass"] is True  # identical
    assert rows["palette-primary"]["pass"] is False  # #1A1A1A vs #222222
    assert "hex" in rows["palette-primary"]["note"]
    assert rows["font-ui"]["pass"] is False  # absent in candidate
    assert rows["font-ui"]["note"] == "missing in candidate"
    assert rows["extra-spacing"] == {
        "id": "extra-spacing", "pass": True, "note": "extra in candidate"
    }


def test_delta_self_is_all_pass() -> None:
    base = load_record(FIXTURE)
    rows = delta(base, base)
    assert [r["id"] for r in rows] == ["layout-390", "palette-primary", "font-ui"]
    assert all_pass(rows)


def test_delta_mismatch_is_not_all_pass() -> None:
    assert not all_pass(delta(load_record(FIXTURE), load_record(CANDIDATE)))
    assert not all_pass([])


def test_delta_tolerance_and_kind() -> None:
    base = load_record(FIXTURE)
    cand = load_record(FIXTURE)
    cand["items"][0]["value"]["hero_height_px"] = 424
    assert delta(base, cand)[0]["pass"] is False
    assert delta(base, cand, tolerance=4)[0]["pass"] is True
    cand["items"][1]["kind"] = "font"
    assert "kind" in delta(base, cand, tolerance=4)[1]["note"]


def test_delta_rejects_empty_baseline_and_bad_tolerance() -> None:
    empty = make_record(source="x", items=[])
    with pytest.raises(ValueError, match="no items"):
        delta(empty, load_record(CANDIDATE))
    with pytest.raises(ValueError, match="tolerance"):
        delta(load_record(FIXTURE), load_record(CANDIDATE), tolerance=-1)


# ---- Phase 3: dry brief card -----------------------------------------------

EXAMPLE = SKILL_ROOT / "evals" / "fixtures" / "example_brief.md"


def test_example_brief_matches_renderer() -> None:
    from render_brief import render_brief

    text = render_brief(load_record(FIXTURE), load_record(CANDIDATE), date="2026-11-02")
    assert EXAMPLE.read_text(encoding="utf-8").replace("\r\n", "\n") == text


def test_brief_without_candidate_does_not_score() -> None:
    from render_brief import render_brief

    text = render_brief(load_record(FIXTURE))
    assert "Awaiting build" in text
    assert "Overall:" not in text
    for heading in ("## Source", "## Evidence summary", "## Build brief",
                    "## Check delta (after build)", "## Next"):
        assert heading in text


def test_compose_mapping_note_names_all_sources() -> None:
    note = (SKILL_ROOT / "references" / "compose-mapping.md").read_text(encoding="utf-8")
    for name in ("powercore-website-clone", "powercore-website-feature-scan",
                 "powercore-site-map-tree"):
        assert name in note
