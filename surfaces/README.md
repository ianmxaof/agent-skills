# Surfaces (operator tooling catalog)

Living home for **non-agent** tooling we maintain alongside skills: Windhawk mods, userscripts mirrors, and later partable product slices.

This is inventory + working copies. Runtime install paths stay where the tools expect them (e.g. `%ProgramData%\Windhawk\ModsSource`).

## Layout

| Path | What |
|---|---|
| `windhawk/` | Installed mod sources + settings snapshot |
| `userscripts/` | Optional mirrors / notes (canonical TBCC enhancers stay in `telegram_bot2/tbcc/userscripts/`) |
| `products/` | *(planned)* API-worthy slices parted from extension / dashboard / second-brain |

## Windhawk

- **Source snapshot:** `windhawk/ModsSource/*.wh.cpp` (from `%ProgramData%\Windhawk\ModsSource`)
- **Pack:** `windhawk/windhawk-mods-pack.zip`
- **Settings export:** `windhawk/settings/windhawk-settings.reg` (`HKLM\SOFTWARE\Windhawk`)

Refresh from a live install:

```powershell
$dest = "C:\Powercore-repo-main\agent-skills\surfaces\windhawk"
Copy-Item "$env:ProgramData\Windhawk\ModsSource\*" "$dest\ModsSource\" -Force
Compress-Archive -Path "$dest\ModsSource\*" -DestinationPath "$dest\windhawk-mods-pack.zip" -Force
reg export "HKLM\SOFTWARE\Windhawk" "$dest\settings\windhawk-settings.reg" /y
```

Consolidation work (merge taskbar packs, tighten exclusion lists) starts from `ModsSource/`, not from the Windhawk engine GitHub repo.

## Stash / StashDB

TBCC already ships an AOF-branded StashDB backlog enhancer (extension + Tampermonkey). Notes: `telegram_bot2/tbcc/userscripts/inbox/stashdb/NOTES.md`.

Stash *app* plugin work is a separate surface — track candidates under `products/` when we cut a repo for them.
