@echo off
title HumanMol AI Platform Launcher
echo ===============================================================================
echo                HumanMol AI - Disease-to-Molecule Discovery Platform
echo ===============================================================================
echo.
echo Starting Backend (FastAPI Scientific Engine on port 8000)...
start "HumanMol AI - Backend (Port 8000)" cmd /k "C:\Users\hp\miniconda3\envs\humanmol-xpert\python.exe scientific-engine/main.py"

echo Starting Frontend (Next.js UI on port 3000)...
start "HumanMol AI - Frontend (Port 3000)" cmd /k "cd frontend && npm run dev"

echo.
echo Waiting for servers to initialize...
timeout /t 5 /nobreak >nul

echo Opening browser at http://localhost:3000...
start http://localhost:3000

echo.
echo ===============================================================================
echo HumanMol AI is now running:
echo   - Web UI:       http://localhost:3000
echo   - Backend API:  http://localhost:8000
echo   - Swagger Docs: http://localhost:8000/docs
echo ===============================================================================
echo Keep the backend and frontend terminal windows open while using the platform.
echo.
pause
