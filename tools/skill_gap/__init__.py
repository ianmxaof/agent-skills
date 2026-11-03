"""PowerCore skill-gap gate — detect missing transferable skills (suggest-only)."""

from .catalog import SkillEntry, load_skill_catalog, nearest_skills
from .gate import SkillGapResult, evaluate_skill_gap, score_skill_gap

__all__ = [
    "SkillEntry",
    "SkillGapResult",
    "evaluate_skill_gap",
    "load_skill_catalog",
    "nearest_skills",
    "score_skill_gap",
]
