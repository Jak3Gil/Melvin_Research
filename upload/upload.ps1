# ESP32 Upload Helper Script
# This script helps identify the correct COM port and uploads the firmware

Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Write-Host "ESP32 Servo Control - Upload Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check for USB Serial devices
Write-Host "Scanning for USB Serial devices..." -ForegroundColor Yellow
$usbDevices = Get-PnpDevice | Where-Object {
    $_.FriendlyName -like "*USB*Serial*" -or 
    $_.FriendlyName -like "*CH340*" -or 
    $_.FriendlyName -like "*CP210*"
}

if ($usbDevices) {
    Write-Host "Found USB Serial devices:" -ForegroundColor Green
    $ports = @()
    $usbDevices | ForEach-Object {
        if ($_.FriendlyName -match 'COM(\d+)') {
            $port = "COM$($matches[1])"
            $ports += $port
            Write-Host "  - $($_.FriendlyName) -> $port" -ForegroundColor Green
        }
    }
    Write-Host ""
    
    if ($ports.Count -eq 0) {
        Write-Host "No COM ports found. Please check Device Manager." -ForegroundColor Red
        exit 1
    }
    
    # Try each port
    $uploaded = $false
    foreach ($port in $ports) {
        Write-Host "Attempting to upload to $port..." -ForegroundColor Yellow
        Write-Host "IMPORTANT: Put ESP32 in bootloader mode NOW:" -ForegroundColor Cyan
        Write-Host "  1. Hold the BOOT button" -ForegroundColor Cyan
        Write-Host "  2. Press and release the RESET button (while holding BOOT)" -ForegroundColor Cyan
        Write-Host "  3. Release the BOOT button" -ForegroundColor Cyan
        Write-Host "  4. The ESP32 is now in bootloader mode" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Starting upload in 3 seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
        
        python -m platformio run --target upload --upload-port $port
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "Upload successful to $port! The servo should start moving." -ForegroundColor Green
            $uploaded = $true
            break
        } else {
            Write-Host "Upload to $port failed. Trying next port..." -ForegroundColor Yellow
            Write-Host ""
        }
    }
    
    if (-not $uploaded) {
        Write-Host ""
        Write-Host "Upload failed on all ports. Please try:" -ForegroundColor Red
        Write-Host "1. Close any programs using the serial port (Arduino IDE, serial monitors, etc.)" -ForegroundColor Red
        Write-Host "2. Put ESP32 in bootloader mode before running this script" -ForegroundColor Red
        Write-Host "3. Manually upload: python -m platformio run --target upload --upload-port COMX" -ForegroundColor Red
        Write-Host "   (Replace COMX with your ESP32's COM port: $($ports -join ', '))" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "No USB Serial devices found. Please:" -ForegroundColor Red
    Write-Host "1. Ensure ESP32 is connected via USB" -ForegroundColor Red
    Write-Host "2. Install USB drivers (run tools/install_drivers.ps1)" -ForegroundColor Red
    Write-Host "3. Check Device Manager for COM ports" -ForegroundColor Red
    exit 1
}

