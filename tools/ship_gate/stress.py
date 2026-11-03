"""Stress-lane thresholds and stress evidence helpers."""

from __future__ import annotations

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .verdicts import is_green, normalize_verdict


STRESS_MAX_AGE_DAYS = 7
STRESS_MAX_AGE_S = STRESS_MAX_AGE_DAYS * 24 * 3600


def parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        raw = str(ts).strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def age_seconds(ts: str | None, *, now: datetime | None = None) -> float | None:
    dt = parse_ts(ts)
    if dt is None:
        return None
    now = now or datetime.now(timezone.utc)
    return max(0.0, (now - dt).total_seconds())


def write_stress_evidence(
    agent_skills_root: Path,
    *,
    root_id: str,
    product_id: str | None,
    payload: dict[str, Any],
) -> Path:
    """Write stress:<root_id> and optional stress:<store_id> evidence."""
    dest_dir = agent_skills_root / ".ship-gate" / "stress"
    dest_dir.mkdir(parents=True, exist_ok=True)
    paths = [dest_dir / f"{root_id}.json"]
    if product_id:
        paths.append(dest_dir / f"{product_id}.json")
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    for p in paths:
        p.write_text(text, encoding="utf-8")
    return paths[0]


def read_stress_evidence(
    agent_skills_root: Path, key: str
) -> dict[str, Any] | None:
    path = agent_skills_root / ".ship-gate" / "stress" / f"{key}.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def check_stress_fresh(
    agent_skills_root: Path,
    key: str,
    *,
    max_age_s: float = STRESS_MAX_AGE_S,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Require green stress evidence for key within max_age_s."""
    path = agent_skills_root / ".ship-gate" / "stress" / f"{key}.json"
    data = read_stress_evidence(agent_skills_root, key)
    if not data:
        return {
            "ok": False,
            "reason": f"no stress evidence for {key} (run --lane stress)",
            "path": str(path),
            "key": key,
        }
    worst = normalize_verdict(data.get("worst"))
    if not is_green(worst):
        return {
            "ok": False,
            "reason": f"stress worst={worst}",
            "path": str(path),
            "key": key,
        }
    age = age_seconds(data.get("ts"), now=now)
    if age is None:
        return {
            "ok": False,
            "reason": "stress evidence missing ts",
            "path": str(path),
            "key": key,
        }
    if age > max_age_s:
        days = age / 86400.0
        return {
            "ok": False,
            "reason": f"stress evidence expired ({days:.1f}d > {max_age_s / 86400:.0f}d)",
            "path": str(path),
            "key": key,
            "age_s": age,
        }
    return {
        "ok": True,
        "path": str(path),
        "key": key,
        "age_s": age,
        "worst": worst,
        "run_id": data.get("run_id"),
    }


def apply_probe_threshold(
    probe_payload: dict[str, Any] | None,
    threshold: dict[str, Any],
    base_verdict: str,
) -> dict[str, Any]:
    """Apply numeric / list thresholds to a silent_fail-style probe JSON."""
    if not threshold:
        return {"verdict": normalize_verdict(base_verdict), "metrics": {}}

    payload = probe_payload or {}
    surfaces = list(payload.get("surfaces") or [])
    metrics: dict[str, Any] = {
        "surface_count": len(surfaces),
        "probe_verdict": payload.get("verdict"),
    }

    ok_ids = {str(s.get("id")) for s in surfaces if normalize_verdict(s.get("verdict")) == "ok"}
    fail_n = sum(1 for s in surfaces if normalize_verdict(s.get("verdict")) == "fail")
    blocked_n = sum(1 for s in surfaces if normalize_verdict(s.get("verdict")) == "blocked")
    stale_n = sum(1 for s in surfaces if normalize_verdict(s.get("verdict")) == "stale")
    metrics.update({"ok": len(ok_ids), "fail": fail_n, "blocked": blocked_n, "stale": stale_n})

    required = list(threshold.get("require_surface_ok") or [])
    missing = [rid for rid in required if rid not in ok_ids]
    if missing:
        return {
            "verdict": "fail",
            "evidence": f"required surfaces not ok: {', '.join(missing)}",
            "metrics": metrics,
        }

    max_fail = threshold.get("max_fail_surfaces")
    if max_fail is not None and fail_n > int(max_fail):
        return {
            "verdict": "fail",
            "evidence": f"fail_surfaces={fail_n} > max {max_fail}",
            "metrics": metrics,
        }

    max_blocked = threshold.get("max_blocked_surfaces")
    if max_blocked is not None and blocked_n > int(max_blocked):
        return {
            "verdict": "fail",
            "evidence": f"blocked_surfaces={blocked_n} > max {max_blocked}",
            "metrics": metrics,
        }

    min_ok = threshold.get("min_ok_surfaces")
    if min_ok is not None and len(ok_ids) < int(min_ok):
        return {
            "verdict": "fail",
            "evidence": f"ok_surfaces={len(ok_ids)} < min {min_ok}",
            "metrics": metrics,
        }

    # If probe worst is blocked/fail/never_seen, still fail unless only stale allowed
    allow_worst = set(threshold.get("allow_worst") or ["ok", "idle"])
    pv = normalize_verdict(payload.get("verdict") or base_verdict)
    if pv not in allow_worst and pv in ("fail", "blocked", "never_seen"):
        return {
            "verdict": pv,
            "evidence": f"probe worst={pv} not in allow_worst",
            "metrics": metrics,
        }
    # stale allowed via allow_worst including stale
    if pv == "stale" and "stale" not in allow_worst:
        return {
            "verdict": "fail",
            "evidence": "probe worst=stale (not allowed by threshold)",
            "metrics": metrics,
        }

    return {
        "verdict": "ok",
        "evidence": (
            f"stress thresholds ok ok={len(ok_ids)} fail={fail_n} "
            f"blocked={blocked_n} stale={stale_n}"
        ),
        "metrics": metrics,
    }


def apply_latency_threshold(
    samples_ms: list[float],
    threshold: dict[str, Any],
) -> dict[str, Any]:
    """p95 / max latency gate."""
    if not samples_ms:
        return {"verdict": "blocked", "evidence": "no latency samples", "metrics": {}}
    sorted_s = sorted(samples_ms)
    n = len(sorted_s)
    p95_idx = min(n - 1, max(0, int(0.95 * (n - 1))))
    p95 = sorted_s[p95_idx]
    mean = statistics.fmean(samples_ms)
    metrics = {
        "n": n,
        "p95_ms": round(p95, 3),
        "mean_ms": round(mean, 3),
        "max_ms": round(max(samples_ms), 3),
    }
    p95_max = threshold.get("p95_ms_max")
    if p95_max is not None and p95 > float(p95_max):
        return {
            "verdict": "fail",
            "evidence": f"p95={p95:.2f}ms > max {p95_max}ms",
            "metrics": metrics,
        }
    max_ms = threshold.get("max_ms")
    if max_ms is not None and max(samples_ms) > float(max_ms):
        return {
            "verdict": "fail",
            "evidence": f"max={max(samples_ms):.2f}ms > {max_ms}ms",
            "metrics": metrics,
        }
    min_n = threshold.get("min_iterations")
    if min_n is not None and n < int(min_n):
        return {
            "verdict": "fail",
            "evidence": f"iterations={n} < min {min_n}",
            "metrics": metrics,
        }
    return {
        "verdict": "ok",
        "evidence": f"p95={p95:.2f}ms n={n}",
        "metrics": metrics,
    }
