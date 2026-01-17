# COM3 CAN Adapter Check Script
# Checks if COM3 (CH340) is configured as a CAN adapter

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COM3 CAN Adapter Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$com3Device = Get-PnpDevice | Where-Object { $_.FriendlyName -match "COM3" }

if ($com3Device) {
    Write-Host "Device Found:" -ForegroundColor Green
    Write-Host "  Name: $($com3Device.FriendlyName)" -ForegroundColor White
    Write-Host "  Status: $($com3Device.Status)" -ForegroundColor $(if ($com3Device.Status -eq "OK") { "Green" } else { "Red" })
    Write-Host "  Instance ID: $($com3Device.InstanceId)" -ForegroundColor Gray
    Write-Host ""
    
    if ($com3Device.InstanceId -match "VID_1A86&PID_7523") {
        Write-Host "Device Type: CH340 USB-to-Serial Bridge" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Note: CH340 is typically a USB-to-Serial chip." -ForegroundColor Cyan
        Write-Host "Some CAN adapters (like CANable, CANtact) use CH340 with SLCAN protocol." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "To use COM3 as a CAN adapter:" -ForegroundColor Yellow
        Write-Host "  1. The device must support SLCAN (Serial Line CAN)" -ForegroundColor White
        Write-Host "  2. Use CAN tools like:" -ForegroundColor White
        Write-Host "     - can-utils (Linux)" -ForegroundColor White
        Write-Host "     - slcand (slcan daemon)" -ForegroundColor White
        Write-Host "     - PCAN-View (if compatible)" -ForegroundColor White
        Write-Host ""
    }
} else {
    Write-Host "COM3 not found!" -ForegroundColor Red
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing COM3 Connection" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test if COM3 is available
try {
    $port = New-Object System.IO.Ports.SerialPort COM3,115200,None,8,one
    $port.Open()
    Write-Host "COM3 opened successfully at 115200 baud" -ForegroundColor Green
    Write-Host ""
    Write-Host "Port Settings:" -ForegroundColor Yellow
    Write-Host "  Baud Rate: $($port.BaudRate)" -ForegroundColor White
    Write-Host "  Data Bits: $($port.DataBits)" -ForegroundColor White
    Write-Host "  Parity: $($port.Parity)" -ForegroundColor White
    Write-Host "  Stop Bits: $($port.StopBits)" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Checking for CAN adapter (SLCAN protocol)..." -ForegroundColor Yellow
    Write-Host "Sending SLCAN version command: V" -ForegroundColor Cyan
    $port.Write("V`r")
    Start-Sleep -Milliseconds 100
    
    if ($port.BytesToRead -gt 0) {
        $response = $port.ReadExisting()
        Write-Host "Response: $response" -ForegroundColor Green
        if ($response -match "v\d+\.\d+") {
            Write-Host "SLCAN adapter detected!" -ForegroundColor Green
        }
    } else {
        Write-Host "No immediate response (device may need initialization)" -ForegroundColor Yellow
    }
    
    $port.Close()
    Write-Host "Port closed." -ForegroundColor Green
} catch {
    Write-Host "Error accessing COM3: $_" -ForegroundColor Red
    Write-Host "Make sure no other program is using COM3." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "If this is a CAN adapter:" -ForegroundColor White
Write-Host "  - Use CAN utilities to configure bitrate" -ForegroundColor White
Write-Host "  - Common bitrates: 125k, 250k, 500k, 1M" -ForegroundColor White
Write-Host ""
Write-Host "If this is your ESP32:" -ForegroundColor White
Write-Host "  - Use: python -m platformio device monitor --port COM3" -ForegroundColor Cyan
Write-Host "  - Or upload code to COM3" -ForegroundColor White
Write-Host ""

