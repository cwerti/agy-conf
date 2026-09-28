#!/usr/bin/env python3
"""
Autonomous Session Logger for AI Coding Agents.
Records reasoning, decisions, and tasks into memory/sessions/
and synchronizes with personal GitHub repository defined by AGENT_MEMORY_REPO_URL.
"""

import sys
import os
import re
import datetime
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_DIR = BASE_DIR / "memory"
SESSIONS_DIR = MEMORY_DIR / "sessions"
ENV_FILE = BASE_DIR / ".env"


def load_env():
    if ENV_FILE.exists():
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, _, v = line.partition("=")
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v
        except Exception:
            pass


load_env()


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def record_session(topic: str, objective: str, reasoning: str, files_changed: list, next_steps: str = "", push: bool = False):
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    slug = slugify(topic)[:40] or "session"
    session_file = SESSIONS_DIR / f"{today}-{slug}.md"

    content = f"""# Session Log: {topic}

- **Date**: {today}
- **Workspace**: `{BASE_DIR}`
- **Objective**: {objective}

## Reasoning & Decisions
{reasoning}

## Files Changed
"""
    for f in files_changed:
        content += f"- `{f}`\n"

    if next_steps:
        content += f"\n## Next Steps\n{next_steps}\n"

    with open(session_file, "w", encoding="utf-8") as fp:
        fp.write(content)

    print(f"Session recorded in: {session_file}")

    memory_repo_url = os.environ.get("AGENT_MEMORY_REPO_URL", "")
    if memory_repo_url:
        print(f"Designated Memory Repository: {memory_repo_url}")

    if push:
        try:
            print("Syncing session documentation to memory repository...")
            subprocess.run(["git", "add", "memory/"], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "commit", "-m", f"docs(memory): log session - {topic}"], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "push"], cwd=BASE_DIR, check=True)
            print("Successfully pushed session log to remote.")
        except Exception as e:
            print(f"Warning: git push skipped or failed: {e}")

    return session_file


def main():
    if len(sys.argv) < 3:
        print("Usage: record_session.py <topic> <objective> [reasoning] [--push] [files...]")
        sys.exit(0)

    topic = sys.argv[1]
    objective = sys.argv[2]
    reasoning = sys.argv[3] if len(sys.argv) > 3 else "Session completed."

    push = False
    files = []
    for arg in sys.argv[4:]:
        if arg == "--push":
            push = True
        else:
            files.append(arg)

    record_session(topic, objective, reasoning, files, push=push)


if __name__ == "__main__":
    main()
