---
name: powercore-repo-trust
description: Triages an untrusted local checkout or GitHub/gist/paste URL for supply-chain
  and deception smells before vendoring. Runs semantic-deception-detector first (claim ledger
  + --ask), then install-hook / workflow / opaque-base64 pass. Emits smell_level and
  operator_action (smell ≠ go-ahead). Use for /repo-trust, repo trust triage, or "is this
  safe to vendor".
purpose: Triages an untrusted local checkout or GitHub/gist/paste URL for supply-chain and
  deception smells before vendoring — with question-aware claim verification
trigger_phrases:
- /powercore-repo-trust
- powercore repo trust
- /gist
- /paste
- /repo-trust
- /Ghidra
inputs:
- operator paste or focused context
- optional --ask question
outputs:
- skill Output Contract markdown (smell, action, claim ledger, next)
jev_hints:
  lane: chat
  cost: cheap
  needs_context: true
if_stumped: Ask once for the missing input or context; do not invent results.
example_invocation: /repo-trust --ask "does plan-edit-before-execute exist?" on this URL
---
# PowerCore Repo Trust (v1.2)

Defensive **source** triage — not reverse engineering, not malware confirmation.

Changelog:
- v1.0 — semantic + install/workflow/b64 second pass; Hub card.
- v1.1 — `smell_level` / `operator_action` / `claim_ledger` / mandatory `next_step`. `--ask` question-aware verify. LOW smell is never “Looks fine to vendor.”
- v1.2 — opt-in `--deps` (typosquat denylist) + `--meta` (no LICENSE / docs-heavy). Hub chip fills `--ask` placeholder; formatter leads with Action.

## Purpose

- Answer: *what should I do with this tree?* — not *does it smell LOW?*
- Always run `semantic-deception-detector` first (script is truth for docs-vs-behavior / TrapDoor Unicode / injection bait / claim ledger).
- Thin second pass: install hooks, workflow write grants, opaque base64.
- Compose `operator_action`: `IGNORE` | `SPOT_CHECK` | `HARVEST_OK` | `PIPELINE_FIT` | `STOP`.
- Never declare guilt, intent, or legal liability. TrapDoor Unicode extract stays Threat Monitor B1 — wrap shared sanitizer when it lands; do not fork.

## When to Invoke

- `/repo-trust`, `repo trust`, `safe to vendor`, `scan this github for malice`
- Prefer with `--ask "does <feature> exist?"` when evaluating a named harvest
- Situational: after Desk / integration-scan says "fits"

**Do not use for:** binary RE, cracking, Frida/Ghidra, executing untrusted code, “malware confirmed.”

## CLI

```powershell
python "$env:USERPROFILE\.cursor\skills\powercore-repo-trust\scripts\repo_trust.py" --json "https://github.com/owner/repo"
python "$env:USERPROFILE\.cursor\skills\powercore-repo-trust\scripts\repo_trust.py" --ask "does plan-edit-before-execute exist?" --json "https://github.com/owner/repo"
python "$env:USERPROFILE\.cursor\skills\powercore-repo-trust\scripts\repo_trust.py" --ask "does X exist?" --deps --meta --json "https://github.com/owner/repo"
python "$env:USERPROFILE\.cursor\skills\powercore-repo-trust\scripts\repo_trust.py" --self-test
```

## Vincent Hub

1. Hub runs against **this tab’s URL** — do not ask for a PowerShell paste.
2. If no stdout, press **Run** on `/run repo-trust` with the repo tab focused.
3. Summarize with the Output Contract. Lead with **action** + claim misses — not legacy `trust_level` alone.

## Agent procedure

1. Resolve target. Prefer `scripts/repo_trust.py`. Pass `--ask` when the operator named a feature.
2. Exit `1` = `operator_action` in `{STOP, PIPELINE_FIT, SPOT_CHECK}` or legacy `trust_level` ≠ LOW.
3. Emit Output Contract. Stop. Do not install/vendor from a LOW smell alone.

## Output Contract

```markdown
# Repo trust check

## Verdict
smell=…  action=…  (legacy trust_level=…)

## Claim ledger
- [hit|miss|unknown] …

## Semantic
…

## Second pass
…

## Not claimed
Not malware. Not intent. Smell ≠ safe to vendor.

## Next
<script next_step — never empty on REVIEW+>
```

1. **Verdict** — lead with `smell_level` + `operator_action`. Legacy `trust_level` is secondary.
2. **Claim ledger** — hits/misses/unknown from `--ask` or README feature bullets.
3. **Semantic** — structural score + up to 15 findings.
4. **Second pass** — install hooks / workflow / opaque blobs.
5. **Next** — copy script `next_step` (`/pipeline-fit`, spot-check, or stop). Never invent “Looks fine to keep exploring.”

## Sibling skills

- `semantic-deception-detector` — metal detector + claim ledger engine
- `powercore-skill-fire-gate` — plan→approve before firing this skill on scary targets
- `powercore-pipeline-fit` — ADOPT/HARVEST/WATCH after `HARVEST_OK` or on `PIPELINE_FIT`
- `tbcc-integration-scan` — TBCC signal-path fit only
