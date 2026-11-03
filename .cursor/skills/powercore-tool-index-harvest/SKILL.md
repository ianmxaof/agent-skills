---
name: powercore-tool-index-harvest
description: Harvest a free-tools or tools-directory page into a deduped capability
  inventory (cluster, inputs, outputs, processing mode, funnel target) and match
  rows against PowerCore Vault/Hub skills. Use for /tool-index, tool index harvest,
  or harvest this tools page.
purpose: Tool directory → spec-ready inventory + dedupe against existing skills
trigger_phrases:
- /powercore-tool-index-harvest
- /tool-index
- tool index harvest
- harvest this tools page
inputs:
- focused Hub tab or pasted tools-directory URL/body
outputs:
- inventory table + dedupe report + one primary build target
jev_hints:
  lane: chat
  cost: cheap
  needs_context: true
if_stumped: Ask once for the directory URL or paste; do not invent tool counts.
example_invocation: /tool-index on the current tab
---
# PowerCore Tool Index Harvest (v0.1)

Canonical Cursor skill. Triple Surface (locked): Cursor (this file) + Claude Code twin
under consuming repos' `.claude/skills/powercore-tool-index-harvest/` + GPT paste at
`agent-skills/docs/gpt-paste/POWERCORE_TOOL_INDEX_HARVEST_GPT_PASTE.md`.

Foundation harvested from wavespeed.ai/free-tools catalog pattern.

## Purpose

Take a category index / free-tools directory and emit a PowerCore inventory —
per-tool `{id, cluster, inputs, outputs, processing: local|server, funnel_target}` —
so new micro-tools can be specced, deduped against Vault/Hub skills, and scored
before any build.

## When to invoke

- Tools directory, free-tools hub, "all tools" listing page
- Operator wants specs, dedupe, or a build queue from a directory page

**Skip when:** single-tool page (`/capture` or `powercore-secret-forge`-class reverse);
repo trust (`powercore-repo-trust`); catalog **page builder** (`powercore-tool-catalog`).

## Execution Profile

- Freedom: medium
- Mode: Agent

## Harness attach

| Surface | Value |
|---------|-------|
| **MCP** | Firecrawl / Hub scrape optional |
| **Hooks** | endgates on stop |
| **Memory** | inventory markdown in chat or operator path |
| **Compose** | → `powercore-tool-catalog` (UI) · → `powercore-pipeline-fit` · ← `/capture` |

## Behavioral rules

- Inventory the **card shape**, not marketing copy.
- Drop "100% free" / "no watermark" into a `claims` column — never into the spec.
- `processing: local|server` — local only if the **card** says so; an index-wide banner is a claim, not proof.
- Dedupe before spec: match each row to an existing Vault/Hub skill id when possible.
- One primary build target per run; the rest go to a backlog table.
- Do not claim a tool was built or a page scraped unless Hub/tools returned it.

## Checklist (copy and tick)

```
- [ ] 1. Confirm source is a directory/index (not a single tool)
- [ ] 2. Extract cluster spine + per-card rows
- [ ] 3. Classify processing + funnel targets; park adjectives in claims
- [ ] 4. Dedupe against known PowerCore skill / Store ids
- [ ] 5. Pick one primary target; emit Output Contract
```

## Procedure

1. Parse clusters and card fields (badge, title, one-line pitch, open link).
2. Normalize rows to the inventory schema.
3. Dedupe / nearest-skill match.
4. Rank one primary + backlog.

## Output contract

```markdown
# Tool index harvest

## Source
url / date / claimed tool count

## Inventory
| id | cluster | inputs | outputs | processing | funnel | claims |
|----|---------|--------|---------|------------|--------|--------|

## Dedupe
row → existing skill/store id | none

## Primary target
one row + why

## Missing evidence
yaml evidence_gaps ledger (whitelist resolvers)
```

## Do not

- Invent tool counts beyond what the page states
- Treat a funnel link (→ paid model) as a free feature
- Build every row in one turn

## Triple Surface

| Surface | Path |
|---------|------|
| Cursor (canonical) | `agent-skills/.cursor/skills/powercore-tool-index-harvest/SKILL.md` |
| Claude Code twin | `<project>/.claude/skills/powercore-tool-index-harvest/SKILL.md` |
| GPT / any-agent paste | `agent-skills/docs/gpt-paste/POWERCORE_TOOL_INDEX_HARVEST_GPT_PASTE.md` |

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-tool-index-harvest --check
```

## Status

v0.1 — chat foundation. Later: Hub `/run` deterministic fetch→rows scanner.
