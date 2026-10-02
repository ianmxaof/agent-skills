# PowerCore Ship Gate — nightly stress lane (local / agent-first)
# Run: powershell -NoProfile -File tools/ship_gate/nightly.ps1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path (Join-Path $Root "tools\ship_gate\run.py"))) {
  $Root = "C:\Powercore-repo-main\agent-skills"
}
Set-Location $Root
Write-Host "PSG nightly stress @ $(Get-Date -Format o) cwd=$Root"

$failed = 0
py -3.13 -m tools.ship_gate.run --lane stress --root text-expander
if ($LASTEXITCODE -ne 0) { $failed += 1 }

py -3.13 -m tools.ship_gate.run --lane stress --root tbcc
if ($LASTEXITCODE -ne 0) { $failed += 1 }

if ($failed -gt 0) {
  Write-Host "PSG nightly FAILED ($failed root(s))"
  exit 1
}
Write-Host "PSG nightly ok"
exit 0
