# Start Live Camera Streams from Jetson
# Opens both camera streams in browser

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin",
    [int]$Port = 8080
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Live Camera Streams" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get Jetson IP
Write-Host "Getting Jetson IP address..." -ForegroundColor Yellow
$jetsonIP = ssh "${Username}@${Hostname}" "hostname -I | awk '{print `$1}'"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to get Jetson IP" -ForegroundColor Red
    exit 1
}

Write-Host "Jetson IP: $jetsonIP" -ForegroundColor Green
Write-Host ""

# Start streaming server in background
Write-Host "Starting camera stream server on Jetson..." -ForegroundColor Yellow
Write-Host "Server will run in background. Use 'ssh ${Username}@${Hostname} pkill -f camera_stream_server.py' to stop" -ForegroundColor Yellow
Write-Host ""

# Start server in background
ssh "${Username}@${Hostname}" "nohup python3 ~/camera_stream_server.py $Port > /tmp/camera_stream.log 2>&1 &"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to start stream server" -ForegroundColor Red
    exit 1
}

# Wait a moment for server to start
Start-Sleep -Seconds 3

# Check if server is running
$checkServer = ssh "${Username}@${Hostname}" "pgrep -f camera_stream_server.py"
if (-not $checkServer) {
    Write-Host "Warning: Server may not have started. Check logs:" -ForegroundColor Yellow
    Write-Host "  ssh ${Username}@${Hostname} cat /tmp/camera_stream.log" -ForegroundColor Cyan
    exit 1
}

Write-Host "Server started successfully!" -ForegroundColor Green
Write-Host ""

# Construct URLs
$streamUrl = "http://${jetsonIP}:${Port}/"
$stream1Url = "http://${jetsonIP}:${Port}/stream1.mjpg"
$stream2Url = "http://${jetsonIP}:${Port}/stream2.mjpg"

Write-Host "========================================" -ForegroundColor Green
Write-Host "Camera Stream URLs:" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "View Both Cameras: $streamUrl" -ForegroundColor Cyan
Write-Host "Camera 1 Only: $stream1Url" -ForegroundColor Cyan
Write-Host "Camera 2 Only: $stream2Url" -ForegroundColor Cyan
Write-Host ""

# Open in browser
Write-Host "Opening streams in browser..." -ForegroundColor Yellow
Start-Process $streamUrl

Write-Host ""
Write-Host "Streams are now live!" -ForegroundColor Green
Write-Host "To stop the server, run:" -ForegroundColor Yellow
Write-Host "  ssh ${Username}@${Hostname} 'pkill -f camera_stream_server.py'" -ForegroundColor Cyan

