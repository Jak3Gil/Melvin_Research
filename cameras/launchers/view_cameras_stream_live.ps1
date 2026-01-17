# Live Video Stream Viewer for USB Cameras
# Opens browser windows showing live MJPEG streams from both cameras

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin",
    [int]$Port1 = 8080,
    [int]$Port2 = 8081
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $ProjectRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Live Camera Stream Viewer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Upload and start streaming server on Jetson
Write-Host "Step 1: Starting streaming server on Jetson..." -ForegroundColor Yellow

# Upload stream script if it exists in cameras/scripts
$streamScript = "stream_cameras_live.sh"
$streamScriptPath = Join-Path $ProjectRoot "cameras\scripts\$streamScript"
if (Test-Path $streamScriptPath) {
    scp $streamScriptPath "${Username}@${Hostname}:~/$streamScript"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to upload stream script" -ForegroundColor Red
        exit 1
    }
}

# Start streaming server in background
Write-Host "Starting MJPEG streams on Jetson..." -ForegroundColor Yellow
ssh "${Username}@${Hostname}" "chmod +x ~/$streamScript && nohup ~/$streamScript $Port1 $Port2 > ~/stream.log 2>&1 &"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to start streaming server" -ForegroundColor Red
    exit 1
}

Write-Host "Waiting for streams to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Step 2: Open browser windows with streams
Write-Host "`nStep 2: Opening live video streams..." -ForegroundColor Yellow

$url1 = "http://${Hostname}:${Port1}/stream.mjpg"
$url2 = "http://${Hostname}:${Port2}/stream.mjpg"

Write-Host "Camera 1 stream: $url1" -ForegroundColor Green
Write-Host "Camera 2 stream: $url2" -ForegroundColor Green

# Open streams in browser
Write-Host "`nOpening Camera 1 in browser..." -ForegroundColor Cyan
Start-Process $url1

Start-Sleep -Seconds 1

Write-Host "Opening Camera 2 in browser..." -ForegroundColor Cyan
Start-Process $url2

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Live streams are now running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Camera 1: $url1" -ForegroundColor White
Write-Host "Camera 2: $url2" -ForegroundColor White
Write-Host ""
Write-Host "The streams will continue running in the background on the Jetson." -ForegroundColor Yellow
Write-Host "To stop the streams, run:" -ForegroundColor Yellow
Write-Host "  ssh ${Username}@${Hostname} 'pkill -f stream_cameras_live.sh'" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to close this window (streams will continue running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

