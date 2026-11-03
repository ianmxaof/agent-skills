# PowerCore agentic workflow — Horthy notes → CC↔CC (follow-on)

**Depends on:** `2026-10-02_agent-skills-toolset-exponential` closed (Phases 1–4 ACKd — checkpoint 2026-10-02). Ready for Phase 0 when operator pastes into PLANNER.  
**Track:** context engineering + vertical-slice doctrine + **product git gate**  
**Repo cwd:** `C:\Powercore-repo-main\agent-skills` (primary); `powercore-ops/` for PPQ/ship-gate edits; cite `telegram_bot2/` read-only  
**Relay:** `/cc-cc` (Planner ↔ Grinder)  
**Source notes:** `llm-rag/_sidecar_out_of_vault/MarkText/json-vs-xml-davidondrej-agentic-workflow.md` (Dexter Horthy via David Ondrej — **ignore** the Coursera/SEO JSON-vs-XML append; out of scope)  
**Pointer:** do **not** overwrite `telegram_bot2/tbcc/docs/handoffs/CURRENT_DIRECTIVE.md`  
**Reverse:** `agent-skills/docs/handoffs/2026-10-02_horthy-agentic-workflow-powercore_report.md`  
**Operator prefs (2026-10-02):** keep skill-selection + cost wins; **include product git/GitHub gate**; **leave mega dirty-tree cleanup for later** (no mass `git add` / tree-hygiene phases).

### OPERATOR ACK — tip prune (LOCKED 2026-10-02)

**APPROVED for Grinder to implement.** Do not re-ask. Do not leave H5 as proposal-only.

| Field | Value |
|-------|--------|
| **Authority** | Operator (Cursor session) — explicit revise: “approval on the prune for the grinder to implement” |
| **Scope** | **agent-skills-owned** tips only, per `docs/proposals/2026-10-02_tip-budget-prune.md` |
| **Must apply** | (1) Track `.cursor/rules/` needed for tip edits (pathspecs only). (2) Glob-scope `powercore-skill-versions.mdc`. (3) Shorten `tbcc-cc-paste-bridge.mdc`, `powercore-token-hygiene.mdc`, `powercore-chat-contract.mdc` toward ≤200 tok each as in the proposal. |
| **Must preserve** | `powercore-endgates.mdc` alwaysApply (selection backstop). Skill catalog untouched. |
| **Must verify after** | `run_rank_evals --json` green; `endgates --auto --plain` still prints `open-skills:`; tip_budget total dropped vs baseline. |
| **Out** | `telegram_bot2` tips (`tbcc-silent-fail`, `tbcc-plain-language`) — handoff note only, separate Lane C. |
| **Revert** | One tip commit at a time so a rank/endgates regression reverts cleanly. |

Planner Phase 0: **record H5 = APPROVED — implement**; falsify only the *how* (pathspecs, order), not whether.

---

## Goal

Turn the high-signal Horthy points into **PowerCore-native, cheap, reversible** workflow upgrades: less context bloat, clearer vertical slices, human-in-the-loop that already matches our factory — **without** inventing a new agent framework or switching serialization formats. Also lock **every PowerCore product root to its own git repo + remote** so operators never have to remember `git init`.

Done when:

1. A short doctrine doc exists under `agent-skills/docs/` (or `powercore-ops/design/`) naming: lights-off ban, four-stage gate, tracer-bullet / vertical slice, dumb-zone compaction, inverse prompt, bottleneck-not-token-max — each mapped to an **existing** PowerCore surface (skill/rule/CLI).
2. One thin skill or tip compose edge lands: **session compaction** (summarize → fresh session) with a testable CLI or checklist.
3. Planner ACK checklist gains **inverse prompt** one-liner (which choices low confidence?).
4. Directive / CC-run / entropy templates get **one** vertical-slice verification sentence (external stop required) — no rewrite of every skill.
5. Explicit **reject list** in report: JSON→XML migration, lights-off factory, unbounded context dumps, new mega always-on tip.
6. **Tip prune applied** (agent-skills-owned tips per OPERATOR ACK); tip_budget down; rank_evals + endgates still green.
7. **Product git gate:** PPQ P0 + `product_qualify scaffold` (+ ship-gate/pre_activate check) require product root `.git` + configured `origin` remote; existing gaps (`powercore-store`, `text-expander`) listed with a **manual** backfill checklist (init/create remote only when operator ACKs that product — do not mass-create remotes blindly).

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
| Bottleneck (The Goal) | Tip-budget prune: **OPERATOR APPROVED** — Grinder implements agent-skills-owned rows (see OPERATOR ACK); safety note below |
| Incident → PR factory | **Defer** — only note as future compose with silent-fail / island alerts; no implement this pass |
| Product git / GitHub | PPQ P0 row + scaffold hook + ship-gate refuse without `.git`/`origin`; backfill list for store + text-expander |

### Out of scope

- Migrating any PowerCore API/config from JSON to XML (notes title noise; cost-negative)
- Building a new “agentic factory” product or replacing Cursor/CC
- Overnight rewriting all skills
- Auto lights-off (no human read of diffs)
- Touching island money bots / `.env` / `CURRENT_DIRECTIVE` caption track
- **Mega dirty-tree cleanup** (agent-skills 200+ untracked / powercore-ops vault detritus) — later session
- Blind `gh repo create` / `origin repo create` for every folder without operator product-by-product ACK
- Editing telegram_bot2 tip files from this thread (separate Lane C)

---

## Prior state (verified framing)

- PowerCore already has multiphase CC↔CC, entropy-scan, silent-fail, endgates, crystallize, skill-gap — **factory pieces exist**; notes mostly **name and tighten** habits, not greenfield.
- No in-repo hits for “dumb zone”, “compaction”, “inverse prompt”, “tracer bullet” under agent-skills / powercore-ops (gap is vocabulary + protocol, not tooling absence).
- Prior thread: tip soft-cap overruns + skill-gap ACK loop — bottleneck is review/trust and context cost, not “more skills.”
- Exponential toolset closed; prune **proposal** at `docs/proposals/2026-10-02_tip-budget-prune.md` — status flipped to **IMPLEMENT** by OPERATOR ACK above (was proposal-only).
- Product roots missing `.git` (2026-10-02 skim): `powercore-store`, `text-expander`. Others under Powercore-repo-main already have git.

### Tip prune ↔ skill selection (safety — locked)

- **Skill index/catalog does NOT read alwaysApply tips.** `load_skill_catalog` / `nearest_skills` / endgates rank scan `.cursor/skills/*/SKILL.md` on disk.
- Prune shortens or **glob-scopes** tips so they cost fewer tokens every turn. It does **not** remove skills from the catalog.
- Apply order (Grinder): track rules → skill-versions glob → paste-bridge shorten → token-hygiene shorten → chat-contract shorten (each its own commit or pair if tiny).
- **Preserve:** `powercore-endgates.mdc` alwaysApply — selection backstop. Do not delete or demote it.
- After each tip commit: `run_rank_evals --json` green + `endgates --auto --plain` prints `open-skills:`. Regression → revert that commit before continuing.

---

## Issue cards

| id | symptom | evidence | severity | depends_on | acceptance |
|----|---------|----------|----------|------------|------------|
| H1 | No named compaction / dumb-zone protocol | rg no hits; notes 42:04–42:20 | P0 | none | Doc + checklist/CLI: compact → reset; cites crystallize/handoff paths |
| H2 | Phases sometimes horizontal (many files, no mid verify) | factory default bias in notes; our phases vary | P0 | none | Forward template / cc-cc: each phase = tracer + external stop |
| H3 | Planner ACK lacks inverse prompt | powercore-cc-cc-relay has no “low confidence?” | P1 | none | One required question in Planner ACK Output Contract |
| H4 | Four-stage gate not explicit | entropy/directive exist but not sequenced as Product→Arch→Design→Slice | P1 | none | Doctrine table maps each stage → existing skill; Planner Phase 0 checklist |
| H5 | Tip/token maxing vs bottleneck | tip_budget over soft caps; proposal doc; **OPERATOR APPROVED** | P0 | prior I6 | Implement full agent-skills prune per OPERATOR ACK; rank_evals + endgates green after each tip commit; tip_budget total down |
| H6 | JSON/XML distraction | notes filename + Coursera block | P2 | none | Report reject; zero format migrations |
| H7 | Products can ship without own git/remote | `powercore-store`, `text-expander` git=False; PPQ P0 lacks git row | P0 | none | PPQ P0 + scaffold + ship-gate check; backfill checklist for the two gaps; no blind remote create |

---

## Constraints

- **judgment_ceiling (Grinder):** MUST implement H5 prune as approved (agent-skills tips listed in OPERATOR ACK); MUST NOT invent new product doctrine; MUST NOT edit telegram_bot2 tip files; MUST NOT scaffold `powercore-skill-improve`; MUST NOT mass-create GitHub remotes without per-product operator ACK; MUST NOT dirty-tree hygiene; MUST NOT skip H5 or reopen “should we prune?”.
- **judgment_ceiling (Planner):** MUST NOT re-block H5; MUST keep lights-on + verify rank_evals/endgates after Grinder H5; MUST reject XML; MAY order tip commits / pause mid-H5 only on verify fail.
- Fence labels: `PASTE INTO CC-PLANNER` / `PASTE INTO CC-GRINDER` only.
- Prefer editing thin docs + one skill/tip over new mega-skills.

---

## Verification

```powershell
cd C:\Powercore-repo-main\agent-skills
rg -n "dumb.?zone|compaction|tracer|inverse" docs/ .cursor/skills/powercore-cc-cc-relay/ docs/gpt-paste/ 2>$null
py -3.13 -m tools.skill_gap.endgates --prompt "compaction test" --response "wrote compact doc and reset" --auto --plain
py -3.13 -m tools.skill_gap.run_rank_evals --json
# after H5 prune:
py -3.13 -c "from tools.skill_gap.metrics import measure_tip_budget as m; import json; print(json.dumps(m(), indent=2))"
# after H7:
cd C:\Powercore-repo-main\powercore-ops
# show P0 git rows in design + scaffold dry-run / status for a sample product
rg -n "git|\.git|origin|remote" design/powercore-product-qualification.md products/REGISTRY.yaml
```

Human: open one sample forward handoff and confirm each Phase lists an external stop. Confirm `powercore-store` / `text-expander` appear on the backfill list.

---

## Working agreement

1. Exponential predecessor is closed — start when operator pastes into PLANNER.
2. Planner Phase 0 falsifies H1–H7 against disk.
3. Grinder one phase at a time; reverse report append; STOP for Planner.
4. No CURRENT_DIRECTIVE overwrite; no mega dirty-tree commits.

---

## Phases

### Phase 0 — Planner only

- Confirm exponential predecessor finished (cite report path + close-out SHA if present).
- Verdict keep/drop/amend H1–H7. **H5 is pre-approved — verdict must be `APPROVED — implement`**, not “proposal” or “wait for operator.” H7: keep. H6: reject.
- Lock grind order: Phase 1 = H1+H6; Phase 2 = H2+H3; Phase 3 = H4+**H5 full prune**; Phase 4 = H7 git gate.
- Emit `PASTE INTO CC-GRINDER` Phase 1 only. In every Grinder fence after Phase 2, remind: **H5 prune is operator-approved — implement in Phase 3.**

### Phase 1 — Doctrine + compaction (H1, H6)

- Write `agent-skills/docs/POWERCORE_AGENTIC_WORKFLOW.md` (short): map Horthy → PowerCore surfaces; reject XML; ban lights-off; note tip prune ≠ skill catalog.
- Add compaction checklist (≤15 lines) + optional thin CLI or script that writes a dated compact stub under `docs/handoffs/` or `.skill-gap/compacts/`.
- Report.

### Phase 2 — Vertical slice + inverse prompt (H2, H3)

- Patch `powercore-cc-cc-relay` (+ Claude twin if present) Planner ACK: require inverse-confidence question; Grinder phase contract: one external stop per phase.
- Patch directive-generator / handoff template snippet (agent-skills or tbcc twin — **smallest** surface) with tracer-bullet verification line.
- No mass skill rewrite.

### Phase 3 — Four-stage map + tip prune IMPLEMENT (H4, H5) — OPERATOR APPROVED

- Add stage→skill table to doctrine doc.
- **Commit A:** track agent-skills `.cursor/rules/` tip files needed (pathspecs only — no unrelated skills/vendor/apps).
- **Commit B:** `powercore-skill-versions.mdc` → glob-scope (`evals/versions/**` or equivalent); verify rank_evals + endgates.
- **Commit C:** shorten `tbcc-cc-paste-bridge.mdc` toward ≈150 tok (fence names + blind-paste + skill pointer).
- **Commit D:** shorten `powercore-token-hygiene.mdc` toward ≈180 tok (keep endgates + rank-eval lines).
- **Commit E:** shorten `powercore-chat-contract.mdc` toward ≈190 tok (pointer to `powercore-ops/chat_contract/`).
- After **each** of B–E: tip_budget snapshot + `run_rank_evals --json` + `endgates --auto --plain` → must show `open-skills:`. Fail → revert that commit, STOP for Planner (do not abandon the rest of H5 without Planner).
- Mark proposal doc status: **IMPLEMENTED (agent-skills)**; leave telegram_bot2 rows as “handoff to Lane C.”
- Do **not** wait for another operator yes — already approved.

### Phase 4 — Product git gate (H7)

- Update `powercore-ops/design/powercore-product-qualification.md` P0: require product root is a git repo with `origin` remote (blocker yes).
- Update `tools/product_qualify` scaffold (and skill text): after creating QUALIFICATION.md, check/init git in REGISTRY root path; ensure `.gitignore` exists; **stop** before remote create — print exact `gh repo create` / Cursor `origin` commands for operator ACK (or `--create-remote` only when explicitly passed).
- Ship-gate / pre_activate: refuse or warn when product root lacks `.git` or `origin` (smallest surface that already gates activate).
- Write backfill checklist for `powercore-store` + `text-expander` (and any other REGISTRY roots missing git); **do not** init remotes unless operator names the product in an ACK.
- Verify + STOP.

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
- [ ] Paste this path into PLANNER: agent-skills/docs/handoffs/2026-10-02_horthy-agentic-workflow-powercore.md
- [ ] Blind-paste fences PLANNER ↔ GRINDER only
- [ ] Tip prune: already APPROVED — Grinder implements in Phase 3 (no second ask)
- [ ] Leave caption CURRENT_DIRECTIVE alone
- [ ] Dirty-tree cleanup: later (not this thread)
- [ ] After H5: confirm open-skills still ranks; after H7: store/text-expander on backfill list only until you ACK remotes
```

---

## Distilled actionable points (from notes — signal only)

1. **Stay lights-on** — humans read diffs; agents don’t replace trust (matches silent-fail).
2. **Four stages before code** — Product / Arch / Program Design / Vertical slice (entropy → directive → phased grind).
3. **Tracer bullets** — each phase end-to-end + testable; fight horizontal mega-diffs.
4. **Context-cheap** — high-signal only; avoid dumb zone (~half window → compact + reset).
5. **Inverse prompt** — “what are you not confident about?”
6. **Bottleneck first** — tip prune cuts always-on cost; skill catalog stays; don’t tip-max.
7. **Product git gate** — every product root gets `.git` + remote via PPQ/scaffold/ship-gate, not memory.
8. **Skip** — JSON vs XML holy war; full lights-off factory; incident-router factory; mega dirty-tree this pass.
