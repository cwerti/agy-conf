---
name: youtrack-helper
description: Fetch issue details, acceptance criteria, and post updates to JetBrains YouTrack using the lightweight youtrack_client.
---

# YouTrack Helper Workflow

Use this skill whenever working on a task referenced by a YouTrack issue ID (e.g. `PROJ-123`, `TASK-42`).

## Execution Steps

### 1. Fetch Task Details
Retrieve the task summary, description, acceptance criteria, and comments:
```powershell
python scripts/youtrack_client.py get <ISSUE-ID>
```

### 2. Prepare Git Feature Branch
Create a branch adhering to team standards:
```powershell
git checkout -b feature/<ISSUE-ID>-<short-description>
```

### 3. Post Progress or Completion Comment (Optional)
When task is implemented, add a comment:
```powershell
python scripts/youtrack_client.py comment <ISSUE-ID> "Implemented in branch feature/<ISSUE-ID>..."
```
