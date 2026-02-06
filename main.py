"""
Main application for Slack-Obsidian Brain Dump.

This application listens for Slack webhook events and processes messages
from a designated "brain dump" channel, using Claude to categorize and
format them into Obsidian notes.
"""
import logging
import sys
from flask import Flask, request, jsonify
import config
from slack_handler import SlackHandler
from claude_processor import ClaudeProcessor
from obsidian_writer import ObsidianWriter

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

# Initialize Flask app
app = Flask(__name__)

# Initialize handlers
slack_handler = SlackHandler()
claude_processor = ClaudeProcessor()
obsidian_writer = ObsidianWriter()


@app.route('/slack/events', methods=['POST'])
def slack_events():
    """
    Handle incoming Slack events via webhook.
    
    This endpoint receives events from Slack and processes brain dump messages.
    """
    # Parse request
    data = request.json
    
    # Handle URL verification challenge
    if data.get('type') == 'url_verification':
        logger.info("Handling URL verification challenge")
        return jsonify({'challenge': data['challenge']})
    
    # Verify request authenticity
    timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
    signature = request.headers.get('X-Slack-Signature', '')
    
    if not slack_handler.verify_request(request.get_data().decode('utf-8'), timestamp, signature):
        logger.warning("Invalid Slack request signature")
        return jsonify({'error': 'Invalid signature'}), 403
    
    # Handle event
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
        processed_data = claude_processor.process_message(
            message_text=event_info['text'],
            thread_context=thread_context
        )
    except Exception as e:
        logger.error(f"Error processing with Claude: {e}", exc_info=True)
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
        # React with error emoji
        slack_handler.add_reaction(
            event_info['channel_id'],
            event_info['message_ts'],
            'x'
        )


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'vault_path': str(config.CLAUDE_FOLDER_PATH),
        'channel_id': config.SLACK_BRAIN_DUMP_CHANNEL_ID
    }), 200


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
        app.run(
            host='0.0.0.0',
            port=config.FLASK_PORT,
            debug=config.DEBUG_MODE
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
