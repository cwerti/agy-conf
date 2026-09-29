#!/usr/bin/env python3
"""
Autonomous Memory Recall Hook for Antigravity (PreInvocation).

Implements the AGY PreInvocation hook contract:
- On session start (invocationNum == 1 or first turn), queries SQLite FTS5 memory index.
- Selects top relevant architectural decisions, facts, and stack constraints.
- Injects a compact, high-density ephemeral memory context into the agent's turn.
- Zero-cost for subsequent turns (empty injectSteps).
"""

import sys
import os
import json
from pathlib import Path

if sys.platform == "win32":
    import io
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = REPO_ROOT / "memory"
KNOWLEDGE_DIR = MEMORY_DIR / "knowledge"
INDEX_DIR = MEMORY_DIR / "index"
DB_PATH = INDEX_DIR / "memory.db"

# Lazy import search from memory_index
sys.path.insert(0, str(REPO_ROOT / "scripts"))
try:
    from memory_index import search_memory, build_index
except ImportError:
    search_memory = None
    build_index = None


def get_session_start_memories(workspace_name: str = "") -> str:
    """Retrieve top key architectural decisions and active facts."""
    if not DB_PATH.exists() and build_index:
        try:
            build_index()
        except Exception:
            pass

    decisions = []
    facts = []

    # Read latest decisions from decisions.jsonl
    decisions_file = KNOWLEDGE_DIR / "decisions.jsonl"
    if decisions_file.exists():
        try:
            lines = decisions_file.read_text(encoding="utf-8").strip().splitlines()
            for l in lines[-4:]:  # Latest 4 decisions
                if l.strip():
                    d = json.loads(l)
                    decisions.append(f"• [{d.get('id', 'ADR')}] {d.get('question', '')} -> {d.get('decision', '')}")
        except Exception:
            pass

    # Read latest facts from facts.jsonl
    facts_file = KNOWLEDGE_DIR / "facts.jsonl"
    if facts_file.exists():
        try:
            lines = facts_file.read_text(encoding="utf-8").strip().splitlines()
            for l in lines[-5:]:  # Latest 5 facts
                if l.strip():
                    f = json.loads(l)
                    text = f.get('text', '')
                    if len(text) > 140:
                        text = text[:137] + "..."
                    facts.append(f"• {text}")
        except Exception:
            pass

    # Workspace-specific recall if workspace given
    ws_matches = []
    if workspace_name and search_memory:
        try:
            hits = search_memory(workspace_name, top_k=2)
            for h in hits:
                if h.get("type") in ("decision", "pattern"):
                    snippet = h.get("text", "")[:120]
                    ws_matches.append(f"• ({h.get('type')}) {snippet}")
        except Exception:
            pass

    blocks = ["[Autonomous Agent Memory Recall]"]
    if decisions:
        blocks.append("Active Architectural Decisions (ADR):")
        blocks.extend(decisions)
    if facts:
        blocks.append("\nKey Verified Facts & Stack Constraints:")
        blocks.extend(facts)
    if ws_matches:
        blocks.append(f"\nContext for '{workspace_name}':")
        blocks.extend(ws_matches)

    return "\n".join(blocks)


def main():
    invocation_num = 1
    workspace_paths = []

    try:
        raw_input = sys.stdin.read()
        if raw_input.strip():
            payload = json.loads(raw_input)
            invocation_num = payload.get("invocationNum", 1)
            workspace_paths = payload.get("workspacePaths", [])
    except Exception:
        pass

    # Only inject on invocation 1 to keep token overhead minimal
    if invocation_num <= 1:
        ws_name = Path(workspace_paths[0]).name if workspace_paths else Path.cwd().name
        memory_text = get_session_start_memories(ws_name)
        result = {
            "injectSteps": [
                {
                    "ephemeralMessage": memory_text
                }
            ]
        }
    else:
        result = {
            "injectSteps": []
        }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
