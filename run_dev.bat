@echo off
echo =========================================================================
echo               JalRakshak Dev Servers Startup Launcher
echo =========================================================================
echo.

:: 1. Navigate to backend and install dependencies
echo [1/3] Checking and installing backend python requirements...
cd backend
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Default global pip installation failed or requires admin. 
    echo Attempting user-space installation...
    python -m pip install --user -r requirements.txt
)
cd ..

:: 2. Launch FastAPI API server in a new window
echo [2/3] Spawning Uvicorn API backend server in a separate window...
start "JalRakshak API Backend (Port 8000)" cmd /k "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

:: 3. Launch React frontend server in another window
echo [3/3] Spawning React dev server in a separate window...
start "JalRakshak Web Frontend (Port 5173)" cmd /k "cd frontend && npm run dev"

echo.
echo =========================================================================
echo SUCCESS: BOTH SERVERS SUCCESSFULLY SPAWNED!
echo.
echo * FastAPI Hub: http://127.0.0.1:8000
echo * Swagger APIs Docs: http://127.0.0.1:8000/docs
echo * React Web Dashboard: http://localhost:5173
echo.
echo Keep this window open if you want to inspect launcher states, or close it.
echo The spawned CMD windows contain the actual server logs and hot-reloads.
echo =========================================================================
pause
