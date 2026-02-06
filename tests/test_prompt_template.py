# test_prompt_template.py
import os
import sys
from pathlib import Path
sys.path.insert(0, 'cloud-run')

# Test 1: Default loading
print("Test 1: Default prompt template")
import config
assert config.CATEGORIZATION_PROMPT is not None
assert len(config.CATEGORIZATION_PROMPT) > 100
print("✓ Default prompt loaded")
print(f"  Length: {len(config.CATEGORIZATION_PROMPT)} characters")

# Test 2: Custom template
print("\nTest 2: Custom template via env var")
test_template_path = Path('cloud-run/templates/test_prompt.txt')
test_template_path.write_text("Test prompt: {slack_message}")

# Use absolute path for env var
os.environ['PROMPT_TEMPLATE'] = str(test_template_path.absolute())

# Reload config module
import importlib
importlib.reload(config)
assert 'Test prompt' in config.CATEGORIZATION_PROMPT, f"Expected 'Test prompt' in content, got: {config.CATEGORIZATION_PROMPT}"
print("✓ Custom template loaded via PROMPT_TEMPLATE env var")

# Test 3: Fallback to default when custom file removed
print("\nTest 3: Fallback to default when file missing")
test_template_path.unlink()  # Delete the test file
os.environ['PROMPT_TEMPLATE'] = 'templates/nonexistent.txt'
importlib.reload(config)
assert config.CATEGORIZATION_PROMPT is not None
assert len(config.CATEGORIZATION_PROMPT) > 100
print("✓ Fallback to default works")

# Cleanup
if 'PROMPT_TEMPLATE' in os.environ:
    del os.environ['PROMPT_TEMPLATE']

print("\n✓ All prompt template tests passed")
