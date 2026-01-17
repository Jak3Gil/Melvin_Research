@echo off
echo ========================================
echo   RobStride Motor Studio Launcher
echo ========================================
echo.
echo Which motor studio do you want to open?
echo.
echo 1. Motor Studio v00122 (motor_tool.exe) - RECOMMENDED
echo 2. Motor Studio 17nm (motor_tool.exe)
echo 3. Motor Studio 120nm (z1_motor_tool.exe)
echo 4. Driver (driver.exe)
echo 5. Open folder in Explorer
echo.
set /p choice="Enter choice (1-5): "

if "%choice%"=="1" goto motorv00122
if "%choice%"=="2" goto motor17
if "%choice%"=="3" goto motor120
if "%choice%"=="4" goto driver
if "%choice%"=="5" goto explorer
goto end

:motorv00122
echo.
echo Launching Motor Studio v00122 (English)...
cd /d "C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122"
set LANG=en_US
set LC_ALL=en_US.UTF-8
set QT_TRANSLATE_LANG=en
start "" "motor_tool.exe"
goto end

:motor17
echo.
echo Launching 17nm Motor Studio...
cd /d "c:\Users\Owner\Downloads\Studio (2)\Studio"
for /r %%i in (motor_tool.exe) do (
    if exist "%%i" (
        echo Found: %%i
        start "" "%%i"
        goto end
    )
)
echo ERROR: motor_tool.exe not found!
goto end

:motor120
echo.
echo Launching 120nm Motor Studio...
cd /d "c:\Users\Owner\Downloads\Studio (2)\Studio"
for /r %%i in (z1_motor_tool.exe) do (
    if exist "%%i" (
        echo Found: %%i
        start "" "%%i"
        goto end
    )
)
echo ERROR: z1_motor_tool.exe not found!
goto end

:driver
echo.
echo Launching Driver...
start "" "c:\Users\Owner\Downloads\motorstudio0.0.8\motorstudio0.0.8\driver.exe"
goto end

:explorer
echo.
echo Opening folder in Explorer...
explorer "c:\Users\Owner\Downloads\Studio (2)\Studio"
goto end

:end
echo.
pause

