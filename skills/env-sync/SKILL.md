---
name: env-sync
description: Sync and deploy universal agent configurations (rules, MCP, skills, permissions) across machines and workspaces.
---

# Environment Sync Workflow

Use this skill when the user wants to sync their agent configuration repository, pull updates, or deploy configs to a new workspace or machine.

## Execution Steps

### 1. Check Git Status
Run `git status` in the config repository to see if there are uncommitted local modifications:
```powershell
git status
```
If there are uncommitted changes, ask the user if they wish to commit or stash them before pulling.

### 2. Fetch & Rebase
Pull the latest updates from remote:
```powershell
git pull --rebase origin main
```

### 3. Deploy to Current Environment
Run the cross-platform install script to refresh symlinks / copies:
- On Windows:
  ```powershell
  pwsh -ExecutionPolicy Bypass -File scripts/install.ps1
  ```
- On Linux / macOS:
  ```bash
  bash scripts/install.sh
  ```

### 4. Verify Policy & MCP Integrity
- Validate command security rules:
  ```powershell
  python security/check_command.py "git status"
  ```
- Check that `~/.gemini/config/mcp_config.json` is properly linked or synced.
