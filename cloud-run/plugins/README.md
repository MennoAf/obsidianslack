# ObsidianSlack Plugin System

Extend ObsidianSlack functionality with custom processing hooks without modifying core code.

## Quick Start

### 1. Create a Plugin

Create a Python file in the `plugins/` directory:

```python
# plugins/my_plugin.py
from plugins.base import ProcessorPlugin
import logging

logger = logging.getLogger(__name__)


class MyPlugin(ProcessorPlugin):
    """Your custom plugin."""

    def __init__(self):
        super().__init__()
        logger.info("MyPlugin initialized")

    def on_note_created(self, note_path, note_content, metadata):
        """Called after a note is created."""
        logger.info(f"New note created: {note_path}")
        # Your custom logic here
```

### 2. Plugin is Auto-Loaded

Plugins are automatically discovered and loaded on startup. No configuration needed!

### 3. Disable Plugins (Optional)

To disable all plugins:
```bash
export PLUGINS_ENABLED=false
```

---

## Available Hooks

All hooks are **optional** - implement only what you need.

### `on_message_received(message_text, metadata)`

Called when a Slack message is received, before any processing.

**Use cases:**
- Filter/skip certain messages
- Log incoming messages
- Pre-process message text

**Parameters:**
- `message_text` (str): Raw message from Slack
- `metadata` (dict): `user_id`, `channel_id`, `slack_ts`, `thread_ts`, `is_reply`

**Return:**
- `None` or `{}`: Continue processing normally
- `{'skip': True}`: Skip processing this message

**Example:**
```python
def on_message_received(self, message_text, metadata):
    # Skip messages from specific user
    if metadata.get('user_id') == 'U12345':
        return {'skip': True}

    # Log all messages
    logger.info(f"Message from {metadata['user_id']}: {message_text[:50]}...")
```

---

### `on_processing_start(message_text, metadata)`

Called before sending the message to Claude for processing.

**Use cases:**
- Modify message before Claude sees it
- Add custom context
- Track processing start time

**Parameters:**
- `message_text` (str): Message text that will be sent to Claude
- `metadata` (dict): Message metadata

**Return:**
- `None`: Continue normally
- `dict`: Can include modified `message_text` or `metadata`

**Example:**
```python
def on_processing_start(self, message_text, metadata):
    # Add timestamp for duration tracking
    metadata['start_time'] = datetime.now()

    # Could modify message text if needed
    # return {'message_text': modified_text}
```

---

### `on_processing_complete(processed_data, original_message, metadata)`

Called after Claude has processed the message.

**Use cases:**
- Modify Claude's output
- Log processing results
- Calculate processing duration

**Parameters:**
- `processed_data` (dict): Structured data from Claude (title, category, tags, etc.)
- `original_message` (str): Original message text
- `metadata` (dict): Message metadata

**Return:**
- `None`: Continue normally
- `dict`: Can include modified `processed_data`

**Example:**
```python
def on_processing_complete(self, processed_data, original_message, metadata):
    # Log processing stats
    if 'start_time' in metadata:
        duration = datetime.now() - metadata['start_time']
        logger.info(f"Processed in {duration.total_seconds()}s")

    # Could add custom tags
    # processed_data['base_tags'].append('custom-tag')
    # return {'processed_data': processed_data}
```

---

### `on_note_created(note_path, note_content, metadata)`

Called after an Obsidian note has been written to disk.

**Use cases:**
- Sync to other services (Notion, GitHub, etc.)
- Add custom Slack reactions
- Send notifications
- Update databases

**Parameters:**
- `note_path` (str): Full path to the created `.md` file
- `note_content` (str): Complete note content (frontmatter + body)
- `metadata` (dict): `title`, `category`, `tags`, `has_tasks`, `channel_id`, `slack_ts`

**Return:** None

**Example:**
```python
def on_note_created(self, note_path, note_content, metadata):
    # Add custom Slack reaction based on category
    if metadata['category'] == 'tasks':
        # slack_client.reactions_add(reaction='ballot_box_with_check')
        pass

    # Sync to Notion
    # notion_api.create_page(title=metadata['title'], content=note_content)
```

---

### `on_error(error, context)`

Called when an error occurs during processing.

**Use cases:**
- Custom error logging
- Send error notifications
- Retry logic

**Parameters:**
- `error` (Exception): The exception that occurred
- `context` (dict): Where the error occurred (`stage`, `message`, etc.)

**Return:** None

**Example:**
```python
def on_error(self, error, context):
    logger.error(f"Error in {context.get('stage')}: {error}")

    # Send to error tracking service
    # sentry.capture_exception(error)
```

---

## Plugin Structure

### Simple Plugin (Single File)

```
plugins/
└── my_plugin.py       # Plugin class inside
```

### Complex Plugin (Package)

```
plugins/
└── my_plugin/
    ├── __init__.py    # Plugin class here
    ├── config.py      # Plugin config
    └── helpers.py     # Helper functions
```

---

## Plugin Examples

See `plugins/examples/` for complete examples:

- **`logging_plugin.py`** - Enhanced logging and analytics
- **`filter_plugin.py`** - Filter messages by patterns/users
- **`slack_reaction_plugin.py`** - Add custom Slack reactions

To enable an example, move it out of `examples/`:
```bash
mv plugins/examples/logging_plugin.py plugins/
```

---

## Best Practices

### 1. Error Handling

Always wrap plugin logic in try/except:
```python
def on_note_created(self, note_path, note_content, metadata):
    try:
        # Your logic here
        pass
    except Exception as e:
        logger.error(f"Error in {self.name}: {e}")
```

### 2. Logging

Use the logger for debugging:
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Detailed info")
logger.info("Important events")
logger.warning("Warnings")
logger.error("Errors")
```

### 3. Performance

Keep hooks fast - they run on every message:
```python
# Good: Quick check
def on_message_received(self, message_text, metadata):
    if len(message_text) < 10:
        return {'skip': True}

# Bad: Slow API call
def on_message_received(self, message_text, metadata):
    response = requests.get('https://slow-api.com')  # Blocks processing!
```

### 4. Configuration

Use environment variables for plugin config:
```python
def __init__(self):
    super().__init__()
    self.api_key = os.getenv('MY_PLUGIN_API_KEY')
    self.enabled = os.getenv('MY_PLUGIN_ENABLED', 'true').lower() == 'true'
```

---

## Troubleshooting

### Plugin Not Loading

**Check logs for:**
```
✓ Loaded 1 plugin(s): MyPlugin
```

**Common issues:**
- Plugin file in `examples/` directory (move it to `plugins/`)
- Plugin class doesn't inherit from `ProcessorPlugin`
- Syntax errors in plugin file
- Missing `__init__.py` in plugin package

### Plugin Not Running

**Check:**
1. Plugin is enabled: `plugin.enabled = True`
2. Hook method name is correct (e.g., `on_note_created`, not `note_created`)
3. No errors in plugin code (check logs)

### Disable All Plugins

```bash
export PLUGINS_ENABLED=false
```

### Disable Specific Plugin

```python
# In your plugin's __init__
def __init__(self):
    super().__init__()
    self.enabled = False  # Disable this plugin
```

---

## Advanced: Plugin State

Plugins can maintain state across messages:

```python
class StatsPlugin(ProcessorPlugin):
    def __init__(self):
        super().__init__()
        self.message_count = 0
        self.notes_created = 0

    def on_message_received(self, message_text, metadata):
        self.message_count += 1

    def on_note_created(self, note_path, note_content, metadata):
        self.notes_created += 1
        logger.info(f"Stats: {self.message_count} messages, {self.notes_created} notes")
```

---

## Plugin Ideas

- **Notion Sync**: Sync notes to Notion database
- **GitHub Issues**: Create GitHub issues from task notes
- **Email Digest**: Daily email summary of notes created
- **Slack Summary**: Post daily summaries to Slack
- **Analytics**: Track message volume, categories, response times
- **Custom Tags**: Add project-specific or team-specific tags
- **Duplicate Detection**: Check for similar existing notes
- **Auto-Archive**: Move old notes to archive folders
- **URL Expansion**: Fetch page titles for URLs
- **Image OCR**: Extract text from shared images

---

## Need Help?

- See example plugins in `plugins/examples/`
- Check base class: `plugins/base.py`
- Review plugin loader: `plugins/plugin_loader.py`
- Read main docs: `../CUSTOMIZATION.md`
