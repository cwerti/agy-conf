# Universal Agent Configuration Installer (Windows PowerShell)
# [CmdletBinding()]
param (
    [string]$ProjectDir = "",
    [switch]$AllProjects,
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

            $isOptional = ($key -match "GITLAB|YOUTRACK")

            # Interactive prompt
            if ($isOptional) {
                $promptMsg = "  -> Enter value for $key (Optional - press Enter to skip if not using)"
                if ($defaultVal -and $defaultVal -notmatch "xxxx") {
                    $promptMsg += " [$defaultVal]"
                }
            } else {
                $promptMsg = "  -> Enter value for $key"
                if ($defaultVal) {
                    $promptMsg += " [$defaultVal]"
                }
            }
            $promptMsg += ": "

            $userInput = Read-Host -Prompt $promptMsg

            if ([string]::IsNullOrWhiteSpace($userInput)) {
                if ($isOptional -and ($defaultVal -match "xxxx" -or -not $defaultVal)) {
                    $finalVal = ""
                } else {
                    $finalVal = $defaultVal
                }
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
# 3. Project Workspaces Setup
# ------------------------------------------------------------------------------
function Configure-SingleProject {
    param (
        [string]$TargetDir
    )
    if (-not (Test-Path $TargetDir)) { return }
    $normTarget = ($TargetDir -replace '\\', '/').ToLower()
    $normRepo = ($RepoRoot -replace '\\', '/').ToLower()
    if ($normTarget -eq $normRepo -or $normTarget -match "agent-memory") { return }

    $AgentsDir = Join-Path $TargetDir ".agents"
    $RulesDir = Join-Path $AgentsDir "rules"
    $SkillsDir = Join-Path $AgentsDir "skills"
    New-Item -ItemType Directory -Path $RulesDir -Force | Out-Null
    New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null

    # Link AGENTS.md and GEMINI.md
    Create-SafeLinkOrCopy -Source (Join-Path $RepoRoot "AGENTS.md") -Destination (Join-Path $TargetDir "AGENTS.md")
    Create-SafeLinkOrCopy -Source (Join-Path $RepoRoot "GEMINI.md") -Destination (Join-Path $TargetDir "GEMINI.md")

    # Copy/Link hooks
    Create-SafeLinkOrCopy -Source (Join-Path $RepoRoot "security\hooks.json") -Destination (Join-Path $AgentsDir "hooks.json")

    # Add to trustedFolders.json
    $tfPath = Join-Path $UserProfile ".gemini\trustedFolders.json"
    if (Test-Path $tfPath) {
        try {
            $tfData = Get-Content $tfPath -Raw | ConvertFrom-Json
            if (-not $tfData.PSObject.Properties[$normTarget]) {
                $tfData | Add-Member -NotePropertyName $normTarget -NotePropertyValue "TRUST_FOLDER" -Force
                $tfData | ConvertTo-Json -Depth 5 | Set-Content -Path $tfPath -Encoding UTF8
            }
        } catch {}
    }
    Write-Host "  [OK] Configured project: $TargetDir" -ForegroundColor Green
}

if ($ProjectDir -and -not $GlobalOnly) {
    Write-Host "`n[3/5] Setting up Project Workspace: $ProjectDir" -ForegroundColor Cyan
    if (-not (Test-Path $ProjectDir)) {
        Write-Host "  Error: Target project directory does not exist: $ProjectDir" -ForegroundColor Red
    } else {
        Configure-SingleProject -TargetDir $ProjectDir
    }
} elseif ($AllProjects -or (-not $GlobalOnly -and -not $ProjectDir)) {
    $shouldApplyAll = $AllProjects
    if (-not $AllProjects -and -not $GlobalOnly) {
        Write-Host "`n[3/5] Project Workspaces Setup..." -ForegroundColor Cyan
        $ans = Read-Host -Prompt "Apply configuration, AGENTS.md, and hooks to all discovered projects in workspace? [Y/n]"
        if ([string]::IsNullOrWhiteSpace($ans) -or $ans.ToLower().StartsWith("y")) {
            $shouldApplyAll = $true
        }
    }

    if ($shouldApplyAll) {
        Write-Host "`n[3/5] Applying Configuration to All Discovered Projects..." -ForegroundColor Cyan
        $discovered = @{}

        # A. From ~/.gemini/projects.json
        $geminiProjectsFile = Join-Path $UserProfile ".gemini\projects.json"
        if (Test-Path $geminiProjectsFile) {
            try {
                $pjson = Get-Content $geminiProjectsFile -Raw | ConvertFrom-Json
                if ($pjson.projects) {
                    foreach ($prop in $pjson.projects.PSObject.Properties) {
                        $pPath = $prop.Name
                        if (Test-Path $pPath) {
                            $discovered[$pPath] = $true
                        }
                    }
                }
            } catch {}
        }

        # B. Sibling directories in workspace root (e.g. D:\uriit\*)
        $ParentDir = Split-Path $RepoRoot -Parent
        if (Test-Path $ParentDir) {
            Get-ChildItem -Path $ParentDir -Directory | ForEach-Object {
                $candidate = $_.FullName
                if ($candidate -ne $RepoRoot -and $candidate -notmatch "agent-memory") {
                    $discovered[$candidate] = $true
                }
            }
        }

        $validCount = 0
        foreach ($p in $discovered.Keys) {
            $norm = ($p -replace '\\', '/').ToLower()
            $normR = ($RepoRoot -replace '\\', '/').ToLower()
            if ($norm -ne $normR -and $norm -notmatch "agent-memory" -and (Test-Path $p)) {
                Configure-SingleProject -TargetDir $p
                $validCount++
            }
        }
        Write-Host "  Successfully configured $validCount project workspace(s)." -ForegroundColor Green
    } else {
        Write-Host "`n[3/5] Skipping project workspace setup (pass -AllProjects or -ProjectDir <path>)." -ForegroundColor DarkGray
    }
} else {
    Write-Host "`n[3/5] Skipping project workspace setup (-GlobalOnly specified)." -ForegroundColor DarkGray
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

# Clone or locate personal memory repository if configured
$MemRepoUrl = $env:AGENT_MEMORY_REPO_URL
$ParentDir = Split-Path $RepoRoot -Parent
$DefaultMemDir = Join-Path $ParentDir "agent-memory"

if (-not $MemRepoUrl -and (Test-Path (Join-Path $RepoRoot ".env"))) {
    Get-Content (Join-Path $RepoRoot ".env") | ForEach-Object {
        if ($_ -match '^\s*AGENT_MEMORY_REPO_URL\s*=\s*(.+)$') {
            $MemRepoUrl = $matches[1].Trim().Trim('"').Trim("'")
        }
    }
}

if ($MemRepoUrl -and -not (Test-Path $DefaultMemDir)) {
    try {
        Write-Host "  Cloning personal memory repository from $MemRepoUrl..." -ForegroundColor DarkGray
        & git clone $MemRepoUrl $DefaultMemDir
        if (Test-Path $DefaultMemDir) {
            Write-Host "  [OK] Cloned personal memory repository to $DefaultMemDir" -ForegroundColor Green
        }
    } catch {
        Write-Host "  Note: Could not clone memory repository automatically. Clone it manually to: $DefaultMemDir" -ForegroundColor DarkGray
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

# ------------------------------------------------------------------------------
# PowerShell Profile Configuration
# ------------------------------------------------------------------------------
$ProfileShortcutLine = ". '$RepoRoot\scripts\profile_alias.ps1'"
$addProfile = Read-Host -Prompt "Add AGY shortcuts (agy-db, agy-sync, agy-mem, agy-doc) to your permanent PowerShell `$PROFILE? [Y/n]"
if ([string]::IsNullOrWhiteSpace($addProfile) -or $addProfile.ToLower().StartsWith("y")) {
    try {
        $profileDir = Split-Path -Parent $PROFILE
        if (-not (Test-Path $profileDir)) {
            New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
        }
        $existingProfile = if (Test-Path $PROFILE) { Get-Content $PROFILE -Raw } else { "" }
        if ($existingProfile -notmatch [regex]::Escape($ProfileShortcutLine)) {
            Add-Content -Path $PROFILE -Value "`n# AGY Agent Shortcuts`n$ProfileShortcutLine`n"
            Write-Host "  [OK] Added AGY shortcuts to $PROFILE" -ForegroundColor Green
        } else {
            Write-Host "  [OK] Shortcuts already present in $PROFILE" -ForegroundColor Green
        }
    } catch {
        Write-Host "  Warning: could not update `$PROFILE automatically: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n⚡ Tip: You can load shortcuts in current session manually with:" -ForegroundColor DarkGray
    Write-Host "  $ProfileShortcutLine" -ForegroundColor White
}
Write-Host "`nAll set! Open a new PowerShell terminal or run: . '$RepoRoot\scripts\profile_alias.ps1'`n" -ForegroundColor Cyan
