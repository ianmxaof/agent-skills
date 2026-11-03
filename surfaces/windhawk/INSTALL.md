# Windhawk packs — install / enable

Sources:

- Repo: `agent-skills/surfaces/windhawk/ModsSource/`
- Live: `%ProgramData%\Windhawk\ModsSource\` (`tools/sync_to_programdata.ps1`)

## Why packs were invisible

Windhawk `@id` may only use `a-z`, `0-9`, and `-`.  
Filename stays `local@taskbar-volume-pack.wh.cpp`, but **inside** the file:

```
// @id              taskbar-volume-pack
```

`local@…` in `@id` is invalid — Windhawk skips the mod. Fixed in repo; re-sync required.

## Packs

| Filename | `@id` | Disable these upstreams |
|---|---|---|
| `local@taskbar-volume-pack.wh.cpp` | `taskbar-volume-pack` | volume-control, volume-control-per-app |
| `local@taskbar-autohide-pack.wh.cpp` | `taskbar-autohide-pack` | auto-hide-when-maximized, autohide-instant-show |

## Steps

### 1. Elevated sync (required again)

```powershell
cd C:\Powercore-repo-main\agent-skills\surfaces\windhawk
pwsh -File tools\sync_to_programdata.ps1
pwsh -File tools\disable_replaced_upstreams.ps1
```

### 2. Fully quit Windhawk (tray → Exit), then reopen

### 3. Find packs → Compile → On

Names: **Taskbar Volume Pack**, **Taskbar Autohide Pack**.

### 4. Still missing? Create manually

Windhawk → **Create a new mod** → replace template with full file contents from the repo `ModsSource\local@taskbar-*-pack.wh.cpp` → Compile.

### 5. Disable the four upstreams (if disable script didn’t stick)

### 6. Recompile explorer-details + slick-window

## Regenerate

```powershell
py -3.13 tools\amalgamate_packs.py
pwsh -File tools\sync_to_programdata.ps1
```
