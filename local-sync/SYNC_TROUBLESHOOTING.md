# Sync Automation Troubleshooting Guide

Detailed troubleshooting for automated sync setup across macOS, Linux, and Windows.

**[← Back to Local Sync Guide](README.md)**

---

## Table of Contents

- [macOS Issues](#macos-issues)
  - [Operation Not Permitted (Full Disk Access)](#operation-not-permitted-full-disk-access)
  - [Cron vs LaunchAgent: Which to Use?](#cron-vs-launchagent-which-to-use)
  - [LaunchAgent Not Running](#launchagent-not-running)
  - [Cron Not Running](#cron-not-running)
- [Linux Issues](#linux-issues)
  - [Cron Not Running](#linux-cron-not-running)
  - [SELinux Blocking Script](#selinux-blocking-script)
  - [Permission Denied on Script](#permission-denied-on-script)
- [Windows Issues](#windows-issues)
  - [PowerShell Execution Policy](#powershell-execution-policy)
  - [Task Scheduler Not Running](#task-scheduler-not-running)
  - [Git Not Found in Task Scheduler](#git-not-found-in-task-scheduler)
- [Cross-Platform Issues](#cross-platform-issues)
  - [Git Authentication Failed](#git-authentication-failed)
  - [Merge Conflicts](#merge-conflicts)
  - [Notes Not Appearing](#notes-not-appearing)

---

## macOS Issues

### Operation Not Permitted (Full Disk Access)

**Symptoms:**
- Sync script works when run manually but fails when run by cron or LaunchAgent
- Error log shows: `/bin/bash: Operation not permitted`
- Exit code 126 in LaunchAgent status

**Cause:**
macOS security prevents automated processes from accessing protected folders (Documents, Desktop, Downloads) without explicit permission.

**Solution 1: Grant Full Disk Access to Cron (Recommended)**

1. **Trigger cron to register with the system:**
   ```bash
   crontab -l
   ```

2. **Open System Settings:**
   - Go to **Privacy & Security** → **Full Disk Access**

3. **Add cron:**
   - Click the **+** button
   - Press **Cmd+Shift+G** and type: `/usr/sbin/cron`
   - Select `cron` and enable the toggle

4. **Restart cron:**
   ```bash
   sudo killall cron
   ```

5. **Verify it works:**
   ```bash
   # Wait 5 minutes for next run, then check:
   tail /path/to/vault/sync.log
   ```

**Solution 2: Grant Full Disk Access to Bash (for LaunchAgent)**

If using LaunchAgent instead of cron:

1. **Open System Settings:**
   - Go to **Privacy & Security** → **Full Disk Access**

2. **Add bash:**
   - Click the **+** button
   - Press **Cmd+Shift+G** and type: `/bin/bash`
   - Select `bash` and enable the toggle

3. **Reload LaunchAgent:**
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.obsidianslack.sync.plist
   launchctl load ~/Library/LaunchAgents/com.obsidianslack.sync.plist
   ```

**Solution 3: Move Vault to Non-Protected Location**

If you don't want to grant Full Disk Access:

```bash
# Move vault to a non-protected location
mv ~/Documents/Londo_/40_Claude ~/ObsidianVault/40_Claude

# Update sync script path
nano ~/sync_from_github.sh
# Change VAULT_PATH to new location

# Update Obsidian vault location in the app
```

---

### Cron vs LaunchAgent: Which to Use?

**Use Cron if:**
- ✅ You want simple, standard Unix scheduling
- ✅ You're comfortable granting Full Disk Access to cron
- ✅ You want the same approach as Linux

**Use LaunchAgent if:**
- ✅ You want macOS-native scheduling
- ✅ You need the task to run even when logged out
- ✅ You want better error logging (`StandardErrorPath`)
- ❌ But it requires Full Disk Access for bash

**Our Recommendation:** Use **cron** on macOS for simplicity and cross-platform consistency.

---

### LaunchAgent Not Running

**Check if LaunchAgent is loaded:**
```bash
launchctl list | grep obsidianslack
```

**Expected output:**
```
-    0    com.obsidianslack.sync
```

**If not listed:**
```bash
launchctl load ~/Library/LaunchAgents/com.obsidianslack.sync.plist
```

**If exit code is not 0 (e.g., 126):**
See [Operation Not Permitted](#operation-not-permitted-full-disk-access) above.

**Check error logs:**
```bash
tail -f /tmp/obsidian-sync-error.log
```

**Manually trigger LaunchAgent:**
```bash
launchctl start com.obsidianslack.sync
```

---

### Cron Not Running

**Verify cron is active:**
```bash
# Check if cron service is running
ps aux | grep cron
```

**Verify your crontab:**
```bash
crontab -l
```

**Expected output:**
```
*/5 * * * * /path/to/sync_from_github.sh
```

**Test script manually:**
```bash
bash -x ~/sync_from_github.sh
```

**Check cron logs:**
```bash
# macOS doesn't have traditional /var/log/cron, use system log:
log show --predicate 'eventMessage contains "cron"' --info --last 1h
```

**Common cron issues:**
- ❌ Script path is relative instead of absolute
- ❌ Script doesn't have execute permissions: `chmod +x script.sh`
- ❌ Environment variables not set (cron has minimal environment)

**Fix: Use absolute paths in crontab:**
```bash
# ✅ Good
*/5 * * * * /Users/jasonbauman/sync_from_github.sh

# ❌ Bad
*/5 * * * * ~/sync_from_github.sh
```

---

## Linux Issues

### Linux Cron Not Running

**Check cron service status:**
```bash
# SystemD (Ubuntu 16+, Debian 8+, CentOS 7+)
sudo systemctl status cron

# Older systems
sudo service cron status
```

**If not running, start it:**
```bash
sudo systemctl start cron
sudo systemctl enable cron  # Enable on boot
```

**Verify crontab:**
```bash
crontab -l
```

**Check cron logs:**
```bash
# Ubuntu/Debian
grep CRON /var/log/syslog

# CentOS/RHEL
grep CRON /var/log/cron

# View live logs
sudo tail -f /var/log/syslog | grep CRON
```

---

### SELinux Blocking Script

**Symptoms:**
- Script works manually but fails in cron
- Error: `Permission denied` even with correct file permissions
- SELinux is enabled: `sestatus` shows "enforcing"

**Check if SELinux is blocking:**
```bash
sudo ausearch -m avc -ts recent | grep sync
```

**Solution 1: Adjust SELinux context:**
```bash
# Set proper context for script
sudo chcon -t user_cron_spool_t ~/sync_from_github.sh

# Restore default contexts
sudo restorecon -v ~/sync_from_github.sh
```

**Solution 2: Create SELinux policy (advanced):**
```bash
# Generate policy from audit logs
sudo ausearch -c 'sync_from_github' --raw | audit2allow -M my-syncscript
sudo semodule -i my-syncscript.pp
```

**Solution 3: Disable SELinux (not recommended for production):**
```bash
sudo setenforce 0  # Temporary
# For permanent: edit /etc/selinux/config
```

---

### Permission Denied on Script

**Check file permissions:**
```bash
ls -la ~/sync_from_github.sh
```

**Should show:**
```
-rwxr-xr-x  1 user user  2169 Feb 07 08:00 /home/user/sync_from_github.sh
```

**Fix permissions:**
```bash
chmod +x ~/sync_from_github.sh
```

**Check directory permissions:**
```bash
# Ensure cron can read the script directory
ls -ld ~
```

**Fix if needed:**
```bash
chmod 755 ~
```

---

## Windows Issues

### PowerShell Execution Policy

**Symptoms:**
- Error: `cannot be loaded because running scripts is disabled on this system`
- Task Scheduler shows error 0x1

**Check current policy:**
```powershell
Get-ExecutionPolicy
```

**Solution:**
```powershell
# Set execution policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify
Get-ExecutionPolicy -List
```

**Alternative: Bypass in Task Scheduler:**
When creating the task, use these arguments:
```
-ExecutionPolicy Bypass -File "C:\Users\yourusername\sync_from_github.ps1"
```

---

### Task Scheduler Not Running

**Check task status:**
```powershell
Get-ScheduledTask -TaskName "ObsidianSlack Sync" | Select-Object State, LastRunTime, LastTaskResult
```

**Expected output:**
```
State  : Ready
LastRunTime : 2/7/2026 8:05:00 AM
LastTaskResult : 0  # 0 = success
```

**Common LastTaskResult codes:**
- `0` - Success ✅
- `1` - Incorrect function call or unknown error
- `0x1` - Execution policy blocked script
- `0xFFFD0000` - Task timeout
- `0x41301` - Task is currently running

**Check Task Scheduler GUI:**
1. Open Task Scheduler
2. Find "ObsidianSlack Sync"
3. Right panel → "History" tab (enable if disabled)
4. Look for errors in Event Viewer

**Run task manually to test:**
```powershell
Start-ScheduledTask -TaskName "ObsidianSlack Sync"
```

**Check if Task Scheduler service is running:**
```powershell
Get-Service -Name "Schedule" | Select-Object Status, StartType
```

**Start if stopped:**
```powershell
Start-Service -Name "Schedule"
Set-Service -Name "Schedule" -StartupType Automatic
```

---

### Git Not Found in Task Scheduler

**Symptoms:**
- Error: `'git' is not recognized as an internal or external command`
- Script works in PowerShell but fails in Task Scheduler

**Cause:**
Task Scheduler doesn't inherit your PATH environment variable.

**Solution 1: Use full path to git in script:**

Edit `sync_from_github.ps1`:
```powershell
# Replace 'git' with full path
$gitPath = "C:\Program Files\Git\cmd\git.exe"

# Then use $gitPath instead of 'git'
& $gitPath pull origin main
```

**Find git path:**
```powershell
(Get-Command git).Source
```

**Solution 2: Set PATH in Task Scheduler:**

1. Open Task Scheduler → Edit task
2. Actions → Edit action
3. "Start in" field: Add `C:\Program Files\Git\cmd`

---

## Cross-Platform Issues

### Git Authentication Failed

**Symptoms:**
```
fatal: Authentication failed for 'https://github.com/...'
fatal: could not read Username for 'https://github.com'
```

**Cause:**
- Personal Access Token expired or invalid
- Token not embedded in remote URL
- Insufficient token permissions

**Solution 1: Check token permissions**

Go to [GitHub Settings → Tokens](https://github.com/settings/tokens) and verify:
- ✅ Token is not expired
- ✅ Token has `repo` scope

**Solution 2: Re-add remote with token:**

```bash
cd /path/to/vault/40_Claude

# Remove old remote
git remote remove origin

# Add new remote with token embedded
git remote add origin https://YOUR_TOKEN@github.com/username/repo.git

# Test
git pull origin main
```

**Security Note:** The token is stored in `.git/config`. Keep this file private.

**Solution 3: Use Git Credential Manager (Windows):**

```powershell
# Install Git Credential Manager (included with Git for Windows)
git credential-manager configure

# Remove cached credentials
git credential-manager clear

# Next pull will prompt for credentials
git pull origin main
```

---

### Merge Conflicts

**Symptoms:**
```
error: Your local changes to the following files would be overwritten by merge:
    inbox/some-note.md
```

**Cause:**
You edited a note locally that was also updated in GitHub.

**Solution 1: Stash local changes (recommended):**

```bash
cd /path/to/vault/40_Claude
git stash
git pull origin main
git stash pop  # Merge your changes back
```

**Solution 2: Discard local changes (if not important):**

```bash
git checkout -- inbox/some-note.md
git pull origin main
```

**Solution 3: Keep local version:**

```bash
git pull origin main
# If conflicts occur:
git checkout --ours inbox/some-note.md
git add inbox/some-note.md
git commit -m "Keep local version"
```

**Prevention:**
The sync script should only pull, never commit. If you're manually editing notes in `40_Claude/inbox/`, move them to a subfolder first.

---

### Notes Not Appearing

**Checklist:**

1. **Verify sync script is running:**
   ```bash
   # macOS/Linux
   tail /path/to/vault/sync.log

   # Windows
   Get-Content "$HOME\sync.log" -Tail 20
   ```

2. **Check if notes exist in GitHub:**
   - Visit your repository: `https://github.com/username/obsidian-brain-dumps`
   - Look in the `inbox/` folder
   - If notes are not in GitHub, the issue is with Cloud Run, not local sync

3. **Verify vault path in script:**
   ```bash
   # macOS/Linux
   grep VAULT_PATH ~/sync_from_github.sh

   # Windows
   Select-String -Path "$HOME\sync_from_github.ps1" -Pattern "VaultPath"
   ```

4. **Test git pull manually:**
   ```bash
   cd /path/to/vault/40_Claude
   git pull origin main
   ls -la inbox/
   ```

5. **Check Obsidian vault location:**
   - Open Obsidian → Settings → Files & Links
   - Verify vault path matches sync script path

6. **Restart Obsidian:**
   - Sometimes Obsidian needs a restart to detect new files

---

## Debugging Tips

### Enable Verbose Logging

**macOS/Linux:**

Edit `sync_from_github.sh` and add:
```bash
set -x  # Enable debug mode
```

**Windows:**

Edit `sync_from_github.ps1` and add:
```powershell
$VerbosePreference = "Continue"
Write-Verbose "Starting sync..."
```

---

### Test Automation in Isolation

**macOS/Linux - Test cron environment:**

```bash
# Create test cron job
echo "* * * * * env > /tmp/cron-env.txt" | crontab -

# Wait 1 minute, then check
cat /tmp/cron-env.txt

# Compare to your environment
env > /tmp/user-env.txt
diff /tmp/cron-env.txt /tmp/user-env.txt

# Clean up test cron
crontab -r
```

**Windows - Test Task Scheduler environment:**

Create a test task:
```powershell
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Command `"Get-ChildItem Env: | Out-File C:\Users\$env:USERNAME\task-env.txt`""
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1)
Register-ScheduledTask -TaskName "Test Environment" -Action $Action -Trigger $Trigger

# Wait, then check
Get-Content C:\Users\$env:USERNAME\task-env.txt

# Clean up
Unregister-ScheduledTask -TaskName "Test Environment" -Confirm:$false
```

---

### Monitor Real-Time Logs

**macOS/Linux:**

```bash
# Watch sync log
tail -f /path/to/vault/sync.log

# Watch system logs for cron
# macOS
log stream --predicate 'eventMessage contains "cron"' --info

# Linux
sudo tail -f /var/log/syslog | grep CRON
```

**Windows:**

```powershell
# Watch sync log
Get-Content "$HOME\sync.log" -Wait -Tail 20

# Watch Task Scheduler events
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" -MaxEvents 20
```

---

## Still Having Issues?

1. **Run the sync script manually first:**
   - If manual runs work but automation doesn't, it's a permissions/environment issue
   - If manual runs fail, it's a git/path configuration issue

2. **Check the basics:**
   - Script has execute permissions (Unix) or execution policy allows it (Windows)
   - Paths are absolute, not relative
   - Git is in PATH or full path is used
   - GitHub token is valid and has repo access

3. **Platform-specific help:**
   - macOS: Check Full Disk Access settings
   - Linux: Check SELinux/AppArmor status
   - Windows: Check Execution Policy and Task Scheduler service

4. **Open an issue:**
   - If you're still stuck, open an issue on GitHub with:
     - Your OS and version
     - Output of manual script run
     - Relevant logs (cron, Task Scheduler, system logs)
     - Your automation setup (crontab, plist, task XML)

---

**[← Back to Local Sync Guide](README.md)** | **[← Back to Main README](../README.md)**
