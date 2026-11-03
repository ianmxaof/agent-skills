---
name: powercore-cleanroom-brief
description: Evidence-gated clone brief for any web surface. Runs deterministic
  captures (layout at 3 widths, palette, fonts, DOM features), wraps them in an
  evidence record with confidence/coverage/limitations, then emits a build brief
  and a pass/fail delta against the result. Use for /cleanroom, /cleanroom-brief,
  "clone this correctly", or evidence-gated rebuild.
purpose: Same job as a clean-room rebuild engine — study, then hold a build agent to a check
trigger_phrases:
- /powercore-cleanroom-brief
- /cleanroom
- /cleanroom-brief
- clone this correctly
- evidence-gated rebuild
inputs:
- current tab URL or pasted surface URL
outputs:
- evidence record (summary first, paged) + build brief + check deltas
jev_hints:
  lane: operator
  cost: medium
  needs_context: true
if_stumped: Ask once for the target URL and clean vs deep mode; do not invent captures.
example_invocation: /cleanroom-brief on the current tab
---
# PowerCore Cleanroom Brief (v0.1)

Canonical Cursor skill. Triple Surface (locked): Cursor (this file) + Claude Code twin
under consuming repos' `.claude/skills/powercore-cleanroom-brief/` + GPT paste at
`agent-skills/docs/gpt-paste/POWERCORE_CLEANROOM_BRIEF_GPT_PASTE.md`.

Upstream of rebuild work. Composes existing capture skills — does **not** reimplement
scraping. Foundation harvested from storytold/craft-anything (Study → Build → Check).

## Purpose

Turn "clone this surface" into a deterministic evidence pass (recorded with confidence +
limits) that a build agent must clear before the result is accepted — instead of one-shot
generate-and-pray.

## When to invoke

- Operator wants a surface rebuilt and the result **checked**, not just eyeballed
- `/cleanroom`, `/cleanroom-brief`, "clone this correctly"

**Skip when:** aesthetics-only harvest (`powercore-website-clone`); feature inventory only
(`powercore-website-feature-scan`); Desk parking (`/capture`).

## Modes

| Mode | Flag | Allowed evidence |
|------|------|------------------|
| `clean` (default) | — | Screenshots at 390/768/1440, visible text, measured layout/colour/font/spacing, opened menus. **No** source/JS reads. |
| `deep` | `--deep` | Adds page JS and source reads |

## Execution Profile

- Freedom: medium (envelope + delta are locked; capture composition may vary)
- Mode: Agent

## Harness attach

| Surface | Value |
|---------|-------|
| **MCP** | none (Hub tab / Firecrawl optional later) |
| **Hooks** | endgates on stop |
| **Memory** | evidence records under operator-chosen path or chat card |
| **Compose** | ← `powercore-website-clone`, `powercore-website-feature-scan`, `powercore-site-map-tree` → build agent / `/directive` |

## Behavioral rules

- Inspection is deterministic; the coding agent is only the builder.
- Never invent confidence when a capture was refused by mode.
- Never score similarity without **both** baseline and post-build captures.
- Never claim pass without a per-item delta.
- Prefer summary-first paging for large evidence records.

## Checklist (copy and tick)

Order matters.

```
- [ ] 1. Confirm mode (clean | deep) + target URL
- [ ] 2. Capture baseline via compose skills → evidence record
- [ ] 3. Emit build brief (stack, structure, tokens, must-match list)
- [ ] 4. After build: re-capture → delta against the record
- [ ] 5. Emit Output Contract; stop for operator ACK on pass/fail
```

## Procedure

1. **Capture (per mode)** → evidence items: `id, kind, value, confidence, coverage, limits`.
2. **Build brief** — what the agent must match; cite evidence ids.
3. **Check** — re-capture at the same widths; list mismatches; pass/fail per item.
4. **Page big records** — summary first, then detail on request.

## Output contract

```markdown
# Cleanroom brief

## Source
url / mode / date

## Evidence summary
id · kind · confidence · coverage · limits (paged if large)

## Build brief
must-match list + stack/structure notes

## Check delta (after build)
item · baseline · result · pass|fail

## Next
1. …
```

## Do not

- Score similarity without both captures
- Invent confidence when mode refused a capture
- Claim pass without the delta
- Vendor or run craft-anything Rust engine unless operator explicitly adopts it

## Triple Surface

| Surface | Path |
|---------|------|
| Cursor (canonical) | `agent-skills/.cursor/skills/powercore-cleanroom-brief/SKILL.md` |
| Claude Code twin | `<project>/.claude/skills/powercore-cleanroom-brief/SKILL.md` |
| GPT / any-agent paste | `agent-skills/docs/gpt-paste/POWERCORE_CLEANROOM_BRIEF_GPT_PASTE.md` |

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-cleanroom-brief --check
```

## Status

v0.1 — chat foundation. Later: Hub `/run cleanroom-brief` once envelope + delta are
deterministic scripts.
