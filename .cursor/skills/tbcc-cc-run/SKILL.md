---
name: tbcc-cc-run
description: >-
  CC Relay execute hop — read the latest forward directive under tbcc/docs/handoffs/
  (or CURRENT_DIRECTIVE.md) and implement the active phase as TARGET. Invoke with
  /cc-run, /relay-run, /tbcc-cc-run, or "run the latest directive". Also honors a
  pasted Cursor PASTE INTO CLAUDE CODE ACK fence as the go signal. Does not author
  a new handoff; does not ask push-vs-Cursor as the main question.
---

# TBCC CC Run (v1.1) — CC Relay execute

Changelog: v1.1 — paste bridge: honor Cursor `PASTE INTO CLAUDE CODE` ACK; end with `PASTE INTO CURSOR`. v1.0 — execute latest forward directive; companion to Cursor `/directive` + `/cc-report`.

## Purpose

- You are the **TARGET** of a Cursor-authored directive already on disk **and/or** a pasted Cursor ACK fence.
- Load it, run the **active phase only** (or the fence’s `Do:`), write the reverse `_report.md`, then **STOP** with a paste fence for Cursor.
- Fix the failure mode where `/handoff-cc` / `/directive` inside Claude Code *repackages* work instead of doing it.

## When to Invoke

- Trigger phrases: `/cc-run`, `/relay-run`, `/tbcc-cc-run`, `run the latest directive`, `execute the handoff`, `do Phase N from the forward handoff`
- Situational: operator returns from Cursor after `/directive` or pastes a `PASTE INTO CLAUDE CODE` block and expects grind without reading
- **Skip:** no forward file / CURRENT_DIRECTIVE missing **and** no usable ACK fence → ask once for path. Operator wants a *new* directive authored → `/tbcc-directive-generator` instead. Review-only → tell them `/cc-report` is Cursor-side.

## Execution Profile

- Mode: **Agent** (implement)
- Model lane: Claude Code grind (this session)
- Parallelism: none
- Mode inheritance: n/a

## Delegation & Tooling

- Read: `tbcc/docs/handoffs/CURRENT_DIRECTIVE.md` first (pointer)
- Else: newest `tbcc/docs/handoffs/YYYY-MM-DD_*.md` that is **not** `*_report.md`
- Or: path named in the user message / ACK fence
- If the user paste starts with `PASTE INTO CLAUDE CODE`: treat `Verdict` / `Do` / `Do not` as the immediate work order; still ground Goal/Scope in the forward file when present
- Reverse write: matching `*_report.md` (stem + `_report`)
- Do **not** load `handoff-claude-code` / directive-generator to re-author unless the forward file is empty

## Behavioral Rules

- Reason by: disk forward file is source of truth for Goal/Scope; **pasted ACK fence wins** for “what to do next right now” when it names Phase N / amend / stop
- **Execute** Goal / Scope / active Phase / Verification from that file (or fence `Do:`)
- Prefer section titled `ACTIVE for /cc-run` or `## ACTIVE` if present; else the lowest unfinished Phase listed in the file / CURRENT_DIRECTIVE `active_phase`; else fence `Do:`
- Avoid: asking “push or hand to Cursor?” as the primary next step; inventing a new Goal; starting Phase N+1 unless the ACK fence says so; mass invites / bot Start / hard-cutover unless the fence allows it
- Prioritize: Fence + Prior state + judgment_ceiling in the forward file; island rules in `.claude/CLAUDE.md`; paste-bridge in `.cursor/rules/tbcc-cc-paste-bridge.mdc`

## Output Contract

1. State which file + which phase you are executing (one line)
2. Do the work
3. Append/write `tbcc/docs/handoffs/<stem>_report.md` for that phase
4. Commit if the forward file’s Working agreement says so (no secrets; no `git add -A`)
5. Stop with a fenced block:

```text
PASTE INTO CURSOR
/cc-report
Report: tbcc/docs/handoffs/<stem>_report.md
Status: Phase N complete | blocked
HEAD: <hash or uncommitted>
Do: review + ACK (paste fence back to Claude Code)
Do not: assume Phase N+1 started
```

Done means: reverse report updated and `PASTE INTO CURSOR` uttered.  
Failure: missing forward file → ask path once. Blocked on operator secret/id → report blocked + STOP (do not invent).

## Exit Conditions

- Next: operator blind-pastes into Cursor → **`/cc-report`** → ACK fence pasted back here
- Composes: → Cursor `cc-report` (not a CC skill)
- Do not auto-run the next phase unless the pasted ACK’s `Do:` explicitly starts it

## Agent procedure

1. If message contains `PASTE INTO CLAUDE CODE`, parse Verdict/Do/Do not first.
2. Resolve forward path via CURRENT_DIRECTIVE → else newest non-report handoff → else ask.
3. Read `active_phase` (pointer) or `ACTIVE for /cc-run` section or Phases list (or fence Do).
4. Execute **only** that phase against Goal/Scope/Constraints/Verification.
5. Write reverse report → STOP with `PASTE INTO CURSOR`.
6. Never open with “handoff is ready — push?” — if push is required by Working agreement + `TBCC_AUTO_PUSH=1`, push after commit as a footnote, still STOP for `/cc-report`.
