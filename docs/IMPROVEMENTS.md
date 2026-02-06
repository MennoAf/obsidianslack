# ObsidianSlack Improvement Recommendations

Analysis Date: 2026-02-06

## Executive Summary

While ObsidianSlack is functional and secure, there are opportunities to make it more:
1. **Cross-platform compatible** (currently has Unix-only code)
2. **User-customizable** (templates, prompts, tags are hardcoded)
3. **Easy to extend** (plugin architecture for custom processing)

---

## 1. Cross-Platform Issues

### Issue 1.1: Unix-only File Locking ✅ COMPLETED (2026-02-06)

**Location:** `cloud-run/obsidian_writer.py:4`

**Status:** Implemented using cross-platform `filelock` library

**Problem:**
```python
import fcntl  # Unix-only, fails on Windows
```

The file locking for parent note updates uses `fcntl`, which doesn't exist on Windows.

**Impact:**
- Code crashes on Windows when processing thread replies
- Limits deployment options (Windows servers, local Windows development)

**Solution:**
```python
# Cross-platform file locking
import sys

if sys.platform == 'win32':
    import msvcrt

    def lock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)

    def unlock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def lock_file(f):
        fcntl.flock(f, fcntl.LOCK_EX)

    def unlock_file(f):
        fcntl.flock(f, fcntl.LOCK_UN)
```

**Alternative:** Use `filelock` package (cross-platform):
```python
from filelock import FileLock

lock = FileLock(f"{parent_path}.lock")
with lock:
    # Read/modify/write
```

---

## 2. Customization & Flexibility Issues

### Issue 2.1: Hardcoded Prompt Template 🔧 MEDIUM PRIORITY

**Location:** `cloud-run/config.py:210+`

**Problem:**
- The Claude prompt is a 100+ line string hardcoded in `config.py`
- Users can't easily customize without editing code
- Different users have different note-taking styles

**Current:**
```python
CATEGORIZATION_PROMPT = """Analyze this Slack message..."""  # 100+ lines
```

**Solution:** External template file with variable substitution

Create `cloud-run/templates/categorization_prompt.txt`:
```
Analyze this Slack message and extract structured information:

Message: {slack_message}
{thread_context}
{urls_found}

Your categories: {categories}

[rest of template...]
```

Load in config:
```python
def load_prompt_template(template_name='categorization_prompt.txt'):
    template_path = Path(__file__).parent / 'templates' / template_name
    if template_path.exists():
        return template_path.read_text()
    # Fallback to default
    return DEFAULT_CATEGORIZATION_PROMPT

# Allow override via env var
CATEGORIZATION_PROMPT = load_prompt_template(
    os.getenv('PROMPT_TEMPLATE', 'categorization_prompt.txt')
)
```

**Benefits:**
- Users can modify templates without touching code
- Can version control different templates
- Easy A/B testing of prompts

### Issue 2.2: Hardcoded Tag Rules 🔧 MEDIUM PRIORITY

**Location:** `cloud-run/config.py:67-150`

**Problem:**
- Tag rules are Python dictionaries hardcoded in config
- 80+ lines of domain mappings, keywords, language tags
- Users must edit Python code to customize

**Solution:** YAML/JSON configuration file

Create `cloud-run/config/tag_rules.yaml`:
```yaml
domains:
  github.com:
    - dev/github
    - code
  stackoverflow.com:
    - dev/stackoverflow
    - code
  # Users add their own domains

keywords:
  urgent:
    - urgent
    - priority
  bug:
    - bug
    - issue

code_languages:
  python:
    - code/python
  javascript:
    - code/javascript
```

Load in config:
```python
import yaml

def load_tag_rules(config_file='config/tag_rules.yaml'):
    config_path = Path(__file__).parent / config_file
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return DEFAULT_TAG_RULES

TAG_RULES = load_tag_rules(os.getenv('TAG_RULES_FILE', 'config/tag_rules.yaml'))
```

**Benefits:**
- Non-programmers can customize tags
- Easier to share configurations
- Can load different rules per deployment

### Issue 2.3: Hardcoded Note Template 🔧 MEDIUM PRIORITY

**Location:** `cloud-run/obsidian_writer.py:145-168, 170-220`

**Problem:**
- Note structure is hardcoded in Python
- Frontmatter fields are fixed
- Content sections are fixed

**Current Structure (hardcoded):**
```markdown
---
created: ...
title: ...
tags: ...
category: ...
---

# Title

## Summary

## Content

## Tasks

## Key References
```

**Solution:** Jinja2 template system

Create `cloud-run/templates/note_template.md.j2`:
```jinja2
---
created: {{ created }}
title: {{ title }}
tags:
{% for tag in tags %}
  - {{ tag }}
{% endfor %}
category: {{ category }}
source: slack
{% if source_domain %}
source_domain: {{ source_domain }}
{% endif %}
slack_ts: {{ slack_ts }}
status: unprocessed
priority: {{ priority }}
---

# {{ title }}

## Summary
{{ summary }}

## Content
{{ content }}

{% if tasks %}
## Tasks
{% for task in tasks %}
- [ ] {{ task.description }}
{% endfor %}
{% endif %}

{% if key_urls %}
## Key References
{% for url in key_urls %}
- [{{ url.title or url.url }}]({{ url.url }})
{% endfor %}
{% endif %}
```

Usage:
```python
from jinja2 import Environment, FileSystemLoader

template_env = Environment(
    loader=FileSystemLoader('templates')
)

def render_note(template_name, **context):
    template = template_env.get_template(template_name)
    return template.render(**context)

# In obsidian_writer.py
note_content = render_note('note_template.md.j2',
    created=created,
    title=title,
    tags=tags,
    # ... etc
)
```

**Benefits:**
- Users can customize note structure
- Can create multiple template types
- Easy to preview changes

### Issue 2.4: No Plugin/Extension System 💡 LOW PRIORITY

**Problem:**
- All processing logic is monolithic
- Users can't add custom processing steps
- Hard to extend without modifying core code

**Solution:** Simple plugin hook system

Create `cloud-run/plugins/` directory structure:
```
cloud-run/
└── plugins/
    ├── __init__.py
    ├── base.py          # Base plugin class
    └── example/
        └── notion_sync.py  # Example plugin
```

Base plugin interface:
```python
# plugins/base.py
class ProcessorPlugin:
    """Base class for plugins."""

    def on_message_received(self, message_text, metadata):
        """Called when message is received."""
        pass

    def on_note_created(self, note_path, note_content, metadata):
        """Called after note is created."""
        pass

    def on_error(self, error, context):
        """Called when error occurs."""
        pass

# Example plugin
class NotionSyncPlugin(ProcessorPlugin):
    def on_note_created(self, note_path, note_content, metadata):
        # Sync to Notion
        notion_api.create_page(note_content)
```

Plugin loading:
```python
# main.py
def load_plugins():
    plugins = []
    plugin_dir = Path('plugins')
    for file in plugin_dir.glob('*/'):
        if file.is_dir():
            # Import and instantiate plugins
            pass
    return plugins

plugins = load_plugins()

# Call plugin hooks
for plugin in plugins:
    plugin.on_message_received(message_text, metadata)
```

---

## 3. Documentation Improvements

### Issue 3.1: No Customization Guide

**Solution:** Create `CUSTOMIZATION.md` with:
- How to modify templates
- How to add custom tags
- How to change note structure
- Examples of common customizations

### Issue 3.2: No Development Setup Guide

**Solution:** Create `DEVELOPMENT.md` with:
- Local development setup
- Testing without Slack webhooks
- Debugging tips
- How to contribute plugins

---

## 4. Configuration Management Improvements

### Issue 4.1: Mixed Configuration Sources

**Problem:**
- Some config in environment variables
- Some config hardcoded in Python
- No clear hierarchy

**Solution:** Unified configuration system

```python
# config/settings.yaml
slack:
  bot_token: ${SLACK_BOT_TOKEN}  # Load from env
  channel_id: ${SLACK_BRAIN_DUMP_CHANNEL_ID}

obsidian:
  vault_path: ${OBSIDIAN_VAULT_PATH}
  folder_name: ${CLAUDE_FOLDER_NAME:40_Claude}  # Default value
  subfolders:
    - inbox
    - code
    - news

templates:
  prompt: templates/categorization_prompt.txt
  note: templates/note_template.md.j2

plugins:
  enabled:
    - notion_sync
    - slack_reactions
```

---

## 5. Recommended Implementation Priority

### Phase 1: Critical (Do First)
1. ✅ **Cross-platform file locking** - Blocks Windows users
2. 🔧 **External prompt template** - Biggest user pain point

### Phase 2: High Value (Do Soon)
3. 🔧 **YAML tag rules** - Easy win, big flexibility gain
4. 🔧 **Note template system** - Unlocks customization

### Phase 3: Nice to Have (Do Later)
5. 💡 **Plugin system** - Advanced users only
6. 📚 **Better documentation** - Ongoing improvement

---

## 6. Breaking Changes to Consider

### Option A: Backward Compatible (Recommended)
- Keep current behavior as default
- Add new features as opt-in
- Gradual migration path

### Option B: Clean Break (v2.0)
- Restructure configuration completely
- Require migration
- Better long-term design

---

## 7. Example: Complete Customization Flow

**User wants to:**
1. Add custom domains to tag mapping
2. Modify note template to add a "Related Notes" section
3. Change prompt to emphasize action items

**With improvements:**

1. Edit `config/tag_rules.yaml`:
```yaml
domains:
  mycompany.com:
    - work/internal
    - company
```

2. Edit `templates/note_template.md.j2`:
```jinja2
{% if related_notes %}
## Related Notes
{% for note in related_notes %}
- [[{{ note }}]]
{% endfor %}
{% endif %}
```

3. Edit `templates/categorization_prompt.txt`:
```
Pay special attention to action items and deadlines.
Mark urgent items with [URGENT] prefix.
```

**No code changes required!**

---

## 8. Estimated Effort

| Improvement | Effort | Impact | Priority |
|-------------|--------|--------|----------|
| Cross-platform locking | 2 hours | High | P0 |
| External templates (prompts) | 3 hours | High | P1 |
| YAML tag rules | 2 hours | Medium | P1 |
| Jinja2 note templates | 4 hours | High | P1 |
| Plugin system | 8 hours | Medium | P2 |
| Documentation | 4 hours | Medium | P2 |

**Total for Phase 1 & 2:** ~15 hours

---

## 9. Risks & Mitigations

### Risk: Breaking existing deployments
**Mitigation:** Keep defaults, make new features opt-in

### Risk: Complexity creep
**Mitigation:** Start simple, only add what's needed

### Risk: Template validation
**Mitigation:** Add schema validation for YAML/Jinja2

---

## Conclusion

The biggest wins for minimal effort:
1. **Fix cross-platform locking** (2 hrs, unblocks Windows)
2. **External prompt template** (3 hrs, 80% of customization needs)
3. **YAML tag rules** (2 hrs, remaining 20% of customization)

These 3 changes (~7 hours total) would make ObsidianSlack usable for 10x more people with different needs.
