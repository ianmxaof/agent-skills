"""PowerCore Ship Gate / silent-fail shared verdict severity map.

Single source of truth for aggregation. Unknown verdicts rank as blocked-equivalent
(not greener than ok). Lower rank = worse.

Severity: fail < never_seen < stale < blocked < ok < idle
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

# Lower number = worse (wins "worst" via min).
SEVERITY: dict[str, int] = {
    "fail": 0,
    "never_seen": 1,
    "stale": 2,
    "blocked": 3,
    "ok": 4,
    "idle": 5,
}

GREEN = frozenset({"ok", "idle"})
BLOCKS_DONE = frozenset({"fail", "never_seen", "stale", "blocked"})

# Vendored copy fingerprint — keep in sync with
# tbcc/backend/app/services/silent_fail_verdicts.py
VERDICT_MAP_VERSION = "psg-1"


def normalize_verdict(raw: Any) -> str:
    v = str(raw or "").strip().lower()
    if v in SEVERITY:
        return v
    return "blocked"


def severity_rank(verdict: Any) -> int:
    return SEVERITY.get(normalize_verdict(verdict), SEVERITY["blocked"])


def is_green(verdict: Any) -> bool:
    return normalize_verdict(verdict) in GREEN


def worst_verdict(verdicts: Iterable[Any]) -> str:
    items = list(verdicts)
    if not items:
        return "ok"
    return min((normalize_verdict(v) for v in items), key=severity_rank)


def worst_row(rows: Iterable[Mapping[str, Any]], *, key: str = "verdict") -> Mapping[str, Any] | None:
    rows = list(rows)
    if not rows:
        return None
    return min(rows, key=lambda r: severity_rank(r.get(key)))
