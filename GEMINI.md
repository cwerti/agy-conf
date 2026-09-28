# Antigravity & Gemini Agent Configuration

This file inherits all guidelines defined in [AGENTS.md](file:///D:/uriit/agy-conf/AGENTS.md).

## Quick Summary
- Review [rules/fastapi.md](file:///D:/uriit/agy-conf/rules/fastapi.md) for backend FastAPI best practices (Pydantic v2, async DB sessions, testing).
- Check [rules/workspaces.md](file:///D:/uriit/agy-conf/rules/workspaces.md) for Work (GitLab/YouTrack) vs Personal (GitHub) guidelines.
- Check [rules/memory.md](file:///D:/uriit/agy-conf/rules/memory.md) for autonomous session journaling in `memory/sessions/`.
- Check [rules/security.md](file:///D:/uriit/agy-conf/rules/security.md) for allowed/prohibited commands.
- Check [rules/git.md](file:///D:/uriit/agy-conf/rules/git.md) for commit standards.
- Consult and evolve configurations via [`config-architect`](file:///D:/uriit/agy-conf/skills/config-architect/SKILL.md).
- Customizations can be added via the [`add-customization`](file:///D:/uriit/agy-conf/skills/add-customization/SKILL.md) skill.
- Record sessions and decisions via the [`session-journal`](file:///D:/uriit/agy-conf/skills/session-journal/SKILL.md) skill.
- Specialized subagents are available in `subagents/` (`code-reviewer`, `database-architect`, `api-tester`, `debugger`).
- Global MCP servers are managed in `mcp/mcp_config.json`.
