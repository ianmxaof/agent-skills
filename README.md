# agent-skills

Modular library of reusable AI agent skills for Cursor, Claude Code, and GPT paste workflows.

Skills are **executable capabilities** (roles + procedures + output contracts), not one-off prompt snippets. Copy what you need into a project, promote to live agent folders, or keep this repo as the shared toolbox next to PowerCore / TBCC work.

## What lives here

| Surface | Path | Role |
|---------|------|------|
| **Cursor skills (canonical)** | `.cursor/skills/<name>/SKILL.md` | Portable library — agents do **not** load this path just because the repo is open |
| **Claude twins** | `.claude/skills/` (+ copies under sibling repos) | Claude Code discovery |
| **GPT pastes** | `docs/gpt-paste/` | Browser / ChatGPT cold-start twins |
| **Vendor inbox** | `vendor/` | Dump → sort → promote pipeline |
| **Tooling** | `tools/`, `scripts/` | Skill-gap, endgates, promote, mutator, evals |
| **Legacy notes** | `skills/` | Older category markdown; prefer `.cursor/skills/` for anything new |

**Triple Surface (locked for new PowerCore skills):** Cursor `SKILL.md` + Claude twin + GPT paste, kept in sync in one change set. Prefer `powercore-*` names for new cross-product skills; existing `tbcc-*` skills stay until deliberately migrated.

## Quick start

```powershell
cd path\to\agent-skills

# See ranked vendor promote candidates
py -3.13 scripts\promote.py --list

# Install one skill into the portable library (and optionally live Cursor)
py -3.13 scripts\promote.py --name <skill-name>          # library only
py -3.13 scripts\promote.py --name <skill-name> --live   # also ~/.cursor/skills

# End-of-turn gates (crystallize → skill-gap → rank)
py -3.13 -m tools.skill_gap.endgates --prompt "..." --response "..." --auto --plain
```

Live loading still comes from:

1. `~/.cursor/skills/` (machine-wide Cursor)
2. A project's `.cursor/skills/` or `.claude/skills/`

This repo is the **source archive**. Promote or copy into those live folders when a skill should run.

## Vendor pipeline (dump → sort → promote)

Found a skill / ruleset / command pack? Dump it here. Nothing goes live until you promote.

```powershell
py -3.13 scripts\pipeline.py https://github.com/example/awesome-cursor-skills
py -3.13 scripts\promote.py --list
py -3.13 scripts\promote.py --name prompt-engineering --live
```

Or in chat: `/ingest-skills` + paste the URL. Details: [`vendor/README.md`](vendor/README.md).

| Path | Role |
|------|------|
| `vendor/incoming/` | Raw dumps |
| `vendor/sorted/` | Classified units + importance cards |
| `.cursor/skills/` | Portable library |
| `~/.cursor/skills/` | Live Cursor install (optional `--live`) |

## Skill-gap and endgates

Detect repeatable how-we-work that is **not** already in the toolbox. Suggest-only — never auto-writes `SKILL.md`.

```powershell
py -3.13 -m tools.skill_gap.run_gate --prompt "..." --response "..." --json
py -3.13 -m tools.skill_gap.run_evals --skill cc-report
py -3.13 -m pytest tests/test_skill_gap.py -q
```

Skills: `powercore-skill-gap`, `powercore-ship-gate`. Spine registry: `docs/skill-spine-registry.json`.

## Skill layout

Each Cursor skill is a folder:

```
.cursor/skills/<skill-name>/
├── SKILL.md          # frontmatter + procedure + output contract
├── scripts/          # optional helpers
├── evals/            # optional fixtures / versions
└── tests/            # optional pytest
```

Namespaces in active use:

- **`powercore-*`** — cross-product PowerCore how-we-work (preferred for new skills)
- **`tbcc-*`** — TBCC / revenue-island ops (kept; do not mint new ones for unrelated work)
- **unprefixed** — shared utilities (`cc-report`, `directive-generator`, …)

## Creating a skill

1. Scaffold under `.cursor/skills/<name>/SKILL.md` (use an existing skill as the template).
2. For PowerCore skills: run Triple Surface scaffold so Claude + GPT paste stay aligned.
3. Add evals/tests when the skill has scripts or a strict output contract.
4. Promote with `scripts/promote.py` when it should load live.

See `meta/promotion-criteria.md` for draft → validated → hardened lifecycle.

## Project structure

```
agent-skills/
├── README.md
├── .cursor/skills/       # Cursor SKILL.md library (canonical)
├── .claude/skills/       # Claude twins in this repo
├── docs/                 # handoffs, gpt-paste, spine registry, design
├── scripts/              # ingest / sort / promote / pipeline
├── tools/                # skill_gap, mutator, …
├── vendor/               # dump zone + catalog
├── surfaces/             # shared surface helpers
├── tests/                # repo-level pytest
├── skills/               # legacy category notes
├── protocols/            # handoff contracts
├── meta/                 # lifecycle / observability policies
├── skill-chains/         # optional multi-skill sequences
└── profiles/             # project-type profiles
```

## Portability

Clone or copy this repo next to any project. Scripts resolve paths from the repo root — no hard dependency on a fixed drive letter or TBCC. To carry skills to another machine: copy the repo, then `promote.py --live` (or copy `.cursor/skills/<name>` into that project's skill folders).

## Who should use this

Anyone building a **shared, versioned skill toolbox** for coding agents — especially multi-surface (Cursor + Claude Code + paste) workflows — instead of scattering one-off prompts per chat.

## License

No license file is published in this repository yet.

## Support

Open an issue: https://github.com/ianmxaof/agent-skills/issues
