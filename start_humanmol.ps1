# HumanMol AI - Complete Localhost Launcher Script

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "       HumanMol AI - Disease-to-Molecule Discovery & Intelligence Platform      " -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

# 1. Start Backend (FastAPI + All Scientific Models)
Write-Host "[1/3] Starting Backend Scientific Engine on http://localhost:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ROOT'; C:\Users\hp\miniconda3\envs\humanmol-xpert\python.exe scientific-engine/main.py"

# 2. Start Frontend (Next.js App Router)
Write-Host "[2/3] Starting Frontend Next.js Interface on http://localhost:3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ROOT\frontend'; npm run dev"

# 3. Wait and open browser
Write-Host "[3/3] Initializing services..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Opening HumanMol AI Web Platform in your default browser..." -ForegroundColor Green
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "Platform Active:" -ForegroundColor Green
Write-Host "  - Frontend UI:       http://localhost:3000" -ForegroundColor White
Write-Host "  - Backend Engine:    http://localhost:8000" -ForegroundColor White
Write-Host "  - API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "Keep both terminal windows open. To stop, close the terminal windows." -ForegroundColor Gray
