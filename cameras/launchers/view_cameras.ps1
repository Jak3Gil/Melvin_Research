# USB Camera Viewer Script
# Captures images from both cameras on Jetson and displays them

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin"
)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "USB Camera Viewer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Capture images on Jetson
Write-Host "Step 1: Capturing images from cameras..." -ForegroundColor Yellow
ssh "${Username}@${Hostname}" "~/capture_cameras.sh"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to capture images" -ForegroundColor Red
    exit 1
}

# Step 2: Create local directory
Write-Host "`nStep 2: Creating local directory..." -ForegroundColor Yellow
$localDir = "camera_images"
if (-not (Test-Path $localDir)) {
    New-Item -ItemType Directory -Path $localDir | Out-Null
}

# Step 3: Transfer images
Write-Host "Step 3: Transferring images from Jetson..." -ForegroundColor Yellow
scp "${Username}@${Hostname}:~/camera_captures/camera1.jpg" "${localDir}/camera1.jpg"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to transfer camera1.jpg" -ForegroundColor Red
    exit 1
}

scp "${Username}@${Hostname}:~/camera_captures/camera2.jpg" "${localDir}/camera2.jpg"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to transfer camera2.jpg" -ForegroundColor Red
    exit 1
}

# Step 4: Open images
Write-Host "`nStep 4: Opening images..." -ForegroundColor Yellow
$camera1 = Join-Path $PWD "${localDir}/camera1.jpg"
$camera2 = Join-Path $PWD "${localDir}/camera2.jpg"

if (Test-Path $camera1) {
    Write-Host "Opening Camera 1 image..." -ForegroundColor Green
    Start-Process $camera1
}

if (Test-Path $camera2) {
    Write-Host "Opening Camera 2 image..." -ForegroundColor Green
    Start-Process $camera2
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Success! Both camera images opened." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Images saved in: $((Resolve-Path $localDir).Path)" -ForegroundColor Cyan

