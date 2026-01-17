# Jetson SSH Connection Script
# This script helps establish SSH connection to NVIDIA Jetson device

param(
    [string]$Hostname = "192.168.1.119",
    [string]$Username = "melvin",
    [int]$Port = 22
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Jetson Connection Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Common Jetson hostnames/IPs to try
$commonHostnames = @(
    "192.168.1.119",  # Primary Jetson
    "jetson.local",
    "192.168.1.100",
    "192.168.0.100",
    "10.0.0.100",
    "192.168.1.101",
    "192.168.0.101"
)

# If hostname not provided, try to discover
if ([string]::IsNullOrWhiteSpace($Hostname)) {
    Write-Host "Hostname/IP not specified. Attempting to discover Jetson..." -ForegroundColor Yellow
    Write-Host ""
    
    # Try common hostnames first
    foreach ($hostnameTry in $commonHostnames) {
        Write-Host "Trying $hostnameTry..." -ForegroundColor Yellow -NoNewline
        $ping = Test-Connection -ComputerName $hostnameTry -Count 1 -Quiet -ErrorAction SilentlyContinue
        if ($ping) {
            Write-Host " Found!" -ForegroundColor Green
            $Hostname = $hostnameTry
            break
        } else {
            Write-Host " Not found" -ForegroundColor Gray
        }
    }
    
    # If not found, ask user
    if ([string]::IsNullOrWhiteSpace($Hostname)) {
        Write-Host ""
        Write-Host "Could not auto-discover Jetson. Please provide connection details:" -ForegroundColor Yellow
        $Hostname = Read-Host "Enter Jetson IP address or hostname"
        
        if ([string]::IsNullOrWhiteSpace($Hostname)) {
            Write-Host "Error: Hostname is required!" -ForegroundColor Red
            exit 1
        }
    }
}

# Ask for username if not provided
if ([string]::IsNullOrWhiteSpace($Username)) {
    $Username = Read-Host "Enter SSH username (default: jetson)"
    if ([string]::IsNullOrWhiteSpace($Username)) {
        $Username = "jetson"
    }
}

Write-Host ""
Write-Host "Connection Details:" -ForegroundColor Green
Write-Host "  Hostname: $Hostname" -ForegroundColor White
Write-Host "  Username: $Username" -ForegroundColor White
Write-Host "  Port: $Port" -ForegroundColor White
Write-Host ""

# Test connectivity
Write-Host "Testing connectivity..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName $Hostname -Count 2 -Quiet -ErrorAction SilentlyContinue

if (-not $ping) {
    Write-Host "Warning: Cannot ping $Hostname. The device may be offline or unreachable." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        exit 1
    }
} else {
    Write-Host "Connectivity test passed!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Connecting to Jetson..." -ForegroundColor Cyan
Write-Host ""

# Check if SSH is available
$sshPath = Get-Command ssh -ErrorAction SilentlyContinue
if (-not $sshPath) {
    Write-Host "Error: SSH command not found!" -ForegroundColor Red
    Write-Host "Please install OpenSSH Client:" -ForegroundColor Yellow
    Write-Host "  Settings > Apps > Optional Features > OpenSSH Client" -ForegroundColor White
    Write-Host "Or install via PowerShell (Admin):" -ForegroundColor White
    Write-Host "  Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0" -ForegroundColor Cyan
    exit 1
}

# Build SSH command
$sshCommand = "ssh -p $Port $Username@$Hostname"

Write-Host "Executing: $sshCommand" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: You may be prompted for password on first connection." -ForegroundColor Yellow
Write-Host "      Use Ctrl+D or type 'exit' to disconnect." -ForegroundColor Yellow
Write-Host ""

# Execute SSH connection
Invoke-Expression $sshCommand

