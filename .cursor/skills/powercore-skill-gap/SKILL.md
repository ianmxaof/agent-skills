---
name: powercore-skill-gap
description: >-
  PowerCore skill-gap gate — MUST run after crystallize on substantive
  devops/agent workflow turns. Detects repeatable how-we-work missing from the
  toolbox and suggests a powercore-* skill (never auto-write). Use when tip
  powercore-skill-gap-gate fires, when naming new skills, creating skills,
  skill surfaces, Claude twin, GPT paste twin, or operator says skill gap /
  auto skill / missing skill / from now on checklist. Prefer powercore-* names;
  do not mint new tbcc-* skills. Includes Triple Surface scaffold, rank_skills,
  binary evals, improve_once.
---

# PowerCore skill-gap (suggest-only)

Sibling of **auto-crystallize**: crystallize captures *facts*; this gate captures
*missing how-we-work* as a proposed skill.

**Naming (locked going forward):** new skills use `powercore-<slug>`. Existing
`tbcc-*` skills stay until deliberately migrated; the catalog treats
`tbcc-foo` ↔ `powercore-foo` as aliases for near-miss matching.

**Create-skill (locked):** every new PowerCore skill ships **Triple Surface** —
Cursor canonical + Claude Code twin + GPT/any-agent paste. Do not stop at
`.cursor/skills/` alone. Cursor built-in `create-skill` only covers Cursor;
this skill owns the multi-surface finish.

## Always-on tip

`.cursor/rules/powercore-endgates.mdc` (single tip). Legacy per-gate tips are `alwaysApply: false`.

Hooks: `.cursor/hooks.json` → `endgates_hook.py` (sessionStart context, stop runs endgates + metrics; followup off unless `POWERCORE_ENDGATES_HOOK_FOLLOWUP=1`).

## Quick reference

| Tier | Score (default) | Agent action |
|---|---:|---|
| skip | <40 | Silent |
| suggest | ≥40 (+ confidence + corpus gap) | One line to operator; **do not** write SKILL.md |

**Never auto-create.** Operator must ACK before scaffolding.

### Suggest line

```text
Skill gap suggested (52) → powercore-vault-models-refresh — nearest: operator-cli, powercore-skill-gap
```

### After operator ACK

Copy and tick:

```
- [ ] 1. Triple Surface scaffold (Cursor + Claude + GPT paste) via CLI below — or create-skill then fill twins
- [ ] 2. Fill Cursor SKILL.md procedure (canonical body)
- [ ] 3. Thin Claude twin(s): drop Cursor-only lane wording; same Output Contract
- [ ] 4. GPT paste: self-contained chat-only procedure (no repo paths required to *run*)
- [ ] 5. `evals/evals.json` with **binary** assertions only
- [ ] 6. `py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-<slug> --check` → ok
- [ ] 7. Optional: improve_once / overnight_loop / skill-creator description loop
- [ ] 8. Pass **Anthropic shape checks** + Triple Surface row before calling done
```

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-<slug> `
  --title "Human Title" --description "Third-person when-to-use…"
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-<slug> --check
```

Backfill twins for an existing Cursor-only skill: same command with `--skip-cursor` (writes Claude + GPT only).

## Triple Surface (locked)

| Surface | Where | Role |
|---|---|---|
| **Cursor** | `agent-skills/.cursor/skills/<name>/SKILL.md` | Canonical — full procedure, evals, versions |
| **Claude Code** | `<project>/.claude/skills/<name>/SKILL.md` | Thin mirror; third-person `description`; no Desktop-Auto/Cloud lane prose |
| **GPT / any agent** | `agent-skills/docs/gpt-paste/<NAME>_GPT_PASTE.md` | Condensed paste for ChatGPT / Gemini / Grok / Claude web — zero filesystem assumed |

Defaults for Claude roots (scaffold CLI): `telegram_bot2`, `powercore-ops`, `agent-skills`.
Need ≥1 Claude twin for `--check` to pass (not necessarily all three roots).

**Sync rule:** version-bump Cursor + Claude + GPT paste in the same change set when Output Contract / triggers / fence change.

**Examples already in the wild:** `directive-generator` (Cursor + `.claude` twin + `tbcc/docs/DIRECTIVE_GENERATOR_GPT_PASTE.md`); pocket condensed blocks in `tbcc/docs/OPERATOR_GPT_POCKET_KIT.md`. New skills use `docs/gpt-paste/` under agent-skills unless the skill is TBCC-doc-native.

**Not covered by:** Cursor built-in `~/.cursor/skills-cursor/create-skill` (Cursor-only) or Anthropic `skill-creator` alone — always finish with Triple Surface.

## Anthropic shape checks

When scaffolding or tightening a skill (keep this thin — do not paste the whole Anthropic video into always-on memory):

| Check | Rule |
|---|---|
| **Triple Surface** | Cursor + ≥1 Claude twin + GPT paste exist; `--check` ok. |
| **Freedom** | Under Execution Profile, tag `Freedom: high \| medium \| low` (mix allowed per step). High = goal-only creative; medium = template; low = exact script / fence / money-touch. |
| **Checklist** | If step **order** matters, use a tickable `- [ ]` list the agent must copy and mark. Skip checklists when order does not matter. |
| **Self-correct** | Emit/review skills: **Draft → check Output Contract → revise until pass**. If failure is uncovered by guidelines, suggest one new rule for operator ACK (never auto-write). |
| **Harness attach** | Each skill names: **MCP** (or `none`), **Hooks** before “done” (endgates / silent-fail / ship-gate / `none`), **Memory** (disk paths vs chat-ok), **Compose** `→` / `←` skills. |
| **Refs** | Link refs only one hop from `SKILL.md`. Any ref file >100 lines needs a Contents list at the top. |
| **Deps** | Scripted / portable skills must name the exact install + run line (do not assume preinstalled tools). |

### Pilot scoreboard (Anthropic + harness)

Manual tally after ~10 live uses of the three pilots (`cc-report`, `tbcc-silent-fail`, `directive-generator`):

- Eval packs green after expand (`run_evals` all PASS)
- Live contract ≥9/10 compliant fences / stops / cold emits
- ≤1 paste/exec re-ask per 5 hops
- Overnight keep must not strip Freedom / Self-correct / Harness attach

## Pending proposals → ACK → scaffold

Endgates rows now log `proposed_slug` + `score` on every suggest. Review the backlog (read-only):

```powershell
py -3.13 -m tools.skill_gap.pending            # structured rows only
py -3.13 -m tools.skill_gap.pending --legacy   # also recover pre-logging rows from the free-text `lines`
```

Only after operator ACK, one line writes all three surfaces (never auto-write):

```powershell
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-<slug> --title "…" --description "…"
```

Compose edge (manual, not wrapped): to tune an *existing* skill rather than mint one, use
`tools.skill_gap.improve_once` / `overnight_loop`. No `powercore-skill-improve` skill yet —
revisit once goldens ≥ 12. Slugs `untitled`, bare `gap`/`vault`/`report`/`fail` are rejected.

## CLI

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.skill_gap.endgates --prompt "..." --response "..." --auto --plain
py -3.13 -m tools.skill_gap.run_gate --prompt "..." --response "..." --json
py -3.13 -m tools.skill_gap.rank_skills --prompt "..." --response "..." --json
py -3.13 -m tools.skill_gap.run_rank_evals --json
py -3.13 -m tools.skill_gap.utilization --report --last 100 --plain   # rank ≠ open; tips = exposure/cost
py -3.13 -m tools.skill_gap.run_evals --skill cc-report
py -3.13 -m tools.skill_gap.improve_once --skill cc-report
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-<slug> --title "…" --description "…"
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-<slug> --check
```

`endgates` = crystallize → skill-gap → rank_skills (one call). `rank_skills` alone when only picking a skill. `run_rank_evals` = golden hit-rate metric.

Env knobs:

| Var | Default | Meaning |
|---|---|---|
| `POWERCORE_SKILL_GAP_ENABLED` | `1` | Set `0` to disable |
| `POWERCORE_SKILL_GAP_SUGGEST_AT` | `40` | Suggest floor |
| `POWERCORE_SKILL_GAP_MIN_CONFIDENCE` | `0.4` | Min confidence |
| `POWERCORE_SKILL_GAP_ROOT` | agent-skills repo | Catalog root |
| `POWERCORE_SKILL_GAP_EXTRA_ROOTS` | _(empty)_ | `os.pathsep`-joined extra skill dirs |

## Score dimensions (0–100)

| Dimension | Max | Signals |
|---|---:|---|
| repeatability | 25 | next time / checklist / multi-step / corrections |
| transferability | 20 | portable / toolbox / powercore / skill |
| corpus_gap | 25 | weak overlap with existing SKILL.md descriptions |
| durability | 15 | must/always/never / SKILL.md / evals |
| operator_cost | 15 | repeated pain, silent fail, manual eyeballing |

Strong near-miss (≥0.70 overlap) → **skip** (extend existing skill instead).

## Binary evals (Layer 2)

Seeded:

- `.cursor/skills/cc-report/evals/evals.json`
- `.cursor/skills/tbcc-silent-fail/evals/evals.json`
- `.cursor/skills/directive-generator/evals/evals.json`

Assertions must be true/false (`contains`, `not_contains`, `regex`, `max_words`, `min_words`).
No subjective “is the tone good?” checks.

## Relation to crystallize

| Gate | Payload | Auto-write? |
|---|---|---|
| auto-crystallize | Durable facts → vault inbox | Yes (when NTK says so) |
| powercore-skill-gap | Missing procedure → proposed skill name | **No** — suggest only |
