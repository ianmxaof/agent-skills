"""PPQ CLI unit tests (no network)."""

from __future__ import annotations

from tools.product_qualify.__main__ import missed_blockers, read_stage, _parse_registry_products


def test_read_stage():
    md = "# x\n\n**Stage:** P3  \n**Updated:** x\n"
    assert read_stage(md) == "P3"


def test_missed_blockers():
    md = """
| id | stage | status | kind | blocker | evidence |
|----|------:|--------|------|---------|----------|
| Q-001 | P0 | covered | auto | yes | ok |
| Q-002 | P2 | missed | manual | yes | gap |
| Q-003 | P2 | missed | manual | no | soft |
| Q-004 | P3 | blocked | manual | yes | wait |
"""
    assert missed_blockers(md) == ["Q-002"]


def test_parse_registry():
    text = """
version: 1
products:
  - id: vault
    name: Vault
    stage: P3
  - id: pc-notes
    store_id: pc-notes
    packaging: desktop-zip
defaults:
  x: y
"""
    products = _parse_registry_products(text)
    assert [p["id"] for p in products] == ["vault", "pc-notes"]
    assert products[0]["stage"] == "P3"
    assert products[1]["packaging"] == "desktop-zip"
