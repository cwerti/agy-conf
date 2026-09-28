# Multi-Environment Guidelines (Work GitLab & YouTrack vs Personal GitHub)

This configuration repository supports both professional work projects and personal open-source/private projects.

## 1. Environment Separation
- **Work Environment**:
  - VCS: Self-hosted GitLab (`https://gitlab.yourcompany.com`).
  - Issue Tracker: JetBrains YouTrack (Issue keys: e.g. `PROJ-123`).
  - Git Author: Ensure corporate email is configured in work repositories (`git config user.email "work@company.com"`).
  - Commits: Reference YouTrack tasks in Conventional Commits:
    - Example: `feat(AUTH-42): add oauth2 token refresh endpoint`
    - Example: `fix(BILLING-108): resolve race condition in invoice payment`
- **Personal Environment**:
  - VCS: Personal GitHub (`https://github.com/username`).
  - Git Author: Use personal GitHub email (`git config user.email "personal@example.com"`).
  - Open source etiquette: Never mention internal corporate URLs, internal hostnames, or internal YouTrack ticket IDs in public commits.

## 2. Preventing Git Configuration Leaks
To automate separation across projects, configure conditional includes in your global `~/.gitconfig`:
```ini
# ~/.gitconfig
[includeIf "gitdir:D:/work/"]
    path = ~/.gitconfig-work

[includeIf "gitdir:D:/personal/"]
    path = ~/.gitconfig-personal
```
- In `~/.gitconfig-work`: set your corporate email and GPG key.
- In `~/.gitconfig-personal`: set your personal GitHub email.

## 3. Tool & Issue Tracker Integrations
- When working on YouTrack tasks:
  - Verify issue requirements and acceptance criteria before writing code.
  - Prefix branch names with the issue ID (e.g. `feature/PROJ-123-description` or `fix/PROJ-123-bug`).
- When creating Merge Requests on Self-hosted GitLab:
  - Include summary of changes, linked YouTrack issue URL, and test results.
