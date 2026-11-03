---
name: powercore-cleanroom-brief
description: Evidence-gated clone brief for any web surface. Runs deterministic
  captures, wraps them in an evidence record with confidence/coverage/limitations,
  then emits a build brief and a pass/fail delta against the result. Use for
  /cleanroom, /cleanroom-brief, clone this correctly, or evidence-gated rebuild.
---
# Cleanroom Brief — Claude Code twin

Thin mirror of `agent-skills/.cursor/skills/powercore-cleanroom-brief/SKILL.md` (canonical).
GPT paste: `agent-skills/docs/gpt-paste/POWERCORE_CLEANROOM_BRIEF_GPT_PASTE.md`.

## When

Evidence-gated rebuild check — not aesthetics-only clone or feature inventory alone.

## Modes

- `clean` (default): screenshots @ 390/768/1440, measured layout/colour/font — no source/JS
- `deep`: adds source/JS (`--deep`)

## Steps

1. Capture → evidence record (`id, kind, value, confidence, coverage, limits`)
2. Envelope module (Cursor canonical): `agent-skills/.cursor/skills/powercore-cleanroom-brief/scripts/evidence_envelope.py`
3. Emit build brief (must-match list)
4. After build: re-capture → pass/fail delta (`delta()` = Phase 2, not yet)
5. Big records: summary first

## Output contract

`# Cleanroom brief` → Source · Evidence summary · Build brief · Check delta · Next

## Do not

- Score without both captures; invent confidence; claim pass without delta
- Start Phase N+1 from a wait/fix Cursor fence

## Relay

After grind phases needing Cursor review: reverse report + `PASTE INTO CURSOR`.
