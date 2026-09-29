#!/usr/bin/env python3
"""
Safe MCP Configuration Merger for Antigravity & AI Agents.

Key Safety Principles:
1. NEVER delete or overwrite existing user MCP servers (e.g. custom postgres-dev, docx, GitLab).
2. Create automated timestamped backups before modifying any configuration.
3. Synchronize configurations across both ~/.gemini/config/mcp_config.json and ~/.gemini/settings.json.
4. Expand ${ENV_VAR} placeholders using local .env and system environment variables.
"""

import os
import sys
import json
import shutil
import re
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_ENV_FILE = REPO_ROOT / ".env"
REPO_MCP_FILE = REPO_ROOT / "mcp" / "mcp_config.json"
USER_HOME = Path(os.environ.get("USERPROFILE") or Path.home())
GEMINI_DIR = USER_HOME / ".gemini"
GLOBAL_CONFIG_DIR = GEMINI_DIR / "config"
GLOBAL_MCP_FILE = GLOBAL_CONFIG_DIR / "mcp_config.json"
SETTINGS_FILE = GEMINI_DIR / "settings.json"


def load_env_vars() -> dict:
    """Load key-value pairs from .env and os.environ."""
    env_vars = dict(os.environ)
    if LOCAL_ENV_FILE.exists():
        try:
            with open(LOCAL_ENV_FILE, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, _, v = line.partition("=")
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k:
                        env_vars[k] = v
        except Exception as e:
            print(f"[WARN] Failed to read {LOCAL_ENV_FILE}: {e}", file=sys.stderr)
    return env_vars


def substitute_vars(value, env_vars: dict):
    """Recursively replace ${VAR_NAME} in strings, lists, and dicts."""
    if isinstance(value, str):
        def repl(match):
            var_name = match.group(1)
            val = env_vars.get(var_name)
            if val is not None and val != "":
                return val
            return match.group(0)  # Keep as-is if not found
        return re.sub(r"\$\{([A-Za-z0-9_]+)\}", repl, value)
    elif isinstance(value, list):
        return [substitute_vars(item, env_vars) for item in value]
    elif isinstance(value, dict):
        return {k: substitute_vars(v, env_vars) for k, v in value.items()}
    return value


def backup_file(file_path: Path) -> Path | None:
    """Create a timestamped backup of the target file if it exists."""
    if not file_path.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_name(f"{file_path.name}.bak_{timestamp}")
    shutil.copy2(file_path, backup_path)
    return backup_path


def load_json_safe(file_path: Path) -> dict:
    if not file_path.exists():
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except Exception as e:
        print(f"[WARN] Could not parse {file_path}: {e}", file=sys.stderr)
        return {}


def has_unresolved_placeholders(obj) -> bool:
    if isinstance(obj, str):
        return bool(re.search(r"\$\{[A-Za-z0-9_]+\}", obj))
    elif isinstance(obj, list):
        return any(has_unresolved_placeholders(x) for x in obj)
    elif isinstance(obj, dict):
        return any(has_unresolved_placeholders(v) for v in obj.values())
    return False


OPTIONAL_SERVER_REQUIREMENTS = {
    "gitlab-work": ["GITLAB_TOKEN", "GITLAB_URL"],
    "youtrack": ["YOUTRACK_PERMANENT_TOKEN", "YOUTRACK_BASE_URL"],
    "github-personal": ["GITHUB_TOKEN"],
}


def merge_mcp():
    env_vars = load_env_vars()

    # 1. Read existing configurations
    existing_mcp_config = load_json_safe(GLOBAL_MCP_FILE)
    existing_settings = load_json_safe(SETTINGS_FILE)

    user_servers = {}

    # Extract from existing ~/.gemini/config/mcp_config.json
    if "mcpServers" in existing_mcp_config and isinstance(existing_mcp_config["mcpServers"], dict):
        for srv_name, srv_conf in existing_mcp_config["mcpServers"].items():
            user_servers[srv_name] = srv_conf

    # Extract from ~/.gemini/settings.json
    if "mcpServers" in existing_settings and isinstance(existing_settings["mcpServers"], dict):
        for srv_name, srv_conf in existing_settings["mcpServers"].items():
            if srv_name not in user_servers:
                user_servers[srv_name] = srv_conf

    # 2. Read repo template mcp_config.json
    repo_config = load_json_safe(REPO_MCP_FILE)
    repo_servers = repo_config.get("mcpServers", {})

    merged_servers = dict(user_servers)  # Start with all existing user servers PRESERVED
    preserved_names = list(user_servers.keys())
    added_names = []
    skipped_names = []

    for name, srv_def in repo_servers.items():
        if name in merged_servers:
            skipped_names.append(name)
            continue

        # Optional servers (GitLab, YouTrack, etc.) - only add if credentials exist
        required_keys = OPTIONAL_SERVER_REQUIREMENTS.get(name, [])
        missing_req = False
        for rk in required_keys:
            val = env_vars.get(rk, "").strip()
            if not val or "xxxx" in val or "YOUR_" in val:
                missing_req = True
                break
        if missing_req:
            skipped_names.append(f"{name} (optional service not configured)")
            continue

        expanded_def = substitute_vars(srv_def, env_vars)
        if has_unresolved_placeholders(expanded_def):
            skipped_names.append(f"{name} (unresolved variables)")
            continue

        merged_servers[name] = expanded_def
        added_names.append(name)

    # 3. Create backups before any write
    mcp_bak = backup_file(GLOBAL_MCP_FILE)
    settings_bak = backup_file(SETTINGS_FILE)

    # 4. Write updated ~/.gemini/config/mcp_config.json
    GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    final_global_config = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "mcpServers": merged_servers
    }

    with open(GLOBAL_MCP_FILE, "w", encoding="utf-8") as f:
        json.dump(final_global_config, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 5. Write updated ~/.gemini/settings.json (preserving all existing non-mcp sections)
    if SETTINGS_FILE.exists():
        updated_settings = dict(existing_settings)
        if "mcpServers" not in updated_settings or not isinstance(updated_settings["mcpServers"], dict):
            updated_settings["mcpServers"] = {}
        for k, v in merged_servers.items():
            if k not in updated_settings["mcpServers"]:
                updated_settings["mcpServers"][k] = v

        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_settings, f, indent=2, ensure_ascii=False)
            f.write("\n")

    summary = {
        "status": "success",
        "global_mcp_path": str(GLOBAL_MCP_FILE),
        "settings_path": str(SETTINGS_FILE) if SETTINGS_FILE.exists() else None,
        "backups": {
            "global_mcp": str(mcp_bak) if mcp_bak else None,
            "settings": str(settings_bak) if settings_bak else None
        },
        "preserved_existing_servers": preserved_names,
        "added_new_servers": added_names,
        "total_active_servers": list(merged_servers.keys())
    }

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


if __name__ == "__main__":
    merge_mcp()
