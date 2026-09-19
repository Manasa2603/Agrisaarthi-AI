@echo off
title AgriSaarthi AI - Frontend Dashboard
color 0B
echo =====================================================================
echo                AgriSaarthi AI - React + Vite Frontend
echo =====================================================================
echo.
cd /d "%~dp0frontend"
echo [1/2] Checking Node environment...
node -v
echo [2/2] Launching Vite development server on http://127.0.0.1:5173...
echo.
npm run dev -- --host 127.0.0.1 --port 5173
pause
