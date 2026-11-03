# Vendor pipeline — dump first, sort later

This is the inbox for skills, rules, and commands you find online.
Nothing here is live until you **promote** it.

## Shelves

| Path | Role |
|------|------|
| `vendor/incoming/` | Raw dumps (clone / zip / copy). Unsorted. |
| `vendor/sorted/<kind>/` | Classified units + `CARD.json` importance scores |
| `vendor/catalog.json` | Registry of every ingest (source, scores, status) |
| `.cursor/skills/` | Portable **library** (still not live in Cursor by itself) |
| `~/.cursor/skills/` | **Live** install (optional `--live`) |

Kinds: `cursor-skill`, `claude-skill`, `rule`, `command`, `warp-skill`, `plugin`, `other`.

## Commands (from repo root)

**Cursor slash command:** `/ingest-skills` then paste a URL (also installed under `~/.cursor/commands/`).

```powershell
cd C:\Powercore-repo-main\agent-skills

# Dump a GitHub repo or path
py -3.13 scripts\ingest.py https://github.com/spencerpauly/awesome-cursor-skills

# Or one-shot ingest + classify + list
py -3.13 scripts\pipeline.py https://github.com/spencerpauly/awesome-cursor-skills

# Re-score everything in incoming
py -3.13 scripts\sort.py

# Boost something you care about, then re-sort that batch
py -3.13 scripts\sort.py --id 2026-09-09_awesome-cursor-skills --boost prompt-engineering=15

# See ranked list
py -3.13 scripts\promote.py --list

# Copy promote-candidates into the portable library only
py -3.13 scripts\promote.py --tier promote-candidate

# Also install into ~/.cursor/skills (agents can see it)
py -3.13 scripts\promote.py --name prompt-engineering --live
```

## Importance tiers

| Tier | Default score | Meaning |
|------|---------------|---------|
| `promote-candidate` | ≥ 60 | Strong structure + description; consider promoting |
| `review` | 40–59 | Maybe useful — operator glance |
| `park` | < 40 | Keep in vendor; do not auto-install |

Scores rise when you `--boost`, when structure is good (`SKILL.md` + description), when the name is not already in the library, and when `use_count` grows after promotes.

**Auto-sort ≠ auto-install.** Promote is always a deliberate step (or `--promote-candidates` on the pipeline).

## Portability

This repo is self-contained:

1. Clone or copy `agent-skills` next to any project
2. Run scripts from its root (paths are relative)
3. Copy `.cursor/skills/<name>/` into that project's `.cursor/skills/` **or** use `--live` for your user folder

No dependency on `telegram_bot2` or TBCC paths.

## Giving an agent URLs

Paste a URL and say: “ingest this into agent-skills.” The agent should run:

```powershell
py -3.13 scripts\pipeline.py <url>
```

Then show you the promote list before anything goes live.
