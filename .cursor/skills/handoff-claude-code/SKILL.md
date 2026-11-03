---
name: handoff-claude-code
description: GSP v2.1 — package work for Claude Code (Lane C). Invoke with /handoff-cc, hand off to Claude Code, or Lane C grind.
---

# Claude Code Handoff Protocol (v1.2)

Changelog: v1.2 — raw issue dumps run `directive-generator` first (`DIRECTIVE_GENERATOR_GPT_PASTE.md`). v1.1 — reverse `_report.md` + Cursor ACK between phases.

## Purpose

- Package the current task into a self-contained prompt for Claude Code (Lane C per model-routing skill).
- Free Cursor for interactive work while long mechanical grinds run in a separate quota.
- Use when work is low-judgment, long-running, or user explicitly requests Claude Code.

## Upstream (raw issues)

- If the operator only has a messy issue dump + “prompt for Claude Code”, run **`directive-generator`** first (`/directive`, `generate a directive`) — it normalizes issue cards, target profile, fence, and verification.
- Then reshape or paste that emit into this handoff block template. Do **not** skip reverse-report / phase STOP rules here.
- Browser twin for cross-model use: `tbcc/docs/DIRECTIVE_GENERATOR_GPT_PASTE.md`

## When to Invoke

- Trigger phrases: `/handoff-cc`, `hand off to Claude Code`, `Lane C`, `Claude Code grind`
- Situational triggers:
  - model-routing selects Lane C (40+ file codemod, boilerplate test sweep)
  - Cursor session needs parallel offline grind
  - Bottom line option 4–5 is Lane C sized
  - `directive-generator` already emitted a Claude Code–targeted block that needs Lane C packaging

## Execution Profile

- Mode: **Agent** (emit handoff block only — no implementation in Cursor unless user says otherwise)
- Model lane: **Lane C (Claude Code)** for execution; **Lane A** in Cursor to build the handoff
- Parallelism: none in Cursor
- Mode inheritance: n/a

## Delegation & Tooling

- Skills invoked: `model-routing`, `tbcc-preflight` (if scope not yet bounded), **`claude-code-report`** (reverse report contract), **`directive-generator`** (when issues are raw / unstructured)
- Commands: verification commands embedded in handoff (pytest, lint)
- MCP: none

## Behavioral Rules

- Reason by: Claude Code has **zero** chat context — everything critical goes in the block
- Avoid:
  - "The function we discussed" or any chat-only references
  - Open-ended scope without file lists or counts
  - Handoff without verification command
  - Opus-level judgment tasks on Lane C (Sonnet-class only on Claude Pro)
  - Expecting the user to paste Claude Code TUI back into Cursor
  - Building a Lane C handoff from an unstructured issue dump without normalizing via `directive-generator` (or manually applying the same card/profile/fence rules)
- Prioritize:
  - Goal, scope, out-of-scope, constraints, verification, working agreement, phases
  - Phases independently verifiable if job may exceed 5-hour window
  - Each phase ends with writing `tbcc/docs/handoffs/YYYY-MM-DD_<topic>_report.md` then **stop**

## Output Contract

- Required sections:
  1. **Handoff block** — single fenced code block, paste-ready for Claude Code
  2. **Quota reminder** — run `/usage` in Claude Code; check weekly cap + 5-hour window
  3. **Lane note** — pull Opus-level phases back to Lane B in Cursor
  4. **Reverse report path** — name the expected `*_report.md` and point at `/cc-report` / `claude-code-report`
- Done means: handoff block is self-contained with verification commands **and** a required reverse-report filename
- Artifacts: handoff block in chat; save forward prompt to `tbcc/docs/handoffs/YYYY-MM-DD_<topic>.md` when lasting more than one session
- Failure contract: if scope unbounded, run `/preflight` first or halt and ask one scoping question

## Exit Conditions

- Next: user pastes block into Claude Code terminal
- Follows into: Claude writes `*_report.md` → user says “read the CC report” → Cursor runs **`claude-code-report`** review → ACK before next phase

## Handoff block template (inside fenced code block)

1. **Goal** — testable definition of done
2. **Scope** — repo root, in-scope paths, **out of scope**
3. **Constraints & gotchas** — conventions, traps from this session
4. **Verification** — exact commands (e.g. `pytest tbcc/backend/tests/test_foo.py -x`)
5. **Working agreement** — commit per phase vs uncommitted; branch; push yes/no; **after each phase write** `tbcc/docs/handoffs/YYYY-MM-DD_<topic>_report.md` using the reverse-report structure, then **stop with a `PASTE INTO CURSOR` fence** for `/cc-report` (do not start next phase). Cursor ACK returns as `PASTE INTO CLAUDE CODE` — see `.cursor/rules/tbcc-cc-paste-bridge.mdc`
6. **Phases** — numbered, each ends with verification command **and** reverse report file
