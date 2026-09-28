---
name: add-customization
description: Interactively add or update rules, skills, MCP servers, or command security policies in this configuration repository.
---

# Add Customization Workflow

Use this skill whenever the user wants to add, modify, or extend any part of their agent configuration repository (`agy-conf`), including:
1. New modular rule (`rules/`)
2. New agent skill (`skills/`)
3. New MCP server configuration (`mcp/`)
4. New command security policy / permission rule (`security/commands.json`)

---

## Workflow Steps

### Step 1: Clarify Customization Type & Scope
Identify what the user wants to add:
- **Rule**: General guidelines, language/framework rules (e.g. Celery, Redis, SQLAlchemy), or architecture patterns.
- **Skill**: A multi-step procedure (e.g. migration runner, release manager, YouTrack ticket workflow).
- **MCP Server**: Integration with an external tool, service, database, or API.
- **Command Policy**: Adding a command to the allowlist, denylist, or confirmation list.

---

### Step 2: Implementation Guidelines

#### Option A: Adding a Rule (`rules/<name>.md`)
1. Create a dedicated Markdown file in `rules/` (e.g. `rules/celery.md` or `rules/postgresql.md`).
2. Follow the standard rule structure:
   - Clear section headers.
   - Do's and Don'ts code examples.
   - Error prevention guidelines.
3. Update [AGENTS.md](file:///D:/uriit/agy-conf/AGENTS.md) and [GEMINI.md](file:///D:/uriit/agy-conf/GEMINI.md) by adding a link to the new rule under the `Detailed Modular Rules` section.

#### Option B: Adding a Skill (`skills/<skill_name>/SKILL.md`)
1. Determine skill name in kebab-case (e.g. `youtrack-helper`, `alembic-check`).
2. Create folder `skills/<skill_name>/` and file `SKILL.md`.
3. Ensure valid YAML frontmatter at the top:
   ```yaml
   ---
   name: <skill-name>
   description: <Clear, trigger-oriented 1-2 sentence description explaining WHEN to activate this skill>
   ---
   ```
4. Write structured markdown instructions:
   - Purpose and prerequisites.
   - Exact terminal commands and arguments.
   - Verification steps to confirm success.
5. If helper scripts are needed, place them in `skills/<skill_name>/scripts/`.

#### Option C: Adding an MCP Server (`mcp/`)
1. Check if the server requires sensitive API tokens:
   - **No tokens**: Add to `mcp/mcp_config.json`.
   - **Requires tokens**: Add template to `mcp/mcp_config.example.json` and guide the user to place their real key in `mcp/mcp_config.local.json` (which is in `.gitignore`).
2. Avoid hardcoding `uv` if not installed on the system; use `python` or `npx` where applicable.
3. Document usage and environment variables in `mcp/servers.md`.
4. Validate that `mcp/mcp_config.json` remains valid JSON:
   ```powershell
   python -m json.tool mcp/mcp_config.json > $null
   ```

#### Option D: Adding a Command Security Rule (`security/commands.json`)
1. Open `security/commands.json`.
2. Choose appropriate policy list:
   - `denylist`: Dangerous commands that must never run.
   - `require_confirmation`: Commands requiring human review before running.
   - `allowlist`: Safe commands that can run automatically.
3. Add the regex pattern with a clear explanation (`reason` or `description`).
4. **Mandatory Verification**: Test the regex immediately:
   ```powershell
   python security/check_command.py "<sample_command_to_test>"
   ```
   Verify that the output matches expected `{"decision": "allow" | "deny" | "ask"}`.

---

### Step 3: Final Verification & Summary
1. Check repository git status:
   ```powershell
   git status
   ```
2. Verify that all modified JSON files are valid and no syntax errors were introduced.
3. Present a concise summary of the changes to the user without pushing to git.
