"""
Example Plugin: Add custom Slack reactions based on note content.

This plugin demonstrates the on_note_created hook.
"""
import logging
from plugins.base import ProcessorPlugin

logger = logging.getLogger(__name__)


class SlackReactionPlugin(ProcessorPlugin):
    """
    Add custom Slack reactions based on note metadata.

    Examples:
    - Add 🎯 for high-priority tasks
    - Add 💡 for ideas category
    - Add 🐛 for bug-related content
    """

    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        logger.info("SlackReactionPlugin initialized")

    def on_note_created(self, note_path, note_content, metadata):
        """
        Add custom reactions to the Slack message based on note content.

        Args:
            note_path: Path to the created note
            note_content: Full note content
            metadata: Note metadata dict
        """
        # Example logic (you would need to implement Slack API calls)
        category = metadata.get('category', '')
        priority = metadata.get('priority', '')
        has_tasks = metadata.get('has_tasks', False)

        reactions = []

        # Add reactions based on category
        if category == 'ideas':
            reactions.append('bulb')  # 💡
        elif category == 'code':
            reactions.append('computer')  # 💻
        elif category == 'news':
            reactions.append('newspaper')  # 📰

        # Add reactions based on priority
        if priority == 'high':
            reactions.append('fire')  # 🔥
        elif priority == 'medium':
            reactions.append('warning')  # ⚠️

        # Add reaction if it has tasks
        if has_tasks:
            reactions.append('ballot_box_with_check')  # ☑️

        logger.info(f"Would add reactions to Slack: {reactions}")
        # TODO: Implement actual Slack API call to add reactions
        # slack_client.reactions_add(
        #     channel=metadata.get('channel_id'),
        #     timestamp=metadata.get('slack_ts'),
        #     name=reaction
        # )
