# Session Log: Initial Repository Setup & Customizations

- **Date**: 2026-09-28
- **Workspace**: `D:\uriit\agy-conf`
- **Objective**: Create a universal agent configuration repository (rules, skills, MCP, permissions, memory) tailored for Windows, FastAPI, self-hosted GitLab, YouTrack, and personal GitHub.

## Reasoning & Decisions
1. **Universal Standards**:
   - Used `AGENTS.md` as the master cross-agent entrypoint with pointers for `GEMINI.md` (Antigravity), `CLAUDE.md`, and `.cursorrules`.
   - Used Agent Skills specification (`skills/<name>/SKILL.md`) with frontmatter metadata.
2. **Backend & Stack Constraints**:
   - Explicitly eliminated `uv` dependencies in favor of standard `npx` and `python` tools.
   - Enforced Pydantic v2, async SQLAlchemy 2.0, non-blocking I/O rules in `rules/fastapi.md`.
3. **Windows Environment Protection**:
   - Added UTF-8 enforcement to prevent CP1251 decode crashes.
   - Added `.gitattributes` to keep LF for scripts/markdown/JSON and CRLF for PowerShell.
4. **Command Security Policy**:
   - Enforced hard denial for destructive commands (`rm -rf /`, `del /s C:\`, `format`, `alembic downgrade base`).
   - Allowed automatic `git push` ONLY to personal GitHub (`github.com` or `agy-conf`), while requiring confirmation for corporate GitLab.
5. **Persistent Memory**:
   - Introduced `memory/context.md` and `memory/sessions/` for long-term agent reasoning logs.

## Next Steps
- Connect personal GitHub remote when ready.
- Activate MCP servers by setting environment variables in PowerShell.
