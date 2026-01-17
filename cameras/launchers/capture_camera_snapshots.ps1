# Capture Snapshots from Both Jetson Cameras

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin"
)

Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

Write-Host "Capturing snapshots from both cameras..." -ForegroundColor Yellow

# Capture Camera 1
Write-Host "Capturing Camera 1..." -ForegroundColor Cyan
ssh "${Username}@${Hostname}" "timeout 3 ffmpeg -f v4l2 -video_size 640x480 -i /dev/video0 -frames:v 1 -y /tmp/camera1_snapshot.jpg 2>/dev/null"
scp "${Username}@${Hostname}:/tmp/camera1_snapshot.jpg" "camera1_snapshot.jpg"

# Capture Camera 2
Write-Host "Capturing Camera 2..." -ForegroundColor Cyan
ssh "${Username}@${Hostname}" "timeout 3 ffmpeg -f v4l2 -video_size 640x480 -i /dev/video2 -frames:v 1 -y /tmp/camera2_snapshot.jpg 2>/dev/null"
scp "${Username}@${Hostname}:/tmp/camera2_snapshot.jpg" "camera2_snapshot.jpg"

Write-Host ""
Write-Host "Snapshots saved:" -ForegroundColor Green
Write-Host "  camera1_snapshot.jpg" -ForegroundColor White
Write-Host "  camera2_snapshot.jpg" -ForegroundColor White

