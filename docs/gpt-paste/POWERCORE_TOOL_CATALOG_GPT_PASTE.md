# Tool Catalog — GPT / any-agent paste twin

Self-contained procedure for chat agents without repo access. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/powercore-tool-catalog/SKILL.md`
- Claude Code: `<project>/.claude/skills/powercore-tool-catalog/SKILL.md`

## When to paste this

Turn a capability list into a local-first free-tools catalog page shape (categories, hero, cards).

## Paste template

```
You are running the PowerCore skill "powercore-tool-catalog" with ZERO prior chat context.

PURPOSE:
Capability list → category spine + hero (≤6) + per-tool cards with honest local-first claims.

DONE WHEN:
Catalog draft markdown is complete and does not invent tools/counts.

INPUTS THE HUMAN MUST FILL:
- capability_list: tools with any known local-first properties
- brand_notes_optional: fonts/colors if known

RULES:
- 8–12 categories max; hero ≤6.
- Card = one action verb + one noun; no marketing sentence as title.
- Local-first claim only when true for that tool.
- Do not invent tools, counts, or payment rails.
- Prefer clean Inter-class UI notes if suggesting chrome.

OUTPUT CONTRACT:
1. # Tool catalog draft
2. ## Category spine
3. ## Hero (≤6)
4. ## Card schema
5. ## Chrome notes
6. ## Next
7. Stop before writing production HTML unless asked.

PROCEDURE:
1. Confirm list + proven local-first flags.
2. Group categories with honest counts.
3. Curate hero.
4. Emit card schema + chrome notes.
```

## Sync rule

When Cursor/Claude Output Contract changes, update this paste in the same change set.
