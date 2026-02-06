# Google Cloud Run Deployment Guide

## Prerequisites

1. Google Cloud account ([sign up for $300 free credit](https://cloud.google.com/free))
2. Google Cloud SDK (`gcloud` CLI) installed
3. Project files from this repository

## Cost Estimate

**Google Cloud Run Pricing (as of 2024):**
- First 2 million requests/month: **FREE**
- CPU: $0.00002400/vCPU-second (only while processing)
- Memory: $0.00000250/GiB-second (only while processing)

**For this use case:** Essentially **FREE** or pennies per month
- You'll likely stay within the free tier
- Even with 1000 brain dumps/month: ~$0.10/month

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

### 2. Initialize gcloud

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

### 3. Prepare Your Environment Variables

Create a file called `env.yaml` with your secrets:

```yaml
ANTHROPIC_API_KEY: "your_anthropic_api_key_here"
SLACK_BOT_TOKEN: "xoxb-your-slack-bot-token"
SLACK_SIGNING_SECRET: "your_slack_signing_secret"
SLACK_BRAIN_DUMP_CHANNEL_ID: "C1234567890"
OBSIDIAN_VAULT_PATH: "/vault"
CLAUDE_FOLDER_NAME: "40_Claude"
FLASK_PORT: "8080"
DEBUG_MODE: "False"
CLAUDE_MODEL: "claude-sonnet-4-5-20250929"
MAX_TOKENS: "4096"
```

**⚠️ IMPORTANT:** Add `env.yaml` to `.gitignore` - never commit secrets!

### 4. Build and Deploy (Option A: Manual)

```bash
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

### 4. Build and Deploy (Option B: Automated via Cloud Build)

```bash
# Submit build and deploy in one command
gcloud builds submit --config cloudbuild.yaml

# Set environment variables after deployment
gcloud run services update slack-obsidian-brain-dump \
  --region us-central1 \
  --env-vars-file env.yaml
```

### 5. Get Your Service URL

```bash
# Get the deployed service URL
gcloud run services describe slack-obsidian-brain-dump \
  --region us-central1 \
  --format 'value(status.url)'
```

You'll get something like: `https://slack-obsidian-brain-dump-xxxxx-uc.a.run.app`

### 6. Configure Slack Webhook

1. Go to your Slack app settings: https://api.slack.com/apps
2. Select your Brain Dump app
3. Go to "Event Subscriptions"
4. Set Request URL to: `https://your-cloud-run-url.run.app/slack/events`
5. Slack will verify the endpoint
6. Save changes

### 7. Test Your Deployment

```bash
# Test health endpoint
curl https://your-cloud-run-url.run.app/health

# Post a test message in your #brain-dump channel
# Check Cloud Run logs:
gcloud run services logs read slack-obsidian-brain-dump \
  --region us-central1 \
  --limit 50
```

## Obsidian Sync Configuration

**IMPORTANT:** Since Cloud Run is stateless and your Obsidian vault is local, you need a sync strategy.

### Option 1: Google Cloud Storage Bucket (Recommended)

Mount a GCS bucket as your vault location:

```bash
# Create a bucket
gsutil mb gs://your-vault-bucket

# Update your deployment to mount the bucket
# (Requires Cloud Run with GCS FUSE - see below)
```

**Then sync locally:**
```bash
# Install gsutil
# Sync vault to your local Obsidian
gsutil -m rsync -r gs://your-vault-bucket /path/to/local/obsidian/vault
```

### Option 2: GitHub/Git Repo (Simpler)

1. Create a private GitHub repo for your vault
2. Cloud Run commits notes to the repo
3. Local script pulls changes periodically

### Option 3: Hybrid - Process in Cloud, Deliver via Slack

Cloud Run could:
1. Process the message
2. Generate the markdown
3. Send it back to you via Slack DM or email
4. You manually save to Obsidian

**This is actually the most practical for Obsidian's local-first philosophy!**

See the next section for implementation.

## Managing Environment Variables

### View current variables:
```bash
gcloud run services describe slack-obsidian-brain-dump \
  --region us-central1 \
  --format 'value(spec.template.spec.containers[0].env)'
```

### Update a single variable:
```bash
gcloud run services update slack-obsidian-brain-dump \
  --region us-central1 \
  --update-env-vars SLACK_BRAIN_DUMP_CHANNEL_ID=C9876543210
```

### Update multiple variables:
```bash
gcloud run services update slack-obsidian-brain-dump \
  --region us-central1 \
  --env-vars-file env.yaml
```

## Monitoring

### View Logs:
```bash
# Real-time logs
gcloud run services logs tail slack-obsidian-brain-dump \
  --region us-central1

# Recent logs
gcloud run services logs read slack-obsidian-brain-dump \
  --region us-central1 \
  --limit 100
```

### Cloud Console:
Visit: https://console.cloud.google.com/run

## Troubleshooting

### Container fails to start:
```bash
# Check logs for errors
gcloud run services logs read slack-obsidian-brain-dump --region us-central1

# Common issues:
# - Missing environment variables
# - Invalid API keys
# - Port configuration (must listen on $PORT)
```

### Slack webhook not working:
```bash
# Verify service is public
gcloud run services get-iam-policy slack-obsidian-brain-dump --region us-central1

# Should show allUsers with roles/run.invoker
```

### Check deployment status:
```bash
gcloud run services describe slack-obsidian-brain-dump \
  --region us-central1
```

## Updating Your Deployment

```bash
# After making code changes
gcloud builds submit --tag gcr.io/slack-brain-dump/slack-obsidian-brain-dump

# Deploy the new version
gcloud run deploy slack-obsidian-brain-dump \
  --image gcr.io/slack-brain-dump/slack-obsidian-brain-dump \
  --region us-central1
```

## Cost Optimization

### Set resource limits:
```bash
gcloud run services update slack-obsidian-brain-dump \
  --region us-central1 \
  --memory 256Mi \
  --cpu 1 \
  --max-instances 5 \
  --min-instances 0 \
  --concurrency 10
```

### Enable request timeout:
```bash
gcloud run services update slack-obsidian-brain-dump \
  --region us-central1 \
  --timeout 30s
```

## Cleanup (Delete Everything)

```bash
# Delete Cloud Run service
gcloud run services delete slack-obsidian-brain-dump --region us-central1

# Delete container images
gcloud container images delete gcr.io/slack-brain-dump/slack-obsidian-brain-dump

# Delete project (if dedicated)
gcloud projects delete slack-brain-dump
```

## Security Best Practices

1. **Use Secret Manager** instead of environment variables for sensitive data:
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

2. **Restrict webhook access** via Slack signing verification (already implemented)

3. **Enable Cloud Armor** if you need DDoS protection

## Next Steps

See `OBSIDIAN_SYNC_SOLUTIONS.md` for detailed strategies on syncing notes from Cloud Run to your local Obsidian vault.
