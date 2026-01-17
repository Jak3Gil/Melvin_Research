# Check COM3 status and help free it

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "COM3 Port Checker" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if COM3 exists
$ports = [System.IO.Ports.SerialPort]::getportnames()
if ($ports -contains "COM3") {
    Write-Host "[OK] COM3 port exists" -ForegroundColor Green
} else {
    Write-Host "[ERROR] COM3 port not found!" -ForegroundColor Red
    Write-Host "Available ports: $($ports -join ', ')" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Checking if COM3 is in use..." -ForegroundColor Yellow

# Try to open COM3 to see if it's locked
try {
    $testPort = New-Object System.IO.Ports.SerialPort COM3,115200,None,8,one
    $testPort.Open()
    $testPort.Close()
    $testPort.Dispose()
    Write-Host "[OK] COM3 is available (not locked)" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can run the motor tester now!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] COM3 is locked by another program" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common programs that lock COM ports:" -ForegroundColor Yellow
    Write-Host "  - Arduino IDE Serial Monitor" -ForegroundColor White
    Write-Host "  - PlatformIO Serial Monitor" -ForegroundColor White
    Write-Host "  - PuTTY or other terminal programs" -ForegroundColor White
    Write-Host "  - Other Python scripts using serial" -ForegroundColor White
    Write-Host "  - Device Manager (if viewing port properties)" -ForegroundColor White
    Write-Host ""
    Write-Host "To fix:" -ForegroundColor Yellow
    Write-Host "  1. Close Arduino IDE Serial Monitor" -ForegroundColor White
    Write-Host "  2. Close PlatformIO Serial Monitor" -ForegroundColor White
    Write-Host "  3. Close any terminal programs using COM3" -ForegroundColor White
    Write-Host "  4. Close any other programs that might use COM3" -ForegroundColor White
    Write-Host "  5. Run this script again to verify COM3 is free" -ForegroundColor White
    Write-Host ""
    Write-Host "Or unplug and replug the USB-to-CAN adapter" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

