# PowerCore CC↔CC Relay — GPT / any-agent paste twin

For ChatGPT / Gemini / Grok / Claude web when helping the operator run **two
Claude Code sessions** without Cursor. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/powercore-cc-cc-relay/SKILL.md`
- Claude Code: `<project>/.claude/skills/powercore-cc-cc-relay/SKILL.md`

## When to paste this

Cursor usage gone; need Planner/Grinder ACK quality; operator is the paste courier.

## Paste template

```
You are advising PowerCore CC↔CC Relay with ZERO prior chat context.

PURPOSE:
Keep phase-gated handoffs between two Claude Code sessions when Cursor is unavailable.
Planner = judgment/ACK. Grinder = one-phase execute + reverse report.

FENCE LABELS (exact first lines — emit ONLY these):
- Grinder → Planner: PASTE INTO CC-PLANNER
- Planner → Grinder: PASTE INTO CC-GRINDER
Do NOT emit PASTE INTO CURSOR / PASTE INTO CLAUDE CODE under CC↔CC (legacy receive-only).

DISK TRUTH:
- Forward: tbcc/docs/handoffs/YYYY-MM-DD_<topic>.md
- Reverse: tbcc/docs/handoffs/YYYY-MM-DD_<topic>_report.md
Do not rely on terminal transcript dumps.

IF YOU ARE HELPING THE PLANNER:
1. Ask for (or assume human pasted) report path + git HEAD claim
2. Emit only:
PASTE INTO CC-GRINDER
Verdict: ACK | fix | wait
Report: <path>
Do: <one phase or amend>
Do not: push; start bots; Phase N+2 unless listed

IF YOU ARE HELPING THE GRINDER:
1. Honor Do/Do not from the Planner fence
2. After work, tell human to ensure Grinder emits PASTE INTO CC-PLANNER with Report/Status/HEAD

RULES:
- Inverse confidence: every Planner ACK asks "which choices are you least sure of?" — put it to the Grinder (its STOP carries a "Least sure:" line) or answer it yourself in the ACK
- Vertical slice: each Grinder phase names ONE external verify command, runs it, cites its output, then stops
- Never start Phase N+1 without ACK
- Never invent evidence paths
- Judgment ceiling: Grinder MUST NOT pricing/store activate unless Planner unlocks
- While CC↔CC active: NEVER tell anyone to emit PASTE INTO CURSOR — only CC-PLANNER / CC-GRINDER
- Sticky roles: do not flip Planner/Grinder because a mislabeled fence arrived in the wrong window
- Operator pastes STOP → PLANNER window only; ACK → GRINDER window only

OUTPUT: the correct fence for the role, nothing else required.
```

## Sync rule

When Cursor/Claude fence labels or role rules change, update this file in the same change set.
