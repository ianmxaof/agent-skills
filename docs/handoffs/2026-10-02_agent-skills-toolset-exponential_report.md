# Report — agent-skills toolset exponential (CC↔CC)

Forward: `2026-10-02_agent-skills-toolset-exponential.md`

## Phase 0 — Planner review (2026-10-02)

Role: Planner. Verified against disk, not the entropy summary.

### Verified facts
- Goldens: 4 (confirmed). Skills: 43 = 7 powercore + 26 tbcc + 10 other (confirmed).
- endgates.jsonl: 168 rows, 17 `skill_gap_suggest=true` (confirmed).
- **Falsified premise (I1):** endgates rows (168 metric log lines in `.skill-gap/metrics/endgates.jsonl`) have keys `ts, skipped, lines, ranked_top, crystallize_tier, skill_gap_suggest, tip_budget_tok` only. **No structured `proposed_slug` or `score` field.** However, all 17 suggestions embed the slug in the free-text `lines` field (e.g., `"Skill gap suggested (N) -> powercore-…"`), so a one-shot parse can backfill a pending list. **Going forward, structured logging of `proposed_slug` and score is the real fix** — enables incremental pending-proposals surface and trend metrics.
- `tip_budget.json`: 3063 tok, 8 files, `over_single` per-file true for the large ones; cumulative OK. Several over-cap tips live in `telegram_bot2/.cursor/rules/` (tbcc-silent-fail, tbcc-plain-language), outside agent-skills.
- Triple Surface `--check`: all three report `missing`. Not Cursor-only as stated: `powercore-token-audit` Claude twin already exists in `telegram_bot2/.claude/skills/`; missing are agent-skills/powercore-ops copies and GPT pastes. Check expects Claude copies under telegram_bot2, powercore-ops, agent-skills + `docs/gpt-paste/POWERCORE_*_GPT_PASTE.md`.
- Handoff said `tools/` is untracked (`?? tools/`) — confirmed; whole tree uncommitted.

### Verdicts
| id | verdict | note |
|----|---------|------|
| I1 | **amend** | Phase 1 must first make `gate.py` **log `proposed_slug` + `score`** to endgates rows (and/or write `.skill-gap/pending.jsonl`), then add the pending CLI over *new* rows. Historical 17 are recoverable from free-text `lines` field if needed (backfill parse); note path in report. Slugify: reject `untitled`, bare `gap`, empty stems. Fix keyword fallback so single generic words (`gap`, `vault`, `report`, `fail`) don't alone mint `powercore-<word>`. |
| I2 | keep | ≥12 goldens, ≥2 near-miss skips, one TBCC-only case that must not steal powercore top1. |
| I3 | keep (thin) | Histogram of `ranked_top` + suggest rate over last N rows. Cannot show "skills actually opened" — state that limit; don't invent a counter. |
| I4 | **amend** | Scope is "add agent-skills + powercore-ops Claude copies and GPT pastes"; token-audit Claude twin already in telegram_bot2. Use `--skip-cursor`; don't overwrite existing twins with divergent content (diff first). |
| I5 | keep as **NO for now** | See below. |
| I6 | keep as **proposal only** | See below. |
| I7 | keep | Doctrine paragraph only. |

### Grind queue (4 phases)
1. **Phase 1** — I1 (log proposed slug+score, slugify hardening, pending CLI, ACK→scaffold one-liner in skill-gap SKILL). First because it fixes data capture that I3 also relies on.
2. **Phase 2** — I2 + I3 thin.
3. **Phase 3** — I4 backfill.
4. **Phase 4** — I6 prune *proposal* doc + I7 doctrine paragraph (no apply).
Commit `tools/skill_gap/` in reviewable slices per phase (Phase 1 commit includes the untracked baseline only if Grinder confirms nothing secret/generated; exclude `__pycache__`, `.skill-gap/metrics` data).

### Explicit calls
- **I5 `powercore-skill-improve`: NO now.** Close the ACK loop and goldens first; a wrapper over `improve_once`/`overnight_loop` before rank evals are meaningful would mutate skills against a 4-case yardstick. Instead document a compose edge in skill-gap SKILL (Phase 1) pointing at those tools. Revisit after Phase 2 goldens ≥12.
- **I6 prune: LATER (proposal only).** Grinder writes the list of over-cap alwaysApply tips (which are agent-skills vs telegram_bot2-owned) in Phase 4; no demotion applied. Not touching telegram_bot2 rules.
- **Not universalized:** no `tbcc-*` rewrites or renames, no TBCC done-conditions removed, no new always-on tips, no auto-scaffold/auto-ACK, `CURRENT_DIRECTIVE.md` untouched.

---

```
PASTE INTO CC-GRINDER
Verdict: go — Phase 1 only
Report: agent-skills/docs/handoffs/2026-10-02_agent-skills-toolset-exponential_report.md (Phase 0 notes appended)
Forward: agent-skills/docs/handoffs/2026-10-02_agent-skills-toolset-exponential.md
Do: You are GRINDER under /cc-cc. Role: Grinder. Run Phase 1 only (I1, amended), cwd agent-skills.
  1. Amendment: endgates.jsonl rows do NOT have a structured `proposed_slug` or `score` field yet. In tools/skill_gap/gate.py + endgates.py, add structured logging of `proposed_slug` and `score` on each suggest row (and/or .skill-gap/pending.jsonl). This enables the pending-proposals CLI and trend metrics going forward. Historical 17 rows can be recovered from the free-text `lines` field if needed (one-shot backfill parse); note the recovery path in Phase 1 report.
  2. Harden _slugify_proposal: reject `untitled`, bare `gap`, empty stems; generic single keywords (gap/vault/report/fail) alone must not mint powercore-<word>. Add pytest cases in tests/test_skill_gap.py.
  3. Add a pending-proposals CLI over the new structured log (dedupe slug, max score, count, last_seen); dry-run it and cite output.
  4. Document the ACK→`scaffold_surfaces` one-liner and a compose-edge note to improve_once/overnight_loop in the skill-gap SKILL.md (no auto-write; no powercore-skill-improve scaffold).
  5. Verify: py -3.13 -m pytest tests/test_skill_gap.py -x -q --tb=short; py -3.13 -m tools.skill_gap.run_rank_evals --json.
  6. Commit this slice only. Exclude __pycache__, .skill-gap/metrics data, and any secrets or .env. Confirm those exclusions before committing the untracked tools/ baseline.
  7. Append "Phase 1" section to the report, then STOP.
Do not: start Phase 2+; auto-ACK or scaffold any skill; touch telegram_bot2 CURRENT_DIRECTIVE.md or telegram_bot2 rules; rename tbcc-*; emit PASTE INTO CURSOR or PASTE INTO CLAUDE CODE.
Stop with: PASTE INTO CC-PLANNER fence naming the report path, files changed, test output, commit SHA.
```

## Phase 1 — Grinder (2026-10-02)

Role: Grinder. Commit `db45776` (agent-skills, 26 files; tools/skill_gap baseline + slice).

### Changes
- `tools/skill_gap/gate.py`: `is_valid_slug()`; `_slugify_proposal` now returns `""` (never `powercore-untitled`); single generic keywords (gap/vault/report/fail/silent) alone no longer mint a name; name collision fallback → `""`; `suggest_line` shows "(no slug - name it on ACK)".
- `tools/skill_gap/metrics.py`: suggest rows in `endgates.jsonl` now carry `proposed_slug` + `score`.
- `tools/skill_gap/pending.py` (new): aggregates slug → count / max score / last_seen; `--legacy` recovers the 17 historical rows by parsing `Skill gap suggested (N) -> <slug>` from free-text `lines`; `--json`, `--last N`. Read-only.
- SKILL.md (Cursor canonical + Claude twin): "Pending proposals → ACK → scaffold" section with the `scaffold_surfaces` one-liner and manual compose edge to `improve_once`/`overnight_loop`. No `powercore-skill-improve`.
- `tests/test_skill_gap.py`: +9 cases (7 slug rejects, accept, log row, pending aggregate).

### Verification
- `pytest tests/test_skill_gap.py -x -q`: **25 passed**.
- `run_rank_evals --json`: golden passed 4/4, hit_rate 1.0 (invoke-miss log rolling hit_rate 0.929).
- `pending` (structured only): `pending: none` (expected; no new rows yet).
- `pending --legacy`:
  - powercore-eval n=2 max=68; powercore-vault-feeds-models 1/51; powercore-paste-handoff 1/48; powercore-ops 1/40; powercore-store 1/40.
  - Legacy rows with `powercore-untitled`/other invalid slugs were filtered out.
  - Note: `powercore-ops` / `powercore-store` look like repo-name artifacts, not procedures — Planner may want to treat as noise.

### Commit hygiene
Staged only: `tools/__init__.py`, `tools/skill_gap/**`, `tests/test_skill_gap.py`, two skill-gap SKILL.md. Confirmed no `__pycache__`, `.skill-gap/` (gitignored, check-ignore verified), `.env`, sessions, or secrets (grep clean). **Left untracked** (out of scope): `tools/ship_gate`, `tools/product_qualify`, `tools/ux_prefs`, other tests, `.cursor/skills/powercore-skill-gap/evals/versions/*`, and the remaining ~77 repo-wide changes.

### Caveats
- Several tests depend on skills still untracked in this repo (catalog/evals); a clean checkout of this commit alone won't pass them until those land.
- Pre-existing `endgates.jsonl` rows were not rewritten (log is gitignored); recovery is via `--legacy`.

## Phase 1 — Planner ACK (2026-10-02)

Verified on disk: commits db45776 + 0b6e581 present; 25 pytest pass; `pending --legacy` works; `is_valid_slug` rejects untitled/bare-generic/non-powercore.

**Verdict: ACK Phase 1. Phase 2 go, with two amendments.**
1. Add `ops`, `store` (repo-name noise) to the generic-stem reject set in gate.py, with a test; re-run `pending --legacy` and cite that the two rows disappear. Small fold-in, same files as Phase 2 touches.
2. Clean-checkout caveat: do not fix by sweeping untracked trees in. In Phase 2 report list which tests depend on untracked files; Phase 3 commits ship_gate/product_qualify/ux_prefs with their twins.
Phase 2 stays: goldens ≥12 (powercore-promo-capture, product-qualify, ux-prefs, near-miss "thanks", store/ship, TBCC-only case not stealing powercore top1, ≥2 near-miss skips), honest failure/miss logging in run_rank_evals, thin utilization CLI (last-N ranked_top histogram + suggest rate; state it can't show skills actually opened). Goldens must be written from desired behavior, not tuned to pass: if a case fails, report it, do not weaken the case or edit ranking code to fit.

## Phase 2 — Grinder (2026-10-02)

Commit `0fb3d7d`. Files: tools/skill_gap/gate.py (ops/store generic), tools/skill_gap/utilization.py (new), tools/skill_gap/evals/rank_skills_cases.json (4 → 13), tests/test_skill_gap.py (+5 → 30 tests).

- **Fold-in:** `ops`,`store` added to generic stems + pytest. `pending --legacy` now lists only powercore-eval (2/68), powercore-vault-feeds-models (1/51), powercore-paste-handoff (1/48); powercore-ops / powercore-store gone.
- **Goldens (13):** added promo-capture, product-qualify, ux-prefs, store-preactivate (ship-gate), token-audit, skill-gap-ack, tbcc-only-sitrep (must not steal powercore), 2 near-miss skips (thanks!, okay got it) + original trivial-thanks.
- **Rank eval result: 12/13, hit_rate 0.923, exit 1. FAILING GOLDEN: `near-miss-got-it` (prompt "okay, got it") → actual top1 = `tbcc-auto-crystallize`, expected no skill.** Not weakened, ranking code untouched. Cause is likely that the skip regex only matches single-word acks, so "okay, got it" with a long-ish response isn't treated as trivial. Planner decides whether to fix ranking in a later phase.
- **Honesty (step 2):** run_rank_evals already exits 1 on any miss, prints passed/total, and logs each case to invoke_miss.jsonl; added a test that a bad case returns exit 1 (miss log redirected to tmp).
- **Utilization CLI:** `py -3.13 -m tools.skill_gap.utilization --last 50` → skipped=24, suggest=3 (rate 0.06); top ranked: cc-report 4, powercore-product-qualify 4, tbcc-auto-crystallize 4, powercore-skill-gap 4, powercore-ux-prefs 3, … Output states it shows what was *ranked*, not skills actually opened.
- **pytest:** tests/test_skill_gap.py 30 passed.
- **Clean-checkout caveat:** tracked skills in git are only powercore-promo-capture, powercore-skill-gap, tbcc-entropy-scan. Depending on untracked skill dirs: 11 of the 13 goldens' skills (tbcc-auto-crystallize, tbcc-silent-fail, powercore-ship-gate, powercore-product-qualify, powercore-ux-prefs, powercore-token-audit, tbcc-sitrep, + trivial cases rely on catalog), test_catalog_loads_skills (cc-report), test_evals_cc_report_pass, test_body_assertions_cc_report, test_evals_silent_fail_pass, test_gap_skips_strong_near_miss (silent-fail), plus any rank test run via run_rank_evals. Untracked trees NOT committed this phase.

## Phase 2 — Planner ACK (2026-10-02)

Verified: 0fb3d7d + 44ac844 present; 30 pytest pass; run_rank_evals reproduces 12/13, hit_rate 0.923, exit 1; sole miss is near-miss-got-it (top1 tbcc-auto-crystallize, score 0.0691).

**Verdict: ACK Phase 2. Failing golden is a real bug, not a bad case — keep the case unchanged and fix the skip logic as a Phase 3 prelude.**
Root cause confirmed: `_SKIP_RE` in rank_skills.py and endgates.py is anchored `^(word)\.?!?\s*$`, so "okay, got it" (compound ack) falls through. The regex is duplicated in both files, so fix once and share.
Fix constraints: allow compound acks (ack-words joined by `,` / `and` / space), bounded to short prompts; must NOT skip substantive prompts that start with an ack ("okay, run the deploy", "yes, and also fix X"). Add positive + negative pytest cases. Do not touch scoring/boosts.
Phase 3 (I4): proceed as amended in Phase 0 (agent-skills + powercore-ops Claude copies + GPT pastes via --skip-cursor; diff before touching existing twins; token-audit twin exists in telegram_bot2). Because only 3 skills are tracked, Phase 3 also commits the dependent untracked trees (ship_gate, product_qualify, ux_prefs + their tests/skills) in separate reviewable commits; after that, re-check the clean-checkout list from the Phase 2 report and cite what remains.
