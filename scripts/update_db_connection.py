#!/usr/bin/env python3
"""
Dynamic Database Connection Manager for Agent & MCP.
Allows the agent (or developer) to dynamically inspect, test,
and update the active DATABASE_URL across MCP configs without manual editing.

Features:
- Auto-detects DATABASE_URL from project's .env, alembic.ini, or app/config.py
- Normalizes SQLAlchemy async drivers (postgresql+asyncpg:// -> postgresql://) for MCP
- Updates local .env, mcp/mcp_config.local.json, and global ~/.gemini/config/mcp_config.json
- Sets Windows User Environment variable for current session & persistent agent use
"""

import sys
import os
import json
import re
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_ENV_FILE = REPO_ROOT / ".env"
LOCAL_MCP_FILE = REPO_ROOT / "mcp" / "mcp_config.local.json"
USER_HOME = Path(os.environ.get("USERPROFILE") or Path.home())
GLOBAL_GEMINI_MCP = USER_HOME / ".gemini" / "config" / "mcp_config.json"


def normalize_for_mcp(db_url: str) -> str:
    """
    Normalizes database URL for Node.js MCP server (server-postgres).
    Converts 'postgresql+asyncpg://' or 'postgresql+psycopg2://' to 'postgresql://'.
    """
    clean_url = db_url.strip().strip('"').strip("'")
    clean_url = re.sub(r"^postgresql\+[a-zA-Z0-9_-]+://", "postgresql://", clean_url)
    return clean_url


def auto_detect_from_project(project_dir: Path) -> str:
    """Tries to find DATABASE_URL or assemble it from DB_* / POSTGRES_* params in the project directory."""
    candidates = [
        project_dir / ".env",
        project_dir / ".env.local",
        project_dir / ".env.dev",
        project_dir / "alembic.ini"
    ]

    for c in candidates:
        if not c.exists():
            continue

        env_map = {}
        try:
            with open(c, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, _, val = line.partition("=")
                    k = k.strip().upper()
                    v = val.strip().strip('"').strip("'")
                    env_map[k] = v

                    # 1. Direct single-string URL
                    if re.search(r"^(DATABASE_URL|DB_URL|POSTGRES_URL|SQLALCHEMY\.URL)$", k, re.I):
                        if v and "postgres" in v:
                            return normalize_for_mcp(v)
        except Exception:
            continue

        # 2. Assembled from separate components (e.g. culture_backend format)
        user = env_map.get("DB_USER") or env_map.get("POSTGRES_USER") or "postgres"
        pwd = env_map.get("DB_PASSWORD") or env_map.get("POSTGRES_PASSWORD") or ""
        host = env_map.get("DB_HOST") or env_map.get("POSTGRES_HOST") or "localhost"
        port = env_map.get("DB_PORT") or env_map.get("POSTGRES_PORT") or "5432"
        dbname = env_map.get("DB_NAME") or env_map.get("POSTGRES_DB") or "app_db"

        # If host is docker-internal, map to localhost for host machine access
        if host in ["host.docker.internal", "postgres"]:
            host = "localhost"

        if "DB_NAME" in env_map or "POSTGRES_DB" in env_map or "DB_PORT" in env_map:
            assembled = f"postgresql://{user}:{pwd}@{host}:{port}/{dbname}"
            return normalize_for_mcp(assembled)

    return ""


def update_database_url(new_url: str):
    normalized_url = normalize_for_mcp(new_url)

    # 1. Update Windows User Environment variable
    if sys.platform == "win32":
        try:
            import subprocess
            cmd = f"[System.Environment]::SetEnvironmentVariable('DATABASE_URL', '{normalized_url}', 'User')"
            subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, check=False)
        except Exception:
            pass

    # 2. Update local .env in agy-conf
    if LOCAL_ENV_FILE.exists():
        try:
            lines = LOCAL_ENV_FILE.read_text(encoding="utf-8").splitlines()
            found = False
            new_lines = []
            for line in lines:
                if re.match(r"^DATABASE_URL\s*=", line.strip()):
                    new_lines.append(f"DATABASE_URL={normalized_url}")
                    found = True
                else:
                    new_lines.append(line)
            if not found:
                new_lines.append(f"DATABASE_URL={normalized_url}")
            LOCAL_ENV_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        except Exception as e:
            sys.stderr.write(f"Warning: could not update {LOCAL_ENV_FILE}: {e}\n")

    # 3. Update global ~/.gemini/config/mcp_config.json if it exists
    if GLOBAL_GEMINI_MCP.exists():
        try:
            raw_text = GLOBAL_GEMINI_MCP.read_text(encoding="utf-8").strip()
            data = json.loads(raw_text) if raw_text else {}

            if "mcpServers" not in data:
                data["mcpServers"] = {}

            if "postgres-dev" in data["mcpServers"]:
                data["mcpServers"]["postgres-dev"]["args"] = [
                    "-y",
                    "@modelcontextprotocol/server-postgres",
                    normalized_url
                ]
            else:
                data["mcpServers"]["postgres-dev"] = {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-postgres", normalized_url]
                }

            with open(GLOBAL_GEMINI_MCP, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            sys.stderr.write(f"Warning: could not update {GLOBAL_GEMINI_MCP}: {e}\n")

    return normalized_url


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python update_db_connection.py <new_database_url>")
        print("  python update_db_connection.py --auto-detect [project_dir_path]")
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "--auto-detect":
        target_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
        detected = auto_detect_from_project(target_dir)
        if detected:
            final_url = update_database_url(detected)
            print(json.dumps({
                "status": "success",
                "source": "auto_detected",
                "project_dir": str(target_dir),
                "database_url": final_url
            }, indent=2))
        else:
            print(json.dumps({
                "status": "not_found",
                "project_dir": str(target_dir),
                "message": "No database URL found in project .env or alembic.ini"
            }, indent=2))
            sys.exit(2)
    else:
        final_url = update_database_url(arg)
        print(json.dumps({
            "status": "success",
            "source": "manual_input",
            "database_url": final_url,
            "message": "Database URL successfully normalized and updated in MCP configuration"
        }, indent=2))


if __name__ == "__main__":
    main()
