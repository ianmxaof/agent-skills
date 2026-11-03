"""Ship Gate unit tests (no live island / R2)."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from tools.ship_gate.tree_hash import short_hash, tree_hash
from tools.ship_gate.verdicts import (
    SEVERITY,
    VERDICT_MAP_VERSION,
    severity_rank,
    worst_verdict,
)
from tools.ship_gate.zip_manifest import check_zip_manifest


def test_fail_beats_ok():
    assert severity_rank("fail") < severity_rank("ok")
    assert worst_verdict(["ok", "fail"]) == "fail"
    assert worst_verdict(["ok", "idle"]) == "ok"


def test_parity_with_tbcc_vendor():
    tbcc = (
        Path(r"C:\Powercore-repo-main\telegram_bot2\tbcc\backend\app\services")
        / "silent_fail_verdicts.py"
    )
    assert tbcc.is_file()
    text = tbcc.read_text(encoding="utf-8")
    assert 'VERDICT_MAP_VERSION = "psg-1"' in text
    assert '"fail": 0' in text
    assert VERDICT_MAP_VERSION == "psg-1"
    assert SEVERITY["fail"] == 0


def test_tree_hash_stable(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    h1 = tree_hash(tmp_path, ["**/*"], [])
    h2 = tree_hash(tmp_path, ["**/*"], [])
    assert h1 == h2
    assert len(h1) == 64
    assert short_hash(h1) == h1[:8]
    (tmp_path / "a.txt").write_text("hello!", encoding="utf-8")
    assert tree_hash(tmp_path, ["**/*"], []) != h1


def test_zip_manifest_ok_and_missing(tmp_path: Path):
    ext = tmp_path / "extension"
    ext.mkdir()
    (ext / "background.js").write_text("// bg", encoding="utf-8")
    (ext / "options.html").write_text("<html></html>", encoding="utf-8")
    manifest = {
        "manifest_version": 3,
        "version": "1.0.0",
        "background": {"service_worker": "background.js"},
        "options_ui": {"page": "options.html"},
    }
    (ext / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    zpath = tmp_path / "dist" / "te-1.0.0.zip"
    zpath.parent.mkdir()
    with zipfile.ZipFile(zpath, "w") as zf:
        for f in ext.iterdir():
            zf.write(f, f.name)
    ok = check_zip_manifest(zpath, expected_version="1.0.0")
    assert ok["verdict"] == "ok"

    # Missing background
    z2 = tmp_path / "dist" / "te-bad.zip"
    with zipfile.ZipFile(z2, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("options.html", "<html></html>")
    bad = check_zip_manifest(z2, expected_version="1.0.0")
    assert bad["verdict"] == "fail"
    assert "background.js" in bad["evidence"]


def test_live_json_path_and_idle_flag(tmp_path: Path, monkeypatch):
    from tools.ship_gate.live import flag_is_off, json_path_get, resolve_idle

    assert json_path_get({"status": "ok"}, "$.status") == "ok"
    assert flag_is_off("0")
    assert not flag_is_off("1")
    monkeypatch.delenv("TBCC_REVENUE_ISLAND_ACTIVE", raising=False)
    (tmp_path / ".env").write_text("TBCC_REVENUE_ISLAND_ACTIVE=0\n", encoding="utf-8")
    idle = resolve_idle("TBCC_REVENUE_ISLAND_ACTIVE", search_roots=[tmp_path])
    assert idle is not None
    assert idle["verdict"] == "idle"
    assert "TBCC_REVENUE_ISLAND_ACTIVE=0" in idle["evidence"]


def test_stress_thresholds_and_expiry(tmp_path: Path):
    from datetime import datetime, timedelta, timezone

    from tools.ship_gate.stress import (
        apply_latency_threshold,
        apply_probe_threshold,
        check_stress_fresh,
        write_stress_evidence,
    )

    gated = apply_latency_threshold([1.0] * 100, {"p95_ms_max": 50, "min_iterations": 100})
    assert gated["verdict"] == "ok"
    slow = apply_latency_threshold([80.0] * 100, {"p95_ms_max": 50, "min_iterations": 100})
    assert slow["verdict"] == "fail"

    probe = apply_probe_threshold(
        {
            "verdict": "stale",
            "surfaces": [
                {"id": "island_api_health", "verdict": "ok"},
                {"id": "loot_public_cta", "verdict": "ok"},
                *[{"id": f"b{i}", "verdict": "ok"} for i in range(10)],
                {"id": "gumroad_default", "verdict": "stale"},
            ],
        },
        {
            "require_surface_ok": ["island_api_health", "loot_public_cta"],
            "min_ok_surfaces": 10,
            "max_fail_surfaces": 0,
            "allow_worst": ["ok", "idle", "stale"],
        },
        "stale",
    )
    assert probe["verdict"] == "ok"

    skills = tmp_path / "agent-skills"
    write_stress_evidence(
        skills,
        root_id="text-expander",
        product_id="text-expander",
        payload={
            "run_id": "rtest",
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "worst": "ok",
            "lane": "stress",
        },
    )
    fresh = check_stress_fresh(skills, "text-expander")
    assert fresh["ok"] is True

    old = write_stress_evidence(
        skills,
        root_id="old",
        product_id=None,
        payload={
            "run_id": "rold",
            "ts": (datetime.now(timezone.utc) - timedelta(days=8)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "worst": "ok",
        },
    )
    assert old.exists()
    expired = check_stress_fresh(skills, "old")
    assert expired["ok"] is False
    assert "expired" in expired["reason"]
