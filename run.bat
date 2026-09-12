@echo off
setlocal enabledelayedexpansion
title Digital Guardrails Launcher

:: Navigate to script directory
cd /d "%~dp0"

echo ======================================================================
echo          Digital Guardrails - Bal Suraksha Hackathon Prototype
echo ======================================================================
echo.

:: Check for virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Python virtual environment not found in .venv\
    echo Please create the virtual environment and install dependencies:
    echo   python -m venv .venv
    echo   .venv\Scripts\python.exe -m pip install -r backend\requirements-ml.txt
    echo.
    pause
    exit /b 1
)

:: Ensure scratch directory exists
if not exist "scratch" (
    mkdir "scratch" 2>nul
)

:: Check for node_modules
if not exist "node_modules" (
    echo [INFO] node_modules not found. Running npm install...
    call npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed.
        pause
        exit /b 1
    )
)

echo [1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Digital Guardrails - Backend" cmd /k "title Digital Guardrails Backend && .venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

echo [2/3] Starting Vite Frontend on http://127.0.0.1:5173 ...
start "Digital Guardrails - Frontend" cmd /k "title Digital Guardrails Frontend && npm run dev"

echo [3/3] Waiting for servers to initialize...
timeout /t 3 /nobreak >nul

echo.
echo ======================================================================
echo                       All services launched!
echo ======================================================================
echo   * Guardian Dashboard:    http://127.0.0.1:5173/
echo   * Youth Support Portal:  http://127.0.0.1:5173/help
echo   * Demo Panel:            http://127.0.0.1:5173/demo
echo   * Backend API:           http://127.0.0.1:8000/
echo   * API Interactive Docs:  http://127.0.0.1:8000/docs
echo   * Health Check:          http://127.0.0.1:8000/api/health
echo ======================================================================
echo Opening browser...
start http://127.0.0.1:5173/

echo.
echo Both backend and frontend are running in separate command windows.
echo To stop the application, close those command windows or press Ctrl+C in them.
echo.
pause
