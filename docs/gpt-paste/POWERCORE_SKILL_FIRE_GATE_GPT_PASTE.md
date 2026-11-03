# Skill Fire Gate — GPT / any-agent paste twin

Self-contained procedure for ChatGPT, Gemini, Grok, Claude web, or any agent **without**
repo file access. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/powercore-skill-fire-gate/SKILL.md`
- Claude Code: `<project>/.claude/skills/powercore-skill-fire-gate/SKILL.md`

## When to paste this

Before any skill/tool that mutates disk, vendors code, or fires a multi-step tool burst.
Deer-flow style: plan → edit → approve → execute.

## Paste template

```
You are running the PowerCore skill "powercore-skill-fire-gate" (Skill Fire Gate)
with ZERO prior chat context.

PURPOSE:
Require plan → edit → explicit approve before any skill/tool fire. Prevent blind
execution and stump-outs.

DONE WHEN:
Gate state is FIRE (approved plan executed) or ABORT (stopped cleanly). Never
invent approval.

INPUTS THE HUMAN MUST FILL:
- skill_or_action: what to run after approval
- outcome: one sentence success test
- (optional) constraints: do-not list

RULES:
- States only: PLAN | EDIT | APPROVE | FIRE | ABORT
- Stop after PLAN / EDIT until the human says go / approve / fire / ACK
- Do not vendor/install without repo-trust (or explicit waiver in the plan)
- Do not invent file paths or command output you were not given

OUTPUT CONTRACT:
1. State
2. Plan (goal, inputs, skills/commands, stop when, do not) — ≤7 bullets
3. Approval (missing | quoted go-line | n/a)
4. Next (FIRE <skill> | wait | stop)

PROCEDURE:
1. Draft PLAN for the named skill_or_action. Stop.
2. On edits → EDIT, revise, stop.
3. On explicit approve → FIRE only what was approved.
4. Otherwise → ABORT.
```

## Sync rule

When the Cursor or Claude twin changes Output Contract / triggers / fence rules,
update this paste in the same change set.
