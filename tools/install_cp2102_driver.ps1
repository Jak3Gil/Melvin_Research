# CP2102 Driver Installation Helper
# This script helps install the CP2102 USB to UART Bridge driver

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CP2102 Driver Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Your ESP32 uses a CP2102 USB-to-Serial chip" -ForegroundColor Yellow
Write-Host "The driver installation failed (Error status in Device Manager)" -ForegroundColor Yellow
Write-Host ""

Write-Host "To fix this:" -ForegroundColor Green
Write-Host "1. Download the CP2102 driver from:" -ForegroundColor White
Write-Host "   https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Or download directly:" -ForegroundColor White
Write-Host "   https://www.silabs.com/documents/public/software/CP210x_Universal_Windows_Driver.zip" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Extract the ZIP file" -ForegroundColor White
Write-Host "4. Run the installer (CP210xVCPInstaller_x64.exe for 64-bit Windows)" -ForegroundColor White
Write-Host "5. Restart your computer if prompted" -ForegroundColor White
Write-Host "6. Unplug and replug your ESP32" -ForegroundColor White
Write-Host "7. Check Device Manager - it should show a COM port now" -ForegroundColor White
Write-Host ""

Write-Host "After installing the driver, run the upload script again!" -ForegroundColor Green
Write-Host ""

# Try to open the download page
$response = Read-Host "Would you like me to open the download page? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    Start-Process "https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers"
    Write-Host "Download page opened in your browser!" -ForegroundColor Green
}

