# Universal Agent Memory Mount Point

This directory is the local template and mount point for AI agent memory.

## Dual-Repository Architecture
In this framework, agent memory is deliberately separated into two repositories:

1. **[`agy-conf`](https://github.com/cwerti/agy-conf)** (This repository):
   - Public/shared universal rules, skills, MCP configurations, subagents, and scripts.
   - Clean of personal logs, credentials, or corporate-specific details.

2. **`agent-memory`** (Personal memory repository, e.g. [`cwerti/agent-memory`](https://github.com/cwerti/agent-memory)):
   - Private repository holding your personal profile (`context.md`), typed knowledge (`knowledge/*.jsonl`), and narrative session logs (`sessions/*.md`).
   - Configured via `AGENT_MEMORY_REPO_URL` and `AGENT_MEMORY_PATH` in `.env`.
   - When present (e.g. cloned as sibling `../agent-memory`), all agent memory operations (`record_session.py`, `memory_index.py`, `memory_recall.py`) automatically target your personal memory repository.

## Getting Started for New Users
1. Copy `memory/context.example.md` to your own personal repository or local `memory/context.md`.
2. Set `AGENT_MEMORY_REPO_URL` in `.env` to your private memory repository.
3. Run `python scripts/install.ps1` (or `install.sh`) to initialize.
