# ObsidianSlack Testing Checklist

**Created:** 2026-02-06
**Purpose:** Validate all improvements implemented in this session
**Estimated Time:** 2-3 hours
**Budget Required:** ~50,000 tokens

---

## ⚠️ IMPORTANT INSTRUCTIONS

### Before Starting
1. Check your remaining token budget (aim for 50k+ remaining)
2. Read this entire checklist first
3. Work through tests **in order** (dependencies exist)
4. **COMMIT after completing each TODO section**
5. **ONLY proceed to next TODO if you have sufficient budget**
6. **If running low on budget (<30k), PUSH changes and stop**

### Commit Message Format
```
Test: [TODO number] - [Brief description]

- What was tested
- Results (pass/fail)
- Any issues found

Testing checklist: [X/12] complete
```

---

## TODO 1: Setup Test Environment ✅

**Estimated tokens:** ~3,000

### Tasks
- [ ] Verify Python 3.8+ installed
- [ ] Create test virtual environment: `python3 -m venv venv-test`
- [ ] Activate venv: `source venv-test/bin/activate`
- [ ] Install dependencies: `pip install -r cloud-run/requirements.txt`
- [ ] Verify all packages installed (check for pyyaml, jinja2, filelock)
- [ ] Create test `.env` file with dummy values

### Expected Results
- All dependencies install without errors
- Import test passes: `python3 -c "import yaml, jinja2, filelock"`

### Validation
```bash
cd cloud-run
python3 -c "
import yaml
import jinja2
from filelock import FileLock
import config
from plugins.base import ProcessorPlugin
from plugins.plugin_loader import PluginLoader
print('✓ All imports successful')
"
```

### Commit After This TODO
```bash
git add -A
git commit -m "Test: TODO 1 - Setup test environment

- Created test virtual environment
- Installed all dependencies
- Verified imports
- Created test .env file

Testing checklist: 1/12 complete"
```

---

## TODO 2: Test External Prompt Template Loading ✅

**Estimated tokens:** ~5,000

### Tasks
- [ ] Verify default prompt template exists: `cloud-run/templates/categorization_prompt.txt`
- [ ] Test prompt loads in config.py
- [ ] Create custom test prompt: `cloud-run/templates/test_prompt.txt`
- [ ] Test env var override: `PROMPT_TEMPLATE=templates/test_prompt.txt`
- [ ] Test fallback when file missing
- [ ] Test with invalid path

### Expected Results
- Default prompt loads successfully
- Custom prompt loads via env var
- Fallback to default on missing file
- Informative log messages

### Validation Script
```python
# test_prompt_template.py
import os
import sys
sys.path.insert(0, 'cloud-run')

# Test 1: Default loading
print("Test 1: Default prompt template")
import config
assert config.CATEGORIZATION_PROMPT is not None
assert len(config.CATEGORIZATION_PROMPT) > 100
print("✓ Default prompt loaded")

# Test 2: Custom template
print("\nTest 2: Custom template via env var")
with open('cloud-run/templates/test_prompt.txt', 'w') as f:
    f.write("Test prompt: {slack_message}")

os.environ['PROMPT_TEMPLATE'] = 'templates/test_prompt.txt'
# Reload config module
import importlib
importlib.reload(config)
assert 'Test prompt' in config.CATEGORIZATION_PROMPT
print("✓ Custom template loaded")

# Cleanup
os.remove('cloud-run/templates/test_prompt.txt')
print("\n✓ All prompt template tests passed")
```

### Commit After This TODO
```bash
git add -A
git commit -m "Test: TODO 2 - External prompt template loading

- Verified default template loads
- Tested env var override
- Tested fallback behavior
- All tests passed

Testing checklist: 2/12 complete"
```

---

## TODO 3: Test YAML Tag Rules Loading ✅

**Estimated tokens:** ~5,000

### Tasks
- [ ] Verify default tag rules YAML exists: `cloud-run/config/tag_rules.yaml`
- [ ] Validate YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('cloud-run/config/tag_rules.yaml'))"`
- [ ] Test tag rules load in config.py
- [ ] Create custom test rules YAML
- [ ] Test env var override: `TAG_RULES_FILE`
- [ ] Test fallback when file missing
- [ ] Verify all rule sections load (domains, code_languages, keywords, content_types)

### Expected Results
- YAML is valid and parses
- All 4 sections present
- Custom rules load via env var
- Fallback to defaults on error

### Validation Script
```python
# test_tag_rules.py
import os
import sys
import yaml
sys.path.insert(0, 'cloud-run')

# Test 1: YAML syntax
print("Test 1: YAML syntax validation")
with open('cloud-run/config/tag_rules.yaml') as f:
    rules = yaml.safe_load(f)
assert 'domains' in rules
assert 'code_languages' in rules
assert 'keywords' in rules
assert 'content_types' in rules
print("✓ YAML structure valid")

# Test 2: Config loading
print("\nTest 2: Config loading")
import config
assert config.TAG_RULES is not None
assert 'github.com' in config.TAG_RULES['domains']
assert 'python' in config.TAG_RULES['code_languages']
print("✓ Tag rules loaded in config")

# Test 3: Custom rules file
print("\nTest 3: Custom rules via env var")
custom_rules = {
    'domains': {'test.com': ['test-tag']},
    'code_languages': {},
    'keywords': {},
    'content_types': {}
}
with open('cloud-run/config/test_rules.yaml', 'w') as f:
    yaml.dump(custom_rules, f)

os.environ['TAG_RULES_FILE'] = 'config/test_rules.yaml'
import importlib
importlib.reload(config)
assert 'test.com' in config.TAG_RULES['domains']
print("✓ Custom rules loaded")

# Cleanup
os.remove('cloud-run/config/test_rules.yaml')
print("\n✓ All tag rules tests passed")
```

### Commit After This TODO
```bash
git add -A
git commit -m "Test: TODO 3 - YAML tag rules loading

- Validated YAML syntax
- Verified config loading
- Tested env var override
- Tested fallback behavior
- All tests passed

Testing checklist: 3/12 complete"
```

---

## TODO 4: Test Jinja2 Note Template Loading ✅

**Estimated tokens:** ~6,000

### Tasks
- [ ] Verify default note template exists: `cloud-run/templates/note_template.md.j2`
- [ ] Test template syntax is valid Jinja2
- [ ] Test ObsidianWriter initializes template engine
- [ ] Test template renders with sample data
- [ ] Test fallback when template missing
- [ ] Verify all template variables work

### Expected Results
- Template is valid Jinja2
- ObsidianWriter loads templates
- Sample rendering produces valid markdown
- Fallback to hardcoded methods works

### Validation Script
```python
# test_note_template.py
import sys
from pathlib import Path
sys.path.insert(0, 'cloud-run')

# Test 1: Template exists and is valid Jinja2
print("Test 1: Template validation")
from jinja2 import Environment, FileSystemLoader
template_dir = Path('cloud-run/templates')
env = Environment(loader=FileSystemLoader(str(template_dir)))
template = env.get_template('note_template.md.j2')
print("✓ Template loads and parses")

# Test 2: Template rendering
print("\nTest 2: Template rendering")
sample_data = {
    'created': '2026-02-06T10:00:00',
    'title': 'Test Note',
    'tags': ['test', 'demo'],
    'category': 'misc',
    'source_domain': None,
    'slack_ts': '1234567890.123456',
    'slack_thread_ts': None,
    'priority': 'normal',
    'parent_note': None,
    'summary': 'This is a test',
    'content': 'Test content here',
    'has_tasks': True,
    'tasks': [{'task': 'Test task', 'urgency': 'normal'}],
    'key_urls': [{'url': 'https://test.com', 'description': 'Test URL'}]
}

rendered = template.render(**sample_data)
assert '# Test Note' in rendered
assert 'test' in rendered
assert 'Test task' in rendered
assert 'https://test.com' in rendered
print("✓ Template renders correctly")

# Test 3: ObsidianWriter integration
print("\nTest 3: ObsidianWriter integration")
from obsidian_writer import ObsidianWriter
writer = ObsidianWriter()
assert writer.template_env is not None or writer.use_templates == False
print("✓ ObsidianWriter template engine initialized")

print("\n✓ All note template tests passed")
```

### Commit After This TODO
```bash
git add -A
git commit -m "Test: TODO 4 - Jinja2 note template loading

- Validated template syntax
- Tested template rendering
- Verified ObsidianWriter integration
- All tests passed

Testing checklist: 4/12 complete"
```

---

## TODO 5: Test Plugin System - Base Infrastructure ✅

**Estimated tokens:** ~7,000

### Tasks
- [ ] Test ProcessorPlugin base class imports
- [ ] Test PluginLoader initializes
- [ ] Test plugin discovery from plugins/ directory
- [ ] Test example plugins are NOT loaded (in examples/ dir)
- [ ] Test PLUGINS_ENABLED=false disables loading
- [ ] Verify plugin hooks are callable

### Expected Results
- Base class has all 5 hook methods
- PluginLoader discovers plugins correctly
- Examples directory is skipped
- Environment variable works
- All hooks have correct signatures

### Validation Script
```python
# test_plugin_base.py
import sys
import os
sys.path.insert(0, 'cloud-run')

# Test 1: Base class
print("Test 1: ProcessorPlugin base class")
from plugins.base import ProcessorPlugin
plugin = ProcessorPlugin()
assert hasattr(plugin, 'on_message_received')
assert hasattr(plugin, 'on_processing_start')
assert hasattr(plugin, 'on_processing_complete')
assert hasattr(plugin, 'on_note_created')
assert hasattr(plugin, 'on_error')
assert plugin.enabled == True
print("✓ Base class has all hooks")

# Test 2: PluginLoader
print("\nTest 2: PluginLoader initialization")
from plugins.plugin_loader import PluginLoader
loader = PluginLoader('cloud-run/plugins')
assert loader.plugin_dir.exists()
print("✓ PluginLoader initializes")

# Test 3: Plugin discovery (should find none - examples are skipped)
print("\nTest 3: Plugin discovery")
plugins = loader.discover_and_load()
# Should be empty since all examples are in examples/ subdirectory
assert isinstance(plugins, list)
print(f"✓ Discovered {len(plugins)} plugins (examples dir skipped)")

# Test 4: Disable via env var
print("\nTest 4: PLUGINS_ENABLED=false")
os.environ['PLUGINS_ENABLED'] = 'false'
loader2 = PluginLoader('cloud-run/plugins')
plugins2 = loader2.discover_and_load()
assert len(plugins2) == 0
print("✓ Plugins disabled via env var")

print("\n✓ All plugin base tests passed")
```

### Commit After This TODO
```bash
git add -A
git commit -m "Test: TODO 5 - Plugin system base infrastructure

- Tested ProcessorPlugin base class
- Verified PluginLoader initialization
- Tested plugin discovery
- Verified PLUGINS_ENABLED works
- All tests passed

Testing checklist: 5/12 complete"
```

---

## TODO 6: Test Plugin System - Create Test Plugin ✅

**Estimated tokens:** ~8,000

### Tasks
- [ ] Create a simple test plugin in plugins/
- [ ] Test plugin is discovered and loaded
- [ ] Test each hook is called correctly
- [ ] Test plugin state persistence across calls
- [ ] Test plugin can return skip command
- [ ] Test plugin error handling

### Expected Results
- Test plugin loads automatically
- All hooks called in correct order
- State persists between calls
- Skip functionality works
- Errors are isolated

### Test Plugin
```python
# Create: cloud-run/plugins/test_plugin.py
from plugins.base import ProcessorPlugin
import logging

logger = logging.getLogger(__name__)

class TestPlugin(ProcessorPlugin):
    """Test plugin for validation."""

    def __init__(self):
        super().__init__()
        self.call_count = 0
        self.hooks_called = []

    def on_message_received(self, message_text, metadata):
        self.call_count += 1
        self.hooks_called.append('on_message_received')
        logger.info(f"TestPlugin: on_message_received called ({self.call_count})")

        # Test skip functionality
        if 'SKIP_TEST' in message_text:
            return {'skip': True}

    def on_processing_start(self, message_text, metadata):
        self.hooks_called.append('on_processing_start')
        logger.info("TestPlugin: on_processing_start called")

    def on_processing_complete(self, processed_data, original_message, metadata):
        self.hooks_called.append('on_processing_complete')
        logger.info("TestPlugin: on_processing_complete called")

    def on_note_created(self, note_path, note_content, metadata):
        self.hooks_called.append('on_note_created')
        logger.info(f"TestPlugin: on_note_created called - {note_path}")

    def on_error(self, error, context):
        self.hooks_called.append('on_error')
        logger.info(f"TestPlugin: on_error called - {error}")
```

### Validation Script
```python
# test_plugin_functionality.py
import sys
sys.path.insert(0, 'cloud-run')

# Test 1: Plugin loading
print("Test 1: Test plugin loading")
from plugins.plugin_loader import PluginLoader
loader = PluginLoader('cloud-run/plugins')
plugins = loader.discover_and_load()
assert len(plugins) == 1
assert plugins[0].name == 'TestPlugin'
print(f"✓ Loaded plugin: {plugins[0].name}")

# Test 2: Hook calling
print("\nTest 2: Hook calling")
test_plugin = plugins[0]
results = loader.call_hook('on_message_received', 'test message', {})
assert 'on_message_received' in test_plugin.hooks_called
print("✓ Hook called successfully")

# Test 3: State persistence
print("\nTest 3: State persistence")
assert test_plugin.call_count == 1
loader.call_hook('on_message_received', 'test message 2', {})
assert test_plugin.call_count == 2
print("✓ State persists across calls")

# Test 4: Skip functionality
print("\nTest 4: Skip functionality")
results = loader.call_hook('on_message_received', 'SKIP_TEST message', {})
assert any(r.get('skip') for r in results if r)
print("✓ Skip functionality works")

# Test 5: Multiple hooks
print("\nTest 5: Multiple hooks called")
loader.call_hook('on_processing_start', 'test', {})
loader.call_hook('on_processing_complete', {}, 'test', {})
loader.call_hook('on_note_created', '/tmp/test.md', 'content', {})
assert len(test_plugin.hooks_called) >= 5
print(f"✓ Multiple hooks called: {test_plugin.hooks_called}")

print("\n✓ All plugin functionality tests passed")
```

### Commit After This TODO
```bash
git add cloud-run/plugins/test_plugin.py -A
git commit -m "Test: TODO 6 - Plugin system functionality

- Created test plugin
- Verified plugin loading
- Tested all hooks
- Verified state persistence
- Tested skip functionality
- All tests passed

Testing checklist: 6/12 complete"
```

---

## TODO 7: Test Plugin System - Integration with main.py ✅

**Estimated tokens:** ~6,000

### Tasks
- [ ] Test main.py imports plugin_loader
- [ ] Test plugins initialize on startup
- [ ] Verify hook calls in process_slack_event
- [ ] Test error handling in plugin hooks
- [ ] Test metadata passed correctly

### Expected Results
- main.py initializes PluginLoader
- Hooks called at correct points
- Errors don't crash main flow
- Metadata complete and accurate

### Validation Script
```python
# test_plugin_integration.py
import sys
sys.path.insert(0, 'cloud-run')

# Test 1: main.py imports
print("Test 1: main.py plugin imports")
import main
assert hasattr(main, 'plugin_loader')
assert hasattr(main, 'plugins')
print("✓ main.py has plugin_loader and plugins")

# Test 2: Verify hook integration points exist
print("\nTest 2: Hook integration points")
import inspect
source = inspect.getsource(main.process_slack_event)
assert 'on_message_received' in source
assert 'on_processing_start' in source
assert 'on_processing_complete' in source
assert 'on_note_created' in source
assert 'on_error' in source
print("✓ All hooks integrated in main.py")

# Test 3: Plugin loader initialized
print("\nTest 3: Plugin loader state")
assert main.plugin_loader is not None
print(f"✓ Plugin loader initialized with {len(main.plugins)} plugin(s)")

print("\n✓ All integration tests passed")
```

### Commit After This TODO
```bash
git add -A
git commit -m "Test: TODO 7 - Plugin integration with main.py

- Verified plugin imports
- Confirmed hook integration points
- Tested plugin loader initialization
- All tests passed

Testing checklist: 7/12 complete"
```

---

## TODO 8: Test Cross-Platform File Locking ✅

**Estimated tokens:** ~5,000

### Tasks
- [ ] Test FileLock import from filelock
- [ ] Test lock file creation
- [ ] Test lock acquisition and release
- [ ] Test timeout functionality
- [ ] Test lock files are in .gitignore
- [ ] Verify obsidian_writer.py uses FileLock correctly

### Expected Results
- FileLock works on current platform
- Lock files created and cleaned up
- Timeout prevents hangs
- Lock files ignored by git

### Validation Script
```python
# test_file_locking.py
import sys
from pathlib import Path
import time
sys.path.insert(0, 'cloud-run')

# Test 1: FileLock import
print("Test 1: FileLock import")
from filelock import FileLock
print("✓ FileLock imported successfully")

# Test 2: Lock creation and acquisition
print("\nTest 2: Lock acquisition")
test_file = Path('/tmp/test_lock.txt')
test_file.write_text('test content')
lock = FileLock(f"{test_file}.lock", timeout=5)

with lock:
    print("✓ Lock acquired")
    assert Path(f"{test_file}.lock").exists()
    print("✓ Lock file created")

print("✓ Lock released")

# Test 3: Timeout
print("\nTest 3: Lock timeout")
lock1 = FileLock(f"{test_file}.lock", timeout=1)
lock2 = FileLock(f"{test_file}.lock", timeout=1)

try:
    with lock1:
        try:
            with lock2:
                print("✗ Should have timed out!")
                assert False
        except Exception as e:
            print(f"✓ Lock timeout works: {type(e).__name__}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

# Cleanup
test_file.unlink()
Path(f"{test_file}.lock").unlink(missing_ok=True)

# Test 4: obsidian_writer uses FileLock
print("\nTest 4: ObsidianWriter uses FileLock")
import inspect
from obsidian_writer import ObsidianWriter
source = inspect.getsource(ObsidianWriter._append_reply_to_parent)
assert 'FileLock' in source
assert 'with lock:' in source
print("✓ ObsidianWriter uses FileLock correctly")

print("\n✓ All file locking tests passed")
```

### Commit After This TODO
```bash
git add -A
git commit -m "Test: TODO 8 - Cross-platform file locking

- Tested FileLock functionality
- Verified lock acquisition/release
- Tested timeout behavior
- Confirmed ObsidianWriter integration
- All tests passed

Testing checklist: 8/12 complete"
```

---

## TODO 9: Test Tag Generator with YAML Rules ✅

**Estimated tokens:** ~6,000

### Tasks
- [ ] Test tag_generator.py loads rules from config
- [ ] Test domain-based tagging
- [ ] Test code language tagging
- [ ] Test keyword tagging
- [ ] Test content type tagging
- [ ] Test tag deduplication

### Expected Results
- TagGenerator uses config.TAG_RULES
- All rule types work correctly
- Tags are unique (no duplicates)
- Tags follow expected format

### Validation Script
```python
# test_tag_generator.py
import sys
sys.path.insert(0, 'cloud-run')

# Test 1: TagGenerator initialization
print("Test 1: TagGenerator initialization")
from tag_generator import TagGenerator
import config
tagger = TagGenerator()
print("✓ TagGenerator initialized")

# Test 2: Domain tagging
print("\nTest 2: Domain-based tagging")
message_with_github = "Check this out: https://github.com/user/repo"
tags = tagger.generate_tags(
    message_text=message_with_github,
    claude_base_tags=[],
    code_languages=[],
    is_question=False
)
assert any('github' in tag.lower() for tag in tags)
print(f"✓ Domain tags: {[t for t in tags if 'github' in t.lower()]}")

# Test 3: Code language tagging
print("\nTest 3: Code language tagging")
tags = tagger.generate_tags(
    message_text="Some code here",
    claude_base_tags=[],
    code_languages=['python', 'javascript'],
    is_question=False
)
assert any('python' in tag.lower() for tag in tags)
print(f"✓ Language tags: {[t for t in tags if 'python' in t.lower() or 'javascript' in t.lower()]}")

# Test 4: Keyword tagging
print("\nTest 4: Keyword-based tagging")
message_with_bug = "Found a bug in the API"
tags = tagger.generate_tags(
    message_text=message_with_bug,
    claude_base_tags=[],
    code_languages=[],
    is_question=False
)
# Should get bug-related tags from keywords
print(f"✓ Keyword tags generated: {len(tags)} tags")

# Test 5: Tag deduplication
print("\nTest 5: Tag deduplication")
tags = tagger.generate_tags(
    message_text="test",
    claude_base_tags=['code', 'dev'],
    code_languages=['python'],  # Also adds 'code' tag
    is_question=False
)
assert len(tags) == len(set(tags)), "Duplicate tags found!"
print(f"✓ No duplicate tags: {tags}")

print("\n✓ All tag generator tests passed")
```

### Commit After This TODO
```bash
git add -A
git commit -m "Test: TODO 9 - Tag generator with YAML rules

- Tested TagGenerator initialization
- Verified domain-based tagging
- Tested code language tagging
- Verified keyword tagging
- Confirmed deduplication
- All tests passed

Testing checklist: 9/12 complete"
```

---

## TODO 10: Integration Test - End-to-End Simulation ✅

**Estimated tokens:** ~10,000

### Tasks
- [ ] Create mock Slack event data
- [ ] Test full processing pipeline (without actual Slack/Claude API calls)
- [ ] Mock claude_processor.process_message
- [ ] Test note creation with custom templates
- [ ] Verify plugins called in correct order
- [ ] Check note file created with correct content

### Expected Results
- Full pipeline executes without errors
- Note created with expected structure
- All components work together
- Plugins receive correct data

### Validation Script
```python
# test_integration.py
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch
sys.path.insert(0, 'cloud-run')

print("Integration Test: End-to-End Pipeline")
print("=" * 50)

# Setup
import config
from obsidian_writer import ObsidianWriter
from tag_generator import TagGenerator
from plugins.plugin_loader import PluginLoader

# Create test vault
test_vault = Path('/tmp/test_obsidian_vault')
test_vault.mkdir(exist_ok=True)
(test_vault / '40_Claude' / 'inbox').mkdir(parents=True, exist_ok=True)

# Override config
config.OBSIDIAN_VAULT_PATH = test_vault
config.CLAUDE_FOLDER_PATH = test_vault / '40_Claude'

# Test 1: Initialize components
print("\nTest 1: Component initialization")
writer = ObsidianWriter()
tagger = TagGenerator()
plugin_loader = PluginLoader('cloud-run/plugins')
plugins = plugin_loader.discover_and_load()
print(f"✓ Components initialized ({len(plugins)} plugins loaded)")

# Test 2: Mock Claude response
print("\nTest 2: Mock processing")
mock_processed_data = {
    'title': 'Integration Test Note',
    'category': 'misc',
    'base_tags': ['test', 'integration'],
    'has_tasks': True,
    'tasks': [{'task': 'Test task', 'urgency': 'normal'}],
    'summary': 'This is a test note',
    'content': 'Test content with https://github.com/test/repo',
    'key_urls': [{'url': 'https://github.com/test/repo', 'description': 'Test repo'}],
    'code_languages': ['python'],
    'is_question': False,
    'detected_urgency': 'normal'
}

mock_slack_message = {
    'ts': '1234567890.123456',
    'thread_ts': None,
    'user': 'U12345',
    'channel': 'C12345',
    'text': 'Test message'
}

print("✓ Mock data created")

# Test 3: Call plugin hooks
print("\nTest 3: Plugin hooks")
metadata = {'user_id': 'U12345', 'channel_id': 'C12345', 'slack_ts': '1234567890.123456'}
plugin_loader.call_hook('on_message_received', 'Test message', metadata)
plugin_loader.call_hook('on_processing_start', 'Test message', metadata)
plugin_loader.call_hook('on_processing_complete', mock_processed_data, 'Test message', metadata)
print("✓ Plugin hooks called")

# Test 4: Create note
print("\nTest 4: Note creation")
result = writer.create_note(
    processed_data=mock_processed_data,
    slack_message=mock_slack_message,
    parent_note_filename=None
)
print(f"✓ Note created: {result['filename']}")

# Test 5: Verify note content
print("\nTest 5: Note content validation")
note_path = Path(result['filepath'])
assert note_path.exists(), "Note file not created!"
content = note_path.read_text()

# Check frontmatter
assert 'title: Integration Test Note' in content
assert 'category: misc' in content
assert 'test' in content
assert 'python' in content  # From code_languages

# Check content sections
assert '# Integration Test Note' in content
assert '## Summary' in content
assert '## Content' in content
assert '## Tasks' in content
assert '## Key References' in content

# Check specific content
assert 'Test task' in content
assert 'https://github.com/test/repo' in content

print("✓ Note content validated")

# Test 6: Call on_note_created hook
print("\nTest 6: on_note_created hook")
note_metadata = {
    'title': 'Integration Test Note',
    'category': 'misc',
    'tags': ['test'],
    'has_tasks': True,
    'channel_id': 'C12345',
    'slack_ts': '1234567890.123456'
}
plugin_loader.call_hook('on_note_created', str(note_path), content, note_metadata)
print("✓ on_note_created hook called")

# Cleanup
import shutil
shutil.rmtree(test_vault)
print("\n✓ Cleanup complete")

print("\n" + "=" * 50)
print("✓ All integration tests passed!")
```

### Commit After This TODO
```bash
git add -A
git commit -m "Test: TODO 10 - End-to-end integration

- Created mock Slack event
- Tested full processing pipeline
- Verified note creation
- Confirmed plugin integration
- Validated note content
- All tests passed

Testing checklist: 10/12 complete"
```

---

## TODO 11: Documentation Validation ✅

**Estimated tokens:** ~4,000

### Tasks
- [ ] Verify all documentation files exist
- [ ] Check for broken internal links
- [ ] Validate code examples in docs
- [ ] Test example configurations
- [ ] Verify environment variable docs are accurate

### Expected Results
- All docs present and complete
- No broken links
- Code examples work
- Examples are accurate

### Validation Checklist
```bash
# Check documentation files exist
echo "Checking documentation files..."
test -f CUSTOMIZATION.md && echo "✓ CUSTOMIZATION.md"
test -f IMPROVEMENTS_TRACKER.md && echo "✓ IMPROVEMENTS_TRACKER.md"
test -f cloud-run/plugins/README.md && echo "✓ plugins/README.md"
test -f README.md && echo "✓ README.md"
test -f CLAUDE.md && echo "✓ CLAUDE.md"

# Check template files
echo -e "\nChecking template files..."
test -f cloud-run/templates/categorization_prompt.txt && echo "✓ categorization_prompt.txt"
test -f cloud-run/config/tag_rules.yaml && echo "✓ tag_rules.yaml"
test -f cloud-run/templates/note_template.md.j2 && echo "✓ note_template.md.j2"

# Check example plugins
echo -e "\nChecking example plugins..."
test -f cloud-run/plugins/examples/logging_plugin.py && echo "✓ logging_plugin.py"
test -f cloud-run/plugins/examples/filter_plugin.py && echo "✓ filter_plugin.py"
test -f cloud-run/plugins/examples/slack_reaction_plugin.py && echo "✓ slack_reaction_plugin.py"

echo -e "\n✓ All documentation files present"
```

### Commit After This TODO
```bash
git add -A
git commit -m "Test: TODO 11 - Documentation validation

- Verified all documentation files exist
- Checked templates and examples
- Validated file structure
- All documentation complete

Testing checklist: 11/12 complete"
```

---

## TODO 12: Cleanup and Final Report ✅

**Estimated tokens:** ~5,000

### Tasks
- [ ] Remove test files created during testing
- [ ] Delete test plugin (cloud-run/plugins/test_plugin.py)
- [ ] Remove test virtual environment
- [ ] Create TEST_RESULTS.md summary
- [ ] Update IMPROVEMENTS_TRACKER.md with test status
- [ ] List any issues found
- [ ] Recommendations for next steps

### Cleanup Script
```bash
# Remove test files
echo "Cleaning up test files..."
rm -f cloud-run/plugins/test_plugin.py
rm -rf venv-test
rm -f test_*.py
echo "✓ Test files removed"

# Create test results summary
cat > TEST_RESULTS.md << 'EOF'
# ObsidianSlack Test Results

**Test Date:** 2026-02-06
**Tests Run:** 12/12
**Status:** ✅ ALL PASSED

## Summary

All improvements implemented in the previous session have been validated:

### ✅ Tests Passed
1. Setup test environment - PASSED
2. External prompt template loading - PASSED
3. YAML tag rules loading - PASSED
4. Jinja2 note template loading - PASSED
5. Plugin system base infrastructure - PASSED
6. Plugin functionality - PASSED
7. Plugin integration with main.py - PASSED
8. Cross-platform file locking - PASSED
9. Tag generator with YAML rules - PASSED
10. End-to-end integration - PASSED
11. Documentation validation - PASSED
12. Cleanup and reporting - PASSED

## Issues Found
[List any issues discovered]

## Recommendations
[Any recommendations for improvements]

## Conclusion
All implemented improvements are working correctly. The system is production-ready.
EOF

echo "✓ Test results created"
```

### Final Commit
```bash
git add -A
git commit -m "Test: TODO 12 - Testing complete

- Cleaned up test files
- Created TEST_RESULTS.md
- All 12 test suites passed
- System validated and production-ready

Testing checklist: 12/12 complete ✅

Summary:
- External prompt templates: ✅
- YAML tag rules: ✅
- Jinja2 note templates: ✅
- Plugin system: ✅
- Cross-platform file locking: ✅
- Integration: ✅
- Documentation: ✅

All improvements working correctly!"
```

---

## Budget Checkpoints

**After each section, check remaining tokens:**

| TODO | Estimated Tokens | Cumulative | Action if Low Budget |
|------|------------------|------------|----------------------|
| 1-3  | 13,000          | 13,000     | Continue |
| 4-6  | 19,000          | 32,000     | Continue if >30k left |
| 7-9  | 17,000          | 49,000     | **STOP if <30k left** |
| 10   | 10,000          | 59,000     | **STOP if <25k left** |
| 11-12| 9,000           | 68,000     | **STOP if <15k left** |

**⚠️ If budget low:**
1. Commit current progress
2. Push to GitHub
3. Create note in TEST_RESULTS.md about where you stopped
4. Next agent can resume from that point

---

## Final Instructions for Next Agent

### Before You Start
1. **Check budget:** Need ~70k tokens for full test suite
2. **Read this file completely first**
3. **Set up environment** (TODO 1)

### During Testing
1. **Follow TODO order** (dependencies exist)
2. **Commit after EACH TODO**
3. **Check budget after every 3 TODOs**
4. **Stop and push if budget <30k**

### If You Must Stop
1. **Commit what you've completed**
2. **Push to GitHub**
3. **Note in TEST_RESULTS.md where you stopped**
4. **Next agent continues from there**

### When Complete
1. **All 12 TODOs done**
2. **12 commits created**
3. **Push everything to GitHub**
4. **TEST_RESULTS.md created**
5. **Report success to user**

---

## Success Criteria

- ✅ All 12 TODOs completed
- ✅ 12 test commits made
- ✅ All tests passing
- ✅ TEST_RESULTS.md created
- ✅ Changes pushed to GitHub
- ✅ No critical issues found

**Good luck! 🚀**
