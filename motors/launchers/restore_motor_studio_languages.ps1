# Restore Motor Studio Language Files

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Restore Motor Studio Languages" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$translationsPath = "C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122\translations"

# Restore the original English file
$enBackup = Join-Path $translationsPath "qt_en.qm.backup"
$enFile = Join-Path $translationsPath "qt_en.qm"

if (Test-Path $enBackup) {
    Copy-Item $enBackup $enFile -Force
    Write-Host "✓ Restored original qt_en.qm" -ForegroundColor Green
}

# Re-enable all disabled language files
$disabledFiles = Get-ChildItem -Path $translationsPath -Filter "*.qm.disabled"
foreach ($file in $disabledFiles) {
    $originalName = $file.FullName -replace '\.disabled$', ''
    Rename-Item $file.FullName $originalName -Force
    Write-Host "✓ Restored $($file.Name)" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  All languages restored!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

