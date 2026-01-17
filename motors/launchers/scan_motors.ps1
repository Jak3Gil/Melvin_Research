# Robstride Motor Scanner - PowerShell Version
# Scans for Robstride motors using L91 protocol over USB-to-CAN

param(
    [string]$Port = "COM3",
    [int]$BaudRate = 921600,
    [switch]$ScanAll,
    [int]$TestMotor
)

Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Robstride Motor Scanner (L91 Protocol)              ║" -ForegroundColor Cyan
Write-Host "║  Based on: https://github.com/Jak3Gil/Melvin_november║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Port: $Port" -ForegroundColor Yellow
Write-Host "Baud Rate: $BaudRate" -ForegroundColor Yellow
Write-Host ""

# Check if pyserial is available
try {
    $null = python -c "import serial" 2>&1
    Write-Host "✓ Python serial library found" -ForegroundColor Green
    Write-Host ""
    Write-Host "Running Python scanner..." -ForegroundColor Cyan
    Write-Host ""
    
    Set-Location (Join-Path $PSScriptRoot "..\scripts")
    $args = @($Port, $BaudRate)
    if ($ScanAll) { $args += "--scan-all" }
    if ($TestMotor) { $args += "--test"; $args += $TestMotor }
    
    python scan_robstride_motors.py $args
    exit $LASTEXITCODE
} catch {
    Write-Host "✗ Python serial library not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install pyserial:" -ForegroundColor Yellow
    Write-Host "  pip install pyserial" -ForegroundColor White
    Write-Host ""
    Write-Host "Or use the Python script directly:" -ForegroundColor Yellow
    Write-Host "  python scan_robstride_motors.py $Port $BaudRate" -ForegroundColor White
    exit 1
}

