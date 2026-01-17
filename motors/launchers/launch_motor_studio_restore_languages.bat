@echo off
echo ========================================
echo   Restore Motor Studio Languages
echo ========================================
echo.

cd /d "C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122\translations"

REM Restore the original English file
if exist qt_en.qm.backup (
    copy qt_en.qm.backup qt_en.qm >nul 2>&1
    echo Restored original qt_en.qm
)

REM Re-enable all language files
for %%f in (qt_*.qm.disabled) do (
    set "filename=%%f"
    set "newname=!filename:.disabled=!"
    ren "%%f" "!newname!" >nul 2>&1
)
echo Re-enabled all language translations

echo.
echo All languages restored!
echo.
pause

