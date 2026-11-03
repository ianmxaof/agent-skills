# PowerCore skill-gap — GPT / any-agent paste twin

Self-contained procedure for ChatGPT, Gemini, Grok, Claude web, or any agent
**without** repo file access. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/powercore-skill-gap/SKILL.md`
- Claude Code: `<project>/.claude/skills/powercore-skill-gap/SKILL.md`

## When to paste this

Missing how-we-work / "from now on checklist" / create a PowerCore skill /
Cursor + Claude twin + GPT paste surfaces.

## Paste template

```
You are running PowerCore skill-gap with ZERO prior chat context.

PURPOSE:
Detect a missing transferable procedure and package it as a powercore-* skill
proposal. Never auto-write skills without human ACK. When creating after ACK,
ship Triple Surface: Cursor canonical + Claude Code twin + GPT paste.

DONE WHEN:
- You either SKIP (near-miss / low score) OR emit one Suggest line with a
  powercore-<slug> name + nearest existing skills
- If the human ACK'd create: list the three surface paths to write and a
  tickable scaffold checklist

RULES:
- Prefer powercore-* names. Do not mint new tbcc-* skills.
- Suggest only — do not invent full SKILL.md bodies unless the human said ACK create.
- Judgment ceiling: MUST NOT invent pricing/doctrine; MAY propose procedure checklists.
- Do not invent file evidence; mark unknown.

OUTPUT CONTRACT:
1. Tier: skip | suggest
2. If suggest: one line — Skill gap suggested (score) → powercore-<slug> — nearest: …
3. Triple Surface reminder (always when suggest or create):
   - Cursor: agent-skills/.cursor/skills/<name>/SKILL.md
   - Claude: <project>/.claude/skills/<name>/SKILL.md
   - GPT paste: agent-skills/docs/gpt-paste/<NAME>_GPT_PASTE.md
4. Stop for human ACK before writing files.

IF HUMAN SAYS ACK CREATE:
Emit tickable checklist:
- [ ] scaffold_surfaces CLI (or manual stubs for all three surfaces)
- [ ] fill Cursor procedure
- [ ] thin Claude twin (same Output Contract; drop Cursor-only lanes)
- [ ] GPT paste (chat-only; no filesystem assumed to run)
- [ ] binary evals.json
- [ ] --check ok

PROCEDURE:
1. Score repeatability / transferability / corpus gap from the pasted issue.
2. If strong near-miss to an existing skill → skip + name the skill to extend.
3. Else propose powercore-<slug> and stop for ACK.
```

## Sync rule

When Cursor/Claude Output Contract or Triple Surface paths change, update this file in the same change set.
