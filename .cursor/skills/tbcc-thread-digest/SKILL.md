---
name: tbcc-thread-digest
description: >-
  Day-scoped board of Cursor parent Agents plus full subagent exposure (tools,
  weight, local/cloud inference, usage-limit hits). Writes vault
  0-Inbox/thread-digest-YYYY-MM-DD.md, inbox card for second brain, ends with
  file:// anchor. Invoke with /thread-digest, /day-threads, or when cutting
  parallel-agent RAM/MCP load.
---

# TBCC Thread Digest (v1.1)

Changelog: v1.2 — live Cursor $ / tokens via dashboard API + NIC bytes. v1.1 — headcount/subagents. v1.0 — parent subjects.

## Purpose

- Show **what subjects you opened with each Agent chat today** so you can finish or close extras.
- Cut parallel-agent load (RAM, CPU, MCP/WiFi chatter) by making the pile visible.
- Not sitrep (money/CI), not daily-brief (sprint loose ends), not evening digest (vault captures).

## When to Invoke

- Trigger phrases: `/thread-digest`, `/day-threads`, `thread digest`, `what did I open with agents today`, `consolidate agent threads`
- Situational: many Agent chats open; feeling machine/network pressure from MCP; mid-day reset before opening another agent

## Execution Profile

- Mode: Agent (read + write **only** the digest markdown)
- Model lane: A (Auto)
- Parallelism: none required
- MCP: **none** — do not attach Buffer/Cloudflare/TBCC MCP for this skill

## Delegation & Tooling

Run (preferred):

```powershell
cd C:\Powercore-repo-main\telegram_bot2\tbcc\backend
py -3.13 scripts\run_thread_digest.py --all-projects
```

Flags: `--day YYYY-MM-DD` · `--dry-run` · `--json` · omit `--all-projects` to scan default telegram_bot2 slugs only.

Service: `app/services/thread_digest_service.py`

## Headcount + subagent exposure

The digest markdown includes:

1. **Headcount** — parent Agents, subagents, tool-call sum, heavy/cloud/local, usage-limit hits, transcript KB proxy
2. **Parent agents** — subjects
3. **Subagents (full exposure)** — task, parent id, placement, weight, tools, errors
4. **Pare down** — X/Y/Z style mitigations for the next heavy day
5. **Second brain** — vault `0-Inbox` + slim `knowledge/inbox/thread-digest-card-*.md`; Hermes brain pack key `thread_digest`

### What is included for $ / tokens / network

- **Cursor $ + tokens:** live from Cursor dashboard API using local `state.vscdb` auth (no secrets in the markdown).
- **Wi‑Fi / network:** Windows NIC cumulative RX/TX (all apps since adapter reset) — labeled as such; Cursor-only bytes are not exposed by process-monitor.
- Do not invent numbers if the probe fails — show the error line.

## Behavioral Rules

- Prefer the script output over hand-skimming transcripts.
- Do not invent $ or bandwidth numbers.
- End the operator reply with the **Anchor link** line.
- Suggest closing chats / fewer Task spawns from the Pare-down section — do not kill processes yourself.
- Avoid: merging into sitrep; starting Hermes/OpenClaw from this skill.

## Output Contract

1. **Pulse** — day + parent count + subagent count
2. **Headcount** — one short table or bullets
3. **Subjects** — parents (cap ≤12 in chat)
4. **Subagent highlights** — heaviest / usage-limit / cloud (cap ≤10 in chat; full list in file)
5. **Pare down** — the script tips
6. **Anchor** — `file:///` + path

Done means: file written and anchor posted.

## Exit Conditions

- Next: operator closes Agent chats / continues one thread / runs `/sitrep` if they care about shipped work
- Hermes twin: `%LOCALAPPDATA%\hermes\skills\operator-thread-digest\SKILL.md` (optional morning attach)
- Claude Code twin: `.claude/skills/tbcc-thread-digest/SKILL.md`

## Hermes / gateway note (related)

Hermes **gateway** is a long-lived process (`hermes gateway start|stop|restart|status`). It is heavier than a one-shot digest. Prefer: status → restart only when stale → stop when idle for the day. Do not leave orphan PIDs (Windows Job Object can kill children without a clean record — see `hermes gateway status` warnings). OpenClaw orchestration is a separate FastAPI host — start only for a run, stop when done; do not leave uvicorn always-on unless you mean to.
