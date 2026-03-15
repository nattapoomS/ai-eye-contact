@echo off
echo Starting AI Eye Contact (Local Dev)
echo =====================================

:: Start FastAPI backend in new window
start "FastAPI Backend" cmd /k "cd /d %~dp0backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: Wait for backend to boot
timeout /t 3 /nobreak >nul

:: Start background worker in new window
start "Job Worker" cmd /k "cd /d %~dp0backend && python -m worker.job_poller"

:: Start Next.js frontend in new window
start "Next.js Frontend" cmd /k "cd /d %~dp0 && npm run dev"

echo.
echo All services started:
echo   Frontend  ->  http://localhost:3000
echo   Backend   ->  http://localhost:8000
echo   Docs      ->  http://localhost:8000/docs
echo.
echo Close the opened windows to stop each service.
pause
