---
name: tbcc-ext-errors
description: >-
  Triage TBCC Chrome/Brave extension Errors panel issues (gallery.js warnings,
  service worker, content scripts). Invoke with /ext-errors, check extension
  errors, TBCC extension errors, or when the user pastes an extensions Errors
  screenshot / loadTagCatalog / Internal Server Error from the gallery.
---

# TBCC Extension Errors (v1.0)
Changelog: Initial protocol — browser Errors panel + API/log cross-check for TBCC Importer.

## Purpose

- Quickly classify extension Errors-panel noise vs real bugs after gallery/overlay/macrosearch changes.
- Cross-check whether the fault is extension JS, backend 500, or dead API (wrong DATABASE_URL / stack down).
- Give a one-screen verdict + next fix without the user re-explaining the workflow.

## When to Invoke

- Trigger phrases: `/ext-errors`, `check extension errors`, `TBCC extension errors`, `look at the Errors panel`, `extension developer errors`
- Situational triggers:
  - User attaches a screenshot of `brave://extensions` / `chrome://extensions` **Errors**
  - Console shows `TBCC loadTagCatalog`, `Internal Server Error`, or repeated `gallery.js` warnings after an extension reload
  - User says they anticipate errors during a multi-step extension QA pass and wants ongoing triage

## Execution Profile

- Mode: **Debug** preferred when diagnosing; **Agent** allowed to apply a scoped fix after stating the root cause. May switch Debug → Agent when the fix is clear and ≤3 files.
- Model lane: **Lane A (Auto)** for triage; escalate to frontier only if the stack trace implies a design fork
- Parallelism:
  - Optional `explore` subagent, **readonly**, cheap — locate callers of the failing symbol
  - Mode inheritance: explore stays readonly Debug/Ask; do not spawn write-capable implementers until root cause is stated
- Mode inheritance: subagents inherit this protocol’s declared mode at spawn

## Delegation & Tooling

- Skills invoked: `model-routing` (lane choice); this skill is the procedure
- Commands / hooks / Automations: none required
- MCP / integrations required:
  - **cursor-ide-browser** — attempt to open the Errors UI when the user asks to “navigate”
  - Shell — `tbcc-stack-cli.ps1 -Action Status`, probe `http://127.0.0.1:8000/tags/`, tail `tbcc/.tbcc-run/error-hub.log`
- Repo paths: `tbcc/extension/` (esp. `gallery.js`, `background.js`, content scripts), `tbcc/scripts/tbcc-stack-cli.ps1`

## Behavioral Rules

- Reason by: **layer first** — (1) is backend reachable and returning non-500? (2) is the warning expected soft-fail? (3) is it a new regression from this session’s extension edits?
- Avoid:
  - Treating every `console.warn` in the Errors panel as a ship-blocker (soft API failures often log here)
  - Restarting bots or spawning duplicate Telegram processes while diagnosing gallery API errors
  - Claiming `brave://` / `chrome://` navigation succeeded if MCP blocked the internal page — fall back immediately
- Prioritize:
  - One-sentence **Verdict** (noise | backend | extension bug)
  - Exact failing endpoint / file:line
  - Smallest verification step for the user (reload extension vs restart backend vs ignore)

### Browser Errors panel procedure

1. Prefer evidence the user already provided (screenshot / pasted stack).
2. If they ask to navigate: use browser MCP → try `brave://extensions` or `chrome://extensions` → find **TBCC Importer** → open **Errors**.
3. If internal URLs are blocked (common): ask for one fresh screenshot **or** open the gallery side panel DevTools console if already attached; do not loop on navigation.
4. Record: error title, context page (`gallery.html` vs service worker), top stack frame, whether it is `warn` vs uncaught exception.

### Backend cross-check (when message mentions Internal Server Error / loadTagCatalog / sync-bundle)

1. `tbcc-stack-cli.ps1 -Action Status` — is `backend` up?
2. Probe `http://127.0.0.1:8000/tags/` (and optionally `/pools/`, `/channels/`) — status + body snippet.
3. If 500 + empty SQLite / `no such table`: say **backend started without `tbcc/.env` / wrong DATABASE_URL** — restart Backend from tray; do not “fix” gallery.js for that.
4. Tail recent lines of `tbcc/.tbcc-run/error-hub.log` only if API probe is ambiguous.

### Known soft-fail pattern

`gallery.js` `loadTagCatalog` → `console.warn("TBCC loadTagCatalog:", lastErr)` on non-connection errors. This **surfaces in the Extensions Errors UI** even when the gallery UI still works. Classify as:
- **Backend unhealthy** if HTTP 500 / missing tables
- **Noise / expected** only if user intentionally has API down and is testing offline UI
- **Extension bug** only if the request URL/headers are wrong while `/tags/` is healthy in curl

## Output Contract

- Required sections:
  1. **Verdict** — one line: noise | backend | extension | mixed
  2. **Evidence** — error text, file:line, HTTP status if probed
  3. **Root cause** — one short paragraph
  4. **Fix now** — ≤3 concrete steps (or “no code change; restart backend”)
  5. **Watch next** — what new Errors to ignore vs escalate during this QA pass
- Format: concise bullets; no essay
- Done means: user can act on Fix now without re-pasting the same screenshot explanation
- Artifacts: none required (optional note in chat only)
- Failure contract: if browser MCP cannot open `brave://extensions` and no screenshot/stack is available, halt after probes and ask for one Errors screenshot — do not invent stack frames

## Exit Conditions

- Next: user applies Fix now, or says “fix it” → Agent implements scoped fix
- Follows into: normal completion-gates if code changed; otherwise none

## Agent procedure

1. Collect evidence (screenshot / MCP / prior message).
2. Run stack + `/tags/` probes when the error smells like API 500.
3. Emit Output Contract sections 1–5.
4. Only edit code if the user asks to fix, or the verdict is clearly an extension bug introduced in-session and they are mid-QA expecting fixes.
