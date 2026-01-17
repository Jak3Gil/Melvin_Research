# Live USB Camera Viewer Script
# Continuously captures and displays images from both cameras

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin",
    [int]$Interval = 2,
    [int]$MaxRefreshes = 0  # 0 = infinite
)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Live USB Camera Viewer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Jetson: ${Username}@${Hostname}" -ForegroundColor Yellow
Write-Host "Refresh Interval: $Interval seconds" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create local directory
$localDir = "camera_images"
if (-not (Test-Path $localDir)) {
    New-Item -ItemType Directory -Path $localDir | Out-Null
}

$camera1Path = Join-Path $PWD "${localDir}/camera1.jpg"
$camera2Path = Join-Path $PWD "${localDir}/camera2.jpg"

$refreshCount = 0

try {
    while ($true) {
        $refreshCount++
        Write-Host "[$refreshCount] Capturing and updating images..." -ForegroundColor Green
        
        # Capture images on Jetson
        ssh "${Username}@${Hostname}" "~/capture_cameras.sh" | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error: Failed to capture images" -ForegroundColor Red
            break
        }
        
        # Transfer images
        scp "${Username}@${Hostname}:~/camera_captures/camera1.jpg" "${localDir}/camera1.jpg" | Out-Null
        scp "${Username}@${Hostname}:~/camera_captures/camera2.jpg" "${localDir}/camera2.jpg" | Out-Null
        
        # Open/refresh images (Windows will update if already open)
        if (Test-Path $camera1Path) {
            Start-Process $camera1Path -ErrorAction SilentlyContinue
        }
        if (Test-Path $camera2Path) {
            Start-Process $camera2Path -ErrorAction SilentlyContinue
        }
        
        Write-Host "  Updated at $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
        
        if ($MaxRefreshes -gt 0 -and $refreshCount -ge $MaxRefreshes) {
            Write-Host "`nReached maximum refresh count ($MaxRefreshes)" -ForegroundColor Yellow
            break
        }
        
        Start-Sleep -Seconds $Interval
    }
} catch {
    Write-Host "`nStopped by user" -ForegroundColor Yellow
} finally {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Final images saved in: $((Resolve-Path $localDir).Path)" -ForegroundColor Green
    Write-Host "Total refreshes: $refreshCount" -ForegroundColor Green
}

