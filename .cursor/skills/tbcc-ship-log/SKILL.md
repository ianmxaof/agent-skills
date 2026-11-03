---
name: tbcc-ship-log
description: GSP v2.0 protocol — draft and publish short engineer progress updates (X via Buffer) from TBCC git history and improvement notes. Invoke with /ship-log, "TBCC ship log", or "draft my build-in-public tweet".
---

# TBCC Ship Log Protocol (v1.0)

Changelog: Initial protocol — sources, draft contract, Buffer Idea/queue publish path.

## Purpose

- Turn recent TBCC engineering work into short, public-facing X posts (build-in-public / ship log).
- Separate **engineering narrative** from TBCC's existing **content mirrors** (Scheduler → Buffer caption mirrors).
- Use when closing a session, after a meaningful commit batch, or on a weekly cadence.

## When to Invoke

- Trigger phrases: `/ship-log`, `TBCC ship log`, `draft my build-in-public tweet`, `ship log to Buffer`
- Situational triggers:
  - User finished a TBCC feature or fix and wants to share progress
  - End of week recap from git + `tbcc/docs/TBCC_IMPROVEMENT_NOTES.md`
  - User says "integrate GSP" / "run ship log protocol" in the TBCC repo

## Execution Profile

- Mode: **Agent** (draft + optional publish); may switch to **Plan** if the user wants strategy (tone, cadence, what to omit) before drafting
- Model lane: **Lane A (Auto)** for gather + draft + script publish; **Lane B (frontier)** only if user asks for voice/brand strategy across a thread. Per model-routing skill; user picker wins.
- Parallelism:
  - `explore` subagent, readonly, cheap model — optional for scanning recent diffs across many files
  - No implementation subagents unless user also requests code changes

## Delegation & Tooling

- Skills invoked: `protocol-author` (revisions only), `model-routing` (lane picks), `automate` (only if user asks for a Cursor Automation from this workflow)
- Commands:
  - `py -3.13 scripts/ship_log_sources.py` — print git + notes context (tbcc/backend)
  - `py -3.13 scripts/ship_log_buffer.py --dry-run` — draft file paths only; agent drafts tweets in chat
  - `py -3.13 scripts/ship_log_buffer.py --idea --title "..." --text "..."` — Buffer Idea
  - `py -3.13 scripts/ship_log_buffer.py --queue --text "..."` — X queue via createPost
  - `py -3.13 scripts/buffer_channels.py` — list org + channel ids
- MCP (optional): Buffer MCP (`https://mcp.buffer.com/mcp`), TBCC MCP (`tbcc/mcp-server`)
- Env: `TBCC_BUFFER_API_KEY`, `TBCC_BUFFER_ORGANIZATION_ID` (or auto-discover), `TBCC_BUFFER_CHANNEL_ID_PRIMARY` for queue mode

## Behavioral Rules

- Reason by: **what shipped** (user-visible outcomes), not file lists; one concrete win per tweet when possible
- Avoid:
  - API keys, tokens, `.env` values, internal chat ids, session paths
  - NSFW/content-pipeline operational detail unless user explicitly wants that angle
  - Auto-publishing without user approval unless they said `publish` / `--queue` / `--idea`
- Prioritize:
  - ≤260 characters per tweet (leave room for edits; hard cap 280)
  - Plain language; name TBCC once if helpful, not every tweet
  - Cite 1–2 real changes from git subject lines or improvement notes

## Output Contract

- Required sections in chat response:
  1. **Sources** — date range, commit count, notes file excerpt (brief)
  2. **Drafts** — 1–3 tweet options, each with character count
  3. **Recommended** — which draft and why (one line)
  4. **Publish** — what was queued / Idea id / "awaiting your pick"
- Format: Markdown; drafts in fenced blocks for easy copy
- Done means:
  - User has approved drafts **and** either (a) Buffer Idea or queued post was created, or (b) user chose copy-only / dry-run
- Artifacts:
  - Buffer Idea or post when publish mode requested
  - Optional: user pastes chosen draft into `tbcc/docs/TBCC_IMPROVEMENT_NOTES.md` "Ship log" section if they maintain one

## Exit Conditions

- Next: user edits in [Buffer](https://publish.buffer.com) or picks another draft
- Follows into: `automate` skill if user wants scheduled weekly `/ship-log`; otherwise **none**

## Agent procedure (execute in order)

1. Run `ship_log_sources.py` (default 7 days) or user-specified `--since`.
2. Read `tbcc/docs/TBCC_IMPROVEMENT_NOTES.md` if present.
3. Produce **Drafts** per Output Contract; ask which to publish unless user already specified.
4. On approval:
   - **Idea (default):** `ship_log_buffer.py --idea --title "TBCC ship log YYYY-MM-DD" --text "<draft>"`
   - **Queue:** `ship_log_buffer.py --queue --text "<draft>"` (requires X channel id in `.env`)
   - **Buffer MCP:** equivalent createIdea / createPost if MCP is connected and user prefers chat-only tooling
5. Report Idea id or queue result; link to publish.buffer.com.
