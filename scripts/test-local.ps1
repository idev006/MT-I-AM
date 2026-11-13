$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..'))
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3.12 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 venv creation failed' }
}
$Python = '.venv\Scripts\python.exe'
& $Python -m pip install -e '.[test,database]'
if ($LASTEXITCODE -ne 0) { throw 'Install failed' }
& $Python -m pytest -q -ra -m "not full_registry" tests
if ($LASTEXITCODE -ne 0) { throw 'Fast test gate failed' }
& $Python -m pytest -q -ra -m full_registry tests
if ($LASTEXITCODE -ne 0) { throw '52 POC registry test gate failed' }
& $Python -m ruff check src tests
if ($LASTEXITCODE -ne 0) { throw 'ruff check failed' }
& $Python -m mt_iam.poc.platform_cli --config configs/platform.toml --report artifacts/poc-results/local.json
if ($LASTEXITCODE -ne 0) { throw 'POC runner failed' }
Write-Host 'Local gates completed. External-provider BLOCKED results are not full POC PASS.'
