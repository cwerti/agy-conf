#!/usr/bin/env bash
# Universal Agent Configuration Installer & Environment Setup (Linux & macOS)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
USER_HOME="${HOME:-~}"
GEMINI_GLOBAL_CONFIG="${USER_HOME}/.gemini/config"
PROJECT_DIR="${1:-}"
ENV_EXAMPLE="${REPO_ROOT}/.env.example"
ENV_FILE="${REPO_ROOT}/.env"

echo "=========================================================="
echo " Agent Config Installer & Environment Setup (Universal)   "
echo "=========================================================="
echo "Repository root: ${REPO_ROOT}"

# 0. Interactive .env setup
if [ -f "$ENV_EXAMPLE" ] && [ ! -f "$ENV_FILE" ]; then
    echo -e "\n[0/4] Initializing .env configuration from .env.example..."
    echo "Press [Enter] to keep the default/example value or enter your value."
    echo -e "Leave empty if not using a specific service.\n"

    touch "$ENV_FILE"
    while IFS= read -r line || [ -n "$line" ]; do
        trimmed="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        if [[ -z "$trimmed" || "$trimmed" =~ ^# ]]; then
            echo "$line" >> "$ENV_FILE"
            if [[ "$trimmed" =~ ^# && ! "$trimmed" =~ ^#\ = && ! "$trimmed" =~ ^#\ - ]]; then
                echo "  $trimmed"
            fi
            continue
        fi

        if [[ "$trimmed" == *"="* ]]; then
            key="${trimmed%%=*}"
            default_val="${trimmed#*=}"

            read -rp "  -> Enter value for ${key} [${default_val}]: " user_val
            final_val="${user_val:-$default_val}"
            echo "${key}=${final_val}" >> "$ENV_FILE"
        fi
    done < "$ENV_EXAMPLE"
    echo -e "\n  [SUCCESS] Created .env configuration file."
elif [ -f "$ENV_FILE" ]; then
    echo -e "\n[0/4] .env file already exists. (Skipping interactive prompt)."
fi

safe_link_or_copy() {
    local src="$1"
    local dest="$2"
    local dest_dir
    dest_dir="$(dirname "$dest")"
    mkdir -p "$dest_dir"

    if [ -e "$dest" ] || [ -L "$dest" ]; then
        echo "  [SKIP] Destination exists: $dest (remove manually to update)"
        return
    fi

    ln -s "$src" "$dest" && echo "  [LINK] Created symlink: $dest -> $src" || {
        cp -R "$src" "$dest" && echo "  [COPY] Copied: $dest"
    }
}

# 1. Global Setup
echo -e "\n[1/4] Setting up Global AGY Configuration..."
mkdir -p "$GEMINI_GLOBAL_CONFIG"
safe_link_or_copy "${REPO_ROOT}/mcp/mcp_config.json" "${GEMINI_GLOBAL_CONFIG}/mcp_config.json"

# 2. Project Setup
if [ -n "$PROJECT_DIR" ]; then
    echo -e "\n[2/4] Setting up Project Workspace: ${PROJECT_DIR}..."
    if [ ! -d "$PROJECT_DIR" ]; then
        echo "  Error: Target directory does not exist: $PROJECT_DIR" >&2
    else
        mkdir -p "${PROJECT_DIR}/.agents/rules"
        mkdir -p "${PROJECT_DIR}/.agents/skills"
        safe_link_or_copy "${REPO_ROOT}/AGENTS.md" "${PROJECT_DIR}/AGENTS.md"
        safe_link_or_copy "${REPO_ROOT}/GEMINI.md" "${PROJECT_DIR}/GEMINI.md"
        safe_link_or_copy "${REPO_ROOT}/security/hooks.json" "${PROJECT_DIR}/.agents/hooks.json"
    fi
else
    echo -e "\n[2/4] Skipping project workspace setup (pass path as arg1 to configure a project)."
fi

# 3. Validation
echo -e "\n[3/4] Validating Environment & Security Policy..."
if command -v python3 >/dev/null 2>&1; then
    python3 "${REPO_ROOT}/security/check_command.py" "git status"
    echo "  Security policy test passed."
else
    echo "  Warning: python3 not found. Ensure python3 is installed."
fi

echo -e "\n[4/4] Installation completed successfully!"
