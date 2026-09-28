# Security & Permissions Rules

## Secrets & Credentials Protection
- Never hardcode API keys, passwords, database credentials, tokens, or private certificates into code or config files.
- Store sensitive configuration in `.env` files or system environment variables. Ensure `.env` is listed in `.gitignore`.
- Provide `.env.example` with dummy values for documentation.
- Never output the full contents of files containing secrets (e.g., `.env`, credentials JSON) into public chat logs or commit history.

## Command Execution Safety
- Prohibited commands:
  - Destructive recursive deletion of system/root drives (`rm -rf /`, `del /s C:\`).
  - Disk formatting, block writes (`mkfs`, `format`, `dd`).
  - Unverified remote script execution (`curl ... | bash`, `iwr ... | iex`).
  - System shutdown/reboot commands.
- Commands requiring confirmation:
  - Global package installations (`npm i -g`, `pip install --user`).
  - Destructive database migrations or container deletions.
  - Pushing changes to remote git branches.
- Safe commands (safe to run without asking):
  - Read-only inspections (`git status`, `git log`, `ls`, `dir`, `cat`, `view_file`).
  - Version checks (`node -v`, `python --version`, `cargo --version`).
  - Linting and localized automated test suites (`npm test`, `pytest`).
