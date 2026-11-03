---
name: tbcc-protocol-conductor
description: >-
  GSP v2.4 — thin overseer: match protocol-chains.json edges and surface the next
  slash/situational hop (menu only). Invoke with /conductor, what command next,
  standing by for next directive, which protocol next.
---

# TBCC Protocol Conductor (v1.0)

Changelog: Initial — compose-edge matcher over protocol-chains.json; no fat manager; Bottom line Compose: surfacing.

## Purpose

- After a completion (or when the operator asks “what command next”), pick the **obvious next protocol** from the chain graph.
- Keep leaf skills as leafs — this skill only **routes and recommends**, it does not re-implement entropy, directive, or handoff.
- Same idea as browse-intel tying unrelated pages: one thin shared layer, many surfaces.

## When to Invoke

- Trigger phrases: `/conductor`, `what command next`, `which protocol next`, `standing by for next directive`, `hand off to the next agent`
- Situational: CC says “standing by”; `/cc-report` ACK just landed; operator finished a slice and the next hop is ambiguous
- **Skip:** operator already named the next protocol; pure trivia; live bot/`.env` control

## Execution Profile

- Mode: **Ask / Plan** (menu only). Do not auto-run the next protocol unless the operator picks it or a workflow-automation row says to run it.
- Model lane: Desktop Auto. Frontier only if choosing among revenue/doctrine edges.
- Parallelism: none
- Mode inheritance: n/a

## Delegation & Tooling

- Read: `tbcc/docs/protocol-chains.json`, optional `tbcc/docs/entropy-lenses.json`, latest `tbcc/docs/handoffs/*_report.md` when from=cc-report/continue
- May **recommend** loading: `continue-thread`, `tbcc-entropy-scan`, `directive-generator`, `tbcc-prompt-chains`, `handoff-claude-code`, `claude-code-report`
- MCP: none. Do not Start bots.

## Behavioral Rules

- Reason by: **situational-match** only (reuse registry triggers + `when_hints` + thread topic). No separate NLP stack.
- Prefer edges whose `when_hints` clearly hit the last completion. Cap recommendations at **3**.
- If a topic edge fits (e.g. payment notification copy → `/entropy-scan marketing`), surface it even when `from` is `*`.
- Avoid: inventing new protocols inline; merging skills into this file; auto-executing without a pick (except existing zero-command rows in `workflow-automation.mdc`).
- Prioritize: operator time-to-next-command; sprint goal; reversible hops.

## Output Contract

- Required sections:
  1. **Just finished** — one line (protocol or work kind)
  2. **Next hops** — ≤3 bullets: `alias` · why matched · lens if any
  3. **Recommend** — single best hop (or “none obvious”)
  4. **Fence** — will not auto-run unless they pick
- Done means: operator has a clear pick; no code changed by the conductor itself
- Failure: if chains JSON missing, say so and fall back to registry + Exit Conditions only

## Exit Conditions

- Next: operator picks a hop → load that skill fully
- Composes: → `continue-thread` | `entropy-scan` | `directive-generator` | `handoff-claude-code` (by pick)
- Follows into: Bottom line may repeat the Recommend as a **Compose:** ladder row

## Agent procedure

1. Read `tbcc/docs/protocol-chains.json`.
2. Match edges against last completion + thread hints.
3. Emit Output Contract. Stop for pick.
