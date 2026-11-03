# Tool Index Harvest — GPT / any-agent paste twin

Self-contained procedure for chat agents without repo access. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/powercore-tool-index-harvest/SKILL.md`
- Claude Code: `<project>/.claude/skills/powercore-tool-index-harvest/SKILL.md`

## When to paste this

Harvest a free-tools / tools-directory page into a deduped capability inventory.

## Paste template

```
You are running the PowerCore skill "powercore-tool-index-harvest" with ZERO prior chat context.

PURPOSE:
Directory page → inventory rows {id, cluster, inputs, outputs, processing, funnel_target, claims} + dedupe + one primary build target.

DONE WHEN:
Inventory table + dedupe notes + one primary target are emitted from the pasted page body.

INPUTS THE HUMAN MUST FILL:
- page_body_or_url_excerpt: the tools directory content
- known_skills_optional: existing skill/product ids to dedupe against

RULES:
- Inventory card shape, not marketing adjectives (put those in claims).
- processing=local only if the card itself says so — index-wide banners are claims.
- Do not invent tool counts beyond the page.
- Funnel links to paid models are not free features.
- One primary target; rest = backlog.

OUTPUT CONTRACT:
1. # Tool index harvest
2. ## Source
3. ## Inventory (table)
4. ## Dedupe
5. ## Primary target
6. ## Missing evidence (YAML gaps if needed)
7. Stop before building tools.

PROCEDURE:
1. Confirm source is a directory/index.
2. Extract clusters + cards.
3. Normalize rows; classify processing + funnel.
4. Dedupe; pick one primary.
```

## Sync rule

When Cursor/Claude Output Contract changes, update this paste in the same change set.
