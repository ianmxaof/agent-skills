---
name: powercore-token-audit
description: >-
  Runs the PowerCore token-waste audit (memory, tools, model, hooks, subagents,
  scheduled work, cache). Report only — no drive-by refactors. Use when the
  operator says token audit, /token-audit, SCREENSHOT THIS: THE TOKEN AUDIT,
  or asks to audit CLAUDE.md / MCP / cache for token waste.
---

# Token audit (report only)

Audit this setup for token waste. **Report only** — do not rewrite rules or disconnect MCP unless the operator asks after the report.

## Checklist

### 1. MEMORY

- Check every `CLAUDE.md` in scope: project, parents, user-level, and `@imports`.
- Report approximate token size of each file (chars÷4 is fine if no tokenizer).
- Flag any **single file >5k tokens** and any **cumulative >10k tokens**.

### 2. TOOLS

- List connected MCP servers and **tool count** per server.
- State whether **tool deferral** is ACTIVE or NOT.
- If a proxy/gateway sits in front of tools, say so prominently.

### 3. MODEL

- Report current model, effort/thinking level, and **where** that is set.
- Flag any mode that **auto-changes** the model mid-session.

### 4. HOOKS

- List any `PreToolUse` hooks that rewrite noisy commands to quieter output.
- If none: say so explicitly.

### 5. SUBAGENTS

- Review agent files in project and user agent folders.
- For each: **explicit model** vs **inherits** session model.

### 6. SCHEDULED WORK

- List cron / scheduled / background jobs and intervals.
- Flag any interval **longer than cache lifetime** (cache miss every run).

### 7. CACHE

- Open the newest session log available.
- Per assistant turn: sum `cache_read` + `cache_creation` + input + output; report as **percentages**.
- If logs lack those fields: say **blocked** for this section with what was missing.

## Output

One summary table, sorted by cost (highest first):

| FINDING | SEVERITY | EVIDENCE | COST |
|---------|----------|----------|------|
| … | critical / high / medium / low / info | path or metric | rough $ or token band |

Then at most **3** recommended fixes (menu only — do not apply unless asked).

## Scope defaults

- Cursor: workspace roots in this session + `~/.cursor` agent/skills if readable.
- Claude Code: repo `.claude/` + user Claude memory paths if readable.
- Do not invent sizes; measure or mark unknown.
