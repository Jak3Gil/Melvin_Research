# Live Real-Time Camera Viewer
# Starts HTTP MJPEG streams from both cameras and opens in browser

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin",
    [int]$Port = 8080
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Live Real-Time Camera Streams" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get Jetson IP
Write-Host "Getting Jetson IP address..." -ForegroundColor Yellow
$jetsonIP = ssh "${Username}@${Hostname}" "hostname -I | cut -d' ' -f1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to get Jetson IP" -ForegroundColor Red
    exit 1
}

Write-Host "Jetson IP: $jetsonIP" -ForegroundColor Green
Write-Host ""

# Check if server is already running
Write-Host "Checking for existing stream server..." -ForegroundColor Yellow
$existing = ssh "${Username}@${Hostname}" "pgrep -f camera_stream_server.py"
if ($existing) {
    Write-Host "Stopping existing server (PID: $existing)..." -ForegroundColor Yellow
    ssh "${Username}@${Hostname}" "pkill -f camera_stream_server.py"
    Start-Sleep -Seconds 2
}

# Verify cameras are available
Write-Host "Verifying cameras..." -ForegroundColor Yellow
$camera1 = ssh "${Username}@${Hostname}" "test -e /dev/video0 && echo 'OK' || echo 'NOT FOUND'"
$camera2 = ssh "${Username}@${Hostname}" "test -e /dev/video2 && echo 'OK' || echo 'NOT FOUND'"

if ($camera1 -ne "OK" -or $camera2 -ne "OK") {
    Write-Host "Error: Cameras not found!" -ForegroundColor Red
    Write-Host "Camera 1: $camera1" -ForegroundColor Red
    Write-Host "Camera 2: $camera2" -ForegroundColor Red
    exit 1
}

Write-Host "Camera 1: OK" -ForegroundColor Green
Write-Host "Camera 2: OK" -ForegroundColor Green
Write-Host ""

# Start server in background
Write-Host "Starting live stream server..." -ForegroundColor Yellow
ssh "${Username}@${Hostname}" "nohup python3 ~/camera_stream_server.py $Port > /tmp/camera_stream.log 2>&1 &"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to start stream server" -ForegroundColor Red
    exit 1
}

# Wait for server to start
Write-Host "Waiting for server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Verify server is running
$serverCheck = ssh "${Username}@${Hostname}" "pgrep -f camera_stream_server.py"
if (-not $serverCheck) {
    Write-Host "Error: Server failed to start. Checking logs..." -ForegroundColor Red
    ssh "${Username}@${Hostname}" "cat /tmp/camera_stream.log"
    exit 1
}

Write-Host "Server started successfully (PID: $serverCheck)!" -ForegroundColor Green
Write-Host ""

# Construct URLs
$streamUrl = "http://${jetsonIP}:${Port}/"
$stream1Url = "http://${jetsonIP}:${Port}/stream1.mjpg"
$stream2Url = "http://${jetsonIP}:${Port}/stream2.mjpg"

Write-Host "========================================" -ForegroundColor Green
Write-Host "Live Stream URLs:" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "View Both Cameras (Side by Side):" -ForegroundColor Yellow
Write-Host "  $streamUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Individual Streams:" -ForegroundColor Yellow
Write-Host "  Camera 1: $stream1Url" -ForegroundColor Cyan
Write-Host "  Camera 2: $stream2Url" -ForegroundColor Cyan
Write-Host ""

# Open in default browser
Write-Host "Opening streams in browser..." -ForegroundColor Yellow
Start-Process $streamUrl

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Streams are now LIVE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "The browser should show both cameras side-by-side in real-time." -ForegroundColor White
Write-Host ""
Write-Host "To stop the server:" -ForegroundColor Yellow
Write-Host "  ssh ${Username}@${Hostname} 'pkill -f camera_stream_server.py'" -ForegroundColor Cyan
Write-Host ""
Write-Host "To check server status:" -ForegroundColor Yellow
Write-Host "  ssh ${Username}@${Hostname} 'pgrep -f camera_stream_server.py'" -ForegroundColor Cyan
Write-Host ""

