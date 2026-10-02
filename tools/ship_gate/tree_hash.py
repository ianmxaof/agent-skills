"""Tree hash for registered roots — no git dependency."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable


def _iter_files(root: Path, patterns: list[str], ignore: list[str]) -> Iterable[Path]:
    root = root.resolve()
    if not root.is_dir():
        return
    # Default: all files under root when patterns empty
    if not patterns:
        candidates = [p for p in root.rglob("*") if p.is_file()]
    else:
        candidates = []
        for pat in patterns:
            # Support ** globs relative to root
            candidates.extend(root.glob(pat))
        candidates = [p for p in candidates if p.is_file()]

    ignore_parts = ignore or []
    for path in sorted(set(candidates), key=lambda p: str(p).replace("\\", "/").lower()):
        rel = path.relative_to(root).as_posix()
        skipped = False
        for ig in ignore_parts:
            ig_n = ig.replace("\\", "/")
            if ig_n.endswith("/**"):
                prefix = ig_n[:-3]
                if rel == prefix or rel.startswith(prefix + "/"):
                    skipped = True
                    break
            elif "**/" in ig_n or ig_n.startswith("**/"):
                # simple suffix / name match
                suffix = ig_n.split("**/")[-1]
                if rel.endswith(suffix) or Path(rel).name == suffix.lstrip("*"):
                    skipped = True
                    break
            elif rel == ig_n or rel.startswith(ig_n.rstrip("*")):
                skipped = True
                break
        if skipped:
            continue
        yield path


def tree_hash(root: Path, paths: list[str] | None = None, ignore: list[str] | None = None) -> str:
    """Content + relative path hash (sha256 hex). Empty tree → zeros."""
    h = hashlib.sha256()
    count = 0
    for path in _iter_files(root, paths or [], ignore or []):
        rel = path.relative_to(root.resolve()).as_posix().encode("utf-8")
        h.update(rel)
        h.update(b"\0")
        try:
            h.update(path.read_bytes())
        except OSError:
            h.update(b"MISSING")
        h.update(b"\0")
        count += 1
    if count == 0:
        return "0" * 64
    return h.hexdigest()


def short_hash(full: str, n: int = 8) -> str:
    return (full or "")[:n]
