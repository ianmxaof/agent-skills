---
name: tbcc-preflight
description: GSP v2.1 — plan gate before multi-file TBCC implementation. Invoke with /preflight, TBCC preflight, or before ≥3-file edits.
---

# TBCC Preflight Protocol (v1.0)

Changelog: Initial protocol — blast-radius map, scope fence, verification plan before multi-file edits.

## Purpose

- Prevent wrong-layer refactors and runaway scope before implementation starts.
- Produce a user-approvable plan with files in/out of scope, risks, and verification commands.
- Use when a task likely touches **≥3 files**, spans **backend + frontend/extension**, or has ambiguous blast radius.

## When to Invoke

- Trigger phrases: `/preflight`, `TBCC preflight`, `preflight this`, `plan before implementing`
- Situational triggers:
  - User requests a feature/refactor without an explicit file list
  - Sprint state goal implies cross-cutting work
  - Agent would otherwise edit >3 files on first pass

## Execution Profile

- Mode: **Plan** (required); may switch to **Agent** only after user says go / implement / proceed
- Model lane: **Lane A (Auto)** for explore + plan; **Lane B (frontier)** if architecture fork with high blast radius
- Parallelism:
  - `explore` subagent, **readonly**, cheap model — map files, callers, tests, migrations
  - Mode inheritance: explore subagents stay readonly Plan; implementation subagents forbidden until user approves
- Mode switching: allowed Plan → Agent after explicit approval only

## Delegation & Tooling

- Skills invoked: `model-routing`, `protocol-author` (revisions only)
- Commands: `git diff --stat`, grep/search, `tbcc/docs/TEST_MAP.md`, `tbcc/docs/SPRINT_STATE.md`
- MCP: none required

## Behavioral Rules

- Reason by: blast radius first — what breaks, what tests exist, what migrations needed
- Avoid:
  - Editing code during preflight (readonly until approved)
  - Open-ended scope ("improve the module")
  - Skipping out-of-scope list
- Prioritize:
  - ≤12 files in first implementation slice (scope budget); larger work → phased plan
  - Name exact pytest commands from TEST_MAP
  - Align to `SPRINT_STATE.md` sprint goal

## Output Contract

- Required sections:
  1. **Goal** — one sentence, testable done condition
  2. **Blast radius** — files/dirs in scope, explicitly out of scope
  3. **Risks** — migrations, stack/bots, session locks, secrets
  4. **Verification** — exact commands (lint, pytest, stack status)
  5. **Phases** — if >8 files, numbered slices with independent verify per phase
  6. **Approval** — ask user to pick: proceed / narrow scope / defer
- Done means: plan delivered; **no code changed** unless user already said implement
- Artifacts: plan in chat only (optional: append decision to `tbcc/docs/DECISIONS.md` if architectural fork)
- Failure contract: if explore fails or scope cannot be bounded, halt with what was found and ask one clarifying question

## Exit Conditions

- Next: user says go → Agent mode implementation with scope fence
- Follows into: normal work under completion-gates; `/handoff-cc` if grind is Lane C

## Agent procedure

1. Read `tbcc/docs/SPRINT_STATE.md`.
2. Spawn readonly `explore` if scope is unclear (cheap model).
3. Emit Output Contract sections 1–6.
4. Wait for user approval before any edits.
