# Git & Version Control Guidelines

## Commit Conventions
- Use [Conventional Commits](https://www.conventionalcommits.org/) format:
  - `feat: <short description>`: New feature or capability
  - `fix: <short description>`: Bug fix
  - `refactor: <short description>`: Code restructuring without changing behavior
  - `docs: <short description>`: Documentation updates
  - `test: <short description>`: Adding or updating tests
  - `chore: <short description>`: Maintenance, dependencies, tool configurations
- Keep commit titles under 72 characters, written in imperative present tense.
- Separate logical changes into small, atomic commits rather than one massive commit.

## Branching & Safety
- Never force push (`git push --force` or `-f`) to `main`, `master`, or production branches.
- Do not commit sensitive files: check `.gitignore` before adding untracked files.
- Prefer feature branches (`feat/...`, `fix/...`, `chore/...`) for non-trivial modifications.
- Before committing, always run `git status` and `git diff` to review all staged changes.
