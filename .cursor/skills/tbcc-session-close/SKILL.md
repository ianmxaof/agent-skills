---
name: tbcc-session-close
description: GSP v2.1 — end-of-block closure: completion gates, sprint state patch, improvement notes, optional ship-log. Invoke with /session-close, close session, end work block.
---

# TBCC Session Close Protocol (v1.1)

Changelog: v1.1 — branch-hygiene gate before auto-commit (mixed verticals block). v1.0 — gates + sprint state + notes + optional ship-log chain.

## Purpose

- Close a development block with verifiable quality, updated shared state, and optional public narrative.
- Chain completion gates → sprint state patch → improvement notes → optional ship-log draft.
- Use when finishing a work session, before context switch, or when user says they're done for now.

## When to Invoke

- Trigger phrases: `/session-close`, `close session`, `end work block`, `wrap up this session`
- Situational triggers:
  - Substantive code work completed in the session
  - User switching to another project or ending the day
  - After `/milestone-ship` for smaller incremental closes (milestone ship handles git push)

## Execution Profile

- Mode: **Agent** (read-only verify steps first, then patch docs)
- Model lane: **Lane A (Auto)**
- Parallelism: none
- Mode inheritance: n/a

## Delegation & Tooling

- Skills invoked: `tbcc-ship-log` (optional draft only), `model-routing`
- Commands: completion-gates checks, `git status`, `git diff --stat`
- Files: `tbcc/docs/SPRINT_STATE.md`, `tbcc/docs/TBCC_IMPROVEMENT_NOTES.md`
- MCP: Buffer MCP only if user explicitly requests publish

## Behavioral Rules

- Reason by: what actually shipped vs what remains
- Avoid:
  - Declaring done with failing gates
  - Auto-commit when `git status` hits ≥2 verticals (`tbcc-branch-hygiene.mdc`)
  - Rewriting entire sprint state or improvement notes files
  - Auto-publishing Buffer without user approval / milestone criteria
  - Skipping `git push` when `TBCC_AUTO_PUSH=1` after a successful session commit
- Prioritize:
  - Honest gate report (pass/skip/fail)
  - One vertical per commit / named branch
  - Minimal sprint state diff
  - User-visible wins in improvement notes table
  - Push to origin when auto-push is on; ship-log only if this close qualifies as a **milestone** (see `workflow-automation.mdc`)

## Output Contract

- Required sections:
  1. **Gates** — lint / tests / migration / stack / git / scope — each pass, skip-with-reason, or fail. **Git** must name current branch + verticals in the dirty tree.
  2. **Sprint state** — what was patched in `SPRINT_STATE.md` (or "unchanged")
  3. **Improvement notes** — row added or "none this session"
  4. **Ship-log** — 0–1 draft tweet if user-visible work shipped (optional; skip if trivial/rules-only)
  5. **Bottom line** — per bottom-line-next-steps rule with impact tags
- Done means: gates reported; if mixed verticals, **no commit** and a split menu was shown; sprint state current; user knows uncommitted git state
- Artifacts: patched `SPRINT_STATE.md`; optional `TBCC_IMPROVEMENT_NOTES.md` row
- Failure contract: if a gate fails, report failure first; do not mark sprint items complete; mixed-tree Git fail **does not** auto-recover by committing everything

## Exit Conditions

- Next: user picks from bottom line ladder
- Follows into: `tbcc-ship-log` (publish), `/milestone-ship` (git push), or idle

## Agent procedure

0. **Branch hygiene:** `git status` + current branch. Classify dirty paths (`tbcc-branch-hygiene.mdc`). If ≥2 verticals: Git gate **fail**; emit split menu; **do not auto-commit**; skip push. If wrong branch for the declared vertical: stash or switch before committing.
1. Run applicable completion gates on session changes.
2. Patch `SPRINT_STATE.md` — `Last updated`, **In flight**, **Definition of done** checkboxes, **CI/stack status** if known.
3. If user-visible feature/fix: add one row to `TBCC_IMPROVEMENT_NOTES.md` Implemented table.
5. Optionally draft one ship-log tweet **only if this close is a milestone** (do not publish unless asked / milestone-ship). Routine closes: commit+push only (single vertical).
6. If `TBCC_AUTO_PUSH=1` in `tbcc/.env` and commits were created this close: `git push -u origin HEAD` and report the remote branch.
7. Emit Output Contract + Bottom line.
