#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

COMMIT_MSG="${1:-}"

echo "Syncing agent configuration repository..."

if [ -n "$(git status --porcelain)" ]; then
    echo "Local changes detected:"
    git status -s
    if [ -n "$COMMIT_MSG" ]; then
        echo "Committing changes with message: '$COMMIT_MSG'..."
        git add -A
        git commit -m "$COMMIT_MSG"
    else
        echo "Note: Pass a commit message as arg1 to automatically commit."
    fi
fi

echo "Pulling latest changes from remote..."
git pull --rebase || echo "Warning: git pull failed or remote not configured yet."

bash "${REPO_ROOT}/scripts/install.sh"
