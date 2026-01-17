# Stop Jetson Camera Streams

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin"
)

Write-Host "Stopping camera streams on Jetson..." -ForegroundColor Yellow

ssh "${Username}@${Hostname}" "pkill -f 'ffmpeg.*video[02]' 2>/dev/null; echo 'Streams stopped'"

Write-Host "Done!" -ForegroundColor Green

