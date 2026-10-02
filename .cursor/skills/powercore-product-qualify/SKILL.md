---
name: powercore-product-qualify
description: >-
  PowerCore Product Qualification (PPQ) — maturity ladder for store-ready
  products. Invoke with /ppq, /qualify, product qualify, store readiness,
  installer checklist, sellable backlist, or when a PowerCore product enters
  scope and needs chrome/install/onboarding/Vault review. Loads
  design/powercore-product-qualification.md; audits products under
  products/<id>/QUALIFICATION.md; scaffolds new checklists; does not replace
  /ship-gate or /ux-prefs.
---

# PowerCore Product Qualify (PPQ)

## Purpose

Walk each product from incomplete → **PowerCore-grade / store-ready**:
installer (zip/MSI), onboarding, chrome, Vault/tray hooks, bug backlog.
Honest stages for unfinished products. Sellable only at **P6** + Ship Gate.

## Canonical

| Piece | Path |
|-------|------|
| Doctrine | `powercore-ops/design/powercore-product-qualification.md` |
| Registry | `powercore-ops/products/REGISTRY.yaml` |
| Checklists | `powercore-ops/products/<id>/QUALIFICATION.md` |
| Installer template | `powercore-ops/packaging/product-template/` |
| CLI | `py -3.13 -m tools.product_qualify` (from agent-skills) |

Always-on tip: `.cursor/rules/powercore-product-qualify.mdc`

## When to invoke

- `/ppq`, `/qualify`, `/ppq <id>`, “qualify product”, “store readiness”
- Product enters operator scope; walk the sellable backlist
- Before claiming sellable / store-ready / public download
- Scaffolding MSI/zip for a desktop product (use product-template)

**Skip:** single named bug (“just the bug”); pure Ship Gate re-run with no maturity ask; non-PowerCore repos.

## Modes

### AUDIT (default)

1. Read doctrine + `REGISTRY.yaml`.
2. Load `products/<id>/QUALIFICATION.md` (ask id once if missing).
3. Re-verify **auto** rows with real paths/commands when cheap; leave **manual** as judgment with evidence.
4. Emit scorecard (P0–P6) + ≤10 loose ends (blockers first).
5. Update QUALIFICATION.md statuses only when evidence changed.
6. **Stop** for operator pick — do not implement the whole ladder.

### ADVANCE

Operator says “close P2” / “advance vault to P4”:

1. Fence to **that stage only**.
2. Implement or document; mark rows `covered` with evidence.
3. Recompute stage (lowest unfinished stage with a blocker `missed`).
4. Update REGISTRY `stage` if changed.
5. Summarize; stop.

### SCAFFOLD

New product or missing checklist:

1. Add registry row.
2. Copy standard checklist from doctrine into `products/<id>/QUALIFICATION.md`.
3. Set honest initial statuses (`missed` default; do not fake covered).
4. If `packaging: desktop-msi` or `desktop-zip`, point at `packaging/product-template/`.

### BOARD

List all registry products: id · stage · packaging · top blocker.

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.product_qualify board --plain
py -3.13 -m tools.product_qualify status --id vault --plain
py -3.13 -m tools.product_qualify scaffold --id github-presentation --plain
py -3.13 -m tools.product_qualify media-prompt --id text-expander --plain
```

## P4 Desktop default

Sellable buyer package zip root: **MSI + msi-launcher stub (setup.exe) + START_HERE.md**.  
(Extensions: MSI `n/a`; still need zip + onboarding.)

## Rules

- PPQ ≠ Ship Gate. Green tests ≠ sellable product.
- Store `active: true` today does **not** imply PPQ P6 — close blockers first.
- Do not invent evidence; use `unknown` / `missed`.
- Extensions: MSI often `n/a`; still need P4 zip smoke + P5 onboarding.
- Desktop: P4 requires frozen zip or MSI — `install-dev.ps1` alone is not enough.
- Compose: after UI fixes → `/ux-prefs`; before activate → `/ship-gate --lane pre_activate`.
- After store card (P6): `media-prompt` → Gemini → `_inbox/` → `make-card-loop.ps1` → wire `cardLoopVideo` (see doctrine § Store media pipeline).

## Output contract

```
PPQ <id> stage=P# · blockers=<n> · next=<one line>
```

Then ≤10 loose ends. Stop for pick unless ADVANCE was explicit.

## Compose

→ `/ux-prefs` (P2) → packaging/product-template (P4) → `/ship-gate` (P6) → store activate → `media-prompt` + `make-card-loop.ps1` (hover loop)

## Triple Surface

| Surface | Path |
|---------|------|
| Cursor (canonical) | `agent-skills/.cursor/skills/powercore-product-qualify/SKILL.md` |
| Claude Code twin | `<project>/.claude/skills/powercore-product-qualify/SKILL.md` |
| GPT / any-agent paste | `agent-skills/docs/gpt-paste/POWERCORE_PRODUCT_QUALIFY_GPT_PASTE.md` |

New skills must ship all three — see `powercore-skill-gap` + `scaffold_surfaces`.
