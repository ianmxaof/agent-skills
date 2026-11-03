---
name: tbcc-crystallize
description: Archive the last Cursor assistant completion (or explicit text) to llm-rag vault inbox — same contract as crystallize.py. Use when operator says crystallize, /crystallize, or save this chat to vault.
version: 1.0.0
---

# TBCC Crystallize (Cursor)

**Read-only capture.** Writes markdown to `llm-rag/knowledge/inbox/` with `suggested: true` and PII redaction. Does **not** change pricing, posting, or island deploy.

## When to use

- Operator says `/crystallize`, "crystallize this", "save to vault", "archive last completion"
- After a high-value analysis (revenue thinktank, architecture, handoff) that should enter corpora

## Procedure

1. **Identify content**
   - Default: the **last assistant message** in this thread (full text, not summary)
   - User prompt: the operator's message that triggered it (or preceding user turn)
   - If operator pasted explicit text, use that as `--response`

2. **Write via CLI** (preferred — uses shared `crystallize_service`)

```powershell
cd C:\Powercore-repo-main\telegram_bot2\tbcc\backend

# Option A: prompt + response inline (escape carefully on Windows)
py -3.13 scripts\run_crystallize.py --source cursor --model "cursor-agent" `
  --prompt "USER_PROMPT_HERE" `
  --response "ASSISTANT_RESPONSE_HERE" `
  --json

# Option B: pipe response body
@'
ASSISTANT_RESPONSE_HERE
'@ | py -3.13 scripts\run_crystallize.py --source cursor --stdin --prompt "USER_PROMPT" --json
```

Or via tbcc CLI:

```powershell
cd C:\Powercore-repo-main\telegram_bot2\tbcc\backend
py -3.13 scripts\tbcc_cli.py crystallize --source cursor --prompt "..." --response "..." --json
```

3. **Confirm** — report `path` from JSON. One line to operator: filename + inbox path.

4. **Optional PARA route** — run `INBOX_ROUTER` from `tbcc/docs/prompt-chains/INBOX_ROUTER.yaml` on the capture body (see `tbcc-prompt-chains`). Report label: `task | idea | reference | archive | inbox`. Do not move files automatically — operator moves in Obsidian when ready.

5. **Optional ingest** — if operator wants immediate RAG:

```powershell
cd C:\Powercore-repo-main\llm-rag
.\.venv-313\Scripts\python.exe scripts\obsidian_bulk_ingest.py --paths knowledge/inbox --force
```

## Other surfaces

| Surface | How |
|---------|-----|
| **CLI** | `tbcc crystallize` / `run_crystallize.py` |
| **Secretary** | Admin DM: `/crystallize` (reply to message) or last turn |
| **llm-rag** | Auto-delegates to `src/crystallize.py` when importable (wikilinks) |

## Rules

- Always `--source cursor` from Cursor sessions
- Redaction on by default — do not disable unless operator explicitly requests raw secrets in vault (discouraged)
- **Auto gate (always-on):** see `.cursor/rules/auto-crystallize-gate.mdc` — score every substantive turn; auto-write when NTK tier is `auto`/`must` via `run_crystallize_gate.py --auto`
- Manual `/crystallize` always available; auto gate never replaces explicit operator request
- Mark mentally as `suggested: true` — operator may edit in Obsidian before trusting RAG recall
- Do not touch island money path

## Auto gate CLI

```powershell
cd C:\Powercore-repo-main\telegram_bot2\tbcc\backend
py -3.13 scripts\run_crystallize_gate.py --prompt "..." --response "..." --auto --json
```

Projects registry (open-ended): `tbcc/data/crystallize_project_registry.yaml`

## Blast radius

Proposals/capture only. No `AGENT_BLAST_RADIUS` external stop required for inbox write alone.
