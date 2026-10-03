# Directive Generator — dry-run examples

## Example A — messy fixture (greenfield-ish)

**Input:**

```
TARGET: Claude Code
ISSUES:
- vision lane stuff broken on network?
- tests failing maybe test_media_lane
- also update sprint state
- don't touch payment
- need report back
```

**Preface (outside fence):**

- **Literal:** Package Claude Code work so vision-lane tests pass and status is reported without touching payment.
- **Ascend:** yes — verify/fix `test_media_lane*` + write reverse report; defer sprint-state polish unless required for ACK. Out: payment.
- **TARGET:** Claude Code

**Emit (abridged — full emit must include every required section):**

```
## Goal
All mapped media-lane vision pytest green; reverse report written; stop for Cursor ACK.

## Scope
- In: tbcc/backend/app/services/media_lane_vision_classify.py, related tests
- Out of scope: payment bot, loot, .env, live tray starts

## Prior state
Prior state: none — greenfield. (If continuity, replace this.)

## Issue cards
- I1 | symptom: possible network/vision lane failure | evidence: unknown | P1 | depends: none | acceptance: pytest path named below passes
- I2 | symptom: test_media_lane may fail | evidence: tbcc/backend/tests/test_media_lane_vision_classify.py (guess — confirm) | P0 | depends: none | acceptance: pytest … -q exits 0
- I3 | symptom: sprint state stale | evidence: tbcc/docs/SPRINT_STATE.md | P2 | depends: I2 | acceptance: Last updated patched only if Goal needs it
- I4 | symptom: need report back | evidence: n/a | P0 | depends: I2 | acceptance: *_report.md exists

## Constraints & gotchas
- MUST NOT decide payment/loot pricing or start bots
- MUST NOT commit .env / *.session*
- Cloud-only money: island is canonical

## Verification
cd tbcc/backend && py -3.13 -m pytest tests/test_media_lane_vision_classify.py -x -q --tb=short

## Working agreement
- Commit: per phase if green; push: no unless asked
- After phase: write tbcc/docs/handoffs/YYYY-MM-DD_media-lane-vision_report.md then STOP for Cursor ACK

## Phases
1. Confirm evidence paths; run Verification; fix only failures in Scope; write reverse report; STOP

## Target profile
mode: grind | tools: shell+files | MUST NOT: payment doctrine, live bot spawn, invent network root-cause without evidence
```

**Paste into Claude Code.** Feeds `/handoff-cc` — or paste as-is if sections match.

---

## Example B — continuity (from `2026-08-20_vision-lane-decisions_network-blocked-handoff.md`)

**Messy operator dump (simulated):**

```
TARGET: Claude Code
ISSUES:
- previous session blocked on network to island — need fresh session to deploy vision lane decision log
- migration 119 + classify code already done locally, tests passed
- deploy island, alembic upgrade head, smoke health
- also ghost town no albums posting — check stack-status
- don't re-argue the working tree / don't touch payment
- report back
```

**Ascend:** yes — Goal = migrate 119 + deploy backend + smoke health + confirm decision rows path; ghost-town is **I-orthogonal** (diagnose in report, do not block migrate unless operator says so).

**Prior state (required):**

- Shadow-mode vision lane classify + migration 119 + tests already green locally — do not re-implement
- Tree triage already done — do not re-litigate
- Not deployed / migration not applied on island yet

**Fence out:** payment/loot starts on home; re-writing classify logic; unbounded ghost-town fix as same Goal.

**Failure modes this example forced us to add to v1.0 tighten:**

1. Missing **Prior state** → cold agent re-builds shipped work  
2. Orthogonal outage mixed into Goal → Fence + separate card  

If a future dry-run fails either check, bump generator version and patch paste twin + this file together.
