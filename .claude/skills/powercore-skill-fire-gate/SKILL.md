---
name: powercore-skill-fire-gate
description: >
  Require plan → edit → explicit approve before any skill tool fire. Deer-flow
  plan-edit-before-execute harvest. Use for /skill-fire-gate or blind tool fire.
---

# Skill Fire Gate — Claude Code twin

Thin mirror of `agent-skills/.cursor/skills/powercore-skill-fire-gate/SKILL.md` (canonical).
Same Output Contract and gate states: PLAN → EDIT → APPROVE → FIRE | ABORT.

## When to invoke

Same triggers as the Cursor skill. Prefer this twin in Claude Code sessions.

## Rules

- Stop after PLAN/EDIT until the operator pastes an explicit go/approve/fire/ACK.
- Do not invent approval from vibes.
- After FIRE on multiphase work that needs Cursor review: reverse report + `PASTE INTO CURSOR`.
- Compose: → `powercore-repo-trust` before vendor; do not touch TrapDoor Unicode paths (Threat Monitor B1).

## Triple Surface

Keep in sync with Cursor skill + `agent-skills/docs/gpt-paste/POWERCORE_SKILL_FIRE_GATE_GPT_PASTE.md`.
