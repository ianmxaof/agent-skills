# token audit — GPT / any-agent paste twin

Self-contained procedure for ChatGPT, Gemini, Grok, Claude web, or any agent **without**
repo file access. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/powercore-token-audit/SKILL.md`
- Claude Code: `<project>/.claude/skills/powercore-token-audit/SKILL.md`

## When to paste this

Runs the PowerCore token-waste audit (memory, tools, model, hooks, subagents, scheduled work, cache). Report only — no drive-by refactors. Use when the operator says token audit, /token-audit, SCREENSHOT THIS: THE TOKEN AUDIT, or asks to audit CLAUDE.md / MCP / cache for token waste.

## Paste template

```
You are running the PowerCore skill "powercore-token-audit" (token audit) with ZERO prior chat context.

PURPOSE:
Runs the PowerCore token-waste audit (memory, tools, model, hooks, subagents, scheduled work, cache). Report only — no drive-by refactors. Use when the operator says token audit, /token-audit, SCREENSHOT THIS: THE TOKEN AUDIT, or asks to audit CLAUDE.md / MCP / cache for token waste.

DONE WHEN:
<one testable outcome>

INPUTS THE HUMAN MUST FILL:
- <field>: <what>
- <field>: <what>

RULES:
- Do not invent file paths or command output you were not given.
- Judgment ceiling: MUST NOT on pricing/doctrine unless the human explicitly unlocks it.
- Prefer short, checkable steps over essays.

OUTPUT CONTRACT:
1. <required section>
2. <required section>
3. Stop and ask the human before any irreversible step.

PROCEDURE:
1. …
2. …
3. …
```

## Sync rule

When the Cursor or Claude twin changes Output Contract / triggers / fence rules,
update this paste in the same change set.
