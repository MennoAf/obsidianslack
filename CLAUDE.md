# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

ObsidianSlack captures Slack messages from a designated "brain dump" channel, processes them through Claude AI for structured analysis, and writes them as Obsidian-compatible markdown notes with YAML frontmatter, tags, and wikilinks.

## Project Structure

```
ObsidianSlack/
├── README.md                  # Project overview + quick start
├── CLAUDE.md                  # This file - developer instructions
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
    ├── SYNC_TROUBLESHOOTING.md # Platform-specific troubleshooting
    ├── sync_from_github.sh    # Unix/macOS sync script
    └── sync_from_github.ps1   # Windows PowerShell sync script
```

## Commands

```bash
# Setup
cd cloud-run
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run locally (needs ngrok or similar for Slack webhooks)
python main.py

# Format / lint
black *.py
flake8 *.py

# Docker
docker build -t obsidian-slack .
docker run --env-file .env -p 8080:8080 obsidian-slack

# Cloud Build deploy (GCP)
gcloud builds submit --config cloudbuild.yaml
```

No test suite exists yet.

## Architecture

### Data Flow

```
Slack webhook POST → cloud-run/main.py (/slack/events)
  → slack_handler.py (verify signature, extract message, filter subtypes)
  → claude_processor.py (build prompt from config.CATEGORIZATION_PROMPT, call Claude API, parse JSON response)
  → obsidian_writer.py (generate tags via tag_generator.py, build frontmatter + content)
  → github_sync.py (push .md to GitHub repo)
  → Slack reaction (checkmark on success, X on failure)

GitHub repo → local-sync/sync_from_github.sh (cron/scheduler)
  → git pull → local Obsidian vault/40_Claude/inbox/
```

### Key Design Decisions

- **All notes land in `vault/40_Claude/inbox/`** regardless of category. Category is metadata only — users triage manually into subfolders (code/, news/, ideas/, tasks/, journal/, misc/).
- **The Claude prompt template lives in `config.py`** as `CATEGORIZATION_PROMPT`. It uses `{slack_message}`, `{thread_context}`, `{urls_found}`, `{categories}` placeholders and expects Claude to return JSON with 11 fields (title, category, base_tags, has_tasks, tasks, summary, content, key_urls, code_languages, is_question, detected_urgency).
- **Tags are generated from 5 sources** combined by `tag_generator.py`: Claude's suggested tags, URL domain mappings, code language detection, keyword matching, and content-type flags. All tag rules are defined in `config.TAG_RULES`.
- **Thread replies create separate notes** with bidirectional Obsidian wikilinks (`[[note-name]]`). The parent note gets a `## Replies` section appended. Parent lookup searches all vault subfolders for a note matching `slack_ts` in frontmatter.
- **Fallback resilience**: If Claude fails, a basic note is created with the raw message tagged `unprocessed`. Messages are never dropped.
- **Two storage backends**: `obsidian_writer.py` writes to local filesystem (default). `github_sync.py` provides `GitHubObsidianWriter` as a drop-in replacement for Cloud Run (stateless) deployments, but is **not yet integrated** into `main.py`.

### Module Dependency Graph

```
cloud-run/main.py → slack_handler.py → config
                  → claude_processor.py → config, utils
                  → obsidian_writer.py → config, utils, tag_generator
                                          tag_generator → config, utils
                  → github_sync.py → config, utils

local-sync/sync_from_github.sh (standalone shell script)
```

### Configuration

All config is in `cloud-run/config.py`, loaded from env vars (`.env` file via python-dotenv). `validate_config()` runs at startup and fails fast if required vars are missing. `setup_obsidian_folders()` creates the subfolder structure automatically.

Critical env vars: `ANTHROPIC_API_KEY`, `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, `SLACK_BRAIN_DUMP_CHANNEL_ID`, `GITHUB_TOKEN`, `GITHUB_REPO`. See `.env.example` for the full list.

## Known Issues

See `claude_tasks.md` for a prioritized list of bugs and security issues with fix instructions. Key items:

- Slack signature verification runs after body parsing and url_verification (bypass risk)
- Flask debug mode can expose Werkzeug debugger on 0.0.0.0 (RCE risk)
- No `.dockerignore` — secrets can be baked into images
- JSON extraction regexes in `claude_processor.py` are broken (greedy/non-greedy issues with nested braces)
- YAML frontmatter values other than `title` are not sanitized
- No event deduplication (Slack retries create duplicate notes)
- Race condition on concurrent parent note updates (no file locking)

## Recent Changes (2026-02-06)

### Cross-Platform Support
- **File locking:** Replaced Unix-only `fcntl` with cross-platform `filelock` library
- **Impact:** Project now works on Windows, macOS, and Linux
- **Location:** `cloud-run/obsidian_writer.py`
- **Dependency:** Added `filelock==3.13.1` to requirements.txt

### Improvements Tracking
- Created `IMPROVEMENTS_TRACKER.md` for easy status tracking
- Created `IMPROVEMENTS.md` with detailed improvement analysis
- See these files for future enhancement opportunities

### All Bugs Fixed
- Priority 1 (Security): 8/8 complete
- Priority 2 (Bugs): 11/11 complete
- Priority 3 (Operational): 8/8 complete
- See `claude_tasks.md` for details

### Current State
- ✅ Production-ready on all platforms
- ✅ All known security issues resolved
- ✅ All functional bugs fixed
- ✅ Operational improvements applied
- 📋 Enhancement opportunities documented in IMPROVEMENTS_TRACKER.md
