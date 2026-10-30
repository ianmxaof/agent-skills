---
name: powercore-open-dir-secrets
description: >-
  Probes a host for open directory listings, inventories config/secret files,
  identifies credential prefixes, and verifies exposures on provider GET auth
  endpoints. Use for /open-dir-secrets, open dir secrets, or Hub Scan this tab
  · secrets in open dirs.
---

# PowerCore Open-Dir Secrets

Read-only Hub `[run]` scanner (peer of repo-trust / feature-scan). Five stages:
probe → inventory → identify → verify → report. Tags: LIVE | stale | unverified.

## CLI

```powershell
python "$env:USERPROFILE\.cursor\skills\powercore-open-dir-secrets\scripts\odsec.py" --json "https://example.com"
```

## Vincent Hub

`/run open-dir-secrets` on the target site’s own tab (`needs_tab_url`). Hub injects
the tab URL + `--json`. Do not ask for PowerShell when Hub already ran the skill.

## Constraints

- GET only. Full keys memory-only during verify; stdout/JSON redacted.
- No consent gates in code. Authorization is operational, outside the skill.
- Fixtures: prefix + x-fill only.
