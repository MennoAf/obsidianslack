# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

ObsidianSlack captures Slack messages from a designated "brain dump" channel, processes them through Claude AI for structured analysis, and writes them as Obsidian-compatible markdown notes with YAML frontmatter, tags, and wikilinks.

## Commands

```bash
# Setup
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
Slack webhook POST → main.py (/slack/events)
  → slack_handler.py (verify signature, extract message, filter subtypes)
  → claude_processor.py (build prompt from config.CATEGORIZATION_PROMPT, call Claude API, parse JSON response)
  → obsidian_writer.py (generate tags via tag_generator.py, build frontmatter + content, write .md to vault)
  → Slack reaction (checkmark on success, X on failure)
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
main.py → slack_handler.py → config
        → claude_processor.py → config, utils
        → obsidian_writer.py → config, utils, tag_generator
                                tag_generator → config, utils
github_sync.py (standalone, not yet wired in)
```

### Configuration

All config is in `config.py`, loaded from env vars (`.env` file via python-dotenv). `validate_config()` runs at startup and fails fast if required vars are missing. `setup_obsidian_folders()` creates the subfolder structure automatically.

Critical env vars: `ANTHROPIC_API_KEY`, `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, `SLACK_BRAIN_DUMP_CHANNEL_ID`, `OBSIDIAN_VAULT_PATH`. See `.env.example` for the full list.

## Known Issues

See `claude_tasks.md` for a prioritized list of bugs and security issues with fix instructions. Key items:

- Slack signature verification runs after body parsing and url_verification (bypass risk)
- Flask debug mode can expose Werkzeug debugger on 0.0.0.0 (RCE risk)
- No `.dockerignore` — secrets can be baked into images
- JSON extraction regexes in `claude_processor.py` are broken (greedy/non-greedy issues with nested braces)
- YAML frontmatter values other than `title` are not sanitized
- No event deduplication (Slack retries create duplicate notes)
- Race condition on concurrent parent note updates (no file locking)
