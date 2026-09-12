@echo off
setlocal enabledelayedexpansion
title Digital Guardrails Control Center
cd /d "%~dp0"

:menu
cls
echo ======================================================================
echo          DIGITAL GUARDRAILS (BAL SURAKSHA) - CONTROL CENTER
echo ======================================================================
echo.
echo   [1] Launch Full Application (Backend + Frontend + Open Browser)
echo   [2] Start FastAPI Backend Server Only (http://127.0.0.1:8000)
echo   [3] Start Vite Frontend Server Only (http://127.0.0.1:5173)
echo   [4] Run Full Test Suite (pytest - 20 integration tests)
echo   [5] Export Dataset to Excel (dataset.xlsx) and Seed SQLite DB
echo   [6] Run AI/ML Evaluation Report and Latency Benchmark
echo   [0] Exit
echo.
echo ======================================================================
set /p choice="Select an option [0-6] (Default is 1): "

if "%choice%"=="" set choice=1
if "%choice%"=="1" goto launch_all
if "%choice%"=="2" goto launch_backend
if "%choice%"=="3" goto launch_frontend
if "%choice%"=="4" goto run_tests
if "%choice%"=="5" goto export_excel
if "%choice%"=="6" goto run_eval
if "%choice%"=="0" exit /b 0

echo Invalid selection. Please choose 0 to 6.
timeout /t 2 >nul
goto menu

:launch_all
cls
echo ======================================================================
echo Starting Full Application...
echo ======================================================================
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment .venv not found.
    pause
    goto menu
)

echo [1/3] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "Digital Guardrails - Backend" cmd /k "title Digital Guardrails Backend && cd /d "%~dp0" && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/3] Launching Vite Frontend on http://127.0.0.1:5173 ...
start "Digital Guardrails - Frontend" cmd /k "title Digital Guardrails Frontend && cd /d "%~dp0" && npm run dev"

echo [3/3] Waiting for servers to initialize...
timeout /t 3 /nobreak >nul

echo.
echo Services online:
echo   * Dashboard:           http://127.0.0.1:5173/
echo   * Youth Support:       http://127.0.0.1:5173/help
echo   * Interactive Swagger: http://127.0.0.1:8000/docs
echo   * Health Endpoint:     http://127.0.0.1:8000/health
echo.
echo Opening browser...
start http://127.0.0.1:5173/
pause
goto menu

:launch_backend
cls
echo ======================================================================
echo Starting FastAPI Backend (app.main:app)...
echo ======================================================================
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
goto menu

:launch_frontend
cls
echo ======================================================================
echo Starting Vite Frontend...
echo ======================================================================
npm run dev
pause
goto menu

:run_tests
cls
echo ======================================================================
echo Running Pytest Integration Test Suite...
echo ======================================================================
.venv\Scripts\python.exe -m pytest backend/tests -v
echo.
pause
goto menu

:export_excel
cls
echo ======================================================================
echo Exporting Dataset to Excel (dataset.xlsx) & Seeding Database...
echo ======================================================================
.venv\Scripts\python.exe -m backend.ml.export_to_excel_and_db
echo.
pause
goto menu

:run_eval
cls
echo ======================================================================
echo Running Model Evaluation & Inference Latency Benchmark...
echo ======================================================================
.venv\Scripts\python.exe -m backend.ml.evaluate --mode indicbert
echo.
.venv\Scripts\python.exe -m backend.ml.benchmark_latency
echo.
pause
goto menu
