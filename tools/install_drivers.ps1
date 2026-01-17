# ESP32 USB Driver Installation Helper
# This script provides instructions and checks for common ESP32 USB drivers

Write-Host "ESP32 USB Driver Check" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

# Check for common USB serial drivers
Write-Host "Checking for USB Serial devices..." -ForegroundColor Yellow

$ports = [System.IO.Ports.SerialPort]::getportnames()
Write-Host "Available COM ports: $($ports -join ', ')" -ForegroundColor Yellow
Write-Host ""

# Check Device Manager for USB Serial devices
Write-Host "Checking Device Manager for USB Serial devices..." -ForegroundColor Yellow
$usbDevices = Get-PnpDevice | Where-Object {
    $_.FriendlyName -like "*USB*Serial*" -or 
    $_.FriendlyName -like "*CH340*" -or 
    $_.FriendlyName -like "*CP210*" -or
    $_.FriendlyName -like "*Silicon*" -or
    $_.FriendlyName -like "*FTDI*"
}

if ($usbDevices) {
    Write-Host "Found USB Serial devices:" -ForegroundColor Green
    $usbDevices | ForEach-Object {
        Write-Host "  - $($_.FriendlyName) (Status: $($_.Status))" -ForegroundColor Green
    }
} else {
    Write-Host "No USB Serial devices found. You may need to install drivers." -ForegroundColor Red
    Write-Host ""
    Write-Host "Common ESP32 USB Drivers:" -ForegroundColor Yellow
    Write-Host "1. CH340 Driver:" -ForegroundColor Yellow
    Write-Host "   Download: https://www.wch.cn/downloads/CH341SER_EXE.html" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. CP2102 Driver:" -ForegroundColor Yellow
    Write-Host "   Download: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. FTDI Driver:" -ForegroundColor Yellow
    Write-Host "   Download: https://ftdichip.com/drivers/vcp-drivers/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "After installing the driver:" -ForegroundColor Yellow
    Write-Host "1. Unplug and replug your ESP32" -ForegroundColor Yellow
    Write-Host "2. Check Device Manager for a new COM port" -ForegroundColor Yellow
    Write-Host "3. Run this script again to verify" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "To check Device Manager manually:" -ForegroundColor Yellow
Write-Host "1. Press Win+X and select 'Device Manager'" -ForegroundColor Yellow
Write-Host "2. Look under 'Ports (COM & LPT)' for your ESP32" -ForegroundColor Yellow
Write-Host "3. If you see a yellow exclamation mark, the driver is missing" -ForegroundColor Yellow

