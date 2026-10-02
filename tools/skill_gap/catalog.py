"""Scan PowerCore agent-skills corpus (SKILL.md frontmatter)."""

from __future__ import annotations

import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
_NAME_RE = re.compile(r"^name:\s*[\"']?([^\s\"'#]+)", re.M)
_DESC_RE = re.compile(r"^description:\s*[>|]?\s*(.+?)(?=\n[a-zA-Z_-]+:|\Z)", re.S | re.M)

# Repo root = agent-skills/ (tools/skill_gap → parents[2])
_DEFAULT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class SkillEntry:
    name: str
    description: str
    path: str
    aliases: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def blob(self) -> str:
        parts = [self.name, self.description, *self.aliases]
        return " ".join(p for p in parts if p).lower()


def _skills_roots(repo_root: Path | None = None) -> list[Path]:
    root = repo_root or _repo_root()
    roots: list[Path] = []
    for rel in (".cursor/skills", "skills"):
        p = root / rel
        if p.is_dir():
            roots.append(p)
    extra = (os.getenv("POWERCORE_SKILL_GAP_EXTRA_ROOTS") or "").strip()
    for chunk in extra.split(os.pathsep):
        chunk = chunk.strip()
        if chunk:
            ep = Path(chunk).expanduser()
            if ep.is_dir():
                roots.append(ep)
    return roots


def _repo_root() -> Path:
    raw = (os.getenv("POWERCORE_SKILL_GAP_ROOT") or "").strip()
    return Path(raw).expanduser() if raw else _DEFAULT_ROOT


def _parse_frontmatter(text: str) -> tuple[str, str]:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return "", ""
    block = m.group(1)
    name_m = _NAME_RE.search(block)
    name = (name_m.group(1).strip() if name_m else "") or ""
    desc_m = _DESC_RE.search(block)
    desc = ""
    if desc_m:
        raw = desc_m.group(1).strip()
        # Fold YAML folded/literal style lines
        desc = re.sub(r"\s*\n\s*", " ", raw).strip().strip("\"'")
    return name, desc


def _aliases_from_name(name: str) -> tuple[str, ...]:
    """Legacy tbcc-* ↔ powercore-* aliases for near-miss matching."""
    aliases: list[str] = []
    if name.startswith("tbcc-"):
        aliases.append("powercore-" + name[len("tbcc-") :])
    elif name.startswith("powercore-"):
        aliases.append("tbcc-" + name[len("powercore-") :])
    # Slash-ish tokens
    if "-" in name:
        aliases.append(name.replace("-", " "))
    return tuple(dict.fromkeys(a for a in aliases if a and a != name))


def load_skill_catalog(repo_root: Path | None = None) -> list[SkillEntry]:
    """Load all SKILL.md entries under configured skill roots."""
    entries: list[SkillEntry] = []
    seen: set[str] = set()
    for root in _skills_roots(repo_root):
        for skill_md in sorted(root.rglob("SKILL.md")):
            try:
                text = skill_md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            name, desc = _parse_frontmatter(text)
            if not name:
                name = skill_md.parent.name
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            entries.append(
                SkillEntry(
                    name=name,
                    description=desc or "(no description)",
                    path=str(skill_md.relative_to(_repo_root()) if repo_root is None else skill_md),
                    aliases=_aliases_from_name(name),
                )
            )
    return entries


_TOKEN_RE = re.compile(r"[a-z0-9]{3,}")
_TRIGGER_CHUNK_RE = re.compile(
    r"(?:MUST\s+(?:run|use)|Use when|Invoke when|when (?:the )?operator|"
    r"end of (?:every )?substantive|before claiming)[:\s]+(.{0,220})",
    re.I | re.S,
)
_SLASH_RE = re.compile(r"/([a-z0-9][\w-]{1,40})", re.I)


def _tokens(text: str) -> set[str]:
    return set(_TOKEN_RE.findall((text or "").lower()))


def _trigger_tokens(description: str) -> set[str]:
    """Tokens from description 'Use when' / MUST clauses — higher weight for invoke match."""
    toks: set[str] = set()
    for m in _TRIGGER_CHUNK_RE.finditer(description or ""):
        toks |= _tokens(m.group(1))
    # Also pull slash commands named in the description
    for m in _SLASH_RE.finditer(description or ""):
        toks.add(m.group(1).lower())
        toks |= _tokens(m.group(1).replace("-", " "))
    return toks


def nearest_skills(
    text: str,
    catalog: list[SkillEntry] | None = None,
    *,
    limit: int = 5,
) -> list[tuple[SkillEntry, float]]:
    """Return (skill, overlap_score 0-1) sorted best-first.

    Biases toward description trigger phrases and slash-id mentions so demoted
    always-on tips still surface the right skill to open.
    """
    cat = catalog if catalog is not None else load_skill_catalog()
    q = _tokens(text)
    if not q or not cat:
        return []
    lower = (text or "").lower()
    slashes = {m.group(1).lower() for m in _SLASH_RE.finditer(text or "")}
    scored: list[tuple[SkillEntry, float]] = []
    for entry in cat:
        blob_toks = _tokens(entry.blob())
        if not blob_toks:
            continue
        inter = len(q & blob_toks)
        if inter == 0 and entry.name.lower() not in lower and not (slashes & {entry.name.lower()}):
            # Still allow trigger-only hits
            trig = _trigger_tokens(entry.description)
            if not (q & trig):
                continue
            inter = len(q & trig)
        union = len(q | blob_toks)
        jaccard = inter / union if union else 0.0
        coverage = inter / len(q) if q else 0.0
        score = 0.5 * coverage + 0.35 * jaccard
        # Trigger-phrase overlap (Use when / MUST …)
        trig = _trigger_tokens(entry.description)
        if trig:
            t_inter = len(q & trig)
            if t_inter:
                score += min(0.25, 0.06 * t_inter)
        # Exact name / slash mention
        if entry.name.lower() in lower:
            score = min(1.0, score + 0.35)
        if entry.name.lower() in slashes or entry.name.lower().replace("tbcc-", "") in slashes:
            score = min(1.0, score + 0.3)
        for alias in entry.aliases:
            if alias.lower() in lower:
                score = min(1.0, score + 0.2)
                break
        scored.append((entry, round(min(1.0, score), 4)))
    scored.sort(key=lambda x: (-x[1], x[0].name))
    return scored[: max(1, limit)]
