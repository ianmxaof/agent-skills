---
name: tbcc-signal-scout
description: GSP v2.4 — draft edgy tech diary + optional network bump; fan out to paste hosts / Buffer. Invoke with /signal-scout, scout this, session-close diary, or paste fanout.
---

# TBCC Signal Scout Protocol (v1.0)

Changelog: v1.0 — diary + paste fanout + leak fence; operator blind-post preference.

## Purpose

- Catch **dev-diary** moments while coding TBCC (edgy tech revelation — interesting to the operator first).
- Optionally emit a second **network bump** (SFW CTA → hub / `loot_free`).
- Fan out diary bodies to configured paste hosts (Pastebin, Gist, Pixeldrain, …) and optionally queue X via Buffer.
- Expand discovery surfaces — does **not** replace Buffer content flywheel or island money bots.

## When to Invoke

- Trigger phrases: `/signal-scout`, `signal scout`, `scout this`, `dev diary`, `paste fanout`
- Situational triggers:
  - Session-close after substantive TBCC work when `TBCC_SIGNAL_SCOUT_ON_SESSION_CLOSE=1`
  - Milestone smell (same bar as milestone-ship) and operator wants diary, not only ship-log
  - Operator says they hate babysitting social and wants AI voice / blind post

## Execution Profile

- Mode: **Agent**; may use **Ask** first only if leak-fence ambiguity
- Model lane: **Lane A (Auto)** for draft + script fanout; **Lane B** only for voice/leak doctrine
- Parallelism: optional readonly `explore` (cheap) for recent commits
- Mode inheritance: explore stays readonly

## Delegation & Tooling

- Skills: `tbcc-ship-log` (tone sibling), `model-routing`
- Commands (from `tbcc/backend`):
  - `py -3.13 scripts/signal_scout_fanout.py --draft` — print diary + bump; no network
  - `py -3.13 scripts/signal_scout_fanout.py --execute` — post to all configured API pastes
  - `py -3.13 scripts/signal_scout_fanout.py --execute --buffer-queue` — also Buffer addToQueue PRIMARY X
  - `py -3.13 scripts/ship_log_sources.py` — optional context
- Registry: `tbcc/docs/SIGNAL_SCOUT_PASTE_FANOUT.md` + `app/data/signal_paste_destinations.json`
- Env: see `.env.example` `TBCC_SIGNAL_*`, `TBCC_PASTEBIN_*`, `TBCC_GITHUB_GIST_TOKEN`, `TBCC_PIXELDRAIN_API_KEY`

## Behavioral Rules

- Reason by: one concrete tech win or sharp observation; operator-as-primary reader
- Dual voice:
  1. **Diary** — **prompt-guy** voice: wickedly tight prompts, clever compression, disgustingly good results; operator-as-primary reader; ≤260 for X teaser; longer paste body OK
  2. **Bump** — SFW network CTA (hub / `loot_free`) when the moment is also promo-shaped; conversion viewership for AOF, not corporate build-in-public
- Prefer prompt craft / command kits as the hook; git subjects are evidence, not the lead sentence
- **Leak fence — never publish:**
  - `.env` / API keys / Telethon session paths
  - Internal chat ids, Celery queue names, proprietary scheduler IP
  - Undeployed money doctrine / exact VIP pricing experiments unless already public
  - Age-restricted media descriptions that violate clearnet paste ToS on that host
- Avoid: fake FOMO; NSFW dumps on Pastebin/Gist public; spamming identical text to every host every hour
- Prioritize: configured API hosts first; mark `no_public_api` destinations for operator paste-later
- Blind post: when operator said publish / `--execute` / `TBCC_SIGNAL_SCOUT_AUTO_PASTE=1`, do not re-ask

## Output Contract

- Required sections:
  1. **Opportunity** — one line why this moment is diary-worthy (or “none”)
  2. **Diary** — short (≤260) + optional long body
  3. **Bump** — SFW CTA variant or `skipped`
  4. **Fanout** — per-destination result (`posted` url | `skipped` reason | `failed` msg)
  5. **Leak fence** — pass / blocked items
- Done means: drafts exist; if execute requested, every configured API host attempted and reported
- Failure contract: halt listing what posted vs failed; no silent retry loops
- Artifacts: paste URLs; optional Buffer post id; optional note under `tbcc/docs/operator-scratch/` (gitignored)

## Exit Conditions

- Next: optional `/ship-log` if diary should also become a Buffer Idea; or continue coding
- Follows into: none required
- Composes: → `tbcc-ship-log` when diary should also hit weekly X narrative; → `tbcc-milestone-ship` when milestone bar met

## Agent procedure

1. Gather context (`ship_log_sources` or session diff summary).
2. Draft diary + optional bump; run leak fence.
3. If draft-only: print Output Contract; stop.
4. If execute: `signal_scout_fanout.py --execute` with text; report Fanout table.
5. Do not Start bots; do not touch Telethon sessions.
