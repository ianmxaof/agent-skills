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

---

## Phase 3 — DONE (directive complete)

### Done

- **Compose mapping note:** `references/compose-mapping.md` maps `powercore-website-clone` (BRIEF/TOKENS/MOTION), `powercore-website-feature-scan` (FEATURES/STACK) and `powercore-site-map-tree` (tree/flow-nav card) into envelope items: `kind`, `id` pattern, `value` shape, clean-vs-deep gate, confidence mapping (observed→high, inferred→medium/low, unknown→no item). No scrapers added or touched.
- **Dry brief:** `evals/fixtures/example_brief.md`, generated from the baseline + candidate fixtures by new `scripts/render_brief.py` (pure, deterministic; follows the Output Contract headings; Check delta only when a candidate is supplied, otherwise "Awaiting build — Not scoring"). Result for the fixtures: **FAIL, 2/4 rows pass**.
- **Drift guard:** a test regenerates the example and compares (CRLF-normalized), so the example cannot silently rot.
- **Locked semantics untouched:** `evidence_envelope.py` has zero diff this phase — extras still pass, only `kind` + `value` compared. The mapping note restates both as ground rules.
- Surfaces: Cursor SKILL (Procedure steps 5–7, status v0.1.3), Claude twin, GPT paste step 5 carry the mapping/render pointers.
- Hub `/run`, craft-anything, push, bots, `.env`, TBCC `CURRENT_DIRECTIVE.md`: not touched.

### Files touched (agent-skills)

| Path | Change |
|------|--------|
| `.cursor/skills/powercore-cleanroom-brief/references/compose-mapping.md` | add |
| `.cursor/skills/powercore-cleanroom-brief/scripts/render_brief.py` | add |
| `.cursor/skills/powercore-cleanroom-brief/evals/fixtures/example_brief.md` | add (generated) |
| `.cursor/skills/powercore-cleanroom-brief/tests/test_evidence_envelope.py` | +3 tests (13 total) |
| `.cursor/skills/powercore-cleanroom-brief/SKILL.md` | Procedure + status |
| `.claude/skills/powercore-cleanroom-brief/SKILL.md` | steps 5–6 |
| `docs/gpt-paste/POWERCORE_CLEANROOM_BRIEF_GPT_PASTE.md` | step 5 mapping |
| `docs/handoffs/CURRENT_DIRECTIVE.md` | Cursor's Phase 3 pointer |

Out-of-repo, uncommitted (same edit as Phase 2): identical Claude twins in `telegram_bot2/.claude/skills/powercore-cleanroom-brief/SKILL.md` and `powercore-ops/.claude/skills/powercore-cleanroom-brief/SKILL.md` — both now carry Phase 2 + Phase 3 twin edits.

### Verification

```text
py -3.13 -m pytest .cursor/skills/powercore-cleanroom-brief -x -q --tb=short
.............                                                            [100%]
13 passed

py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-cleanroom-brief --check
surfaces powercore-cleanroom-brief: ok
```

### Judgment calls for Cursor to confirm (mapping policy, not delta semantics)

- **Deep-only gate** for stack rows, DOM-id/API-evidenced features, and sitemap/robots/BFS routes — conservative reading of "clean = no source/JS reads"; written as "operator may relax".
- **Item id/kind vocabulary** (`layout, structure, color, font, spacing, motion, feature, stack, nav, route`) is a convention in the note, not enforced by `validate_item` (kind remains free-form).
- Brief's "Stack / structure notes" is a fixed placeholder; nothing infers a stack from evidence.

### Risks

- Mapping is documentation only: no code converts `TOKENS.md`/`FEATURES.md` into records yet — the brief agent does it by hand per the note.
- `render_brief` shows values as sorted-key JSON, so large values make wide table cells.

### STOP

Directive complete after Cursor `/cc-report` ACK. Pending on the operator's side only: committing the two out-of-repo twin copies, and any push.
