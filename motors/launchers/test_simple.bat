@echo off
echo ============================================================
echo Simple Motor Tester (No Screen Clearing)
echo ============================================================
echo.
cd /d "%~dp0..\scripts"
python test_motors_interactive_debug.py COM3 921600
echo.
echo Script finished. Press any key to exit...
pause >nul

