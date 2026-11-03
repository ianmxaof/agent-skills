# PowerCore endgates — session + stop hooks (Windows-friendly)
# sessionStart: inject short tip (near-zero ongoing cost vs fat rules)
# afterAgentResponse: cache last assistant text
# stop: run endgates observe/auto from transcript when available; log metrics; no followup by default

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_AGENT_SKILLS = Path(r"C:\Powercore-repo-main\agent-skills")
_CACHE_DIR = _AGENT_SKILLS / ".skill-gap" / "hook-cache"


def _read_stdin() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _write(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj))
    sys.stdout.flush()


def session_start(payload: dict) -> dict:
    tip = (
        "Endgates: after substantive turns run "
        "`cd C:\\Powercore-repo-main\\agent-skills; "
        "py -3.13 -m tools.skill_gap.endgates --prompt \"...\" --response \"...\" --auto --plain`. "
        "Trivial thanks/lint: skip. Full procedures in skills tbcc-auto-crystallize / "
        "powercore-skill-gap / powercore-ship-gate."
    )
    return {
        "env": {
            "POWERCORE_ENDGATES_ROOT": str(_AGENT_SKILLS),
        },
        "additional_context": tip,
    }


def after_agent_response(payload: dict) -> dict:
    text = str(payload.get("text") or "")
    conv = str(payload.get("conversation_id") or "default")
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        (_CACHE_DIR / f"{conv}.assistant.txt").write_text(text, encoding="utf-8")
    except OSError:
        pass
    return {}


def _last_turn_from_transcript(path: str | None) -> tuple[str, str]:
    if not path:
        return "", ""
    p = Path(path)
    if not p.is_file():
        # Cursor sometimes points at a directory
        if p.is_dir():
            jsonls = sorted(p.rglob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True)
            if not jsonls:
                return "", ""
            p = jsonls[0]
        else:
            return "", ""
    prompt = ""
    response = ""
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "", ""
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = row.get("role")
        msg = row.get("message") or {}
        content = msg.get("content") if isinstance(msg, dict) else None
        text = ""
        if isinstance(content, list):
            parts = []
            for c in content:
                if isinstance(c, dict) and c.get("type") == "text":
                    parts.append(str(c.get("text") or ""))
            text = "\n".join(parts)
        elif isinstance(content, str):
            text = content
        if role == "user" and text.strip():
            prompt = text.strip()[-4000:]
        elif role == "assistant" and text.strip():
            response = text.strip()[-12000:]
    return prompt, response


def stop(payload: dict) -> dict:
    # Never auto-loop unless operator opts in
    if int(payload.get("loop_count") or 0) > 0:
        return {}
    if str(payload.get("status") or "") not in ("completed", ""):
        return {}

    conv = str(payload.get("conversation_id") or "default")
    cached = _CACHE_DIR / f"{conv}.assistant.txt"
    prompt = ""
    response = ""
    if cached.is_file():
        try:
            response = cached.read_text(encoding="utf-8", errors="replace")
        except OSError:
            response = ""
    if not response:
        prompt, response = _last_turn_from_transcript(
            payload.get("transcript_path") or os.environ.get("CURSOR_TRANSCRIPT_PATH")
        )
    if not response.strip():
        return {}

    if str(_AGENT_SKILLS) not in sys.path:
        sys.path.insert(0, str(_AGENT_SKILLS))
    try:
        from tools.skill_gap.endgates import run_endgates

        auto = (os.environ.get("POWERCORE_ENDGATES_HOOK_AUTO") or "1").strip() != "0"
        result = run_endgates(prompt=prompt or "(hook)", response=response, auto=auto)
    except Exception as e:
        # Fail open — never block stop
        try:
            err_path = _CACHE_DIR / "last_error.txt"
            _CACHE_DIR.mkdir(parents=True, exist_ok=True)
            err_path.write_text(str(e), encoding="utf-8")
        except OSError:
            pass
        return {}

    follow = (os.environ.get("POWERCORE_ENDGATES_HOOK_FOLLOWUP") or "0").strip() in (
        "1",
        "true",
        "yes",
        "on",
    )
    if follow and result.get("lines") and not result.get("skipped"):
        # Only nudge when something actionable happened
        actionable = any(
            ("Auto-crystallized" in ln) or ("Skill gap suggested" in ln) for ln in result["lines"]
        )
        if actionable:
            return {"followup_message": "endgates:\n" + "\n".join(result["lines"][:5])}
    return {}


def main() -> int:
    mode = "stop"
    if len(sys.argv) > 1:
        mode = sys.argv[1].lstrip("-")
    payload = _read_stdin()
    if mode in ("sessionStart", "session-start", "session_start"):
        _write(session_start(payload))
    elif mode in ("afterAgentResponse", "after-agent-response", "after_agent_response"):
        _write(after_agent_response(payload))
    else:
        _write(stop(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
