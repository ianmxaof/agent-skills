---
name: tbcc-milestone-ship
description: GSP v2.0 — on significant TBCC milestones commit, push to GitHub, draft ship-log tweets, publish via Buffer. Invoke with /milestone-ship, TBCC milestone ship, or ship milestone to GitHub.
---

# TBCC Milestone Ship Protocol (v1.0)

Changelog: Initial protocol — git push gate, ship-log handoff, Buffer publish pipeline.

## Purpose

- Close the loop when weeks of local TBCC work hits a **significant milestone**: version control, public narrative, social post.
- Compensate for infrequent manual git habits by making **routine work → commit → push** automatic when `TBCC_AUTO_PUSH=1`, and reserving **milestone → optional Buffer/X** for recognition-worthy ships.
- Chain for milestones: **commit** → **push** (usually already done) → **draft tweets** → **Buffer publish** (Idea or X).
- Chain for routine closes: **commit** → **push** only — no social.

## When to Invoke

- Trigger phrases: `/milestone-ship`, `TBCC milestone ship`, `ship milestone to GitHub`, `push milestone and post`
- Situational triggers:
  - User declares a milestone (feature complete, protocol/automation landed, migration batch ready)
  - Large uncommitted batch should not sit local-only any longer
  - After `/milestone-ship` prep, user says `go` / `publish` / `--execute`

## Execution Profile

- Mode: **Agent**; may use **Plan** first if milestone scope is ambiguous (what to exclude from commit)
- Model lane: **Lane A (Auto)** for orchestration; **Lane B** only if milestone commit message needs architecture framing
- Parallelism: none required; optional readonly `explore` for summarizing diff stats

## Delegation & Tooling

- Skills: `tbcc-ship-log` (draft tone/rules), `protocol-author` (revisions), `model-routing`, `automate` (optional scheduled reminder)
- Commands (from `tbcc/backend`):
  - `py -3.13 scripts/milestone_ship.py --status` — unpushed work + last remote push dates
  - `py -3.13 scripts/milestone_ship.py --commit-only --message "..."` — commit staged files
  - `py -3.13 scripts/milestone_ship.py --push` — push current branch
  - `py -3.13 scripts/milestone_ship.py --post --text "..." [--idea|--queue] [--share-now]` — Buffer after push
  - `py -3.13 scripts/milestone_ship.py --execute --message "..." --post-variant 1` — full pipeline (use with care)
- Env: git `origin` remote; `TBCC_BUFFER_API_KEY`, channel ids for queue mode
- Never commit: `.env`, `*.session*`, `.tbcc-run/`, secrets, local-only vendored clones (`services/lustpress/`)

## Behavioral Rules

- Reason by: **milestone outcome** (what users/operators get), not raw file counts
- Avoid:
  - Pushing without user confirmation on `--execute` unless they explicitly said go/publish now
  - Committing secrets, Telethon sessions, API keys
  - Force-push to `main` without explicit user request
- Prioritize:
  - Current branch push (default); merge to `main` only when user asks
  - 2–3 tweet variants after push, with character counts
  - Default Buffer path: **shareNow** on X when user says “make our first post” / “post it”; otherwise **Idea** for review

## Output Contract

- Required sections:
  1. **Git status** — branch, commits ahead, last `origin/*` push date
  2. **Commit** — hash + subject if created
  3. **Push** — remote branch + result
  4. **Drafts** — 2–3 tweet variants
  5. **Buffer** — Idea id or queued/posted confirmation + link to publish.buffer.com
- Done means: changes are on GitHub **and** Buffer has Idea or live/queued post (per user choice)
- Artifacts: git commit on remote; Buffer post/Idea; optional note in `tbcc/docs/TBCC_IMPROVEMENT_NOTES.md`

## Exit Conditions

- Next: monitor CI if configured; edit post in Buffer if Idea mode
- Follows into: `tbcc-ship-log` for smaller incremental updates without a full milestone commit

## Agent procedure

1. Run `milestone_ship.py --status`.
2. Confirm milestone scope with user unless they already said execute.
3. Stage via git (respect `tbcc/.gitignore`); write commit message from milestone theme.
4. `git push -u origin HEAD` on current branch.
5. Follow **tbcc-ship-log** Output Contract for drafts; user picks variant unless `--post-variant N` given.
6. `milestone_ship.py --post` or `ship_log_buffer.py` with chosen text.
7. Report full pipeline results per Output Contract.
