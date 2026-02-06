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
print(f"  Sections: {list(rules.keys())}")

# Test 2: Config loading
print("\nTest 2: Config loading")
import config
assert config.TAG_RULES is not None
assert 'github.com' in config.TAG_RULES['domains']
assert 'python' in config.TAG_RULES['code_languages']
print("✓ Tag rules loaded in config")
print(f"  Domains: {len(config.TAG_RULES['domains'])} entries")
print(f"  Languages: {len(config.TAG_RULES['code_languages'])} entries")
print(f"  Keywords: {len(config.TAG_RULES['keywords'])} entries")
print(f"  Content types: {len(config.TAG_RULES['content_types'])} entries")

# Test 3: Custom rules file
print("\nTest 3: Custom rules via env var")
from pathlib import Path
custom_rules = {
    'domains': {'test.com': ['test-tag']},
    'code_languages': {},
    'keywords': {},
    'content_types': {}
}
custom_path = Path('cloud-run/config/test_rules.yaml')
with open(custom_path, 'w') as f:
    yaml.dump(custom_rules, f)

os.environ['TAG_RULES_FILE'] = str(custom_path.absolute())
import importlib
importlib.reload(config)
assert 'test.com' in config.TAG_RULES['domains']
print("✓ Custom rules loaded")

# Cleanup
custom_path.unlink()
if 'TAG_RULES_FILE' in os.environ:
    del os.environ['TAG_RULES_FILE']

print("\n✓ All tag rules tests passed")
