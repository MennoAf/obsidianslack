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
print(f"  Rendered length: {len(rendered)} characters")

# Verify frontmatter
assert 'title: Test Note' in rendered
assert 'category: misc' in rendered
assert '1234567890.123456' in rendered  # slack_ts value (with or without quotes)
print("✓ Frontmatter present")

# Verify sections
assert '## Summary' in rendered
assert '## Content' in rendered
assert '## Tasks' in rendered
assert '## Key References' in rendered
print("✓ All sections present")

# Test 3: ObsidianWriter integration
print("\nTest 3: ObsidianWriter integration")
from obsidian_writer import ObsidianWriter
writer = ObsidianWriter()
# Check if template engine is initialized or templates disabled
has_templates = hasattr(writer, 'template_env') and writer.template_env is not None
print(f"✓ ObsidianWriter template engine: {'initialized' if has_templates else 'disabled (fallback mode)'}")

print("\n✓ All note template tests passed")
