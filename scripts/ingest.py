#!/usr/bin/env python3
"""Ingest a GitHub URL, git repo, or local folder into vendor/incoming/.

Examples:
  py -3.13 scripts/ingest.py https://github.com/spencerpauly/awesome-cursor-skills
  py -3.13 scripts/ingest.py https://github.com/org/repo/tree/main/resources/prompt-engineering
  py -3.13 scripts/ingest.py C:\\path\\to\\skill-folder --name my-skill
  py -3.13 scripts/ingest.py https://raw.githubusercontent.com/.../SKILL.md --name prompt-engineering
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from _lib import REPO_ROOT, load_catalog, load_config, save_catalog, slugify, utc_now


def parse_github_url(url: str) -> dict[str, str] | None:
    """Return {owner, repo, ref, subpath} or None."""
    url = url.strip().rstrip("/")
    m = re.match(
        r"https?://github\.com/([^/]+)/([^/]+)(?:/tree/([^/]+)(?:/(.*))?)?$",
        url,
    )
    if not m:
        return None
    owner, repo, ref, subpath = m.group(1), m.group(2), m.group(3), m.group(4)
    if repo.endswith(".git"):
        repo = repo[:-4]
    return {
        "owner": owner,
        "repo": repo,
        "ref": ref or "main",
        "subpath": (subpath or "").strip("/"),
    }


def git_clone_shallow(repo_url: str, dest: Path, ref: str | None = None) -> None:
    cmd = ["git", "clone", "--depth", "1"]
    if ref:
        cmd.extend(["--branch", ref])
    cmd.extend([repo_url, str(dest)])
    # Some repos use master; retry without branch if branch fails
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as first:
        if ref and ref != "master":
            cmd2 = ["git", "clone", "--depth", "1", "--branch", "master", repo_url, str(dest)]
            try:
                subprocess.run(cmd2, check=True, capture_output=True, text=True)
                return
            except subprocess.CalledProcessError:
                pass
        # last try: default branch
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(dest)],
            check=True,
            capture_output=True,
            text=True,
        )


def download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as resp:
        dest.write_bytes(resp.read())


def strip_nested_git(path: Path) -> None:
    git_dir = path / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir, ignore_errors=True)


def ingest_github(url: str, dest_name: str | None) -> Path:
    cfg = load_config()
    incoming = REPO_ROOT / cfg["incoming_dir"]
    incoming.mkdir(parents=True, exist_ok=True)

    # raw file
    if "raw.githubusercontent.com" in url or url.endswith(".md") or url.endswith(".mdc"):
        name = dest_name or slugify(Path(url.split("?")[0]).stem)
        batch = incoming / f"{utc_now()[:10]}_{name}"
        batch.mkdir(parents=True, exist_ok=True)
        filename = Path(url.split("?")[0]).name
        target = batch / filename
        download_file(url, target)
        # if SKILL.md alone, wrap as skill folder
        if filename.lower() == "skill.md":
            skill_dir = batch / name
            skill_dir.mkdir(exist_ok=True)
            shutil.move(str(target), str(skill_dir / "SKILL.md"))
            return skill_dir
        return batch

    parsed = parse_github_url(url)
    if not parsed:
        raise SystemExit(f"Unrecognized GitHub URL: {url}")

    name = dest_name or slugify(parsed["repo"] if not parsed["subpath"] else Path(parsed["subpath"]).name)
    stamp = utc_now()[:10]
    dest = incoming / f"{stamp}_{name}"
    if dest.exists():
        shutil.rmtree(dest)

    repo_url = f"https://github.com/{parsed['owner']}/{parsed['repo']}.git"
    with tempfile.TemporaryDirectory(prefix="agent-skills-ingest-") as tmp:
        tmp_path = Path(tmp) / "clone"
        print(f"Cloning {repo_url} ...")
        git_clone_shallow(repo_url, tmp_path, parsed["ref"])
        src = tmp_path
        if parsed["subpath"]:
            src = tmp_path / parsed["subpath"]
            if not src.exists():
                raise SystemExit(f"Subpath not found in repo: {parsed['subpath']}")
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            dest.mkdir(parents=True)
            shutil.copy2(src, dest / src.name)
    strip_nested_git(dest)
    # write provenance
    (dest / "SOURCE.txt").write_text(
        f"source: {url}\ningested_at: {utc_now()}\nowner: {parsed['owner']}\nrepo: {parsed['repo']}\n",
        encoding="utf-8",
    )
    return dest


def ingest_local(path: Path, dest_name: str | None) -> Path:
    cfg = load_config()
    incoming = REPO_ROOT / cfg["incoming_dir"]
    incoming.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        raise SystemExit(f"Path not found: {path}")
    name = dest_name or slugify(path.name)
    dest = incoming / f"{utc_now()[:10]}_{name}"
    if dest.exists():
        shutil.rmtree(dest)
    if path.is_dir():
        shutil.copytree(path, dest, ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"))
    else:
        dest.mkdir(parents=True)
        shutil.copy2(path, dest / path.name)
    (dest / "SOURCE.txt").write_text(
        f"source: {path.resolve()}\ningested_at: {utc_now()}\n",
        encoding="utf-8",
    )
    return dest


def register_batch(dest: Path, source: str) -> None:
    cfg = load_config()
    catalog = load_catalog(cfg)
    item_id = dest.name
    catalog["items"][item_id] = {
        "id": item_id,
        "source": source,
        "incoming_path": str(dest.relative_to(REPO_ROOT)).replace("\\", "/"),
        "ingested_at": utc_now(),
        "status": "incoming",
        "kind": None,
        "units": [],
        "operator_boost": 0,
        "use_count": 0,
        "importance": None,
        "notes": "",
    }
    save_catalog(catalog, cfg)


def main() -> int:
    ap = argparse.ArgumentParser(description="Dump a skill/rule/command source into vendor/incoming")
    ap.add_argument("source", help="GitHub URL, raw file URL, or local path")
    ap.add_argument("--name", help="Override destination folder slug")
    ap.add_argument("--sort", action="store_true", help="Run sort.py immediately after ingest")
    args = ap.parse_args()

    src = args.source.strip()
    if src.startswith("http://") or src.startswith("https://"):
        dest = ingest_github(src, args.name)
    else:
        dest = ingest_local(Path(src), args.name)

    register_batch(dest, src)
    print(f"Ingested -> {dest.relative_to(REPO_ROOT)}")
    print("Status: incoming (not live). Run: py -3.13 scripts/sort.py")

    if args.sort:
        from sort import sort_all

        sort_all()
    return 0


if __name__ == "__main__":
    # allow running as script from scripts/ or repo root
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
