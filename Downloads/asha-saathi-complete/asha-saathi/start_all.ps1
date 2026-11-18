# =====================================================================
# ASHA Saathi - Unified Server Launcher (Windows PowerShell)
# Launches both FastAPI Backend and Vite Frontend simultaneously
# =====================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " ASHA Saathi: Launching Complete Prototype Environment" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

$RootPath = $PSScriptRoot
$BackendPath = Join-Path $RootPath "backend"
$FrontendPath = Join-Path $RootPath "frontend"

# Launch Backend in a new PowerShell process
Write-Host "-> Launching FastAPI Backend on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$BackendPath\run_backend.ps1"

Start-Sleep -Seconds 3

# Launch Frontend in a new PowerShell process
Write-Host "-> Launching Vite React Frontend on port 5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$FrontendPath\run_frontend.ps1"

Start-Sleep -Seconds 3

Write-Host "`nAll services active!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Backend API & Docs: http://localhost:8000/docs" -ForegroundColor Cyan

# Open default browser
Start-Process "http://localhost:5173"
