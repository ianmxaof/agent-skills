---
name: powercore-promo-capture
description: >-
  Captures real on-screen screenshots and short window recordings of PowerCore products into promo-captures/ with sidecars, staged for promo and PPQ demoVideo. Invoke with /promo-capture, promo shot, promo clip, or after a UI slice lands.
---

# PowerCore Promo Capture

Canonical Cursor skill. Triple Surface (locked): Cursor (this file) + Claude Code twin
under consuming repos' `.claude/skills/powercore-promo-capture/` + GPT paste at `agent-skills/docs/gpt-paste/POWERCORE_PROMO_CAPTURE_GPT_PASTE.md`.

## Purpose

Get real-pixel screenshots and short (≤90s) window recordings of a running PowerCore product into the dated `promo-captures/` library with sidecar metadata, so promo and PPQ `demoVideo` have raw material without the operator sitting in OBS.

## Canonical

| Piece | Path |
|-------|------|
| CLI | `cd powercore-ops; py -3.13 -m tools.capture {shot,record start|stop,keep,list-windows}` |
| CLI doc | `powercore-ops/tools/capture/README.md` |
| Library | `powercore-ops/promo-captures/<product>/<YYYY-MM-DD>/<HHMMSS>_<tag>.png|mp4` + `.json` sidecar |
| Needs | Windows, Pillow (shots), `ffmpeg` on PATH or `POWERCORE_FFMPEG` (records) |

## When to invoke

- Trigger phrases: `/promo-capture`, `/powercore-promo-capture`, "promo shot", "promo clip", "capture the demo", "screenshot PowerPlayer for the store"
- A product UI slice just landed and needs store/promo art
- PPQ P6 media: optional 30–60s `demoVideo` (`design/powercore-product-qualification.md`)
- **Skip:** TBCC island / always-on or continuous recording; Gemini card hover loops (use the store-media pipeline); anything that would upload, post to Buffer, or flip store `active`.

## Execution Profile

- Freedom: **medium** on staging (what to show, order of clicks); **low** on CLI invocation (use the commands below verbatim)
- Mode: Agent

## Harness attach

| Surface | Value |
|---------|-------|
| **MCP** | none |
| **Hooks** | endgates on stop |
| **Memory** | disk: `promo-captures/` sidecars |
| **Compose** | → `powercore-product-qualify` (demoVideo row); ← `powercore-skill-gap` (scaffold/sync) |

## Behavioral rules

- Reason by: **real pixels only** — the tool crops the desktop composite, so the target window must be launched, unobscured, and on top. Never use Qt `widget.grab()` (black VLC frames) or test patterns.
- Avoid: continuous recording, unbounded records, uploading/posting, setting store `active`, inventing pricing or copy doctrine, touching other agents' UI branch files.
- Prioritize: reproducible geometry (set the window size first), cursor hidden (tool does not draw it), media actually playing for VLC-backed products, an explicit keep/discard verdict per capture.

## Output contract

1. Product, window title, and geometry used
2. Paths of each media + sidecar written under `promo-captures/<product>/<date>/`
3. Keep/discard status per capture (`keep` field: null = unreviewed)
4. Suggested next step (PPQ `demoVideo`, or edit handoff) — stop for the operator

## Triple Surface

| Surface | Path |
|---------|------|
| Cursor (canonical) | `agent-skills/.cursor/skills/powercore-promo-capture/SKILL.md` |
| Claude Code twin | `<project>/.claude/skills/powercore-promo-capture/SKILL.md` |
| GPT / any-agent paste | `agent-skills/docs/gpt-paste/POWERCORE_PROMO_CAPTURE_GPT_PASTE.md` |

Bump all three when tightening. Scaffold:

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-promo-capture --check
```

## Procedure

1. **Launch** the product (not a tray/bot stack on the operator PC — see island policy). Confirm it is visible: `py -3.13 -m tools.capture list-windows`.
2. **Stage:** put real content on screen (play actual media; no black/test frame), set a fixed window size (e.g. 1280x720), close overlapping windows, dismiss popups, leave the cursor out of frame.
3. **Check:** `py -3.13 -m tools.capture shot --window "<title>" --product <id> --tag <slug> --dry-run` to confirm the resolved window and output path.
4. **Shot:** same command without `--dry-run`. For clips: `record start ... [--max-seconds N]`, perform the demo, then `record stop` (cap is 90s default, 300s ceiling; never record unbounded).
5. **Review** the PNG/mp4. Then `py -3.13 -m tools.capture keep keep|discard <sidecar.json>`. Delete discarded media locally; sidecars stay.
6. **Stop** for the operator before any edit, upload, or store step. For `demoVideo`, hand the kept clip to `powercore-product-qualify`.
