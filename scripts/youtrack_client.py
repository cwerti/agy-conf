#!/usr/bin/env python3
"""
Lightweight JetBrains YouTrack API Client for AI Agents.
Uses standard Python library (no external dependencies required).

Features:
- Fetch issue summary, description, custom fields (State, Priority, Assignee), and comments
- Post comments to YouTrack issues
- Supports reading tokens from environment variables or agy-conf .env
"""

import sys
import os
import json
import re
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
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

YOUTRACK_BASE_URL = os.environ.get("YOUTRACK_BASE_URL", "").strip().rstrip("/")
YOUTRACK_TOKEN = os.environ.get("YOUTRACK_PERMANENT_TOKEN", "").strip()


def check_auth():
    if not YOUTRACK_BASE_URL:
        print(json.dumps({
            "error": "YOUTRACK_BASE_URL is not set. Configure it in .env or system environment."
        }, ensure_ascii=False))
        sys.exit(1)
    if not YOUTRACK_TOKEN:
        print(json.dumps({
            "error": "YOUTRACK_PERMANENT_TOKEN is not set. Configure it in .env or system environment."
        }, ensure_ascii=False))
        sys.exit(1)


def make_request(endpoint: str, method: str = "GET", payload: dict = None):
    check_auth()
    url = f"{YOUTRACK_BASE_URL}/api/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {YOUTRACK_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    data_bytes = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        return {"error": f"HTTP {e.code}: {e.reason}", "details": err_msg}
    except Exception as e:
        return {"error": str(e)}


def get_issue(issue_id: str):
    fields = "id,idReadable,summary,description,customFields(name,value(name,localizedName)),comments(author(name),text,created)"
    data = make_request(f"issues/{issue_id}?fields={fields}")
    if "error" in data:
        return data

    # Format cleanly for agent
    state = "Unknown"
    priority = "Normal"
    for cf in data.get("customFields", []):
        name = cf.get("name", "").lower()
        val = cf.get("value")
        if isinstance(val, dict):
            val_str = val.get("name") or val.get("localizedName") or ""
        elif isinstance(val, list) and val:
            val_str = val[0].get("name", "") if isinstance(val[0], dict) else str(val[0])
        else:
            val_str = str(val or "")

        if "state" in name or "статус" in name:
            state = val_str
        elif "priority" in name or "приоритет" in name:
            priority = val_str

    comments = []
    for c in data.get("comments", [])[-5:]:  # Last 5 comments
        author = c.get("author", {}).get("name", "Unknown")
        text = c.get("text", "")
        comments.append({"author": author, "text": text})

    return {
        "id": data.get("idReadable", issue_id),
        "summary": data.get("summary", ""),
        "state": state,
        "priority": priority,
        "description": data.get("description", ""),
        "recent_comments": comments
    }


def add_comment(issue_id: str, comment_text: str):
    data = make_request(f"issues/{issue_id}/comments", method="POST", payload={"text": comment_text})
    return data


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python youtrack_client.py get <ISSUE-ID>")
        print("  python youtrack_client.py comment <ISSUE-ID> <comment_text>")
        sys.exit(0)

    command = sys.argv[1].lower()
    issue_id = sys.argv[2].strip()

    if command == "get":
        result = get_issue(issue_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif command == "comment":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Missing comment text"}, ensure_ascii=False))
            sys.exit(1)
        comment_text = " ".join(sys.argv[3:])
        result = add_comment(issue_id, comment_text)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
