"""Product git gate: a product root must be its own git repo with an `origin`.

Valid = `git rev-parse --show-toplevel` equals the root (strict; not merely
inside some other work tree) AND `origin` is configured. Read-only helper;
never inits a repo or creates a remote (see commands_for()).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any


def _norm(p: str | Path) -> str:
    return os.path.normcase(os.path.realpath(str(p))).rstrip("\\/")


def _git(root: Path, *args: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, timeout=20, check=False,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return 127, str(e)
    return proc.returncode, (proc.stdout or "").strip()


def git_status(root: str | Path) -> dict[str, Any]:
    """Return {root, exists, is_repo_root, toplevel, origin, ok, reason}."""
    r = Path(str(root))
    out: dict[str, Any] = {
        "root": str(r), "exists": r.is_dir(), "is_repo_root": False,
        "toplevel": None, "origin": None, "ok": False, "reason": "",
    }
    if not r.is_dir():
        out["reason"] = "root directory missing"
        return out
    code, top = _git(r, "rev-parse", "--show-toplevel")
    if code != 0 or not top:
        out["reason"] = "not a git repo (no .git)"
        return out
    out["toplevel"] = top
    if _norm(top) != _norm(r):
        out["reason"] = f"inside another work tree ({top}), not its own repo root"
        return out
    out["is_repo_root"] = True
    code, url = _git(r, "remote", "get-url", "origin")
    if code != 0 or not url:
        out["reason"] = "no `origin` remote"
        return out
    out["origin"] = url
    out["ok"] = True
    return out


def commands_for(status: dict[str, Any], name: str) -> list[str]:
    """Exact operator-ACK commands for a root (printed, never run)."""
    root = status["root"]
    cmds: list[str] = []
    if "test-installs" in root.replace("\\", "/").lower():
        return ["# staged buyer copy (test-installs): find the real dev source repo first; do NOT init here"]
    if not status["exists"]:
        return [f"# root missing: {root} (fix REGISTRY root first)"]
    if not status["is_repo_root"]:
        if status["toplevel"]:
            return [f"# {root} is inside {status['toplevel']}; find/choose the product's own repo before init"]
        cmds += [
            f'git -C "{root}" init -b main',
            "# ensure .gitignore exists, review `git status`, then first commit",
        ]
    cmds += [
        f'gh repo create <owner>/{name} --private --source "{root}" --remote origin',
        f'# or: git -C "{root}" remote add origin <url>',
    ]
    return cmds


def ensure_gitignore(root: Path) -> bool:
    """Create a minimal .gitignore if absent. Returns True when created."""
    p = Path(root) / ".gitignore"
    if p.exists():
        return False
    p.write_text(".env\n*.session*\n__pycache__/\nnode_modules/\n.DS_Store\n", encoding="utf-8")
    return True
