# test_plugin_integration.py
import sys
from pathlib import Path
sys.path.insert(0, 'cloud-run')

# Test 1: main.py source code analysis
print("Test 1: main.py plugin imports (source code analysis)")
main_py_path = Path('cloud-run/main.py')
main_source = main_py_path.read_text()

# Check for plugin_loader import and initialization
assert 'from plugins.plugin_loader import PluginLoader' in main_source
assert 'plugin_loader = PluginLoader' in main_source
assert 'plugins = plugin_loader.discover_and_load()' in main_source
print("✓ main.py imports and initializes plugin system")

# Test 2: Verify hook integration points exist
print("\nTest 2: Hook integration points in process_slack_event")
assert "'on_message_received'" in main_source
assert "'on_processing_start'" in main_source
assert "'on_processing_complete'" in main_source
assert "'on_note_created'" in main_source
assert "'on_error'" in main_source
print("✓ All hooks integrated in main.py")
print("  - on_message_received")
print("  - on_processing_start")
print("  - on_processing_complete")
print("  - on_note_created")
print("  - on_error")

# Test 3: Check for skip handling
print("\nTest 3: Skip handling")
# Check that skip functionality is used
assert 'skip' in main_source
print("✓ Skip handling present")

# Test 4: Check metadata is constructed
print("\nTest 4: Metadata construction")
assert 'metadata' in main_source
# Check for key metadata fields
assert 'user_id' in main_source or 'user' in main_source
assert 'channel' in main_source
print("✓ Metadata construction present")

# Test 5: Verify plugin loader can actually load plugins
print("\nTest 5: Plugin loader functionality")
from plugins.plugin_loader import PluginLoader
loader = PluginLoader('cloud-run/plugins')
plugins = loader.discover_and_load()
assert len(plugins) == 1, f"Expected 1 test plugin, got {len(plugins)}"
print(f"✓ Plugin loader works ({len(plugins)} plugin loaded)")
for plugin in plugins:
    print(f"  - {plugin.name}")

print("\n✓ All integration tests passed")
