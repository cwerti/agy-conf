# Autonomous Memory & Session Logging Guidelines

To maintain persistent context across sessions, reduce repetitive token consumption, and preserve critical decisions, the agent must autonomously maintain documentation in `memory/`.

## 1. When to Update Memory
- **End of Significant Tasks**: When completing a feature, refactoring, or setting up configurations.
- **Architectural Decisions (ADR)**: When selecting a library, designing a schema, or establishing a workflow pattern.
- **Troubleshooting & Fixes**: When solving a non-obvious bug or environment issue.

## 2. Memory Structure
- **Global Context (`memory/context.md`)**:
  - Keep this concise (< 150 lines).
  - Update when tools, stack preferences, or active project paths change.
- **Session Logs (`memory/sessions/YYYY-MM-DD-<topic>.md`)**:
  - Format:
    ```markdown
    # Session Log: <Topic>
    - **Date**: YYYY-MM-DD
    - **Workspace**: <Path>
    - **Objective**: <Task Goal>
    
    ## Reasoning & Decisions
    - <Why specific solutions were chosen over alternatives>
    
    ## Changes Made
    - <Key files and additions>
    
    ## Next Steps / Pending
    - <What remains to be done>
    ```

## 3. Personal Memory Repository Variable
- The target repository URL is defined by the environment variable:
  `AGENT_MEMORY_REPO_URL` (configured in system environment variables or local `.env`).
- Git push is automatically permitted to whatever repository matches `AGENT_MEMORY_REPO_URL`.
- Work repositories (GitLab) must NEVER be automatically pushed to.
