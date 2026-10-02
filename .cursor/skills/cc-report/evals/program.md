# program.md — cc-report self-improve loop

Skill under test: `cc-report` (PowerCore CC Relay reverse hop).

## Goal

Maximize composite binary score:

| Layer | Source |
|---|---|
| Fixtures | `evals/evals.json` |
| Triggers | `evals/triggers.json` |
| Body | `evals/body_assertions.json` (SKILL.md must contain contract text) |
| Live (optional) | Vault Rotator ask with SKILL.md as system prompt |

Never stop mid-loop to ask permission when the operator started overnight —
but **never** push, start bots, or touch `.env`.

## Overnight command

```powershell
cd C:\Powercore-repo-main\agent-skills

# Stop when perfect
py -3.13 -m tools.skill_gap.overnight_loop --skill cc-report --until-perfect

# Long watch
py -3.13 -m tools.skill_gap.overnight_loop --skill cc-report --max-iters 500 --sleep 60

# Live model outputs (Vault daemon + Rotator owned)
py -3.13 -m tools.skill_gap.overnight_loop --skill cc-report --until-perfect --live

# Prove mutator
py -3.13 -m tools.skill_gap.overnight_loop --skill cc-report --demo-break --until-perfect --max-iters 5

.\tools\skill_gap\start_overnight.ps1 -Skill cc-report -UntilPerfect
```

## Versioning

Immutable snapshots under `evals/versions/` (CURRENT pointer + pin + rollback fork-forward).

```powershell
py -3.13 -m tools.skill_gap.skill_versions seed --skill cc-report --score 20/20
py -3.13 -m tools.skill_gap.skill_versions list --skill cc-report
py -3.13 -m tools.skill_gap.skill_versions pin --skill cc-report --id v0001
py -3.13 -m tools.skill_gap.skill_versions rollback --skill cc-report --id v0001
```

Overnight **keeps** auto-snapshot. Rollback restores a prior snapshot then creates a new CURRENT (history kept). Rule: `powercore-skill-versions.mdc`.

## Loop (one change per iteration)

1. Score fixtures + triggers + body (+ live if `--live`).
2. If perfect and `--until-perfect` → exit.
3. Else mutate **one** thing in `SKILL.md` (body insert / description phrases / live hint).
4. Re-score. Keep if score did not drop → snapshot version; else restore `.overnight.bak`.
5. Append JSON line to `evals/results.jsonl`.
6. Repeat until perfect, max-iters, or Ctrl+C.

## Hard rules

- Assertions stay **binary**.
- Do not weaken fixtures to green the score.
- Skill id stays `cc-report` (stable slash); new skills use `powercore-*`.
- Never claim a Cursor-only ACK (always emit the paste fence).
- Never rewrite old `evals/versions/v*.md` files.
