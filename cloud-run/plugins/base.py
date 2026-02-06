"""
Base plugin class for ObsidianSlack plugins.

All plugins should inherit from ProcessorPlugin and implement
the hooks they need.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ProcessorPlugin:
    """
    Base class for ObsidianSlack plugins.

    Plugins can hook into various stages of message processing:
    - on_message_received: When a Slack message is received
    - on_processing_start: Before Claude processes the message
    - on_processing_complete: After Claude processes the message
    - on_note_created: After an Obsidian note is written
    - on_error: When an error occurs during processing

    All hooks are optional - only implement the ones you need.
    """

    def __init__(self):
        """Initialize the plugin."""
        self.enabled = True
        self.name = self.__class__.__name__

    def on_message_received(
        self,
        message_text: str,
        metadata: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Called when a Slack message is received, before any processing.

        Args:
            message_text: The raw message text from Slack
            metadata: Message metadata (user, channel, timestamp, etc.)

        Returns:
            Optional dict with modified data, or None to continue normally.
            Can return {'skip': True} to skip processing this message.
        """
        pass

    def on_processing_start(
        self,
        message_text: str,
        metadata: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Called before sending message to Claude for processing.

        Args:
            message_text: The message text that will be sent to Claude
            metadata: Message metadata

        Returns:
            Optional dict with modified message_text or metadata
        """
        pass

    def on_processing_complete(
        self,
        processed_data: Dict[str, Any],
        original_message: str,
        metadata: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Called after Claude has processed the message.

        Args:
            processed_data: The structured data returned by Claude
            original_message: The original message text
            metadata: Message metadata

        Returns:
            Optional dict with modified processed_data
        """
        pass

    def on_note_created(
        self,
        note_path: str,
        note_content: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Called after an Obsidian note has been written to disk.

        Args:
            note_path: Full path to the created note file
            note_content: The full content of the note (frontmatter + content)
            metadata: Note metadata (title, category, tags, etc.)
        """
        pass

    def on_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> None:
        """
        Called when an error occurs during processing.

        Args:
            error: The exception that was raised
            context: Context about where the error occurred
        """
        pass

    def __str__(self):
        """String representation of the plugin."""
        return f"{self.name} (enabled={self.enabled})"
