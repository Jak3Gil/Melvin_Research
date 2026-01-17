# Interactive Motor Tester Launcher
# Run this script to test motors interactively

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Interactive Motor Tester" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting motor tester..." -ForegroundColor Yellow
Write-Host ""
Write-Host "CONTROLS:" -ForegroundColor Green
Write-Host "  W / w - Move motor forward (small jog)" -ForegroundColor White
Write-Host "  S / s - Move motor backward (small jog)" -ForegroundColor White
Write-Host "  SPACE - Next motor" -ForegroundColor White
Write-Host "  Q / q - Quit" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to start..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Set-Location (Join-Path $PSScriptRoot "..\scripts")
python test_motors_interactive.py COM3 921600

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error occurred. Press any key to exit..." -ForegroundColor Red
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

