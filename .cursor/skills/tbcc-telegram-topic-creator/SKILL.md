---
name: tbcc-telegram-topic-creator
description: Creates a new forum topic in an existing Telegram supergroup, or spins up a brand-new forum-enabled group with initial topics, via the TBCC backend's Telethon-backed API. Invoke as /tbcc-telegram-topic-creator, or on requests like "make a new topic in AOF Models", "create a topic called X in group Y", "spin up a new group with topics for Z".
---

# TBCC Telegram Topic Creator

Calls the TBCC backend's `/telegram-groups` endpoints (Telethon under the hood) to create forum topics in an existing group, or create a brand-new forum-enabled group with initial topics.

## When to invoke

- Trigger phrases: `/tbcc-telegram-topic-creator`, "create a topic in [group]", "add a topic called X to [group]", "make a new group with topics for X"
- Situational: operator wants to expand an existing community (e.g. AOF Models `-1004332993350`) with a new topic, or bootstrap a new forum-enabled group from scratch

## Prerequisites

- Backend API reachable — cloud-only per operator policy: `https://api.powercore.app` (never spin up local API/bots to test this; if you must smoke-test, use the island directly)
- Telethon admin session must be logged in (`/health/telegram` returns `ok: true`) — the account tied to `admin.session` must already be a member/admin of the target group with rights to manage topics
- Creating a **new group** makes the acting account (see Multi-account below) the owner — confirm with the operator before calling `create-group`, since group creation is not easily reversible (Telegram allows deleting supergroups, but it destroys all content)

## Multi-account (`account` field)

Both endpoints take an optional `"account"` field (default `"primary"`) selecting which Telegram identity acts. This lets the operator create groups/topics under a different logged-in account instead of the main admin one.

- **`"primary"`** — the existing `admin.session` account (tbcc's own `API_ID`/`API_HASH`). No setup needed.
- **Any other name** (e.g. `"account2"`, `"account3"`) — an account with its **own independent Telethon login**, registered in `tbcc/.env`:
  ```
  TBCC_TELEGRAM_PROFILES_JSON={"account2": "account2", "account3": "account3"}
  ```
  (keys are the `account` value the API expects; values are the `.session` file stem under `tbcc/backend/`). Connects with tbcc's own `API_ID`/`API_HASH` by default — same as every other Telethon client in this codebase.

Check what's configured and confirm each resolves to the expected Telegram user:
```bash
curl -sS https://api.powercore.app/telegram-groups/accounts
```

### Adding a new profile — one independent login per account, never a cloned session

**AyuGram (or any desktop client) can keep every account logged in normally — that's unrelated to this.** Each extra account TBCC acts as needs its own **separate Telethon device authorization**, the same way `admin.session` is one device and your phone is another. Telegram fully supports that running concurrently.

```bash
cd tbcc/backend
python scripts/login_telegram_profile.py --profile account2 --method qr
# or: --method code --phone +15551234567
```

QR method: scan the printed URL from the **already-logged-in** account in that Telegram app (Settings → Devices → Link Desktop Device). Code method: prompts for the SMS/Telegram code (and 2FA password if set). This is interactive — cannot be scripted headlessly; the operator runs it once per extra account. Writes `<stem>.session` under `tbcc/backend/` and does not touch admin/poster/import sessions. Not deployed automatically (`*.session` is excluded from `deploy-island-live.ps1`) — copy it to the island manually, same as `admin.session`.

**Never extract another client's existing AuthKey for this** (tdata, AyuGram, or otherwise) — even with the right API credentials, using one AuthKey concurrently from two hosts gets it killed by Telegram's duplicate-key detection. This happened in production on 2026-09-04/05: `scripts/import_ayugram_sessions.py` (tdata → AuthKey clone, via the now-legacy `scripts/_tdata_auth_extract.py`) was used to pull 3 accounts' keys out of AyuGram and run them from the island; the first live API call from the island logged **two of the three source accounts out of AyuGram entirely** (same key, two locations, at once). Those scripts still exist for historical reference but are **not the path for concurrent-with-AyuGram use** — use `login_telegram_profile.py` instead. If a profile's session ever needs the legacy Telegram Desktop api_id (`2040`) for some other reason, it's available only via the explicit `TBCC_TELEGRAM_LEGACY_DESKTOP_PROFILES=account2,...` opt-in in `app/services/telegram_profiles.py` — never the default.

## Endpoints

### `POST /telegram-groups/create-topic`

Create a topic in an **existing** group.

```json
{
  "group_id": -1004332993350,
  "topic_name": "New Models Q1",
  "icon_color": 16766590,
  "icon_emoji_id": null,
  "description": "optional"
}
```

`group_id` is the full negative supergroup ID (visible in the group's info panel, e.g. `-1004332993350` for AOF Models). `icon_color` is an RGB int (e.g. `0xFF0000` = `16711680` for red) — omit for Telegram's default color rotation. `icon_emoji_id` is a **custom emoji document ID** (not a literal emoji character) — Telegram's topic API has no field for a plain unicode emoji icon or a text description; both are accepted in the request body but only `icon_emoji_id` has an effect.

Response: `{"ok": true, "topic_id": 123, "topic_name": "...", "group_id": -1004332993350}`

### `POST /telegram-groups/create-group`

Create a **new** forum-enabled supergroup, optionally seeded with topics.

```json
{
  "group_name": "AOF Clips",
  "initial_topics": [
    {"name": "General", "icon_color": 16766590},
    {"name": "Uploads", "icon_color": 65280}
  ]
}
```

Response: `{"ok": true, "group_id": -100..., "group_name": "...", "topics": [{"id": 1, "name": "General"}, ...]}`

## Usage patterns

**Manual (Claude Code / dev session):**
```bash
curl -sS -X POST https://api.powercore.app/telegram-groups/create-topic \
  -H "Content-Type: application/json" \
  -d '{"group_id": -1004332993350, "topic_name": "New Topic"}'
```

**From a bot command:** wire a handler in the relevant bot module (`tbcc/backend/app/bots/`) that POSTs to the same endpoint on an admin-only command — do not duplicate the Telethon call, always go through the API so the shared admin session lock (`import_lock()`) is respected.

**From an automated workflow:** call the endpoint from a Celery task or service the same way — import and call `create_forum_topic()` / `create_group_with_topics()` directly from `app.services.telegram_topic_creator` if already inside the backend process (skip the HTTP hop), otherwise POST to the endpoint.

## Known group reference

- **AOF Models**: `group_id = -1004332993350` — community "『AOF』", 23 chats, forum topics already in use (e.g. `#General` at `t.me/c/4332993350/1`)

## Behavioral rules

- Never call `create-group` without operator confirmation — it's a standing, hard-to-undo asset (new group, new admin surface)
- `create-topic` on an existing group is low-risk/reversible (topics can be closed/deleted in Telegram) — safe to call directly on a clear instruction
- Always use the **cloud** API (`api.powercore.app`), never a local instance — per operator policy, no local Telethon session should ever run on the operator PC
- If `/health/telegram` reports session not logged in (primary), stop and tell the operator to run `python scripts/login_telethon_sessions.py`. If a non-primary `account` reports no session file, tell the operator to run `python scripts/login_telegram_profile.py --profile <name>` — do not attempt to work around either

## Files

| Path | Purpose |
|------|---------|
| `tbcc/backend/app/services/telegram_topic_creator.py` | Telethon calls: `create_forum_topic()`, `create_group_with_topics()` |
| `tbcc/backend/app/services/telegram_profiles.py` | Multi-account client cache/locks; `"primary"` vs. imported profiles |
| `tbcc/backend/app/api/telegram_groups.py` | FastAPI endpoints: `/telegram-groups/create-topic`, `/telegram-groups/create-group`, `/telegram-groups/accounts` |
| `tbcc/backend/scripts/login_telegram_profile.py` | **Use this** for a new extra profile — independent Telethon login (QR/code), never a clone |
| `tbcc/backend/scripts/import_ayugram_sessions.py` | **Legacy — do not use for concurrent-with-AyuGram setups.** Clones a tdata AuthKey; caused the 2026-09-04/05 incident |
| `tbcc/backend/scripts/_tdata_auth_extract.py` | Legacy — tdata decrypt/AuthKey extraction backing the script above (MIT, North-web-dev/tdata-extract) |
