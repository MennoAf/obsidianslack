#!/bin/bash
#
# Sync script to pull brain dump notes from GitHub to local Obsidian vault
#
# Usage:
#   1. Make executable: chmod +x sync_from_github.sh
#   2. Edit paths below to match your setup
#   3. Run manually: ./sync_from_github.sh
#   4. Or automate with cron (see instructions in OBSIDIAN_SYNC_SOLUTIONS.md)
#

# ============================================================================
# CONFIGURATION - UPDATE THESE PATHS
# ============================================================================

# Path to your Obsidian vault's 40_Claude folder
VAULT_PATH="/Users/jasonbauman/Documents/Londo_/40_Claude"

# GitHub repository (format: username/repo-name)
GITHUB_REPO="MennoAf/obsidian-brain-dumps"

# Branch name
GITHUB_BRANCH="main"

# Log file location
LOG_FILE="$VAULT_PATH/sync.log"

# ============================================================================
# SCRIPT - DO NOT EDIT BELOW THIS LINE
# ============================================================================

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if vault path exists
if [ ! -d "$VAULT_PATH" ]; then
    log "ERROR: Vault path does not exist: $VAULT_PATH"
    exit 1
fi

# Navigate to vault
cd "$VAULT_PATH" || exit 1

# Check if this is a git repository
if [ ! -d ".git" ]; then
    log "Initializing git repository..."
    git init
    git remote add origin "https://github.com/$GITHUB_REPO.git"
    git fetch origin
    git checkout -b "$GITHUB_BRANCH" "origin/$GITHUB_BRANCH"
    log "Git repository initialized"
fi

# Pull latest changes
log "Starting sync..."

# Stash any local changes (shouldn't be any, but just in case)
git stash --include-untracked > /dev/null 2>&1

# Pull from remote
if git pull origin "$GITHUB_BRANCH" >> "$LOG_FILE" 2>&1; then
    log "✓ Sync successful"
    
    # Count new files
    NEW_FILES=$(git diff HEAD@{1} --name-only --diff-filter=A | wc -l)
    if [ "$NEW_FILES" -gt 0 ]; then
        log "  → $NEW_FILES new notes synced"
    fi
else
    log "✗ Sync failed - check log for details"
    exit 1
fi

# Clean up
git stash pop > /dev/null 2>&1

exit 0
