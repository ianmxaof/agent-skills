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

## Phase 1 — Planner ACK (2026-10-02)

Verified: b3afb93 present, explicit paths only (4 files); `pytest tests -q` 54 passed; doc reviewed — table maps to existing surfaces, reject list complete, tip-prune/catalog note present, checklist 10 lines. Case-sensitivity note on the rg pattern accepted (doc capitalizes; use `rg -i` going forward).

**Verdict: ACK Phase 1. Phase 2 go (H2 + H3).**
Inverse-prompt answers: (1) stub writer stays a pure flag-fed writer — correct, an auto-summarizer would invent "done" evidence; the TODO-placeholder cost is acceptable and visible. (2) Default `.skill-gap/compacts/` (gitignored) is right: durable facts go to crystallize / `*_report.md`; `--out-dir docs/handoffs` stays the opt-in.

Phase 2 amendments:
1. `powercore-cc-cc-relay` (Cursor SKILL, Claude twin, evals) and `directive-generator` are UNTRACKED in agent-skills. Same method as H5: commit A = the files unmodified by explicit path, then the patch as its own commit, so the edit is a reviewable diff. No `git add` of siblings.
2. Smallest surface only: relay SKILL + its Claude twin get (a) Planner ACK must ask the inverse-confidence question ("which choices are you least sure of?") and (b) Grinder phase contract = one external verify command per phase. directive-generator gets ONE tracer-bullet verification line. Bump the relay changelog (v1.2) per skill versioning convention. Do not edit `powercore-cc-cc-relay.mdc` (no tip growth), do not touch telegram_bot2's `tbcc-directive-generator`, no mass skill rewrite.
3. If a GPT paste twin for the relay or directive-generator exists in docs/gpt-paste/, mirror the same sentence there; if not, say so and do not create one.
4. External stop: `rg -n -i "inverse|external (verify|stop)" .cursor/skills/powercore-cc-cc-relay .claude/skills/powercore-cc-cc-relay .cursor/skills/directive-generator`, relay skill's own evals still run (use its evals runner if one exists, else cite that none ran), `pytest tests -q`, `run_rank_evals --json` 13/13.

## Phase 2 — Grinder (2026-10-02)

H2 + H3 only. No tips, no telegram_bot2, nothing pushed.

### Commits
- `a28438c` baseline (UNMODIFIED): relay Cursor SKILL.md + evals/evals.json, relay Claude twin, directive-generator SKILL.md + evals/evals.json + body_assertions.json. Excluded: all `evals/versions/`, directive-generator `examples.md` (not an evals definition; left untracked).
- `56023a3` patch: relay SKILL (v1.1 → **v1.2**, changelog line), relay Claude twin (v1.2 + short section), directive-generator (one tracer-bullet clause on the Phases line), relay GPT paste (same two sentences). `.cursor/rules/*` untouched; no directive-generator paste twin; tbcc-directive-generator untouched.
- Note: `POWERCORE_CC_CC_RELAY_GPT_PASTE.md` was untracked, so the patch commit is its first commit (baseline carve-out only covered the skills).

### What changed
1. Inverse confidence: every Planner ACK asks "which choices are you least sure of?" — put to the Grinder (new `Least sure:` line in the Grinder STOP fence) or answered by the Planner in the ACK (new `Least sure:` line in the ACK fence); Planner tickable updated.
2. Vertical slice: each Grinder phase names ONE external verify command, runs it, cites output, stops (new `Verify:` line in STOP fence; Grinder tickable updated).
3. directive-generator Phases line: each phase is a thin end-to-end tracer-bullet slice with ONE external stop command.

### External stop
- `rg -n -i "inverse|external (verify|stop)" ...` → hits: relay Cursor SKILL lines 15/97/98/151, relay Claude twin 22/25, directive-generator 68, GPT paste 46/47 (all four surfaces).
- Relay evals: `run_evals --skill powercore-cc-cc-relay` → 3/3 PASS. directive-generator evals → ran (see output in session; no versions/results files written).
- `pytest tests -q` → 54 passed. `run_rank_evals --json` → 13/13, hit_rate 1.0.

### Low-confidence choice (inverse prompt)
I made the Grinder STOP carry `Least sure:` and `Verify:` as new fence lines (additive, existing eval assertions still pass) instead of only adding prose rules. Unsure whether Planner will want them as required fence fields versus guidance; extra lines lengthen every fence. Also unsure the baseline should have included `examples.md`.
