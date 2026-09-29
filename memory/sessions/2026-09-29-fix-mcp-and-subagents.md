# Session Log: fix-mcp-and-subagents

- **Date**: 2026-09-29
- **Workspace**: `D:\uriit\agy-conf`
- **Objective**: Safely install and merge MCP servers without deleting user configs, and define subagents

## Reasoning & Decisions
Created merge_mcp_config.py to safely preserve existing servers (postgres-dev, docx, GitLab) while adding new servers from agy-conf and resolving environment variables. Registered all 4 subagents (code-reviewer, database-architect, api-tester, debugger) and documented dynamic subagent protocol in rules/subagents.md.

## Files Changed
- `scripts/merge_mcp_config.py`
- `scripts/install.ps1`
- `scripts/install.sh`
- `rules/subagents.md`
- `AGENTS.md`
- `GEMINI.md`
