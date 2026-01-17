# Ultra-fast camera viewer - updates every 0.1 seconds for near-live experience

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin",
    [double]$Interval = 0.1  # 100ms = 10 FPS
)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ultra-Fast Live Camera Viewer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Refresh Rate: $($Interval*1000)ms ($([math]::Round(1/$Interval)) FPS)" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create local directory
$localDir = "camera_images"
if (-not (Test-Path $localDir)) {
    New-Item -ItemType Directory -Path $localDir | Out-Null
}

$camera1Path = Join-Path $PWD "${localDir}/camera1.jpg"
$camera2Path = Join-Path $PWD "${localDir}/camera2.jpg"

# Open images once (Windows will auto-refresh when files are updated)
if (-not (Get-Process | Where-Object {$_.MainWindowTitle -like "*camera1*"})) {
    if (Test-Path $camera1Path) {
        Start-Process $camera1Path
    }
}
if (-not (Get-Process | Where-Object {$_.MainWindowTitle -like "*camera2*"})) {
    if (Test-Path $camera2Path) {
        Start-Process $camera2Path
    }
}

$refreshCount = 0
$startTime = Get-Date

try {
    while ($true) {
        $refreshCount++
        
        # Capture and transfer in parallel using background jobs
        $job1 = Start-Job -ScriptBlock {
            param($host, $user, $local)
            scp "${user}@${host}:~/camera_captures/camera1.jpg" "${local}/camera1.jpg" | Out-Null
        } -ArgumentList $Hostname, $Username, (Join-Path $PWD $localDir)
        
        $job2 = Start-Job -ScriptBlock {
            param($host, $user, $local)
            scp "${user}@${host}:~/camera_captures/camera2.jpg" "${local}/camera2.jpg" | Out-Null
        } -ArgumentList $Hostname, $Username, (Join-Path $PWD $localDir)
        
        # Capture on Jetson while transferring previous images
        ssh "${Username}@${Hostname}" "~/capture_cameras.sh" | Out-Null
        
        # Wait for transfers to complete
        Wait-Job $job1, $job2 | Out-Null
        Remove-Job $job1, $job2
        
        # Update display (touch files to trigger refresh)
        if ($refreshCount % 10 -eq 0) {
            $elapsed = ((Get-Date) - $startTime).TotalSeconds
            $fps = [math]::Round($refreshCount / $elapsed, 1)
            Write-Host "[$refreshCount] $fps FPS - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green
        }
        
        Start-Sleep -Milliseconds ($Interval * 1000)
    }
} catch {
    Write-Host "`nStopped" -ForegroundColor Yellow
} finally {
    Write-Host "`nTotal updates: $refreshCount" -ForegroundColor Cyan
}

