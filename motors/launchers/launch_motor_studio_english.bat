@echo off
echo ========================================
echo   Launching Motor Studio in English
echo ========================================
echo.

REM Set language to English
set LANG=en_US
set LC_ALL=en_US.UTF-8
set QT_TRANSLATE_LANG=en

REM Launch Motor Studio
cd /d "C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122"
start "" "motor_tool.exe"

echo.
echo Motor Studio launched!
echo.
echo If it's still in Chinese:
echo 1. Look for "Settings" or "设置" menu
echo 2. Look for "Language" or "语言" option
echo 3. Select "English" or "英文"
echo.
pause

