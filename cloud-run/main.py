"""
Main application for Slack-Obsidian Brain Dump.

This application listens for Slack webhook events and processes messages
from a designated "brain dump" channel, using Claude to categorize and
format them into Obsidian notes.
"""
import logging
import sys
import threading
from flask import Flask, request, jsonify
import config
from slack_handler import SlackHandler
from claude_processor import ClaudeProcessor
from obsidian_writer import ObsidianWriter
from plugins.plugin_loader import PluginLoader

# Setup logging
logging.basicConfig(
    level=logging.INFO if not config.DEBUG_MODE else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('brain_dump.log')
    ]
)
logger = logging.getLogger(__name__)

# Event deduplication tracking
_processed_events = set()
_events_lock = threading.Lock()


def _is_duplicate(event_id: str) -> bool:
    """
    Check if an event has already been processed.

    Args:
        event_id: Unique event identifier from Slack

    Returns:
        True if event was already processed, False otherwise
    """
    with _events_lock:
        if event_id in _processed_events:
            return True
        _processed_events.add(event_id)
        # Prevent unbounded memory growth
        if len(_processed_events) > 10000:
            _processed_events.clear()
        return False


# Initialize Flask app
app = Flask(__name__)

# Initialize handlers
slack_handler = SlackHandler()
claude_processor = ClaudeProcessor()
obsidian_writer = ObsidianWriter()

# Initialize plugin system
plugin_loader = PluginLoader()
plugins = plugin_loader.discover_and_load()


@app.route('/slack/events', methods=['POST'])
def slack_events():
    """
    Handle incoming Slack events via webhook.
    
    This endpoint receives events from Slack and processes brain dump messages.
    """
    # 1. Verify signature FIRST (uses raw body)
    raw_body = request.get_data()
    timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
    signature = request.headers.get('X-Slack-Signature', '')

    if not slack_handler.verify_request(raw_body.decode('utf-8'), timestamp, signature):
        logger.warning("Invalid Slack request signature")
        return jsonify({'error': 'Invalid signature'}), 403

    # 2. THEN parse JSON
    data = request.json

    # 3. Handle URL verification challenge
    if data.get('type') == 'url_verification':
        logger.info("Handling URL verification challenge")
        return jsonify({'challenge': data.get('challenge', '')})

    # 4. Check for duplicate events (Slack retries)
    event_id = data.get('event_id')
    if event_id and _is_duplicate(event_id):
        logger.info(f"Skipping duplicate event: {event_id}")
        return jsonify({'status': 'ok'}), 200

    # 5. Handle event
    if data.get('type') == 'event_callback':
        try:
            process_slack_event(data)
        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)

    # Always return 200 OK quickly to avoid Slack retries
    return jsonify({'status': 'ok'}), 200


def process_slack_event(event_data: dict):
    """
    Process a Slack event and create an Obsidian note.
    
    Args:
        event_data: Event data from Slack webhook
    """
    # Parse event
    event_info = slack_handler.handle_event(event_data)
    
    if not event_info:
        logger.debug("Event ignored")
        return
    
    logger.info(f"Processing message: {event_info['message_ts']}")

    # Call plugin hook: on_message_received
    message_metadata = {
        'user_id': event_info.get('user_id'),
        'channel_id': event_info['channel_id'],
        'slack_ts': event_info['message_ts'],
        'thread_ts': event_info.get('thread_ts'),
        'is_reply': event_info['is_reply']
    }

    hook_results = plugin_loader.call_hook(
        'on_message_received',
        event_info['text'],
        message_metadata
    )

    # Check if any plugin wants to skip processing
    for result in hook_results:
        if isinstance(result, dict) and result.get('skip'):
            logger.info("Message processing skipped by plugin")
            return

    # Get thread context if this is a reply
    thread_context = None
    parent_note_filename = None
    
    if event_info['is_reply']:
        thread_context = slack_handler.get_thread_context(
            event_info['channel_id'],
            event_info['thread_ts']
        )
        
        # Find parent note
        parent_note_filename = obsidian_writer.get_note_by_slack_ts(
            event_info['thread_ts']
        )
        
        logger.info(f"Processing reply to thread: {event_info['thread_ts']}")
    
    # Process message with Claude
    try:
        # Call plugin hook: on_processing_start
        plugin_loader.call_hook(
            'on_processing_start',
            event_info['text'],
            message_metadata
        )

        processed_data = claude_processor.process_message(
            message_text=event_info['text'],
            thread_context=thread_context
        )

        # Call plugin hook: on_processing_complete
        plugin_loader.call_hook(
            'on_processing_complete',
            processed_data,
            event_info['text'],
            message_metadata
        )

    except Exception as e:
        logger.error(f"Error processing with Claude: {e}", exc_info=True)

        # Call plugin hook: on_error
        plugin_loader.call_hook(
            'on_error',
            e,
            {'stage': 'claude_processing', 'message': event_info['text']}
        )

        # React with error emoji
        slack_handler.add_reaction(
            event_info['channel_id'],
            event_info['message_ts'],
            'x'
        )
        return
    
    # Create Obsidian note
    try:
        result = obsidian_writer.create_note(
            processed_data=processed_data,
            slack_message=event_info['full_event'],
            parent_note_filename=parent_note_filename
        )
        
        logger.info(f"Created note: {result['filename']}")

        # Call plugin hook: on_note_created
        note_metadata = {
            'title': processed_data.get('title'),
            'category': processed_data.get('category'),
            'tags': processed_data.get('base_tags', []),
            'has_tasks': processed_data.get('has_tasks', False),
            'channel_id': event_info['channel_id'],
            'slack_ts': event_info['message_ts']
        }

        # Read note content for plugins
        from pathlib import Path
        note_content = Path(result['filepath']).read_text(encoding='utf-8')

        plugin_loader.call_hook(
            'on_note_created',
            result['filepath'],
            note_content,
            note_metadata
        )

        # React with checkmark to confirm processing
        slack_handler.add_reaction(
            event_info['channel_id'],
            event_info['message_ts'],
            'white_check_mark'
        )
        
        # Optionally post a reply with the note info
        if config.DEBUG_MODE:
            slack_handler.post_message(
                channel_id=event_info['channel_id'],
                text=f"✅ Created note: `{result['filename']}`",
                thread_ts=event_info['message_ts']
            )
        
    except Exception as e:
        logger.error(f"Error creating note: {e}", exc_info=True)

        # Call plugin hook: on_error
        plugin_loader.call_hook(
            'on_error',
            e,
            {'stage': 'note_creation', 'message': event_info['text']}
        )

        # React with error emoji
        slack_handler.add_reaction(
            event_info['channel_id'],
            event_info['message_ts'],
            'x'
        )


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with basic info."""
    return jsonify({
        'name': 'Slack-Obsidian Brain Dump',
        'status': 'running',
        'endpoints': {
            'events': '/slack/events',
            'health': '/health'
        }
    }), 200


def main():
    """Main entry point."""
    try:
        # Validate configuration
        config.validate_config()
        logger.info("✓ Configuration validated")
        
        # Setup Obsidian folders
        config.setup_obsidian_folders()
        logger.info("✓ Obsidian folders ready")
        
        # Start Flask server
        logger.info(f"Starting server on port {config.FLASK_PORT}")
        host = '127.0.0.1' if config.DEBUG_MODE else '0.0.0.0'
        app.run(
            host=host,
            port=config.FLASK_PORT,
            debug=config.DEBUG_MODE
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
