"""
ObsidianSlack Plugin System

Allows users to extend ObsidianSlack functionality with custom processing hooks.
"""
from .base import ProcessorPlugin
from .plugin_loader import PluginLoader

__all__ = ['ProcessorPlugin', 'PluginLoader']
