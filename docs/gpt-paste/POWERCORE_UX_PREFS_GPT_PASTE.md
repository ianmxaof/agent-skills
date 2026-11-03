# ux prefs — GPT / any-agent paste twin

Self-contained procedure for ChatGPT, Gemini, Grok, Claude web, or any agent **without**
repo file access. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/powercore-ux-prefs/SKILL.md`
- Claude Code: `<project>/.claude/skills/powercore-ux-prefs/SKILL.md`

## When to paste this

Apply and grow PowerCore UX interaction preferences across Vault, Hub, Notes, Store, and future UIs. Use when building or fixing UI/UX (sidebars, scroll, wheel, focus, panels, composers, history rails), when the operator corrects a feel (“wheel should scroll the list”, “Enter sends”), when seeding from Cursor agent-transcript archives (/ux-prefs seed, mine chatlogs), or when invoked as /ux-prefs, /powercore-ux, UX prefs, chrome prefs, design preferences. Loads design/powercore-ux.preferences.md; appends on operator corrections; mines ~/.cursor/projects/*/agent-transcripts via tools.ux_prefs.

## Paste template

```
You are running the PowerCore skill "powercore-ux-prefs" (ux prefs) with ZERO prior chat context.

PURPOSE:
Apply and grow PowerCore UX interaction preferences across Vault, Hub, Notes, Store, and future UIs. Use when building or fixing UI/UX (sidebars, scroll, wheel, focus, panels, composers, history rails), when the operator corrects a feel (“wheel should scroll the list”, “Enter sends”), when seeding from Cursor agent-transcript archives (/ux-prefs seed, mine chatlogs), or when invoked as /ux-prefs, /powercore-ux, UX prefs, chrome prefs, design preferences. Loads design/powercore-ux.preferences.md; appends on operator corrections; mines ~/.cursor/projects/*/agent-transcripts via tools.ux_prefs.

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
