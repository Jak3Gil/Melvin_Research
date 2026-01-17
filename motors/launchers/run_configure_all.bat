@echo off
echo ============================================================
echo Configure All Motors - L91 CAN ID Configuration
echo ============================================================
echo.
echo This script will attempt to configure all motors with
echo unique CAN IDs using software configuration commands.
echo.
pause
cd /d "%~dp0..\scripts"
python configure_all_motors.py
pause

