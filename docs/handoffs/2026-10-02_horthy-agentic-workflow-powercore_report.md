# Report — Horthy agentic workflow → PowerCore (CC↔CC)

Forward: `2026-10-02_horthy-agentic-workflow-powercore.md`

## Phase 0 — Planner review (2026-10-02)

Role: Planner. Predecessor `2026-10-02_agent-skills-toolset-exponential` closed: Planner close-out SHA fb28ee2 (8cbb85b Grinder Phase 4; powercore-ops twins 0176f1f).

### Verified on disk
- No hits for dumb-zone / compaction / tracer / inverse outside the forward file (H1/H3 gap confirmed).
- `.cursor/rules/` in agent-skills is untracked (13 files). `docs/handoffs/2026-10-02_horthy-...md` and `docs/proposals/2026-10-02_tip-budget-prune.md` have uncommitted edits.
- Git: `powercore-store`, `text-expander` have NO `.git` (confirmed). **New:** `vlc-skin` has `.git` but NO `origin` remote — add to the H7 backfill list. powercore-ops / agent-skills / notes-app have origin.
- `measure_tip_budget` counts a rule via regex `^alwaysApply:\s*true$` (metrics.py). Glob-scoping must flip the frontmatter to `alwaysApply: false` + `globs:`, or the file still counts and the "total dropped" check will not move.
- Catalog/rank do not read tips, so `run_rank_evals`/`endgates open-skills:` CANNOT regress from a tip edit. They remain required smoke checks (they guard against accidentally touching skills/endgates), but the real per-commit checks are below.

### Verdicts
| id | verdict | note |
|----|---------|------|
| H1 | keep | Phase 1 doctrine + compaction checklist (<=15 lines) + thin stub CLI. |
| H2 | keep | Template line only; each phase names one external verify command. |
| H3 | keep | One required inverse-confidence question in Planner ACK contract. |
| H4 | keep | Stage->skill table in doctrine doc. |
| H5 | **APPROVED — implement** (amended how only) | See below. Not proposal-only; not re-asked. |
| H6 | keep as reject | JSON->XML rejected; zero format migrations. |
| H7 | keep, amend | Backfill list = powercore-store, text-expander, **vlc-skin (no origin)**. No remote created without per-product operator ACK. |

### H5 how-amendments (whether is locked)
1. **Commit A = baseline snapshot, pathspec only:** the 5 files `powercore-endgates`, `powercore-skill-versions`, `tbcc-cc-paste-bridge`, `powercore-token-hygiene`, `powercore-chat-contract` (.mdc), committed UNMODIFIED, so B–E are clean reviewable diffs and individually revertable. Do NOT `git add .cursor/rules/` wholesale (8 other rules stay untracked — mega-dirty-tree is out of scope). Also commit the two already-modified docs (forward file, proposal) by explicit path.
2. **B (skill-versions):** `alwaysApply: false` + `globs` covering the version-history paths (e.g. `.cursor/skills/*/evals/versions/**`, `tools/skill_gap/skill_versions.py`, `overnight_loop.py`). Confirm file drops out of `measure_tip_budget`.
3. **C–E (shorten):** keep behavior-bearing lines. paste-bridge: fence names + blind-paste + skill pointer. token-hygiene: keep endgates + rank-eval lines. chat-contract: pointer to powercore-ops/chat_contract/. Target token numbers are goals, not gates; do not cut semantics to hit them.
4. **Per-commit verify (B–E):** (a) `measure_tip_budget` snapshot, total strictly down from the pre-commit value; (b) frontmatter still parses (description + alwaysApply present, YAML valid); (c) `powercore-endgates.mdc` byte-identical to commit A; (d) `run_rank_evals --json` 13/13 exit 0; (e) `endgates --auto --plain` prints `open-skills:`. Any fail -> revert that commit, STOP for Planner.
5. Mark the proposal IMPLEMENTED (agent-skills); telegram_bot2 rows (`tbcc-silent-fail`, `tbcc-plain-language`) stay "handoff to Lane C". No telegram_bot2 file touched.

### Grind order (locked)
P1 = H1+H6 (doctrine + compaction); P2 = H2+H3 (vertical-slice + inverse prompt); P3 = H4+**H5 prune (pre-approved)**; P4 = H7 git gate.
Each phase must name one external stop in its report.

### Reject list
JSON->XML migration; lights-off factory; unbounded context dumps; any new always-on tip; incident->PR factory (deferred); mega dirty-tree cleanup; blind remote creation; new mega-skill.

## Phase 1 — Grinder (2026-10-02)

H1 + H6 only. No tip/rule file touched, no telegram_bot2 file touched, nothing pushed.

### Delivered
- `docs/POWERCORE_AGENTIC_WORKFLOW.md`: Horthy point → existing surface table (lights-off → silent-fail + Planner peek + ship-gate/no-done-without-external-stop; four-stage → entropy-scan → directive-generator → phase grind, table deferred to P3; tracer bullet → one phase = one slice = one external verify command; dumb zone → compaction; inverse prompt → Planner ACK / Grinder STOP low-confidence question, wording deferred to P2; bottleneck → tip prune). Reject list (JSON→XML, lights-off, unbounded dumps, new always-on tip, incident→PR deferred, mega dirty-tree, blind remote creation, mega-skill) and the note that tip prune never touches the skill catalog.
- 10-line compaction checklist in the same doc.
- `tools/skill_gap/compact.py`: dated stub writer (`.skill-gap/compacts/` gitignored by default, `--out-dir` override, never overwrites, `-2` suffix on collision); cites `tbcc-auto-crystallize` and `*_report.md` as the habits it wires to.
- `tests/test_skill_gap.py`: +2 tests (stub name/contents/no-overwrite; CLI prints path).

### External stop (output)
- `rg -n -i "dumb.?zone|compaction|tracer|inverse" docs/POWERCORE_AGENTIC_WORKFLOW.md` → hits in the table + checklist (the directive's case-sensitive pattern only matches line 39 "inverse prompt" in the new doc; the doc capitalizes the others).
- Compaction CLI: `py -3.13 -m tools.skill_gap.compact --goal "Phase 1 smoke" --done "doc+cli" --next "Phase 2" --verify "pytest tests -q"` → `...\.skill-gap\compacts\2026-10-02_0256_compact_phase-1-smoke.md` (gitignored: `.gitignore:5 .skill-gap/`).
- `pytest tests -q` → 54 passed. `run_rank_evals --json` → 13/13, hit_rate 1.0.

### Low-confidence choice (inverse prompt)
I made the CLI a pure stub writer (fields supplied via flags) instead of auto-summarizing the session or reading git state, because the tool cannot see the conversation and guessing would invent "done" evidence. Trade-off: the agent must fill `--done/--next`, so a lazy invocation yields TODO placeholders. Also unsure whether the default dir should be gitignored `.skill-gap/compacts/` vs tracked `docs/handoffs/`; I chose ignored to avoid commit noise.
