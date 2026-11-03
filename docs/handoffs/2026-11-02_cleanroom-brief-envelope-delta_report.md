# Reverse report — cleanroom-brief envelope + delta

**Forward:** `docs/handoffs/2026-11-02_cleanroom-brief-envelope-delta.md`  
**cwd:** `C:\Powercore-repo-main\agent-skills`  
**Updated:** 2026-11-02

---

## Phase 1 — DONE

### Done

- Added `scripts/evidence_envelope.py` — TypedDict schema, `validate_*`, `load_record`, `dump_record`, `make_record`, `page_items`.
- Fixture: `evals/fixtures/evidence_baseline.json` (3 items, summary-first).
- Pytest: `tests/test_evidence_envelope.py` — 5 tests (load, round-trip, summary guard, paging, make_record).
- Cursor SKILL Procedure points at envelope module; Claude twins + GPT paste mention path/fields lightly.
- Did **not** implement `delta()` (Phase 2).

### Files touched

| Path | Change |
|------|--------|
| `.cursor/skills/powercore-cleanroom-brief/scripts/evidence_envelope.py` | add |
| `.cursor/skills/powercore-cleanroom-brief/evals/fixtures/evidence_baseline.json` | add |
| `.cursor/skills/powercore-cleanroom-brief/tests/test_evidence_envelope.py` | add |
| `.cursor/skills/powercore-cleanroom-brief/SKILL.md` | Procedure + status |
| `.claude/skills/powercore-cleanroom-brief/SKILL.md` (+ tb2 / ops copies) | module path note |
| `docs/gpt-paste/POWERCORE_CLEANROOM_BRIEF_GPT_PASTE.md` | procedure note |

### Verification

```text
py -3.13 -m pytest .cursor/skills/powercore-cleanroom-brief -x -q --tb=short
.....                                                                    [100%]
5 passed in 0.21s

py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-cleanroom-brief --check
surfaces powercore-cleanroom-brief: ok
```

### Risks

- Passphrase/secret-forge unrelated; no Hub wiring.
- Twin copies in telegram_bot2 / powercore-ops updated on disk — commit separately if desired.
- Summary must list existing item ids only (enforced).

### STOP

Await Cursor `/cc-report` ACK before Phase 2 (`delta()` + mismatch fixture).

---

## Phase 2 — DONE

### Done

- `delta(baseline, candidate, *, tolerance=0.0) -> list[{id, pass, note}]` in `scripts/evidence_envelope.py`, plus `all_pass(rows)`.
- Semantics (structural, no pixel ML): one row per **baseline** item in baseline order. Fail when the candidate lacks the id (`missing in candidate`), `kind` differs, or `value` differs (recursive dict/list compare; numbers within `tolerance`; note names the first differing path, e.g. `value.hex: '#1A1A1A' != '#222222'`). Candidate-only items append as `pass: true`, note `extra in candidate` (gate fails only on what the baseline recorded).
- Guards: empty baseline raises `ValueError` (cannot support a pass claim); negative tolerance raises; `all_pass([])` is False.
- Fixture pair: `evals/fixtures/evidence_baseline.json` vs new `evals/fixtures/evidence_candidate.json` → known **pass** (`layout-390`), **fail** (`palette-primary` hex changed; `font-ui` missing), **extra** (`extra-spacing`).
- Schema/`VERSION` untouched (record format unchanged).
- Phase 3 NOT started.

### Files touched

| Path | Change |
|------|--------|
| `.cursor/skills/powercore-cleanroom-brief/scripts/evidence_envelope.py` | `delta`, `all_pass`, helpers |
| `.cursor/skills/powercore-cleanroom-brief/evals/fixtures/evidence_candidate.json` | add |
| `.cursor/skills/powercore-cleanroom-brief/tests/test_evidence_envelope.py` | +5 delta tests (10 total) |
| `.cursor/skills/powercore-cleanroom-brief/SKILL.md` | Procedure step 4 + Status v0.1.2 |
| `.claude/skills/powercore-cleanroom-brief/SKILL.md` | step 4 points at `delta` / `all_pass` |
| `docs/gpt-paste/POWERCORE_CLEANROOM_BRIEF_GPT_PASTE.md` | step 4 delta contract |
| `docs/handoffs/CURRENT_DIRECTIVE.md` | Cursor's Phase 2 pointer (was already modified on disk) |

### Out-of-repo (uncommitted, not part of this commit)

Same one-line step-4 edit applied to the identical Claude twins in `telegram_bot2/.claude/skills/powercore-cleanroom-brief/SKILL.md` and `powercore-ops/.claude/skills/powercore-cleanroom-brief/SKILL.md` (those repos have unrelated dirt; commit separately if desired).

### Verification

```text
py -3.13 -m pytest .cursor/skills/powercore-cleanroom-brief -x -q --tb=short
..........                                                               [100%]
10 passed

py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-cleanroom-brief --check
surfaces powercore-cleanroom-brief: ok
```

### Decisions for Cursor to confirm (judgment calls)

- Candidate-only items pass (as `extra`) rather than fail. Easy flip if you want strict-set equality.
- `confidence`/`coverage`/`limits` are not compared — only `kind` + `value`.

### Risks

- Value compare is exact type + equality for non-numerics (`"1"` vs `1` fails); numeric tolerance is one global float, not per-kind.
- No Hub wiring, no captures, no network.

### STOP

Await Cursor `/cc-report` ACK before Phase 3 (compose mapping + dry brief card).
