"""
Plugin discovery and loading system.
"""
import logging
import importlib
import inspect
import os
from pathlib import Path
from typing import List
from .base import ProcessorPlugin

logger = logging.getLogger(__name__)


class PluginLoader:
    """
    Discovers and loads plugins from the plugins directory.
    """

    def __init__(self, plugin_dir: str = None):
        """
        Initialize the plugin loader.

        Args:
            plugin_dir: Path to plugins directory. Defaults to plugins/ relative to this file.
        """
        if plugin_dir:
            self.plugin_dir = Path(plugin_dir)
        else:
            self.plugin_dir = Path(__file__).parent

        self.plugins: List[ProcessorPlugin] = []

    def discover_and_load(self) -> List[ProcessorPlugin]:
        """
        Discover and load all plugins from the plugins directory.

        Returns:
            List of loaded plugin instances
        """
        # Check if plugins are disabled via environment variable
        if os.getenv('PLUGINS_ENABLED', 'true').lower() == 'false':
            logger.info("Plugins are disabled via PLUGINS_ENABLED=false")
            return []

        # Get plugin directories (skip __pycache__, base.py, etc.)
        plugin_packages = []
        if self.plugin_dir.exists():
            for item in self.plugin_dir.iterdir():
                # Skip special files/directories
                if item.name.startswith('_') or item.name.startswith('.'):
                    continue
                if item.name in ['base.py', 'plugin_loader.py']:
                    continue

                # Look for Python files or packages
                if item.is_file() and item.suffix == '.py':
                    plugin_packages.append(item.stem)
                elif item.is_dir() and (item / '__init__.py').exists():
                    plugin_packages.append(item.name)

        if not plugin_packages:
            logger.info("No plugins found in plugins directory")
            return []

        # Load each plugin
        for package_name in plugin_packages:
            try:
                self._load_plugin_from_package(package_name)
            except Exception as e:
                logger.error(f"Failed to load plugin '{package_name}': {e}")
                continue

        if self.plugins:
            logger.info(f"✓ Loaded {len(self.plugins)} plugin(s): {', '.join(p.name for p in self.plugins)}")
        else:
            logger.info("No plugins loaded")

        return self.plugins

    def _load_plugin_from_package(self, package_name: str):
        """
        Load a plugin from a package or module.

        Args:
            package_name: Name of the plugin package/module
        """
        # Import the module
        module_name = f"plugins.{package_name}"
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            logger.warning(f"Could not import plugin module '{module_name}': {e}")
            return

        # Find ProcessorPlugin subclasses in the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Skip the base class itself
            if obj is ProcessorPlugin:
                continue

            # Check if it's a subclass of ProcessorPlugin
            if issubclass(obj, ProcessorPlugin):
                try:
                    # Instantiate the plugin
                    plugin_instance = obj()
                    self.plugins.append(plugin_instance)
                    logger.debug(f"Loaded plugin: {plugin_instance}")
                except Exception as e:
                    logger.error(f"Failed to instantiate plugin '{name}': {e}")

    def call_hook(self, hook_name: str, *args, **kwargs):
        """
        Call a hook on all loaded plugins.

        Args:
            hook_name: Name of the hook method to call
            *args: Positional arguments to pass to the hook
            **kwargs: Keyword arguments to pass to the hook

        Returns:
            List of return values from plugins (skips None values)
        """
        results = []

        for plugin in self.plugins:
            if not plugin.enabled:
                continue

            # Check if plugin has this hook
            if not hasattr(plugin, hook_name):
                continue

            hook_method = getattr(plugin, hook_name)
            if not callable(hook_method):
                continue

            try:
                result = hook_method(*args, **kwargs)
                if result is not None:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error calling {hook_name} on {plugin.name}: {e}")
                # Try to call on_error hook
                try:
                    plugin.on_error(e, {'hook': hook_name, 'args': args, 'kwargs': kwargs})
                except Exception:
                    pass  # Silently ignore errors in error handler

        return results
