---
name: semantic-deception-detector
description: >-
  Scans a local codebase for docs-vs-behavior mismatches, hidden Unicode in
  agent rule files, and comment text that looks like prompt-injection bait.
  Use for semantic deception detection, obfuscated-intent reviews,
  TrapDoor-style CLAUDE.md / .cursorrules hiding, or /semantic-scan.
---

# Semantic Deception Detector (v1.0.2)

Changelog:
- v1.0 — local metal-detector skill; evidence-backed triage, not a polygraph.
- v1.0.1 — fixed cross-file false pairing (a denial in one file could be paired with a capability in an unrelated file) and a docstring line-number attribution bug (function/class docstring claims were reported at line 1 instead of their real line). Both `direct_contradiction`/`side_effect_contradiction` pairing and the `undocumented_capability` omission check are now scoped per file.
- v1.0.2 — every finding now carries a `confidence` field (`high` | `heuristic`, fixed per category — see table below). Report adds `structural_score`/`structural_level`, computed from `high`-confidence findings only. `--json` and text-mode exit codes now gate on `structural_level`, not the total `risk_level` — so heuristic-only findings (`undocumented_capability`, non-rule `hidden_unicode`) are still reported for human review but no longer trip unattended/Hermes gating on their own.
- v1.0.3-cli — `semantic_scan.py` CLI accepts local paths **or** URLs (GitHub repo/tree/blob, gist, pastebin raw, generic raw URL). Fetch layer is stdlib-only; `scan.py` stays local-only. Hub: `operator-cli` → `operator semantic-scan`.

Reusable agent skill. Cursor and Hermes share the same scanner script.

## Purpose

- Flag **suspicious** mismatches between what a tree *claims* (README, docstrings, package metadata) and what the code *does* (imports, network, subprocess, eval/exec, pickle, ctypes).
- Flag **hidden Unicode** in agent rule files (`CLAUDE.md`, `.cursorrules`, `.cursor/rules`, `SKILL.md`) and comment/rule text that matches known prompt-injection bait.
- Produce a human-reviewable report. Never declare guilt, intent, or legal liability.

## When to Invoke

- Trigger phrases: `/semantic-scan`, `semantic deception detector`, `scan for obfuscated intent`, `docs vs code mismatch`, `TrapDoor scan`, `hidden unicode in CLAUDE.md`
- Situational: operator is about to vendor a local checkout, review a dependency tree on disk, or audit agent rule files after a supply-chain scare

**Do not use for:** judging “ulterior motives,” bypassing model safety, generating hidden Unicode / jailbreaks, or **executing** untrusted fetched code. CLI fetch is read-only triage — clone if you need to run/build.

## CLI (terminal)

For ad-hoc scans of repos/gists/pastes you find on the web:

```powershell
python "$env:USERPROFILE\.cursor\skills\semantic-deception-detector\scripts\semantic_scan.py" --json "https://github.com/owner/repo"
python "$env:USERPROFILE\.cursor\skills\operator-cli\operator_cli.py" semantic-scan --json "https://gist.github.com/user/id"
```

Supported URL shapes: GitHub repo root, `/tree/ref/subpath`, single-file `/blob/ref/path`, public gist, `pastebin.com/raw/…`, other raw text URLs (size-capped). Temp checkout is deleted after the scan unless you copy results first.

JSON adds a top-level `fetch` block: `source_url`, `source_kind`, `scan_root`.

## Execution Profile (agent / Cursor)

- Mode: Agent (readonly scan). Do not switch to Plan.
- Model lane: Desktop Auto for the scripted scan. Optional short Frontier Ask only if the operator wants a *second-pass narrative* of an already-scored HIGH report.
- Parallelism: none required. Readonly explore is allowed.
- Mode inheritance: n/a

## Delegation & Tooling

- Skills invoked: none required
- Local engine: `scripts/scan.py` (stdlib only; no network)
- CLI fetch + scan: `scripts/semantic_scan.py` or `operator_cli.py semantic-scan` (see CLI section)
- MCP: none for agent invocations

## Behavioral Rules

- Reason by: **script first**, then summarize. The AST/regex pass is the source of truth; the model only explains findings.
- Treat every finding as **suspicious / needs review**, not intentional deception. Stale docs are the common case.
- Demand evidence: path + line + snippet for every alarm. No vibe scores.
- Lead with `structural_level`/`structural_score` (high-confidence findings only) for the headline verdict; report `risk_level`/`risk_score` (total, all confidence levels) as the fuller picture. Never present a heuristic-only finding (`undocumented_capability`, non-rule `hidden_unicode`) with the same confidence language as a `high`-confidence one.
- Scope: **local directories only**. If the operator pastes a URL, tell them to clone it themselves, then scan the checkout.
- Skip secrets: the scanner already ignores `.env`, session files, and credentials by name. Do not `cat` those files to “enrich” the report.
- Do not assume bad faith. Do not compare against a legal/policy PDF unless the operator supplied one *and* asked for a docs-consistency pass (separate from this scanner).
- Do not run scanned code, Docker sandboxes, or install the target as a package.

## Agent procedure

1. Resolve the target to a local folder. If missing, ask once. **Do not assume "current workspace root" means the right thing** — the Cursor/Hermes workspace root can change independently of what the operator wants scanned (e.g. it was `telegram_bot2\tbcc` when that was the only open folder; it is `telegram_bot2` — the wider monorepo, `tbcc` plus `aof-forum` and everything else — now that the workspace root moved up a level). For TBCC/AOF work, the known-good default is the `tbcc` subfolder specifically:

```powershell
python "$env:USERPROFILE\.cursor\skills\semantic-deception-detector\scripts\scan.py" --json -- "C:\Powercore-repo-main\telegram_bot2\tbcc"
```

Only scan the full monorepo root (`telegram_bot2`, no `tbcc` suffix) if the operator explicitly asks for the wider surface — it pulls in `aof-forum/` and everything else alongside `tbcc/`.

2. Run the scanner (Windows PowerShell example; adjust the skill home if this file was copied):

```powershell
python "$env:USERPROFILE\.cursor\skills\semantic-deception-detector\scripts\scan.py" --json -- "<LOCAL_DIR>"
```

From this skill directory:

```powershell
python .\scripts\scan.py --json -- .
python .\scripts\scan.py --self-test
```

Exit code `1` means `structural_level` is REVIEW or HIGH — i.e. at least one `high`-confidence finding (`direct_contradiction`, `side_effect_contradiction`, `hidden_unicode_agent_rule`, `injection_bait`). Heuristic-only findings (`undocumented_capability`, non-rule `hidden_unicode`) still appear in the report but do not by themselves flip the exit code — check `risk_level`/`risk_score` (total) for the fuller, noisier picture. Exit `2` means bad args / URL refused. Neither is a scanner crash.

3. Read the JSON. Group findings by `category`. Quote `path:line` and `evidence`.
4. Optional LLM pass (only if the operator asked, or risk_level is HIGH): for each `direct_contradiction` / `hidden_unicode_agent_rule` / `injection_bait`, write one sentence of *what a reviewer should check*. Do not invent extra findings the script did not emit.
5. Emit the Output Contract. Stop. Do not “fix” the target tree unless the operator asked.

## Output Contract

Required sections:

1. **Verdict** — lead with `structural_level` | `structural_score` (high-confidence findings only — copy both from the script). Follow with total `risk_level` | `risk_score` (all confidence levels) as the fuller picture. One sentence: what to do (ignore / spot-check / human security review).
2. **Evidence** — table or list: category, path:line, evidence, detail, **confidence** (`high` | `heuristic`, from the script's `confidence` field — do not invent or infer it). Cap at 25 rows; say how many were omitted.
3. **Likely benign** — call out undocumented `eval` in tests, README lag, UTF-8 BOM. Do not drop HIGH categories here.
4. **Not claimed** — explicit: this is not malware confirmation, not intent, not a legal opinion.
5. **Next** — one question: deeper file review, or stop.

Done means: scanner ran on a local path; report includes script score + evidence; no remote clone; no code execution of the target.

Failure contract: if Python is missing, `scan.py` errors, or the path is a URL, halt. Report what completed. Do not hand-roll a replacement parser in-session.

## Exit Conditions

- Next: operator picks a finding to inspect, or discards the report
- Follows into: none (orthogonal to TBCC sprint protocols)

## What the script actually flags

| Category | Meaning | Confidence |
|---|---|---|
| `direct_contradiction` | Docs deny network / filesystem / subprocess; code still does it, same file | `high` |
| `side_effect_contradiction` | Docs claim pure / no side effects; code has network, spawn, or exec, same file | `high` |
| `hidden_unicode_agent_rule` | Zero-width / bidi chars in agent rule files (TrapDoor-class hiding) | `high` |
| `injection_bait` | Comment or rule-file text matching known instruction-override bait | `high` |
| `undocumented_capability` | subprocess / eval / ctypes / pickle in non-test code with no docs mention in that same file (noisy) | `heuristic` |
| `hidden_unicode` | Same chars outside rule files (lower weight; BOM ignored) | `heuristic` |

`confidence` is fixed per category (v1.0.2), not inferred per finding. `structural_score`/`structural_level` sum only `high`-confidence findings — that's the number safe to gate unattended runs on. `risk_score`/`risk_level` sum everything and stay useful for a human doing a full pass, but including `heuristic` categories makes them noisier by design.

## Pitfalls

- False positives are the job. A high score on a large app that uses `requests` and never said “no network” is usually LOW unless denials exist.
- JS is regex, not a parser. Python AST is the reliable half.
- Will not catch time bombs, env-gated payloads, or encrypted strings. Say so if the operator asks “are we safe?”
- Scanning this skill’s own `scripts/scan.py` will surface its detector signature strings as `injection_bait`. That is expected.
- `undocumented_capability` and non-rule `hidden_unicode` are `heuristic`, on purpose — they're common in ordinary, benign code (an API launcher importing `subprocess`, a compound emoji literal). List them for a human to skim; do not treat them as evidence of anything on their own, and do not let them gate an unattended/Hermes run — that's what `structural_level` is for.

## Verification

```powershell
python "$env:USERPROFILE\.cursor\skills\semantic-deception-detector\scripts\scan.py" --self-test
```

Must print `self-test: PASS`.
