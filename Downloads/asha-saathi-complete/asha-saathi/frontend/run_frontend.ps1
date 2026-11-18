# =====================================================================
# ASHA Saathi - Frontend Runner Script (Windows PowerShell)
# =====================================================================
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting ASHA Saathi React + Vite Frontend" -ForegroundColor Green
Write-Host " Mobile-First Field Worker Interface" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

Set-Location $PSScriptRoot
Write-Host "Frontend running at: http://localhost:5173" -ForegroundColor Green

npm.cmd run dev -- --host
