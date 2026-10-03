---
name: tbcc-continue-thread
description: >-
  GSP v2.4 — after a CC reverse-report ACK, resurface deferred/out-of-scope as the
  next directive path. Invoke with /continue-thread, next directive, what should
  CC do next, pick up deferred.
---

# TBCC Continue Thread (v1.0)

Changelog: Initial — deferred-first continue after ACK; optional entropy lens; feeds directive-generator.

## Purpose

- Close the gap between “slice shipped / standing by” and “what do I paste into Claude Code next.”
- Read the latest reverse report’s fence / out-of-scope / open questions and put **deferred work first**.
- Do not invent a greenfield plan when the report already named the next proof.

## When to Invoke

- Trigger phrases: `/continue-thread`, `next directive`, `what should CC do next`, `pick up deferred`, `continue the CC thread`
- Situational: after `/cc-report` ACK; CC message ends with “standing by for the next directive”
- **Skip:** no handoff report exists; operator wants an unrelated new vertical; “just the bug” on a named file

## Execution Profile

- Mode: **Plan / Ask** then emit; Agent only if they ask to run `/directive` after
- Model lane: Desktop Auto for packing; Frontier Plan/Ask if deferred items are monetization/doctrine
- Parallelism: none
- Mode inheritance: n/a

## Delegation & Tooling

- Read latest matching `tbcc/docs/handoffs/*_report.md` (or path the operator names)
- Optional: `tbcc/docs/entropy-lenses.json` + `tbcc-entropy-scan` when several deferred items compete
- Then: `directive-generator` / `handoff-claude-code` on pick
- Chains: `tbcc/docs/protocol-chains.json` edges `cc-report-ack-to-continue`, `continue-to-directive`, `continue-to-entropy`

## Behavioral Rules

- Reason by: confirm prior slice done-condition → list deferred / out-of-scope / open questions from the report → recommend **one** next slice with a testable done-condition
- Prefer report-authored deferred over new ideas
- Avoid: re-opening fenced “do not touch”; island deploy unless deferred says so; unbounded vision architecture
- Prioritize: operator ACK state; sprint goal; reversible verification slices (e.g. ground-truth re-test before new models)

## Output Contract

- Required:
  1. **Prior slice** — done? (yes/no + one evidence line)
  2. **Deferred** — ≤5 bullets from the report fence / open list
  3. **Recommend** — one next slice + done-condition + suggested lens if useful
  4. **Paste path** — `/directive` vs `/entropy-scan <lens>` vs `/handoff-cc`
- Done means: operator can paste or pick without inventing glue
- Failure: if report missing sections, halt and ask which handoff file

## Exit Conditions

- Next: `/directive` or `/entropy-scan <lens>` or `/handoff-cc` per Recommend
- Composes: → `directive-generator` | `entropy-scan` | `handoff-claude-code`
- Follows into: Bottom line **Compose:** row with the alias

## Agent procedure

1. Locate the report (operator path or newest `*_report.md` for the thread topic).
2. Emit Output Contract. Do not implement the deferred work until they pick.
