@echo off
echo ============================================================
echo Motor CAN ID Remapping Tool
echo ============================================================
echo.
echo This will attempt to configure motors with unique CAN IDs
echo and verify that different motors respond to different IDs.
echo.
echo WARNING: This may not work if motors don't support
echo software CAN ID configuration.
echo.
pause
cd /d "%~dp0..\scripts"
python remap_motor_ids.py
pause

