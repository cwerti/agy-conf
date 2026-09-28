---
name: mcp-manager
description: Safely add, configure, test, and remove Model Context Protocol (MCP) servers across agents, including dynamic database switching.
---

# MCP Manager Workflow

Use this skill when adding a new MCP server, switching database connections between projects, or managing existing servers.

## Guidelines
1. **Catalog Lookup**: Consult `mcp/mcp_config.example.json` and `mcp/servers.md` to identify recommended configurations.
2. **Never Commit API Keys**: If a server requires secret keys, save them into `mcp/mcp_config.local.json` or system environment variables, never into `mcp/mcp_config.json`.
3. **Validation**: Test server execution manually or via CLI before registering.
4. **Deploy**: Run `scripts/install.ps1` (or `install.sh`) to link the updated MCP config into the global directory `~/.gemini/config/mcp_config.json`.

## Dynamic Project Database Switching
When switching between different backend projects with separate databases:

### Option A: Auto-Detect from Project Directory
```powershell
python scripts/update_db_connection.py --auto-detect "D:\uriit\my_project"
```
The script searches the project's `.env`, `alembic.ini`, or `config.py` for `DATABASE_URL`, normalizes it for MCP, and updates the configuration.

### Option B: Manual / On-Failure Update
If an MCP database tool fails to connect:
1. Prompt the user for the project's database URL.
2. Run:
   ```powershell
   python scripts/update_db_connection.py "<user_provided_url>"
   ```
3. The script automatically handles async SQLAlchemy drivers (`postgresql+asyncpg://` -> `postgresql://`) and updates the active MCP configuration.
