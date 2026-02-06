# test_plugin_functionality.py
import sys
sys.path.insert(0, 'cloud-run')

# Test 1: Plugin loading
print("Test 1: Test plugin loading")
from plugins.plugin_loader import PluginLoader
loader = PluginLoader('tests/fixtures')
plugins = loader.discover_and_load()
assert len(plugins) == 1, f"Expected 1 plugin, got {len(plugins)}"
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
print(f"  Call count: {test_plugin.call_count}")

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
