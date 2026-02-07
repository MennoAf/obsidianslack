# Git Workflow - ObsidianSlack

This repository uses a **dual-remote setup** to maintain a private fork while staying synced with the original public repository.

## Remote Configuration

```bash
origin   → git@github.com:MennoAf/second_brain.git      (your private repo)
upstream → git@github.com:MennoAf/obsidianslack.git     (original public repo)
```

## Daily Workflow

### Regular Development (Private Repo)

```bash
# Make changes
git add .
git commit -m "Your commit message"

# Push to your private repo (default)
git push
```

### Pull Updates from Original Repo

```bash
# Fetch latest changes from the public repo
git fetch upstream

# Merge updates into your local branch
git merge upstream/master
# Alternative: git pull upstream master

# Push merged updates to your private repo
git push
```

### Contribute Improvements Back to Original

#### Option A: Pull Request (Recommended)

```bash
# Create a feature branch
git checkout -b my-improvement

# Make changes
git add .
git commit -m "Add awesome feature"

# Push to your private repo
git push origin my-improvement

# Then on GitHub:
# Create Pull Request from MennoAf/second_brain:my-improvement → MennoAf/obsidianslack:master
```

#### Option B: Direct Push (If You Have Write Access)

```bash
# Ensure your master is up to date
git checkout master
git pull upstream master

# Push directly to upstream
git push upstream master

# Sync to your private repo
git push origin master
```

## Maintenance Commands

### Check Remote Configuration

```bash
git remote -v
```

### View All Branches

```bash
# Local branches
git branch

# All branches (including remote)
git branch -a
```

### Sync All Branches

```bash
# Fetch all updates from upstream
git fetch upstream

# Push all local branches to your private repo
git push origin --all

# Push all tags to your private repo
git push origin --tags
```

### Handle Merge Conflicts

```bash
# If merge has conflicts
git fetch upstream
git merge upstream/master

# Fix conflicts in your editor, then:
git add .
git commit -m "Merge upstream changes"
git push
```

## Reset/Reconfiguration

If you ever need to reconfigure the remotes:

```bash
# Remove existing remotes
git remote remove origin
git remote remove upstream

# Re-add them
git remote add origin git@github.com:MennoAf/second_brain.git
git remote add upstream git@github.com:MennoAf/obsidianslack.git

# Verify
git remote -v
```

## Best Practices

1. **Fetch regularly**: Run `git fetch upstream` at least daily to stay current
2. **Keep master clean**: Do new work in feature branches
3. **Test before pushing**: Ensure changes work before pushing to either remote
4. **Descriptive commits**: Write clear commit messages for easier collaboration
5. **Sync often**: Keep your private repo in sync with your changes

## Troubleshooting

### "Divergent branches" error

```bash
# If your branch has diverged from upstream
git fetch upstream
git rebase upstream/master
# Or if you prefer merging:
git merge upstream/master
```

### Accidentally pushed to wrong remote

```bash
# If you pushed to upstream by mistake and need to undo
git push upstream :branch-name  # Deletes the branch (use with caution!)
```

### Force sync with upstream (nuclear option)

```bash
# WARNING: This discards ALL local changes
git fetch upstream
git reset --hard upstream/master
git push origin master --force
```
