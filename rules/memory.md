# Autonomous Memory & Session Logging Guidelines

To maintain persistent context across sessions, reduce repetitive token consumption, and preserve critical decisions, the agent must autonomously maintain structured memory in `memory/`.

---

## 1. Architecture: Git-Based Typed Memory

Memory is split into three tiers based on access frequency and lifecycle:

```text
memory/
├── context.md               # Tier 1: Concise developer profile & stack rules (< 150 lines)
├── knowledge/               # Tier 2: Typed structured knowledge (Git-tracked JSONL)
│   ├── facts.jsonl          # Environmental facts & tool constraints
│   ├── decisions.jsonl      # Architectural Decisions (ADR: question, decision, reasoning)
│   ├── patterns.jsonl       # Codebase conventions & verified workflows
│   └── errors.jsonl         # Solved tricky errors and verified resolutions
├── sessions/                # Tier 3: Human-readable narrative session journals (Markdown)
│   └── YYYY-MM-DD-<slug>.md
└── index/                   # Local derived search cache (Git-ignored)
    └── memory.db            # SQLite FTS5 (BM25) full-text index
```

---

## 2. Autonomous Ingestion & Recall

The agent autonomously manages the memory lifecycle:

### A. Automatic Recall on Session Start
Via Antigravity's `PreInvocation` hook ([`scripts/memory_recall.py`](file:///D:/uriit/agy-conf/scripts/memory_recall.py)), on turn 1 of every session:
- Top architectural decisions and verified facts are injected into the agent's context as an ephemeral system message.
- Zero token overhead on subsequent turns (`injectSteps: []`).

### B. Fast Local Search
When investigating past choices, the agent or developer searches memory without LLM API overhead:
```powershell
python scripts/memory_index.py search "<keywords>"
```

### C. Autonomous Session Ingestion
When concluding a milestone or session:
1. Run `python scripts/record_session.py "<topic>" "<objective>" "<reasoning>" [files...]`.
2. The script writes the Markdown log, extracts typed knowledge into `knowledge/*.jsonl`, and rebuilds the SQLite FTS5 index.

---

## 3. Remote Sync & Dedicated Memory Repository
- The target repository URL is defined by `AGENT_MEMORY_REPO_URL` (e.g. `https://github.com/cwerti/agent-memory.git`).
- The local clone path is resolved via `AGENT_MEMORY_PATH` (defaults to sibling `../agent-memory`).
- `record_session.py` commits and pushes directly to `agent-memory`, keeping `agy-conf` clean and generic.
- Git push is automatically permitted to the personal memory repository and personal GitHub repos.
- Corporate repositories (GitLab) must **never** receive automatic memory pushes.
