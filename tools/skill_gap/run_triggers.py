#!/usr/bin/env python3
"""Layer-1 trigger eval for skill descriptions vs triggers.json.

Uses explicit trigger phrases (plus description-derived slash/name hits),
not raw Jaccard — avoids false positives on common words like \"report\".

  py -3.13 -m tools.skill_gap.run_triggers --skill cc-report
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
_DESC_RE = re.compile(r"^description:\s*[>|]?\s*(.+?)(?=\n[a-zA-Z_-]+:|\Z)", re.S | re.M)

# Default phrases for cc-report; skills may override via triggers.json "phrases".
_DEFAULT_PHRASES: dict[str, list[str]] = {
    "cc-report": [
        "/cc-report",
        "/claude-code-report",
        "cc-report",
        "claude-code-report",
        "cc report",
        "reverse handoff",
        "paste into cursor",
        "lane c",
        "_report.md",
        "handoffs/",
        "claude code finished",
        "claude code report",
    ],
}


def _parse_description(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return ""
    dm = _DESC_RE.search(m.group(1))
    if not dm:
        return ""
    return re.sub(r"\s*\n\s*", " ", dm.group(1)).strip().strip("\"'")


def _phrases_for(skill_name: str, data: dict) -> list[str]:
    custom = data.get("phrases")
    if isinstance(custom, list) and custom:
        return [str(p).lower() for p in custom]
    return list(_DEFAULT_PHRASES.get(skill_name, [skill_name.lower(), f"/{skill_name.lower()}"]))


def _predict(prompt: str, phrases: list[str]) -> tuple[bool, list[str]]:
    lower = (prompt or "").lower()
    hits = [p for p in phrases if p and p in lower]
    return (len(hits) > 0, hits)


def run_triggers(skill_dir: Path, *, threshold: float = 0.12) -> dict:
    # threshold kept for CLI compat; phrase matcher does not use it.
    _ = threshold
    skill_md = skill_dir / "SKILL.md"
    triggers_path = skill_dir / "evals" / "triggers.json"
    if not skill_md.is_file() or not triggers_path.is_file():
        return {"ok": False, "error": "missing SKILL.md or evals/triggers.json"}

    description = _parse_description(skill_md)
    data = json.loads(triggers_path.read_text(encoding="utf-8"))
    skill_name = str(data.get("skill") or skill_dir.name)
    phrases = _phrases_for(skill_name, data)
    # Ensure description-mentioned slash forms are included
    for token in ("/cc-report", "/claude-code-report", "paste into cursor", "reverse handoff"):
        if token in description.lower() and token not in phrases:
            phrases.append(token)

    cases = list(data.get("cases") or [])
    results = []
    passed = 0
    for case in cases:
        prompt = str(case.get("prompt") or "")
        should = bool(case.get("should_trigger"))
        predicted, hits = _predict(prompt, phrases)
        ok = predicted == should
        if ok:
            passed += 1
        results.append(
            {
                "id": case.get("id"),
                "should_trigger": should,
                "predicted": predicted,
                "hits": hits,
                "ok": ok,
            }
        )
    total = len(results)
    return {
        "ok": passed == total and total > 0,
        "skill": skill_name,
        "threshold": threshold,
        "phrases": phrases,
        "passed": passed,
        "total": total,
        "score": f"{passed}/{total}" if total else "0/0",
        "description_preview": description[:180],
        "cases": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Phrase-based skill trigger eval")
    parser.add_argument("--skill", required=True)
    parser.add_argument("--threshold", type=float, default=0.12)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    skill_dir = _REPO / ".cursor" / "skills" / args.skill
    result = run_triggers(skill_dir, threshold=args.threshold)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get("error"):
            print(result["error"], file=sys.stderr)
            return 2
        print(
            f"{result['skill']} triggers: {result['score']} "
            f"({'PASS' if result['ok'] else 'FAIL'})"
        )
        for case in result.get("cases") or []:
            if not case["ok"]:
                print(
                    f"  FAIL {case['id']}: should={case['should_trigger']} "
                    f"pred={case['predicted']} hits={case.get('hits')}"
                )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
