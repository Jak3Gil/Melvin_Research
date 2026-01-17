# Start Jetson Camera Streams
# This script starts the camera streaming servers on the Jetson

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Jetson Camera Streams" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting streaming servers on Jetson..." -ForegroundColor Yellow

# Start streaming servers in background
$startScript = @"
#!/bin/bash
WIDTH=640
HEIGHT=480
FPS=30

# Kill any existing streams
pkill -f "ffmpeg.*video0" 2>/dev/null
pkill -f "ffmpeg.*video2" 2>/dev/null

sleep 1

# Stream Camera 1
ffmpeg -f v4l2 -video_size `${WIDTH}x`${HEIGHT} -framerate `$FPS -i /dev/video0 \
    -f mjpeg -qscale 2 -listen 1 -timeout 60 http://0.0.0.0:8080/ > /tmp/cam1.log 2>&1 &
PID1=`$!

# Stream Camera 2  
ffmpeg -f v4l2 -video_size `${WIDTH}x`${HEIGHT} -framerate `$FPS -i /dev/video2 \
    -f mjpeg -qscale 2 -listen 1 -timeout 60 http://0.0.0.0:8081/ > /tmp/cam2.log 2>&1 &
PID2=`$!

echo "Streams started (PIDs: `$PID1, `$PID2)"
echo "Camera 1: http://$Hostname:8080"
echo "Camera 2: http://$Hostname:8081"
"@

$startScript | ssh "${Username}@${Hostname}" "cat > /tmp/start_streams.sh && chmod +x /tmp/start_streams.sh && /tmp/start_streams.sh"

Write-Host ""
Write-Host "Streams are now running!" -ForegroundColor Green
Write-Host ""
Write-Host "View cameras in your browser:" -ForegroundColor Yellow
Write-Host "  Camera 1: http://$Hostname:8080" -ForegroundColor Cyan
Write-Host "  Camera 2: http://$Hostname:8081" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or open view_jetson_cameras.html for a dual-view interface" -ForegroundColor Yellow
Write-Host ""

# Try to open HTML viewer
if (Test-Path "view_jetson_cameras.html") {
    $response = Read-Host "Open HTML viewer in browser? (Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        Start-Process "view_jetson_cameras.html"
        Write-Host "HTML viewer opened!" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "To stop streams, run: .\stop_camera_streams.ps1" -ForegroundColor Yellow

