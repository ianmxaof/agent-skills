# Skill/Tip exposure analytics — CC↔CC directive (Option A)

**Track:** agent-skills observability — exposure report (rank ≠ open)  
**Repo cwd:** `C:\Powercore-repo-main\agent-skills`  
**Relay:** `/cc-cc` (Planner ↔ Grinder)  
**Operator pick:** Entropy scan Option **A** — exposure report CLI only (no skill-open hook)  
**Pointer:** do **not** overwrite `telegram_bot2/tbcc/docs/handoffs/CURRENT_DIRECTIVE.md` (caption track still ACTIVE)  
**Reverse:** `agent-skills/docs/handoffs/2026-10-03_skill-tip-exposure-analytics_report.md`

---

## Goal

Add a single **Skill/Tip exposure report** CLI under `tools.skill_gap` that joins existing endgates + tip_budget data so the operator can see how often skills are **ranked** and which tips are **always-on expensive** — without claiming false “call counts.”

Done when:

1. `py -3.13 -m tools.skill_gap.analytics --last 100 --plain` (name may be `analytics` or extend `utilization` — Planner picks smallest surface) prints:
   - Top skills by `ranked_top` frequency (last N endgates rows)
   - Suggest rate (skill_gap_suggest)
   - Skills in catalog that never appear in `ranked_top` over that window (never-ranked sample, capped)
   - Tip exposure table: alwaysApply tip name · tok · over_single · path (from `measure_tip_budget`)
2. Docs / module docstring state clearly: **rank ≠ open**; tips = exposure/cost, not fires.
3. `--json` works; pytest covers summarize helpers (happy path + empty log).
4. `utilization.py` either becomes the thin backend or is called by the new module — no duplicate histogram logic.

---

## Scope

### In scope

- Reuse `endgates.jsonl` + `measure_tip_budget()` + `load_skill_catalog()`
- CLI + short note in `powercore-skill-gap` SKILL.md (one compose line) or `tools/skill_gap` README if one exists
- Tests in `tests/test_skill_gap.py` (or adjacent)

### Out of scope

- Skill-open / Read hooks (Option B — deferred)
- Claiming tip “call counts” or inventing telemetry to the cloud
- Tip prune / tip edits
- Mega dirty-tree commits; `git add -A`
- telegram_bot2 CURRENT_DIRECTIVE / island / bots
- Changing rank_skills / selection algorithms

---

## Prior state (verified framing)

- `tools/skill_gap/utilization.py` — ranked_top histogram + suggest rate; LIMIT note already correct.
- `tools/skill_gap/metrics.py` — `measure_tip_budget`, endgates log append.
- `tools/skill_gap/catalog.py` — `load_skill_catalog` for never-ranked join.
- Tip budget after Lane C prune ~1400 tok (2026-10-03); selection still via endgates.

---

## Issue cards

| id | symptom | evidence | severity | depends_on | acceptance |
|----|---------|----------|----------|------------|------------|
| A1 | No single report joining skill rank + tip cost | utilization vs tip_budget separate | P0 | none | One CLI prints both sections |
| A2 | Easy to misread rank as usage | utilization LIMIT_NOTE | P0 | none | Banner/doc every plain+json output |
| A3 | Never-ranked skills invisible | catalog not joined | P1 | A1 | Cap list (e.g. ≤20) of catalog names absent from ranked_top window |
| A4 | No test | — | P1 | A1 | pytest green for summarize |

---

## Constraints

- **judgment_ceiling (Grinder):** MUST NOT implement Option B hooks; MUST NOT rename “exposure” to “calls/usage” in user-facing strings; MUST NOT tip-edit.
- **judgment_ceiling (Planner):** MAY choose extend `utilization` vs new `analytics` module; MUST keep honesty banner.
- Fence labels: `PASTE INTO CC-PLANNER` / `PASTE INTO CC-GRINDER` only.

---

## Verification

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.skill_gap.analytics --last 100 --plain
# or: py -3.13 -m tools.skill_gap.utilization --report --last 100 --plain  (if Planner chose extend)
py -3.13 -m tools.skill_gap.analytics --last 100 --json
py -3.13 -m pytest tests/test_skill_gap.py -x -q --tb=short -k "utiliz or analytics or exposure"
```

Human: plain output must include the rank≠open note and a tip table.

---

## Working agreement

1. Planner Phase 0: falsify A1–A4; lock module name + phase split.
2. Grinder one phase at a time; reverse report; STOP for Planner.
3. Commit slice(s) with pathspecs only (tools/skill_gap + tests + thin skill note). No secrets / no metrics jsonl force-add unless already tracked pattern.

---

## Phases

### Phase 0 — Planner only

- Confirm Option A only (no open-hook).
- Pick: new `analytics.py` **or** extend `utilization.py` with `--tips` / full report (prefer extend if <~80 LOC added).
- Emit `PASTE INTO CC-GRINDER` Phase 1 only.

### Phase 1 — Core report (A1, A2, A4)

- Implement summarize + CLI + honesty banner + pytest.
- Dry-run `--plain` and cite snippet in report.

### Phase 2 — Never-ranked + tip table polish (A3) + skill compose line

- Catalog join (capped); tip_budget section; one line in `powercore-skill-gap` SKILL under CLI.
- Final verify; STOP.

---

## Target profile

| Field | Value |
|-------|--------|
| mode | Planner → Grinder |
| tools | filesystem + shell on agent-skills |
| judgment_ceiling | Grinder MUST NOT Option B / tip edits |
| context | ZERO chat — this file + reverse report |

---

## Operator courier

```
- [ ] Paste into PLANNER: agent-skills/docs/handoffs/2026-10-03_skill-tip-exposure-analytics.md
- [ ] Blind-paste PLANNER ↔ GRINDER only
- [ ] Leave CURRENT_DIRECTIVE.md alone
- [ ] Do not ask for Option B unless operator opens it
```
