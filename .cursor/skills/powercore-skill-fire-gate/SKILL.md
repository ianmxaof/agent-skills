---
name: powercore-skill-fire-gate
description: >
  Require plan → edit → explicit approve before any skill tool fire. Deer-flow
  plan-edit-before-execute harvest. Use for /skill-fire-gate, blind tool fire,
  stump-out prevention, or "gate the next skill run".
purpose: >
  Block blind skill/tool execution until a short plan is written, edited if
  needed, and explicitly approved by the operator.
trigger_phrases:
  - /powercore-skill-fire-gate
  - /skill-fire-gate
  - skill fire gate
  - plan before execute
  - gate this skill run
  - no blind tool fire
inputs:
  - named next skill or tool action
  - optional draft plan from the agent
outputs:
  - gate state: PLAN | EDIT | APPROVE | FIRE | ABORT
  - approved plan text (or abort reason)
jev_hints:
  lane: chat
  cost: cheap
  needs_context: true
if_stumped: Ask once for the skill name and desired outcome; do not invent approval.
example_invocation: /skill-fire-gate before running /repo-trust on that gist
---

# Skill Fire Gate (v0.1)

Deer-flow **plan → edit → approve → execute** harvest for PowerCore skills.
Prevents stump-outs and blind tool fire. Does **not** replace Threat Monitor
sanitizer ownership or `/repo-trust` triage.

## Purpose

- Force a visible plan before any skill that mutates disk, talks to remotes, or vendors code.
- Let the operator edit the plan in chat before FIRE.
- Abort cleanly when approval is missing — never invent a go signal.

## When to invoke

- `/skill-fire-gate`, `plan before execute`, `gate this skill run`
- Before: `/repo-trust`, harvest installs, ACP/relay multi-tool bursts, unfamiliar vendor scripts
- **Skip:** read-only Q&A; already-approved multiphase `PASTE INTO …` fences that name the next step; Threat Monitor B1 Unicode path work (wrap sanitizer — do not re-gate those internals here)

## Freedom

- Freedom: **low** on gate states; **medium** on plan wording.

## Gate states (locked)

| State | Meaning |
|-------|---------|
| `PLAN` | Agent drafts ≤7 bullets: goal, inputs, commands/skills, stop conditions, do-not |
| `EDIT` | Operator changes the plan; agent rewrites only what they asked |
| `APPROVE` | Operator says go / approve / fire / ACK for this plan |
| `FIRE` | Run the named skill/tool exactly as approved |
| `ABORT` | Missing approval, scope creep, or operator stop |

## Output contract

```markdown
# Skill fire gate

## State
PLAN | EDIT | APPROVE | FIRE | ABORT

## Plan
- goal:
- inputs:
- skills/commands:
- stop when:
- do not:

## Approval
missing | quoted operator go-line | n/a (ABORT)

## Next
FIRE <skill> | wait for edit/approve | stop
```

## Procedure

1. Name the skill/action to gate. If unclear, ask once → `ABORT` if still missing.
2. Emit `PLAN` with the Output Contract (≤7 bullets). **Stop.** Do not run tools yet.
3. On operator edits → `EDIT`, revise plan, stop again.
4. On explicit approve (`go`, `approve`, `fire`, `ACK` for this plan) → `FIRE`.
5. On FIRE: invoke only the approved skill/commands. No Phase N+1, no start bots, no `.env`.
6. If the operator refuses or changes goal mid-flight → `ABORT`.

## Do-not

- Do not treat “looks good” vibes without a go-word as APPROVE.
- Do not FIRE install/vendor paths without a prior `/repo-trust` (or operator waiver in the plan).
- Do not rewrite TrapDoor Unicode extractors — Threat Monitor B1 owns shared sanitizer.
- Do not auto-chain into another ungated skill after FIRE completes unless the approved plan listed it.

## Harness attach

| Surface | Value |
|---------|-------|
| **MCP** | none |
| **Hooks** | endgates on stop |
| **Memory** | chat-ok (plan text) |
| **Compose** | → `powercore-repo-trust` before vendor; → `powercore-pipeline-fit` after HARVEST_OK |

## Triple Surface

| Surface | Path |
|---------|------|
| Cursor (canonical) | `agent-skills/.cursor/skills/powercore-skill-fire-gate/SKILL.md` |
| Claude Code twin | `<project>/.claude/skills/powercore-skill-fire-gate/SKILL.md` |
| GPT paste | `agent-skills/docs/gpt-paste/POWERCORE_SKILL_FIRE_GATE_GPT_PASTE.md` |

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-skill-fire-gate --check
```
