# Launch Motor Studio in English
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Launching Motor Studio in English" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables for English
$env:LANG = "en_US"
$env:LC_ALL = "en_US.UTF-8"
$env:QT_TRANSLATE_LANG = "en"

# Launch Motor Studio
$motorStudioPath = "C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122\motor_tool.exe"

if (Test-Path $motorStudioPath) {
    Write-Host "✓ Found Motor Studio" -ForegroundColor Green
    Write-Host "✓ Launching with English language settings..." -ForegroundColor Green
    Write-Host ""
    
    Start-Process -FilePath $motorStudioPath -WorkingDirectory "C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122"
    
    Write-Host "Motor Studio launched!" -ForegroundColor Green
    Write-Host ""
    Write-Host "If it's still in Chinese, look for:" -ForegroundColor Yellow
    Write-Host "  - Settings/设置 menu" -ForegroundColor White
    Write-Host "  - Language/语言 option" -ForegroundColor White
    Write-Host "  - Select English/英文" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "✗ Motor Studio not found at expected location" -ForegroundColor Red
    Write-Host "  Path: $motorStudioPath" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

