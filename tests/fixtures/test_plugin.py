"""Test plugin for validation."""
from plugins.base import ProcessorPlugin
import logging

logger = logging.getLogger(__name__)


class TestPlugin(ProcessorPlugin):
    """Test plugin for validation."""

    def __init__(self):
        super().__init__()
        self.call_count = 0
        self.hooks_called = []

    def on_message_received(self, message_text, metadata):
        self.call_count += 1
        self.hooks_called.append('on_message_received')
        logger.info(f"TestPlugin: on_message_received called ({self.call_count})")

        # Test skip functionality
        if 'SKIP_TEST' in message_text:
            return {'skip': True}

    def on_processing_start(self, message_text, metadata):
        self.hooks_called.append('on_processing_start')
        logger.info("TestPlugin: on_processing_start called")

    def on_processing_complete(self, processed_data, original_message, metadata):
        self.hooks_called.append('on_processing_complete')
        logger.info("TestPlugin: on_processing_complete called")

    def on_note_created(self, note_path, note_content, metadata):
        self.hooks_called.append('on_note_created')
        logger.info(f"TestPlugin: on_note_created called - {note_path}")

    def on_error(self, error, context):
        self.hooks_called.append('on_error')
        logger.info(f"TestPlugin: on_error called - {error}")
