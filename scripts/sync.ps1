# Sync script for Windows
param (
    [string]$CommitMessage = ""
)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location -Path $RepoRoot

Write-Host "Syncing agent configuration repository..." -ForegroundColor Cyan

# Check git status
$Status = git status --porcelain
if ($Status) {
    Write-Host "Local changes detected:" -ForegroundColor Yellow
    git status -s
    if ($CommitMessage) {
        Write-Host "Committing changes with message: '$CommitMessage'..." -ForegroundColor Cyan
        git add -A
        git commit -m $CommitMessage
    } else {
        Write-Host "Note: Run with -CommitMessage 'your message' to automatically commit and push." -ForegroundColor Yellow
    }
}

# Pull latest
Write-Host "Pulling latest changes from remote..." -ForegroundColor Cyan
try {
    git pull --rebase
} catch {
    Write-Host "Warning: git pull failed or remote not configured yet." -ForegroundColor Yellow
}

# Run installer
& "$PSScriptRoot\install.ps1" -GlobalOnly
