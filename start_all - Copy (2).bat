@echo off
title AgriSaarthi AI - Master Launcher
color 0E
echo =====================================================================
echo                AgriSaarthi AI - Master Platform Launcher
echo =====================================================================
echo.
echo Starting Backend Server on http://127.0.0.1:8000 ...
start "AgriSaarthi Backend" "%~dp0run_backend.bat"

echo Waiting 3 seconds for backend gateway to initialize...
timeout /t 3 /nobreak >nul

echo Starting Frontend Server on http://127.0.0.1:5173 ...
start "AgriSaarthi Frontend" "%~dp0run_frontend.bat"

echo Waiting 2 seconds for Vite bundler...
timeout /t 2 /nobreak >nul

echo Opening browser at http://127.0.0.1:5173 ...
start http://127.0.0.1:5173

echo.
echo =====================================================================
echo Both servers are now running in separate windows!
echo - Frontend: http://127.0.0.1:5173
echo - Backend:  http://127.0.0.1:8000
echo - Swagger:  http://127.0.0.1:8000/docs
echo.
echo Leave the two command windows open while testing or presenting.
echo =====================================================================
pause
