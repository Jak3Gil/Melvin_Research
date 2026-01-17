# Motor Studio - Force English Interface

Write-Host "Motor Studio - Force English Mode" -ForegroundColor Cyan
Write-Host ""

$translationsPath = "C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122\translations"
$motorToolPath = "C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122"

# Step 1: Backup and remove the empty English file
Write-Host "Step 1: Removing empty English translation file..." -ForegroundColor Yellow

$enFile = Join-Path $translationsPath "qt_en.qm"
$enBackup = Join-Path $translationsPath "qt_en.qm.backup"

if (Test-Path $enFile) 
{
    if (-not (Test-Path $enBackup)) 
    {
        Copy-Item $enFile $enBackup -Force
        Write-Host "  Backed up qt_en.qm" -ForegroundColor Green
    }
    Remove-Item $enFile -Force
    Write-Host "  Removed empty English file" -ForegroundColor Green
}

# Step 2: Disable all other language files
Write-Host ""
Write-Host "Step 2: Disabling non-English translations..." -ForegroundColor Yellow

$languageFiles = Get-ChildItem -Path $translationsPath -Filter "qt_*.qm"
foreach ($file in $languageFiles) 
{
    $disabledName = $file.FullName + ".disabled"
    if (-not (Test-Path $disabledName)) 
    {
        Rename-Item $file.FullName $disabledName -Force
        Write-Host "  Disabled $($file.Name)" -ForegroundColor Gray
    }
}

Write-Host "  All non-English translations disabled" -ForegroundColor Green

# Step 3: Set environment variables for English
Write-Host ""
Write-Host "Step 3: Setting English environment..." -ForegroundColor Yellow

$env:LANG = "en_US.UTF-8"
$env:LC_ALL = "en_US.UTF-8"
$env:LANGUAGE = "en_US:en"

Write-Host "  Environment configured for English" -ForegroundColor Green

# Step 4: Launch Motor Studio
Write-Host ""
Write-Host "Step 4: Launching Motor Studio..." -ForegroundColor Yellow
Write-Host ""

$motorToolExe = Join-Path $motorToolPath "motor_tool.exe"

if (Test-Path $motorToolExe) 
{
    Start-Process -FilePath $motorToolExe -WorkingDirectory $motorToolPath
    
    Write-Host "Motor Studio Launched in English!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The interface should now be in English." -ForegroundColor White
    Write-Host ""
    Write-Host "To restore other languages later, run:" -ForegroundColor Yellow
    Write-Host "  .\restore_motor_studio_languages.ps1" -ForegroundColor Cyan
    Write-Host ""
} 
else 
{
    Write-Host "Motor Studio executable not found!" -ForegroundColor Red
    Write-Host "  Expected: $motorToolExe" -ForegroundColor Yellow
}

Write-Host ""
pause

