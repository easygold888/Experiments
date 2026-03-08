param(
  [int]$Port = 8000,
  [string]$Host = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

Write-Host "== PMI Windows Launcher ==" -ForegroundColor Cyan
Write-Host "Project: $PSScriptRoot\..\.." -ForegroundColor DarkGray

Set-Location (Join-Path $PSScriptRoot "..\..")

if (-not (Test-Path ".venv")) {
  Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Yellow
  py -m venv .venv
} else {
  Write-Host "[1/4] Virtual environment already exists." -ForegroundColor Green
}

Write-Host "[2/4] Activating environment..." -ForegroundColor Yellow
. .\.venv\Scripts\Activate.ps1

Write-Host "[3/4] Installing/updating dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

Write-Host "[4/4] Starting server at http://$Host`:$Port ..." -ForegroundColor Yellow
Write-Host "Open in browser: http://$Host`:$Port" -ForegroundColor Green
Write-Host "Health check URL: http://$Host`:$Port/api/health" -ForegroundColor Green
Write-Host "Press CTRL+C to stop." -ForegroundColor DarkYellow

python -m uvicorn app.main:app --host $Host --port $Port --reload
