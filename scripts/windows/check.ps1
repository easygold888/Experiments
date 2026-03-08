param(
  [int]$Port = 8000,
  [string]$Host = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

Write-Host "Checking PMI endpoints on http://$Host`:$Port" -ForegroundColor Cyan

$urls = @(
  "http://$Host`:$Port/api/health",
  "http://$Host`:$Port/api/fx/latest?base=USD&symbols=EUR,JPY",
  "http://$Host`:$Port/api/country/MEX",
  "http://$Host`:$Port/api/events?max_records=2",
  "http://$Host`:$Port/api/overview?base=USD&country=MEX"
)

foreach ($u in $urls) {
  try {
    $res = Invoke-RestMethod -Uri $u -Method Get -TimeoutSec 15
    Write-Host "OK  $u" -ForegroundColor Green
  }
  catch {
    Write-Host "FAIL $u" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor DarkRed
  }
}
