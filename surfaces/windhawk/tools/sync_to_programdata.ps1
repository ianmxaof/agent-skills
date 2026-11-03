# Sync ModsSource → %ProgramData%\Windhawk\ModsSource
$ErrorActionPreference = "Stop"
$src = Join-Path $PSScriptRoot "..\ModsSource" | Resolve-Path
$dst = Join-Path $env:ProgramData "Windhawk\ModsSource"
if (-not (Test-Path $dst)) {
    throw "Windhawk ModsSource missing: $dst"
}
Write-Host "Copy $src -> $dst"
Copy-Item -Path (Join-Path $src "*") -Destination $dst -Force
Write-Host "Done. Compile new local@ packs in Windhawk UI, then disable replaced upstreams."
Get-ChildItem $dst -Filter "local@taskbar-*-pack.wh.cpp" | Format-Table Name, Length, LastWriteTime
