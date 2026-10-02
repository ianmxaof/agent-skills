# PowerCore agentic workflow — Horthy notes → CC↔CC (follow-on)

**Depends on:** finish `2026-10-02_agent-skills-toolset-exponential.md` (Phases 1–4 ACKd) **before** starting Phase 0 here.  
**Track:** context engineering + vertical-slice doctrine for PowerCore agent work  
**Repo cwd:** `C:\Powercore-repo-main\agent-skills` (primary); read-only cite `powercore-ops/` / `telegram_bot2/` as needed  
**Relay:** `/cc-cc` (Planner ↔ Grinder)  
**Source notes:** `llm-rag/_sidecar_out_of_vault/MarkText/json-vs-xml-davidondrej-agentic-workflow.md` (Dexter Horthy via David Ondrej — **ignore** the Coursera/SEO JSON-vs-XML append; out of scope)  
**Pointer:** do **not** overwrite `telegram_bot2/tbcc/docs/handoffs/CURRENT_DIRECTIVE.md`  
**Reverse:** `agent-skills/docs/handoffs/2026-10-02_horthy-agentic-workflow-powercore_report.md`

---

## Goal

Turn the high-signal Horthy points into **PowerCore-native, cheap, reversible** workflow upgrades: less context bloat, clearer vertical slices, human-in-the-loop that already matches our factory — **without** inventing a new agent framework or switching serialization formats.

Done when:

1. A short doctrine doc exists under `agent-skills/docs/` (or `powercore-ops/design/`) naming: lights-off ban, four-stage gate, tracer-bullet / vertical slice, dumb-zone compaction, inverse prompt, bottleneck-not-token-max — each mapped to an **existing** PowerCore surface (skill/rule/CLI).
2. One thin skill or tip compose edge lands: **session compaction** (summarize → fresh session) with a testable CLI or checklist.
3. Planner ACK checklist gains **inverse prompt** one-liner (which choices low confidence?).
4. Directive / CC-run / entropy templates get **one** vertical-slice verification sentence (external stop required) — no rewrite of every skill.
5. Explicit **reject list** in report: JSON→XML migration, lights-off factory, unbounded context dumps, new mega always-on tip.

---

## Scope

### In scope

| Horthy idea | PowerCore action |
|-------------|------------------|
| Lights-off fallacy | Map to silent-fail + Planner peek + “no done without external stop”; doctrine only |
| Four stages (Product → Arch → Program Design → Vertical slices) | Map to entropy-scan → directive → phase grind; add checklist to directive-generator / cc-cc Planner Phase 0 |
| Vertical slice / tracer bullet | Require each grind phase to name one **external** verify command; reinforce in forward handoff template |
| Context engineering / dumb zone | Compaction protocol: when session fat → write compact design/progress md → reset; wire to crystallize / handoff report habit |
| Inverse prompting | Planner ACK asks Grinder (or self): low-confidence choices |
| Bottleneck (The Goal) | Tip-budget / endgates: prefer prune over more tips; cite I6 follow-through from prior thread |
| Incident → PR factory | **Defer** — only note as future compose with silent-fail / island alerts; no implement this pass |

### Out of scope

- Migrating any PowerCore API/config from JSON to XML (notes title noise; cost-negative)
- Building a new “agentic factory” product or replacing Cursor/CC
- Overnight rewriting all skills
- Auto lights-off (no human read of diffs)
- Touching island money bots / `.env` / `CURRENT_DIRECTIVE` caption track
- Applying tip prune without operator ACK (proposal + compose only unless prior exponential Phase 4 already wrote the list — then may implement **agent-skills-owned** tip demotions only if Planner ACKs)

---

## Prior state (verified framing)

- PowerCore already has multiphase CC↔CC, entropy-scan, silent-fail, endgates, crystallize, skill-gap — **factory pieces exist**; notes mostly **name and tighten** habits, not greenfield.
- No in-repo hits for “dumb zone”, “compaction”, “inverse prompt”, “tracer bullet” under agent-skills / powercore-ops (gap is vocabulary + protocol, not tooling absence).
- Prior thread: tip soft-cap overruns + skill-gap ACK loop — bottleneck is review/trust and context cost, not “more skills.”

---

## Issue cards

| id | symptom | evidence | severity | depends_on | acceptance |
|----|---------|----------|----------|------------|------------|
| H1 | No named compaction / dumb-zone protocol | rg no hits; notes 42:04–42:20 | P0 | none | Doc + checklist/CLI: compact → reset; cites crystallize/handoff paths |
| H2 | Phases sometimes horizontal (many files, no mid verify) | factory default bias in notes; our phases vary | P0 | none | Forward template / cc-cc: each phase = tracer + external stop |
| H3 | Planner ACK lacks inverse prompt | powercore-cc-cc-relay has no “low confidence?” | P1 | none | One required question in Planner ACK Output Contract |
| H4 | Four-stage gate not explicit | entropy/directive exist but not sequenced as Product→Arch→Design→Slice | P1 | none | Doctrine table maps each stage → existing skill; Planner Phase 0 checklist |
| H5 | Tip/token maxing vs bottleneck | tip_budget over soft caps; Horthy 45:00–47:30 | P2 | prior I6 | Doctrine: optimize bottleneck; optional apply agent-skills tip demotions only if Planner yes |
| H6 | JSON/XML distraction | notes filename + Coursera block | P2 | none | Report reject; zero format migrations |

---

## Constraints

- **judgment_ceiling (Grinder):** MUST NOT invent new product doctrine; MUST NOT auto-apply tip prune across telegram_bot2; MUST NOT scaffold `powercore-skill-improve` unless prior exponential thread reopened it.
- **judgment_ceiling (Planner):** MAY drop H5 apply; MUST keep lights-on; MUST reject XML migration.
- Fence labels: `PASTE INTO CC-PLANNER` / `PASTE INTO CC-GRINDER` only.
- Prefer editing thin docs + one skill/tip over new mega-skills.

---

## Verification

```powershell
cd C:\Powercore-repo-main\agent-skills
# after H1/H2 land:
rg -n "dumb.?zone|compaction|tracer|inverse" docs/ .cursor/skills/powercore-cc-cc-relay/ docs/gpt-paste/ 2>$null
py -3.13 -m tools.skill_gap.endgates --prompt "compaction test" --response "wrote compact doc and reset" --auto --plain
# if tip demotion applied (agent-skills only):
py -3.13 -m tools.skill_gap.metrics  # or tip_budget measure — cite exact cmd Grinder used
```

Human: open one sample forward handoff and confirm each Phase lists an external stop.

---

## Working agreement

1. Wait until exponential toolset report shows Phases 1–4 complete (or operator says “start Horthy now”).
2. Planner Phase 0 falsifies H1–H6 against disk after exponential lands.
3. Grinder one phase at a time; reverse report append; STOP for Planner.
4. No CURRENT_DIRECTIVE overwrite.

---

## Phases

### Phase 0 — Planner only

- Confirm exponential predecessor finished (cite report path + last phase).
- Verdict keep/drop/amend H1–H6.
- Lock grind order (default: H1 → H2 → H3 → H4; H5 proposal-only unless yes; H6 reject note in Phase 1 report).
- Emit `PASTE INTO CC-GRINDER` Phase 1 only.

### Phase 1 — Doctrine + compaction (H1, H6)

- Write `agent-skills/docs/POWERCORE_AGENTIC_WORKFLOW.md` (short): map Horthy → PowerCore surfaces; reject XML; ban lights-off.
- Add compaction checklist (≤15 lines) + optional thin CLI or script that writes a dated compact stub under `docs/handoffs/` or `.skill-gap/compacts/`.
- Report.

### Phase 2 — Vertical slice + inverse prompt (H2, H3)

- Patch `powercore-cc-cc-relay` (+ Claude twin if present) Planner ACK: require inverse-confidence question; Grinder phase contract: one external stop per phase.
- Patch directive-generator / handoff template snippet (agent-skills or tbcc twin — **smallest** surface) with tracer-bullet verification line.
- No mass skill rewrite.

### Phase 3 — Four-stage map + bottleneck (H4, H5)

- Add stage→skill table to doctrine doc.
- Tip-bottleneck: write or extend prune proposal; apply **only** agent-skills-owned tips if Planner ACK’d apply; else stop at proposal.
- Final Goal Verification; STOP.

---

## Target profile

| Field | Value |
|-------|--------|
| mode | Planner judgment → Grinder implement |
| tools | filesystem + shell on agent-skills |
| judgment_ceiling | Grinder MUST NOT doctrine-expand beyond locked Phase 0 |
| context | ZERO chat — this file + reverse report + predecessor exponential report |

---

## Operator courier

```
- [ ] Finish current exponential CC↔CC first
- [ ] Then paste this path into PLANNER: agent-skills/docs/handoffs/2026-10-02_horthy-agentic-workflow-powercore.md
- [ ] Blind-paste fences PLANNER ↔ GRINDER only
- [ ] Leave caption CURRENT_DIRECTIVE alone
```

---

## Distilled actionable points (from notes — signal only)

1. **Stay lights-on** — humans read diffs; agents don’t replace trust (matches silent-fail).
2. **Four stages before code** — Product / Arch / Program Design / Vertical slice (entropy → directive → phased grind).
3. **Tracer bullets** — each phase end-to-end + testable; fight horizontal mega-diffs.
4. **Context-cheap** — high-signal only; avoid dumb zone (~half window → compact + reset).
5. **Inverse prompt** — “what are you not confident about?”
6. **Bottleneck first** — don’t tip-max / token-max everything (The Goal).
7. **Skip** — JSON vs XML holy war; full lights-off factory; incident-router factory this pass.
