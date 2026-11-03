---
name: powercore-tool-catalog
description: Builds a category-indexed, local-first free-tools catalog page from a
  capability list — hero block, category spine, per-tool cards, all local-only
  claims enforced. Use for /tool-catalog, /catalog, tool hubs, demo indexes, or
  Store landing pages.
purpose: Capability list → browsable local-first catalog under PowerCore chrome
trigger_phrases:
- /powercore-tool-catalog
- /tool-catalog
- /catalog
- free tools catalog
inputs:
- capability list (from operator or powercore-tool-index-harvest)
outputs:
- catalog IA + card schema markdown (and optional HTML/CSS stub later)
jev_hints:
  lane: chat
  cost: cheap
  needs_context: true
if_stumped: Ask once for the capability list; do not invent tools or counts.
example_invocation: /tool-catalog from this inventory
---
# PowerCore Tool Catalog (v0.1)

Canonical Cursor skill. Triple Surface (locked): Cursor (this file) + Claude Code twin
under consuming repos' `.claude/skills/powercore-tool-catalog/` + GPT paste at
`agent-skills/docs/gpt-paste/POWERCORE_TOOL_CATALOG_GPT_PASTE.md`.

Sibling of **`powercore-tool-index-harvest`** (directory → inventory). This skill owns
**rendering the catalog page shape**, not scraping a competitor index.

## Purpose

Turn a capability list into a local-first free-tools index (category spine + hero
block + per-tool cards) matching PowerCore chrome.

## When to invoke

- Operator has a capability list and wants a browsable index page
- Store / Hub demo index, tool hub landing

**Skip when:** harvesting a live directory (`powercore-tool-index-harvest`); single
tool body implementation.

## Execution Profile

- Freedom: medium
- Mode: Agent

## Harness attach

| Surface | Value |
|---------|-------|
| **MCP** | none |
| **Hooks** | endgates on stop |
| **Memory** | markdown draft; optional path under powercore-store / Hub |
| **Compose** | ← `powercore-tool-index-harvest` · ← `powercore-website-clone` (tokens) · Chrome fonts |

## Behavioral rules

- Every card asserts a **real** local-first property (no upload / no signup) only when true for that tool.
- Aisle counts sit in the section header, never stuffed into the card.
- Card = one action verb + one noun; no marketing sentence as the title.
- Do not invent counts, tools, or claims not in the source list.
- Prefer Inter-class UI stack (`powercore-chrome` tokens) — no Segoe/IBM Plex-first defaults.

## Checklist (copy and tick)

```
- [ ] 1. Confirm capability list + which claims are proven local-first
- [ ] 2. Group into 8–12 categories with honest counts
- [ ] 3. Curate hero ≤6
- [ ] 4. Emit card schema + chrome notes
- [ ] 5. Stop before writing production HTML unless operator says execute
```

## Output contract

```markdown
# Tool catalog draft

## Category spine
group · count

## Hero (≤6)
title · one-line · action

## Card schema
badge · title · one-line · action · local-first property

## Chrome notes
tokens / fonts / spacing (or "need /run website-clone")

## Next
1. …
```

## Do not

- Invent counts, tools, or claims not in the source list
- Add payment rails, SKU grids, or alternate brand schemes
- Claim a tool rendered unless a Hub/build result says so

## Triple Surface

| Surface | Path |
|---------|------|
| Cursor (canonical) | `agent-skills/.cursor/skills/powercore-tool-catalog/SKILL.md` |
| Claude Code twin | `<project>/.claude/skills/powercore-tool-catalog/SKILL.md` |
| GPT / any-agent paste | `agent-skills/docs/gpt-paste/POWERCORE_TOOL_CATALOG_GPT_PASTE.md` |

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-tool-catalog --check
```

## Status

v0.1 — chat artifact. Later: Hub `/run tool-catalog` if a deterministic generator lands.
