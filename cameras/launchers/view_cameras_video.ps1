# View cameras as live video streams
# Supports UDP, RTSP, and HTTP video streams

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin",
    [string]$Method = "UDP"  # UDP, RTSP, or HTTP
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Live Video Camera Streams" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$jetsonIP = ssh "${Username}@${Hostname}" "hostname -I | cut -d' ' -f1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to get Jetson IP" -ForegroundColor Red
    exit 1
}

Write-Host "Jetson IP: $jetsonIP" -ForegroundColor Green
Write-Host ""

# Check for VLC
$vlcPath = $null
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

if ($Method -eq "UDP") {
    Write-Host "Starting UDP video streams..." -ForegroundColor Yellow
    Write-Host "Camera 1: udp://@:5004" -ForegroundColor Cyan
    Write-Host "Camera 2: udp://@:5005" -ForegroundColor Cyan
    Write-Host ""
    
    if ($vlcPath) {
        Write-Host "Opening Camera 1 in VLC..." -ForegroundColor Green
        Start-Process $vlcPath -ArgumentList "udp://@:5004"
        Start-Sleep -Seconds 1
        Write-Host "Opening Camera 2 in VLC..." -ForegroundColor Green
        Start-Process $vlcPath -ArgumentList "udp://@:5005"
    } else {
        Write-Host "VLC not found. Please install VLC Media Player:" -ForegroundColor Yellow
        Write-Host "  https://www.videolan.org/vlc/" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Or use VLC manually:" -ForegroundColor Yellow
        Write-Host "  Media > Open Network Stream" -ForegroundColor White
        Write-Host "  Enter: udp://@:5004" -ForegroundColor White
    }
    
} elseif ($Method -eq "HTTP") {
    Write-Host "Starting HTTP video streams..." -ForegroundColor Yellow
    Write-Host "Camera 1: http://${jetsonIP}:8080/camera1" -ForegroundColor Cyan
    Write-Host "Camera 2: http://${jetsonIP}:8080/camera2" -ForegroundColor Cyan
    Write-Host ""
    
    if ($vlcPath) {
        Start-Process $vlcPath -ArgumentList "http://${jetsonIP}:8080/camera1"
        Start-Sleep -Seconds 1
        Start-Process $vlcPath -ArgumentList "http://${jetsonIP}:8080/camera2"
    } else {
        Write-Host "Opening in default browser..." -ForegroundColor Yellow
        Start-Process "http://${jetsonIP}:8080/camera1"
        Start-Sleep -Seconds 1
        Start-Process "http://${jetsonIP}:8080/camera2"
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Video streams opened!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

