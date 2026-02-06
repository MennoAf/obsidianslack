"""
Example Plugin: Filter messages based on custom criteria.

This plugin demonstrates the on_message_received hook with skip functionality.
"""
import logging
import re
from plugins.base import ProcessorPlugin

logger = logging.getLogger(__name__)


class MessageFilterPlugin(ProcessorPlugin):
    """
    Filter out messages that match certain patterns.

    Use cases:
    - Skip bot messages
    - Skip messages with certain keywords
    - Skip very short messages
    - Skip messages from specific users
    """

    def __init__(self):
        """Initialize the plugin."""
        super().__init__()

        # Customize these patterns
        self.skip_patterns = [
            r'^/\w+',  # Skip slash commands
            r'^\s*$',  # Skip empty messages
        ]

        self.skip_users = []  # Add user IDs to skip

        self.min_message_length = 10  # Skip messages shorter than this

        logger.info("MessageFilterPlugin initialized")

    def on_message_received(self, message_text, metadata):
        """
        Check if message should be skipped.

        Returns:
            dict with {'skip': True} to skip processing
        """
        # Check user filter
        if metadata.get('user_id') in self.skip_users:
            logger.info(f"Skipping message from filtered user: {metadata.get('user_id')}")
            return {'skip': True}

        # Check length filter
        if len(message_text.strip()) < self.min_message_length:
            logger.info(f"Skipping message (too short): {len(message_text)} chars")
            return {'skip': True}

        # Check pattern filters
        for pattern in self.skip_patterns:
            if re.match(pattern, message_text):
                logger.info(f"Skipping message matching pattern: {pattern}")
                return {'skip': True}

        # Message passed all filters
        return None
