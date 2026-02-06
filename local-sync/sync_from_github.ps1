# Sync script to pull brain dump notes from GitHub to local Obsidian vault (Windows)
#
# Usage:
#   1. Edit paths below to match your setup
#   2. Run manually: .\sync_from_github.ps1
#   3. Or automate with Task Scheduler (see instructions in OBSIDIAN_SYNC_SOLUTIONS.md)
#

# ============================================================================
# CONFIGURATION - UPDATE THESE PATHS
# ============================================================================

# Path to your Obsidian vault's 40_Claude folder
$VaultPath = "C:\path\to\your\vault\40_Claude"

# GitHub repository (format: username/repo-name)
$GitHubRepo = "yourusername/obsidian-brain-dumps"

# Branch name
$GitHubBranch = "main"

# Log file location
$LogFile = Join-Path $VaultPath "sync.log"

# ============================================================================
# SCRIPT - DO NOT EDIT BELOW THIS LINE
# ============================================================================

# Function to log with timestamp
function Write-Log {
    param($Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp - $Message" | Add-Content -Path $LogFile
}

# Check if vault path exists
if (-not (Test-Path $VaultPath)) {
    Write-Log "ERROR: Vault path does not exist: $VaultPath"
    exit 1
}

# Navigate to vault
Set-Location $VaultPath

# Check if this is a git repository
if (-not (Test-Path ".git")) {
    Write-Log "Initializing git repository..."
    git init
    git remote add origin "https://github.com/$GitHubRepo.git"
    git fetch origin
    git checkout -b $GitHubBranch "origin/$GitHubBranch"
    Write-Log "Git repository initialized"
}

# Pull latest changes
Write-Log "Starting sync..."

# Stash any local changes (shouldn't be any, but just in case)
git stash --include-untracked 2>&1 | Out-Null

# Pull from remote
try {
    $output = git pull origin $GitHubBranch 2>&1
    Write-Log "✓ Sync successful"
    
    # Count new files
    $newFiles = (git diff HEAD@{1} --name-only --diff-filter=A).Count
    if ($newFiles -gt 0) {
        Write-Log "  → $newFiles new notes synced"
    }
}
catch {
    Write-Log "✗ Sync failed - $($_.Exception.Message)"
    exit 1
}

# Clean up
git stash pop 2>&1 | Out-Null

exit 0
