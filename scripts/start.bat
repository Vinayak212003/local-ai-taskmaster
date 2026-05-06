@echo off
REM scripts\start.bat — Start LocalAI TaskMaster on Windows
REM Usage: scripts\start.bat

title LocalAI TaskMaster

echo.
echo  ==========================================
echo   LocalAI TaskMaster — Windows Startup
echo  ==========================================
echo.

REM ── Check Python ──────────────────────────────────────────────────────────
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Python not found. Install Python 3.10+ from python.org
    pause
    exit /b 1
)
echo  [OK] Python found

REM ── Check .env ────────────────────────────────────────────────────────────
IF NOT EXIST ".env" (
    copy ".env.example" ".env" >nul
    echo  [OK] Created .env from .env.example
)

REM ── Backend setup ─────────────────────────────────────────────────────────
cd backend
IF NOT EXIST "venv" (
    echo  Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install -q -r requirements.txt
echo  [OK] Backend dependencies installed

REM ── Create database directory ──────────────────────────────────────────────
IF NOT EXIST "..\database" mkdir "..\database"

REM ── Start backend in new window ────────────────────────────────────────────
echo  Starting backend...
start "LocalAI-Backend" cmd /k "cd /d %CD% && venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo  [OK] Backend launched

cd ..

REM ── Frontend setup ────────────────────────────────────────────────────────
where node >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    cd frontend
    IF NOT EXIST "node_modules" (
        echo  Installing frontend dependencies...
        call npm install
    )
    echo  Starting frontend...
    start "LocalAI-Frontend" cmd /k "npm run dev"
    echo  [OK] Frontend launched
    cd ..
) ELSE (
    echo  [WARN] Node.js not found — frontend skipped
)

echo.
echo  ==========================================
echo    LocalAI TaskMaster is running!
echo  ==========================================
echo    Frontend:  http://localhost:5173
echo    API:       http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo  ==========================================
echo.
pause
