---
name: powercore-product-qualify
description: >-
  PowerCore Product Qualification (PPQ) — maturity ladder for store-ready
  products. Invoke with /ppq, /qualify, product qualify, store readiness,
  installer checklist, sellable backlist. Loads
  powercore-ops/design/powercore-product-qualification.md.
---

# PowerCore Product Qualify (PPQ) — Claude Code twin

Thin mirror of `agent-skills/.cursor/skills/powercore-product-qualify/SKILL.md`.
Doctrine: `powercore-ops/design/powercore-product-qualification.md`.
GPT paste: `agent-skills/docs/gpt-paste/POWERCORE_PRODUCT_QUALIFY_GPT_PASTE.md`.

## When to invoke

`/ppq`, `/qualify`, store readiness, installer/MSI/zip checklist, sellable backlist.

## Modes

AUDIT (default) → scorecard + ≤10 loose ends → stop for pick.  
ADVANCE only when operator names a stage. SCAFFOLD / BOARD per Cursor skill.

## P4 desktop default

Sellable buyer package zip root: **MSI + setup.exe + START_HERE.md**.  
Extensions: MSI `n/a`; still need zip + onboarding. `install-dev.ps1` ≠ P4.

## CLI

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.product_qualify board --plain
py -3.13 -m tools.product_qualify status --id <id> --plain
```

## Rules

- PPQ ≠ Ship Gate. Both required before sellable / store `active: true`.
- Do not invent evidence; use `missed` / `unknown`.
- Judgment ceiling: MUST NOT flip store activate or change pricing without Cursor ACK.
- After UI fixes → `/ux-prefs`; before activate → `/ship-gate --lane pre_activate`.

## Output contract

```
PPQ <id> stage=P# · blockers=<n> · next=<one line>
```

Then ≤10 loose ends. Stop for pick unless ADVANCE was explicit.
