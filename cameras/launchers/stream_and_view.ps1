# Stream cameras and view locally
# Uses ffmpeg on Jetson to continuously capture, then syncs via SCP

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin"
)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Live Camera Stream Viewer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create local directory
$localDir = "camera_images"
if (-not (Test-Path $localDir)) {
    New-Item -ItemType Directory -Path $localDir | Out-Null
}

Write-Host "Starting camera capture on Jetson..." -ForegroundColor Yellow

# Start ffmpeg processes on Jetson to continuously update images
$cmd = @"
cd ~/camera_streams
ffmpeg -f v4l2 -input_format mjpeg -video_size 1280x720 -framerate 30 -i /dev/video0 -f image2 -update 1 -y camera1.jpg >/dev/null 2>&1 &
ffmpeg -f v4l2 -input_format mjpeg -video_size 1280x720 -framerate 30 -i /dev/video2 -f image2 -update 1 -y camera2.jpg >/dev/null 2>&1 &
echo "Streaming started"
"@

ssh "${Username}@${Hostname}" $cmd | Out-Null
Start-Sleep -Seconds 2

Write-Host "Starting image sync..." -ForegroundColor Yellow
Write-Host "Images will update at ~30 FPS" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

$cam1Path = Join-Path $PWD "${localDir}/camera1_live.jpg"
$cam2Path = Join-Path $PWD "${localDir}/camera2_live.jpg"
$opened = $false

try {
    $frameCount = 0
    while ($true) {
        # Sync images
        scp "${Username}@${Hostname}:~/camera_streams/camera1.jpg" $cam1Path 2>$null | Out-Null
        scp "${Username}@${Hostname}:~/camera_streams/camera2.jpg" $cam2Path 2>$null | Out-Null
        
        # Open images on first successful sync
        if (-not $opened -and (Test-Path $cam1Path) -and (Test-Path $cam2Path)) {
            Write-Host "Opening images..." -ForegroundColor Green
            Start-Process $cam1Path
            Start-Process $cam2Path
            $opened = $true
        }
        
        $frameCount++
        if ($frameCount % 30 -eq 0) {
            Write-Host "`rSynced $frameCount frames... " -NoNewline -ForegroundColor Cyan
        }
        
        Start-Sleep -Milliseconds 33  # ~30 FPS
    }
} catch {
    Write-Host "`nStopping..." -ForegroundColor Yellow
} finally {
    Write-Host "`nStopping camera streams on Jetson..." -ForegroundColor Yellow
    ssh "${Username}@${Hostname}" "pkill -f 'ffmpeg.*video[02]'" | Out-Null
    Write-Host "Done!" -ForegroundColor Green
}

