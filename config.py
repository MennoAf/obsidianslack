"""
Configuration and constants for Slack-Obsidian Brain Dump application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Anthropic Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

# Slack Configuration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_BRAIN_DUMP_CHANNEL_ID = os.getenv("SLACK_BRAIN_DUMP_CHANNEL_ID")

# Obsidian Configuration
OBSIDIAN_VAULT_PATH = Path(os.getenv("OBSIDIAN_VAULT_PATH", ""))
CLAUDE_FOLDER_NAME = os.getenv("CLAUDE_FOLDER_NAME", "40_Claude")
CLAUDE_FOLDER_PATH = OBSIDIAN_VAULT_PATH / CLAUDE_FOLDER_NAME

# Application Configuration
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Obsidian Folder Structure
OBSIDIAN_SUBFOLDERS = [
    "inbox",
    "code",
    "news",
    "ideas",
    "tasks",
    "journal",
    "misc"
]

# Categories
VALID_CATEGORIES = ["code", "news", "ideas", "tasks", "journal", "misc"]

# Tag Generation Rules
TAG_RULES = {
    # Domain-based tagging
    # Add your commonly used domains here
    'domains': {
        'github.com': ['dev/github', 'code'],
        'stackoverflow.com': ['dev/stackoverflow', 'code'],
        'stackexchange.com': ['dev/stackexchange', 'code'],
        
        # News sites
        'theverge.com': ['news/tech', 'source/theverge'],
        'cnn.com': ['news/general', 'source/cnn'],
        'bbc.com': ['news/general', 'source/bbc'],
        'nytimes.com': ['news/general', 'source/nytimes'],
        'techcrunch.com': ['news/tech', 'startups', 'source/techcrunch'],
        'arstechnica.com': ['news/tech', 'source/arstechnica'],
        'wired.com': ['news/tech', 'source/wired'],
        
        # Social & Media
        'youtube.com': ['video', 'source/youtube'],
        'youtu.be': ['video', 'source/youtube'],
        'reddit.com': ['social/reddit'],
        'twitter.com': ['social/twitter'],
        'x.com': ['social/twitter'],
        'linkedin.com': ['social/linkedin', 'professional'],
        
        # Content platforms
        'medium.com': ['articles', 'source/medium'],
        'substack.com': ['articles', 'newsletter', 'source/substack'],
        'dev.to': ['articles', 'code', 'source/devto'],
        
        # Research & Academic
        'arxiv.org': ['research', 'academic', 'source/arxiv'],
        'scholar.google.com': ['research', 'academic'],
        'researchgate.net': ['research', 'academic'],
        
        # Productivity & Collaboration
        'docs.google.com': ['docs', 'collaboration'],
        'notion.so': ['docs', 'source/notion'],
        'figma.com': ['design', 'source/figma'],
        'miro.com': ['design', 'collaboration'],
        'trello.com': ['project-management', 'tasks'],
        'asana.com': ['project-management', 'tasks'],
        
        # Developer tools
        'gitlab.com': ['dev/gitlab', 'code'],
        'bitbucket.org': ['dev/bitbucket', 'code'],
        'npmjs.com': ['dev/npm', 'code'],
        'pypi.org': ['dev/pypi', 'code/python'],
        
        # Documentation
        'readthedocs.io': ['docs', 'technical'],
        'docs.python.org': ['docs', 'code/python'],
        'developer.mozilla.org': ['docs', 'code/javascript', 'web'],
    },
    
    # Code language detection
    'code_languages': {
        'python': ['code/python', 'programming'],
        'javascript': ['code/javascript', 'programming'],
        'typescript': ['code/typescript', 'programming'],
        'java': ['code/java', 'programming'],
        'c++': ['code/cpp', 'programming'],
        'c': ['code/c', 'programming'],
        'rust': ['code/rust', 'programming'],
        'go': ['code/go', 'programming'],
        'ruby': ['code/ruby', 'programming'],
        'php': ['code/php', 'programming'],
        'swift': ['code/swift', 'programming'],
        'kotlin': ['code/kotlin', 'programming'],
        'sql': ['code/sql', 'database'],
        'bash': ['code/bash', 'scripting'],
        'shell': ['code/shell', 'scripting'],
        'powershell': ['code/powershell', 'scripting'],
        'html': ['code/html', 'web'],
        'css': ['code/css', 'web'],
        'react': ['code/react', 'frontend'],
        'vue': ['code/vue', 'frontend'],
        'angular': ['code/angular', 'frontend'],
        'django': ['code/django', 'backend'],
        'flask': ['code/flask', 'backend'],
        'fastapi': ['code/fastapi', 'backend'],
        'node': ['code/nodejs', 'backend'],
        'express': ['code/express', 'backend'],
    },
    
    # Keyword-based tagging
    'keywords': {
        'meeting': ['work/meeting'],
        'call': ['work/meeting'],
        'standup': ['work/meeting', 'agile'],
        'sprint': ['work/sprint', 'agile'],
        'retrospective': ['work/retrospective', 'agile'],
        'api': ['dev/api', 'technical'],
        'bug': ['dev/bug', 'troubleshooting'],
        'issue': ['dev/bug', 'troubleshooting'],
        'error': ['dev/bug', 'troubleshooting'],
        'feature': ['dev/feature', 'product'],
        'design': ['design', 'creative'],
        'deadline': ['urgent', 'tasks'],
        'review': ['work/review'],
        'documentation': ['docs', 'writing'],
        'docs': ['docs', 'writing'],
        'tutorial': ['learning', 'education'],
        'course': ['learning', 'education'],
        'research': ['research', 'learning'],
        'architecture': ['dev/architecture', 'technical'],
        'database': ['database', 'technical'],
        'deployment': ['devops', 'deployment'],
        'ci/cd': ['devops', 'automation'],
        'testing': ['dev/testing', 'quality'],
        'security': ['security', 'technical'],
        'performance': ['performance', 'optimization'],
        'refactor': ['dev/refactoring', 'code-quality'],
        'migration': ['dev/migration', 'technical'],
    },
    
    # Content type detection flags
    'content_types': {
        'contains_code_block': ['code', 'technical'],
        'contains_url': ['reference', 'link'],
        'contains_question': ['question'],
        'contains_list': ['structured'],
    }
}

# Urgency Detection Keywords
URGENCY_KEYWORDS = {
    'high': [
        'urgent', 'asap', 'immediately', 'critical', 'emergency',
        'deadline today', 'due today', 'due tomorrow', 'high priority',
        'blocking', 'blocker', 'production', 'outage', 'down'
    ],
    'medium': [
        'important', 'soon', 'this week', 'priority', 'needed',
        'required', 'should', 'ought to'
    ],
    'low': [
        'eventually', 'someday', 'maybe', 'when possible',
        'nice to have', 'could', 'might'
    ]
}

# Categorization Prompt Template
CATEGORIZATION_PROMPT = """Analyze this Slack message and extract structured information:

MESSAGE:
{slack_message}

THREAD CONTEXT (if reply):
{thread_context}

URLs FOUND:
{urls_found}

Provide a JSON response with:
1. "title": A clear, concise title (3-8 words, no special chars except hyphens and spaces)
2. "category": One of {categories}
3. "base_tags": Array of your suggested tags (domain and code language tags will be added automatically)
4. "has_tasks": boolean - does this contain actionable items?
5. "tasks": array of objects with {{"task": "description", "urgency": "high/medium/low/normal"}}
6. "summary": 1-2 sentence summary of the content
7. "content": The original message with proper markdown formatting, preserving all code blocks, links, and formatting
8. "key_urls": Array of important URLs mentioned (if any) with format {{"url": "...", "description": "..."}}
9. "code_languages": Array of programming languages detected in code blocks (if any)
10. "is_question": boolean - is this asking a question?
11. "detected_urgency": "high", "medium", "low", or "normal" based on language used

IMPORTANT RULES:
- Do NOT summarize the content field - keep the original message verbatim
- Preserve all code blocks with proper markdown formatting (```language)
- Keep all URLs as clickable markdown links [text](url)
- Maintain original formatting, line breaks, and emphasis
- If code blocks exist, detect their language from syntax or context
- Look for urgency indicators: deadlines, "urgent", "asap", "critical", etc.
- Identify tasks even if not in numbered/bullet format

Return ONLY valid JSON, no markdown formatting, no other text.

Example response format:
{{
  "title": "Fix Production API Timeout",
  "category": "tasks",
  "base_tags": ["backend", "api", "troubleshooting"],
  "has_tasks": true,
  "tasks": [
    {{"task": "Debug API connection", "urgency": "high"}},
    {{"task": "Contact AWS support", "urgency": "high"}}
  ],
  "summary": "Production API experiencing timeout errors requiring immediate debugging and AWS support contact.",
  "content": "Original message here...",
  "key_urls": [{{"url": "https://status.aws.amazon.com", "description": "AWS Status Page"}}],
  "code_languages": ["python"],
  "is_question": false,
  "detected_urgency": "high"
}}
"""


def validate_config():
    """Validate that all required configuration is present."""
    errors = []
    
    if not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY is not set")
    
    if not SLACK_BOT_TOKEN:
        errors.append("SLACK_BOT_TOKEN is not set")
    
    if not SLACK_SIGNING_SECRET:
        errors.append("SLACK_SIGNING_SECRET is not set")
    
    if not SLACK_BRAIN_DUMP_CHANNEL_ID:
        errors.append("SLACK_BRAIN_DUMP_CHANNEL_ID is not set")
    
    if not OBSIDIAN_VAULT_PATH or not OBSIDIAN_VAULT_PATH.exists():
        errors.append(
            f"OBSIDIAN_VAULT_PATH is not set or does not exist: "
            f"{OBSIDIAN_VAULT_PATH}"
        )

    if OBSIDIAN_VAULT_PATH and OBSIDIAN_VAULT_PATH.exists():
        if not str(CLAUDE_FOLDER_PATH.resolve()).startswith(
            str(OBSIDIAN_VAULT_PATH.resolve())
        ):
            errors.append(
                "CLAUDE_FOLDER_NAME must not escape OBSIDIAN_VAULT_PATH"
            )
    
    if errors:
        raise ValueError(
            "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        )


def setup_obsidian_folders():
    """Create Obsidian folder structure if it doesn't exist."""
    # Create main Claude folder
    CLAUDE_FOLDER_PATH.mkdir(parents=True, exist_ok=True)
    
    # Create subfolders
    for subfolder in OBSIDIAN_SUBFOLDERS:
        (CLAUDE_FOLDER_PATH / subfolder).mkdir(exist_ok=True)
    
    print(f"✓ Obsidian folders created at: {CLAUDE_FOLDER_PATH}")
