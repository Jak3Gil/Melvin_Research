@echo off
echo ============================================================
echo Motor Investigation Tool
echo ============================================================
echo.
echo This will help diagnose why only 2 motors are responding
echo when you expect 15 motors.
echo.
pause
cd /d "%~dp0..\scripts"
python investigate_motors.py
pause

