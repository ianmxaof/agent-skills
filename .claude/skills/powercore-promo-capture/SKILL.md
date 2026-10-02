---
name: powercore-promo-capture
description: >-
  Captures real on-screen screenshots and short window recordings of PowerCore products into promo-captures/ with sidecars, staged for promo and PPQ demoVideo. Invoke with /promo-capture, promo shot, promo clip, or after a UI slice lands.
---

# PowerCore Promo Capture — Claude Code twin

Thin mirror of `agent-skills/.cursor/skills/powercore-promo-capture/SKILL.md` (canonical).
GPT / chat-only twin: `agent-skills/docs/gpt-paste/POWERCORE_PROMO_CAPTURE_GPT_PASTE.md`.

## When to invoke

`/promo-capture`, "promo shot", "promo clip", a UI slice just landed, or PPQ `demoVideo` media is needed.
**Skip:** TBCC island / continuous recording; Buffer / store `active` / upload steps.

## Commands (low freedom — use verbatim, from `powercore-ops/`)

```powershell
py -3.13 -m tools.capture list-windows
py -3.13 -m tools.capture shot --window "<title>" --product <id> --tag <slug> [--dry-run]
py -3.13 -m tools.capture record start --window "<title>" --product <id> --tag <slug> [--max-seconds N]
py -3.13 -m tools.capture record stop
py -3.13 -m tools.capture keep keep|discard <sidecar.json>
```

Library: `powercore-ops/promo-captures/<product>/<YYYY-MM-DD>/` (media git-ignored, sidecars tracked). Needs Pillow, and ffmpeg on PATH for clips.

## Rules

- **Real pixels only:** launch the product, unobscured, real media playing, fixed window size, cursor out of frame. No `widget.grab()` / test patterns.
- Records are bounded (90s default, 300s ceiling). Never continuous.
- Do not upload, post to Buffer, set store `active`, or invent pricing/doctrine. Stop for the operator.
- Do not touch other agents' UI branch files.
- Compose: → `powercore-product-qualify` (demoVideo); ← `powercore-skill-gap`.
- Load the Cursor canonical body when procedure detail is missing here.
- After a grind phase needing review: reverse report + `PASTE INTO CURSOR`.

## Output contract

1. Product, window, geometry · 2. Media + sidecar paths · 3. keep/discard per capture · 4. Suggested next step, then stop.

## Triple Surface

Keep in sync with Cursor skill + GPT paste when version-bumping.
