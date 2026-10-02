---
name: powercore-ship-gate
description: >-
  PowerCore Ship Gate (PSG) — MUST run before claiming done/deployed/ship/
  sellable on a registered PowerCore root. Lean CODE every code pass; LIVE
  only after deploy; pre_activate before store active:true. Use when tip
  powercore-ship-gate fires, /ship-gate, PSG, pre-activate, or ship readiness
  / stress automation. Composes with silent-fail as LIVE probe library —
  does not replace /silent-fail deep ops protocol.
---

# PowerCore Ship Gate (PSG)

## Purpose

No agent claims **done / deployed / sellable** without a fresh external check.
Lean = CODE (tests, pack, zip_manifest, catalog). Live = island probes only
after a deploy in this pass. Same verdict map as silent-fail (`fail` included).

## Always-on tip

`.cursor/rules/powercore-endgates.mdc` — then load this skill for PSG lanes/contract before claiming done/deployed/sellable.


## CLI

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.ship_gate.run --auto --root text-expander --json
py -3.13 -m tools.ship_gate.run --auto --root pc-notes --json
py -3.13 -m tools.ship_gate.run --auto --root github-seo --json
py -3.13 -m tools.ship_gate.run --auto --root tbcc --json
py -3.13 -m tools.ship_gate.run --lane live --root tbcc --json
py -3.13 -m tools.ship_gate.run --check-evidence --root text-expander
py -3.13 -m tools.ship_gate.run --lane pre_activate --product text-expander --json
```

## Lanes (Phase 3)

| Lane | When | Notes |
|------|------|--------|
| lean | every code pass | tests / pack / zip_manifest / ship_smoke / catalog |
| live | after deploy, or explicit `--lane live` | island `/health` + loot CTA HTTP; `idle_flag` respected |
| pre_activate | before `active: true` | lean + **stress ≤7d** + evidence file |
| stress | nightly / `--lane stress` | thresholded; writes `agent-skills/.ship-gate/stress/<key>.json` |

```powershell
py -3.13 -m tools.ship_gate.run --lane stress --root text-expander
py -3.13 -m tools.ship_gate.run --lane stress --root tbcc
powershell -NoProfile -File tools\ship_gate\nightly.ps1
```

Stress thresholds (registry): text-expander p95 expand under 50ms over 100 iters; money-path requires island+loot ok, at least 10 ok surfaces, allows Gumroad stale.
Missing/expired stress evidence **blocks** pre_activate and store `predeploy` evidence check.

Live never runs local Redis/DB probes.

## Summary line (mandatory)

```
PSG <run_id> tree=<hash8> <lane>: <ok> ok / <idle> idle / <bad> not-green — <worst> [<watch>: <reason>] — evidence: <path>
```

## Done contract

1. No done/fixed/ready/deployed/ship/sell without PSG whose `tree_hash` matches and worst is `ok` or `idle(<FLAG>=value)`.
2. `blocked` / `fail` / `stale` / `never_seen` → not done; name watch + one next fix.
3. Never use probe **exit code** (always 0); parse `--json` verdict.
4. No Start bots / restart / edit checks to go green.
5. Store activate: `pre_activate` evidence under `powercore-store/.ship-gate/pre_activate/<id>@<ver>.json`; `npm run deploy` runs `predeploy` which requires it.

## Skip

- No registered root changed (chat-only / Ask-mode)
- Only `ignore` globs changed
- Changed but unmapped → print `PSG: unmapped <path>` (never green)

## Compose

- Silent-fail = LIVE lane probe library + deep `/silent-fail`
- PSG owns end-of-pass for brand/product; calls silent-fail only on `--lane live --deployed`
- `/cc-report` must refuse ACK without PSG summary line + evidence path when code roots changed
- **Sellable / store-ready:** also require PPQ ≥ P6 (`powercore-product-qualify` / `/ppq`) — PSG green alone is not product-complete

## Evidence

- `<root>/.ship-gate/last.json` (gitignore)
- `agent-skills/.ship-gate/runs/<run_id>.json`
