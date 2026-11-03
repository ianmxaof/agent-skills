# TBCC Explorer context menu — reference

## File checklist for a new suite

| File | Required |
|---|---|
| `tbcc/tools/{name}-context-menu.ps1` | Yes — handler |
| `tbcc/tools/{name}-context-menu-*.vbs` | Yes — one per action (or generated) |
| `tbcc/tools/register-{name}-context-menu.ps1` | Yes — HKCU registration |
| `tbcc/tools/tbcc-explorer-context-menu.ps1` | Reuse — do not fork |

## Registry layout

```text
HKCU\Software\Classes\Directory\shell\TBCC{Prefix}{Item}_{FolderSuffix}
  (Default) = TBCC: {TitleBase} ({FolderName})
  AppliesTo = System.Kind:=folder AND System.FileName:="{FolderName}"
  Icon      = C:\...\favicon.ico
  command\
    (Default) = wscript.exe "C:\...\launcher.vbs" "%1"

HKCU\Software\Classes\Directory\Background\shell\...  (same keys, command uses "%V")
HKCU\Software\Classes\DesktopBackground\shell\...     (static, no path arg)
```

## Stashtag folder list source

```python
from app.services.aof_lane_tag_map import LANE_DISK_FOLDERS
names = sorted(set(LANE_DISK_FOLDERS.values()) | {"Unsorted"})
```

Invoked from register script via `py -3.13 -c` with `sys.path` → `tbcc/backend`.

## Erome vs folder-titled pattern

| Pattern | Register script | Title |
|---|---|---|
| Static folder action | `register-erome-context-menu.ps1` | Same title all folders |
| Folder-titled action | `register-stashtag-context-menu.ps1` | `{Base} ({Lane})` per AppliesTo |
| File extension action | Erome `SystemFileAssociations\.mp4\shell` | Static per ext |

## Troubleshooting

| Symptom | Fix |
|---|---|
| Old menu text after register | F5 / new Explorer window |
| Duplicate Start entries | Ensure generic fallback has `NOT (...)` AppliesTo |
| Menu never appears | Check `HKCU` path; run register as same Windows user |
| `%1` literal in dialog | VBS must strip `%1`/`%V` when Explorer did not expand |
| Background menu wrong path | Use `%V`, not `%1`, for `Directory\Background\shell` |
