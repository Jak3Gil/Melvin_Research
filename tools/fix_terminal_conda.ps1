# Script to help fix terminal issues caused by conda initialization
# This checks for conda initialization in shell config files

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Checking for conda initialization issues" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Windows locations
Write-Host "Checking Windows shell config files..." -ForegroundColor Yellow
$files = @(
    "$env:USERPROFILE\.zshrc",
    "$env:USERPROFILE\.bashrc",
    "$env:USERPROFILE\.bash_profile"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "Found: $file" -ForegroundColor Green
        $content = Get-Content $file -Raw
        if ($content -match '__conda_setup|conda.*shell') {
            Write-Host "  WARNING: Contains conda initialization!" -ForegroundColor Red
            Write-Host "  You should comment out the conda initialization lines" -ForegroundColor Yellow
        } else {
            Write-Host "  No conda initialization found" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "Checking WSL..." -ForegroundColor Yellow
if (Get-Command wsl -ErrorAction SilentlyContinue) {
    Write-Host "WSL is installed" -ForegroundColor Green
    Write-Host ""
    Write-Host "To check WSL shell config files, run in WSL:" -ForegroundColor Cyan
    Write-Host "  wsl" -ForegroundColor White
    Write-Host "  cat ~/.zshrc | grep conda" -ForegroundColor White
    Write-Host "  cat ~/.bashrc | grep conda" -ForegroundColor White
    Write-Host ""
    Write-Host "To fix, edit the file and comment out conda lines:" -ForegroundColor Cyan
    Write-Host "  wsl" -ForegroundColor White
    Write-Host "  nano ~/.zshrc  (or ~/.bashrc)" -ForegroundColor White
    Write-Host "  # Comment out lines starting with __conda_setup" -ForegroundColor White
} else {
    Write-Host "WSL not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "If you found conda initialization, comment out these lines:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host '__conda_setup="$(''/Users/ferferof/anaconda3/bin/conda'' ''shell.zsh'' ''hook'' 2> /dev/null)"' -ForegroundColor Gray
Write-Host 'if [ $? -eq 0 ]; then' -ForegroundColor Gray
Write-Host '    eval "$__conda_setup"' -ForegroundColor Gray
Write-Host 'else' -ForegroundColor Gray
Write-Host '    if [ -f "/Users/ferferof/anaconda3/etc/profile.d/conda.sh" ]; then' -ForegroundColor Gray
Write-Host '        . "/Users/ferferof/anaconda3/etc/profile.d/conda.sh"' -ForegroundColor Gray
Write-Host '    else' -ForegroundColor Gray
Write-Host '        export PATH="$PATH:/Users/ferferof/anaconda3/bin"' -ForegroundColor Gray
Write-Host '    fi' -ForegroundColor Gray
Write-Host 'fi' -ForegroundColor Gray
Write-Host 'unset __conda_setup' -ForegroundColor Gray
Write-Host ""
Write-Host "Add # at the start of each line to comment them out." -ForegroundColor Yellow
Write-Host ""

