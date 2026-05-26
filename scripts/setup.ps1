# Eshwar AI — Windows setup (Python 3.10 or 3.11)
# Run from project root:  .\scripts\setup.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Find-Python {
    foreach ($ver in @("3.11", "3.10", "3.12", "3.13")) {
        try {
            $out = & py "-$ver" -c "import sys; print(sys.version)" 2>$null
            if ($LASTEXITCODE -eq 0) {
                return $ver
            }
        } catch { }
    }
    return $null
}

$pyVer = Find-Python
if (-not $pyVer) {
    Write-Host "ERROR: Install Python 3.10 or 3.11 from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "Python 3.14 is NOT supported yet (tokenizers / sentence-transformers fail to build)."
    exit 1
}

Write-Host "Using Python $pyVer (avoid 3.14 for this project)" -ForegroundColor Cyan

if (Test-Path ".venv") {
    Write-Host "Removing old .venv ..."
    Remove-Item -Recurse -Force ".venv"
}

Write-Host "Creating virtual environment ..."
& py "-$pyVer" -m venv .venv

$pip = Join-Path $Root ".venv\Scripts\python.exe"
& $pip -m pip install --upgrade pip
& $pip -m pip install -r requirements.txt

Write-Host ""
Write-Host "Done. Next steps:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  copy .env.example .env    # add GOOGLE_API_KEY"
Write-Host "  python -m backend.ingest --reset"
Write-Host "  streamlit run app/app.py"
