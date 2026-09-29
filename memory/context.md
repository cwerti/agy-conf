# Persistent Agent Memory & Context

This file serves as the long-term memory for AI agents across sessions, reducing token consumption and preventing repetitive questions.

## Developer Profile & Stack
- **OS**: Windows (PowerShell / `pwsh`)
- **Primary Backend**: Python & FastAPI
- **Package Management**: Standard `venv`, `poetry`, `pip` (strictly **no `uv`**)
- **Database & ORM**: PostgreSQL, SQLAlchemy 2.0 (async sessions), Alembic
- **Testing & Quality**: `pytest` (`pytest-asyncio`, `httpx`), `ruff`, `mypy`

## Multi-Environment Mapping
1. **Work Environment**:
   - VCS: Self-hosted corporate GitLab (`GITLAB_URL`, `GITLAB_TOKEN`)
   - Issue Tracker: JetBrains YouTrack (`YOUTRACK_BASE_URL`, `YOUTRACK_PERMANENT_TOKEN`)
   - Commit Format: `feat(TASK-ID): description`
   - Git Push: Requires explicit confirmation before executing.
2. **Personal Environment**:
   - VCS: Personal GitHub
   - Scope: Open-source, personal tools, and this configuration repository (`agy-conf`)
   - Git Push: **Allowed automatically** to personal GitHub.

## Active Projects & Workspaces
- `D:\uriit\agy-conf`: Universal Agent Configuration, Memory, Rules & MCP Repository.
- `D:\uriit\culture_backend`: Production Backend Service (FastAPI, Poetry, PoeThePoet, PostgreSQL, Redis, RabbitMQ, Centrifugo).

## Key Architectural Decisions (ADR)
- **Reference Architecture (from culture_backend)**:
  - Clean Layered Separation: `routes/` (HTTP transport, HTTPException) ➔ `internal/` (Business logic, pure domain, no HTTP imports) ➔ `models/` & `schemas/`.
  - Self-contained migrations: `migrations/versions/` must never import from `app.models`.
  - Task runner: `poetry run poe (lint|format|isort|code-check|migrations-check)`.
  - Linting: `ruff.toml` with `line-length = 120`.
- **Windows UTF-8**: Always enforce `encoding="utf-8"` in Python file operations.
- **Async Safety**: Never perform blocking I/O in `async def` FastAPI path operations.
- **Git-Based Typed Memory**: Structured knowledge stored in `memory/knowledge/` (facts, decisions, patterns, errors), indexed via SQLite FTS5 (`scripts/memory_index.py`), and recalled autonomously at session start via PreInvocation hook (`scripts/memory_recall.py`).
- **Session Journaling**: Agent autonomously writes session logs to `memory/sessions/` and synchronizes them to personal GitHub.

