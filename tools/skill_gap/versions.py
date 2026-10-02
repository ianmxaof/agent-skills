"""Immutable skill version snapshots + CURRENT pointer (rollback / pin / fork)."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

Source = Literal["seed", "overnight", "rollback", "manual", "pin"]


@dataclass
class VersionEntry:
    id: str
    file: str
    ts: str
    score: str = ""
    note: str = ""
    parent: str | None = None
    source: str = "manual"
    pinned: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VersionIndex:
    current: str | None = None
    entries: list[VersionEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "current": self.current,
            "entries": [e.to_dict() for e in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VersionIndex:
        entries = [
            VersionEntry(**{k: v for k, v in e.items() if k in VersionEntry.__dataclass_fields__})
            for e in (data.get("entries") or [])
            if isinstance(e, dict) and e.get("id")
        ]
        return cls(current=data.get("current"), entries=entries)


def versions_dir(skill_dir: Path) -> Path:
    return skill_dir / "evals" / "versions"


def index_path(skill_dir: Path) -> Path:
    return versions_dir(skill_dir) / "index.json"


def current_path(skill_dir: Path) -> Path:
    return versions_dir(skill_dir) / "CURRENT"


def changelog_path(skill_dir: Path) -> Path:
    return versions_dir(skill_dir) / "CHANGELOG.md"


def load_index(skill_dir: Path) -> VersionIndex:
    path = index_path(skill_dir)
    if not path.is_file():
        return VersionIndex()
    try:
        return VersionIndex.from_dict(json.loads(path.read_text(encoding="utf-8")))
    except Exception:
        return VersionIndex()


def save_index(skill_dir: Path, index: VersionIndex) -> None:
    d = versions_dir(skill_dir)
    d.mkdir(parents=True, exist_ok=True)
    index_path(skill_dir).write_text(
        json.dumps(index.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if index.current:
        current_path(skill_dir).write_text(index.current + "\n", encoding="utf-8")


def _next_seq(index: VersionIndex) -> int:
    best = 0
    for e in index.entries:
        m = re.match(r"v(\d+)", e.id)
        if m:
            best = max(best, int(m.group(1)))
    return best + 1


def _make_id(seq: int, score: str) -> tuple[str, str]:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    score_slug = re.sub(r"[^\d]+", "-", (score or "na").strip()).strip("-") or "na"
    vid = f"v{seq:04d}_{ts}_{score_slug}"
    return vid, f"{vid}.md"


def _append_changelog(skill_dir: Path, entry: VersionEntry, *, action: str) -> None:
    path = changelog_path(skill_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file():
        path.write_text(
            "# Skill versions changelog\n\n"
            "Immutable snapshots. Rollback forks forward (does not rewrite history).\n\n",
            encoding="utf-8",
        )
    line = (
        f"- `{entry.id}` · {action} · score={entry.score or '-'} · "
        f"source={entry.source} · parent={entry.parent or '-'} · {entry.note or ''}\n"
    )
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)


def snapshot(
    skill_dir: Path,
    *,
    score: str = "",
    note: str = "",
    source: Source = "manual",
    parent: str | None = None,
    set_current: bool = True,
) -> VersionEntry:
    """Copy SKILL.md into evals/versions/ and update index + CURRENT."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(skill_md)

    index = load_index(skill_dir)
    # Default parent = current tip
    if parent is None:
        parent = index.current

    seq = _next_seq(index)
    vid, fname = _make_id(seq, score)
    dest_dir = versions_dir(skill_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / fname
    shutil.copy2(skill_md, dest)

    entry = VersionEntry(
        id=vid,
        file=fname,
        ts=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        score=score,
        note=note,
        parent=parent,
        source=source,
        pinned=False,
    )
    index.entries.append(entry)
    if set_current:
        index.current = vid
    save_index(skill_dir, index)
    _append_changelog(skill_dir, entry, action="snapshot")
    return entry


def ensure_seed(skill_dir: Path, *, score: str = "", note: str = "initial seed") -> VersionEntry | None:
    """Create v0001 from SKILL.md if no versions exist yet."""
    index = load_index(skill_dir)
    if index.entries:
        return None
    return snapshot(skill_dir, score=score, note=note, source="seed", parent=None)


def get_entry(skill_dir: Path, version_id: str) -> VersionEntry | None:
    index = load_index(skill_dir)
    needle = version_id.strip()
    for e in index.entries:
        if e.id == needle or e.id.startswith(needle) or e.file == needle:
            return e
    # Prefix match unique
    matches = [e for e in index.entries if e.id.startswith(needle) or needle in e.id]
    if len(matches) == 1:
        return matches[0]
    return None


def pin(skill_dir: Path, version_id: str) -> VersionEntry:
    entry = get_entry(skill_dir, version_id)
    if not entry:
        raise KeyError(f"version not found: {version_id}")
    index = load_index(skill_dir)
    for e in index.entries:
        if e.id == entry.id:
            e.pinned = True
            entry = e
            break
    save_index(skill_dir, index)
    _append_changelog(skill_dir, entry, action="pin")
    return entry


def unpin(skill_dir: Path, version_id: str) -> VersionEntry:
    entry = get_entry(skill_dir, version_id)
    if not entry:
        raise KeyError(f"version not found: {version_id}")
    index = load_index(skill_dir)
    for e in index.entries:
        if e.id == entry.id:
            e.pinned = False
            entry = e
            break
    save_index(skill_dir, index)
    _append_changelog(skill_dir, entry, action="unpin")
    return entry


def rollback(skill_dir: Path, version_id: str, *, note: str = "") -> VersionEntry:
    """Restore SKILL.md from a snapshot, then fork-forward a new CURRENT version.

    History is preserved: the dead-end tip stays in the index; new tip parents
    the chosen version so overnight continues from the preferred base.
    """
    entry = get_entry(skill_dir, version_id)
    if not entry:
        raise KeyError(f"version not found: {version_id}")
    src = versions_dir(skill_dir) / entry.file
    if not src.is_file():
        raise FileNotFoundError(src)

    skill_md = skill_dir / "SKILL.md"
    shutil.copy2(src, skill_md)

    new = snapshot(
        skill_dir,
        score=entry.score,
        note=note or f"rollback to {entry.id}",
        source="rollback",
        parent=entry.id,
        set_current=True,
    )
    return new


def list_versions(skill_dir: Path) -> dict[str, Any]:
    index = load_index(skill_dir)
    return {
        "skill": skill_dir.name,
        "current": index.current,
        "count": len(index.entries),
        "entries": [e.to_dict() for e in index.entries],
        "pinned": [e.id for e in index.entries if e.pinned],
    }
