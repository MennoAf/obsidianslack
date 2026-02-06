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
original_vault = config.OBSIDIAN_VAULT_PATH
original_claude = config.CLAUDE_FOLDER_PATH
config.OBSIDIAN_VAULT_PATH = test_vault
config.CLAUDE_FOLDER_PATH = test_vault / '40_Claude'

# Test 1: Initialize components
print("\nTest 1: Component initialization")
writer = ObsidianWriter()
tagger = TagGenerator()
plugin_loader = PluginLoader('tests/fixtures')
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
print(f"  Frontmatter: present")
print(f"  Sections: Summary, Content, Tasks, Key References")
print(f"  Result keys: {list(result.keys())}")

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

# Test 7: Verify TestPlugin state
print("\nTest 7: TestPlugin state verification")
if len(plugins) > 0:
    test_plugin = plugins[0]
    print(f"✓ TestPlugin called {test_plugin.call_count} times")
    print(f"  Hooks called: {test_plugin.hooks_called}")
else:
    print("  (No plugins loaded)")

# Cleanup
import shutil
shutil.rmtree(test_vault)
config.OBSIDIAN_VAULT_PATH = original_vault
config.CLAUDE_FOLDER_PATH = original_claude
print("\n✓ Cleanup complete")

print("\n" + "=" * 50)
print("✓ All integration tests passed!")
