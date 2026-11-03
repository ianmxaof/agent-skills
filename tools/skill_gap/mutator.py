"""Propose and apply one SKILL.md change for the overnight loop."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from .body_assertions import missing_body_needles


@dataclass
class Mutation:
    kind: str
    detail: str
    applied: bool = False


def backup_skill(skill_md: Path) -> Path:
    bak = skill_md.with_suffix(".md.overnight.bak")
    shutil.copy2(skill_md, bak)
    return bak


def restore_skill(skill_md: Path, bak: Path) -> None:
    if bak.is_file():
        shutil.copy2(bak, skill_md)


def _ensure_output_contract_bullets(text: str, needles: list[str]) -> str:
    block = "\n".join(f"- REQUIRED: `{n}` must appear in multiphase ACKs." for n in needles)
    marker = "## Output Contract"
    if marker in text:
        return text.replace(marker, marker + "\n\n" + block + "\n", 1)
    return text.rstrip() + f"\n\n{marker}\n\n{block}\n"


def _ensure_description_phrases(text: str, phrases: list[str]) -> str:
    """Append missing trigger phrases into the YAML description fold."""
    m = re.match(r"(---\s*\n)(.*?)(\n---\s*\n)(.*)$", text, re.S)
    if not m:
        return text
    pre, fm, mid, body = m.group(1), m.group(2), m.group(3), m.group(4)
    dm = re.search(r"^(description:\s*[>|]?\s*)(.*?)(?=\n[a-zA-Z_-]+:|\Z)", fm, re.S | re.M)
    if not dm:
        return text
    prefix, desc = dm.group(1), dm.group(2)
    lower = desc.lower()
    add = [p for p in phrases if p.lower() not in lower]
    if not add:
        return text
    extra = " Also trigger on: " + ", ".join(add) + "."
    # Keep description as folded style
    new_desc = desc.rstrip() + extra + "\n"
    new_fm = fm[: dm.start()] + prefix + new_desc + fm[dm.end() :]
    return pre + new_fm + mid + body


def _append_live_hint(text: str, failed_ids: list[str]) -> str:
    hint = (
        "\n## Overnight live-eval note\n\n"
        "- When answering `/cc-report` style prompts, every multiphase reply MUST include a fenced "
        "`PASTE INTO CLAUDE CODE` block with `Verdict:`, `Report:`, `Do:`, and `Do not:` lines. "
        f"(Failed live cases: {', '.join(failed_ids) or 'unknown'}.)\n"
    )
    if "## Overnight live-eval note" in text:
        return text
    return text.rstrip() + "\n" + hint


def propose_and_apply(
    skill_dir: Path,
    *,
    body_result: dict,
    trigger_result: dict,
    live_result: dict | None = None,
) -> Mutation | None:
    """Apply exactly one mutation. Returns None if nothing to fix."""
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8", errors="replace")

    # Priority 0: repair demo / corruption placeholders
    if "PASTE_INTO_CURSOR_REMOVED" in text:
        skill_md.write_text(
            text.replace("PASTE_INTO_CURSOR_REMOVED", "PASTE INTO CURSOR"),
            encoding="utf-8",
        )
        return Mutation(kind="repair_placeholder", detail="restore PASTE INTO CURSOR", applied=True)

    # Priority 1: body contains-failures
    if not body_result.get("ok"):
        missing = missing_body_needles(skill_dir)
        if missing:
            new_text = _ensure_output_contract_bullets(text, missing[:4])
            if new_text != text:
                skill_md.write_text(new_text, encoding="utf-8")
                return Mutation(kind="body_insert", detail=f"inserted {missing[:4]}", applied=True)
        # not_contains failures: strip known retired affirmative wording
        bad = "ACK stays in Cursor. Do not paste"
        if bad in text:
            skill_md.write_text(text.replace(bad, "Use the paste fence instead"), encoding="utf-8")
            return Mutation(kind="strip_retired_ack", detail=bad, applied=True)

    # Priority 2: trigger failures (should_trigger true but predicted false)
    if not trigger_result.get("ok"):
        failed = [
            c
            for c in (trigger_result.get("cases") or [])
            if not c.get("ok") and c.get("should_trigger")
        ]
        if failed:
            # Pull phrases from triggers.json
            phrases_path = skill_dir / "evals" / "triggers.json"
            phrases: list[str] = []
            if phrases_path.is_file():
                import json

                data = json.loads(phrases_path.read_text(encoding="utf-8"))
                phrases = [str(p) for p in (data.get("phrases") or [])][:8]
            # Also use words from failed prompt ids
            for c in failed:
                pid = str(c.get("id") or "")
                if pid:
                    phrases.append(pid.replace("-", " "))
            new_text = _ensure_description_phrases(text, phrases)
            if new_text != text:
                skill_md.write_text(new_text, encoding="utf-8")
                return Mutation(
                    kind="description_phrases",
                    detail=f"boost triggers for {[c.get('id') for c in failed]}",
                    applied=True,
                )

    # Priority 3: live failures
    if live_result and not live_result.get("ok") and not live_result.get("skipped"):
        failed_ids = [str(c.get("id")) for c in (live_result.get("cases") or []) if not c.get("ok")]
        if failed_ids:
            new_text = _append_live_hint(text, failed_ids)
            if new_text != text:
                skill_md.write_text(new_text, encoding="utf-8")
                return Mutation(kind="live_hint", detail=f"live fail {failed_ids}", applied=True)

    return None
