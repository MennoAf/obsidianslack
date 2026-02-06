"""
Slack API integration and webhook handling.
"""
import logging
from typing import Optional, Dict, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import config

logger = logging.getLogger(__name__)


class SlackHandler:
    """Handle Slack API interactions."""
    
    def __init__(self):
        """Initialize Slack client."""
        self.client = WebClient(token=config.SLACK_BOT_TOKEN)
        self.channel_id = config.SLACK_BRAIN_DUMP_CHANNEL_ID
    
    def get_message(self, channel_id: str, message_ts: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific message from Slack.
        
        Args:
            channel_id: Channel ID
            message_ts: Message timestamp
            
        Returns:
            Message dict or None if not found
        """
        try:
            result = self.client.conversations_history(
                channel=channel_id,
                latest=message_ts,
                limit=1,
                inclusive=True
            )
            
            if result['messages']:
                return result['messages'][0]
            
            logger.warning(f"Message not found: {message_ts}")
            return None
            
        except SlackApiError as e:
            logger.error(f"Error fetching message: {e}")
            return None
    
    def get_thread_context(
        self,
        channel_id: str,
        thread_ts: str
    ) -> Optional[str]:
        """
        Get the parent message of a thread for context.
        
        Args:
            channel_id: Channel ID
            thread_ts: Thread timestamp (parent message)
            
        Returns:
            Parent message text or None
        """
        parent_message = self.get_message(channel_id, thread_ts)
        if parent_message:
            return parent_message.get('text', '')
        return None
    
    def add_reaction(self, channel_id: str, message_ts: str, emoji: str = "white_check_mark"):
        """
        Add a reaction emoji to a message.
        
        Args:
            channel_id: Channel ID
            message_ts: Message timestamp
            emoji: Emoji name (without colons)
        """
        try:
            self.client.reactions_add(
                channel=channel_id,
                timestamp=message_ts,
                name=emoji
            )
            logger.info(f"Added reaction :{emoji}: to message {message_ts}")
        except SlackApiError as e:
            logger.error(f"Error adding reaction: {e}")
    
    def post_message(self, channel_id: str, text: str, thread_ts: Optional[str] = None):
        """
        Post a message to Slack.
        
        Args:
            channel_id: Channel ID to post to
            text: Message text
            thread_ts: Optional thread timestamp to reply to
        """
        try:
            self.client.chat_postMessage(
                channel=channel_id,
                text=text,
                thread_ts=thread_ts
            )
            logger.info(f"Posted message to {channel_id}")
        except SlackApiError as e:
            logger.error(f"Error posting message: {e}")
    
    def get_recent_messages(
        self,
        channel_id: Optional[str] = None,
        limit: int = 10
    ) -> list:
        """
        Get recent messages from a channel.
        
        Args:
            channel_id: Channel ID (defaults to brain dump channel)
            limit: Number of messages to fetch
            
        Returns:
            List of message dicts
        """
        if channel_id is None:
            channel_id = self.channel_id
        
        try:
            result = self.client.conversations_history(
                channel=channel_id,
                limit=limit
            )
            return result['messages']
        except SlackApiError as e:
            logger.error(f"Error fetching messages: {e}")
            return []
    
    def verify_request(self, request_data: dict, timestamp: str, signature: str) -> bool:
        """
        Verify that a request came from Slack.
        
        Args:
            request_data: Request body
            timestamp: X-Slack-Request-Timestamp header
            signature: X-Slack-Signature header
            
        Returns:
            True if request is valid
        """
        import hmac
        import hashlib
        import time
        
        # Check timestamp is recent (within 5 minutes)
        if abs(time.time() - int(timestamp)) > 60 * 5:
            logger.warning("Request timestamp too old")
            return False
        
        # Verify signature
        sig_basestring = f"v0:{timestamp}:{request_data}".encode('utf-8')
        my_signature = 'v0=' + hmac.new(
            config.SLACK_SIGNING_SECRET.encode('utf-8'),
            sig_basestring,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(my_signature, signature):
            logger.warning("Invalid signature")
            return False
        
        return True
    
    def handle_event(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a Slack event.
        
        Args:
            event_data: Event data from Slack
            
        Returns:
            Processed event info or None if should be ignored
        """
        event = event_data.get('event', {})
        event_type = event.get('type')
        
        # Only process message events
        if event_type != 'message':
            logger.debug(f"Ignoring non-message event: {event_type}")
            return None
        
        # Ignore bot messages
        if event.get('bot_id'):
            logger.debug("Ignoring bot message")
            return None
        
        # Only process regular messages (no subtype)
        # Bot messages are already filtered above
        if event.get('subtype') is not None:
            logger.debug(f"Ignoring message subtype: {event.get('subtype')}")
            return None
        
        # Check if message is in the brain dump channel
        channel = event.get('channel')
        if channel != self.channel_id:
            logger.debug(f"Ignoring message from other channel: {channel}")
            return None
        
        # Extract message info
        message_ts = event.get('ts')
        thread_ts = event.get('thread_ts')
        text = event.get('text', '')
        
        # Determine if this is a reply
        is_reply = thread_ts is not None and thread_ts != message_ts
        
        return {
            'channel_id': channel,
            'message_ts': message_ts,
            'thread_ts': thread_ts,
            'text': text,
            'is_reply': is_reply,
            'full_event': event
        }
