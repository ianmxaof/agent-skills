---
name: powercore-tool-index-harvest
description: Harvest a free-tools or tools-directory page into a deduped capability
  inventory (cluster, inputs, outputs, processing mode, funnel target) and match
  rows against PowerCore Vault/Hub skills. Use for /tool-index, tool index harvest,
  or harvest this tools page.
---
# Tool Index Harvest — Claude Code twin

Thin mirror of `agent-skills/.cursor/skills/powercore-tool-index-harvest/SKILL.md`.
GPT paste: `agent-skills/docs/gpt-paste/POWERCORE_TOOL_INDEX_HARVEST_GPT_PASTE.md`.

## When

Directory / free-tools index pages — not single-tool reverse or catalog page build.

## Rules

- Card shape → inventory; marketing adjectives → `claims` column only
- `processing: local|server` only if the card says so
- Dedupe before spec; one primary target per run

## Output contract

`# Tool index harvest` → Source · Inventory table · Dedupe · Primary target · Missing evidence YAML

## Do not

- Invent counts; treat funnel links as free features; build every row in one turn
