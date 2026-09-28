# Universal Agent Instructions

This repository contains shared rules, skills, MCP configurations, and command security policies for AI coding agents (Antigravity/AGY, Claude Code, Cursor, Windsurf, Copilot).

## Core Principles
1. **Direct & Actionable**: Keep responses concise and focused on tested code changes.
2. **Safety First**: Never execute destructive system commands. Comply strictly with [security/commands.json](file:///D:/uriit/agy-conf/security/commands.json).
3. **Verified Code**: Run tests, linters, or manual verification commands after proposing or editing code.
4. **Clean Git History**: Follow Conventional Commits (`feat:`, `fix:`, `refactor:`, `chore:`). Never force-push to `main`/`master`.
5. **Autonomous Documentation**: Maintain session reasoning and decisions in `memory/sessions/` and sync to personal GitHub.

## Detailed Modular Rules
- **General Behavior**: See [rules/general.md](file:///D:/uriit/agy-conf/rules/general.md)
- **FastAPI & Python Standards**: See [rules/fastapi.md](file:///D:/uriit/agy-conf/rules/fastapi.md)
- **Multi-Environment (Work GitLab/YouTrack vs Personal GitHub)**: See [rules/workspaces.md](file:///D:/uriit/agy-conf/rules/workspaces.md)
- **Autonomous Memory & Session Logging**: See [rules/memory.md](file:///D:/uriit/agy-conf/rules/memory.md)
- **Git & Commit Guidelines**: See [rules/git.md](file:///D:/uriit/agy-conf/rules/git.md)
- **Security & Permissions**: See [rules/security.md](file:///D:/uriit/agy-conf/rules/security.md)
- **Code Quality & Testing**: See [rules/code-quality.md](file:///D:/uriit/agy-conf/rules/code-quality.md)

## Customization Structure
- **Skills**: Progressive workflows located in `skills/<skill_name>/SKILL.md`
  - [`config-architect`](file:///D:/uriit/agy-conf/skills/config-architect/SKILL.md): Interactive AI consultant to discuss, design, and plan changes to this repository.
  - [`session-journal`](file:///D:/uriit/agy-conf/skills/session-journal/SKILL.md): Autonomously document session reasoning, decisions, and sync to personal GitHub.
  - [`add-customization`](file:///D:/uriit/agy-conf/skills/add-customization/SKILL.md): Interactively add new rules, skills, MCP, or commands to this repo.
  - [`env-sync`](file:///D:/uriit/agy-conf/skills/env-sync/SKILL.md): Sync configurations across machines.
  - [`env-doctor`](file:///D:/uriit/agy-conf/skills/env-doctor/SKILL.md): Troubleshoot and diagnose environment tools.
  - [`mcp-manager`](file:///D:/uriit/agy-conf/skills/mcp-manager/SKILL.md): Safely configure and test MCP servers.
  - [`youtrack-helper`](file:///D:/uriit/agy-conf/skills/youtrack-helper/SKILL.md): Fetch task requirements and post updates to JetBrains YouTrack.
- **Subagents**: Specialized autonomous agents declared in `subagents/`
  - `code-reviewer`: Senior Python & FastAPI read-only reviewer for PRs, Pydantic v2, and async safety.
  - `database-architect`: PostgreSQL & SQLAlchemy 2.0 specialist for migrations and query plans.
  - `api-tester`: QA engineer writing and running pytest-asyncio and httpx test suites.
  - `debugger`: Troubleshooter isolating bugs and analyzing logs in an isolated workspace.
- **MCP Servers**: Centralized server declarations in `mcp/mcp_config.json` (examples in `mcp/mcp_config.example.json`)
- **Security & Hooks**: Pre-execution gates in `security/hooks.json` validated by `security/check_command.py`
