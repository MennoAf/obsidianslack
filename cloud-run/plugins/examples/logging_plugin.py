"""
Example Plugin: Enhanced logging of message processing.

This plugin demonstrates multiple hooks working together.
"""
import logging
from datetime import datetime
from plugins.base import ProcessorPlugin

logger = logging.getLogger(__name__)


class LoggingPlugin(ProcessorPlugin):
    """
    Log detailed information about message processing.

    Useful for debugging and analytics.
    """

    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        self.message_count = 0
        logger.info("LoggingPlugin initialized")

    def on_message_received(self, message_text, metadata):
        """Log when a message is received."""
        self.message_count += 1
        logger.info(
            f"[{self.message_count}] Message received from {metadata.get('user_id')} "
            f"in channel {metadata.get('channel_id')}"
        )
        logger.debug(f"Message preview: {message_text[:100]}...")

    def on_processing_start(self, message_text, metadata):
        """Log processing start time."""
        metadata['processing_start_time'] = datetime.now()
        logger.info(f"Starting Claude processing for message {metadata.get('slack_ts')}")

    def on_processing_complete(self, processed_data, original_message, metadata):
        """Log processing completion and stats."""
        if 'processing_start_time' in metadata:
            duration = datetime.now() - metadata['processing_start_time']
            logger.info(
                f"Claude processing completed in {duration.total_seconds():.2f}s - "
                f"Category: {processed_data.get('category')}, "
                f"Tasks: {len(processed_data.get('tasks', []))}"
            )

    def on_note_created(self, note_path, note_content, metadata):
        """Log note creation."""
        logger.info(f"Note created: {note_path}")
        logger.debug(f"Note size: {len(note_content)} bytes")

    def on_error(self, error, context):
        """Log errors with context."""
        logger.error(
            f"Error in {context.get('hook', 'unknown')}: {error}",
            exc_info=True
        )
