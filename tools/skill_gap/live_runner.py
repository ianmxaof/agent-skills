"""Optional live runner: ask PowerCore Vault Rotator with SKILL.md as system prompt."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .evals_runner import run_evals_file


def _vault_url() -> str:
    return (os.getenv("POWERCORE_VAULT_URL") or "http://127.0.0.1:18792").rstrip("/")


def vault_ask(
    messages: list[dict[str, str]],
    *,
    timeout: float = 90.0,
) -> tuple[int, dict[str, Any]]:
    url = _vault_url() + "/v1/rotator/ask"
    body = json.dumps({"messages": messages, "route_override": {"route_mode": "auto"}}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {"error": raw}
        return e.code, payload
    except Exception as e:
        return 0, {"error": str(e)}


def _skill_system_prompt(skill_md: Path, *, max_chars: int = 12000) -> str:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[truncated]"
    return (
        "You are executing the following Cursor agent skill. "
        "Follow its Output Contract exactly. Reply as the skill would to the operator.\n\n"
        + text
    )


def run_live_evals(
    skill_dir: Path,
    *,
    max_cases: int = 3,
    timeout: float = 90.0,
) -> dict[str, Any]:
    """Run positive fixture prompts live via Vault ask; score assertions on model output."""
    evals_path = skill_dir / "evals" / "evals.json"
    skill_md = skill_dir / "SKILL.md"
    if not evals_path.is_file() or not skill_md.is_file():
        return {"ok": False, "error": "missing evals or SKILL.md", "skipped": True}

    data = json.loads(evals_path.read_text(encoding="utf-8"))
    cases = [
        c
        for c in (data.get("cases") or [])
        if isinstance(c, dict) and c.get("expect_ok", True) is not False
    ][: max(1, max_cases)]

    system = _skill_system_prompt(skill_md)
    results: list[dict[str, Any]] = []
    passed = 0
    for case in cases:
        prompt = str(case.get("prompt") or "").strip()
        if not prompt:
            continue
        code, body = vault_ask(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            timeout=timeout,
        )
        if code != 200 or not body.get("ok", True):
            err = body.get("error") or body.get("content") or f"http_{code}"
            results.append(
                {
                    "id": case.get("id"),
                    "ok": False,
                    "error": str(err)[:200],
                    "live": True,
                }
            )
            continue
        content = str(body.get("content") or "")
        # Score using the case's assertions against live content
        from .evals_runner import _check

        assertions = list(case.get("assertions") or [])
        a_results = [_check(a, content) for a in assertions if isinstance(a, dict)]
        ok = all(a.ok for a in a_results) if a_results else False
        if ok:
            passed += 1
        results.append(
            {
                "id": case.get("id"),
                "ok": ok,
                "live": True,
                "content_preview": content[:240],
                "assertions": [
                    {"type": a.type, "ok": a.ok, "detail": a.detail} for a in a_results
                ],
            }
        )

    total = len(results)
    return {
        "ok": passed == total and total > 0,
        "skipped": False,
        "skill": skill_dir.name,
        "passed": passed,
        "total": total,
        "score": f"{passed}/{total}" if total else "0/0",
        "cases": results,
    }
