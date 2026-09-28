# General Agent Guidelines

## Interaction Style
- Be direct, concise, and focused on working solutions.
- Provide actionable code and explanations without superfluous conversational padding.
- Always explain the "why" behind non-obvious architecture or configuration decisions.
- When requirements are underspecified or high-risk, ask clarifying questions before making destructive changes.

## Verification & Integrity
- Always verify changes after editing files (run tests, type checks, or linters).
- Maintain existing codebase style, naming conventions, and file structures.
- Preserve existing comments, docstrings, and licensing headers unless explicitly instructed otherwise.
- Never guess or fabricate API signatures or environment variables; inspect source code or docs first.
