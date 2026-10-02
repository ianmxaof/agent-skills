---
name: powercore-cc-cc-relay
description: >-
  Claude Code ↔ Claude Code ACK/handoff when Cursor is dark — Planner reviews
  *_report.md and emits PASTE INTO CC-GRINDER; Grinder runs one phase and emits
  PASTE INTO CC-PLANNER. Never emit PASTE INTO CURSOR while this skill is active.
  Invoke with /cc-cc, /cc-pair, two Claude sessions, Cursor usage gone.
---

# PowerCore CC↔CC Relay — Claude Code twin (v1.1)

Canonical: `agent-skills/.cursor/skills/powercore-cc-cc-relay/SKILL.md`.

## Critical override

While `/cc-cc` is active, **do not emit** `PASTE INTO CURSOR` or `PASTE INTO CLAUDE CODE`
(even though `tbcc-cc-run` / CLAUDE.md say that). Emit only:

- Grinder STOP → `PASTE INTO CC-PLANNER`
- Planner ACK → `PASTE INTO CC-GRINDER`

## Sticky roles

State once: `Role: Planner` or `Role: Grinder`. Do not flip when a mislabeled
`PASTE INTO CURSOR` arrives in the wrong window — say **Wrong window** and stay put.

## Operator courier

STOP fence → paste into **PLANNER** window only.  
ACK fence → paste into **GRINDER** window only.  
Never paste a STOP back into the session that emitted it.

## Pickup after Cursor→CC switch

Agents do not inherit the other chat. Continue from **disk report + fence Do:**.
Operator must label windows and declare roles before the next hop.
