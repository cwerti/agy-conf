---
name: env-doctor
description: Inspect and diagnose developer tools, runtimes, MCP servers, and agent permissions in the current environment.
---

# Environment Doctor Workflow

Use this skill when setting up a new environment, troubleshooting tool failures, or diagnosing agent issues.

## Diagnostic Checklist

### 1. Core Tooling & Runtimes
Check the availability of essential developer tools:
```powershell
python --version
node -v
git --version
```

### 2. Antigravity & Agent Environment
- Check Antigravity version and configuration paths:
  - Global config path: `~/.gemini/config/`
  - Workspace customizations: `.agents/`
- Verify that `AGENTS.md` and `GEMINI.md` are present and accessible.

### 3. Command Security Gate
Run test evaluations against the security policy to ensure the hook and script function properly:
```powershell
# Safe command test (expected: allow)
python security/check_command.py "git status"

# Destructive command test (expected: deny)
python security/check_command.py "rm -rf /"

# Confirmation required test (expected: ask)
python security/check_command.py "git push origin feat"
```

### 4. MCP Servers Connectivity
Check if configured MCP executables (e.g. `uvx`, `npx`) are installed and discoverable in `$env:PATH`:
```powershell
where.exe uvx
where.exe npx
```
Review `mcp/mcp_config.json` for syntax errors.
