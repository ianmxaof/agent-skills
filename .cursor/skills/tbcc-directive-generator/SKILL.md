---
name: tbcc-directive-generator
description: Turns a target agent (another Claude Code instance, Cursor, or a browser-chat GPT like ChatGPT/DeepSeek/Gemini) plus a raw issue dump into a cold-start, paste-ready directive with issue cards, a target profile, a fence, verification, and a reverse stop-gate. Invoke with /tbcc-directive-generator, /directive, "generate a directive", or "handoff prompt for X".
---

# TBCC Directive Generator

Adapted from `~/.cursor/skills/directive-generator/SKILL.md` (v1.3) — Cursor's model-lane routing (Desktop Auto / Frontier Plan-Ask / Cloud Agent) is dropped, since Claude Code has no equivalent lanes (the same adaptation `tbcc-entropy-scan` and `.claude/CLAUDE.md`'s Next-steps ladder already made). Cursor's sibling skills that don't exist on this side (`handoff-claude-code`, `claude-code-report`, `tbcc-preflight`) are replaced with what actually exists here: `tbcc-cc-run` (TARGET-side execution) and the CC Relay reverse-report convention already in `.claude/CLAUDE.md`.

## Purpose

Produce a self-contained, paste-ready directive for a **cold** receiving agent — zero prior chat context. Two shapes, chosen by TARGET:

- **Agentic TARGET** (another Claude Code instance, Cursor, a cloud agent) — has filesystem/tool access. Emit persists as a forward handoff file, and only *carefully* touches `CURRENT_DIRECTIVE.md` (see Constraints).
- **Chat-only TARGET** (ChatGPT, DeepSeek, Gemini, Grok web UI, or any GPT with no file access) — gets a single self-contained fenced block instead, since it can't read a repo path. Companion doc: `tbcc/docs/DIRECTIVE_GENERATOR_GPT_PASTE.md`.

## When to invoke

- Trigger phrases: `/tbcc-directive-generator`, `/directive`, "generate a directive", "handoff prompt for X", "directive for Claude Code / Cursor / ChatGPT / DeepSeek / Gemini"
- Situational: the operator pastes an unstructured issue dump and names (or clearly implies) a receiving agent, or asks to package this session's findings for someone else to pick up
- **Skip:** the operator already has a scoped Goal/paths/verify and just wants this session to *execute* now — that's plain implementation or `/cc-run`, not this. Per `.claude/CLAUDE.md` § Directive Generator: "do not implement in the author turn unless they say execute here."

## Behavioral rules

- Reason by: the cold agent has **zero** chat context — every fact it needs goes into the emit, never "as discussed above."
- Avoid: chat-only references; emitting without a Verification section; smuggling doctrine/pricing judgment into a grind-mode TARGET; implementing instead of emitting; unbounded "fix everything" without a Fence; silently overwriting `CURRENT_DIRECTIVE.md` when it already points at an active, un-ACK'd thread — check it first (see Constraints).
- Prioritize: Literal ask → issue cards → target profile → Ascend/Fence → Emit → Stop.

If TARGET is missing, ask once. If ISSUES are empty, ask once. Do not invent issues or Prior State from chat vibes — `.claude/CLAUDE.md` states this explicitly for anyone targeting a Claude Code session.

## Issue card schema

| Field | Required | Notes |
|---|---|---|
| id | yes | I1, I2, … |
| symptom | yes | one line |
| evidence | yes | a real path/log/repro this session actually checked — mark `unknown` rather than guess |
| severity | yes | P0 / P1 / P2 |
| depends_on | yes | I# or none |
| acceptance | yes | testable |

## Target profile schema

| Field | Required | Notes |
|---|---|---|
| mode | yes | Plan / Agent / grind |
| tools | yes | what the TARGET actually has — filesystem+shell (Claude Code/Cursor/cloud agent) vs. none (browser chat) |
| judgment_ceiling | yes | MAY / MUST NOT — ties to `.claude/CLAUDE.md`: "Cursor owns judgment (pricing, doctrine); Lane C implements locked plans only." A grind TARGET is always MUST NOT on doctrine/pricing calls. |
| context | implied | always ZERO prior chat |

## Output contract

1. **Preface** (outside the fence, short) — Literal ask; Ascend yes/no + one line; TARGET named.
2. **Emit** — one fenced block, paste-ready:
   - Goal
   - Scope (in + **Out of scope**)
   - Prior state (`none — greenfield`, or continuity bullets citing real paths this session verified — not guessed)
   - Issue cards (≤8)
   - Constraints & gotchas (include the judgment ceiling)
   - Verification (≥1 exact command or observable check)
   - Working agreement (reverse report + STOP for ACK if multiphase/grind)
   - Phases (only if >1; each ends verify + reverse report when grind)
   - Target profile
3. **Paste line** — say exactly where it goes:
   - Agentic TARGET: `Save as tbcc/docs/handoffs/YYYY-MM-DD_<topic>.md; only point CURRENT_DIRECTIVE.md at it after the Constraints check below.`
   - Chat-only TARGET: `Paste into <TARGET>'s chat window as-is — self-contained, no file access assumed.`
4. **Reverse path** — `tbcc/docs/handoffs/YYYY-MM-DD_<topic>_report.md` for a TBCC grind; otherwise a "structured reverse reply" spec (Done / Files touched / Verification / Risks / Do not continue until ACK).

Done means: the emit would survive a cold start — no chat-only refs, Verification present, Fence present, and every Prior State claim traceable to a real file this session actually read.

## Constraints specific to this repo

- **`CURRENT_DIRECTIVE.md` guard**: read it before pointing it at a new directive. If it already names an active, un-ACK'd thread, do not overwrite it — emit the forward handoff file standalone and tell the operator explicitly that the pointer was left alone and why. Not hypothetical: `tbcc/docs/handoffs/2026-08-25_llm-rotator-auto-routing-directive.md` was deliberately kept out of `CURRENT_DIRECTIVE.md` this same week because that pointer was already on the loot-forum-twin thread.
- **Verify Prior State before writing it.** A directive claiming "X already does Y" must be backed by this session actually having read X — not a plausible guess. This repo already caught one ungrounded secondhand summary this week (`claritas.txt`'s first pass on the CL4R1T4S repo); don't reintroduce the same failure mode in the other direction by fabricating Prior State for the *next* agent.
- Chat-only TARGETs (GPT paste twin) cannot run `pytest` or check a file — their Verification section must be either "ask a human to run X and paste the output back" or a self-checkable logic/output description, never a shell command they can't execute.

## Exit conditions

- Agentic TARGET, TBCC-side: the operator (or this session) runs the forward handoff via `/cc-run` in the receiving Claude Code instance, or pastes the fence directly into Cursor/a cloud agent.
- Multiphase grind: reverse `_report.md` → operator ACK → next phase. Do not auto-implement past Phase 0 unless the operator says "execute here."
- Chat-only TARGET: nothing to exit-condition on this side — the paste is the deliverable. If the operator brings a reply back from it, treat that reply the same as any pasted secondhand analysis: `tbcc-integration-scan`'s verify-before-trust rule applies before acting on any of it.

## Procedure

1. Parse TARGET + ISSUES from the operator's ask, plus any repo/branch/sprint/do-not-touch context already visible this session.
2. Read `tbcc/docs/SPRINT_STATE.md` for the current goal/do-not-touch list, and `tbcc/docs/handoffs/CURRENT_DIRECTIVE.md` for the guard above.
3. Normalize ISSUES into cards — verify each `evidence` path by reading it; mark `unknown` rather than guess.
4. Decide Ascend (one higher-yield slice) or Fence-as-is — same discipline as `tbcc-entropy-scan`.
5. Run `SYNTHESIS_COMPRESSION` from `tbcc/docs/prompt-chains/SYNTHESIS_COMPRESSION.yaml` on the normalized issue summary; use the one-sentence output as **Goal** in the emit fence (inline — see `tbcc-prompt-chains`).
6. Emit per the Output Contract, branching the Paste line and Verification shape by the TARGET's actual tool access.
7. If TARGET is Claude Code and the operator confirms this is the active thread, update `CURRENT_DIRECTIVE.md` and add an `ACTIVE for /cc-run` section to the forward file. Otherwise leave `CURRENT_DIRECTIVE.md` untouched.
8. Stop. Do not implement the issues in this turn unless the operator explicitly says to execute here.

Companion for chat-only targets: `tbcc/docs/DIRECTIVE_GENERATOR_GPT_PASTE.md`. Keep both in sync when tightening either one.
