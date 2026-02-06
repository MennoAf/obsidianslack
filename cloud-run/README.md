# Cloud Run Deployment Guide

This guide covers deploying the ObsidianSlack webhook server to Google Cloud Run. The server receives Slack events, processes messages with Claude AI, and pushes markdown notes to a GitHub repository.

**[← Back to main README](../README.md)**

## Overview

Google Cloud Run hosts a stateless Flask application that:
1. Receives webhook events from Slack
2. Processes messages through Claude AI for categorization
3. Generates structured markdown notes with YAML frontmatter
4. Pushes notes to a GitHub repository for syncing

## Prerequisites

1. **Google Cloud account** - [Sign up for $300 free credit](https://cloud.google.com/free)
2. **Google Cloud SDK** - `gcloud` CLI installed
3. **Anthropic API key** - [Get from console.anthropic.com](https://console.anthropic.com/)
4. **Slack workspace admin access** - To create and configure Slack app
5. **GitHub account** - For storing generated notes

## Cost Estimate

**Google Cloud Run Pricing (2024):**
- First 2 million requests/month: **FREE**
- CPU: $0.00002400/vCPU-second (only while processing)
- Memory: $0.00000250/GiB-second (only while processing)

**For typical use:** Essentially **FREE** or pennies per month
- 1000 brain dumps/month: ~$0.10/month
- Most users stay within the free tier

## Step-by-Step Deployment

### 1. Install Google Cloud SDK

**macOS:**
```bash
brew install google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install

### 2. Initialize Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create slack-brain-dump --name="Slack Brain Dump"

# Set as active project
gcloud config set project slack-brain-dump

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Create Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name it "Brain Dump Bot" and select your workspace

**Add Bot Token Scopes:**
1. Go to "OAuth & Permissions"
2. Add these scopes:
   - `channels:history` - Read messages in public channels
   - `channels:read` - View basic channel info
   - `chat:write` - Send messages
   - `reactions:write` - Add emoji reactions
   - `users:read` - View users in workspace
3. Install the app to your workspace
4. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

**Get Signing Secret:**
1. Go to "Basic Information"
2. Copy the "Signing Secret"

**Create Brain Dump Channel:**
1. In Slack, create a channel (e.g., `#brain-dump`)
2. Invite your bot: `/invite @Brain Dump Bot`
3. Get channel ID:
   - Right-click channel → View channel details
   - Scroll down to see Channel ID (e.g., `C1234567890`)

### 4. Create GitHub Repository

The Cloud Run service will push notes to a GitHub repository:

```bash
# Create a private repository on GitHub named "obsidian-brain-dumps"
# Or use GitHub CLI:
gh repo create obsidian-brain-dumps --private
```

**Create Personal Access Token:**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope (full control of private repositories)
3. Copy the token (starts with `ghp_`)

### 5. Prepare Environment Variables

Create a file called `env.yaml` in the `cloud-run/` directory:

```yaml
ANTHROPIC_API_KEY: "your_anthropic_api_key_here"
SLACK_BOT_TOKEN: "xoxb-your-slack-bot-token"
SLACK_SIGNING_SECRET: "your_slack_signing_secret"
SLACK_BRAIN_DUMP_CHANNEL_ID: "C1234567890"
GITHUB_TOKEN: "ghp_your_github_personal_access_token"
GITHUB_REPO: "yourusername/obsidian-brain-dumps"
OBSIDIAN_VAULT_PATH: "/vault"
CLAUDE_FOLDER_NAME: "40_Claude"
FLASK_PORT: "8080"
DEBUG_MODE: "False"
CLAUDE_MODEL: "claude-sonnet-4-5-20250929"
MAX_TOKENS: "4096"
```

**⚠️ IMPORTANT:** Add `env.yaml` to `.gitignore` - never commit secrets!

### 6. Build and Deploy

**Option A: Automated via Cloud Build (Recommended)**

```bash
# Navigate to cloud-run directory
cd cloud-run

# Submit build and deploy
gcloud builds submit --config cloudbuild.yaml

# Set environment variables after deployment
gcloud run services update slack-obsidian-brain-dump \
  --region us-central1 \
  --env-vars-file env.yaml
```

**Option B: Manual Deployment**

```bash
# Navigate to cloud-run directory
cd cloud-run

# Build the Docker image
gcloud builds submit --tag gcr.io/slack-brain-dump/slack-obsidian-brain-dump

# Deploy to Cloud Run
gcloud run deploy slack-obsidian-brain-dump \
  --image gcr.io/slack-brain-dump/slack-obsidian-brain-dump \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file env.yaml \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60s \
  --max-instances 10 \
  --min-instances 0
```

### 7. Get Service URL

```bash
# Get the deployed service URL
gcloud run services describe slack-obsidian-brain-dump \
  --region us-central1 \
  --format 'value(status.url)'
```

You'll get something like: `https://slack-obsidian-brain-dump-xxxxx-uc.a.run.app`

### 8. Configure Slack Event Subscriptions

1. Go to your Slack app settings: [https://api.slack.com/apps](https://api.slack.com/apps)
2. Select your Brain Dump app
3. Go to "Event Subscriptions"
4. Enable Events
5. Set Request URL to: `https://your-cloud-run-url.run.app/slack/events`
6. Slack will verify the endpoint (should show "Verified ✓")
7. Subscribe to **Bot Events**:
   - `message.channels` - Listen to messages in public channels
8. Save changes
9. Reinstall your app if prompted

### 9. Test Your Deployment

```bash
# Test health endpoint
curl https://your-cloud-run-url.run.app/health

# Post a test message in your #brain-dump channel
# Check Cloud Run logs:
gcloud run services logs read slack-obsidian-brain-dump \
  --region us-central1 \
  --limit 50
```

**Verify GitHub:**
- Check your `obsidian-brain-dumps` repository
- New notes should appear in the `inbox/` folder

## Managing Your Deployment

### View Logs

```bash
# Real-time logs
gcloud run services logs tail slack-obsidian-brain-dump \
  --region us-central1

# Recent logs (last 100 lines)
gcloud run services logs read slack-obsidian-brain-dump \
  --region us-central1 \
  --limit 100

# Filter for errors only
gcloud run services logs read slack-obsidian-brain-dump \
  --region us-central1 \
  --filter "severity>=ERROR"
```

**Cloud Console:**
Visit [https://console.cloud.google.com/run](https://console.cloud.google.com/run)

### Update Environment Variables

**View current variables:**
```bash
gcloud run services describe slack-obsidian-brain-dump \
  --region us-central1 \
  --format 'value(spec.template.spec.containers[0].env)'
```

**Update a single variable:**
```bash
gcloud run services update slack-obsidian-brain-dump \
  --region us-central1 \
  --update-env-vars SLACK_BRAIN_DUMP_CHANNEL_ID=C9876543210
```

**Update multiple variables:**
```bash
gcloud run services update slack-obsidian-brain-dump \
  --region us-central1 \
  --env-vars-file env.yaml
```

### Deploy Code Updates

```bash
# After making code changes
cd cloud-run

# Rebuild and deploy
gcloud builds submit --tag gcr.io/slack-brain-dump/slack-obsidian-brain-dump

gcloud run deploy slack-obsidian-brain-dump \
  --image gcr.io/slack-brain-dump/slack-obsidian-brain-dump \
  --region us-central1
```

### Check Deployment Status

```bash
gcloud run services describe slack-obsidian-brain-dump \
  --region us-central1
```

## Cost Optimization

### Adjust Resource Limits

```bash
gcloud run services update slack-obsidian-brain-dump \
  --region us-central1 \
  --memory 256Mi \
  --cpu 1 \
  --max-instances 5 \
  --min-instances 0 \
  --concurrency 10
```

### Set Request Timeout

```bash
gcloud run services update slack-obsidian-brain-dump \
  --region us-central1 \
  --timeout 30s
```

## Troubleshooting

### Container Fails to Start

```bash
# Check logs for errors
gcloud run services logs read slack-obsidian-brain-dump --region us-central1

# Common issues:
# - Missing environment variables
# - Invalid API keys
# - Port configuration (must listen on $PORT, default 8080)
```

### Slack Webhook Not Working

```bash
# Verify service is public
gcloud run services get-iam-policy slack-obsidian-brain-dump --region us-central1

# Should show allUsers with roles/run.invoker
# If not, run:
gcloud run services add-iam-policy-binding slack-obsidian-brain-dump \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

### GitHub Sync Not Working

**Check logs:**
```bash
gcloud run services logs read slack-obsidian-brain-dump \
  --region us-central1 \
  --filter "github"
```

**Common issues:**
- Invalid GitHub token
- Wrong repository name format (should be `username/repo`)
- Insufficient token permissions (needs `repo` scope)

### Messages Not Processing

1. Check Slack Event Subscriptions are enabled
2. Verify webhook URL is correct
3. Ensure bot is invited to the channel
4. Check Cloud Run logs for errors
5. Verify `SLACK_BRAIN_DUMP_CHANNEL_ID` matches your channel

## Security Best Practices

### Use Secret Manager (Recommended)

Instead of environment variables, use Google Secret Manager:

```bash
# Store secrets
echo -n "your-api-key" | gcloud secrets create anthropic-api-key --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Reference in deployment
gcloud run deploy slack-obsidian-brain-dump \
  --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest"
```

### Verify Slack Signature

The application already implements Slack signature verification in `slack_handler.py`. This prevents unauthorized webhook calls.

### Restrict Access

Cloud Run service must be public for Slack webhooks, but signature verification ensures only Slack can trigger processing.

## Cleanup (Delete Everything)

```bash
# Delete Cloud Run service
gcloud run services delete slack-obsidian-brain-dump --region us-central1

# Delete container images
gcloud container images delete gcr.io/slack-brain-dump/slack-obsidian-brain-dump

# Delete project (if dedicated)
gcloud projects delete slack-brain-dump
```

## Next Steps

After deploying to Cloud Run, set up local syncing to pull notes to your Obsidian vault:

**[📖 Local Sync Setup Guide →](../local-sync/README.md)**

## Additional Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Slack Events API](https://api.slack.com/events-api)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [GitHub API Documentation](https://docs.github.com/en/rest)

---

**[← Back to main README](../README.md)**
