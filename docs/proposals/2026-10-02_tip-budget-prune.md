# Proposal — alwaysApply tip-budget prune (2026-10-02)

**Status: IMPLEMENTED (agent-skills-owned tips), 2026-10-02.** Operator-approved; applied in Horthy Phase 3 (commits 34dfc57, 9e2f3ea, 8373648, db9364f; baseline eeaf0cc). Total 3063 → 2080 tok. `tbcc-silent-fail` + `tbcc-plain-language` remain **handoff to Lane C** (telegram_bot2-owned, not touched). Note: telegram_bot2 carries its own `powercore-skill-versions.mdc` (151 tok, alwaysApply) that the budget now counts in place of the glob-scoped agent-skills copy.
Source: `agent-skills/.skill-gap/metrics/tip_budget.json` (measured 2026-10-02T09:31Z).

## Budget snapshot

- 8 alwaysApply tips, **3063 tok** total (cumulative cap 6000 → OK). Endgates tip 159 tok (cap 200 → OK).
- Single-tip soft cap: **200 tok**. **6 of 8 tips exceed it.** Two tips are compliant (powercore-chrome-fonts 193, powercore-endgates 159) and are not listed below.

## Tips over the 200-tok single cap

| Tip | Tok | Over by | Owner repo | Recommended action |
|-----|----:|--------:|------------|--------------------|
| tbcc-cc-paste-bridge.mdc | 739 | 539 | agent-skills | **Shorten** to ≈150 tok (fence names + "blind-paste, end with the fence" + pointer). Procedure already lives in the `powercore-cc-cc-relay` / `tbcc-cc-run` skills. |
| tbcc-silent-fail.mdc | 494 | 294 | **telegram_bot2** | **Shorten** to ≈180 tok (gate triggers + skip list + pointer to `tbcc-silent-fail` skill). *Owner action only.* |
| powercore-skill-versions.mdc | 448 | 248 | agent-skills | **Demote to skill-only / glob-scope**: its own header says "always on when editing overnight skills". Scope to `.cursor/skills/**/evals/versions/**` (or fold into `powercore-skill-gap`), keep ≈0 always-on tok. |
| tbcc-plain-language.mdc | 388 | 188 | **telegram_bot2** | **Keep with reason / light shorten**: operator-requested tone rule, genuinely needs to be always-on. Trim examples to ≈200 tok. *Owner action only.* |
| powercore-token-hygiene.mdc | 346 | 146 | agent-skills | **Shorten** to ≈180 tok; the full checklist already lives in `powercore-token-audit`. Keep the endgates + rank-eval command lines. |
| powercore-chat-contract.mdc | 296 | 96 | agent-skills | **Shorten** to ≈190 tok: keep "follow `powercore-ops/chat_contract/`" + Enter-sends; move the Do/Do-not lists into that directory's README. |

## Estimated savings (if every row is applied to ≤200 tok)

- agent-skills-owned (4 tips): 739+448+346+296 = 1829 → target ≈150+0+180+190 = 520 → **≈ −1300 tok**.
- telegram_bot2-owned (2 tips): 494+388 = 882 → ≈ 380 → **≈ −500 tok**.
- Total: 3063 → ≈ 1260 tok (**≈ −1800 tok, ~59%**). Even agent-skills-only gets 3063 → ≈ 1760.
- Estimates are token counts by the repo's own `_estimate_tok`; re-measure with `measure_tip_budget()` after any edit.

## Do not touch telegram_bot2-owned rules from this repo

`tbcc-silent-fail.mdc` and `tbcc-plain-language.mdc` live under `telegram_bot2/.cursor/rules/`. They are measured here but **owned by telegram_bot2**: agent-skills sessions must not edit them. Hand the two rows above to a telegram_bot2 session (Lane C) as a separate directive.

## Known drift — token-audit has two twin shapes

- `telegram_bot2/.claude/skills/powercore-token-audit/SKILL.md` is a **full-body** copy of the Cursor canonical (plus small Claude-specific edits).
- `agent-skills/.claude/...` and `powercore-ops/.claude/...` are **thin stubs** (description + pointer).
- **One-line fix path:** on a deliberate future pass, regenerate the telegram_bot2 twin from canonical (`scaffold_surfaces --skill powercore-token-audit --force --claude-root C:\Powercore-repo-main\telegram_bot2` after supplying the real description) — diff first, since `--force` overwrites.

## Suggested order if approved (each its own revertible commit)

1. powercore-skill-versions → glob-scope (largest agent-skills cut, lowest risk).
2. tbcc-cc-paste-bridge, powercore-token-hygiene, powercore-chat-contract → shorten.
3. Hand telegram_bot2 rows to its owner.
Evidence after each: `py -3.13 -m tools.skill_gap.endgates --auto --plain` (prints tip-budget) and `py -3.13 -c "from tools.skill_gap.metrics import measure_tip_budget as m; print(m()['total_tok'])"`.
