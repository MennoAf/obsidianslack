# Obsidian Sync Solutions for Cloud Run

## The Challenge

Obsidian is **local-first** by design. Your Cloud Run service is stateless and can't directly write to your local computer. Here are your options, ranked by practicality:

---

## ⭐ Option 1: Deliver via Slack → Manual Save (EASIEST)

**How it works:**
1. Cloud Run processes your brain dump
2. Sends you the formatted markdown via Slack DM
3. You copy/paste into Obsidian (or save the file)

**Pros:**
- ✅ Simple - no complex sync needed
- ✅ You review before saving (fits your 40_Claude staging workflow)
- ✅ Works on phone and desktop
- ✅ No additional services needed

**Cons:**
- ❌ Manual step required
- ❌ Not truly "automatic"

**Implementation:**
Just modify the Slack handler to DM you the markdown content instead of (or in addition to) writing to a file.

---

## ⭐⭐ Option 2: Git Repository Sync (RECOMMENDED)

**How it works:**
1. Cloud Run writes notes to a private GitHub repo
2. Your computer pulls changes every X minutes
3. Notes sync to your local Obsidian vault via Git

**Pros:**
- ✅ Fully automatic once set up
- ✅ Version control for your notes
- ✅ Works with Obsidian Sync (no conflicts)
- ✅ Can sync to multiple devices
- ✅ Free (GitHub private repos are free)

**Cons:**
- ❌ Requires Git setup
- ❌ 5-10 minute sync delay

**Setup:** See detailed guide below ⬇️

---

## ⭐⭐⭐ Option 3: Obsidian Sync + Watched Folder (BEST OF BOTH WORLDS)

**How it works:**
1. Cloud Run writes to a Google Cloud Storage bucket OR Git repo
2. A sync script on your computer pulls new notes to a watched folder
3. Obsidian Sync handles the rest automatically

**Pros:**
- ✅ Automatic everywhere
- ✅ Works on desktop, mobile, tablet
- ✅ Leverages your existing Obsidian Sync subscription
- ✅ No manual intervention

**Cons:**
- ❌ Requires running a sync script on one device
- ❌ Slight complexity in setup

**Setup:** See detailed guide below ⬇️

---

## ⭐ Option 4: Dropbox/Google Drive (LEGACY)

**How it works:**
1. Cloud Run writes to Dropbox/Google Drive via API
2. Obsidian vault is in the synced folder
3. Changes sync automatically

**Pros:**
- ✅ Automatic sync
- ✅ Works if you already use these services

**Cons:**
- ❌ Conflicts with Obsidian Sync (can't use both)
- ❌ API setup complexity
- ❌ Potential file conflicts

---

# 📋 Detailed Implementation Guides

## Implementation A: Git Repository Sync (Recommended)

### Step 1: Create a Private GitHub Repository

```bash
# Create a new private repo on GitHub
# Let's call it "obsidian-brain-dumps"

# Initialize in your Obsidian vault's 40_Claude folder
cd /path/to/your/vault/40_Claude
git init
git remote add origin git@github.com:yourusername/obsidian-brain-dumps.git
```

### Step 2: Modify Cloud Run to Push to GitHub

Add these to your `requirements.txt`:
```
PyGithub==2.1.1
```

Create new file `github_sync.py`:

```python
"""
GitHub repository sync for Obsidian notes.
"""
import os
import base64
from github import Github, GithubException
import logging

logger = logging.getLogger(__name__)

class GitHubSync:
    """Sync notes to GitHub repository."""
    
    def __init__(self):
        self.github = Github(os.getenv('GITHUB_TOKEN'))
        self.repo_name = os.getenv('GITHUB_REPO')  # e.g., "yourusername/obsidian-brain-dumps"
        self.repo = self.github.get_repo(self.repo_name)
    
    def write_note(self, filename: str, content: str, folder: str = "inbox"):
        """
        Write a note to the GitHub repository.
        
        Args:
            filename: Name of the file
            content: Markdown content
            folder: Subfolder (default: inbox)
        """
        path = f"{folder}/{filename}"
        
        try:
            # Try to get existing file
            try:
                file = self.repo.get_contents(path)
                # Update existing file
                self.repo.update_file(
                    path,
                    f"Update {filename}",
                    content,
                    file.sha
                )
                logger.info(f"Updated file in GitHub: {path}")
            except GithubException:
                # File doesn't exist, create it
                self.repo.create_file(
                    path,
                    f"Add {filename}",
                    content
                )
                logger.info(f"Created file in GitHub: {path}")
                
        except Exception as e:
            logger.error(f"Error writing to GitHub: {e}")
            raise
```

Update `env.yaml` with:
```yaml
GITHUB_TOKEN: "ghp_your_personal_access_token"
GITHUB_REPO: "yourusername/obsidian-brain-dumps"
```

### Step 3: Set Up Local Sync Script

Create `sync_from_github.sh` in your Obsidian vault:

```bash
#!/bin/bash

# Navigate to your 40_Claude folder
cd /path/to/your/vault/40_Claude

# Pull latest changes
git pull origin main

# Log the sync
echo "$(date): Synced from GitHub" >> sync.log
```

Make it executable:
```bash
chmod +x sync_from_github.sh
```

### Step 4: Automate Sync

**macOS/Linux (cron):**
```bash
# Edit crontab
crontab -e

# Add this line to sync every 5 minutes
*/5 * * * * /path/to/your/vault/40_Claude/sync_from_github.sh
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Repeat every 5 minutes
4. Action: Run `sync_from_github.sh`

**Better option - fswatch (macOS/Linux):**
```bash
# Install fswatch
brew install fswatch  # macOS
# apt-get install fswatch  # Linux

# Watch for changes and pull
fswatch -o /path/to/your/vault/40_Claude | xargs -n1 -I{} git -C /path/to/your/vault/40_Claude pull
```

---

## Implementation B: Obsidian Sync + Google Cloud Storage

### Step 1: Create GCS Bucket

```bash
gsutil mb -l us-central1 gs://your-brain-dump-bucket
```

### Step 2: Modify obsidian_writer.py

Change the write path to use GCS:

```python
from google.cloud import storage

class ObsidianWriter:
    def __init__(self):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket('your-brain-dump-bucket')
    
    def _write_file(self, filepath: Path, content: str):
        """Write to GCS bucket instead of local filesystem."""
        blob_name = f"40_Claude/{filepath.name}"
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(content, content_type='text/markdown')
```

### Step 3: Local Sync Script

```bash
#!/bin/bash

# Sync GCS bucket to local Obsidian vault
gsutil -m rsync -r gs://your-brain-dump-bucket/40_Claude /path/to/your/vault/40_Claude

echo "$(date): Synced from GCS" >> sync.log
```

Run this every 5 minutes via cron/Task Scheduler.

---

## Implementation C: Slack DM Delivery (Simplest)

### Modify slack_handler.py

Add a method to send markdown via DM:

```python
def send_note_via_dm(self, user_id: str, filename: str, content: str):
    """
    Send the generated note as a Slack DM.
    
    Args:
        user_id: Slack user ID to send to
        filename: Name of the note file
        content: Full markdown content
    """
    message = f"""
📝 *New Brain Dump Note Created*

Filename: `{filename}`

```markdown
{content}
```

Save this to your Obsidian vault!
"""
    
    try:
        self.client.chat_postMessage(
            channel=user_id,
            text=message,
            unfurl_links=False,
            unfurl_media=False
        )
        logger.info(f"Sent note via DM to {user_id}")
    except Exception as e:
        logger.error(f"Error sending DM: {e}")
```

### Update main.py

After creating the note, send it to you:

```python
# In process_slack_event function, after creating note:
slack_handler.send_note_via_dm(
    user_id='YOUR_SLACK_USER_ID',
    filename=result['filename'],
    content=frontmatter + content
)
```

### On Your Phone/Computer

When you get the DM:
1. **Desktop:** Copy the markdown, save as `.md` file in Obsidian vault
2. **Mobile:** Use Obsidian's "Create note from clipboard" feature
3. **Automated:** Use iOS Shortcuts or Android Tasker to auto-save

---

## My Recommendation for You

Given that you have **Obsidian Sync**, I recommend:

### **Hybrid Approach: Git Sync + Obsidian Sync**

1. **Cloud Run → GitHub** (automatic)
2. **GitHub → Your Desktop** (cron job every 5 minutes)
3. **Desktop → Other Devices** (Obsidian Sync handles it)

**Why this works:**
- ✅ Fully automatic once set up
- ✅ Git provides version control and backup
- ✅ Obsidian Sync handles mobile/tablet seamlessly
- ✅ You keep the `40_Claude` staging area workflow
- ✅ No conflicts with Obsidian Sync (they work together)

**Setup time:** ~30 minutes  
**Ongoing maintenance:** None

---

## Quick Setup Checklist

- [ ] Create private GitHub repo
- [ ] Generate GitHub Personal Access Token
- [ ] Add `PyGithub` to requirements.txt
- [ ] Create `github_sync.py` module
- [ ] Update Cloud Run environment variables
- [ ] Redeploy to Cloud Run
- [ ] Set up local sync script
- [ ] Add cron job / Task Scheduler
- [ ] Test with a brain dump message
- [ ] Verify sync to Obsidian

---

## Questions?

**Q: What about conflicts?**  
A: Since Cloud Run only writes new files (never edits), conflicts are impossible. Once you move notes from `40_Claude/inbox/` to your main vault, they're untouched by the sync.

**Q: What if I'm offline?**  
A: Changes queue in Git/GCS. When you come online, they sync automatically.

**Q: Can I use this on mobile?**  
A: Yes! The Git→Desktop→Obsidian Sync chain means mobile gets updates automatically via Obsidian Sync.

**Q: How much does this cost?**  
A: GitHub: Free, Cloud Run: ~Free, Obsidian Sync: You already have it. Total: $0

Let me know which approach you want to implement and I can provide the complete code!
