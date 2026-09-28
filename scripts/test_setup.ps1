# ==============================================================================
# Comprehensive Self-Test & Verification Script for agy-conf
# Usage in PowerShell:
#   .\scripts\test_setup.ps1
# ==============================================================================

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location -Path $RepoRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Running Automated Verification for agy-conf Environment   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$Passed = 0
$Failed = 0

function Assert-Test {
    param(
        [string]$Name,
        [scriptblock]$TestBlock
    )
    try {
        $result = & $TestBlock
        if ($result -eq $true) {
            Write-Host "  [PASS] $Name" -ForegroundColor Green
            $script:Passed++
        } else {
            Write-Host "  [FAIL] $Name" -ForegroundColor Red
            $script:Failed++
        }
    } catch {
        Write-Host "  [FAIL] $Name - Error: $_" -ForegroundColor Red
        $script:Failed++
    }
}

# 1. Tooling & Runtimes
Write-Host "`n[1/6] Core Runtimes & Tools:" -ForegroundColor Yellow

Assert-Test "Python 3.10+ Available" {
    $v = python --version 2>&1
    return ($v -like "*Python 3*")
}

Assert-Test "Node.js & npx in PATH" {
    $n = where.exe npx 2>&1
    return ($n -ne $null -and $n.Length -gt 0)
}

Assert-Test "Git Available" {
    $g = git --version 2>&1
    return ($g -like "*git version*")
}

# 2. JSON Integrity Checks
Write-Host "`n[2/6] Config Files Integrity (JSON Syntax):" -ForegroundColor Yellow

Assert-Test "security/commands.json is valid JSON" {
    python -m json.tool security/commands.json > $null
    return ($LASTEXITCODE -eq 0)
}

Assert-Test "security/hooks.json is valid JSON" {
    python -m json.tool security/hooks.json > $null
    return ($LASTEXITCODE -eq 0)
}

Assert-Test "mcp/mcp_config.json is valid JSON" {
    python -m json.tool mcp/mcp_config.json > $null
    return ($LASTEXITCODE -eq 0)
}

Assert-Test "mcp/mcp_config.example.json is valid JSON" {
    python -m json.tool mcp/mcp_config.example.json > $null
    return ($LASTEXITCODE -eq 0)
}

# 3. Security Policy Gate (Commands)
Write-Host "`n[3/6] Security Policy Gate (check_command.py):" -ForegroundColor Yellow

Assert-Test "Safe command allowed (pytest)" {
    $res = python security/check_command.py "pytest tests/" | ConvertFrom-Json
    return ($res.decision -eq "allow")
}

Assert-Test "Poe task runner allowed (poetry run poe code-check)" {
    $res = python security/check_command.py "poetry run poe code-check" | ConvertFrom-Json
    return ($res.decision -eq "allow")
}

Assert-Test "Dangerous command blocked (rm -rf /)" {
    $res = python security/check_command.py "rm -rf /" | ConvertFrom-Json
    return ($res.decision -eq "deny")
}

Assert-Test "Database wipe blocked (alembic downgrade base)" {
    $res = python security/check_command.py "alembic downgrade base" | ConvertFrom-Json
    return ($res.decision -eq "deny")
}

Assert-Test "Git push to personal repo allowed (agy-conf)" {
    $res = python security/check_command.py "git push origin main" | ConvertFrom-Json
    return ($res.decision -eq "allow")
}

Assert-Test "Git force push to main blocked" {
    $res = python security/check_command.py "git push --force origin main" | ConvertFrom-Json
    return ($res.decision -eq "deny")
}

# 4. Secret Leak Protection (check_secrets.py)
Write-Host "`n[4/6] Secret Leak Guard (check_secrets.py):" -ForegroundColor Yellow

Assert-Test "Clean code writing is permitted" {
    $cleanPayload = '{"toolCall": {"name": "write_to_file", "args": {"TargetFile": "app.py", "CodeContent": "def test(): pass"}}}'
    $res = $cleanPayload | python security/check_secrets.py | ConvertFrom-Json
    return ($res.decision -eq "allow")
}

Assert-Test "Hardcoded GitHub token is blocked" {
    $leakPayload = '{"toolCall": {"name": "write_to_file", "args": {"TargetFile": "app.py", "CodeContent": "TOKEN = ''ghp_123456789012345678901234567890''"}}}'
    $res = $leakPayload | python security/check_secrets.py | ConvertFrom-Json
    return ($res.decision -eq "deny")
}

Assert-Test "Hardcoded GitLab token is blocked" {
    $leakPayload = '{"toolCall": {"name": "write_to_file", "args": {"TargetFile": "app.py", "CodeContent": "TOKEN = ''glpat-12345678901234567890''"}}}'
    $res = $leakPayload | python security/check_secrets.py | ConvertFrom-Json
    return ($res.decision -eq "deny")
}

Assert-Test "Writing tokens into .env is permitted" {
    $envPayload = '{"toolCall": {"name": "write_to_file", "args": {"TargetFile": ".env", "CodeContent": "SECRET=ghp_123456789012345678901234567890"}}}'
    $res = $envPayload | python security/check_secrets.py | ConvertFrom-Json
    return ($res.decision -eq "allow")
}

# 5. Database Auto-Detection
Write-Host "`n[5/6] Database Auto-Detection (update_db_connection.py):" -ForegroundColor Yellow

Assert-Test "Auto-detects DB from culture_backend and normalizes asyncpg" {
    $out = python scripts/update_db_connection.py --auto-detect "d:\uriit\culture_backend" | ConvertFrom-Json
    return ($out.status -eq "success" -and $out.database_url -like "*localhost:5469*")
}

# 6. Memory & Subagents
Write-Host "`n[6/6] Subagents & Documentation Manifests:" -ForegroundColor Yellow

$Subagents = @("code-reviewer", "database-architect", "api-tester", "debugger")
foreach ($sub in $Subagents) {
    Assert-Test "Subagent manifest exists: $sub" {
        return (Test-Path "subagents\$sub\subagent.json")
    }
}

Assert-Test "Initial session log exists in memory/sessions/" {
    return (Test-Path "memory\sessions\2026-09-28-init-agent-conf.md")
}

# Summary
Write-Host "`n==========================================================" -ForegroundColor Cyan
if ($Failed -eq 0) {
    Write-Host " ALL $Passed VERIFICATION TESTS PASSED SUCCESSFULLY! " -ForegroundColor Green
} else {
    Write-Host " TESTS FAILED: $Failed, Passed: $Passed " -ForegroundColor Red
}
Write-Host "==========================================================" -ForegroundColor Cyan
