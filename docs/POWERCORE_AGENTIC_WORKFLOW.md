# PowerCore agentic workflow (Horthy notes, mapped)

Doctrine only. Every point maps to a surface that **already exists**; nothing here adds a tip, a framework, or a format change. Source: Dexter Horthy via David Ondrej notes (llm-rag sidecar); the JSON-vs-XML material is ignored.

## Point → existing surface

| Horthy point | PowerCore surface |
|--------------|-------------------|
| **Lights-off ban** — never ship diffs nobody read | `tbcc-silent-fail` (external stop, not self-report) + Planner peek in `powercore-cc-cc-relay` + "no done without an external stop" (`powercore-ship-gate` before done/deploy/active). |
| **Four-stage gate** (product → architecture → program design → vertical slices) | entropy-scan → directive-generator → phase grind. The stage→skill table is added in a later phase. |
| **Tracer bullet / vertical slice** | One phase = one thin end-to-end slice that names **one external verify command** and stops for the Planner/Cursor ACK (`tbcc-cc-run`, `powercore-cc-cc-relay`). |
| **Dumb zone** — quality drops as context fills | Compaction: summarize → fresh session. Checklist + `tools.skill_gap.compact` below. Wires to `tbcc-auto-crystallize` and `*_report.md` handoffs. |
| **Inverse prompt** — ask the model what it is unsure of | Planner ACK asks the Grinder (or itself) "which choices were low-confidence?"; the Grinder's STOP fence already ends with one. Template wording lands in a later phase. |
| **Bottleneck, not token-max** (The Goal) | Review/trust is the bottleneck. Spend tokens where a human check is scarce; the tip-budget prune (`docs/proposals/2026-10-02_tip-budget-prune.md`) cuts always-on cost. |

Tip prune shortens or glob-scopes **tips**. It does **not** touch the skill catalog (`load_skill_catalog` / rank read `.cursor/skills/*/SKILL.md`, never tips); `powercore-endgates` stays alwaysApply as the selection backstop.

## Reject list

- JSON → XML migration (cost-negative; zero format changes).
- Lights-off factory (no human read of diffs).
- Unbounded context dumps into a session.
- Any **new** always-on tip.
- Incident → PR factory (deferred; future compose with silent-fail / island alerts only).
- Mega dirty-tree cleanup (separate later session; no mass `git add`).
- Blind remote creation (no `gh repo create` without per-product operator ACK).
- New mega-skill; a `powercore-skill-improve` wrapper.

## Compaction checklist (summarize → fresh session)

Compact when: the thread is long, answers get vaguer or loop, or a phase just closed.

1. Stop starting new work; finish or park the current slice.
2. Commit or note anything uncommitted (`git status`).
3. State the goal in one sentence.
4. List what is **done**, each with evidence (SHA, command output).
5. Keep only the **decisions** a fresh session must not re-litigate.
6. Name the **next one slice** and its single external stop command.
7. List open / low-confidence choices (inverse prompt).
8. Run: `py -3.13 -m tools.skill_gap.compact --goal "..." --done "..." --next "..." --verify "..."`
9. Durable facts → crystallize (`tbcc-auto-crystallize`); phase results → the `*_report.md`.
10. Open a **fresh** session; paste the stub, not the old thread. Do not paste raw logs.

Stubs go to `.skill-gap/compacts/` (gitignored); `--out-dir docs/handoffs` keeps one in git.
