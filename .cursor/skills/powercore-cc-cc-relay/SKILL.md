---
name: powercore-cc-cc-relay
description: >-
  Claude Code ↔ Claude Code ACK/handoff when Cursor usage is dark — Planner
  session reviews *_report.md and emits PASTE INTO CC-GRINDER; Grinder executes
  phases and emits PASTE INTO CC-PLANNER. Invoke with /cc-cc, /cc-pair,
  /cc-cc-relay, CC to CC handoff, two Claude sessions, Cursor usage gone,
  paste bridge without Cursor, or Planner/Grinder relay. Same disk contract as
  CC Relay; fence labels swap roles. Prefer this over ad-hoc dual-CC chat.
  Never emit PASTE INTO CURSOR while this skill is active.
---

# PowerCore CC↔CC Relay (v1.2)

Changelog: v1.2 — Planner ACK asks the inverse-confidence question; each Grinder phase names ONE external verify command. v1.1 — forbid emitting `PASTE INTO CURSOR` under this skill; sticky roles; operator courier checklist; mid-switch from Cursor clarified. v1.0 — Planner/Grinder failover.

## Purpose

- Keep **Cursor-quality** phase gates when Cursor Pro usage is exhausted.
- Two Claude Code sessions play **Planner** (judgment/ACK) and **Grinder** (execute).
- Operator **blind-pastes** fences between **labeled** windows.
- Disk `*_report.md` remains source of truth.

**Not** a replacement for Cursor↔CC when Cursor has quota.

## The failure mode this version fixes

`tbcc-cc-run` / CLAUDE.md train Grinder to emit `PASTE INTO CURSOR`. Under CC↔CC that label is wrong: it sounds like “go back to Cursor,” and any CC session that *receives* it (via the old alias) flips to **Planner** — including the Grinder window if the operator pastes there. Result: two Planners, no Grinder, mid-switch chaos.

**Rule:** while `/cc-cc` is active, **never emit** `PASTE INTO CURSOR` or `PASTE INTO CLAUDE CODE`. Emit only `PASTE INTO CC-PLANNER` / `PASTE INTO CC-GRINDER`.

## Roles (sticky)

| Role | Does | Does not |
|------|------|----------|
| **Planner** | Read report + git; emit `PASTE INTO CC-GRINDER` | Implement phases; push; Start bots |
| **Grinder** | One phase; write `*_report.md`; emit `PASTE INTO CC-PLANNER` | Re-author Goal; start next phase without ACK |

**Sticky role:** once this session has declared `Role: Planner` or `Role: Grinder` this thread, **do not flip** because a fence arrived. If the operator pastes a Planner-bound fence into a Grinder window (or the reverse), reply with one line:

```text
Wrong window for this fence. Paste PASTE INTO CC-PLANNER into the Planner session (not here). I stay Grinder.
```

Do **not** silently become Planner.

### How a session learns its role

1. Operator says `/cc-cc` + `you are Planner` or `you are Grinder`, **or**
2. First paste this session: `PASTE INTO CC-GRINDER` → this session is Grinder; `PASTE INTO CC-PLANNER` → this session is Planner
3. Mid-switch from Cursor: operator pastes once into **each** window: `Role: Planner — /cc-cc` and `Role: Grinder — /cc-cc` before continuing

## Fence labels (locked — emit these only)

| Direction | First line |
|-----------|------------|
| Grinder → Planner | `PASTE INTO CC-PLANNER` |
| Planner → Grinder | `PASTE INTO CC-GRINDER` |

**Receive-only legacy** (do not emit): if you *see* `PASTE INTO CURSOR` while `/cc-cc` is active → treat as mislabeled Planner-bound STOP; **ask which window is Planner** if role is unset; if you are already Grinder → refuse role flip (wrong-window line above). Same for `PASTE INTO CLAUDE CODE` → mislabeled Grinder-bound ACK.

## Operator courier (required)

```
- [ ] Label two CC windows: PLANNER | GRINDER (rename tab / sticky note)
- [ ] After Grinder STOP: paste the fence ONLY into PLANNER
- [ ] After Planner ACK: paste the fence ONLY into GRINDER
- [ ] Never paste a STOP fence back into the same window that emitted it
```

Agents do not share chat memory. Pickup is **disk report + fence Do:**, not “continue the other transcript.”

## When to invoke

- `/cc-cc`, `/cc-pair`, Cursor usage gone, two Claude sessions, Planner/Grinder
- **Skip:** Cursor has quota → `cc-report` + `tbcc-cc-run` with Cursor fences

## Execution Profile

- Freedom: **low** on fence labels (exact); **medium** on Planner verdict
- Mode: Agent

## Harness attach

| Surface | Value |
|---------|-------|
| **MCP** | none |
| **Hooks** | endgates on Planner; silent-fail if Grinder touches Beat/deploy |
| **Memory** | disk forward + `*_report.md` only |
| **Compose** | Grinder habits from `tbcc-cc-run` but **fence labels overridden** by this skill |

## Behavioral rules

- Reason by: file + git
- Planner falsifies; Grinder executes `Do:`
- Override: this skill’s fence labels **win** over `tbcc-cc-run` / CLAUDE.md `PASTE INTO CURSOR` while `/cc-cc` is active
- Inverse confidence: every Planner ACK asks "which choices are you least sure of?" — put it to the Grinder (its STOP carries a `Least sure:` line) or, if absent, answer it yourself in the ACK
- Vertical slice: each Grinder phase names ONE external verify command, runs it, cites its output, then stops
- Avoid: role flip on legacy fences; dual implementers; chat-only continuity after Cursor→CC switch

## Output contract

### Grinder STOP

```text
PASTE INTO CC-PLANNER
/cc-cc-report
Report: tbcc/docs/handoffs/<stem>_report.md
Status: Phase N complete | blocked
HEAD: <hash or uncommitted>
Verify: <the one external command + its output>
Least sure: <low-confidence choice made this phase>
Do: review + ACK (paste PASTE INTO CC-GRINDER back into Grinder window)
Do not: assume Phase N+1 started
```

### Planner ACK

```text
PASTE INTO CC-GRINDER
Verdict: ACK | fix | wait
Report: tbcc/docs/handoffs/<stem>_report.md
Least sure: <Grinder's answer, or Planner's own if none given>
Do: <exact next>
Do not: push; start bots; touch .env; Phase N+2 unless listed
```

### Self-correct

1. Draft fence.
2. Check: first line is `PASTE INTO CC-PLANNER` or `PASTE INTO CC-GRINDER` — **never** `PASTE INTO CURSOR` / `PASTE INTO CLAUDE CODE`.
3. Revise once if wrong.

## Procedure

### Tickable — Planner

```
- [ ] 1. State Role: Planner (once)
- [ ] 2. Read *_report.md + git vs HEAD
- [ ] 3. Verdict ACK | fix | wait; ask/answer "which choices are you least sure of?"
- [ ] 4. Emit PASTE INTO CC-GRINDER only
- [ ] 5. Stop
```

### Tickable — Grinder

```
- [ ] 1. State Role: Grinder (once)
- [ ] 2. Honor PASTE INTO CC-GRINDER Do/Do not
- [ ] 3. One phase only; name ONE external verify command, run it, cite output
- [ ] 4. Append *_report.md
- [ ] 5. STOP with PASTE INTO CC-PLANNER (never PASTE INTO CURSOR)
```

## Mid-switch from Cursor (operator script)

1. Open / label PLANNER + GRINDER windows.
2. Into PLANNER: `Role: Planner. /cc-cc. Continue from report path: <path>`
3. Into GRINDER: `Role: Grinder. /cc-cc. Wait for PASTE INTO CC-GRINDER.`
4. If last STOP said `PASTE INTO CURSOR`, re-paste into **PLANNER** as:

```text
PASTE INTO CC-PLANNER
(report path and Status from the mislabeled fence — same body)
```

Or tell Planner: “Treat the pasted PASTE INTO CURSOR block as PASTE INTO CC-PLANNER; you are Planner; ACK with PASTE INTO CC-GRINDER.”

## Triple Surface

| Surface | Path |
|---------|------|
| Cursor | `agent-skills/.cursor/skills/powercore-cc-cc-relay/SKILL.md` |
| Claude | `<project>/.claude/skills/powercore-cc-cc-relay/SKILL.md` |
| GPT paste | `agent-skills/docs/gpt-paste/POWERCORE_CC_CC_RELAY_GPT_PASTE.md` |

## Exit conditions

- Next: courier pastes into the **other** labeled window
- Same window that STOPped must not auto-resume as the other role
