# Slack-Obsidian Brain Dump

Automatically process Slack messages from a dedicated "brain dump" channel and transform them into organized Obsidian notes using Claude AI.

## Features

- 🤖 **AI-Powered Categorization**: Claude analyzes your messages and categorizes them automatically
- 🏷️ **Smart Tagging**: Automatic tag generation based on content, URLs, code languages, and keywords
- 📝 **Structured Notes**: Creates well-formatted Obsidian notes with frontmatter
- 🔗 **Thread Support**: Handles Slack thread replies with bidirectional Wikilinks
- 🔥 **Priority Detection**: Identifies urgent tasks and marks them with fire emojis
- 📊 **Domain Tracking**: Extracts source domains for easy filtering
- ✅ **Slack Reactions**: Confirms processing with checkmark reactions

## Architecture

```
Slack Channel "brain-dump"
    ↓ (webhook trigger on new message)
Flask Server (main.py)
    ↓ (processes event)
Claude API (claude_processor.py)
    ↓ (analyzes and structures)
Obsidian Writer (obsidian_writer.py)
    ↓ (writes markdown file)
Obsidian Vault/40_Claude/inbox/
```

## Prerequisites

- Python 3.8+
- Anthropic API key (comes with Claude Pro)
- Slack workspace with admin access
- Obsidian vault (local or synced)

## Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd slack-obsidian-brain-dump

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
nano .env
```

Required environment variables:

```bash
# Anthropic API Key (get from https://console.anthropic.com/)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Slack Bot Token (starts with xoxb-)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token

# Slack Signing Secret
SLACK_SIGNING_SECRET=your_slack_signing_secret

# Channel ID for brain dump (e.g., C1234567890)
SLACK_BRAIN_DUMP_CHANNEL_ID=C1234567890

# Path to your Obsidian vault
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault

# Optional: Customize folder name (default: 40_Claude)
CLAUDE_FOLDER_NAME=40_Claude

# Optional: Port for Flask server (default: 5000)
FLASK_PORT=5000
```

### 3. Create Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name it "Brain Dump Bot" and select your workspace
4. Under "OAuth & Permissions", add these **Bot Token Scopes**:
   - `channels:history` - Read messages in public channels
   - `channels:read` - View basic channel info
   - `chat:write` - Send messages
   - `reactions:write` - Add emoji reactions
   - `users:read` - View users in workspace
5. Install the app to your workspace
6. Copy the "Bot User OAuth Token" (starts with `xoxb-`)
7. Under "Basic Information", copy the "Signing Secret"
8. Add these values to your `.env` file

### 4. Setup Slack Event Subscriptions

1. In your Slack app settings, go to "Event Subscriptions"
2. Enable Events
3. Set Request URL to: `https://your-domain.com/slack/events`
   - Note: You need to deploy first or use ngrok for local testing (see below)
4. Subscribe to **Bot Events**:
   - `message.channels` - Listen to messages in public channels
5. Save changes
6. Reinstall your app if prompted

### 5. Create Brain Dump Channel

1. In Slack, create a new channel (e.g., `#brain-dump`)
2. Invite your bot: `/invite @Brain Dump Bot`
3. Copy the channel ID:
   - Right-click channel → View channel details
   - Scroll down to see Channel ID
4. Add this to your `.env` file as `SLACK_BRAIN_DUMP_CHANNEL_ID`

## Running Locally (Development)

### Using ngrok for Webhook Testing

```bash
# Install ngrok (https://ngrok.com/)
# Start ngrok tunnel
ngrok http 5000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Add to Slack Event Subscriptions: https://abc123.ngrok.io/slack/events

# In another terminal, start the app
python main.py
```

The server will start on `http://localhost:5000`

## Deployment Options

### Option 1: Railway.app (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add environment variables via Railway dashboard
# Deploy
railway up
```

### Option 2: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
flyctl launch

# Set environment variables
flyctl secrets set ANTHROPIC_API_KEY=your_key
flyctl secrets set SLACK_BOT_TOKEN=your_token
# ... (set all env vars)

# Deploy
flyctl deploy
```

### Option 3: AWS Lambda + API Gateway

See `docs/aws-deployment.md` for detailed instructions.

### Option 4: Run on Your Computer (Always On)

```bash
# Start the server
python main.py

# Keep running in background (macOS/Linux)
nohup python main.py > output.log 2>&1 &

# Or use a process manager like supervisord
```

## Usage

### Basic Usage

1. Post any message in your `#brain-dump` channel
2. The bot will:
   - Analyze the message with Claude
   - Create a categorized note in `40_Claude/inbox/`
   - Add a ✅ reaction to confirm processing

### Thread Replies

1. Reply to any message in a thread
2. A new note will be created with:
   - A Wikilink to the parent note
   - The parent note will be updated with a link to the reply

### Example Messages

**Simple idea:**
```
Had a thought about building a recipe app that uses AI to generate 
meal plans based on what's in your fridge
```

**With URL:**
```
Check out this article about Python 3.13:
https://realpython.com/python313-features
Need to update our codebase
```

**Urgent task:**
```
URGENT: Production API is down!
Need to:
1. Debug connection
2. Contact AWS support ASAP
3. Update stakeholders
```

## Note Structure

Generated notes follow this structure:

```markdown
---
created: 2025-02-04 19:32
title: "Python 3.13 New Features"
tags:
  - claude
  - code/python
  - learning
  - source/realpython
category: code
source: slack
source_domain: realpython.com
slack_ts: 1707076320.123456
status: unprocessed
priority: normal
---

# Python 3.13 New Features

## Summary
Article about Python 3.13's new features with action items for codebase updates.

## Content
[Original message content preserved here]

## Tasks
- [ ] Review Python 3.13 typing improvements
- [ ] Update codebase

## Key References
- [Python 3.13 Features](https://realpython.com/python313-features)
```

## Folder Structure

```
your-obsidian-vault/
└── 40_Claude/
    ├── inbox/          # All new notes land here
    ├── code/           # Code-related (after review)
    ├── news/           # News and articles
    ├── ideas/          # Project ideas
    ├── tasks/          # Action items
    ├── journal/        # Personal reflections
    └── misc/           # Uncategorized
```

## Customization

### Adding New Domains

Edit `config.py` and add to `TAG_RULES['domains']`:

```python
'domains': {
    'your-site.com': ['custom/tag', 'another-tag'],
    # ... more domains
}
```

### Adjusting Categories

Edit `config.py` and modify `VALID_CATEGORIES`:

```python
VALID_CATEGORIES = ["code", "news", "ideas", "tasks", "journal", "misc", "your-category"]
```

### Changing Priority Logic

Edit `obsidian_writer.py` in the `_determine_priority()` method.

## Monitoring

### View Logs

```bash
# Real-time logs
tail -f brain_dump.log

# Search for errors
grep ERROR brain_dump.log
```

### Health Check

```bash
curl http://localhost:5000/health
```

## Troubleshooting

### Messages not processing

1. Check Slack Event Subscriptions are enabled
2. Verify webhook URL is correct
3. Check bot is invited to the channel
4. View logs for errors: `tail -f brain_dump.log`

### Bot not responding

1. Verify `SLACK_BOT_TOKEN` is correct
2. Check bot has correct permissions
3. Ensure app is reinstalled after permission changes

### Notes not appearing in Obsidian

1. Check `OBSIDIAN_VAULT_PATH` is correct
2. Verify folder permissions
3. Look for files in `40_Claude/inbox/`

### Claude API errors

1. Verify `ANTHROPIC_API_KEY` is valid
2. Check API rate limits
3. Review `brain_dump.log` for specific errors

## Development

### Running Tests

```bash
# TODO: Add tests
pytest tests/
```

### Code Style

This project follows PEP 8. Format code with:

```bash
black *.py
flake8 *.py
```

### Adding New Features

1. Create feature branch
2. Update relevant module
3. Test thoroughly
4. Submit PR

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Follow PEP 8 style guidelines
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions

## Roadmap

- [ ] Add support for images/attachments
- [ ] Implement batch processing of old messages
- [ ] Add Slack slash commands for manual triggering
- [ ] Support multiple brain dump channels
- [ ] Add note templates customization via UI
- [ ] Implement note merging for related topics
- [ ] Add search functionality for processed notes

## Credits

Built with:
- [Anthropic Claude API](https://www.anthropic.com/)
- [Slack SDK for Python](https://slack.dev/python-slack-sdk/)
- [Flask](https://flask.palletsprojects.com/)

---

Made with ❤️ for better brain dumping
