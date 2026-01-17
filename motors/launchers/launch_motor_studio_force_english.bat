@echo off
echo ========================================
echo   Motor Studio - Force English Mode
echo ========================================
echo.

REM Backup the empty English translation file
cd /d "C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122\translations"
if exist qt_en.qm.backup (
    echo English file already backed up
) else (
    copy qt_en.qm qt_en.qm.backup >nul 2>&1
    echo Backed up original qt_en.qm
)

REM Remove the empty English file so Qt uses default (untranslated = English)
del qt_en.qm >nul 2>&1
echo Removed empty English translation file

REM Rename all other language files so only English is available
for %%f in (qt_*.qm) do (
    if not "%%f"=="qt_en.qm" (
        if not exist "%%f.disabled" (
            ren "%%f" "%%f.disabled" >nul 2>&1
        )
    )
)
echo Disabled all non-English translations

echo.
echo ========================================
echo   Launching Motor Studio in English
echo ========================================
echo.

REM Set environment to English
set LANG=en_US
set LC_ALL=en_US.UTF-8
set LANGUAGE=en_US:en
set QT_TRANSLATE_LANG=

REM Launch from the motor tool directory
cd /d "C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122"
start "" "motor_tool.exe"

echo.
echo Motor Studio launched!
echo.
echo The interface should now be in English (untranslated Qt = English)
echo.
echo To restore other languages later, run:
echo   launch_motor_studio_restore_languages.bat
echo.
pause

