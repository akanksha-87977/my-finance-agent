# Launch FastAPI backend locally.
# Uses backend/.venv if present, otherwise falls back to repoRoot/.venv.

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"

$venvCandidates = @(
  (Join-Path $backendDir ".venv\Scripts\python.exe"),
  (Join-Path $repoRoot ".venv\Scripts\python.exe")
)

$venvPython = $null
foreach ($c in $venvCandidates) {
  if (Test-Path $c) { $venvPython = $c; break }
}

if ($null -eq $venvPython) {
  throw "Could not find python.exe for venv. Looked in: $($venvCandidates -join ', ')"
}

Push-Location $backendDir

# Ensure Python can import the `app` package.
$env:PYTHONPATH = $backendDir

# Ensure DATABASE_URL is set; otherwise backend will fall back to SQLite and existing
# Postgres accounts won't be found.
if ([string]::IsNullOrWhiteSpace($env:DATABASE_URL)) {
  $env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/financial_ai"
  Write-Host "DATABASE_URL was not set; using default: " $env:DATABASE_URL -ForegroundColor Yellow
}
else {
  Write-Host "DATABASE_URL provided: " $env:DATABASE_URL -ForegroundColor Green
}

Write-Host "Starting uvicorn with DATABASE_URL=" $env:DATABASE_URL -ForegroundColor Cyan

& $venvPython -m uvicorn app.main_entry:app --host 0.0.0.0 --port 8000 --reload
Pop-Location


