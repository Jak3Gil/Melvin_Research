@echo off
echo ============================================================
echo Activate All Motors - Software Activation
echo ============================================================
echo.
echo This will try different software methods to activate/enable
echo all motors since hardware is confirmed working.
echo.
pause
cd /d "%~dp0..\scripts"
python activate_all_motors.py
pause

