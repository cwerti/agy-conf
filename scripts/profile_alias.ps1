# ==============================================================================
# PowerShell Profile Shortcuts for Universal AI Agent Configuration
# To load in your PowerShell session:
#   . D:\uriit\agy-conf\scripts\profile_alias.ps1
# Or append to your $PROFILE:
#   Add-Content $PROFILE "`n. '$((Get-Item $MyInvocation.MyCommand.Path).FullName)'"
# ==============================================================================

$script:AgyConfRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

# 1. Quick Sync with Git
function agy-sync {
    param([string]$Message = "")
    & "$script:AgyConfRoot\scripts\sync.ps1" -CommitMessage $Message
}

# 2. Dynamic Database Switcher for MCP
function agy-db {
    param([string]$DbUrl = "")
    if ($DbUrl) {
        & python "$script:AgyConfRoot\scripts\update_db_connection.py" $DbUrl
    } else {
        Write-Host "Auto-detecting DATABASE_URL in current project directory..." -ForegroundColor Cyan
        & python "$script:AgyConfRoot\scripts\update_db_connection.py" --auto-detect (Get-Location).Path
    }
}

# 3. Autonomous Session Logger
function agy-log {
    param(
        [Parameter(Mandatory=$true)][string]$Topic,
        [Parameter(Mandatory=$true)][string]$Objective,
        [string]$Reasoning = "Session recorded via PowerShell shortcut."
    )
    & python "$script:AgyConfRoot\scripts\record_session.py" $Topic $Objective $Reasoning
}

# 4. YouTrack Issue Lookup
function agy-yt {
    param([Parameter(Mandatory=$true)][string]$IssueId)
    & python "$script:AgyConfRoot\scripts\youtrack_client.py" get $IssueId
}

# 5. Environment Doctor
function agy-doctor {
    Write-Host "--- Checking Core Tooling ---" -ForegroundColor Cyan
    python --version
    node -v
    git --version
    where.exe npx
    Write-Host "`n--- Testing Security Gate ---" -ForegroundColor Cyan
    & python "$script:AgyConfRoot\security\check_command.py" "git status"
}

Write-Host "AGY PowerShell shortcuts loaded: agy-sync, agy-db, agy-log, agy-yt, agy-doctor" -ForegroundColor DarkCyan
