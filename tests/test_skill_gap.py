"""Tests for PowerCore skill-gap gate + evals runner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _root_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POWERCORE_SKILL_GAP_ROOT", str(_REPO))
    monkeypatch.setenv("POWERCORE_SKILL_GAP_ENABLED", "1")


def test_catalog_loads_skills():
    from tools.skill_gap.catalog import load_skill_catalog

    cat = load_skill_catalog(_REPO)
    names = {e.name for e in cat}
    assert "powercore-skill-gap" in names
    assert "cc-report" in names
    assert len(cat) >= 10


def test_nearest_finds_silent_fail():
    from tools.skill_gap.catalog import load_skill_catalog, nearest_skills

    cat = load_skill_catalog(_REPO)
    near = nearest_skills(
        "run silent fail pass /silent-fail external stop evidence zombie",
        cat,
        limit=3,
    )
    assert near
    assert any("silent" in e.name for e, _ in near)


def test_gap_suggests_novel_procedure():
    from tools.skill_gap.gate import score_skill_gap

    gate = score_skill_gap(
        user_prompt=(
            "From now on, every time we fix a Vault Models refresh timeout we should "
            "follow a checklist and eventually make this a reusable Cursor skill "
            "across PowerCore repos — we keep forgetting the parallel hop refresh."
        ),
        ai_response=(
            "Going forward the procedure is: 1) classify provider 2) raise tray timeout "
            "3) parallel refresh_all_hops 4) restart daemon. Prefer powercore naming. "
            "This should be a portable agent-skills playbook with binary evals."
        ),
    )
    assert gate.score >= 40
    assert gate.should_suggest is True
    assert gate.proposed_name.startswith("powercore-")
    assert not gate.proposed_name.startswith("tbcc-")


def test_gap_scores_demote_always_on_to_skill():
    from tools.skill_gap.gate import score_skill_gap

    gate = score_skill_gap(
        user_prompt="demote heavy always-on gates to tips pointing at skills",
        ai_response=(
            "Tipified auto-crystallize and skill-gap always-on rules. Going forward "
            "load skill bodies on invoke; prefer powercore naming for any new "
            "portable checklist across agent-skills. rank_skills helps pick which "
            "skill to open after the prune."
        ),
    )
    assert gate.dimensions["repeatability"] >= 10
    assert gate.dimensions["transferability"] >= 8
    assert gate.score >= 35


def test_endgates_skips_trivial():
    from tools.skill_gap.endgates import run_endgates

    out = run_endgates(prompt="thanks", response="ok", auto=False)
    assert out["skipped"] is True


def test_tip_budget_tracks_endgates():
    from tools.skill_gap.metrics import measure_tip_budget

    budget = measure_tip_budget()
    assert budget["ok"] is True
    assert "endgates_tip_tok" in budget
    # Single tip should be lean
    if budget["endgates_tip_tok"]:
        assert budget["endgates_tip_tok"] <= 200


def test_gap_skips_strong_near_miss():
    from tools.skill_gap.gate import score_skill_gap

    # Heavy overlap with existing silent-fail skill should not mint a new skill
    gate = score_skill_gap(
        user_prompt="/silent-fail second-pass non-activity zombie pass",
        ai_response=(
            "Silent-fail protocol: external stops only, class-2 never_seen, "
            "tbcc-silent-fail skill, probe verdict ok stale idle blocked."
        ),
    )
    # May score mid but should_suggest false when nearest is very strong
    if gate.nearest and gate.nearest[0]["score"] >= 0.7:
        assert gate.should_suggest is False


def test_evals_cc_report_pass():
    from tools.skill_gap.evals_runner import run_evals_file

    path = _REPO / ".cursor" / "skills" / "cc-report" / "evals" / "evals.json"
    result = run_evals_file(path)
    assert result["ok"] is True
    assert result["total"] >= 6
    assert result["passed"] == result["total"]


def test_body_assertions_cc_report():
    from tools.skill_gap.body_assertions import run_body_assertions

    skill_dir = _REPO / ".cursor" / "skills" / "cc-report"
    result = run_body_assertions(skill_dir)
    assert result["ok"] is True
    assert result["total"] >= 3


def test_versions_seed_pin_rollback(tmp_path: Path):
    from tools.skill_gap import versions as V

    skill = tmp_path / "demo-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# demo\nPASTE INTO CURSOR\n", encoding="utf-8")
    (skill / "evals").mkdir()

    seed = V.ensure_seed(skill, score="1/1", note="test seed")
    assert seed is not None
    assert seed.id.startswith("v0001_")
    assert (V.versions_dir(skill) / seed.file).is_file()
    assert V.load_index(skill).current == seed.id

    # Second seed is no-op
    assert V.ensure_seed(skill) is None

    # Mutate skill, snapshot overnight-style
    (skill / "SKILL.md").write_text("# demo v2\nPASTE INTO CURSOR\nDo not:\n", encoding="utf-8")
    snap = V.snapshot(skill, score="2/2", note="keep", source="overnight")
    assert snap.parent == seed.id
    assert V.load_index(skill).current == snap.id

    V.pin(skill, seed.id)
    data = V.list_versions(skill)
    assert seed.id in data["pinned"]

    # Rollback to seed → new CURRENT forked from seed
    rb = V.rollback(skill, seed.id, note="felt better")
    assert rb.source == "rollback"
    assert rb.parent == seed.id
    assert V.load_index(skill).current == rb.id
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("# demo\n")
    assert "Do not:" not in text
    # Old tip still in index
    assert snap.id in {e.id for e in V.load_index(skill).entries}


def test_overnight_demo_break_recovers():
    import subprocess
    import sys

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.skill_gap.overnight_loop",
            "--skill",
            "cc-report",
            "--demo-break",
            "--until-perfect",
            "--max-iters",
            "5",
            "--sleep",
            "0",
        ],
        cwd=str(_REPO),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "perfect" in proc.stdout.lower() or "kept" in proc.stdout.lower()
    # Skill must still contain PASTE INTO CURSOR after recovery
    text = (_REPO / ".cursor" / "skills" / "cc-report" / "SKILL.md").read_text(encoding="utf-8")
    assert "PASTE INTO CURSOR" in text
    assert "PASTE_INTO_CURSOR_REMOVED" not in text


def test_evals_silent_fail_pass():
    from tools.skill_gap.evals_runner import run_evals_file

    path = _REPO / ".cursor" / "skills" / "tbcc-silent-fail" / "evals" / "evals.json"
    result = run_evals_file(path)
    assert result["ok"] is True


def test_scaffold_surfaces_triple(tmp_path: Path):
    from tools.skill_gap.scaffold_surfaces import check_surfaces, scaffold_surfaces

    repo = tmp_path / "agent-skills"
    (repo / ".cursor" / "skills").mkdir(parents=True)
    claude_a = tmp_path / "proj-a"
    claude_b = tmp_path / "proj-b"
    claude_a.mkdir()
    claude_b.mkdir()

    out = scaffold_surfaces(
        "powercore-demo-surface",
        title="Demo Surface",
        description="Demo skill for Triple Surface tests. Use when testing scaffold.",
        repo=repo,
        claude_roots=[claude_a, claude_b],
        force=False,
    )
    assert out["actions"]["cursor"] == "wrote"
    assert out["check"]["ok"] is True
    assert (repo / ".cursor" / "skills" / "powercore-demo-surface" / "SKILL.md").is_file()
    assert (claude_a / ".claude" / "skills" / "powercore-demo-surface" / "SKILL.md").is_file()
    assert (claude_b / ".claude" / "skills" / "powercore-demo-surface" / "SKILL.md").is_file()
    paste = repo / "docs" / "gpt-paste" / "POWERCORE_DEMO_SURFACE_GPT_PASTE.md"
    assert paste.is_file()
    assert "ZERO prior chat context" in paste.read_text(encoding="utf-8")

    # Idempotent skip
    out2 = scaffold_surfaces(
        "powercore-demo-surface",
        repo=repo,
        claude_roots=[claude_a],
        force=False,
    )
    assert out2["actions"]["cursor"] == "skipped_exists"

    report = check_surfaces(
        "powercore-demo-surface",
        repo=repo,
        claude_roots=[claude_a, claude_b],
    )
    assert report["ok"] is True


def test_scaffold_surfaces_cli_check(tmp_path: Path):
    import subprocess
    import sys

    from tools.skill_gap.scaffold_surfaces import scaffold_surfaces

    repo = tmp_path / "agent-skills"
    (repo / ".cursor" / "skills").mkdir(parents=True)
    proj = tmp_path / "proj"
    proj.mkdir()
    scaffold_surfaces(
        "powercore-cli-check",
        repo=repo,
        claude_roots=[proj],
    )
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.skill_gap.scaffold_surfaces",
            "--skill",
            "powercore-cli-check",
            "--root",
            str(repo),
            "--claude-root",
            str(proj),
            "--check",
            "--json",
        ],
        cwd=str(_REPO),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["ok"] is True


def test_run_gate_cli_json():
    import subprocess
    import sys

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.skill_gap.run_gate",
            "--prompt",
            "ok",
            "--response",
            "ok",
            "--json",
        ],
        cwd=str(_REPO),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["ok"] is True
    assert data["gate"]["tier"] == "skip"


@pytest.mark.parametrize(
    "text",
    [
        "",
        "nothing relevant here at all",
        "we saw a gap",
        "the vault",
        "weekly report",
        "it will fail",
        "silent",
        "ops",
        "store",
    ],
)
def test_slugify_rejects_untitled_and_bare_generic(text: str):
    from tools.skill_gap.gate import _slugify_proposal

    assert _slugify_proposal(text) == ""


def test_slugify_accepts_multi_keyword_and_explicit_name():
    from tools.skill_gap.gate import _slugify_proposal, is_valid_slug

    assert _slugify_proposal("refresh the vault models timeout") == (
        "powercore-refresh-vault-models-timeout"
    )
    assert _slugify_proposal("use powercore-foo-bar here") == "powercore-foo-bar"
    assert not is_valid_slug("powercore-untitled")
    assert not is_valid_slug("powercore-gap")
    assert not is_valid_slug("powercore-ops")
    assert not is_valid_slug("powercore-store")
    assert not is_valid_slug("tbcc-anything")


def test_endgates_log_records_proposed_slug_and_score(monkeypatch, tmp_path: Path):
    from tools.skill_gap import metrics

    monkeypatch.setattr(metrics, "_METRICS_DIR", tmp_path)
    monkeypatch.setattr(metrics, "_ENDGATES_LOG", tmp_path / "endgates.jsonl")
    metrics.append_endgates_log(
        {"lines": ["x"], "skill_gap": {"should_suggest": True, "proposed_name": "powercore-a-b", "score": 55}}
    )
    metrics.append_endgates_log({"lines": ["y"], "skill_gap": {"should_suggest": False}})
    rows = [json.loads(r) for r in (tmp_path / "endgates.jsonl").read_text().splitlines()]
    assert rows[0]["proposed_slug"] == "powercore-a-b" and rows[0]["score"] == 55
    assert "proposed_slug" not in rows[1]


def test_pending_aggregates_structured_and_legacy(tmp_path: Path):
    from tools.skill_gap.pending import load_pending

    log = tmp_path / "e.jsonl"
    rows = [
        {"ts": "2026-10-01T00:00:00", "proposed_slug": "powercore-a-b", "score": 50},
        {"ts": "2026-10-02T00:00:00", "proposed_slug": "powercore-a-b", "score": 60},
        {"ts": "2026-09-01T00:00:00", "skill_gap_suggest": True,
         "lines": ["Skill gap suggested (45) -> powercore-old-one — nearest: x"]},
        {"ts": "2026-09-02T00:00:00", "skill_gap_suggest": True,
         "lines": ["Skill gap suggested (70) -> powercore-untitled — nearest: x"]},
    ]
    log.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    cur = load_pending(log)
    assert [v["slug"] for v in cur] == ["powercore-a-b"]
    assert cur[0]["count"] == 2 and cur[0]["max_score"] == 60
    assert cur[0]["last_seen"] == "2026-10-02T00:00:00"
    both = load_pending(log, legacy=True)
    assert {v["slug"] for v in both} == {"powercore-a-b", "powercore-old-one"}


def test_rank_goldens_cover_required_cases():
    cases = json.loads(
        (_REPO / "tools" / "skill_gap" / "evals" / "rank_skills_cases.json").read_text(
            encoding="utf-8"
        )
    )
    ids = {c["id"] for c in cases}
    assert len(cases) >= 12
    assert sum(1 for c in cases if c.get("expect_skip")) >= 2
    tops = {c.get("expect_top1") for c in cases}
    assert {"powercore-promo-capture", "powercore-product-qualify", "powercore-ux-prefs"} <= tops
    assert any(i.startswith("tbcc-only") for i in ids)


def test_utilization_histogram_and_limit_note(tmp_path: Path):
    from tools.skill_gap.utilization import LIMIT_NOTE, summarize

    log = tmp_path / "e.jsonl"
    rows = [
        {"ranked_top": "a", "skill_gap_suggest": True},
        {"ranked_top": "a"},
        {"ranked_top": "b"},
        {"skipped": True},
    ]
    log.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    s = summarize(log, last_n=10)
    assert s["n"] == 4 and s["suggest_rate"] == 0.25 and s["skipped_trivial"] == 1
    assert s["ranked_top_histogram"] == {"a": 2, "b": 1}
    assert "not skills opened" in LIMIT_NOTE


def _tmp_rules(tmp_path: Path) -> list[Path]:
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "t.mdc").write_text("---\nalwaysApply: true\n---\n" + "x" * 400, encoding="utf-8")
    (rules / "n.mdc").write_text("---\nalwaysApply: false\n---\nskip", encoding="utf-8")
    return [rules]


def test_utilization_report_happy_path(tmp_path: Path):
    from tools.skill_gap.utilization import build_report

    log = tmp_path / "e.jsonl"
    log.write_text(json.dumps({"ranked_top": "a", "skill_gap_suggest": True}), encoding="utf-8")
    r = build_report(10, _tmp_rules(tmp_path), log_path=log)
    assert r["n"] == 1 and r["ranked_top_histogram"] == {"a": 1}
    assert [t["name"] for t in r["tips"]] == ["t.mdc"]
    assert set(r["tips"][0]) == {"name", "tok", "over_single", "path"}
    assert r["total_tok"] == r["tips"][0]["tok"] > 0


def test_utilization_report_empty_log(tmp_path: Path):
    from tools.skill_gap.utilization import build_report

    r = build_report(10, _tmp_rules(tmp_path), log_path=tmp_path / "missing.jsonl")
    assert r["n"] == 0 and r["suggest_rate"] is None and r["ranked_top_histogram"] == {}


def test_utilization_report_banner_plain_and_json(tmp_path: Path):
    from tools.skill_gap.utilization import LIMIT_NOTE, TIP_NOTE, build_report, format_report

    r = build_report(10, _tmp_rules(tmp_path), log_path=tmp_path / "missing.jsonl")
    assert LIMIT_NOTE in r["limit"] and TIP_NOTE in r["limit"]
    plain = format_report(r)
    assert plain.startswith(LIMIT_NOTE) and TIP_NOTE in plain.splitlines()[1]


def test_rank_evals_cli_nonzero_on_miss(monkeypatch, tmp_path: Path):
    from tools.skill_gap import metrics
    from tools.skill_gap.run_rank_evals import main

    monkeypatch.setattr(metrics, "_METRICS_DIR", tmp_path)
    monkeypatch.setattr(metrics, "_MISS_LOG", tmp_path / "miss.jsonl")

    bad = tmp_path / "c.json"
    bad.write_text(
        json.dumps([{"id": "x", "prompt": "/silent-fail", "response": "silent-fail zombie",
                     "expect_top1": "no-such-skill"}]),
        encoding="utf-8",
    )
    assert main(["--cases", str(bad)]) == 1


@pytest.mark.parametrize(
    "prompt",
    ["thanks", "thanks!", "okay, got it", "ok thanks", "yes and thanks", "Thank you.", "👍"],
)
def test_trivial_ack_positive(prompt: str):
    from tools.skill_gap.trivial import is_trivial_ack

    assert is_trivial_ack(prompt)


@pytest.mark.parametrize(
    "prompt",
    [
        "okay, run the deploy",
        "yes, and also fix X",
        "thanks, now ship the store SKU",
        "",
        "ok " * 20,
    ],
)
def test_trivial_ack_negative(prompt: str):
    from tools.skill_gap.trivial import is_trivial_ack

    assert not is_trivial_ack(prompt)


def test_rank_and_endgates_share_ack_pattern():
    from tools.skill_gap import endgates, rank_skills

    assert endgates.is_trivial_ack is rank_skills.is_trivial_ack
    assert rank_skills.rank_skills_for_invoke(
        user_prompt="okay, got it", ai_response="Great, let me know."
    ) == []


def test_compact_writes_dated_stub_and_never_overwrites(tmp_path: Path):
    from datetime import datetime

    from tools.skill_gap.compact import write_compact

    now = datetime(2026, 10, 2, 14, 5)
    a = write_compact(goal="Ship the Gate!", done=["x (abc123)"], next_steps=["y"],
                      verify="pytest -q", out_dir=tmp_path, now=now)
    b = write_compact(goal="Ship the Gate!", out_dir=tmp_path, now=now)
    assert a.name == "2026-10-02_1405_compact_ship-the-gate.md"
    assert b != a and b.name.endswith("-2.md")
    text = a.read_text(encoding="utf-8")
    assert "- x (abc123)" in text and "pytest -q" in text and "tbcc-auto-crystallize" in text
    assert "TODO" in b.read_text(encoding="utf-8")


def test_compact_cli_prints_path(tmp_path: Path, capsys):
    from tools.skill_gap.compact import main

    assert main(["--goal", "g", "--out-dir", str(tmp_path)]) == 0
    assert str(tmp_path) in capsys.readouterr().out
