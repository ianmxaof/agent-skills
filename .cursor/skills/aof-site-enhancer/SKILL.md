---
name: aof-site-enhancer
description: >-
  Port or build AOF-branded site enhancers for TBCC extension (passive content
  scripts) plus standalone Tampermonkey builds for promo. Use when the user asks
  for userscript, site enhancer, Sleazy Fork, bunkr/erome/thisvid passive
  install, or AOF mainhub/subscriptions bot metadata.
---

# AOF Site Enhancer

## Dual track (always both)

1. **Tampermonkey** — `tbcc/tools/<site>-enhancer/<site>-enhancer.user.js` (promo + name recognition)
2. **TBCC extension** — `tbcc/extension/<site>-enhancer.js` (passive install, no TM required)

Build: `node tbcc/tools/bunkr-enhancer/build.mjs` (pattern for other sites).

## Extension wiring checklist

1. Wrap body in `tbccWaitForModule('<module_id>', function () { … })`
2. Register in `tbcc/extension/tbcc-extension-modules.js` (`MODULES` array)
3. Add `content_scripts` block in `tbcc/extension/manifest.json` (bump version)
4. Optional: `tbccBindModuleDisableListener(moduleId, teardown)`
5. Shared libs as needed: `tbcc-suite-rail.js`, `tbcc-browse-intel-common.js`

## AOF promo (metadata + in-app)

| Surface | Value |
|---------|-------|
| Main hub | `https://telegram.me/aofmainhub` |
| VIP / subscriptions | `@aofsubscriptions_bot` |
| Loot taste (optional) | `@aof_lootgod_bot` — only when sampler angle fits |

- Put hub + VIP in `@description` on Tampermonkey builds
- Optional dismissible footer chip in-app (one CTA per surface — see `tbcc/docs/AOF_PLACEMENT_DOCTRINE.md`)
- ZIP / watermark naming: `telegram.me/aofmainhub` via `tbcc-promo-watermark.js`

## Tampermonkey publish hygiene

- Publish to **Sleazy Fork** (adult), not Greasy Fork
- **No** `@updateURL` / `@downloadURL` on community forks
- Prefer `@grant none`; use `fetch` + `localStorage` instead of GM APIs
- Docs: `tbcc/docs/<site>-enhancer/SLEAZY_FORK_PUBLISH.md` (copy from erome-enhancer)

## Reference implementation

- Erome: `tbcc/tools/erome-enhancer/`, `tbcc/extension/erome-enhancer.js`
- Bunkr: `tbcc/tools/bunkr-enhancer/`, `tbcc/extension/bunkr-enhancer.js`

## Inbox intake

Drop candidate `.user.js` in `tbcc/userscripts/inbox/<site>/` before merge. Note `@match`, `@grant`, license, keep/merge/drop.

## Backend reuse

Before reimplementing site APIs, check:

- `tbcc/backend/app/services/crawler_resolver.py`
- `tbcc/extension/gallery.js`

## Attribution

MIT upstream → `tbcc/docs/<site>-enhancer/NOTICE.md`
