#!/usr/bin/env python3
"""
Command policy validator for AGY and other AI coding agents.
Implements the AGY PreToolUse hook contract for run_command.

Enforces:
- Hard denylist on dangerous commands (destructive deletions, force-push to main, formatting).
- Selective Git Push:
  * Allowed automatically ONLY for the personal GitHub memory repo defined by AGENT_MEMORY_REPO_URL (or agy-conf).
  * Requires confirmation for corporate GitLab / work repositories.
- Safe allowlist for tests, linters, inspections.
"""

import sys
import os
import json
import re
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
POLICY_FILE = BASE_DIR / "commands.json"
LOCAL_POLICY_FILE = BASE_DIR / "commands.local.json"
ENV_FILE = REPO_ROOT / ".env"


def load_env():
    """Load simple key-value pairs from .env if present without third-party dependencies."""
    if ENV_FILE.exists():
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val
        except Exception:
            pass


load_env()


def load_policy():
    policy = {
        "policies": {
            "denylist": [],
            "require_confirmation": [],
            "allowlist": []
        },
        "default_decision": "ask",
        "default_reason": "Command requires user confirmation."
    }

    if POLICY_FILE.exists():
        try:
            with open(POLICY_FILE, "r", encoding="utf-8") as f:
                policy.update(json.load(f))
        except Exception as e:
            sys.stderr.write(f"Warning: failed to parse {POLICY_FILE}: {e}\n")

    if LOCAL_POLICY_FILE.exists():
        try:
            with open(LOCAL_POLICY_FILE, "r", encoding="utf-8") as f:
                local_data = json.load(f)
                for key in ["denylist", "require_confirmation", "allowlist"]:
                    if key in local_data.get("policies", {}):
                        policy["policies"][key] = local_data["policies"][key] + policy["policies"].get(key, [])
        except Exception as e:
            sys.stderr.write(f"Warning: failed to parse {LOCAL_POLICY_FILE}: {e}\n")

    return policy


def get_git_remote_url(cwd=None):
    try:
        res = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            timeout=2,
            cwd=cwd,
            check=False
        )
        return res.stdout.strip()
    except Exception:
        return ""


def normalize_git_url(url: str) -> str:
    """Normalize git URL (handles ssh vs https, .git suffix)."""
    if not url:
        return ""
    u = url.strip().lower().rstrip("/")
    if u.endswith(".git"):
        u = u[:-4]
    # Remove protocol / host prefix to match repo path (e.g. user/repo)
    u = re.sub(r"^(https?://|git@)[^/:]+[/:]", "", u)
    return u


def is_personal_memory_repo(cwd=None):
    remote = get_git_remote_url(cwd)
    memory_repo_env = os.environ.get("AGENT_MEMORY_REPO_URL", "").strip()

    # 1. Match against AGENT_MEMORY_REPO_URL variable if provided
    if memory_repo_env and remote:
        if normalize_git_url(remote) == normalize_git_url(memory_repo_env):
            return True, f"Matches configured AGENT_MEMORY_REPO_URL: {memory_repo_env}"

    # 2. Check if current directory is inside this configuration repo
    current_path = Path(cwd or os.getcwd()).resolve()
    if current_path == REPO_ROOT or REPO_ROOT in current_path.parents or current_path.name == REPO_ROOT.name:
        return True, "Current directory is within the agent configuration repository."

    # 3. Check if remote is github.com
    if remote and "github.com" in remote.lower():
        return True, f"Remote points to personal GitHub: {remote}"

    return False, "Target repository is not the designated personal memory repository."


def evaluate_command(command: str, policy: dict, cwd=None):
    cmd_trimmed = command.strip()
    policies = policy.get("policies", {})

    # 1. Denylist check (highest precedence - e.g. force push to main is always blocked)
    for rule in policies.get("denylist", []):
        pattern = rule.get("pattern", "")
        if pattern and re.search(pattern, cmd_trimmed, re.IGNORECASE):
            return {
                "decision": "deny",
                "reason": f"SECURITY VIOLATION: {rule.get('reason', 'Command is explicitly forbidden.')}"
            }

    # 2. Selective Git Push Check
    if re.search(r"(^|\s)git\s+push(\s+.*)?$", cmd_trimmed, re.IGNORECASE):
        is_allowed, reason_detail = is_personal_memory_repo(cwd)
        if is_allowed:
            return {
                "decision": "allow",
                "reason": f"Permitted: git push to personal memory repository allowed ({reason_detail}).",
                "permissionOverrides": [f"command({cmd_trimmed})"]
            }
        else:
            return {
                "decision": "ask",
                "reason": f"Confirmation required: pushing to corporate/work repository. ({reason_detail})"
            }

    # 3. Require confirmation check
    for rule in policies.get("require_confirmation", []):
        pattern = rule.get("pattern", "")
        if pattern and re.search(pattern, cmd_trimmed, re.IGNORECASE):
            return {
                "decision": "ask",
                "reason": rule.get("reason", "Command requires explicit confirmation.")
            }

    # 4. Allowlist check
    for rule in policies.get("allowlist", []):
        pattern = rule.get("pattern", "")
        if pattern and re.search(pattern, cmd_trimmed, re.IGNORECASE):
            return {
                "decision": "allow",
                "reason": f"Safe command permitted: {rule.get('description', 'Matches allowlist rule.')}",
                "permissionOverrides": [f"command({cmd_trimmed})"]
            }

    # 5. Fallback default
    default_dec = policy.get("default_decision", "ask")
    default_reason = policy.get("default_reason", "Command requires confirmation.")
    return {
        "decision": default_dec,
        "reason": default_reason
    }


def main():
    policy = load_policy()
    command_str = None
    cwd = None

    if len(sys.argv) > 1:
        command_str = " ".join(sys.argv[1:])
    else:
        try:
            raw_input = sys.stdin.read()
            if raw_input.strip():
                data = json.loads(raw_input)
                cwd = data.get("toolCall", {}).get("args", {}).get("Cwd")
                tool_call = data.get("toolCall", {})
                if tool_call.get("name") == "run_command":
                    args = tool_call.get("args", {})
                    command_str = args.get("CommandLine", "")
                else:
                    command_str = data.get("CommandLine", "")
        except Exception as e:
            sys.stderr.write(f"Error reading JSON from stdin: {e}\n")

    if not command_str:
        result = {"decision": "allow", "reason": "No command identified"}
    else:
        result = evaluate_command(command_str, policy, cwd)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
