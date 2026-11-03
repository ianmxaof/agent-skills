# PowerCore Product Qualify (PPQ) — GPT / any-agent paste twin

Self-contained procedure for ChatGPT, Gemini, Grok, Claude web, or any agent
**without** repo file access. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/powercore-product-qualify/SKILL.md`
- Claude Code: `<project>/.claude/skills/powercore-product-qualify/SKILL.md`
- Doctrine (when a human can paste excerpts): `powercore-ops/design/powercore-product-qualification.md`

## When to paste this

Store readiness, installer checklist, sellable backlist, `/ppq`, `/qualify`,
or "is this product finished enough to sell under PowerCore?"

## Paste template

```
You are running PowerCore Product Qualification (PPQ) with ZERO prior chat context.

PURPOSE:
Walk a product from incomplete → PowerCore-grade / store-ready using stages
P0–P6. Honest stages for unfinished products. Sellable only at P6 + Ship Gate.

MODES:
- AUDIT (default): scorecard + ≤10 loose ends; stop for human pick
- ADVANCE: close one named stage only when human says so
- BOARD: list products id · stage · packaging · top blocker (from pasted registry)
- SCAFFOLD: new checklist shape only — do not fake covered rows

STAGES (locked ladder):
P0 Scaffold | P1 Core loop | P2 Chrome | P3 Vault/tray | P4 Install |
P5 Onboarding | P6 Store

P4 DESKTOP DEFAULT (sellable package shape):
Buyer zip whose root includes MSI + setup.exe + START_HERE.md
(extensions: MSI n/a; sideload zip + START_HERE still required).
install-dev.ps1 alone is NOT P4.

INPUTS THE HUMAN MUST PASTE:
- product id
- current QUALIFICATION.md excerpt OR "unknown"
- REGISTRY row OR packaging type
- any install/artifact paths already on disk

RULES:
- PPQ ≠ Ship Gate. Green tests ≠ sellable.
- Do not invent evidence; use missed / unknown.
- Judgment ceiling: MUST NOT set store active:true or change pricing.
- Stop after AUDIT scorecard unless human said ADVANCE <stage>.

OUTPUT CONTRACT:
1. One line: PPQ <id> stage=P# · blockers=<n> · next=<one line>
2. ≤10 loose ends (blockers first), each with evidence or unknown
3. Fence: what you will NOT implement this turn
4. Stop for pick

PROCEDURE:
1. Resolve mode (AUDIT default).
2. Map pasted evidence onto P0–P6; lowest unfinished blocker stage wins.
3. Emit scorecard + loose ends.
4. If ADVANCE: only that stage's rows; recompute stage; stop.
```

## Sync rule

When Cursor/Claude PPQ Output Contract or P4 packaging default changes, update this file in the same change set.
