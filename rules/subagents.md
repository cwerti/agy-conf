# Subagent Management & Autonomous Delegation Rules

This rule defines how Antigravity / Gemini coding agents declare, activate, and manage specialized autonomous subagents.

---

## 1. Subagent Lifecycle & Registration Protocol

In Antigravity, custom subagents are session-scoped and defined using the `define_subagent` tool.
Pre-configured subagent blueprints are stored in `subagents/<subagent_name>/subagent.json`.

### Automatic Registration
Whenever the user requests a subagent or the agent determines that a task requires specialized delegation:
1. **Check Availability**: If the subagent is not listed under active subagents, load its blueprint from `subagents/<name>/subagent.json`.
2. **Define Subagent**: Call `define_subagent` passing:
   - `name`: Matches the folder/blueprint name (e.g. `code-reviewer`, `database-architect`, `api-tester`, `debugger`).
   - `role`: Role description.
   - `description`: Scope and triggering conditions.
   - `system_prompt`: Domain-specific prompt from the JSON blueprint.
   - `enable_write_tools`, `enable_mcp_tools`, `enable_subagent_tools`: Boolean flags from the blueprint.
3. **Invoke Delegation**: Call `invoke_subagent` with a specific, actionable `Prompt` and appropriate `Workspace` mode (`inherit`, `branch`, or `share`).

---

## 2. Available Specialized Subagents

| Subagent | Blueprint Path | Capabilities | Typical Use Cases |
| :--- | :--- | :--- | :--- |
| **`code-reviewer`** | [`subagents/code-reviewer/subagent.json`](file:///D:/uriit/agy-conf/subagents/code-reviewer/subagent.json) | Read-only, MCP tools | Pre-commit/PR audit, Pydantic v2 validation, async I/O safety, N+1 query checks. |
| **`database-architect`** | [`subagents/database-architect/subagent.json`](file:///D:/uriit/agy-conf/subagents/database-architect/subagent.json) | Read + Write, MCP tools | Alembic migrations review, `EXPLAIN ANALYZE` plans, index strategy, SQLAlchemy models. |
| **`api-tester`** | [`subagents/api-tester/subagent.json`](file:///D:/uriit/agy-conf/subagents/api-tester/subagent.json) | Read + Write, Test Execution | Async unit & integration tests (`pytest-asyncio`, `httpx.AsyncClient`), edge cases. |
| **`debugger`** | [`subagents/debugger/subagent.json`](file:///D:/uriit/agy-conf/subagents/debugger/subagent.json) | Read + Write, Isolated Workspace | Docker logs investigation, python tracebacks, reproducing flaky or complex bugs. |

---

## 3. Communication & Context Hygiene

- Never flood the user with raw transcripts of subagent conversations.
- Synthesize the subagent's findings into a concise, prioritized executive summary.
- Subagents requiring write tools for dangerous or exploratory code should be spawned with `Workspace="branch"` to keep the main workspace clean.
