# View cameras using VLC Media Player
# VLC has excellent support for MJPEG streams

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin",
    [int]$Port = 8080
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Camera Viewer - VLC Method" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if VLC is installed
$vlcPath = Get-Command vlc -ErrorAction SilentlyContinue
if (-not $vlcPath) {
    # Try common VLC locations
    $commonPaths = @(
        "${env:ProgramFiles}\VideoLAN\VLC\vlc.exe",
        "${env:ProgramFiles(x86)}\VideoLAN\VLC\vlc.exe",
        "$env:LOCALAPPDATA\Programs\VideoLAN\VLC\vlc.exe"
    )
    
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            $vlcPath = $path
            break
        }
    }
}

if (-not $vlcPath) {
    Write-Host "VLC Media Player not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install VLC from: https://www.videolan.org/vlc/" -ForegroundColor Yellow
    Write-Host "Or use the Python viewer instead: python camera_viewer_simple.py" -ForegroundColor Yellow
    exit 1
}

$jetsonIP = ssh "${Username}@${Hostname}" "hostname -I | cut -d' ' -f1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to get Jetson IP" -ForegroundColor Red
    exit 1
}

$stream1Url = "http://${jetsonIP}:${Port}/stream1.mjpg"
$stream2Url = "http://${jetsonIP}:${Port}/stream2.mjpg"

Write-Host "Opening Camera 1 in VLC..." -ForegroundColor Yellow
Start-Process $vlcPath -ArgumentList $stream1Url

Start-Sleep -Seconds 1

Write-Host "Opening Camera 2 in VLC..." -ForegroundColor Yellow
Start-Process $vlcPath -ArgumentList $stream2Url

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Streams opened in VLC!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Camera 1: $stream1Url" -ForegroundColor Cyan
Write-Host "Camera 2: $stream2Url" -ForegroundColor Cyan
Write-Host ""

