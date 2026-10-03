---
name: tbcc-silent-fail
description: >-
  GSP v2.4 — second-pass check for expected work that never fired, stalled, or
  was orphaned (class-2 silent abandon). External stops only — no agent
  self-attestation. Invoke with /silent-fail, /zombie-pass (alias), silent fail
  pass, second-pass non-activity.
---

# TBCC Silent-Fail Pass (v1.4)

Changelog: v1.4 — Harness attach (MCP/hooks/memory/compose). v1.3 — Freedom low + tickable probe checklist + revise-if-no-stop loop. v1.2 — always-on repo rule `.cursor/rules/tbcc-silent-fail.mdc`. v1.1 — Phase 2 pilots B+D. v1.0 — protocol contract.

## Purpose

- **Always-on:** `.cursor/rules/tbcc-silent-fail.mdc` (`alwaysApply: true`) — gate before "done" on Beat/worker/deploy/crew/multiphase/CC ACK. This skill is the full protocol when invoked explicitly.
- Catch **class 2** failures: stack/process may look fine, but enabled expected work **never succeeded**, went **stale** past cadence, or left **orphaned** queue state — including “never fired once in its lifetime.”
- Require **external stop evidence** (HTTP / Redis / DB / file / pytest / log timestamp). Agent “I checked” is never enough.
- Reuse Calm Ops / governor / scheduling health for **class 1**; fence **class 3** intentional idle so it is not paged as a zombie.

## Failure classes (locked)

| Class | Meaning | Protocol role |
|-------|---------|----------------|
| **1 process-down** | PID/worker/API missing | Reuse existing detectors; do not fork a parallel health stack |
| **2 work-never-ran** | Enabled + expected cadence, but `never_seen` or `last_success` too old / orphaned work | **Primary subject** of this protocol |
| **3 intentional-idle** | `*_ENABLED=0`, island Beat omit, governor `governed_idle`, feature off | **Not a zombie** — tag `idle` and skip escalate |

**Name collision:** `network_liveness_*` / AOF network liveness = content posting cadence — **out of subject** unless the operator explicitly names a posting watch.

## When to Invoke

- Trigger phrases: `/silent-fail`, `/zombie-pass` (alias), `silent fail`, `second-pass non-activity`, `zombie pass`, `never-fired check`
- Situational:
  - **Always-on lean:** after sitrep / ops-picture / multiphase handoff ACK when scheduling or Beat-facing work shipped
  - **Conditional:** multi-part deploys; `/crew` (when that skill exists); ≥2 systems expected to move together; operator says components “might be dormant”
- **Skip:** pure docs/lint copy edits; named one-line bug with “just the bug”; inventing restart policy; Start bots / `.env`; Supervisor panel deep rewrite; dead-link watchdog build; treating governor-idle as fail without enablement+cadence proof

## Always-on vs conditional

| Mode | When | What to check | Cap |
|------|------|---------------|-----|
| **Always-on (lean)** | Session start sitrep, post-deploy smoke, weekly ops hygiene | Class-1 reuse: `/health`, scheduling_health / celery_ops; plus ≤3 registry watches marked `mode: always_on` | ≤5 watches total |
| **Conditional** | Crew/multiphase/deploy with many moving parts | Watches tied to the change set + any `mode: conditional` registry entries that match touched surfaces | ≤8 watches; prefer the slice’s blast radius |

Default when ambiguous: **conditional on the current blast radius**, plus one always-on class-1 health stop.

## Execution Profile

- Freedom: **low** (exact external-stop probes + locked verdict enum; no freestyle “looks fine”)
- Mode: **Ask / Agent readonly** for probes; **no** Start bots; **no** auto-restart
- Model lane: Desktop Auto; Frontier only if classifying enablement vs idle is ambiguous across many env gates
- Parallelism: optional one readonly cheap `explore` to locate probe helpers
- Mode inheritance: explore stays readonly; no implementation subagents in this protocol

## Delegation & Tooling

- Prior inventory: `tbcc/docs/handoffs/2026-08-24_silent-fail-second-pass_report.md`
- Registry sketch (design): `tbcc/docs/SILENT_FAIL_REGISTRY.example.json` — do not invent production daemons from the example alone
- Reuse (read): `idle_service_governor.py`, `system_health.py` (`cached_scheduling_health`), `intake_scheduler.py` (`get_last_run_ts`), `post_scheduler.py` (drain_tick / due_queue), `ops_picture_report.py`
- Optional reasoning (Plan only, when class-2 cause unclear): `tbcc-prompt-chains` bundle `incident_triage` (`FIRST_PRINCIPLES_STRIP` → `CRITICAL_PATH_ANALYSIS`) on pasted probe evidence — does not replace external stops
- Island truth: `https://api.powercore.app/health` — **not** home tray `/ops/stack-status` alone (tray-unavailable on island)
- MCP: none; do not Start bots
- Compose: after this pass → fix plan / `/preflight` / `/directive` only if operator picks; `/crew` (future) **must** end with a silent-fail stop list

## Harness attach

| Surface | Value |
|---------|--------|
| **MCP** | none (CLI probes: `silent_fail_probe.py`, health HTTP) |
| **Hooks** | this skill *is* the done-hook for Beat/crew/CC ACK / multiphase “done” |
| **Memory** | disk: optional registry notes; reply must carry probe command + snippet (chat-ok for verdict table) |
| **Compose** | → `tbcc-preflight` \| `directive-generator` |

## Behavioral Rules

- Reason by: for each watch — `enablement` ∧ `expected_cadence` → probe → verdict `ok` | `stale` | `never_seen` | `idle` | `blocked`
- Flag zombie only when **both** enablement and expected cadence are true **and** (`never_seen` **or** age(`last_success`) > threshold) **or** orphaned queue evidence
- Idle-desired ≠ zombie (class 3)
- Avoid: self-attestation; auto-restart; paging channel invention; second parallel health daemon; conflating network liveness with this pass
- Prioritize: reversible read-only probes; reuse existing Redis/API helpers; operator ACK before any mutate

## External stops schema

Every watch row in the output **must** include ≥1 stop of these kinds (copy the probe result verbatim):

| `stop_kind` | Example |
|-------------|---------|
| `http` | `GET https://api.powercore.app/health` → body contains `"status":"ok"` |
| `api_field` | scheduling snapshot `celery_ops_worker_running == true` |
| `redis` | key present/value age (e.g. intake `last_run`) |
| `db` | row `updated_at` / side-effect timestamp |
| `file` | artifact path exists + mtime |
| `pytest` | exact `py -3.13 -m pytest …` exit 0 |
| `log_ts` | log line with timestamp proving success |

**Forbidden as sole stop:** “looks fine”, “I ran the worker mentally”, “agent claims done”.

Verdicts:

- `ok` — enablement on, probe within cadence
- `stale` — enablement on, last_success older than threshold
- `never_seen` — enablement on, no success evidence ever (or sentinel 0 / missing key where success should write)
- `idle` — class 3; not a fail
- `blocked` — cannot probe (no Redis/API); report and stop expanding that watch

## Output Contract

Required (dense):

1. **Mode** — `always_on` | `conditional` (+ one-line why)
2. **Watches** — table/list ≤8: `id` | class | verdict | **external stop evidence** (command + snippet)
3. **Zombies** — only `stale` / `never_seen` rows; empty if none
4. **Fence** — what was skipped as idle / out of subject / Do-not-touch
5. **Next** — none | `/preflight` | `/directive` | discuss Phase 2 pilot — **no auto-fix**

Done means: every listed watch has an external stop; operator can re-run the same commands; self-correct passed (no verdict without stop evidence).

Failure contract: if a probe errors, mark `blocked`, show the error, do not invent success; do not Start services to “make the probe green.”

### Self-correct (verdicts)

1. **Draft** the watches table with provisional verdicts.
2. **Check** every row has ≥1 external stop (command + snippet). Rows with only agent claim → fail.
3. **Revise** — re-probe or mark `blocked`; never finalize `ok`/`stale`/`never_seen`/`idle` without stop evidence.
4. If a failure mode is not covered by this skill, suggest **one** new rule for operator ACK (do not auto-write).

## Exit Conditions

- Next: operator picks fix / ignore / add registry watch / unlock Phase 2 pilot
- Composes: → `tbcc-preflight` (if ≥3-file fix) | `directive-generator` (Lane C grind)
- Follows from: `/crew` (tbcc-agent-crew) **must** end with this pass
- Follows into: Bottom line may show **Compose: /silent-fail** after multiphase ACK or crew

## Agent procedure

Copy this checklist and tick as you go (order matters):

```
- [ ] 1. Resolve mode (always_on vs conditional) from trigger + blast radius
- [ ] 2. Load registry example + Phase 0 report; pick ≤8 watches (prefer blast-radius match)
- [ ] 3. For each watch: prove enablement; run external probe; assign verdict
- [ ] 4. Self-correct: every row has stop evidence — revise or mark blocked until pass
- [ ] 5. Emit Output Contract. Stop — no restarts, no commits unless asked
```

## Worked example (external stops)

```powershell
# Class 1 — island API
(Invoke-WebRequest -Uri "https://api.powercore.app/health" -UseBasicParsing -TimeoutSec 15).Content

# Class 2 pilot B — intake last_run (needs REDIS_URL)
cd tbcc/backend
py -3.13 scripts/silent_fail_probe.py intake --lane inbox
# first line: ok | stale | never_seen | idle | blocked

# Class 2 pilot D — Beat storage-hub-r2-export via Media.r2.exported_at (needs DATABASE_URL)
py -3.13 scripts/silent_fail_probe.py r2-export
py -3.13 scripts/silent_fail_probe.py all --json
```

## Registry

See `tbcc/docs/SILENT_FAIL_REGISTRY.example.json`. Pilots B+D implemented in `app/services/silent_fail_probes.py` + `scripts/silent_fail_probe.py`.