"""Binary assertions against SKILL.md body (so overnight edits can move the score)."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .evals_runner import AssertionResult, _check


@dataclass
class BodyCaseResult:
    id: str
    ok: bool
    assertions: list[AssertionResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "ok": self.ok,
            "assertions": [asdict(a) for a in self.assertions],
        }


DEFAULT_CC_REPORT_BODY: list[dict[str, Any]] = [
    {
        "id": "paste-fence-required",
        "assertions": [
            {"type": "contains", "value": "PASTE INTO CLAUDE CODE"},
            {"type": "contains", "value": "PASTE INTO CURSOR"},
        {"type": "not_contains", "value": "ACK stays in Cursor. Do not paste"},
        ],
    },
    {
        "id": "ack-fields-required",
        "assertions": [
            {"type": "contains", "value": "Verdict:"},
            {"type": "contains", "value": "Report:"},
            {"type": "contains", "value": "Do:"},
            {"type": "contains", "value": "Do not:"},
        ],
    },
    {
        "id": "forbidden-actions",
        "assertions": [
            {"type": "regex", "value": "(?i)do not:.*push|never push|Do not:.*push"},
            {"type": "contains", "value": "start bots"},
        ],
    },
]


def load_body_cases(skill_dir: Path) -> list[dict[str, Any]]:
    path = skill_dir / "evals" / "body_assertions.json"
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        return list(data.get("cases") or [])
    if skill_dir.name == "cc-report":
        return list(DEFAULT_CC_REPORT_BODY)
    return []


def run_body_assertions(skill_dir: Path) -> dict[str, Any]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return {"ok": False, "error": "missing SKILL.md", "passed": 0, "total": 0, "score": "0/0"}
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    cases = load_body_cases(skill_dir)
    results: list[BodyCaseResult] = []
    for case in cases:
        assertions = list(case.get("assertions") or [])
        a_results = [_check(a, text) for a in assertions if isinstance(a, dict)]
        ok = all(a.ok for a in a_results) if a_results else False
        results.append(BodyCaseResult(id=str(case.get("id") or "body"), ok=ok, assertions=a_results))
    passed = sum(1 for r in results if r.ok)
    total = len(results)
    return {
        "ok": passed == total and total > 0,
        "skill": skill_dir.name,
        "passed": passed,
        "total": total,
        "score": f"{passed}/{total}" if total else "0/0",
        "cases": [r.to_dict() for r in results],
    }


def missing_body_needles(skill_dir: Path) -> list[str]:
    """Return contains-needles that failed (for mutator)."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return []
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    missing: list[str] = []
    for case in load_body_cases(skill_dir):
        for a in case.get("assertions") or []:
            if not isinstance(a, dict):
                continue
            if str(a.get("type") or "").lower() != "contains":
                continue
            needle = str(a.get("value") or "")
            if needle and needle not in text:
                missing.append(needle)
    return missing
