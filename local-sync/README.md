# Local Sync Setup Guide

This guide covers setting up automated syncing from the GitHub repository (where Cloud Run pushes notes) to your local Obsidian vault.

**[← Back to main README](../README.md)**

## Overview

The local sync system pulls new notes from your GitHub repository on a regular schedule and places them in your Obsidian vault. This works seamlessly with Obsidian Sync to propagate notes to all your devices.

**How it works:**
1. Cloud Run writes notes to GitHub repository
2. Local sync script pulls changes every few minutes
3. Notes appear in your Obsidian vault at `40_Claude/inbox/`
4. (Optional) Obsidian Sync propagates to mobile/tablet

## Prerequisites

- **Git** installed locally
- **Obsidian vault** (local or synced)
- **GitHub repository** set up (from Cloud Run deployment)
- **GitHub Personal Access Token** with repo access
- **Cron access** (macOS/Linux) or **Task Scheduler** (Windows)

## Quick Start

### 1. Verify Git Installation

```bash
git --version
# Should show: git version 2.x.x
```

If not installed:
- **macOS:** `brew install git` or download from [git-scm.com](https://git-scm.com/)
- **Linux:** `sudo apt-get install git` or `sudo yum install git`
- **Windows:** Download from [git-scm.com](https://git-scm.com/)

### 2. Create GitHub Personal Access Token

1. Go to [GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name: "ObsidianSlack Sync"
4. Select scopes:
   - ✅ `repo` - Full control of private repositories
5. Click "Generate token"
6. **Copy the token immediately** (starts with `ghp_`) - you won't see it again!

### 3. Initialize Git in Your Obsidian Vault

Navigate to your Obsidian vault's Claude folder and initialize Git:

```bash
# Navigate to your vault's Claude folder
cd /path/to/your/obsidian/vault/40_Claude

# Initialize Git repository
git init

# Add the remote repository (replace with your username and repo)
git remote add origin https://YOUR_GITHUB_TOKEN@github.com/yourusername/obsidian-brain-dumps.git

# Initial pull to sync existing notes
git pull origin main

# If this is a new repo, you might need to create the main branch first:
git checkout -b main
```

**Security Note:** The token is stored in the `.git/config` file. Keep this private and add it to your `.gitignore`.

### 4. Configure Sync Script

**macOS/Linux:**

1. Copy the sync script:
```bash
cp /path/to/ObsidianSlack/local-sync/sync_from_github.sh ~/sync_from_github.sh
```

2. Edit the script with your vault path:
```bash
nano ~/sync_from_github.sh
```

3. Update these variables:
```bash
VAULT_PATH="/path/to/your/obsidian/vault/40_Claude"
```

4. Make it executable:
```bash
chmod +x ~/sync_from_github.sh
```

5. Test it manually:
```bash
~/sync_from_github.sh
```

**Windows:**

1. Copy the PowerShell script:
```powershell
Copy-Item "C:\path\to\ObsidianSlack\local-sync\sync_from_github.ps1" -Destination "$HOME\sync_from_github.ps1"
```

2. Edit the script with your vault path:
```powershell
notepad $HOME\sync_from_github.ps1
```

3. Update this variable:
```powershell
$VaultPath = "C:\path\to\your\obsidian\vault\40_Claude"
```

4. Test it manually:
```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\sync_from_github.ps1"
```

## Automation Setup

### macOS/Linux: Using Cron

Cron runs scheduled tasks automatically in the background.

**Edit crontab:**
```bash
crontab -e
```

**Add this line to sync every 5 minutes:**
```bash
*/5 * * * * /Users/yourusername/sync_from_github.sh >> /Users/yourusername/sync.log 2>&1
```

**Or sync every 10 minutes:**
```bash
*/10 * * * * /Users/yourusername/sync_from_github.sh >> /Users/yourusername/sync.log 2>&1
```

**Verify cron job is scheduled:**
```bash
crontab -l
```

**View sync logs:**
```bash
tail -f ~/sync.log
```

### macOS: Using launchd (Alternative to Cron)

Launchd is more reliable than cron on macOS for user-level tasks.

**Create plist file:**
```bash
nano ~/Library/LaunchAgents/com.yourusername.obsidianslack.plist
```

**Add this content:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yourusername.obsidianslack</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/yourusername/sync_from_github.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer> <!-- 300 seconds = 5 minutes -->
    <key>StandardOutPath</key>
    <string>/Users/yourusername/sync.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/yourusername/sync_error.log</string>
</dict>
</plist>
```

**Load and start:**
```bash
launchctl load ~/Library/LaunchAgents/com.yourusername.obsidianslack.plist
launchctl start com.yourusername.obsidianslack
```

**Verify it's running:**
```bash
launchctl list | grep obsidianslack
```

**Stop or unload:**
```bash
launchctl stop com.yourusername.obsidianslack
launchctl unload ~/Library/LaunchAgents/com.yourusername.obsidianslack.plist
```

### Windows: Using Task Scheduler

Task Scheduler runs scheduled tasks automatically in the background.

**Create scheduled task:**

1. Open Task Scheduler (search in Start menu)
2. Click "Create Basic Task"
3. Name: "ObsidianSlack Sync"
4. Trigger: "Daily"
5. Daily settings: Start at login, Repeat every **5 minutes**, for **Indefinitely**
6. Action: "Start a program"
7. Program/script: `powershell.exe`
8. Arguments: `-ExecutionPolicy Bypass -File "C:\Users\yourusername\sync_from_github.ps1"`
9. Finish

**Alternative: Using Command Line**

```powershell
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$HOME\sync_from_github.ps1`""
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "ObsidianSlack Sync" -Action $Action -Trigger $Trigger -Description "Sync ObsidianSlack notes from GitHub"
```

**Verify task:**
```powershell
Get-ScheduledTask -TaskName "ObsidianSlack Sync"
```

**View logs:**
```powershell
Get-Content "$HOME\sync.log" -Tail 50 -Wait
```

## Advanced: Real-Time Sync with fswatch (macOS/Linux)

For near-instant syncing, use `fswatch` to watch the repository for changes:

**Install fswatch:**
```bash
# macOS
brew install fswatch

# Linux (Ubuntu/Debian)
sudo apt-get install fswatch

# Linux (Fedora/RHEL)
sudo dnf install fswatch
```

**Create watch script:**
```bash
nano ~/watch_sync.sh
```

**Add content:**
```bash
#!/bin/bash
VAULT_PATH="/path/to/your/obsidian/vault/40_Claude"

# Watch for changes and pull
while true; do
    cd "$VAULT_PATH"
    git fetch origin main

    # Check if there are new commits
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})

    if [ $LOCAL != $REMOTE ]; then
        echo "$(date): New changes detected, pulling..."
        git pull origin main
    fi

    sleep 30  # Check every 30 seconds
done
```

**Make executable and run:**
```bash
chmod +x ~/watch_sync.sh
nohup ~/watch_sync.sh &
```

## Troubleshooting

**For detailed platform-specific troubleshooting (macOS permissions, Linux SELinux, Windows Task Scheduler issues), see:**
**[📖 SYNC_TROUBLESHOOTING.md](SYNC_TROUBLESHOOTING.md)** - Comprehensive troubleshooting guide

### Quick Fixes

### Git Authentication Fails

**Error:** `fatal: Authentication failed`

**Solution:**
1. Verify your Personal Access Token is valid
2. Check the token has `repo` scope
3. Re-add the remote with the token:
```bash
cd /path/to/vault/40_Claude
git remote remove origin
git remote add origin https://YOUR_TOKEN@github.com/username/repo.git
```

### Merge Conflicts

**Error:** `error: Your local changes would be overwritten by merge`

**Solution:**
The sync script should only pull (never commit), so conflicts shouldn't happen. If they do:
```bash
cd /path/to/vault/40_Claude
git stash
git pull origin main
git stash pop
```

### Sync Not Running

**macOS/Linux (cron):**
```bash
# Check cron is running
sudo systemctl status cron  # Linux
sudo launchctl list | grep cron  # macOS

# View cron logs
grep CRON /var/log/syslog  # Linux
log show --predicate 'process == "cron"' --last 1h  # macOS

# Test script manually
bash -x ~/sync_from_github.sh
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Find "ObsidianSlack Sync" task
3. Check "Last Run Result" (should be 0x0 for success)
4. View "History" tab for detailed logs
5. Run manually: Right-click → Run

### Permission Denied

**macOS/Linux:**
```bash
# Ensure script is executable
chmod +x ~/sync_from_github.sh

# Check file permissions
ls -la ~/sync_from_github.sh
```

**Windows:**
```powershell
# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Notes Not Appearing in Obsidian

1. Check the vault path in your sync script is correct
2. Verify Git is pulling successfully:
```bash
cd /path/to/vault/40_Claude
git pull origin main
```
3. Check that notes are in the GitHub repository
4. Verify Obsidian is watching the correct vault folder

## Integration with Obsidian Sync

If you use Obsidian Sync, the synced notes will automatically propagate to all your devices:

1. **Desktop** (where sync script runs) ← Git pulls from GitHub
2. **Mobile/Tablet** ← Obsidian Sync from desktop

This creates a seamless flow: Cloud Run → GitHub → Desktop → Obsidian Sync → All Devices

**No additional configuration needed!** Just ensure Obsidian Sync is enabled for the `40_Claude` folder.

## Performance Tips

### Reduce Sync Frequency for Battery Life

On laptops, frequent syncing can drain battery. Adjust the interval:

**Cron (every 15 minutes):**
```bash
*/15 * * * * /Users/yourusername/sync_from_github.sh
```

**Task Scheduler (every 15 minutes):**
Change "Repeat every" to 15 minutes

### Only Sync When Computer is Awake

**macOS launchd:**
Add this to the plist:
```xml
<key>RunAtLoad</key>
<true/>
```

**Windows Task Scheduler:**
In settings, check "Wake the computer to run this task" only if needed

## Next Steps

- **[← Back to Cloud Run Deployment](../cloud-run/README.md)**
- **[← Back to main README](../README.md)**

## Additional Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Cron Documentation](https://man7.org/linux/man-pages/man5/crontab.5.html)
- [Windows Task Scheduler Guide](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)

---

**[← Back to main README](../README.md)**
