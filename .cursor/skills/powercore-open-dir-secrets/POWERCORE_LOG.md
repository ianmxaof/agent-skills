# POWERCORE_LOG — powercore-open-dir-secrets

## 2026-10-30 — Maverick strike

**What:** Ship `open-dir-secrets` scanner (`odsec.py`) as a Maverick strike — five stages
(probe / inventory / identify / verify / report), GET-only, redacted-at-write, Hub `[run]`
peer of repo-trust / feature-scan. Diplomat wraps; does not unwrap.
**Why:** Defensive config-audit class (gitleaks / nuclei exposed-config / trufflehog verify).
Operator-selected hosts; authorization outside code.
**Risk:** Diplomat may flag verify-against-provider as dual-use; contract + this LOG are the
sanctioned channel — code ships as specified.
**Revert:** delete `powercore-open-dir-secrets/` (+ later Phase 2 registry/present/Hub allowlist).
**Watch:** Phase 2 Hub `prepareTrustScanArgv` allowlist; no consent gates; exit 0 always.

## 2026-10-30 — sendgrid verify row kept as shipped

**What:** `PROVIDERS["sendgrid"]` remains `("SG.", "https://api.sendgrid.com/v3/scopes")`
exactly as Artifact 1. No code change. Non-200/401 (including 403) → `live: null` / unverified.
**Why:** Phase 1 ACK locked the row; 403→unverified is already the default “other status” path.
**Risk:** SendGrid may return 403 for some valid keys on `/v3/scopes` → false unverified, not
false LIVE. Acceptable until a cheaper GET auth endpoint is chosen later.
**Revert:** n/a (no-change). Future endpoint swap is a new LOG + code change.
**Watch:** smoke/CI must not assert a specific sendgrid verify outcome.

## 2026-10-30 — inventory path join: no char-class lstrip on hrefs

**What:** Artifact used `href.lstrip("./")`, which strips every leading `.`/`/` char and
turns `.env` into `env`. Replaced with prefix-only `./` trim so dotfiles stay intact.
**Why:** Without this, open-dir listings never fetch `.env` / `.env.bak` — core miss.
**Risk:** Low; only changes relative href normalization.
**Revert:** restore `lstrip("./")` (breaks dotfile inventory).
**Watch:** smoke must include a `.env` href and show a redacted row.

## 2026-10-30 — PLACEHOLDER dropped bare `xxxx` substring

**What:** Artifact `PLACEHOLDER` included `xxxx`, which also matched hard-constraint smoke
dummies (`sk-` + 40× `x`). Pattern is now `YOUR_|changeme|placeholder|example|TODO` only.
**Why:** Without this, mandated prefix+x-fill fixtures never classify; smoke cannot pass.
**Risk:** A real listing whose key material literally contains `xxxx` as filler may now classify
(still redacted; verify still runs). Rare vs blocked smoke.
**Revert:** restore `xxxx` in `PLACEHOLDER` and change smoke dummies to non-x fill (needs ACK).
**Watch:** smoke `.env` must stay prefix + x-fill only — no realistic entropy.
**Rule used:** remove the `xxxx` alternation from the PLACEHOLDER regex; leave
`YOUR_|changeme|placeholder|example|TODO` intact so doc-template / instructions text
still fails closed (those tokens mark non-live placeholders, not x-fill dummies).

## 2026-10-30 — Hub core: prepareTrustScanArgv allowlist +id

**What:** Add `open-dir-secrets` to `powercore-browser-hub/extension/vincent-skills.js`
`prepareTrustScanArgv` allowlist (same any-https inject branch shape as website-clone /
feature-scan: `--json` + tab URL). No `network_capture`. Zero edits to the repo-trust path.
**Why:** `needs_tab_url` in present is presentation-only; without this allowlist Hub never
injects the tab URL for `/run open-dir-secrets`.
**Risk:** Wrong allowlist shape could break feature-scan inject — verify feature-scan branch
unchanged; only add `isOdsec` parallel to `isAesthetic`.
**Revert:** remove `isOdsec` / hint / gate inclusion; leave present+registry.
**Watch:** extension reload after edit; `/run feature-scan` still injects tab URL.
