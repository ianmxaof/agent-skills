---
name: tbcc-explorer-context-menu
description: >-
  Add or replicate Windows Explorer right-click context menus for TBCC with
  optional per-folder titles via AppliesTo (e.g. "TBCC: Start … (AOF ASS)").
  Use when adding Explorer menus, folder-conditional menu labels, HKCU shell
  registration, VBS hidden launchers, or replicating the Stashtag/Erome pattern.
---

# TBCC Explorer context menu (folder-titled pattern)

Register **current-user** Explorer menus under `HKCU:\Software\Classes\`. TBCC uses **VBS → PowerShell → tbcc_cli** (no console flash, no backend API required for local actions).

## Title format (folder-titled items)

When the menu should reflect the lane/folder name:

```text
{TitleBase} ({FolderName})
```

Example:

```text
TBCC: Start Stashtag ONNX (act tagger) (AOF ASS)
```

Implementation: **one registry key per folder name**, not dynamic text at click time.

| Registry value | Example |
|---|---|
| `(Default)` | `TBCC: Start Stashtag ONNX (act tagger) (AOF ASS)` |
| `AppliesTo` | `System.Kind:=folder AND System.FileName:="AOF ASS"` |
| `command` | `wscript.exe "…\launcher.vbs" "%1"` or `"%V"` |

Also register a **generic fallback** with `AppliesTo = NOT (System.FileName:="AOF ASS" OR …)` so non-lane folders still get `{TitleBase}` without duplicate entries on lane folders.

## Shared library (use this — do not copy-paste registry code)

Dot-source:

```powershell
. "$PSScriptRoot\tbcc-explorer-context-menu.ps1"
```

| Function | Purpose |
|---|---|
| `Register-TbccExplorerFolderTitledMenu` | `{TitleBase} ({FolderName})` + AppliesTo per folder |
| `Register-TbccExplorerStaticMenu` | Single fixed title (Stop, Batch, desktop) |
| `Unregister-TbccExplorerMenuSuite` | Remove all keys matching `MenuPrefix*` |
| `New-TbccExplorerVbsLauncher` | Generate VBS that forwards `%1` / `%V` as `-FolderPath` |
| `Set-TbccExplorerShellKey` | Low-level HKCU key writer |

Path args by target:

| Target | Explorer arg | When |
|---|---|---|
| `Directory\shell` | `%1` | Right-click **folder icon** in list |
| `Directory\Background\shell` | `%V` | Right-click **inside open folder** |
| `DesktopBackground\shell` | *(none)* | Desktop wallpaper |

## Replicate a new menu suite (checklist)

Copy the **Stashtag reference** (`tbcc/tools/register-stashtag-context-menu.ps1`), then:

1. **Handler PS1** — `tbcc/tools/{name}-context-menu.ps1`
   - Params: `-Action`, `-FolderPath`, `-Quiet`
   - Call `tbcc_cli.py …` or other local logic
   - Resolve folder label: `Split-Path -Leaf $FolderPath`
   - Log to `tbcc/.tbcc-run/{name}-context-menu.log`

2. **VBS launchers** — one per action, or generate:
   ```powershell
   New-TbccExplorerVbsLauncher `
     -OutPath "$toolsDir\my-action.vbs" `
     -Ps1Path "$toolsDir\my-context-menu.ps1" `
     -Ps1Arguments '-Action myaction -Quiet' `
     -Force
   ```

3. **Register script** — `tbcc/tools/register-{name}-context-menu.ps1`
   - Choose unique `MenuPrefix` (e.g. `TBCCMyFeature` — alphanumeric, no spaces)
   - Folder-titled item → `Register-TbccExplorerFolderTitledMenu`
   - Static items → `Register-TbccExplorerStaticMenu`
   - `-Unregister` → `Unregister-TbccExplorerMenuSuite`

4. **Folder name list** for AppliesTo
   - Python source: `LANE_DISK_FOLDERS` values + `Unsorted` (see Stashtag register script)
   - Or hardcode `[string[]]$FolderNames = @("AOF ASS", …)`

5. **Icon** (optional): `tbcc/extension/icons/favicon.ico`

6. **Register on machine**
   ```powershell
   cd tbcc\tools
   .\register-{name}-context-menu.ps1
   ```
   Explorer refresh: **F5** or new window.

7. **Verify**
   ```powershell
   reg query "HKCU\Software\Classes\Directory\shell\TBCCMyFeatureStart_AOFASS"
   ```

8. **Document** one line in `tbcc/tools/README.md` or relevant pipeline doc.

## Reference implementation

| Piece | Path |
|---|---|
| Library | `tbcc/tools/tbcc-explorer-context-menu.ps1` |
| Stashtag register | `tbcc/tools/register-stashtag-context-menu.ps1` |
| Stashtag handler | `tbcc/tools/stashtag-context-menu.ps1` |
| Static-only example | `tbcc/tools/register-erome-context-menu.ps1` |

## PowerShell handler snippet

```powershell
param(
  [ValidateSet("start", "stop", "batch")]
  [string]$Action = "status",
  [string]$FolderPath = "",
  [switch]$Quiet
)

function Resolve-FolderLabel {
  param([string]$RawPath)
  $p = if ($RawPath) { $RawPath.Trim().Trim('"') } else { "" }
  if (-not $p -or $p -eq "%1" -or $p -eq "%V") { return "" }
  if (Test-Path -LiteralPath $p) { return Split-Path -LiteralPath $p -Leaf }
  return Split-Path $p -Leaf
}

$folderLabel = Resolve-FolderLabel $FolderPath
# Use $folderLabel in dialogs/logs; menu title already set by AppliesTo at register time.
```

## Register snippet (folder-titled Start)

```powershell
. "$PSScriptRoot\tbcc-explorer-context-menu.ps1"

$menuPrefix = "TBCCExample"
$folderNames = @("AOF ASS", "AOF BIG TITS")  # or Get-AofLaneFolderNames

Register-TbccExplorerFolderTitledMenu `
  -MenuPrefix $menuPrefix `
  -ItemKeySuffix "Start" `
  -TitleBase "TBCC: Do the thing" `
  -LauncherVbsPath "$PSScriptRoot\example-start.vbs" `
  -FolderNames $folderNames `
  -IconPath "$tbccRoot\extension\icons\favicon.ico" `
  -IncludeGenericFallback
```

## Limits (do not promise beyond this)

- **Menu title** is fixed per registry key; “dynamic” means **per-folder keys**, not runtime string formatting.
- `AppliesTo` matches **folder display name anywhere on disk**, not only under `AOF NETWORK`.
- **Desktop** has no folder context — use static title only.
- **File** context menus use `SystemFileAssociations\{ext}\shell` (see Erome register) — different target, same `Set-TbccExplorerShellKey`.
- Shell COM extensions are out of scope unless AppliesTo is insufficient.

## Unregister

```powershell
cd tbcc\tools
.\register-{name}-context-menu.ps1 -Unregister
```
