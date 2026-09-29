# Universal Agent Configuration Installer (Windows PowerShell)
# [CmdletBinding()]
param (
    [string]$ProjectDir = "",
    [switch]$GlobalOnly,
    [switch]$Force,
    [switch]$Reconfigure
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$UserProfile = $env:USERPROFILE
$GeminiGlobalConfig = Join-Path $UserProfile ".gemini\config"
$EnvExampleFile = Join-Path $RepoRoot ".env.example"
$EnvFile = Join-Path $RepoRoot ".env"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Agent Config Installer & Environment Setup (Universal)   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Repository root: $RepoRoot"

# ------------------------------------------------------------------------------
# 0. Interactive Environment Configuration (.env from .env.example)
# ------------------------------------------------------------------------------
function Setup-EnvInteractive {
    Write-Host "`n[0/4] Checking Environment Configuration (.env)..." -ForegroundColor Cyan

    if (-not (Test-Path $EnvExampleFile)) {
        Write-Host "  Warning: .env.example not found at $EnvExampleFile" -ForegroundColor Yellow
        return
    }

    if ((Test-Path $EnvFile) -and -not $Reconfigure) {
        Write-Host "  [OK] .env file already exists. (Use -Reconfigure to prompt again)" -ForegroundColor Green
        # Load .env into current process session
        Get-Content $EnvFile | ForEach-Object {
            $line = $_.Trim()
            if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
                $parts = $line.Split("=", 2)
                $k = $parts[0].Trim()
                $v = $parts[1].Trim().Trim('"').Trim("'")
                [System.Environment]::SetEnvironmentVariable($k, $v, "Process")
            }
        }
        return
    }

    Write-Host "`nInitializing .env configuration from .env.example..." -ForegroundColor Yellow
    Write-Host "Press [Enter] to accept the suggested value in brackets, or type your value." -ForegroundColor DarkGray
    Write-Host "Leave empty if a service is not used yet.`n" -ForegroundColor DarkGray

    $NewLines = @()
    $ConfiguredVars = @{}
    $Lines = Get-Content $EnvExampleFile

    foreach ($line in $Lines) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            $NewLines += $line
            if ($trimmed.StartsWith("#") -and -not $trimmed.StartsWith("# =") -and -not $trimmed.StartsWith("# -")) {
                Write-Host "  $trimmed" -ForegroundColor DarkCyan
            }
            continue
        }

        if ($trimmed.Contains("=")) {
            $parts = $trimmed.Split("=", 2)
            $key = $parts[0].Trim()
            $defaultVal = $parts[1].Trim()

            # Interactive prompt
            $promptMsg = "  -> Enter value for $key"
            if ($defaultVal) {
                $promptMsg += " [$defaultVal]"
            }
            $promptMsg += ": "

            $userInput = Read-Host -Prompt $promptMsg

            if ([string]::IsNullOrWhiteSpace($userInput)) {
                $finalVal = $defaultVal
            } else {
                $finalVal = $userInput.Trim()
            }

            $NewLines += "$key=$finalVal"
            $ConfiguredVars[$key] = $finalVal
            [System.Environment]::SetEnvironmentVariable($key, $finalVal, "Process")
        }
    }

    # Save to .env
    $NewLines | Set-Content -Path $EnvFile -Encoding UTF8
    Write-Host "`n  [SUCCESS] Created .env configuration file." -ForegroundColor Green

    # Optional: Apply to Windows User Profile
    Write-Host ""
    $applyToWindows = Read-Host -Prompt "Apply these variables to your Windows User Profile permanently for AGY & MCP? [Y/n]"
    if ([string]::IsNullOrWhiteSpace($applyToWindows) -or $applyToWindows.ToLower().StartsWith("y")) {
        foreach ($k in $ConfiguredVars.Keys) {
            $val = $ConfiguredVars[$k]
            if ($val -and -not $val.Contains("xxxx") -and -not $val.Contains("your-")) {
                [System.Environment]::SetEnvironmentVariable($k, $val, "User")
                Write-Host "  [APPLIED] Set User EnvVar: $k" -ForegroundColor Green
            }
        }
        Write-Host "  User environment variables updated successfully." -ForegroundColor Green
    }
}

Setup-EnvInteractive

# ------------------------------------------------------------------------------
# Helper for Symlinks / Copies
# ------------------------------------------------------------------------------
function Create-SafeLinkOrCopy {
    param (
        [string]$Source,
        [string]$Destination
    )

    $DestParent = Split-Path -Parent $Destination
    if (-not (Test-Path $DestParent)) {
        New-Item -ItemType Directory -Path $DestParent -Force | Out-Null
    }

    if (Test-Path $Destination) {
        if ($Force) {
            Remove-Item -Path $Destination -Force -Recurse
        } else {
            Write-Host "  [SKIP] Destination exists: $Destination (use -Force to overwrite)" -ForegroundColor Yellow
            return
        }
    }

    try {
        New-Item -ItemType SymbolicLink -Path $Destination -Target $Source -ErrorAction Stop | Out-Null
        Write-Host "  [LINK] Created symlink: $Destination -> $Source" -ForegroundColor Green
    } catch {
        if ((Get-Item $Source).PSIsContainer) {
            Copy-Item -Path $Source -Destination $Destination -Recurse -Force
        } else {
            Copy-Item -Path $Source -Destination $Destination -Force
        }
        Write-Host "  [COPY] Copied (symlink fallback): $Destination" -ForegroundColor Green
    }
}

# ------------------------------------------------------------------------------
# 1. Global Setup (~/.gemini/config) & MCP Merger
# ------------------------------------------------------------------------------
Write-Host "`n[1/5] Setting up Global AGY Configuration & MCP Servers..." -ForegroundColor Cyan
if (-not (Test-Path $GeminiGlobalConfig)) {
    New-Item -ItemType Directory -Path $GeminiGlobalConfig -Force | Out-Null
}

$MergeScript = Join-Path $RepoRoot "scripts\merge_mcp_config.py"
if (Test-Path $MergeScript) {
    try {
        Write-Host "  Safely merging MCP configurations (preserving existing user servers and creating backups)..." -ForegroundColor DarkCyan
        $mergeRaw = & python $MergeScript
        $mergeObj = $mergeRaw | ConvertFrom-Json
        Write-Host "  [OK] MCP servers merged successfully." -ForegroundColor Green
        if ($mergeObj.preserved_existing_servers) {
            Write-Host "    Preserved existing servers: $($mergeObj.preserved_existing_servers -join ', ')" -ForegroundColor Yellow
        }
        if ($mergeObj.added_new_servers) {
            Write-Host "    Added new servers:         $($mergeObj.added_new_servers -join ', ')" -ForegroundColor Green
        }
    } catch {
        Write-Host "  Warning: MCP merger encountered an issue: $_" -ForegroundColor Yellow
    }
}

# Global PreToolUse & PreInvocation Security / Memory Hooks
$GlobalHooksDest = Join-Path $GeminiGlobalConfig "hooks.json"
$NormalizedRepo = ($RepoRoot -replace '\\', '/')
$GlobalHooksContent = @"
{
  "autonomous-memory-recall": {
    "enabled": true,
    "PreInvocation": [
      {
        "type": "command",
        "command": "python $NormalizedRepo/scripts/memory_recall.py",
        "timeout": 5
      }
    ]
  },
  "command-security-guard": {
    "enabled": true,
    "PreToolUse": [
      {
        "matcher": "run_command",
        "hooks": [
          {
            "type": "command",
            "command": "python $NormalizedRepo/security/check_command.py",
            "timeout": 10
          }
        ]
      }
    ]
  },
  "secret-leak-guard": {
    "enabled": true,
    "PreToolUse": [
      {
        "matcher": "write_to_file|replace_file_content",
        "hooks": [
          {
            "type": "command",
            "command": "python $NormalizedRepo/security/check_secrets.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
"@
Set-Content -Path $GlobalHooksDest -Value $GlobalHooksContent -Encoding UTF8
Write-Host "  [OK] Installed global PreToolUse & PreInvocation hooks." -ForegroundColor Green

# Ensure repository and workspace are registered in trustedFolders.json
$TrustedFoldersPath = Join-Path $UserProfile ".gemini\trustedFolders.json"
if (Test-Path $TrustedFoldersPath) {
    try {
        $tf = Get-Content $TrustedFoldersPath -Raw | ConvertFrom-Json
        $tfModified = $false
        $key1 = $NormalizedRepo.ToLower()
        $key2 = ($NormalizedRepo.Substring(0, 1).ToUpper() + $NormalizedRepo.Substring(1))
        if (-not $tf.PSObject.Properties[$key1]) {
            $tf | Add-Member -NotePropertyName $key1 -NotePropertyValue "TRUST_FOLDER" -Force
            $tfModified = $true
        }
        if (-not $tf.PSObject.Properties[$key2]) {
            $tf | Add-Member -NotePropertyName $key2 -NotePropertyValue "TRUST_FOLDER" -Force
            $tfModified = $true
        }
        if ($tfModified) {
            $tf | ConvertTo-Json | Set-Content -Path $TrustedFoldersPath -Encoding UTF8
            Write-Host "  [OK] Registered repository in trustedFolders.json." -ForegroundColor Green
        }
    } catch {
        Write-Host "  Warning: could not update trustedFolders.json: $_" -ForegroundColor Yellow
    }
}

# Ensure local .agents/hooks.json exists for current repo
$LocalAgentsDir = Join-Path $RepoRoot ".agents"
if (-not (Test-Path $LocalAgentsDir)) {
    New-Item -ItemType Directory -Path $LocalAgentsDir -Force | Out-Null
}
Set-Content -Path (Join-Path $LocalAgentsDir "hooks.json") -Value $GlobalHooksContent -Encoding UTF8

# ------------------------------------------------------------------------------
# 2. Subagent Blueprints Verification
# ------------------------------------------------------------------------------
Write-Host "`n[2/5] Validating Specialized AI Subagent Blueprints..." -ForegroundColor Cyan
$SubagentsDir = Join-Path $RepoRoot "subagents"
if (Test-Path $SubagentsDir) {
    $SubDirs = Get-ChildItem -Path $SubagentsDir -Directory
    foreach ($sd in $SubDirs) {
        $cfg = Join-Path $sd.FullName "subagent.json"
        if (Test-Path $cfg) {
            try {
                $subData = Get-Content $cfg -Raw | ConvertFrom-Json
                Write-Host "  [OK] Registered blueprint: $($subData.name) - $($subData.role)" -ForegroundColor Green
            } catch {
                Write-Host "  [ERR] Invalid subagent JSON: $cfg" -ForegroundColor Red
            }
        }
    }
    Write-Host "  Subagents are activated on demand via define_subagent / invoke_subagent." -ForegroundColor DarkGray
}

# ------------------------------------------------------------------------------
# 3. Project-level setup (if requested)
# ------------------------------------------------------------------------------
if ($ProjectDir -and -not $GlobalOnly) {
    Write-Host "`n[3/5] Setting up Project Workspace: $ProjectDir" -ForegroundColor Cyan
    if (-not (Test-Path $ProjectDir)) {
        Write-Host "  Error: Target project directory does not exist: $ProjectDir" -ForegroundColor Red
    } else {
        $AgentsDir = Join-Path $ProjectDir ".agents"
        $RulesDir = Join-Path $AgentsDir "rules"
        $SkillsDir = Join-Path $AgentsDir "skills"
        New-Item -ItemType Directory -Path $RulesDir -Force | Out-Null
        New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null

        # Link AGENTS.md and GEMINI.md
        Create-SafeLinkOrCopy -Source (Join-Path $RepoRoot "AGENTS.md") -Destination (Join-Path $ProjectDir "AGENTS.md")
        Create-SafeLinkOrCopy -Source (Join-Path $RepoRoot "GEMINI.md") -Destination (Join-Path $ProjectDir "GEMINI.md")

        # Copy/Link hooks
        Create-SafeLinkOrCopy -Source (Join-Path $RepoRoot "security\hooks.json") -Destination (Join-Path $AgentsDir "hooks.json")
    }
} else {
    Write-Host "`n[3/5] Skipping project workspace setup (pass -ProjectDir <path> to configure a project)." -ForegroundColor DarkGray
}

# ------------------------------------------------------------------------------
# 4. Environment verification & Git Hooks
# ------------------------------------------------------------------------------
Write-Host "`n[4/5] Validating Environment, Security Policy & Git Hooks..." -ForegroundColor Cyan
try {
    $TestOutput = & python (Join-Path $RepoRoot "security\check_command.py") "git status"
    Write-Host "  Security policy test passed: $TestOutput" -ForegroundColor Green
} catch {
    Write-Host "  Warning: Python or check_command.py check failed. Ensure Python is installed." -ForegroundColor Yellow
}

# Configure Git hooks path
if (Test-Path (Join-Path $RepoRoot ".git")) {
    try {
        git config core.hooksPath .githooks
        Write-Host "  Git hooks enabled (.githooks/pre-commit and .githooks/commit-msg)." -ForegroundColor Green
    } catch {
        Write-Host "  Warning: could not configure git core.hooksPath." -ForegroundColor Yellow
    }
}

# Build or refresh local FTS5 agent memory index
$MemIndexScript = Join-Path $RepoRoot "scripts\memory_index.py"
if (Test-Path $MemIndexScript) {
    try {
        $idxRes = & python $MemIndexScript build
        Write-Host "  [OK] Agent memory FTS5 index built successfully." -ForegroundColor Green
    } catch {
        Write-Host "  Warning: could not build agent memory index: $_" -ForegroundColor Yellow
    }
}

Write-Host "`n[5/5] Installation completed successfully!" -ForegroundColor Cyan
Write-Host "`n⚡ Tip: Load PowerShell shortcuts by running:" -ForegroundColor Yellow
Write-Host "  . '$RepoRoot\scripts\profile_alias.ps1'" -ForegroundColor White
Write-Host "Or add it to your permanent `$PROFILE for instant access to agy-db, agy-sync, agy-log, agy-yt!`n" -ForegroundColor DarkGray
