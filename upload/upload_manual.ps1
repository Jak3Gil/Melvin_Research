# Manual ESP32 Upload Script
# Run this when you're ready to upload

Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ESP32 Servo Control - Manual Upload" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check available ports
Write-Host "Checking for ESP32 on COM ports..." -ForegroundColor Yellow
$ports = [System.IO.Ports.SerialPort]::getportnames()
Write-Host "Available COM ports: $($ports -join ', ')" -ForegroundColor Yellow

$usbPorts = Get-PnpDevice | Where-Object {
    $_.FriendlyName -like "*USB*Serial*" -or 
    $_.FriendlyName -like "*CH340*" -or 
    $_.FriendlyName -like "*CP210*"
} | ForEach-Object {
    if ($_.FriendlyName -match 'COM(\d+)') {
        "COM$($matches[1])"
    }
}

if ($usbPorts) {
    Write-Host "`nFound USB Serial devices on: $($usbPorts -join ', ')" -ForegroundColor Green
} else {
    Write-Host "`nNo USB Serial devices found!" -ForegroundColor Red
    Write-Host "Make sure ESP32 is connected via USB." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "INSTRUCTIONS:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Close any programs using the serial port:" -ForegroundColor White
Write-Host "   - Arduino IDE Serial Monitor" -ForegroundColor White
Write-Host "   - PlatformIO Serial Monitor" -ForegroundColor White
Write-Host "   - Any other serial terminal programs" -ForegroundColor White
Write-Host ""
Write-Host "2. Put ESP32 in BOOTLOADER MODE:" -ForegroundColor Yellow
Write-Host "   a) Hold the BOOT button" -ForegroundColor Cyan
Write-Host "   b) Press and release the RESET button (while holding BOOT)" -ForegroundColor Cyan
Write-Host "   c) Release the BOOT button" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. IMMEDIATELY after step 2, press ENTER to start upload" -ForegroundColor Green
Write-Host "   (You have about 10 seconds before it exits bootloader mode)" -ForegroundColor Yellow
Write-Host ""

$null = Read-Host "Press ENTER when ESP32 is in bootloader mode"

# Try each port
foreach ($port in $usbPorts) {
    Write-Host "`nAttempting upload to $port..." -ForegroundColor Yellow
    python -m platformio run --target upload --upload-port $port
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n========================================" -ForegroundColor Green
        Write-Host "SUCCESS! Code uploaded to $port" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Your servo should start moving now!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "Failed on $port, trying next..." -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Red
Write-Host "Upload failed on all ports" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "Troubleshooting:" -ForegroundColor Yellow
Write-Host "1. Make sure ESP32 is in bootloader mode when you press ENTER" -ForegroundColor White
Write-Host "2. Try unplugging and replugging the USB cable" -ForegroundColor White
Write-Host "3. Check Device Manager to see which COM port your ESP32 is on" -ForegroundColor White
Write-Host "4. Make sure no other programs are using the serial port" -ForegroundColor White
Write-Host ""
Write-Host "You can also try manually:" -ForegroundColor Yellow
Write-Host "  python -m platformio run --target upload --upload-port COMX" -ForegroundColor Cyan
Write-Host "  (Replace COMX with your ESP32's port)" -ForegroundColor Cyan

