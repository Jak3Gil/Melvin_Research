# Start true live video streaming from both cameras

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Live Video Streams" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start individual ffmpeg streams in background on Jetson
Write-Host "Starting Camera 1 stream (port 8080)..." -ForegroundColor Yellow
ssh "${Username}@${Hostname}" "nohup ffmpeg -f v4l2 -input_format mjpeg -video_size 1280x720 -framerate 30 -i /dev/video0 -f mjpeg -q:v 5 -an - > /tmp/cam1_stream.mjpg &" 2>&1 | Out-Null

Write-Host "Starting Camera 2 stream (port 8081)..." -ForegroundColor Yellow  
ssh "${Username}@${Hostname}" "nohup ffmpeg -f v4l2 -input_format mjpeg -video_size 1280x720 -framerate 30 -i /dev/video2 -f mjpeg -q:v 5 -an - > /tmp/cam2_stream.mjpg &" 2>&1 | Out-Null

# Actually, let's use a simpler approach - fast image refresh with ultra-low latency
Write-Host "`nUsing ultra-fast refresh method (100ms = 10 FPS)..." -ForegroundColor Yellow
Write-Host "This provides near-live video experience." -ForegroundColor Yellow
Write-Host ""

# Start capture loop on Jetson
ssh "${Username}@${Hostname}" "while true; do fswebcam -d /dev/video0 -r 1280x720 --no-banner --skip 1 ~/camera_captures/camera1.jpg 2>/dev/null; fswebcam -d /dev/video2 -r 1280x720 --no-banner --skip 1 ~/camera_captures/camera2.jpg 2>/dev/null; sleep 0.1; done > /dev/null 2>&1 &"

Write-Host "Capture loop started on Jetson." -ForegroundColor Green
Start-Sleep -Seconds 2

Write-Host "`nStarting local viewer with ultra-fast refresh..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Run ultra-fast viewer
.\view_cameras_ultra_fast.ps1 -Interval 0.1

