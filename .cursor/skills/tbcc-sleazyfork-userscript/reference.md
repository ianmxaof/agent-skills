# Sleazy Fork reference — AOF userscripts

## Shared userscript header block

Paste after `@name`, `@version`, `@description`; before `@match`:

```
// @namespace    https://t.me/aofmainhub
// @homepageURL  https://t.me/aofmainhub
// @supportURL   https://t.me/aofsubscriptions_bot
// @author       AOF Network
// @license      MIT
```

Full minimal example:

```
// ==UserScript==
// @name         AOF Example Enhancer — Suite
// @namespace    https://t.me/aofmainhub
// @version      1.0.0
// @license      MIT
// @author       AOF Network
// @description  Does the thing. Free drops: t.me/aofmainhub · Packs & VIP: t.me/aofsubscriptions_bot
// @homepageURL  https://t.me/aofmainhub
// @supportURL   https://t.me/aofsubscriptions_bot
// @match        https://example.com/*
// @grant        none
// @run-at       document-idle
// ==/UserScript==
```

---

## Description suffix (verbatim)

Append to every `@description` and SF **Description** field:

```
Free drops: t.me/aofmainhub · Packs & VIP: t.me/aofsubscriptions_bot
```

---

## Additional info — Markdown template (new script)

Replace `{PLACEHOLDERS}`. Toggle **Markdown** on Sleazy Fork.

```markdown
# AOF {SITE} — {TAGLINE}

{One paragraph: what merged, community build, settings stay in browser.}

## What it does

- **{Feature 1}** — {one line}
- **{Feature 2}** — {one line}

## Quick start

1. Install with Tampermonkey or Violentmonkey.
2. Disable duplicate {SITE} userscripts (and the TBCC {SITE} extension module if you use both).
3. Open {SITE URL} — features load with the page.

## Privacy

- {Grants or @grant none}
- {What hosts are fetched}
- No AOF telemetry in this build

## Credits

{Upstream authors}. Merged and packaged by **Altar of Flesh (AOF)**.

---

Same crew, different surface — if this script earns its keep:

**Free pull:** [Loot God](https://t.me/aof_lootgod_bot) ([@aof_lootgod_bot](https://t.me/aof_lootgod_bot))

**VIP / checkout:** [@aofsubscriptions_bot](https://t.me/aofsubscriptions_bot)

**Network map:** [AOF Main Hub](https://t.me/aofmainhub)

*The script itself does not phone home.*
```

### Footer block (copy verbatim — do not edit links)

Use exactly this after `---` in every listing:

```markdown
---

Same crew, different surface — if this script earns its keep:

**Free pull:** [Loot God](https://t.me/aof_lootgod_bot) ([@aof_lootgod_bot](https://t.me/aof_lootgod_bot))

**VIP / checkout:** [@aofsubscriptions_bot](https://t.me/aofsubscriptions_bot)

**Network map:** [AOF Main Hub](https://t.me/aofmainhub)

*The script itself does not phone home.*
```

---

## Telegram link map

| Purpose | URL | Used in |
|---------|-----|---------|
| Main hub / namespace / homepage | `https://t.me/aofmainhub` | `@namespace`, `@homepageURL`, footer |
| Packs & VIP / support | `https://t.me/aofsubscriptions_bot` | `@supportURL`, footer, chip label "Packs & VIP" |
| Free loot roll | `https://t.me/aof_lootgod_bot?start=loot_free` | Promo chip only |
| Description text refs | `t.me/aofmainhub` · `t.me/aofsubscriptions_bot` | Plain text in `@description` (no https) |

---

## In-page promo chip (mandatory)

Source: `tbcc/extension/tbcc-aof-promo-chip.js`

Rendered as fixed bottom-center bar with clickable HTML links. Default mount:

```javascript
globalThis.TBCCAofPromoChip?.mount?.({
  siteId: 'onlyfans',      // manifest promoSiteId
  lead: 'More on AOF',     // manifest promoLead
  includeLoot: true        // default; third link = loot bot
});
```

Build pipeline inlines the full promo-chip IIFE before feature code, then appends boot mount.

---

## Title naming

```
AOF {SiteOrBrand} Enhancer — {Short capability list}
AOF {Site} Performer Search          # single-purpose (Stash)
AOF Link Bypass — GPLinks & Shorteners
```

Use em dash `—` (U+2014), not `-`.

---

## SF upload quick reference

| Field | Value |
|-------|-------|
| Name | Title from catalog |
| Description | `@description` line |
| Additional info | Markdown from `SLEAZY_FORK_LISTINGS.md` |
| License | MIT |
| Adult content | Yes |
| Code | Built `*.user.js` from `tools/` |
