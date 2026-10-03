# Windhawk merge assessment (2026-09-11)

Snapshot: `surfaces/windhawk/ModsSource` + `settings/windhawk-settings.reg`.

## Status (implemented 2026-09-11)

| Item | Status |
|---|---|
| `local@taskbar-volume-pack.wh.cpp` | **Done** — `tools/amalgamate_packs.py` |
| `local@taskbar-autohide-pack.wh.cpp` | **Done** |
| Retarget explorer-details + slick-window excludes | **Done** (kept `@include *`, grew `@exclude`) |
| Sync to `%ProgramData%\Windhawk` + disable upstreams | **Needs elevated** — see `INSTALL.md` |
| Icon-size + tray spacing pack | **Skipped** (tray was OFF) |
| Styler merges | **Won’t do** |

Target after enable packs + disable four upstreams: **~7** active (2 packs replace 4 mods).

## Packs

| Mod id | Replaces |
|---|---|
| `local@taskbar-volume-pack` | `taskbar-volume-control`, `taskbar-volume-control-per-app` |
| `local@taskbar-autohide-pack` | `taskbar-auto-hide-when-maximized`, `taskbar-autohide-instant-show` |

Volume pack defaults system scroll area to **tray** so buttons stay free for per-app.

## Your steps

See `INSTALL.md`. Short version:

```powershell
# elevated PowerShell
cd C:\Powercore-repo-main\agent-skills\surfaces\windhawk
pwsh -File tools\sync_to_programdata.ps1
pwsh -File tools\disable_replaced_upstreams.ps1
```

Then Windhawk → compile both `local@taskbar-*-pack` → enable packs → confirm four upstreams stay disabled → recompile explorer-details + slick-window.

## Wiki

Injection / exclude semantics: [Injection targets and critical system processes](https://github.com/ramensoftware/windhawk/wiki/Injection-targets-and-critical-system-processes).
