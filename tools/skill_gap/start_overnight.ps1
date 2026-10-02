# PowerCore overnight skill improve loop
param(
    [string]$Skill = "cc-report",
    [int]$MaxIters = 500,
    [double]$SleepSecs = 60,
    [switch]$UntilPerfect,
    [switch]$Live,
    [int]$LiveMax = 3,
    [switch]$DemoBreak
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path (Join-Path $Root "tools\skill_gap\overnight_loop.py"))) {
    $Root = "C:\Powercore-repo-main\agent-skills"
}
Set-Location $Root

$argsList = @(
    "-3.13", "-m", "tools.skill_gap.overnight_loop",
    "--skill", $Skill,
    "--max-iters", "$MaxIters",
    "--sleep", "$SleepSecs"
)
if ($UntilPerfect) { $argsList += "--until-perfect" }
if ($Live) { $argsList += @("--live", "--live-max", "$LiveMax") }
if ($DemoBreak) { $argsList += "--demo-break" }

Write-Host "Starting overnight: py $($argsList -join ' ')"
& py @argsList
exit $LASTEXITCODE
