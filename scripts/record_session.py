#!/usr/bin/env python3
"""
Autonomous Session Logger & Knowledge Ingester for AI Coding Agents.
Records reasoning, decisions, and tasks into memory/sessions/,
autonomously extracts typed knowledge into memory/knowledge/,
rebuilds the SQLite FTS5 index, and synchronizes with personal GitHub repository.
"""

import sys
import os
import re
import datetime
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_DIR = BASE_DIR / "memory"
SESSIONS_DIR = BASE_DIR / "memory" / "sessions"
KNOWLEDGE_DIR = BASE_DIR / "memory" / "knowledge"
ENV_FILE = BASE_DIR / ".env"

# Import memory_index utilities
sys.path.insert(0, str(BASE_DIR / "scripts"))
try:
    from memory_index import (
        extract_knowledge_from_session, append_knowledge, build_index,
        resolve_memory_dir, get_memory_paths, KNOWLEDGE_TYPES
    )
except ImportError:
    extract_knowledge_from_session = None
    append_knowledge = None
    build_index = None
    resolve_memory_dir = lambda: BASE_DIR / "memory"
    get_memory_paths = lambda: {"sessions_dir": BASE_DIR / "memory" / "sessions", "knowledge_dir": BASE_DIR / "memory" / "knowledge"}
    KNOWLEDGE_TYPES = ("facts", "decisions", "patterns", "errors")


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
    mem_dir = resolve_memory_dir()
    sessions_dir = mem_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.date.today().isoformat()
    slug = slugify(topic)[:40] or "session"
    session_file = sessions_dir / f"{today}-{slug}.md"

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

    print(f"Session recorded in: {session_file} (Target Memory Repo: {mem_dir.name})")

    # Autonomous Knowledge Ingestion
    if extract_knowledge_from_session and append_knowledge and build_index:
        try:
            extracted = extract_knowledge_from_session(session_file)
            added_count = 0
            for item in extracted:
                kt = item.get("type", "fact") + "s"
                if kt not in KNOWLEDGE_TYPES:
                    kt = "facts"
                append_knowledge(kt, item)
                added_count += 1
            indexed_total = build_index()
            print(f"Autonomous memory: extracted {added_count} items into knowledge/, indexed {indexed_total} total records.")
        except Exception as e:
            print(f"Warning: autonomous knowledge ingestion failed: {e}", file=sys.stderr)

    memory_repo_url = os.environ.get("AGENT_MEMORY_REPO_URL", "")
    if memory_repo_url:
        print(f"Designated Remote Memory Repository: {memory_repo_url}")

    if push:
        is_git_repo = (mem_dir / ".git").exists()
        git_target = mem_dir if is_git_repo else BASE_DIR
        try:
            print(f"Syncing session documentation to memory repository ({git_target})...")
            if is_git_repo:
                subprocess.run(["git", "add", "sessions/", "knowledge/"], cwd=git_target, check=True)
            else:
                subprocess.run(["git", "add", "memory/sessions/", "memory/knowledge/"], cwd=git_target, check=True)
            subprocess.run(["git", "commit", "-m", f"docs(memory): log session - {topic}"], cwd=git_target, check=True)
            subprocess.run(["git", "push"], cwd=git_target, check=True)
            print("Successfully pushed session log to memory remote.")
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
