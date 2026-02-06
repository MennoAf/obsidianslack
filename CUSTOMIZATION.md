# ObsidianSlack Customization Guide

This guide explains how to customize ObsidianSlack without modifying Python code. All customizations use external configuration files that can be easily edited, version controlled, and shared.

---

## Table of Contents

1. [Overview](#overview)
2. [Customizing the Claude Prompt](#customizing-the-claude-prompt)
3. [Customizing Tag Rules](#customizing-tag-rules)
4. [Customizing Note Templates](#customizing-note-templates)
5. [Using Plugins](#using-plugins)
6. [Environment Variable Reference](#environment-variable-reference)
7. [Common Customization Examples](#common-customization-examples)
8. [Troubleshooting](#troubleshooting)

---

## Overview

ObsidianSlack provides four layers of customization:

| What | File/Directory | Purpose |
|------|----------------|---------|
| **Prompt Template** | `templates/categorization_prompt.txt` | Control how Claude analyzes messages |
| **Tag Rules** | `config/tag_rules.yaml` | Define automatic tag mappings |
| **Note Template** | `templates/note_template.md.j2` | Control note structure and formatting |
| **Plugins** | `plugins/*.py` | Extend with custom processing hooks |

All files have sensible defaults. The system gracefully falls back if files are missing or invalid.

---

## Customizing the Claude Prompt

### Location
`cloud-run/templates/categorization_prompt.txt`

### What It Does
This prompt tells Claude how to analyze Slack messages and extract structured information like title, category, tags, tasks, and urgency.

### How to Customize

1. **Edit the default template:**
   ```bash
   vim cloud-run/templates/categorization_prompt.txt
   ```

2. **Or use a custom template:**
   ```bash
   # Set environment variable
   export PROMPT_TEMPLATE=/path/to/my_custom_prompt.txt
   ```

### Customization Ideas

#### Emphasize Different Information
Add instructions to focus on specific aspects:
```
ADDITIONAL INSTRUCTIONS:
- Pay special attention to action items and deadlines
- Extract meeting times in ISO format
- Identify people mentioned by @username
- Flag messages containing sensitive information
```

#### Change Category Priorities
Modify the categorization logic:
```
CATEGORY RULES:
- If message contains code: always use "code" category
- If message has deadlines: always use "tasks" category
- Default to "ideas" for brainstorming discussions
```

#### Adjust Output Format
Request additional fields in JSON:
```json
{
  "title": "...",
  "category": "...",
  "mentioned_people": ["@alice", "@bob"],
  "estimated_time": "30 minutes",
  "related_projects": ["project-x"]
}
```

### Template Variables

Your prompt must include these placeholders:
- `{slack_message}` - The actual message text
- `{thread_context}` - Parent message if this is a reply
- `{urls_found}` - List of URLs detected
- `{categories}` - Valid category list

### Testing Your Prompt

1. Make changes to the template
2. Restart the application
3. Send a test message to your brain dump channel
4. Check the generated note

---

## Customizing Tag Rules

### Location
`cloud-run/config/tag_rules.yaml`

### What It Does
Automatically adds tags to notes based on:
- URL domains found in messages
- Programming languages detected
- Keywords in message text
- Content structure (code blocks, lists, etc.)

### How to Customize

1. **Edit the default rules:**
   ```bash
   vim cloud-run/config/tag_rules.yaml
   ```

2. **Or use custom rules:**
   ```bash
   export TAG_RULES_FILE=/path/to/my_tag_rules.yaml
   ```

### File Structure

```yaml
# Domain-based tagging
domains:
  example.com:
    - tag1
    - tag2

# Code language detection
code_languages:
  python:
    - code/python
    - programming

# Keyword-based tagging
keywords:
  meeting:
    - work/meeting

# Content type flags
content_types:
  contains_code_block:
    - code
    - technical
```

### Common Customizations

#### Add Your Company's Internal Sites

```yaml
domains:
  # Your company domains
  mycompany.com:
    - work/internal
    - company

  mycompany.atlassian.net:
    - work/jira
    - project-management

  mycompany.slack.com:
    - work/slack
    - communication
```

#### Add Project-Specific Keywords

```yaml
keywords:
  # Your projects
  project-alpha:
    - projects/alpha
    - priority/high

  project-beta:
    - projects/beta
    - experimental

  # Your team names
  backend-team:
    - team/backend

  frontend-team:
    - team/frontend
```

#### Add Domain-Specific Languages

```yaml
code_languages:
  # Add specialized languages
  solidity:
    - code/solidity
    - blockchain

  hcl:
    - code/hcl
    - terraform
    - infrastructure
```

#### Customize Content Type Tags

```yaml
content_types:
  contains_code_block:
    - technical
    - reference  # Changed from 'code'

  contains_question:
    - needs-answer  # Changed from 'question'
    - follow-up
```

### Tag Best Practices

1. **Use hierarchical tags** - `work/meeting` instead of `work-meeting`
2. **Be consistent** - Pick a naming convention and stick to it
3. **Don't over-tag** - 3-7 tags per note is ideal
4. **Use namespaces** - Group related tags (`code/python`, `code/javascript`)

---

## Customizing Note Templates

### Location
`cloud-run/templates/note_template.md.j2`

### What It Does
Controls the structure and formatting of generated markdown notes, including:
- YAML frontmatter fields
- Section headers
- Content layout
- Task formatting
- Link formatting

### How to Customize

1. **Edit the default template:**
   ```bash
   vim cloud-run/templates/note_template.md.j2
   ```

2. **Or use a custom template:**
   ```bash
   export NOTE_TEMPLATE=my_note_template.md.j2
   export NOTE_TEMPLATE_DIR=/path/to/templates/
   ```

### Template Syntax (Jinja2)

```jinja2
{# Comments look like this #}

{{ variable }}              {# Output variable #}
{% if condition %}...{% endif %}   {# Conditional #}
{% for item in list %}...{% endfor %}  {# Loop #}
```

### Available Variables

| Variable | Type | Description |
|----------|------|-------------|
| `created` | string | Timestamp in ISO format |
| `title` | string | Note title |
| `tags` | list | List of tag strings |
| `category` | string | Note category |
| `source_domain` | string | Domain of first URL (optional) |
| `slack_ts` | string | Slack message timestamp |
| `slack_thread_ts` | string | Thread timestamp (optional) |
| `priority` | string | Priority level (high/medium/low/normal) |
| `parent_note` | string | Parent note name (optional) |
| `summary` | string | Brief summary |
| `content` | string | Main message content |
| `has_tasks` | boolean | Whether note has tasks |
| `tasks` | list | Task objects with `.task` and `.urgency` |
| `key_urls` | list | URL objects with `.url` and `.description` |

### Common Customizations

#### Add Custom Frontmatter Fields

```jinja2
---
created: {{ created }}
title: {{ title }}
tags:
{%- for tag in tags %}
  - {{ tag }}
{%- endfor %}
category: {{ category }}
priority: {{ priority }}

{# Add your custom fields #}
author: Jason
vault: brain-dump
reviewed: false
---
```

#### Change Section Order

```jinja2
# {{ title }}

{# Tasks first instead of summary #}
{% if has_tasks and tasks %}
## 🎯 Action Items
{%- for task_obj in tasks %}
- [ ] {{ task_obj.task }} {% if task_obj.urgency == 'high' %}⚡{% endif %}
{%- endfor %}
{% endif %}

{# Then summary #}
{% if summary %}
## 📝 Summary
{{ summary }}
{% endif %}

{# Then content #}
## 💬 Content
{{ content }}
```

#### Add Custom Emoji/Formatting

```jinja2
## 🔥 Priority: {{ priority|upper }}

{% if priority == 'high' %}
> ⚠️ **HIGH PRIORITY** - Address this soon!
{% elif priority == 'medium' %}
> 📌 Medium priority - Keep on radar
{% endif %}
```

#### Create Different Templates by Category

You can create multiple templates and switch between them:

**templates/task_note.md.j2** (for task-heavy notes):
```jinja2
---
title: {{ title }}
category: {{ category }}
due_date:
status: todo
---

# ✅ {{ title }}

## Tasks
{%- for task_obj in tasks %}
- [ ] {{ task_obj.task }}
{%- endfor %}

## Context
{{ content }}
```

Then set: `export NOTE_TEMPLATE=task_note.md.j2`

#### Add Dataview Fields (Obsidian Plugin)

```jinja2
---
title: {{ title }}
tags: {{ tags }}
category: {{ category }}
priority: {{ priority }}

{# Dataview-compatible fields #}
created:: {{ created }}
priority:: {{ priority }}
{%- if has_tasks %}
task-count:: {{ tasks|length }}
{%- endif %}
---
```

---

## Using Plugins

### What Are Plugins?

Plugins let you extend ObsidianSlack functionality without modifying core code. They use hooks that run at different stages of message processing.

### Quick Start

#### 1. Create a Plugin

```python
# cloud-run/plugins/my_plugin.py
from plugins.base import ProcessorPlugin
import logging

logger = logging.getLogger(__name__)


class MyPlugin(ProcessorPlugin):
    """My custom plugin."""

    def on_note_created(self, note_path, note_content, metadata):
        """Called after a note is created."""
        logger.info(f"New note: {metadata['title']}")
        # Add your custom logic here
```

#### 2. Plugin Loads Automatically

Place your plugin in `cloud-run/plugins/` and it loads automatically on startup.

### Available Hooks

Plugins can implement any of these hooks (all optional):

| Hook | When It Runs | Use Cases |
|------|--------------|-----------|
| `on_message_received` | Message received from Slack | Filter messages, pre-process text |
| `on_processing_start` | Before Claude processes | Modify input, add context |
| `on_processing_complete` | After Claude processes | Modify output, add tags |
| `on_note_created` | After note written | Sync to services, add reactions |
| `on_error` | When error occurs | Custom error handling |

### Example: Sync to Notion

```python
from plugins.base import ProcessorPlugin
import requests
import os


class NotionSyncPlugin(ProcessorPlugin):
    """Sync notes to Notion database."""

    def __init__(self):
        super().__init__()
        self.notion_api_key = os.getenv('NOTION_API_KEY')
        self.database_id = os.getenv('NOTION_DATABASE_ID')

    def on_note_created(self, note_path, note_content, metadata):
        """Create a Notion page for each note."""
        if not self.notion_api_key:
            return

        # Create Notion page
        headers = {
            'Authorization': f'Bearer {self.notion_api_key}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }

        data = {
            'parent': {'database_id': self.database_id},
            'properties': {
                'Title': {
                    'title': [{'text': {'content': metadata['title']}}]
                },
                'Category': {
                    'select': {'name': metadata['category']}
                },
                'Tags': {
                    'multi_select': [{'name': tag} for tag in metadata['tags']]
                }
            }
        }

        response = requests.post(
            'https://api.notion.com/v1/pages',
            headers=headers,
            json=data
        )

        if response.ok:
            logger.info(f"Synced to Notion: {metadata['title']}")
```

### Example Plugins

See `cloud-run/plugins/examples/` for complete examples:

- **`logging_plugin.py`** - Enhanced logging and analytics
- **`filter_plugin.py`** - Filter messages by patterns
- **`slack_reaction_plugin.py`** - Custom Slack reactions

To enable an example:
```bash
mv cloud-run/plugins/examples/logging_plugin.py cloud-run/plugins/
```

### Configuration

**Disable all plugins:**
```bash
export PLUGINS_ENABLED=false
```

**Configure plugin via environment:**
```python
# In your plugin
def __init__(self):
    super().__init__()
    self.api_key = os.getenv('MY_PLUGIN_API_KEY')
```

### Full Documentation

See `cloud-run/plugins/README.md` for complete plugin documentation:
- All hook signatures and parameters
- Best practices
- Advanced examples
- Troubleshooting

---

## Environment Variable Reference

### Prompt Template

| Variable | Default | Description |
|----------|---------|-------------|
| `PROMPT_TEMPLATE` | `templates/categorization_prompt.txt` | Path to Claude prompt template |

### Tag Rules

| Variable | Default | Description |
|----------|---------|-------------|
| `TAG_RULES_FILE` | `config/tag_rules.yaml` | Path to tag rules YAML file |

### Note Template

| Variable | Default | Description |
|----------|---------|-------------|
| `NOTE_TEMPLATE` | `note_template.md.j2` | Template filename |
| `NOTE_TEMPLATE_DIR` | `cloud-run/templates/` | Template directory path |

### Plugins

| Variable | Default | Description |
|----------|---------|-------------|
| `PLUGINS_ENABLED` | `true` | Set to `false` to disable all plugins |

### Setting Environment Variables

**In .env file:**
```bash
PROMPT_TEMPLATE=/custom/path/my_prompt.txt
TAG_RULES_FILE=/custom/path/my_tags.yaml
NOTE_TEMPLATE=custom_note.md.j2
```

**In Cloud Run deployment:**
```bash
gcloud run services update obsidian-slack \
  --set-env-vars "PROMPT_TEMPLATE=/path/to/prompt.txt"
```

**In Docker:**
```bash
docker run --env-file .env \
  -e NOTE_TEMPLATE=custom.md.j2 \
  obsidian-slack
```

---

## Common Customization Examples

### Example 1: Work-Focused Setup

**Tag Rules (config/tag_rules.yaml):**
```yaml
keywords:
  okr:
    - work/okrs
    - goals

  quarterly:
    - planning/quarterly

  1-on-1:
    - work/1-on-1
    - management
```

**Prompt Additions:**
```
Focus on extracting:
- OKR references and progress updates
- Action items with owners (@person)
- Deadlines and milestones
```

### Example 2: Learning & Research

**Tag Rules:**
```yaml
domains:
  coursera.org:
    - learning/coursera
    - education

  udemy.com:
    - learning/udemy
    - education

keywords:
  learn:
    - learning
    - personal-development

  tutorial:
    - learning/tutorial
    - reference
```

**Note Template:**
```jinja2
# 📚 {{ title }}

{% if summary %}
## What I Learned
{{ summary }}
{% endif %}

## Notes
{{ content }}

{% if key_urls %}
## Resources
{%- for url_obj in key_urls %}
- [ ] Review: [{{ url_obj.description }}]({{ url_obj.url }})
{%- endfor %}
{% endif %}
```

### Example 3: Developer Brain Dump

**Tag Rules:**
```yaml
domains:
  stackoverflow.com:
    - dev/stackoverflow
    - solutions

  github.com:
    - dev/github
    - code

keywords:
  bug:
    - dev/bug
    - troubleshooting
    - priority/high

  refactor:
    - dev/refactor
    - tech-debt
```

**Note Template:**
```jinja2
---
title: {{ title }}
tags: {{ tags }}
category: {{ category }}
priority: {{ priority }}
{%- if has_tasks %}
has-action-items: true
{%- endif %}
---

# 🔧 {{ title }}

{% if summary %}
**TL;DR:** {{ summary }}
{% endif %}

## Details
{{ content }}

{% if has_tasks %}
## Action Items
{%- for task in tasks %}
- [ ] {{ task.task }} {%- if task.urgency == 'high' %} 🔥{% endif %}
{%- endfor %}
{% endif %}

{% if key_urls %}
## Links
{%- for url in key_urls %}
- [{{ url.description }}]({{ url.url }})
{%- endfor %}
{% endif %}

---
*Captured from Slack on {{ created }}*
```

---

## Troubleshooting

### Prompt Template Issues

**Problem:** "Using default prompt template" message

**Solutions:**
1. Check file exists: `ls cloud-run/templates/categorization_prompt.txt`
2. Check file permissions: `chmod 644 cloud-run/templates/categorization_prompt.txt`
3. Check environment variable: `echo $PROMPT_TEMPLATE`

**Problem:** Claude returns unexpected output

**Solutions:**
1. Verify your prompt asks for JSON output
2. Check you're using the required placeholders: `{slack_message}`, `{categories}`, etc.
3. Test with the default prompt to isolate the issue

### Tag Rules Issues

**Problem:** "Using default tag rules" message

**Solutions:**
1. Check file exists: `ls cloud-run/config/tag_rules.yaml`
2. Validate YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('cloud-run/config/tag_rules.yaml'))"`
3. Check environment variable: `echo $TAG_RULES_FILE`

**Problem:** Tags not being applied

**Solutions:**
1. Check YAML structure matches expected format (domains/code_languages/keywords/content_types)
2. Verify tag rules use lowercase domains
3. Check tag syntax (no special characters except `/` and `-`)

### Note Template Issues

**Problem:** "Using fallback note generation" message

**Solutions:**
1. Check template directory exists: `ls cloud-run/templates/`
2. Check template file exists: `ls cloud-run/templates/note_template.md.j2`
3. Check environment variables:
   ```bash
   echo $NOTE_TEMPLATE
   echo $NOTE_TEMPLATE_DIR
   ```

**Problem:** Template rendering errors

**Solutions:**
1. Validate Jinja2 syntax (matching `{% %}` tags, proper variable names)
2. Check variable names match documented list
3. Test template rendering:
   ```python
   from jinja2 import Environment, FileSystemLoader
   env = Environment(loader=FileSystemLoader('templates'))
   template = env.get_template('note_template.md.j2')
   # Test render
   ```

**Problem:** Notes have unexpected formatting

**Solutions:**
1. Check for extra whitespace in template
2. Use `{%- %}` and `{%+ %}` for whitespace control
3. Review Jinja2 `trim_blocks` and `lstrip_blocks` settings

### General Debugging

**Enable detailed logging:**
```bash
# In your .env file
DEBUG_MODE=true
```

**Check application logs:**
```bash
# Local
tail -f brain_dump.log

# Cloud Run
gcloud run logs read obsidian-slack --limit 50
```

**Test configuration loading:**
```python
# In Python shell
import config
print(config.CATEGORIZATION_PROMPT[:100])  # First 100 chars
print(config.TAG_RULES.keys())  # Tag rule sections
```

---

## Next Steps

1. **Start small** - Make one change at a time
2. **Test thoroughly** - Send test messages after each change
3. **Version control** - Commit your customizations to git
4. **Share configs** - Export your customizations for others:
   ```bash
   tar -czf my-obsidian-config.tar.gz \
     cloud-run/templates/ \
     cloud-run/config/
   ```

---

## Support

- **Documentation:** See `README.md`, `CLAUDE.md`, `IMPROVEMENTS.md`
- **Issues:** Report bugs at your repository's issue tracker
- **Examples:** Check `IMPROVEMENTS.md` for more customization ideas

---

**Last Updated:** 2026-02-06
