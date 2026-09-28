# Python & FastAPI Development Guidelines (Culture Backend Architecture)

This guideline is based on the production architecture of `culture_backend`.

## 1. Clean Layered Architecture
- **`app/routes/` (HTTP Interface)**:
  - Responsible ONLY for HTTP transport, request/response validation, query params, and status codes.
  - Catches domain exceptions and converts them to `HTTPException`.
  - Injects business services via `Depends()` or dependency containers.
- **`app/internal/` (Business Logic / Services)**:
  - **CRITICAL**: The service layer must NOT know about HTTP transport (`fastapi`).
  - Never import `fastapi`, `HTTPException`, or `status` inside `app/internal/**`.
  - Raise domain exceptions (e.g. `ItemNotFoundError`, `PermissionDeniedError`, `ValidationError`).
- **`app/models/` (Data Models)**:
  - SQLAlchemy ORM models.
  - Never expose models directly in route returns; always map through Pydantic schemas.
- **`app/schemas/` (Pydantic DTOs)**:
  - Strict separation: `ItemCreate`, `ItemUpdate`, `ItemResponse`, `ItemFilter`.
- **`app/dependencies/` & `di_container.py`**:
  - Centralized dependency injection (`dependency-injector` or FastAPI `Depends`).

## 2. Database & Migrations
- **Self-Contained Migrations**:
  - **CRITICAL**: Migration scripts in `migrations/versions/` MUST be 100% self-contained.
  - **NEVER** import from `app.models` or `app...` inside an Alembic migration. If models change in the future, old migrations will fail!
  - Always declare local table representations or use raw DDL if data migrations are required.
- **SQLAlchemy Async**:
  - Use async engine with pool pre-ping: `create_async_engine(..., pool_pre_ping=True)`.
  - Always prevent N+1 queries using eager loading (`selectinload` / `joinedload`).
  - Never execute `alembic downgrade base` in non-local environments.

## 3. Tooling, Task Runner & Code Style
- **Poetry & PoeThePoet**:
  - Run checks via project tasks:
    - `poetry run poe lint` (Ruff linter for changed files)
    - `poetry run poe format` (Ruff formatting)
    - `poetry run poe isort` (Import sorting)
    - `poetry run poe code-check` (Format + Isort + Lint)
    - `poetry run poe migrations-check` (Consistency of Alembic heads)
- **Ruff & Pyright**:
  - `line-length = 120`.
  - Application code must never import or depend on `tests/`.
- **Async & Non-blocking I/O**:
  - No `time.sleep()`, synchronous `requests`, or synchronous DB calls in `async def`.
  - Use `asyncio.sleep()`, `httpx.AsyncClient`, `aiofiles`, and `asyncpg`.

## 4. Windows Development Specifics
- **File Encodings**: Always explicitly specify `encoding="utf-8"` in `open(...)`.
- **Paths**: Use `pathlib.Path` or `/` forward slashes. Avoid string concatenation with `\`.
- **Virtual Environment**: `.venv\Scripts\Activate.ps1`.
- **PowerShell Commands**: Use PowerShell syntax (`$env:VAR="val"`).

## 5. Dynamic Database & MCP Connection Protocol
- **Auto-Discovery**: When switching to a project workspace, auto-detect `DATABASE_URL` from `.env`, `alembic.ini`, or `app/core/config.py`:
  ```powershell
  python scripts/update_db_connection.py --auto-detect (Get-Location).Path
  ```
- **Connection Failure Recovery**: If database MCP tools fail, ask the user for `DATABASE_URL` and run `scripts/update_db_connection.py "<url>"`. The script automatically strips `+asyncpg` for Node.js MCP compatibility.
