# Code Quality & Testing Rules

## Code Standards
- Write clean, idiomatic, self-documenting code following language best practices (PEP 8 for Python, ESLint/Prettier for JS/TS, standard gofmt for Go, rustfmt for Rust).
- Add clear type annotations (TypeScript types, Python type hints) where applicable.
- Avoid dead code, unused imports, and unhandled exception suppression (e.g. bare `except: pass`).

## Testing & Verification
- When fixing a bug, write or run a reproducing test case before declaring it solved.
- Keep test commands deterministic and fast. Avoid running end-to-end suites if unit tests suffice.
- Check compiler/linter warnings immediately after code changes and resolve them.
