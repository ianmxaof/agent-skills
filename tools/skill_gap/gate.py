"""Skill-gap importance gate — suggest missing PowerCore skills (never auto-write)."""

from __future__ import annotations

import os
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from .catalog import SkillEntry, load_skill_catalog, nearest_skills

_SKIP_USER_RE = re.compile(
    r"^(thanks|thank you|ok|okay|cool|got it|yes|no|yep|nope|👍|done)\.?!?\s*$",
    re.I,
)

_PROCEDURE_RE = re.compile(
    r"\b(next time|every time|always|whenever|checklist|procedure|playbook|"
    r"workflow|runbook|from now on|going forward|standardize|template)\b",
    re.I,
)
_DEMOTE_RE = re.compile(
    r"\b(demot(?:e|ion|ed)|tipif(?:y|ied)|thin tip|always-?on tip|"
    r"load skill|invoke when|MUST (?:run|use)|rank_skills|"
    r"skill index|end-of-turn gate)\b",
    re.I,
)
_MULTI_STEP_RE = re.compile(
    r"(?m)^\s*(?:\d+[.)]\s+|[-*]\s+).+\n\s*(?:\d+[.)]\s+|[-*]\s+)",
)
_CORRECTION_RE = re.compile(
    r"\b(instead|don't|do not|prefer|rename|naming convention|wrong|"
    r"missed|forgot|we should have|keep forgetting)\b",
    re.I,
)
_TRANSFER_RE = re.compile(
    r"\b(across|reusable|portable|toolbox|agent-skills|powercore|brand|"
    r"any (?:repo|project)|cursor skill|claude (?:code )?skill)\b",
    re.I,
)
_SKILLISH_RE = re.compile(
    r"\b(skill|slash command|/[\w-]+|always-on rule|\.mdc|SKILL\.md)\b",
    re.I,
)


@dataclass
class SkillGapResult:
    score: int
    confidence: float
    tier: Literal["skip", "suggest"]
    proposed_name: str = ""
    nearest: list[dict[str, Any]] = field(default_factory=list)
    rationale: str = ""
    should_suggest: bool = False
    dimensions: dict[str, int] = field(default_factory=dict)
    corpus_size: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def suggest_line(self, *, plain: bool = False) -> str:
        if not self.should_suggest:
            return ""
        near = ", ".join(n["name"] for n in self.nearest[:3]) or "(none)"
        name = self.proposed_name or "(no slug - name it on ACK)"
        prefix = "Skill gap suggested" if plain else "Skill gap suggested"
        # Keep output Windows-console safe (no emoji in CLI JSON/print paths).
        return f"{prefix} ({self.score}) -> {name} — nearest: {near}"


def _env_int(name: str, default: int) -> int:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _enabled() -> bool:
    return (os.getenv("POWERCORE_SKILL_GAP_ENABLED") or "1").strip() != "0"


def _suggest_at() -> int:
    return _env_int("POWERCORE_SKILL_GAP_SUGGEST_AT", 40)


def _min_confidence() -> float:
    return _env_float("POWERCORE_SKILL_GAP_MIN_CONFIDENCE", 0.4)


# Single generic words must not alone mint a skill name.
_GENERIC_SLUG_KEYWORDS = frozenset({"gap", "vault", "report", "fail", "silent"})
_REJECTED_SLUGS = frozenset({"", "powercore-", "powercore-untitled", "powercore-gap"})


def is_valid_slug(slug: str) -> bool:
    """True for a mintable proposal: powercore-<stem>, not untitled/bare-generic."""
    s = (slug or "").strip().lower()
    if s in _REJECTED_SLUGS or not s.startswith("powercore-"):
        return False
    stem = s[len("powercore-"):].strip("-")
    return bool(stem) and stem != "untitled" and stem not in _GENERIC_SLUG_KEYWORDS


def _slugify_proposal(text: str) -> str:
    """Prefer powercore-* names (never mint new tbcc-* skills).

    Returns "" when no valid slug can be derived (never "powercore-untitled").
    """
    lower = text.lower()

    keywords = [
        "paste-bridge",
        "paste",
        "bridge",
        "silent-fail",
        "silent",
        "fail",
        "refresh",
        "vault",
        "rotator",
        "feeds",
        "handoff",
        "report",
        "eval",
        "gap",
        "daemon",
        "models",
        "timeout",
        "classify",
        "provider",
        "checklist",
        "playbook",
    ]
    hits = [k for k in keywords if k.replace("-", " ") in lower or k in lower]
    # Dedupe overlapping (silent-fail beats silent+fail)
    cleaned: list[str] = []
    for h in hits:
        if any(h != c and h in c for c in hits):
            continue
        cleaned.append(h.replace(" ", "-"))
    cleaned = list(dict.fromkeys(cleaned))[:4]
    if cleaned:
        candidate = f"powercore-{'-'.join(cleaned)}"[:64]
        if is_valid_slug(candidate):
            return candidate

    m = re.search(r"\bpowercore-([a-z0-9]+(?:-[a-z0-9]+){0,4})\b", lower)
    if m:
        candidate = f"powercore-{m.group(1)}"[:64]
        if is_valid_slug(candidate):
            return candidate

    return ""


def _score_repeatability(text: str) -> int:
    score = 0
    if _PROCEDURE_RE.search(text):
        score += 12
    if _DEMOTE_RE.search(text):
        score += 10
    if _MULTI_STEP_RE.search(text):
        score += 10
    if text.count("\n") >= 12 and ("1." in text or "- " in text):
        score += 5
    if _CORRECTION_RE.search(text):
        score += 6
    return min(25, score)


def _score_transferability(text: str) -> int:
    score = 0
    if _TRANSFER_RE.search(text):
        score += 12
    if _SKILLISH_RE.search(text):
        score += 8
    if _DEMOTE_RE.search(text):
        score += 6
    if re.search(r"\b(cursor|claude code|agent)\b", text, re.I):
        score += 4
    return min(20, score)


def _score_corpus_gap(nearest: list[tuple[SkillEntry, float]]) -> tuple[int, float]:
    """High score when no strong near-miss exists."""
    if not nearest:
        return 25, 0.55
    top = nearest[0][1]
    # top overlap 0.8+ → almost no gap; 0.15 → large gap
    if top >= 0.75:
        return 2, 0.9
    if top >= 0.55:
        return 8, 0.75
    if top >= 0.35:
        return 14, 0.6
    if top >= 0.2:
        return 20, 0.55
    return 25, 0.5


def _score_durability(text: str) -> int:
    score = 0
    if len(text) > 600:
        score += 5
    if re.search(r"\b(must|always|never|canonical|source of truth|convention)\b", text, re.I):
        score += 6
    if re.search(r"\b(SKILL\.md|evals?|assertion|frontmatter)\b", text, re.I):
        score += 4
    return min(15, score)


def _score_operator_cost(text: str) -> int:
    score = 0
    if _CORRECTION_RE.search(text):
        score += 8
    if re.search(r"\b(overnight|every (?:session|turn|deploy)|repeatedly|again)\b", text, re.I):
        score += 5
    if re.search(r"\b(timeout|silent fail|forgot|manual|eyeball)\b", text, re.I):
        score += 4
    return min(15, score)


def score_skill_gap(
    *,
    user_prompt: str = "",
    ai_response: str = "",
    catalog: list[SkillEntry] | None = None,
) -> SkillGapResult:
    """Heuristic skill-gap score. Never sets auto-create — suggest only."""
    prompt = (user_prompt or "").strip()
    response = (ai_response or "").strip()
    combined = f"{prompt}\n{response}".strip()

    if not _enabled():
        return SkillGapResult(
            score=0,
            confidence=1.0,
            tier="skip",
            rationale="POWERCORE_SKILL_GAP_ENABLED=0",
            should_suggest=False,
        )

    if _SKIP_USER_RE.match(prompt) and len(response) < 200:
        return SkillGapResult(
            score=0,
            confidence=0.95,
            tier="skip",
            rationale="trivial ack",
            should_suggest=False,
        )

    if not combined:
        return SkillGapResult(
            score=0,
            confidence=1.0,
            tier="skip",
            rationale="empty turn",
            should_suggest=False,
        )

    cat = catalog if catalog is not None else load_skill_catalog()
    near = nearest_skills(combined, cat, limit=5)

    rep = _score_repeatability(combined)
    transfer = _score_transferability(combined)
    gap, gap_conf = _score_corpus_gap(near)
    durable = _score_durability(combined)
    cost = _score_operator_cost(combined)

    total = rep + transfer + gap + durable + cost
    total = max(0, min(100, total))

    dims = {
        "repeatability": rep,
        "transferability": transfer,
        "corpus_gap": gap,
        "durability": durable,
        "operator_cost": cost,
    }

    # Confidence: blend corpus match confidence with whether procedure signals fired
    signal_conf = 0.35
    if rep >= 10:
        signal_conf += 0.15
    if transfer >= 8:
        signal_conf += 0.15
    if cost >= 6:
        signal_conf += 0.1
    confidence = round(min(0.95, 0.4 * gap_conf + 0.6 * signal_conf), 3)

    suggest_floor = _suggest_at()
    min_conf = _min_confidence()
    should = total >= suggest_floor and confidence >= min_conf and gap >= 10

    # If a near-miss is very strong, do not suggest a new skill
    if near and near[0][1] >= 0.7:
        should = False

    proposed = _slugify_proposal(combined) if should or total >= suggest_floor else ""
    # Avoid proposing an existing name
    existing = {e.name.lower() for e in cat}
    if proposed and proposed.lower() in existing:
        proposed = f"{proposed}-v2" if not proposed.endswith("-v2") else f"{proposed}-gap"
        if proposed.lower() in existing:
            proposed = ""

    nearest_payload = [
        {"name": e.name, "score": s, "path": e.path, "description": e.description[:160]}
        for e, s in near
    ]

    tier: Literal["skip", "suggest"] = "suggest" if should else "skip"
    rationale = (
        f"dims={dims}; nearest={nearest_payload[0]['name'] if nearest_payload else 'none'}"
        f"@{nearest_payload[0]['score'] if nearest_payload else 0}; "
        f"propose={proposed or '-'}"
    )

    return SkillGapResult(
        score=total,
        confidence=confidence,
        tier=tier,
        proposed_name=proposed if should else proposed,
        nearest=nearest_payload,
        rationale=rationale,
        should_suggest=should,
        dimensions=dims,
        corpus_size=len(cat),
    )


def evaluate_skill_gap(
    *,
    user_prompt: str = "",
    ai_response: str = "",
    catalog: list[SkillEntry] | None = None,
) -> SkillGapResult:
    """Public entry — same as score_skill_gap (no LLM refine in v1)."""
    return score_skill_gap(
        user_prompt=user_prompt,
        ai_response=ai_response,
        catalog=catalog,
    )
