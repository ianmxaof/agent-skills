"""Rank which existing skills to open for a turn (invoke heuristic).

Complements skill-gap (which suggests *new* skills). After demoting fat
always-on rules to tips, agents can call this CLI when unsure which skill
body to load.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

from .catalog import SkillEntry, load_skill_catalog, nearest_skills

_SUBSTANTIVE_RE = re.compile(
    r"\b(implement|wire|fix|deploy|architect|design|crystallize|ship|"
    r"skill|gate|prune|demote|procedure|checklist)\b",
    re.I,
)
_SILENT_RE = re.compile(
    r"\b(silent-?fail|/silent-fail|never_seen|zombie|external stop)\b",
    re.I,
)
_SHIP_RE = re.compile(r"\b(done|deployed|ship|sellable|pre-?activate|PSG|ship-gate)\b", re.I)
_CRYST_RE = re.compile(
    r"\b(crystallize|vault|NTK|need-to-know|durable|canonical|from now on)\b",
    re.I,
)
_GAP_RE = re.compile(
    r"\b(skill gap|from now on|playbook|reusable|powercore-|checklist|"
    r"demote|tipif|always-?on)\b",
    re.I,
)

# Soft boosts for end-of-turn tips after prune
_ENDGATE_BOOSTS: dict[str, float] = {
    "tbcc-auto-crystallize": 0.12,
    "powercore-skill-gap": 0.1,
    "powercore-ship-gate": 0.12,
    "tbcc-silent-fail": 0.15,
    "powercore-token-audit": 0.05,
}


_SKIP_RE = re.compile(
    r"^(thanks|thank you|ok|okay|cool|got it|yes|no|yep|nope|👍|done)\.?!?\s*$",
    re.I,
)


def rank_skills_for_invoke(
    *,
    user_prompt: str = "",
    ai_response: str = "",
    catalog: list[SkillEntry] | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """Return ranked skills with score + short reason."""
    prompt = (user_prompt or "").strip()
    response = (ai_response or "").strip()
    combined = f"{prompt}\n{response}".strip()
    # Trivial turns: do not recommend skills (avoids false crystallize tops)
    if not response or (len(response) < 120 and _SKIP_RE.match(prompt)):
        return []
    cat = catalog if catalog is not None else load_skill_catalog()
    near = nearest_skills(combined, cat, limit=max(limit, 12))
    by_name = {e.name: (e, s) for e, s in near}

    # Ensure endgate skills are candidates when turn looks substantive
    if _SUBSTANTIVE_RE.search(combined) or len(response) > 400 or _SILENT_RE.search(combined):
        for e in cat:
            if e.name in _ENDGATE_BOOSTS and e.name not in by_name:
                by_name[e.name] = (e, 0.08)

    ranked: list[dict[str, Any]] = []
    for name, (entry, base) in by_name.items():
        score = base
        reasons: list[str] = ["token-overlap"]
        boost = _ENDGATE_BOOSTS.get(name, 0.0)
        if boost and _SUBSTANTIVE_RE.search(combined):
            if name == "tbcc-auto-crystallize" and _CRYST_RE.search(combined):
                score = min(1.0, score + boost + 0.08)
                reasons.append("crystallize-signals")
            elif name == "powercore-skill-gap" and _GAP_RE.search(combined):
                score = min(1.0, score + boost + 0.08)
                reasons.append("skill-gap-signals")
            elif name == "powercore-ship-gate" and _SHIP_RE.search(combined):
                score = min(1.0, score + boost + 0.1)
                reasons.append("ship-signals")
            elif name == "tbcc-silent-fail" and _SILENT_RE.search(combined):
                score = min(1.0, score + boost + 0.15)
                reasons.append("silent-fail-signals")
            elif boost and len(response) > 600:
                score = min(1.0, score + boost * 0.5)
                reasons.append("substantive-endgate")
        # Slash /silent-fail even on shorter turns
        if name == "tbcc-silent-fail" and _SILENT_RE.search(combined):
            score = min(1.0, score + 0.25)
            if "silent-fail-signals" not in reasons:
                reasons.append("silent-fail-signals")
        ranked.append(
            {
                "name": entry.name,
                "score": round(score, 4),
                "path": entry.path,
                "reasons": reasons,
                "description": (entry.description or "")[:160],
            }
        )

    ranked.sort(key=lambda r: (-r["score"], r["name"]))
    return ranked[: max(1, limit)]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Rank skills to open for this turn")
    p.add_argument("--prompt", default="")
    p.add_argument("--response", default="")
    p.add_argument("--file", help="Read assistant response from file")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--json", action="store_true")
    p.add_argument("--min-score", type=float, default=0.12)
    args = p.parse_args(argv)

    response = args.response
    if args.file:
        response = open(args.file, encoding="utf-8").read()

    rows = rank_skills_for_invoke(
        user_prompt=args.prompt,
        ai_response=response,
        limit=args.limit,
    )
    rows = [r for r in rows if r["score"] >= args.min_score] or rows[:3]

    if args.json:
        print(json.dumps({"ok": True, "ranked": rows}, indent=2))
    else:
        for r in rows:
            why = ",".join(r["reasons"])
            print(f"{r['score']:.3f}  {r['name']}  ({why})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
