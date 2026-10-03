# Skill/Tip exposure analytics — report

Forward: `2026-10-03_skill-tip-exposure-analytics.md`

## Phase 0 — Planner (done)

**Locked:** Option A only. No skill-open/Read hook (Option B), no tip edits, no call counts.

**Module decision: extend `tools/skill_gap/utilization.py`** (no new `analytics.py`). Estimated +60–80 LOC, so it meets the "prefer extend" bar. The histogram and suggest-rate logic stays in `summarize()`, so there is no duplicate.

**Falsification of cards (checked against source):**

| id | result |
|----|--------|
| A1 | Confirmed. `utilization.summarize` and `metrics.measure_tip_budget` are separate with no join. |
| A2 | Partly met. `LIMIT_NOTE` exists, but it is printed only in plain mode, as a trailing line. It is in the JSON via `limit`, and plain mode has no top banner. Move the banner to the top of plain output. |
| A3 | Confirmed. `catalog.load_skill_catalog()` is not joined. |
| A4 | Partly met. `test_skill_gap.py:403` covers `summarize` and `LIMIT_NOTE`, but there is no empty-log test and no report test. |

**Gotchas for the Grinder:**
- `measure_tip_budget()` has a side effect: it writes `.skill-gap/metrics/tip_budget.json`. That is acceptable (it is the existing cache), but do not `git add` it. Check whether that path is gitignored.
- `measure_tip_budget` hardcodes absolute roots (`telegram_bot2`, `powercore-ops`). Tests must pass `rules_roots=` with a tmp dir and must not rely on the real tree.
- `load_skill_catalog` takes `repo_root`, and passing it changes `path` handling. Tests should pass a tmp root with a `skills/` dir.
- `ranked_top` is a single name per row (the top pick only). The never-ranked list means "never the top pick in the window", not "never ranked at all". Label it exactly that.
- Aliases: catalog has `tbcc-*` and `powercore-*` twins. Match `ranked_top` against name and aliases, or the never-ranked list will show false positives.

**Honesty banner (exact strings, required at the top of plain output and in the JSON `limit` field):**
- Rank ≠ open: `ranked_top` is what endgates RANKED, not skills opened (no opened-skill counter exists).
- Tips = exposure/cost (alwaysApply token estimate, chars÷4), not fires or call counts.

**Phase split (unchanged from forward):**
- Phase 1: A1, A2, A4. Add `build_report()` (calls `summarize` and `measure_tip_budget`), a `--report` flag, the top banner, `--plain` (also accept it as a no-op alias for the default), and tests for the happy path and the empty log.
- Phase 2: A3 (never-top-ranked list, capped at 20, alias-aware), tip table polish, and one compose line in the `powercore-skill-gap` SKILL under CLI.

**Verification command note:** the forward lists `tools.skill_gap.analytics`, which will not exist. The real entry point is `py -3.13 -m tools.skill_gap.utilization --report --last 100 --plain` (and `--json`).

Phase 0 STOP. Awaiting Grinder Phase 1.

## Phase 1 — Grinder (done)

**Commit:** `5169c08` — `tools/skill_gap/utilization.py`, `tests/test_skill_gap.py` only (pathspec commit; `.skill-gap/` is gitignored, so `tip_budget.json` is not staged).

**Pytest:** `py -3.13 -m pytest tests/test_skill_gap.py -x -q --tb=short -k "utiliz or exposure or report"` → 7 passed, 41 deselected.

**Added:** `build_report(last_n, rules_roots=None, log_path=None)`, `format_report()`, `TIP_NOTE`, `--report` and `--plain` flags (`--json` with `--report` emits the dict; the old no-flag path is unchanged). JSON keys: summary fields + `tips[{name,tok,over_single,path}]` + `total_tok` + `limit` (both banner lines).
New tests: happy path, empty/missing log (n=0, suggest_rate None), banner in plain + JSON `limit`; all use tmp rules roots only.

**CLI** (`--report --last 100 --plain`, first lines):
```
ranked_top = what endgates RANKED, not skills opened (no opened-skill counter exists).
Tips = exposure/cost (alwaysApply token estimate, chars/4), not fires or call counts.

last 100 endgates rows: skipped=51 suggest=5 (rate=0.05)
    7  powercore-skill-gap
    7  tbcc-silent-fail
    6  tbcc-auto-crystallize
    6  cc-report
    5  powercore-ux-prefs
    ...
alwaysApply tips (name | tok | over_single | path):
  tbcc-cc-paste-bridge.mdc | 248 | True | ...
  powercore-chat-contract.mdc | 229 | True | ...
  powercore-token-hygiene.mdc | 218 | True | ...
total alwaysApply tok: 1400
```

**Deviations:**
- `LIMIT_NOTE` reworded from "not skills actually opened" to the locked "not skills opened"; the existing assertion at `test_utilization_histogram_and_limit_note` was updated to match.
- `build_report` has an extra optional `log_path` arg (for tmp-log tests); signature is otherwise as specified.
- `--report` without `--plain` also prints plain text (plain is the default, `--plain` is a no-op alias).
- The real CLI reads the real `telegram_bot2`/`powercore-ops` rule roots (hardcoded in `measure_tip_budget`); tests do not.
- The report file itself is left uncommitted (the spec's pathspec was limited to the two code files).

Phase 1 STOP. Awaiting Planner ACK for Phase 2 (A3 + SKILL.md line).

## Phase 2 — Grinder (done)

**Commit:** see `git log -1` on this branch (message: "feat(skill-gap): never-top-ranked list + tip cap header"). Files: `tools/skill_gap/utilization.py`, `tests/test_skill_gap.py`, `.cursor/skills/powercore-skill-gap/SKILL.md`, this report.

**Pytest (full file):** `py -3.13 -m pytest tests/test_skill_gap.py -x -q --tb=short` → 51 passed.

**Added:** `never_top_ranked()` (catalog names minus histogram keys; alias- and case-insensitive; sorted, cap 20), `build_report(..., catalog_root=None)` → `never_top_ranked: {count, shown, names}` and `soft_cap_single`. Plain output: tip header now says "largest first" with the soft cap (200 tok); new section labeled exactly `never the top pick in the window (catalog skills not ranked_top in last N rows; NOT 'unused')`. Tests: alias match (`TBCC-Foo` ranked hides `powercore-foo`), cap (25 → shown 20, count 25), empty log lists all + label/cap in plain; all use tmp catalog roots.

**SKILL.md:** one compose line added under `## CLI` in `.cursor/skills/powercore-skill-gap/SKILL.md` (CRLF preserved). `.claude/skills/powercore-skill-gap/SKILL.md` has no CLI section, so no mirror was added.

**CLI snippet:**
```
alwaysApply tips, largest first (name | tok | over_single | path; soft cap/tip = 200 tok):
  tbcc-cc-paste-bridge.mdc | 248 | True | ...
  ...
total alwaysApply tok: 1400

never the top pick in the window (catalog skills not ranked_top in last N rows; NOT 'unused'): 29 (showing 20)
  claude-code-report
  github-seo-sentry
  handoff-claude-code
  ...
```
`--report --json` parses as valid JSON.

**Deviations:** none. The pre-existing dirty files (.gitignore, README.md, etc.) were not touched.

Phase 2 STOP.
