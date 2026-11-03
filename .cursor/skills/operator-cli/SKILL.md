---
name: operator-cli
description: >-
  Unified CLI hub for operator skills (semantic scan, and others as registered).
  Invoke with `operator` or `python -m operator_cli` when on PATH.
---

# Operator CLI (v0.3)

Changelog:
- v0.1 — registry stub; first subcommand delegates to semantic-deception-detector.
- v0.2 — capability-bus v0: `registry.json` is now the actual machine-readable skill list (`operator list` reads it, doesn't hard-code it). Registered four skills: `semantic-scan` (live), `research` / `llm` / `slots` (delegate to `tbcc_cli.py` — those engines already exist, this just makes them discoverable and reachable from one hub, see "Do not rebuild" below).
- v0.3 — `operator.cmd` PATH shim; `TBCC_REPO_ROOT` env override for delegate paths (default still `C:\Powercore-repo-main\telegram_bot2`, else walk up from cwd).

## Purpose

Single entry point for skills you want at the terminal without opening Cursor/Hermes:

```powershell
operator list
operator semantic-scan --json https://github.com/owner/repo
operator research feed-list --json
operator llm status
operator slots list --json
```

After PATH install (below), run `operator` from any directory. Delegates resolve `tbcc_cli.py` via `TBCC_REPO_ROOT` when set, else the default checkout path.

## Layout

| Path | Role |
|------|------|
| `%USERPROFILE%\.cursor\skills\operator-cli\operator.cmd` | PATH shim → `operator_cli.py` |
| `%USERPROFILE%\.cursor\skills\operator-cli\operator_cli.py` | Thin dispatcher (not `operator.py` — stdlib shadow) |
| `%USERPROFILE%\.cursor\skills\operator-cli\registry.json` | Machine-readable skill list — id, description, entry, corpora[], status |
| `%USERPROFILE%\.cursor\skills\semantic-deception-detector\scripts\` | Scan engine + fetch + `semantic_scan.py` (the `semantic-scan` **live** skill) |
| `tbcc\backend\scripts\tbcc_cli.py` | The engine `research` / `llm` / `slots` **delegate** to — see "Do not rebuild" |

Add a skill by adding an entry to `registry.json` and, if it needs custom arg handling beyond plain forwarding, a subcommand in `operator_cli.py`.

## Do not rebuild

`research`, `llm`, and `slots` are **delegates**, not reimplementations:
- `llm` — TBCC's local LLM provider/model index + sticky rotator (`app/services/llm_model_index.py`). Already handles refresh/status/next/ask/keys/models across ~13 providers.
- `slots` — API Pocket, the operator's PC-local REST service-slot registry (`app/services/api_slot_registry.py`). Already handles add/list/show/call/remove/suggest.
- `research` — the RSS/Atom research scanner (`app/services/research_scanner.py`). `feed-add`/`feed-list` are new (capability-bus v0); `scan` was pre-existing.

`operator_cli.py` forwards to `tbcc_cli.py <subcommand> <rest of argv>` unchanged for these three — it does not parse or validate their arguments itself, so any flag `tbcc_cli.py research/llm/slots` accepts works through the hub with no extra wiring.

## Install (optional)

Add to PATH:

```powershell
$hub = "$env:USERPROFILE\.cursor\skills\operator-cli"
$scripts = "$env:USERPROFILE\.cursor\skills\semantic-deception-detector\scripts"
# User-level PATH — run once in PowerShell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$hub;$scripts", "User")
```

Then open a **new** terminal and:

```powershell
operator list
operator semantic-scan --json <target>
```

Optional — different checkout:

```powershell
$env:TBCC_REPO_ROOT = "D:\other\telegram_bot2"
operator research feed-list --json
```

Direct without hub: `semantic_scan.py --json <target>` (semantic-deception-detector `scripts/` on PATH).

## Subcommands

| Command | Status | Delegates to |
|---------|--------|----------------|
| `list` | live | reads `registry.json` |
| `semantic-scan` | live | `semantic-deception-detector/scripts/semantic_scan.py` |
| `research` | delegate | `tbcc_cli.py research` (`scan`, `feed-add`, `feed-list`) |
| `llm` | delegate | `tbcc_cli.py llm` (`status`, `next`, `ask`, `keys`, `models`, …) |
| `slots` | delegate | `tbcc_cli.py slots` (`add`, `list`, `show`, `call`, `remove`, `suggest`) |

## Capability bus: local transferable context, not Context7

`registry.json`'s `corpora` field lists local file paths worth reading for context on a skill — e.g. `research`'s corpora point at `research_scanner_sources.json` and its Hermes SKILL.md. This is **not** a Context7-style cloud documentation lookup: nothing here is fetched from a hosted docs index, versioned by a package registry, or shared beyond this machine. It's a pointer list into files that already live in this repo/skills tree, meant to save an agent a `find`/`grep` round trip before it touches a registered skill — same spirit as this file's own "Do not rebuild" section, just structured for a script to read instead of a human. If a skill's context genuinely belongs in a cloud doc source later, that's a distinct, larger decision (see `tbcc/docs/OPERATOR_CAPABILITY_BUS.md`) — not something this registry does today.

## Security

- Fetched trees are **never executed** — fetch → scan → delete temp.
- Size caps on downloads (see `fetch_target.py`).
- Structural score gates exit code for unattended use.

## Verification

```powershell
python "$env:USERPROFILE\.cursor\skills\operator-cli\operator_cli.py" list
python "$env:USERPROFILE\.cursor\skills\operator-cli\operator_cli.py" semantic-scan --self-test
python "$env:USERPROFILE\.cursor\skills\operator-cli\operator_cli.py" semantic-scan --json https://github.com/octocat/Hello-World
python "$env:USERPROFILE\.cursor\skills\operator-cli\operator_cli.py" research feed-list --json
python "$env:USERPROFILE\.cursor\skills\operator-cli\operator_cli.py" llm status
python "$env:USERPROFILE\.cursor\skills\operator-cli\operator_cli.py" slots list --json
```

Expect structural LOW on benign tiny repos; inspect HIGH manually. `list` should print all four registered skills; the three delegate commands should return without crashing (empty/near-empty output is fine — they're reporting real local state, not a fixture).
