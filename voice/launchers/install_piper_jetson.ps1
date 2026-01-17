# Piper TTS Installation Helper Script
# This script connects to Jetson and installs Piper TTS

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Piper TTS Installation for Jetson" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Upload the installation script
Write-Host "Step 1: Uploading installation script to Jetson..." -ForegroundColor Yellow

# Use scp to copy the script
$scriptPath = Join-Path $PSScriptRoot "install_piper_jetson.sh"
if (-not (Test-Path $scriptPath)) {
    Write-Host "Error: install_piper_jetson.sh not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Copying script to Jetson..." -ForegroundColor Yellow
scp $scriptPath "${Username}@${Hostname}:~/install_piper_jetson.sh"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to copy script to Jetson!" -ForegroundColor Red
    Write-Host "Make sure SSH is accessible and you can connect to the Jetson." -ForegroundColor Yellow
    exit 1
}

Write-Host "Script uploaded successfully!" -ForegroundColor Green
Write-Host ""

# Execute the installation script on Jetson
Write-Host "Step 2: Running installation script on Jetson..." -ForegroundColor Yellow
Write-Host "This may take several minutes. Please wait..." -ForegroundColor Yellow
Write-Host ""

ssh "${Username}@${Hostname}" "chmod +x ~/install_piper_jetson.sh && ~/install_piper_jetson.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Installation completed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Installation encountered errors" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Please check the output above for details." -ForegroundColor Yellow
}

