# =====================================================================
# ASHA Saathi - Backend Runner Script (Windows PowerShell)
# =====================================================================
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting ASHA Saathi FastAPI Backend Server" -ForegroundColor Green
Write-Host " AI Voice Field Register for ASHA Workers" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# Set Python Path and Environment
$env:PYTHONPATH = $PSScriptRoot

# Locate Python Executable
$PythonCmd = "python"
if (Test-Path "C:\Users\Siddarth\AppData\Local\Programs\Python\Python313\python.exe") {
    $PythonCmd = "C:\Users\Siddarth\AppData\Local\Programs\Python\Python313\python.exe"
}

Write-Host "Using Python: $PythonCmd" -ForegroundColor DarkCyan
Write-Host "Running on: http://127.0.0.1:8000 (API Docs: http://127.0.0.1:8000/docs)" -ForegroundColor Green

& $PythonCmd -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
