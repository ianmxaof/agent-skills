---
name: tbcc-entropy-scan
description: >-
  Runs a capped leftover-yield scan with evidence-scored vertices across a lens
  rolodex (revenue, innovation, devops, marketing). Invoke with /entropy-scan,
  /entropy-scan marketing, /entropy-scan brainstorm, scour vertices.
---

# TBCC Entropy Scan (v1.2-dev)

Changelog: v1.2 (in progress) — S1: evidence + confidence per vertex, self-correct step. v1.1 — lens registry via `tbcc/docs/entropy-lenses.json`; compose Exit. v1.0 — initial conversion scan.

## Purpose

- Surface missed yield **before** locking a plan — then stop for a pick.
- Lenses change the vertex axes only; the four-section contract stays the same.
- Not an always-on executive for every bug fix.

## When to Invoke

- Trigger phrases: `/entropy-scan`, `/entropy-scan <lens>`, `entropy scan`, `scour vertices`, `max yield this request`, `conversion vertices`, `/tbcc-entropy-scan`
- Situational: product/funnel/pricing/CTA; or topic matches a lens `when_hints` in the JSON (e.g. notification tone → `marketing`)
- **Skip:** named file-level bug fix; docs/lint/pytest only; tray / Telethon / `.env` / bot spawn; island deploy mechanics; “just the bug” / “literal only”

## Execution Profile

- Mode: **Plan / Ask**; no code edits during the scan
- Model lane: Frontier Plan/Ask when judgment gate fires; Auto for small copy/CTA; never Cloud for the scan itself
- Parallelism: optional one readonly cheap explore
- Mode inheritance: explore stays readonly

## Delegation & Tooling

- **Required read:** `tbcc/docs/entropy-lenses.json` (axes + infer_rules)
- Also: `tbcc/docs/SPRINT_STATE.md`; paste twin `tbcc/docs/ENTROPY_SCAN_GPT_PASTE.md`
- After pick: `tbcc-preflight` if ≥3 files; else implement / `directive-generator` per chains
- Optional text lens (Plan only): `tbcc-prompt-chains` → `ENTROPY_AUDIT` on a pasted docs/handoff excerpt when vertices flag stale assumptions — not a replacement for this scan
- MCP: none; do not Start bots

## Behavioral Rules

- Resolve lens: explicit `/entropy-scan <lens>` → else infer from `infer_rules` → else default `revenue` only for funnel/money asks; if topic is clearly non-revenue, **ask once** or use inferred lens (do not force monetization axes on devops/marketing threads)
- Reason by: literal → ≤5 vertices on that lens’s `vertex_axes` → one slice or no-ascend
- Avoid: fake FOMO; dark patterns; rewriting Do not touch; unbounded implementation
- Prioritize: operator done-condition; sprint goal; reversible slices

## Output Contract

- Required (dense), still exactly **four** sections — depth lives inside the Vertices lines, never as a fifth section:
  1. **Literal ask** — one sentence (+ **Lens:** name)
  2. **Vertices** — ≤5 lines, one of:
     - `- [missed·<high|med|low>] <axis> — <claim> · ev: <path:line | cmd output | "inferred">`
     - `- [covered·<high|med|low>] <axis> — <claim> · ev: <...>`
     - a `blocked` line — see Behavioral Rules for the `(hard)`/`(soft)` form
     - `ev: inferred` (no file/cmd evidence) forces `conf: low` — never `high`/`med` on a vibe
  3. **Ascend?** — yes + one slice + done-condition **or** no + why literal
  4. **Fence** — in / out
- Done means: operator picked or said literal only; **no code** in this protocol
- Failure: blocked vertex → tag and stop expanding

### Self-correct

1. **Draft** the four sections.
2. **Check**: every `missed`/`covered` line has `ev:`; `ev: inferred` lines are `conf: low`; ≤5 vertex lines total.
3. **Revise** once if any check fails — fix the line, don't drop the section.

## Exit Conditions

- Next: pick → `/preflight` if ≥3 files, else implement on Desktop Auto; or `/directive` for Lane C
- Composes: → `preflight` | `directive-generator` | `tbcc-prompt-chains` (ENTROPY_AUDIT / LEVERAGE_MATRIX on option sets) | implement
- Follows into: Bottom line **Compose:** when a chain edge is obvious

## Agent procedure

1. Read sprint state + `entropy-lenses.json`. Resolve lens.
2. If skip matches: one line, do literal ask.
3. Emit four sections. Stop for pick.
