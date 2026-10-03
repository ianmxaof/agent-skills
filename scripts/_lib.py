"""Shared helpers for agent-skills vendor pipeline. Paths are always repo-relative."""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_config() -> dict[str, Any]:
    path = REPO_ROOT / "vendor" / "config.json"
    return json.loads(path.read_text(encoding="utf-8"))


def expand_user_path(raw: str) -> Path:
    return Path(raw).expanduser().resolve()


def load_catalog(cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    cfg = cfg or load_config()
    path = REPO_ROOT / cfg["catalog_path"]
    if not path.exists():
        return {"version": 1, "updated_at": None, "items": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_catalog(catalog: dict[str, Any], cfg: dict[str, Any] | None = None) -> Path:
    cfg = cfg or load_config()
    path = REPO_ROOT / cfg["catalog_path"]
    catalog["updated_at"] = utc_now()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:80] or "item"


def read_text_safe(path: Path, limit: int = 200_000) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return data[:limit]


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end].strip()
    out: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        out[key.strip()] = val.strip().strip("\"'")
    return out


def detect_kind(path: Path) -> str:
    """Classify a file or directory as a skill/rule/command kind."""
    if path.is_file():
        name = path.name.lower()
        if name.endswith(".mdc") or name == ".cursorrules":
            return "rule"
        if name.endswith(".md") and ("command" in str(path).replace("\\", "/").lower() or path.parent.name in {"commands", "command"}):
            return "command"
        if name == "skill.md":
            # parent folder is the skill unit
            return "cursor-skill"
        if name.endswith(".md"):
            text = read_text_safe(path, 4000)
            fm = parse_frontmatter(text)
            if "maturity" in fm or "execution-modes" in fm or "category" in fm:
                return "warp-skill"
            if "name" in fm and "description" in fm:
                return "cursor-skill"
            return "other"
        return "other"

    # directory
    names = {p.name.lower() for p in path.iterdir()} if path.exists() else set()
    if "skill.md" in names:
        # prefer claude vs cursor by path hints
        joined = str(path).replace("\\", "/").lower()
        if "/.claude/" in joined or "claude" in path.name.lower():
            return "claude-skill"
        return "cursor-skill"
    if any(n.endswith(".mdc") for n in names) or ".cursorrules" in names:
        return "rule"
    if "commands" in names or path.name.lower() in {"commands", "command"}:
        return "command"
    if ".cursor-plugin" in names or "plugin.json" in names:
        return "plugin"
    # nested scan one level
    for child in path.iterdir() if path.exists() else []:
        if child.is_dir() and (child / "SKILL.md").exists():
            return "cursor-skill"
        if child.suffix.lower() == ".mdc":
            return "rule"
    return "other"


def iter_candidate_units(root: Path) -> list[Path]:
    """Find skill/rule/command units under a dump root."""
    units: list[Path] = []
    if not root.exists():
        return units

    # single skill folder
    if root.is_dir() and (root / "SKILL.md").exists():
        return [root]
    if root.is_file():
        return [root]

    # resources/<name>/SKILL.md pattern (awesome-cursor-skills)
    resources = root / "resources"
    scan_roots = [resources] if resources.is_dir() else [root]

    seen: set[Path] = set()
    for scan in scan_roots:
        for skill_md in scan.rglob("SKILL.md"):
            unit = skill_md.parent
            if unit not in seen:
                seen.add(unit)
                units.append(unit)
        for mdc in scan.rglob("*.mdc"):
            if mdc not in seen:
                seen.add(mdc)
                units.append(mdc)
        commands_dirs = [p for p in scan.rglob("*") if p.is_dir() and p.name.lower() in {"commands", "command"}]
        for cdir in commands_dirs:
            for md in cdir.glob("*.md"):
                if md not in seen:
                    seen.add(md)
                    units.append(md)
        # Warp-style single markdown skills
        for md in scan.rglob("*.md"):
            if md.name.lower() in {"readme.md", "contributing.md", "license.md", "changelog.md"}:
                continue
            if md.parent.name.lower() in {"commands", "command"}:
                continue
            if (md.parent / "SKILL.md").exists():
                continue
            text = read_text_safe(md, 2000)
            fm = parse_frontmatter(text)
            if "maturity" in fm or "execution-modes" in fm:
                if md not in seen:
                    seen.add(md)
                    units.append(md)

    if not units and root.is_dir():
        # whole dump as one other unit
        units.append(root)
    return units


def existing_library_names(cfg: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for rel in (cfg.get("library_cursor"),):
        lib = REPO_ROOT / rel
        if lib.is_dir():
            for child in lib.iterdir():
                if child.is_dir():
                    names.add(child.name.lower())
    warp = REPO_ROOT / cfg.get("library_warp", "skills")
    if warp.is_dir():
        for md in warp.rglob("*.md"):
            names.add(md.stem.lower())
    return names


def score_item(
    *,
    kind: str,
    path: Path,
    name: str,
    operator_boost: int,
    use_count: int,
    library_names: set[str],
    cfg: dict[str, Any],
) -> dict[str, Any]:
    weights = cfg["importance"]["weights"]
    text = ""
    skill_md = path / "SKILL.md" if path.is_dir() else path
    if skill_md.is_file():
        text = read_text_safe(skill_md)
    fm = parse_frontmatter(text)

    # Prefer frontmatter name when present
    if fm.get("name"):
        name = slugify(fm["name"])

    # structure
    structure = 0
    if path.is_dir() and (path / "SKILL.md").exists():
        structure = 25
    elif kind in {"rule", "command", "warp-skill"} and path.is_file():
        structure = 18
    elif kind == "plugin":
        structure = 15
    else:
        structure = 5

    # description quality
    desc = fm.get("description", "")
    desc_score = 0
    if len(desc) >= 40:
        desc_score = 20
    elif len(desc) >= 15:
        desc_score = 12
    elif "description" in text.lower() or "## when" in text.lower():
        desc_score = 8

    # uniqueness
    uniq = 20
    if name.lower() in library_names:
        uniq = 4
    else:
        for existing in library_names:
            if existing and (existing in name.lower() or name.lower() in existing):
                uniq = 10
                break

    boost = max(0, min(20, int(operator_boost)))
    usage = min(10, int(use_count) * 2)
    # fresh ingest gets a small bump; caller can pass ingested_at later — default 5
    recency = 5

    total = (
        structure * weights["structure"] / 25
        + desc_score * weights["description_quality"] / 20
        + uniq * weights["uniqueness"] / 20
        + boost * weights["operator_boost"] / 20
        + usage * weights["usage"] / 10
        + recency * weights["recency"] / 5
    )
    total = round(min(100, max(0, total)), 1)

    promote_at = cfg["importance"]["promote_at"]
    review_at = cfg["importance"]["review_at"]
    if total >= promote_at:
        tier = "promote-candidate"
    elif total >= review_at:
        tier = "review"
    else:
        tier = "park"

    return {
        "name": name,
        "score": total,
        "tier": tier,
        "dimensions": {
            "structure": structure,
            "description_quality": desc_score,
            "uniqueness": uniq,
            "operator_boost": boost,
            "usage": usage,
            "recency": recency,
        },
        "frontmatter": {k: fm[k] for k in ("name", "description") if k in fm},
    }


def strip_batch_prefix(name: str) -> str:
    """Turn 2026-09-09_prompt-engineering into prompt-engineering."""
    return re.sub(r"^\d{4}-\d{2}-\d{2}[_-]", "", name)


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
