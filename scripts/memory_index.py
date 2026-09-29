#!/usr/bin/env python3
"""
Git-Based Agent Memory: Indexing, Search, and Knowledge Extraction.

Implements a lightweight, zero-dependency (stdlib + sqlite3) memory system:
- Typed knowledge store (facts, decisions, patterns, errors) in JSONL
- SQLite FTS5 full-text index with BM25 ranking
- Deterministic extraction from session Markdown files
- CLI for build/search/extract operations

Based on insights from:
- "Why Git Is the Memory Solution for the ADLC" (arXiv:2607.14390)
- "GitOfThoughts" (arXiv:2606.14470)
- "CommitDistill" (arXiv:2605.18284)
"""

import sys
import os
import json
import re
import sqlite3
import hashlib
import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env"


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


def resolve_memory_dir() -> Path:
    """
    Resolve the active memory directory.
    Priority:
    1. AGENT_MEMORY_PATH environment variable (if exists)
    2. Sibling directory 'agent-memory' (e.g. D:/uriit/agent-memory)
    3. User home ~/.gemini/agent-memory (if exists)
    4. Fallback: local memory/ inside agy-conf repo
    """
    env_p = os.environ.get("AGENT_MEMORY_PATH")
    if env_p and Path(env_p).exists():
        return Path(env_p).resolve()

    sibling = REPO_ROOT.parent / "agent-memory"
    if sibling.exists() and (sibling / "context.md").exists():
        return sibling.resolve()

    home_mem = Path.home() / ".gemini" / "agent-memory"
    if home_mem.exists() and (home_mem / "context.md").exists():
        return home_mem.resolve()

    return (REPO_ROOT / "memory").resolve()


def get_memory_paths():
    mdir = resolve_memory_dir()
    return {
        "memory_dir": mdir,
        "knowledge_dir": mdir / "knowledge",
        "sessions_dir": mdir / "sessions",
        "index_dir": mdir / "index",
        "db_path": mdir / "index" / "memory.db",
        "context_file": mdir / "context.md",
    }


KNOWLEDGE_TYPES = ("facts", "decisions", "patterns", "errors")


def ensure_dirs():
    paths = get_memory_paths()
    paths["knowledge_dir"].mkdir(parents=True, exist_ok=True)
    paths["index_dir"].mkdir(parents=True, exist_ok=True)
    for kt in KNOWLEDGE_TYPES:
        fp = paths["knowledge_dir"] / f"{kt}.jsonl"
        if not fp.exists():
            fp.touch()


def _connect_db() -> sqlite3.Connection:
    ensure_dirs()
    db_path = get_memory_paths()["db_path"]
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
            id, type, text, tags, source, created,
            tokenize='unicode61'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory_meta (
            id TEXT PRIMARY KEY,
            type TEXT,
            text TEXT,
            tags TEXT,
            source TEXT,
            created TEXT,
            raw_json TEXT
        )
    """)
    return conn


# ---------------------------------------------------------------------------
# Knowledge JSONL I/O
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Knowledge JSONL I/O
# ---------------------------------------------------------------------------

def load_knowledge(ktype: str) -> list[dict]:
    fp = get_memory_paths()["knowledge_dir"] / f"{ktype}.jsonl"
    if not fp.exists():
        return []
    entries = []
    with open(fp, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def append_knowledge(ktype: str, entry: dict) -> str:
    ensure_dirs()
    fp = get_memory_paths()["knowledge_dir"] / f"{ktype}.jsonl"
    if "id" not in entry:
        prefix = ktype[0]
        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        entry["id"] = f"{prefix}{ts}_{hashlib.md5(entry.get('text', '').encode()).hexdigest()[:6]}"
    if "type" not in entry:
        entry["type"] = ktype.rstrip("s")  # facts -> fact
    if "created" not in entry:
        entry["created"] = datetime.date.today().isoformat()
    with open(fp, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry["id"]


# ---------------------------------------------------------------------------
# Extraction: Session MD -> Typed Knowledge
# ---------------------------------------------------------------------------

def extract_knowledge_from_session(session_path: Path) -> list[dict]:
    """Extract facts, decisions, and patterns from a session Markdown file."""
    text = session_path.read_text(encoding="utf-8")
    extracted = []
    source = f"session/{session_path.stem}"
    date_match = re.search(r"\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})", text)
    created = date_match.group(1) if date_match else datetime.date.today().isoformat()

    # Extract reasoning/decisions section
    reasoning_match = re.search(
        r"##\s*Reasoning\s*[&\s]*Decisions?\s*\n(.*?)(?=\n##|\Z)",
        text, re.DOTALL | re.IGNORECASE
    )
    if reasoning_match:
        reasoning_text = reasoning_match.group(1).strip()
        # Each numbered or bulleted item is a potential decision or fact
        items = re.findall(r"[-*\d.]+\s*\*\*([^*]+)\*\*[:\s]*(.*?)(?=\n[-*\d.]|\Z)", reasoning_text, re.DOTALL)
        for title, body in items:
            body = body.strip()
            if any(kw in body.lower() for kw in ["выбр", "решил", "потому что", "вместо", "chose", "decided", "because", "instead"]):
                extracted.append({
                    "type": "decision",
                    "question": title.strip(),
                    "decision": body[:500],
                    "source": source,
                    "created": created,
                    "tags": _auto_tags(title + " " + body)
                })
            else:
                extracted.append({
                    "type": "fact",
                    "text": f"{title.strip()}: {body[:300]}",
                    "source": source,
                    "created": created,
                    "tags": _auto_tags(title + " " + body)
                })

    # Extract file changes as patterns
    changes_match = re.search(
        r"##\s*(Files?\s*Changed|Changes?\s*Made)\s*\n(.*?)(?=\n##|\Z)",
        text, re.DOTALL | re.IGNORECASE
    )
    if changes_match:
        files = re.findall(r"`([^`]+)`", changes_match.group(2))
        if files:
            extracted.append({
                "type": "pattern",
                "text": f"Session '{session_path.stem}' modified: {', '.join(files[:15])}",
                "source": source,
                "created": created,
                "tags": ["files-changed"]
            })

    return extracted


def _auto_tags(text: str) -> list[str]:
    """Generate simple keyword tags from text."""
    tag_keywords = {
        "python": ["python", "pip", "poetry", "pytest", "pydantic", "fastapi"],
        "database": ["postgres", "sqlalchemy", "alembic", "migration", "database", "sql"],
        "git": ["git", "commit", "branch", "push", "merge"],
        "docker": ["docker", "container", "compose"],
        "security": ["security", "token", "secret", "permission"],
        "mcp": ["mcp", "server", "model context protocol"],
        "config": ["config", "env", "setting", "install"],
        "testing": ["test", "pytest", "coverage"],
    }
    text_lower = text.lower()
    tags = []
    for tag, keywords in tag_keywords.items():
        if any(kw in text_lower for kw in keywords):
            tags.append(tag)
    return tags or ["general"]


# ---------------------------------------------------------------------------
# FTS5 Index Build & Search
# ---------------------------------------------------------------------------

def build_index():
    """Rebuild the FTS5 index from all memory sources."""
    conn = _connect_db()
    conn.execute("DELETE FROM memory_fts")
    conn.execute("DELETE FROM memory_meta")
    count = 0
    paths = get_memory_paths()

    # 1. Index knowledge JSONL files
    for ktype in KNOWLEDGE_TYPES:
        for entry in load_knowledge(ktype):
            _index_entry(conn, entry)
            count += 1

    # 2. Index session Markdown files
    sessions_dir = paths["sessions_dir"]
    if sessions_dir.exists():
        for md_file in sorted(sessions_dir.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            entry = {
                "id": f"session_{md_file.stem}",
                "type": "session",
                "text": text[:2000],
                "tags": _auto_tags(text),
                "source": f"sessions/{md_file.name}",
                "created": md_file.stem[:10] if re.match(r"\d{4}-\d{2}-\d{2}", md_file.stem) else ""
            }
            _index_entry(conn, entry)
            count += 1

    # 3. Index context.md
    context_file = paths["context_file"]
    if context_file.exists():
        ctx_text = context_file.read_text(encoding="utf-8")
        entry = {
            "id": "global_context",
            "type": "context",
            "text": ctx_text[:3000],
            "tags": ["context", "global"],
            "source": "context.md",
            "created": ""
        }
        _index_entry(conn, entry)
        count += 1

    conn.commit()
    conn.close()
    return count


def _index_entry(conn: sqlite3.Connection, entry: dict):
    eid = entry.get("id", "")
    etype = entry.get("type", "")
    parts = [
        entry.get("text", ""),
        entry.get("question", ""),
        entry.get("decision", ""),
        entry.get("reasoning", "")
    ]
    text = " \n ".join(p for p in parts if p).strip()
    tags = ",".join(entry.get("tags", []))
    source = entry.get("source", "")
    created = entry.get("created", "")

    conn.execute(
        "INSERT OR REPLACE INTO memory_meta (id, type, text, tags, source, created, raw_json) VALUES (?,?,?,?,?,?,?)",
        (eid, etype, text, tags, source, created, json.dumps(entry, ensure_ascii=False))
    )
    conn.execute(
        "INSERT INTO memory_fts (id, type, text, tags, source, created) VALUES (?,?,?,?,?,?)",
        (eid, etype, text, tags, source, created)
    )


def search_memory(query: str, top_k: int = 5) -> list[dict]:
    """BM25 search over indexed memory. Returns ranked results with LIKE fallback."""
    paths = get_memory_paths()
    if not paths["db_path"].exists():
        build_index()

    words = [re.sub(r"[^\w]", "", w) for w in query.strip().split()]
    words = [w for w in words if w]
    if not words:
        return []

    # Safe FTS5 tokens
    fts_tokens = [f"{w}*" for w in words]
    fts_query = " OR ".join(fts_tokens)

    conn = _connect_db()
    rows = []
    try:
        rows = conn.execute("""
            SELECT id, type, text, tags, source, created, 
                   rank AS score
            FROM memory_fts
            WHERE memory_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (fts_query, top_k)).fetchall()
    except Exception:
        rows = []

    # If FTS returns no rows or errored, fallback to LIKE search over memory_meta
    if not rows:
        like_clauses = " OR ".join(["text LIKE ? OR tags LIKE ?"] * len(words))
        like_params = []
        for w in words:
            like_params.extend([f"%{w}%", f"%{w}%"])
        like_params.append(top_k)
        try:
            raw_rows = conn.execute(f"""
                SELECT id, type, text, tags, source, created, 0.0 AS score
                FROM memory_meta
                WHERE {like_clauses}
                LIMIT ?
            """, like_params).fetchall()
            rows = raw_rows
        except Exception:
            rows = []

    conn.close()
    results = []
    for row in rows:
        results.append({
            "id": row[0], "type": row[1], "text": row[2][:300],
            "tags": row[3], "source": row[4], "created": row[5],
            "score": round(row[6], 4)
        })
    return results

    conn.close()
    results = []
    for row in rows:
        results.append({
            "id": row[0], "type": row[1], "text": row[2][:300],
            "tags": row[3], "source": row[4], "created": row[5],
            "score": round(row[6], 4)
        })
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  memory_index.py build              — Rebuild FTS5 index")
        print("  memory_index.py search <query>      — BM25 search")
        print("  memory_index.py extract <session.md> — Extract knowledge from session")
        print("  memory_index.py ingest <session.md>  — Extract + append + reindex")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "build":
        count = build_index()
        print(json.dumps({"status": "ok", "indexed": count}, indent=2))

    elif cmd == "search":
        query = " ".join(sys.argv[2:])
        if not query:
            print("Error: provide a search query", file=sys.stderr)
            sys.exit(1)
        results = search_memory(query, top_k=5)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif cmd == "extract":
        path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        if not path or not path.exists():
            print("Error: provide a valid session file path", file=sys.stderr)
            sys.exit(1)
        extracted = extract_knowledge_from_session(path)
        print(json.dumps(extracted, indent=2, ensure_ascii=False))

    elif cmd == "ingest":
        path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        if not path or not path.exists():
            print("Error: provide a valid session file path", file=sys.stderr)
            sys.exit(1)
        extracted = extract_knowledge_from_session(path)
        for entry in extracted:
            ktype = entry.get("type", "fact") + "s"
            if ktype not in KNOWLEDGE_TYPES:
                ktype = "facts"
            eid = append_knowledge(ktype, entry)
            print(f"  Added {entry['type']}: {eid}")
        count = build_index()
        print(json.dumps({"status": "ok", "extracted": len(extracted), "indexed": count}, indent=2))

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
