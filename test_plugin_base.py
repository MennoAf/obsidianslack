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
print(f"  Name: {plugin.name}")
print(f"  Enabled: {plugin.enabled}")

# Test 2: PluginLoader
print("\nTest 2: PluginLoader initialization")
from plugins.plugin_loader import PluginLoader
loader = PluginLoader('cloud-run/plugins')
assert loader.plugin_dir.exists()
print("✓ PluginLoader initializes")
print(f"  Plugin directory: {loader.plugin_dir}")

# Test 3: Plugin discovery (should find none - examples are skipped)
print("\nTest 3: Plugin discovery")
plugins = loader.discover_and_load()
# Should be empty since all examples are in examples/ subdirectory
assert isinstance(plugins, list)
print(f"✓ Discovered {len(plugins)} plugins (examples dir skipped)")
for p in plugins:
    print(f"  - {p.name}")

# Test 4: Disable via env var
print("\nTest 4: PLUGINS_ENABLED=false")
os.environ['PLUGINS_ENABLED'] = 'false'
loader2 = PluginLoader('cloud-run/plugins')
plugins2 = loader2.discover_and_load()
assert len(plugins2) == 0
print("✓ Plugins disabled via env var")

# Cleanup
if 'PLUGINS_ENABLED' in os.environ:
    del os.environ['PLUGINS_ENABLED']

print("\n✓ All plugin base tests passed")
