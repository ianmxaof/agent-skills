---
name: tbcc-sleazyfork-userscript
description: >-
  Build, validate, and publish AOF Tampermonkey userscripts on Sleazy Fork.
  Exact header metadata, @description suffix, Markdown Additional info blocks,
  upload form copy, promo-chip requirement, and sf-format line splitting. Use
  when creating or publishing AOF userscripts, Sleazy Fork listings, platform
  enhancers, or when the user mentions SF upload fields, promo chip, or
  aofmainhub bot links.
---

# TBCC Sleazy Fork userscript skill

Canonical repo docs (read before publishing):

| Doc | Purpose |
|-----|---------|
| `tbcc/docs/SLEAZY_FORK_CATALOG.md` | Index, versions, upload paths, per-script summaries |
| `tbcc/docs/SLEAZY_FORK_LISTINGS.md` | **Additional info** Markdown paste blocks (all 12 scripts) |
| `tbcc/docs/bunkr-enhancer/SLEAZY_FORK_PUBLISH.md` | Deep-dive example publish kit |
| [reference.md](reference.md) | Header template, SF form fields, footer HTML links, promo chip |
| `tbcc/docs/SLEAZY_FORK_SKILL_REFERENCE.md` | Same templates (repo copy) |

Build all artifacts:

```powershell
cd C:\Powercore-repo-main\telegram_bot2\tbcc
node userscripts/sleazyfork-build/build.mjs
```

Validate one built script:

```powershell
node userscripts/sleazyfork-build/validate-sf-artifact.mjs userscripts/coomer-enhancer/coomer-enhancer.user.js
```

---

## When to use

- New platform enhancer or new SF listing for an AOF script
- Operator asks for Sleazy Fork title, description, Additional info, or upload copy
- Auditing whether a `*.user.js` is SF-ready (header, promo chip, no third-party update URLs)
- After merging inbox scripts into `userscripts/<platform>-enhancer/`

**Skip:** Greasy Fork (non-adult), non-AOF upstream forks, extension-only bundles (`extension/*.js` without Tampermonkey header).

---

## AOF brand rules (non-negotiable)

### 1. Userscript header (`// ==UserScript==`)

Every AOF SF script uses **exactly** these meta lines (plus `@match`, `@grant`, optional `@require` / `@connect` / `@exclude`):

```
// @namespace    https://t.me/aofmainhub
// @homepageURL  https://t.me/aofmainhub
// @supportURL   https://t.me/aofsubscriptions_bot
// @author       AOF Network
// @license      MIT
```

- **Namespace / homepage** → discovery hub [`t.me/aofmainhub`](https://t.me/aofmainhub)
- **Support URL** → packs & VIP [`t.me/aofsubscriptions_bot`](https://t.me/aofsubscriptions_bot)
- Title pattern: `AOF <Site> Enhancer — <Subtitle>` (em dash `—`, not hyphen)
- **Never** ship `@updateURL` / `@downloadURL` on AOF-published scripts

Generate headers via `renderAofHeader()` in `tbcc/userscripts/shared/promo-chip.mjs` or edit `manifest.json` → `tm.name` / `tm.description` / `version` then rebuild.

### 2. Short description (`@description` + SF Description field)

One line. Feature summary first, then **verbatim suffix**:

```
Free drops: t.me/aofmainhub · Packs & VIP: t.me/aofsubscriptions_bot
```

Middle dot `·` between the two Telegram refs (not bullet, not pipe).

### 3. In-page AOF link popup (promo chip) — **always**

Every AOF Tampermonkey build **must** embed `tbcc/extension/tbcc-aof-promo-chip.js` and call mount on load.

Platform enhancers: handled by `platform-enhancer-build.mjs` (`readPromoChip()` + boot block).

Boot pattern (site id from manifest `promoSiteId`):

```javascript
(function () {
  'use strict';
  function mountPromo() {
    try {
      globalThis.TBCCAofPromoChip?.mount?.({ siteId: 'coomer', lead: 'More drops' });
    } catch (_) {}
  }
  if (document.body) mountPromo();
  else document.addEventListener('DOMContentLoaded', mountPromo, { once: true });
})();
```

Default chip links (HTML `<a>` popup, bottom-center):

| Label | URL |
|-------|-----|
| t.me/aofmainhub | `https://t.me/aofmainhub` |
| Packs & VIP | `https://t.me/aofsubscriptions_bot` |
| Free loot roll | `https://t.me/aof_lootgod_bot?start=loot_free` |

Lead text: manifest `promoLead` (default `More on AOF`). Dismissible per-site via localStorage — that is OK; chip must **mount on every fresh visit** until dismissed.

**Validation:** built file contains `TBCCAofPromoChip` and `mountPromo` (or `TBCCAofPromoChip?.mount`).

### 4. Sleazy Fork code format

`formatForSleazyFork()` in `tbcc/userscripts/shared/sf-format.mjs` splits lines >500 chars so SF does not flag minified code. All `*.user.js` from `sleazyfork-build` and platform enhancer builds pass through this.

---

## Sleazy Fork upload form — field copy

Post: [sleazyfork.org/scripts/new](https://sleazyfork.org/en/scripts/new)

| SF field | What to paste | Source |
|----------|---------------|--------|
| **Name** | `AOF … — …` title | `manifest.json` → `tm.name` or catalog |
| **Description** | Same as `@description` (with AOF suffix) | `tm.description` |
| **Additional info** | Markdown block | `SLEAZY_FORK_LISTINGS.md` section for script, or generate from [reference.md](reference.md) template |
| **License** | MIT | always |
| **Adult content** | **Yes** | always for AOF site enhancers |
| **Code** | Full built `userscripts/.../*.user.js` | after `node userscripts/sleazyfork-build/build.mjs` |
| **Language** | JavaScript | |
| **Application** | Tampermonkey | |

**Additional info:** toggle **Markdown** mode. Copy from opening `#` heading through the footer italic line `*The script itself does not phone home.*` inclusive.

---

## Workflow: new or updated AOF enhancer

```
- [ ] 1. Drop upstream into tbcc/userscripts/inbox/<site>/ (+ NOTES.md row)
- [ ] 2. Add feature filename to userscripts/<site>-enhancer/manifest.json → features[]
- [ ] 3. Bump manifest version (patch for features, minor for new site)
- [ ] 4. Update tm.description + tm.match/grant/connect/require if needed
- [ ] 5. node userscripts/<site>-enhancer/build.mjs  (or full sleazyfork-build)
- [ ] 6. node userscripts/sleazyfork-build/validate-sf-artifact.mjs <path>
- [ ] 7. Update SLEAZY_FORK_CATALOG.md + SLEAZY_FORK_LISTINGS.md section
- [ ] 8. Paste SF form fields from listings doc; upload code
- [ ] 9. Tell operator: disable duplicate upstream scripts + TBCC extension module for same site
```

### manifest.json source of truth

| Build style | Edit |
|-------------|------|
| Platform enhancers | `userscripts/<platform>-enhancer/manifest.json` |
| Bunkr | `userscripts/bunkr-enhancer/build.mjs` → `TM_HEADER` |
| FetLife community | `userscripts/packages/fetlife-suite/manifest.community.json` |
| Erome / ThisVid community | `userscripts/sleazyfork-build/build.mjs` |

---

## Workflow: generate Additional info for a **new** script

Use the template in [reference.md](reference.md):

1. `# AOF <Site> — <tagline>` H1
2. One-paragraph intro (merged scripts, community build, localStorage)
3. `## What it does` — bullet list with **bold** feature names
4. `## Quick start` — numbered 1–3 (install, disable dupes, visit site)
5. `## Privacy` — grants, fetches, no AOF telemetry
6. `## Credits` — upstream authors + **Altar of Flesh (AOF)**
7. `---` then **verbatim AOF footer** (Loot God, VIP bot, Main Hub links)

Append new section to `tbcc/docs/SLEAZY_FORK_LISTINGS.md` and row to catalog index.

---

## Pre-publish checklist (every script)

1. Upload **`userscripts/.../*.user.js`** — not `extension/*.js` alone
2. Header: AOF namespace/homepage/support, **no** third-party `@updateURL` / `@downloadURL`
3. `TBCCAofPromoChip` present (in-page popup)
4. `formatForSleazyFork` applied (no 500+ char lines)
5. Adult content: **Yes**
6. Operator disables duplicate userscripts + TBCC extension module for same site

---

## Related code

| File | Role |
|------|------|
| `userscripts/shared/platform-enhancer-build.mjs` | Merge inbox features + promo chip + AOF header |
| `userscripts/shared/promo-chip.mjs` | `AOF_TM_META`, `renderAofHeader`, `readPromoChip` |
| `userscripts/shared/sf-format.mjs` | Line split for SF |
| `extension/tbcc-aof-promo-chip.js` | In-page link popup |
| `userscripts/sleazyfork-build/build.mjs` | Rebuild all SF artifacts |
| `userscripts/sleazyfork-build/validate-sf-artifact.mjs` | SF readiness gate |
