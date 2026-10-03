---
name: tbcc-sprint-start
description: GSP v2.1 — initialize or reset tbcc/docs/SPRINT_STATE.md for a new sprint. Invoke with /sprint-start, start sprint, new sprint.
---

# TBCC Sprint Start Protocol (v1.0)

Changelog: Initial protocol — sprint state card initialization from user goal.

## Purpose

- Create or reset `tbcc/docs/SPRINT_STATE.md` so every subsequent session warm-starts with shared context.
- Capture sprint goal, blockers, do-not-touch, and definition of done before implementation.

## When to Invoke

- Trigger phrases: `/sprint-start`, `start sprint`, `new sprint`, `reset sprint state`
- Situational triggers:
  - Beginning a new feature arc or ops push
  - Prior sprint completed; need fresh goal
  - `SPRINT_STATE.md` missing or stale

## Execution Profile

- Mode: **Plan** first if goal unclear; **Agent** to write file once goal is known
- Model lane: **Lane A (Auto)**; **Lane B** if sprint spans architecture decisions
- Parallelism: optional readonly `explore` for backlog context from `TBCC_IMPROVEMENT_NOTES.md`
- Mode inheritance: explore stays readonly until file write

## Delegation & Tooling

- Skills invoked: `model-routing`, `protocol-author` (revisions)
- Files: `tbcc/docs/SPRINT_STATE.md`, `tbcc/docs/TBCC_IMPROVEMENT_NOTES.md` (read for deferred items)
- Commands: none required

## Behavioral Rules

- Reason by: one clear sprint outcome the user can recognize as done
- Avoid:
  - Vague goals ("improve TBCC")
  - Overwriting prior sprint history without user confirmation on reset
- Prioritize:
  - ≤5 definition-of-done checkboxes, testable
  - Explicit deferred list pointing to improvement notes
  - Realistic in-flight table (empty is fine)

## Output Contract

- Required sections:
  1. **Sprint goal** — one paragraph shown to user for confirm/edit
  2. **SPRINT_STATE.md** — full file written or reset
  3. **Next step** — recommend `/preflight` if goal implies multi-file work
- Done means: `SPRINT_STATE.md` exists with today's date and user-confirmed goal
- Artifacts: `tbcc/docs/SPRINT_STATE.md`
- Failure contract: if user goal too vague after one question, halt with draft goal for edit

## Exit Conditions

- Next: `/preflight` or direct implementation aligned to sprint goal
- Follows into: normal development under sprint-state + completion-gates rules

## Agent procedure

1. Read existing `SPRINT_STATE.md` and `TBCC_IMPROVEMENT_NOTES.md` deferred section.
2. Ask at most one question if goal not provided.
3. Write/reset `SPRINT_STATE.md` from template in repo.
4. Confirm goal with user; adjust on feedback.
