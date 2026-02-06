# ObsidianSlack

Automatically transform Slack brain dumps into organized Obsidian notes using Claude AI.

## What This Does

ObsidianSlack captures messages from a designated Slack channel, processes them through Claude AI for intelligent categorization and structuring, then writes them as Obsidian-compatible markdown notes with YAML frontmatter, smart tags, and wikilinks.

## Architecture

The project consists of two parts that work together:

```
┌─────────────────────────────────────────────────────────────┐
│                     CLOUD DEPLOYMENT                        │
│                                                             │
│  Slack Channel → Cloud Run → Claude AI → GitHub Repo       │
│  (brain-dump)    (webhook)   (process)   (storage)         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      LOCAL SYNC                             │
│                                                             │
│  GitHub Repo → Sync Script → Local Obsidian Vault          │
│  (polling)     (cron/scheduler) (40_Claude/inbox/)          │
└─────────────────────────────────────────────────────────────┘
```

**Part 1: Cloud Run Deployment** - Python Flask app that receives Slack webhooks, processes messages with Claude AI, and pushes markdown notes to a GitHub repository.

**Part 2: Local Sync** - Lightweight scripts that pull new notes from GitHub to your local Obsidian vault on a schedule.

## Features

- 🤖 **AI-Powered Categorization** - Claude analyzes your messages and categorizes them automatically
- 🏷️ **Smart Tagging** - Automatic tag generation based on content, URLs, code languages, and keywords
- 📝 **Structured Notes** - Creates well-formatted Obsidian notes with YAML frontmatter
- 🔗 **Thread Support** - Handles Slack thread replies with bidirectional wikilinks
- 🔥 **Priority Detection** - Identifies urgent tasks and marks them appropriately
- 📊 **Domain Tracking** - Extracts source domains for easy filtering
- ✅ **Slack Reactions** - Confirms processing with checkmark reactions

## Quick Start

### Part 1: Cloud Run Deployment

Deploy the webhook server to Google Cloud Run to process Slack messages:

1. Set up Google Cloud project and enable APIs
2. Configure Slack app with event subscriptions
3. Set environment variables (API keys, tokens, channel ID)
4. Deploy container to Cloud Run
5. Configure Slack webhook URL

**[📖 Full Cloud Run Deployment Guide →](cloud-run/README.md)**

### Part 2: Local Sync Setup

Set up automated syncing from GitHub to your local Obsidian vault:

1. Create GitHub personal access token
2. Configure sync script with vault path
3. Set up cron job (macOS/Linux) or Task Scheduler (Windows)
4. Test sync manually before automation

**[📖 Full Local Sync Setup Guide →](local-sync/README.md)**

## Prerequisites

**For Cloud Deployment:**
- Google Cloud account ([free $300 credit](https://cloud.google.com/free))
- Anthropic API key ([from Claude Pro](https://console.anthropic.com/))
- Slack workspace admin access
- GitHub account for note storage

**For Local Sync:**
- Git installed locally
- Obsidian vault (local or synced)
- Cron access (macOS/Linux) or Task Scheduler (Windows)

## Example Usage

Post a message in your Slack brain-dump channel:

```
Check out this article about Python 3.13:
https://realpython.com/python313-features

Need to:
- Review new typing improvements
- Update our codebase to use latest features
```

ObsidianSlack automatically creates:

```markdown
---
created: 2025-02-06 14:32
title: "Python 3.13 New Features"
tags:
  - claude
  - code/python
  - learning
  - source/realpython
category: code
source: slack
source_domain: realpython.com
has_tasks: true
---

# Python 3.13 New Features

## Summary
Article about Python 3.13's new features with action items for codebase updates.

## Content
Check out this article about Python 3.13:
https://realpython.com/python313-features

## Tasks
- [ ] Review new typing improvements
- [ ] Update our codebase to use latest features

## Key References
- [Python 3.13 Features](https://realpython.com/python313-features)
```

## Cost

**Google Cloud Run:** Essentially FREE
- First 2 million requests/month free
- Typical usage: 1000 messages/month = ~$0.10/month

**GitHub:** FREE (private repos included)

**Anthropic API:** Pay-as-you-go (included with Claude Pro subscription)

## Project Structure

```
ObsidianSlack/
├── README.md                  # This file - project overview
├── CLAUDE.md                  # Developer instructions for Claude Code
├── claude_tasks.md            # Bug tracking and known issues
├── .env.example               # Environment variable template
├── .gitignore                 # Git exclusions
│
├── cloud-run/                 # Cloud Run deployment files
│   ├── README.md              # Cloud deployment guide
│   ├── main.py                # Flask webhook server
│   ├── slack_handler.py       # Slack API client
│   ├── claude_processor.py    # Claude AI integration
│   ├── obsidian_writer.py     # Note writing logic
│   ├── tag_generator.py       # Tag extraction
│   ├── utils.py               # Helper functions
│   ├── config.py              # Configuration
│   ├── github_sync.py         # GitHub push integration
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Container image
│   ├── cloudbuild.yaml        # GCP build config
│   └── .dockerignore          # Docker exclusions
│
└── local-sync/                # Local sync scripts
    ├── README.md              # Local sync guide
    ├── sync_from_github.sh    # Unix/macOS sync script
    └── sync_from_github.ps1   # Windows PowerShell sync script
```

## Documentation

- **[Cloud Run Deployment Guide](cloud-run/README.md)** - Complete setup for Google Cloud Run deployment
- **[Local Sync Setup Guide](local-sync/README.md)** - Configure local syncing to Obsidian vault
- **[Developer Guide](CLAUDE.md)** - Architecture, data flow, and development instructions
- **[Known Issues](claude_tasks.md)** - Bug tracking and prioritized fixes

## Development

```bash
# Format code
black cloud-run/*.py

# Lint code
flake8 cloud-run/*.py

# Build Docker image locally
cd cloud-run && docker build -t obsidian-slack .

# Run locally with ngrok
ngrok http 8080
python cloud-run/main.py
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Follow PEP 8 style guidelines
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check [claude_tasks.md](claude_tasks.md) for known issues

---

Made with ❤️ for better brain dumping
