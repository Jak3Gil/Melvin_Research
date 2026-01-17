@echo off
echo ============================================================
echo Interactive Motor Tester
echo ============================================================
echo.

REM Check if COM3 is available first
python -c "import serial; s=serial.Serial('COM3', 115200); s.close(); print('COM3 is available')" 2>nul
if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: COM3 port is locked!
    echo ============================================================
    echo.
    echo COM3 is being used by another program.
    echo.
    echo Please close:
    echo   1. All terminal windows (this one is OK)
    echo   2. Arduino IDE Serial Monitor
    echo   3. PlatformIO Serial Monitor  
    echo   4. Any Python scripts using COM3
    echo.
    echo OR: Unplug and replug the USB-to-CAN adapter
    echo.
    echo Then run this script again.
    echo.
    echo (You can also run free_com3.ps1 to check)
    echo.
    pause
    exit /b 1
)

echo [OK] COM3 is available
echo.
echo Starting motor tester...
echo.
echo CONTROLS:
echo   W / w - Move motor forward (small jog)
echo   S / s - Move motor backward (small jog)
echo   SPACE - Next motor
echo   Q / q - Quit
echo.
pause
python test_motors_interactive_debug.py COM3 921600
if errorlevel 1 (
    echo.
    echo Error occurred. Check that COM3 is not in use.
    pause
)
