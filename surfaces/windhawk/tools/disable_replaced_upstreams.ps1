# Disable upstream mods replaced by local packs. Prefer Windhawk stopped.
$ErrorActionPreference = "Stop"
$ids = @(
    "taskbar-volume-control",
    "taskbar-volume-control-per-app",
    "taskbar-auto-hide-when-maximized",
    "taskbar-autohide-instant-show"
)
foreach ($id in $ids) {
    $key = "HKLM:\SOFTWARE\Windhawk\Engine\Mods\$id"
    if (Test-Path $key) {
        Set-ItemProperty -Path $key -Name Disabled -Value 1 -Type DWord
        Write-Host "Disabled $id"
    } else {
        Write-Host "Skip (no key): $id"
    }
}
Write-Host "Enable local@taskbar-volume-pack and local@taskbar-autohide-pack after compile."
