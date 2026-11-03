# Cleanroom Brief — evidence envelope + delta gate

**Track:** agent-skills — `powercore-cleanroom-brief` v0.1 → runnable envelope  
**Repo cwd:** `C:\Powercore-repo-main\agent-skills`  
**TARGET:** Claude Code (grind)  
**Pointer:** do **not** overwrite `telegram_bot2/tbcc/docs/handoffs/CURRENT_DIRECTIVE.md` (other tracks)  
**Local pointer:** `agent-skills/docs/handoffs/CURRENT_DIRECTIVE.md`  
**Reverse:** `agent-skills/docs/handoffs/2026-11-02_cleanroom-brief-envelope-delta_report.md`

---

## ACTIVE for /cc-run

| Field | Value |
|-------|--------|
| **path** | `docs/handoffs/2026-11-02_cleanroom-brief-envelope-delta.md` |
| **status** | **ACTIVE** — Phase 1 only; STOP for Cursor `/cc-report` after reverse report |
| **active_phase** | Phase 1 |
| **updated** | 2026-11-02 |

---

## Goal

Ship a deterministic **evidence envelope + check-delta** for `powercore-cleanroom-brief`: capture items become records with `id, kind, value, confidence, coverage, limits`; a second capture produces a per-item pass/fail delta — without reimplementing website scrapers (compose existing skills).

Done when:

1. A small Python module (or script under the skill) can load/write an evidence record JSON (summary-first shape documented).
2. A `delta(baseline, candidate) -> list[{id, pass, note}]` function exists with ≥1 pytest.
3. Cursor `SKILL.md` Procedure points at the module; Claude twin + GPT paste mention the same contract in the same change set.
4. External stop: `py -3.13 -m pytest <test_path> -x -q --tb=short` exits 0.

---

## Scope

### In scope

- Evidence record schema + paging note (summary first)
- Delta comparator (structural, not pixel ML)
- Fixture JSON under skill `evals/` or `tests/`
- Triple Surface sync for contract wording only
- Compose docs: call out `powercore-website-clone`, `powercore-website-feature-scan`, `powercore-site-map-tree` as capture sources — do not rewrite them

### Out of scope

- Implementing full Hub `/run cleanroom-brief`
- Vendoring storytold/craft-anything Rust engine
- Screenshot capture / browser automation in this directive
- Pixel similarity ML / three-width live screenshot harness
- Money / Telegram / `.env` / island deploy / start bots
- Building `powercore-tool-*` or `secret-forge` further in this grind

---

## Prior state

- **verified:** Triple Surface skill packs on disk (`powercore-cleanroom-brief` Cursor + Claude ×3 + GPT paste); `--check` ok (2026-11-02).
- **do-not-re-litigate:** primary surface = compose existing scans; do not adopt craft-anything as runtime.
- **not-deployed:** no Hub registry entry; no envelope module yet — chat foundation only.
- Foundation source: Hub article-to-tool on storytold/craft-anything (Study → Build → Check).

---

## Issue cards

| id | symptom | evidence | severity | depends_on | acceptance |
|----|---------|----------|----------|------------|------------|
| I1 | No typed evidence envelope | skill Procedure is prose-only | P0 | none | JSON schema or TypedDict + load/dump round-trip |
| I2 | No check delta | skill Output Contract names Check delta but no code | P0 | I1 | `delta()` + pytest on fixture mismatch |
| I3 | Twin drift risk | Triple Surface exists | P1 | I1,I2 | Cursor + ≥1 Claude + GPT paste mention module path / contract fields together |
| I4 | No external stop | unknown prior tests | P0 | I2 | pytest exit 0 command documented in reverse report |

---

## Constraints & gotchas

- **judgment_ceiling:** MUST NOT invent Hub `/run` shipping, pricing, or doctrine; MUST NOT vendor craft-anything; MUST NOT start browsers/bots.
- Prefer pure functions + fixtures over live network.
- Clean vs deep mode is a **flag on the record**, not a scraper rewrite this phase.
- Freedom: medium — locked schema fields; implementation surface may vary.
- Paste bridge: end each phase with `PASTE INTO CURSOR` naming `/cc-report` + reverse path.

---

## Verification

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m pytest .cursor/skills/powercore-cleanroom-brief -x -q --tb=short
# if tests live elsewhere, document exact path in reverse report — still exit 0
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-cleanroom-brief --check
```

Observable: evidence fixture round-trips; delta flags at least one intentional mismatch as fail.

---

## Working agreement

- Commit one slice at a time under `agent-skills` only for this grind; no `git add -A` across monorepo dirt.
- Do not push unless operator says so.
- After each phase: write/append `docs/handoffs/2026-11-02_cleanroom-brief-envelope-delta_report.md`, then **STOP** for Cursor `/cc-report` ACK.
- Do not start Phase N+1 from a wait/fix ACK.

---

## Phases

### Phase 1 — Envelope schema + load/dump (THIS PHASE)

- Add module/script + fixture for evidence records (`id, kind, value, confidence, coverage, limits` + optional `mode`).
- Round-trip test.
- Verify: pytest for round-trip green.
- Reverse report + STOP.

### Phase 2 — Delta gate (after ACK only)

- Implement `delta(baseline, candidate)`.
- Fixture with known pass + fail items.
- Point SKILL Procedure at delta; sync twins lightly.
- Verify: pytest delta green + `--check` ok.
- Reverse report + STOP.

### Phase 3 — Compose note + dry brief card (after ACK only)

- Document how clone/feature-scan/site-map outputs map into envelope fields (no new scrapers).
- Emit one example brief markdown from fixtures.
- Reverse report + STOP — directive complete.

---

## Target profile

| Field | Value |
|-------|--------|
| mode | grind (Agent) |
| tools | shell / files — agent-skills repo |
| judgment_ceiling | MUST NOT (Hub ship, craft-anything adopt, bots, doctrine) |
| context | ZERO prior chat — this file is the source of truth |
