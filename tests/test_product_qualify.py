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


# ---- H7 product git gate -------------------------------------------------

import argparse
import subprocess
from pathlib import Path


import pytest


@pytest.fixture(autouse=True)
def _hermetic_git(monkeypatch, tmp_path):
    # tmp dirs may sit inside a parent work tree (e.g. a git-tracked home dir).
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))


def _git(cwd: Path, *a: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *a], check=True, capture_output=True)


def _tmp_ppq(monkeypatch, tmp_path: Path, root: Path):
    from tools.product_qualify import __main__ as ppq

    reg = tmp_path / "REGISTRY.yaml"
    reg.write_text(
        "version: 1\nproducts:\n  - id: demo\n    name: demo\n"
        f"    root: {root.as_posix()}\n    store_id: null\n    packaging: unknown\n"
        "    stage: P0\ndefaults:\n  x: 1\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(ppq, "REGISTRY", reg)
    monkeypatch.setattr(ppq, "PRODUCTS", tmp_path / "products")
    return ppq


def _ns(**kw):
    return argparse.Namespace(id="demo", force=False, init_git=False, create_remote=None, **kw)


def test_scaffold_warns_and_prints_commands_without_git(monkeypatch, tmp_path, capsys):
    root = tmp_path / "plain"
    root.mkdir()
    ppq = _tmp_ppq(monkeypatch, tmp_path, root)
    assert ppq.cmd_scaffold(_ns()) == 0
    cap = capsys.readouterr()
    assert "WARNING git gate" in cap.err and "not a git repo" in cap.err
    assert "git -C" in cap.out and "gh repo create <owner>/plain" in cap.out
    assert not (root / ".git").exists()  # never inits without --init-git
    assert "Q-010" in (tmp_path / "products" / "demo" / "QUALIFICATION.md").read_text(encoding="utf-8")


def test_scaffold_clean_with_git_and_origin(monkeypatch, tmp_path, capsys):
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "remote", "add", "origin", "https://example.invalid/x.git")
    ppq = _tmp_ppq(monkeypatch, tmp_path, root)
    assert ppq.cmd_scaffold(_ns()) == 0
    cap = capsys.readouterr()
    assert "git: ok" in cap.out and "WARNING" not in cap.err


def test_git_status_is_strict_about_repo_root(tmp_path):
    from tools.product_qualify.gitcheck import git_status

    repo = tmp_path / "outer"
    sub = repo / "inner"
    sub.mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "remote", "add", "origin", "https://example.invalid/x.git")
    st = git_status(sub)
    assert not st["ok"] and "inside another work tree" in st["reason"]
    assert git_status(repo)["ok"]
    _git(repo, "remote", "remove", "origin")
    assert "origin" in git_status(repo)["reason"]


def test_init_git_is_explicit_and_never_creates_remote(monkeypatch, tmp_path, capsys):
    root = tmp_path / "plain2"
    root.mkdir()
    ppq = _tmp_ppq(monkeypatch, tmp_path, root)
    ns = _ns()
    ns.init_git = True
    assert ppq.cmd_scaffold(ns) == 0
    assert (root / ".git").is_dir() and (root / ".gitignore").is_file()
    out = capsys.readouterr().out
    assert "Operator ACK required" in out and "gh repo create" in out
    r = subprocess.run(["git", "-C", str(root), "remote"], capture_output=True, text=True)
    assert r.stdout.strip() == ""


def test_github_presentation_style_root_is_never_init_suggested():
    from tools.product_qualify.gitcheck import commands_for, git_status

    st = git_status("C:/does/not/exist/test-installs/x/extracted")
    cmds = commands_for({**st, "root": "C:/p/test-installs/x/extracted", "exists": True,
                         "is_repo_root": False, "toplevel": None}, "extracted")
    assert len(cmds) == 1 and "do NOT init" in cmds[0]


def test_scan_dedupes_shared_roots(monkeypatch, tmp_path):
    root = tmp_path / "shared"
    root.mkdir()
    ppq = _tmp_ppq(monkeypatch, tmp_path, root)
    monkeypatch.setattr(ppq, "EXTRA_SCAN_ROOTS", {})
    monkeypatch.setattr(
        ppq, "load_registry",
        lambda: [{"id": "a", "root": root.as_posix()}, {"id": "b", "root": root.as_posix() + "/"}],
    )
    rows = ppq.scan_git_roots()
    assert len(rows) == 1 and rows[0]["products"] == ["a", "b"]


def test_ship_gate_pre_activate_refuses_without_git(monkeypatch, tmp_path, capsys):
    from tools.ship_gate import run as sg

    root = tmp_path / "nogit"
    root.mkdir()
    monkeypatch.setattr(
        sg, "load_registry",
        lambda: {"defaults": {}, "roots": [{"id": "demo", "store_id": "demo", "root": str(root)}]},
    )
    monkeypatch.setattr(sg, "_store_root", lambda reg: None)
    rc = sg.cmd_pre_activate(argparse.Namespace(product="demo", json=False))
    assert rc == 1
    assert "pre_activate blocked" in capsys.readouterr().err
