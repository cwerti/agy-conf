# Persistent Agent Memory & Context (Template)

This file serves as the long-term context for AI agents across sessions, reducing token consumption and preventing repetitive questions.

## Developer Profile & Stack
- **OS**: Windows (PowerShell / `pwsh`) or Linux/macOS (bash)
- **Primary Backend**: Python & FastAPI (or your preferred stack)
- **Package Management**: Standard `venv`, `poetry`, `pip`
- **Database & ORM**: PostgreSQL, SQLAlchemy 2.0 (async sessions), Alembic
- **Testing & Quality**: `pytest` (`pytest-asyncio`, `httpx`), `ruff`, `mypy`

## Multi-Environment Mapping
1. **Work Environment**:
   - VCS: Self-hosted GitLab / GitHub Enterprise
   - Issue Tracker: Jira / YouTrack / GitHub Issues
   - Commit Format: `feat(TASK-ID): description`
   - Git Push: Requires explicit confirmation before executing.
2. **Personal Environment**:
   - VCS: Personal GitHub
   - Scope: Open-source, personal tools, and memory repository
   - Git Push: Allowed automatically to designated memory repo.

## Active Projects & Workspaces
- `path/to/project_a`: Main project description.
- `path/to/project_b`: Secondary project description.

## Key Architectural Decisions (ADR)
- **Layered Separation**: `routes/` (HTTP transport) -> `internal/` (Business domain) -> `models/` & `schemas/`.
- **Git-Based Typed Memory**: Structured knowledge stored in `memory/knowledge/` (facts, decisions, patterns, errors).
- **Session Journaling**: Agent autonomously records session logs to personal memory repository.
