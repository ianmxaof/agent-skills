# LOG — repo-trust / semantic P0+P1 + skill-fire-gate

Date: 2026-11-02  
Scope: P0 contract harden + P1 skill-fire-gate (deer-flow harvest)

## Shipped

| Item | Version / path |
|------|----------------|
| semantic-deception-detector | `scripts/scan.py` **1.1.0** — smell/action/claim_ledger/next_step/`--ask` |
| semantic_scan.py CLI | forwards `--ask` / `--no-readme-claims` |
| powercore-repo-trust | `scripts/repo_trust.py` **1.1.0** — Hub card leads with action + ledger |
| operator-cli | `semantic-scan` + **`repo-trust`** subcommands; `--ask` |
| powercore-skill-fire-gate | Triple Surface (Cursor + 3 Claude twins + GPT paste) |

## Contract (locked)

```
smell_level:     CLEAN | LOW | REVIEW | HIGH | BLOCK
operator_action: IGNORE | SPOT_CHECK | HARVEST_OK | PIPELINE_FIT | STOP
claim_ledger:    [{claim, source, evidence_path, status: hit|miss|unknown}]
next_step:       always set from action (never empty “looks fine” on LOW)
```

## Verification

```powershell
py -3.13 .../semantic-deception-detector/scripts/scan.py --self-test
py -3.13 .../powercore-repo-trust/scripts/repo_trust.py --self-test
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-skill-fire-gate --check
```

Both self-tests PASS. Fire-gate check: ok.

## Fence

- Threat Monitor B1 still owns TrapDoor Unicode shared sanitizer — wrap later, do not fork in scan.py.
- P2 deferred: `--deps` / `--meta` dynamics; harvest-close; sub-audit.
