# PowerCore Promo Capture — GPT / any-agent paste twin

Self-contained procedure for ChatGPT, Gemini, Grok, Claude web, or any agent **without**
repo file access. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/powercore-promo-capture/SKILL.md`
- Claude Code: `<project>/.claude/skills/powercore-promo-capture/SKILL.md`

## When to paste this

You need real screenshots or a short clip of a running PowerCore desktop product for promo or a store `demoVideo`, and the agent cannot read the repo. The human runs the commands; the agent plans and reviews.

## Paste template

```
You are running the PowerCore skill "powercore-promo-capture" (PowerCore Promo Capture) with ZERO prior chat context.

PURPOSE:
Get real-pixel screenshots and short (<=90s) window recordings of a running PowerCore product into a dated library with sidecar metadata.

DONE WHEN:
Each requested shot/clip exists under powercore-ops/promo-captures/<product>/<YYYY-MM-DD>/ with a .json sidecar, and the human has marked each keep or discard.

INPUTS THE HUMAN MUST FILL:
- product id (e.g. powerplayer)
- window title substring (from `py -3.13 -m tools.capture list-windows`)
- tag slug per capture (e.g. trim-open)

RULES:
- Do not invent file paths or command output you were not given.
- Real pixels only: the product must be running, unobscured, with real content playing (no black frames, no test patterns). Never use widget.grab().
- Recordings are short and bounded (default 90s, hard ceiling 300s). Never continuous.
- MUST NOT upload, post to Buffer, set a store product active, or invent pricing/doctrine. Stop for the human before any such step.
- Windows only.
- STORE CARD: card-hybrid/card-still read only kept captures and write only to product-loops/_inbox or product-cards/_variants. NEVER overwrite a live product-cards/<slug>.png or write product-loops/<slug>.webm; publishing needs a separate human ACK.
- DISCLOSURE: if a source capture's notes say STAGED / synthesised / simulated / mock, the output sidecar carries that note and disclosure_required=true; any listing or hover copy must keep it. Default blend is inset (pip hides dark cards).

COMMANDS (run by the human from powercore-ops/; needs Pillow, and ffmpeg on PATH for clips):
  py -3.13 -m tools.capture list-windows
  py -3.13 -m tools.capture shot --window "<title>" --product <id> --tag <slug> [--dry-run]
  py -3.13 -m tools.capture record start --window "<title>" --product <id> --tag <slug> [--max-seconds N]
  py -3.13 -m tools.capture record stop
  py -3.13 -m tools.capture keep keep|discard <path-to-sidecar.json>
  # store card (kept captures only; always --dry-run first):
  py -3.13 -m tools.capture card-hybrid --slug <slug> --card <product-cards/slug.png> --from <record-sidecar.json> --capture-start <s> [--blend inset|pip|softcut|wipe] [--bounce-slug <slug>-hybrid-smoke]
  py -3.13 -m tools.capture card-still  --slug <slug> --card <product-cards/slug.png> --from <sidecar.json> [--blend inset|pip]

OUTPUT CONTRACT:
1. Product, window title, geometry used
2. Media + sidecar paths written
3. Keep/discard per capture
4. Suggested next step (PPQ demoVideo or edit handoff); then stop and ask the human

PROCEDURE:
1. Human launches the product and confirms it appears in list-windows.
2. Stage: real content playing, fixed window size (e.g. 1280x720), no overlapping windows, cursor out of frame.
3. Dry-run the shot to confirm the resolved window and output path.
4. Take the shot, or record start -> demo -> record stop.
5. Human reviews the media and runs keep keep|discard on each sidecar.
6. Optional: card-hybrid / card-still on a kept capture (dry-run first), bounce under a smoke slug.
7. Stop; do not edit, upload, or publish.
```

## Sync rule

When the Cursor or Claude twin changes Output Contract / triggers / fence rules,
update this paste in the same change set.
