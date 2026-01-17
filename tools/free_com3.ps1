# Free COM3 - Check and help identify what's using it

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "COM3 Port Checker and Helper" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Try to open COM3
try {
    $port = New-Object System.IO.Ports.SerialPort COM3,115200,None,8,one
    $port.Open()
    $port.Close()
    $port.Dispose()
    Write-Host "[OK] COM3 is available!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run test_motors.bat" -ForegroundColor Green
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 0
} catch {
    Write-Host "[ERROR] COM3 is locked" -ForegroundColor Red
    Write-Host ""
}

Write-Host "COM3 is currently in use. Please close:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. All terminal windows (Command Prompt, PowerShell, etc.)" -ForegroundColor White
Write-Host "  2. Arduino IDE (if open)" -ForegroundColor White
Write-Host "  3. PlatformIO Serial Monitor (if open)" -ForegroundColor White
Write-Host "  4. Any Python scripts running (check Task Manager)" -ForegroundColor White
Write-Host "  5. Any other serial/USB tools" -ForegroundColor White
Write-Host ""
Write-Host "Quick fix: Unplug and replug the USB-to-CAN adapter" -ForegroundColor Cyan
Write-Host ""
Write-Host "After closing programs, run this script again to check." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

