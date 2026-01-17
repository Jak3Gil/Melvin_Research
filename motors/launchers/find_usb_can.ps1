# USB-CAN Adapter Detection Script
# This script searches for and lists USB-CAN adapters connected to the system

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "USB-CAN Adapter Detection" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Search for CAN-related devices
Write-Host "Scanning for CAN devices..." -ForegroundColor Yellow
Write-Host ""

$canDevices = Get-PnpDevice | Where-Object {
    $_.FriendlyName -like "*CAN*" -or 
    $_.FriendlyName -like "*Kvaser*" -or 
    $_.FriendlyName -like "*PCAN*" -or 
    $_.FriendlyName -like "*CANable*" -or 
    $_.FriendlyName -like "*CANtact*" -or 
    $_.FriendlyName -like "*CANBus*" -or
    $_.FriendlyName -like "*Ixxat*" -or
    $_.FriendlyName -like "*Vector*" -or
    $_.FriendlyName -like "*ZLG*"
}

if ($canDevices) {
    Write-Host "Found CAN devices:" -ForegroundColor Green
    Write-Host ""
    $canDevices | ForEach-Object {
        $statusColor = if ($_.Status -eq "OK") { "Green" } else { "Red" }
        Write-Host "  Device: $($_.FriendlyName)" -ForegroundColor White
        Write-Host "  Status: $($_.Status)" -ForegroundColor $statusColor
        Write-Host "  Instance ID: $($_.InstanceId)" -ForegroundColor Gray
        Write-Host ""
    }
} else {
    Write-Host "No CAN devices found!" -ForegroundColor Red
    Write-Host ""
}

# Also check WMI for more detailed info
Write-Host "Checking WMI for CAN devices..." -ForegroundColor Yellow
Write-Host ""

$wmiCanDevices = Get-WmiObject Win32_PnPEntity | Where-Object {
    $_.Name -like "*CAN*" -or 
    $_.Name -like "*Kvaser*"
}

if ($wmiCanDevices) {
    Write-Host "WMI CAN devices:" -ForegroundColor Green
    Write-Host ""
    $wmiCanDevices | ForEach-Object {
        Write-Host "  Name: $($_.Name)" -ForegroundColor White
        Write-Host "  Status: $($_.Status)" -ForegroundColor $(if ($_.Status -eq "OK") { "Green" } else { "Red" })
        Write-Host "  DeviceID: $($_.DeviceID)" -ForegroundColor Gray
        Write-Host ""
    }
} else {
    Write-Host "No WMI CAN devices found." -ForegroundColor Yellow
    Write-Host ""
}

# Check for COM ports that might be CAN adapters
Write-Host "Checking COM ports for USB-CAN adapters..." -ForegroundColor Yellow
Write-Host ""

$comPorts = Get-WmiObject Win32_SerialPort | Where-Object {
    $_.Description -like "*CAN*" -or 
    $_.Description -like "*Kvaser*" -or
    $_.Name -like "*CAN*"
}

if ($comPorts) {
    Write-Host "CAN-related COM ports:" -ForegroundColor Green
    Write-Host ""
    $comPorts | ForEach-Object {
        Write-Host "  Port: $($_.DeviceID)" -ForegroundColor White
        Write-Host "  Description: $($_.Description)" -ForegroundColor Cyan
        Write-Host "  Name: $($_.Name)" -ForegroundColor Cyan
        Write-Host ""
    }
} else {
    Write-Host "No CAN-related COM ports found." -ForegroundColor Yellow
    Write-Host ""
}

# List all COM ports for reference
Write-Host "All available COM ports:" -ForegroundColor Yellow
$allPorts = [System.IO.Ports.SerialPort]::getportnames()
if ($allPorts) {
    Write-Host ($allPorts -join ', ') -ForegroundColor White
} else {
    Write-Host "No COM ports found." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Common USB-CAN Adapter Brands:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  - Kvaser" -ForegroundColor White
Write-Host "  - Peak PCAN" -ForegroundColor White
Write-Host "  - CANable (slcan)" -ForegroundColor White
Write-Host "  - CANtact" -ForegroundColor White
Write-Host "  - Ixxat" -ForegroundColor White
Write-Host "  - Vector" -ForegroundColor White
Write-Host "  - ZLG" -ForegroundColor White
Write-Host ""
Write-Host "If no devices are found, ensure:" -ForegroundColor Yellow
Write-Host "  1. USB-CAN adapter is plugged in" -ForegroundColor White
Write-Host "  2. Drivers are installed" -ForegroundColor White
Write-Host "  3. Check Device Manager manually (Win+X -> Device Manager)" -ForegroundColor White
Write-Host ""

