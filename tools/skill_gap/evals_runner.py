"""Binary assertion runner for PowerCore skill evals.

Evals live next to a skill:
  .cursor/skills/<name>/evals/evals.json

Schema:
  {
    "skill": "cc-report",
    "cases": [
      {
        "id": "paste-fence",
        "prompt": "...",
        "output": "...",   # fixture text to score (or filled by a live run later)
        "assertions": [
          {"type": "contains", "value": "PASTE INTO CLAUDE CODE"},
          {"type": "not_contains", "value": "ACK stays in Cursor"},
          {"type": "max_words", "value": 800},
          {"type": "regex", "value": "(?m)^Verdict:"}
        ]
      }
    ]
  }
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AssertionResult:
    type: str
    ok: bool
    detail: str = ""


@dataclass
class CaseResult:
    id: str
    ok: bool
    assertions: list[AssertionResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "ok": self.ok,
            "assertions": [asdict(a) for a in self.assertions],
        }


def _check(assertion: dict[str, Any], output: str) -> AssertionResult:
    atype = str(assertion.get("type") or "").strip().lower()
    value = assertion.get("value")
    if atype == "contains":
        needle = str(value)
        ok = needle in output
        return AssertionResult(atype, ok, "found" if ok else f"missing: {needle[:80]}")
    if atype == "not_contains":
        needle = str(value)
        ok = needle not in output
        return AssertionResult(atype, ok, "absent" if ok else f"forbidden present: {needle[:80]}")
    if atype == "regex":
        pat = str(value)
        ok = bool(re.search(pat, output, re.M))
        return AssertionResult(atype, ok, "matched" if ok else f"no match: {pat[:80]}")
    if atype == "max_words":
        limit = int(value)
        words = len(re.findall(r"\S+", output))
        ok = words <= limit
        return AssertionResult(atype, ok, f"words={words} limit={limit}")
    if atype == "min_words":
        limit = int(value)
        words = len(re.findall(r"\S+", output))
        ok = words >= limit
        return AssertionResult(atype, ok, f"words={words} min={limit}")
    return AssertionResult(atype or "unknown", False, f"unsupported assertion type: {atype}")


def run_evals_file(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = list(data.get("cases") or [])
    results: list[CaseResult] = []
    for case in cases:
        output = str(case.get("output") or "")
        assertions = list(case.get("assertions") or [])
        a_results = [_check(a, output) for a in assertions if isinstance(a, dict)]
        assertions_pass = all(a.ok for a in a_results) if a_results else False
        expect_ok = bool(case.get("expect_ok", True))
        # Negative fixtures: expect_ok=false means we require at least one assertion to fail.
        ok = assertions_pass if expect_ok else (not assertions_pass)
        results.append(
            CaseResult(
                id=str(case.get("id") or "case"),
                ok=ok,
                assertions=a_results,
            )
        )
    passed = sum(1 for r in results if r.ok)
    total = len(results)
    return {
        "ok": passed == total and total > 0,
        "skill": data.get("skill"),
        "path": str(path),
        "passed": passed,
        "total": total,
        "score": f"{passed}/{total}" if total else "0/0",
        "cases": [r.to_dict() for r in results],
    }


def find_evals(skill_dir: Path) -> Path | None:
    candidate = skill_dir / "evals" / "evals.json"
    return candidate if candidate.is_file() else None
