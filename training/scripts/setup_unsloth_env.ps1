param(
    [string]$Python = "python",
    [string]$EnvDir = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")
if ([string]::IsNullOrWhiteSpace($EnvDir)) {
    $EnvDir = Join-Path $RepoRoot "training\.venv-unsloth"
}
$EnvFullPath = [System.IO.Path]::GetFullPath($EnvDir)
$BackendPath = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot "backend"))
$FrontendPath = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot "frontend"))
$ReqFile = Join-Path $RepoRoot "training\requirements-unsloth.txt"

if ($EnvFullPath.StartsWith($BackendPath, [System.StringComparison]::OrdinalIgnoreCase) -or
    $EnvFullPath.StartsWith($FrontendPath, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to create the Unsloth training environment inside app runtime directories: $EnvFullPath"
}

Write-Host "Creating isolated Unsloth training environment at $EnvFullPath"
& $Python -m venv $EnvFullPath

$VenvPython = Join-Path $EnvFullPath "Scripts\python.exe"
$UvExe = Join-Path $EnvFullPath "Scripts\uv.exe"

& $VenvPython -m pip install --upgrade pip uv

if (Test-Path $UvExe) {
    & $UvExe pip install -r $ReqFile --torch-backend=auto
} else {
    & $VenvPython -m pip install -r $ReqFile
}

Write-Host ""
Write-Host "Training environment ready for verification."
Write-Host "Activate with: .\training\.venv-unsloth\Scripts\Activate.ps1"
Write-Host "Check with:    python training\scripts\check_training_env.py"
