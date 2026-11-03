# Agent-skills toolset exponential improve — CC↔CC directive

**Track:** agent-skills selection / skill-gap closed loop / rank quality / Triple Surface  
**Repo cwd:** `C:\Powercore-repo-main\agent-skills`  
**Relay:** `/cc-cc` (Planner ↔ Grinder) — **not** Cursor `/cc-report` while this thread is active  
**Pointer:** do **not** overwrite `telegram_bot2/tbcc/docs/handoffs/CURRENT_DIRECTIVE.md` (still ACTIVE on caption-media-first)  
**Reverse:** `agent-skills/docs/handoffs/2026-10-02_agent-skills-toolset-exponential_report.md`  
**Entropy scan source:** Cursor 2026-10-02 agent-skills selection review (innovation lens)

---

## Goal

Make the agent-skills toolbox **choose better, grow on purpose, and get used** — without auto-minting junk skills or mass-rewriting every `tbcc-*` skill this pass.

Done when Planner can falsify or ACK this plan, Grinder lands the locked phases, and these external stops pass:

1. `py -3.13 -m tools.skill_gap.run_rank_evals --json` → hit_rate reported on **≥12** goldens (was 4)
2. Pending skill-gap proposals are queryable from disk (inbox or metrics summary), not only buried in `endgates.jsonl`
3. At least one real ACK→scaffold path documented + smoke-tested (`scaffold_surfaces --check`)
4. Triple Surface `--check` green for the three Cursor-only powercore skills named in Scope
5. Optional: `powercore-skill-improve` Triple Surface scaffold exists **only if** Planner ACKs Phase 4

---

## Scope

### In scope

- Selection quality: expand `tools/skill_gap/evals/rank_skills_cases.json`; tighten proposal slugify / near-miss skip UX in `gate.py`
- Skill-gap closed loop: pending-proposals surface + one-command ACK→`scaffold_surfaces` checklist/CLI glue (still **never auto-write** SKILL bodies without operator ACK)
- Triple Surface backfill: `powercore-ship-gate`, `powercore-token-audit`, `powercore-ux-prefs` (Claude twin + GPT paste via `--skip-cursor`)
- Utilization observability: thin summary CLI or metrics field for ranked_top / suggest rates (reuse `.skill-gap/metrics/`)
- Tip-budget prune **proposal** only (list which alwaysApply rules exceed soft 200 tok) — apply only if Planner ACKs
- Optional meta-skill `powercore-skill-improve` wrapping `improve_once` / `overnight_loop` / `skill_versions` (Planner gate)

### Out of scope

- Mass rename `tbcc-*` → `powercore-*`
- Auto-creating skills without operator ACK
- Overnight mutating every skill in one night
- Expanding always-on tip count before prune
- Island deploy / Start bots / `.env` / money mutate
- Touching `CURRENT_DIRECTIVE.md` caption track
- Rewriting TBCC product skills into “universal” fluff that loses TBCC done-conditions

---

## Prior state (verified 2026-10-02)

- Catalog is a **live filesystem scan** (`tools/skill_gap/catalog.py` `load_skill_catalog` + `nearest_skills`) — there is **no** separate global selection-index JSON; `evals/versions/index.json` is per-skill version history only.
- Endgates pipeline: crystallize → skill-gap → rank (`tools/skill_gap/endgates.py`); hooks in `.cursor/hooks.json`.
- `.cursor/skills/` count: **43** (≈7 `powercore-*`, ≈26 `tbcc-*`, ≈10 other).
- Triple Surface complete under agent-skills for only ~4 powercore skills; ship-gate / token-audit / ux-prefs Cursor-only.
- Endgates metrics: **167** rows, **17** `skill_gap_suggest=true`; proposed slugs include `powercore-untitled`, `powercore-vault`, `powercore-gap`, `powercore-paste-handoff` — almost none scaffolded.
- `improve_once` / `overnight_loop` / `skill_versions` rewrite **existing** skills only; new skills = `scaffold_surfaces` after ACK.
- Rank goldens: **4** cases in `rank_skills_cases.json` (hit_rate 1.0 is underpowered).
- Tip budget: **3063** tok / 6000; **6/8** alwaysApply tips over single-tip soft cap 200 (`tip_budget.json`).
- Naming lock already exists: prefer `powercore-*` for **new** skills; keep existing `tbcc-*` until deliberate migrate (`powercore-skill-gap` SKILL.md).

---

## Issue cards

| id | symptom | evidence | severity | depends_on | acceptance |
|----|---------|----------|----------|------------|------------|
| I1 | Skill-gap suggests but list does not grow | 17 suggests in `endgates.jsonl`; junk slugs `untitled`/`vault`/`gap` | P0 | none | Pending proposals listable; slugify rejects untitled/gap; ≥1 ACK→scaffold smoke path documented |
| I2 | Rank “100%” is fake confidence | only 4 cases in `rank_skills_cases.json` | P0 | none | ≥12 goldens covering powercore + notes/store/promo + ≥2 deliberate near-miss skips; `run_rank_evals --json` exits 0 |
| I3 | No utilization picture | endgates logs `ranked_top` only; no fire dashboard | P1 | none | CLI or metrics summary: top ranked skills + suggest rate over last N rows |
| I4 | Triple Surface incomplete | ship-gate, token-audit, ux-prefs lack Claude+GPT under agent-skills | P1 | none | `scaffold_surfaces --skill <name> --check` ok for all three |
| I5 | “Skill-improvements skill” may be needed | overnight/improve_once exist but no operator-facing skill wrapping them | P2 | I1,I2 | Planner verdict: scaffold `powercore-skill-improve` **or** document compose edge from skill-gap only |
| I6 | Tip tips over soft cap drown selection | tip_budget.json 6/8 over 200 | P2 | none | Written prune proposal (which tips → demote); no apply unless Planner ACK |
| I7 | TBCC-centrism confuses “unused” | 26/43 skills tbcc-*; endgates crystallize path TBCC-hardcoded | P2 | none | Doctrine note in report: keep tbcc-* for TBCC ops; new cross-product skills powercore-*; no mass rename |

---

## Constraints & gotchas

- **judgment_ceiling (Grinder):** MUST NOT invent new skill doctrine/pricing; MUST NOT auto-ACK scaffolds; MUST NOT flip `CURRENT_DIRECTIVE.md`.
- **judgment_ceiling (Planner):** MAY prioritize / drop I5–I6; MAY reject junk proposals; MUST keep never-auto-write.
- Fence labels while `/cc-cc` active: only `PASTE INTO CC-PLANNER` / `PASTE INTO CC-GRINDER` (`powercore-cc-cc-relay`).
- Prefer reversible slices; commit one phase at a time if Working agreement says so; never commit secrets.
- `tools/skill_gap/` may still be partially untracked — commit in reviewable slices when Grinder lands code.

---

## Verification

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.skill_gap.run_rank_evals --json
py -3.13 -m pytest tests/test_skill_gap.py -x -q --tb=short
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-ship-gate --check
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-token-audit --check
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-ux-prefs --check
# after I1: pending-proposals command or path cited in reverse report
```

---

## Working agreement

1. Operator opens **two** Claude Code windows labeled PLANNER | GRINDER; both `cd` to `agent-skills` (or read paths via absolute).
2. Planner runs **Phase 0** first (review/falsify); emits `PASTE INTO CC-GRINDER` with locked phase order.
3. Grinder executes **one phase**, appends reverse report, emits `PASTE INTO CC-PLANNER`.
4. No Phase N+1 without Planner ACK fence.
5. Stop conditions: Goal Verification green, or blocked on operator ACK for a real scaffold.

---

## Phases

### Phase 0 — Planner review pass (Planner only)

Falsify or ACK the Cursor entropy findings. Output in reverse report:

1. Verdict per issue card: keep / drop / amend
2. Ordered grind queue (≤5 phases)
3. Explicit call on I5 (`powercore-skill-improve` yes/no) and I6 (prune now/later)
4. Fence: what will not be universalized

Then emit `PASTE INTO CC-GRINDER` with `Do: Phase 1 only`.

### Phase 1 — Close skill-gap ACK loop (I1)

- Add pending-proposals surface (CLI preferred: read `endgates.jsonl` → dedupe suggested slugs + scores + last_seen)
- Tighten `_slugify_proposal` / reject list so `untitled`, bare `gap`, empty stems cannot ship as suggestions
- Document ACK→`scaffold_surfaces` one-liner in skill-gap SKILL (no auto-write)
- Verify: pytest + one dry-run pending list

### Phase 2 — Expand rank goldens + miss signal (I2, I3 thin)

- Grow `rank_skills_cases.json` to ≥12 cases (include powercore-promo-capture, powercore-product-qualify, powercore-ux-prefs, a near-miss “thanks”, a store/ship case, a TBCC-only case that must not steal powercore top1)
- Ensure `run_rank_evals` / miss log stay honest when cases fail
- Thin utilization summary: last-N ranked_top histogram + suggest rate (metrics.py or small CLI)

### Phase 3 — Triple Surface backfill (I4)

- `scaffold_surfaces --skip-cursor` for ship-gate, token-audit, ux-prefs into default Claude roots + `docs/gpt-paste/`
- `--check` all three green
- Sync rule noted in reverse report

### Phase 4 — Optional skill-improve + tip prune (I5, I6) — only if Planner ACK

- If yes on I5: Triple Surface scaffold `powercore-skill-improve` (procedure: improve_once → overnight → versions pin/rollback; never invent new skills)
- If yes on I6: apply tip prune list from Planner; else leave proposal only
- Doctrine paragraph for I7 in report (tbcc stay; powercore for cross-product)

---

## Target profile

| Field | Value |
|-------|--------|
| mode | Phase 0 Planner (judgment) → Phases 1–4 Grinder (Agent grind) |
| tools | filesystem + shell on `agent-skills` |
| judgment_ceiling | Planner MAY prioritize; Grinder MUST NOT doctrine-expand or auto-scaffold without ACK |
| context | ZERO prior chat — this file + reverse report only |

---

## Operator courier

```
- [ ] Label windows: PLANNER | GRINDER
- [ ] Paste this file path into PLANNER first: agent-skills/docs/handoffs/2026-10-02_agent-skills-toolset-exponential.md
- [ ] Planner Phase 0 → paste fence into GRINDER
- [ ] After each Grinder STOP → paste ONLY into PLANNER
- [ ] Leave CURRENT_DIRECTIVE.md (caption track) alone
```

---

## Compact review brief (for Planner Phase 0)

**What you already have:** live catalog scan + nearest_skills + endgates hooks. That is the “index.” Expanding it means better goldens + proposal quality + observability — not a second parallel skill list unless you invent one on purpose.

**Why the skill list barely grew:** skill-gap is **suggest-only by design**. 17 suggestions fired; slugs are often junk; ACK→scaffold almost never happened. Overnight/improve_once only polish existing skills.

**Why skills look unused:** ranking shows `ranked_top` in metrics, but there is no “which skills agents actually opened” counter. Many skills are TBCC-ops (sitrep, crew, silent-fail) — correctly unused on store/notes work. That is not failure; missing powercore coverage + weak rank goldens is.

**Universalize?** Prefer **new** cross-product skills as `powercore-*` + Triple Surface. Do not rewrite 26 tbcc skills into vague universals this pass. Keep TBCC done-conditions.

**skill-improvements skill?** Likely yes as a thin wrapper (`powercore-skill-improve`) if Planner wants operator-facing improve/overnight — but second to closing the ACK loop and goldens.
