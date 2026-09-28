---
name: session-journal
description: Autonomously record session goals, reasoning, architectural decisions, and sync documentation to personal GitHub repository.
---

# Session Journal & Memory Sync Workflow

Use this skill when completing significant tasks, at the user's request ("зафиксируй сессию", "сохрани в гитхаб"), or when documenting architectural decisions.

## Execution Steps

### 1. Identify Session Insights
Collect:
- **Topic & Objective**: What problem was solved or what feature was built?
- **Key Decisions & Reasoning**: Why was a specific library, pattern, or approach chosen?
- **Modified/Created Files**: List of changed files.
- **Next Steps**: Any pending tasks for future sessions.

### 2. Record Session
Execute the recorder script or write directly to `memory/sessions/YYYY-MM-DD-<slug>.md`:
```powershell
python scripts/record_session.py "<Topic>" "<Objective>" "<Reasoning>" "<Files>"
```

### 3. Update Persistent Context
If global preferences, active projects, or architecture patterns changed, update `memory/context.md`.

### 4. Sync to Personal Memory Repository
The target repository is read from the `AGENT_MEMORY_REPO_URL` variable.
Stage memory files and push (allowed without confirmation when matching `AGENT_MEMORY_REPO_URL`):
```powershell
git add memory/
git commit -m "docs(memory): log session - <Topic>"
git push origin <branch>
```
*(Note: Never push to corporate GitLab automatically; only to the repository matching `AGENT_MEMORY_REPO_URL`).*
