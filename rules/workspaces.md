# Multi-Environment Guidelines (Work GitLab & YouTrack vs Personal GitHub)

This framework operates across two distinct repository layers and two execution environments (Work vs Personal).

---

## 1. Dual-Repository Architecture

To allow the configuration framework to be open-source and shared among other developers while keeping personal context and corporate project data private, configurations and memory are strictly separated into two repositories:

| Repository | Purpose | Visibility | Contents |
| :--- | :--- | :--- | :--- |
| **`cwerti/agy-conf`** | **Universal Agent Framework** | Public / Shared | Rules, skills, MCP definitions, subagent blueprints, security hooks, installation scripts. |
| **`cwerti/agent-memory`** | **Personal Agent Memory** | Private | Developer profile (`context.md`), typed knowledge (`facts`, `decisions`, `patterns`), session logs (`sessions/`), local overrides. |

### Local Resolution Contract:
- `agy-conf` contains only templates (`memory/context.example.md`, `memory/README.md`) and is kept clean of user session logs.
- Memory scripts (`record_session.py`, `memory_index.py`, `memory_recall.py`) automatically detect the personal memory repository via:
  1. `AGENT_MEMORY_PATH` (configured in `.env`).
  2. Sibling directory `../agent-memory`.
  3. `~/.gemini/agent-memory`.
  4. Local fallback: `memory/` (git-ignored for personal data).
- Session recordings and memory pushes target `agent-memory.git` directly, never polluting `agy-conf`.

---

## 2. Environment Separation (Work vs Personal)

### Work Environment:
- **VCS**: Self-hosted corporate GitLab (`https://gitlab.uriit.ru`).
- **Issue Tracker**: JetBrains YouTrack (`https://youtrack.uriit.ru`, issue keys: e.g. `CULT-123`).
- **Git Author**: Ensure corporate email is configured in work repositories (`git config user.email "work@uriit.ru"`).
- **Commits**: Reference YouTrack tasks in Conventional Commits:
  - Example: `feat(CULT-42): add centrifugo websocket authentication endpoint`
  - Example: `fix(REG-108): resolve race condition in invoice payment`
- **Git Push**: **Requires explicit confirmation** before executing. Never auto-push to corporate GitLab.

### Personal Environment:
- **VCS**: Personal GitHub (`https://github.com/cwerti`).
- **Scope**: Open-source repositories (`agy-conf`), personal projects, and personal memory repository (`agent-memory`).
- **Git Author**: Use personal GitHub email (`git config user.email "cwerti@example.com"`).
- **Open Source Etiquette**: Never mention internal corporate URLs, internal hostnames, or internal YouTrack ticket IDs in public commits to `agy-conf`.
- **Git Push**: **Allowed automatically** to personal GitHub (`github.com/cwerti/*`).

---

## 3. Preventing Git Configuration Leaks
To automate author identity separation across projects, configure conditional includes in your global `~/.gitconfig`:
```ini
# ~/.gitconfig
[includeIf "gitdir:D:/uriit/"]
    path = ~/.gitconfig-work

[includeIf "gitdir:D:/personal/"]
    path = ~/.gitconfig-personal
```
- In `~/.gitconfig-work`: set corporate email and signing key.
- In `~/.gitconfig-personal`: set personal GitHub email and credentials.
