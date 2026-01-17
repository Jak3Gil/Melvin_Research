# Local Camera Viewer - Continuously updates local image files
# Opens images in Windows image viewer which auto-refreshes

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin",
    [int]$Port = 8080,
    [double]$FPS = 30.0
)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Local Camera Viewer (Live Updates)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Host "Python not found! Please install Python 3." -ForegroundColor Red
    exit 1
}

# Check for required Python packages
Write-Host "Checking Python dependencies..." -ForegroundColor Yellow
$hasRequests = python -c "import requests; print('OK')" 2>$null
if (-not $hasRequests) {
    Write-Host "Installing requests library..." -ForegroundColor Yellow
    python -m pip install requests --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install requests" -ForegroundColor Red
        exit 1
    }
}

$jetsonIP = ssh "${Username}@${Hostname}" "hostname -I | cut -d' ' -f1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to get Jetson IP" -ForegroundColor Red
    exit 1
}

Write-Host "Jetson IP: $jetsonIP" -ForegroundColor Green
Write-Host ""

# Create output directory
$outputDir = "camera_images"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

Write-Host "Starting local viewer..." -ForegroundColor Yellow
Write-Host "Images will update continuously in: $outputDir" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start Python viewer in background
$pythonScript = Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..\scripts")).Path "camera_viewer_simple.py"
Start-Process python -ArgumentList $pythonScript, $jetsonIP, $Port -NoNewWindow

Start-Sleep -Seconds 3

# Open images in Windows viewer
$cam1Path = Join-Path $PWD "${outputDir}/camera1_live.jpg"
$cam2Path = Join-Path $PWD "${outputDir}/camera2_live.jpg"

# Wait for first images
$maxWait = 10
$waited = 0
while (-not (Test-Path $cam1Path) -and $waited -lt $maxWait) {
    Start-Sleep -Seconds 1
    $waited++
}

if (Test-Path $cam1Path) {
    Write-Host "Opening Camera 1..." -ForegroundColor Green
    Start-Process $cam1Path
}

if (Test-Path $cam2Path) {
    Write-Host "Opening Camera 2..." -ForegroundColor Green
    Start-Process $cam2Path
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Viewer started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Images are updating at ~30 FPS" -ForegroundColor Cyan
Write-Host "Close the image windows and press Ctrl+C here to stop" -ForegroundColor Yellow
Write-Host ""

