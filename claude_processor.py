"""
Claude API integration for processing Slack messages.
"""
import json
import logging
from typing import Dict, Any, Optional
from anthropic import Anthropic
import config
from utils import extract_urls, detect_all_code_languages

logger = logging.getLogger(__name__)


class ClaudeProcessor:
    """Process Slack messages using Claude API."""
    
    def __init__(self):
        """Initialize Claude API client."""
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.CLAUDE_MODEL
        self.max_tokens = config.MAX_TOKENS
    
    def process_message(
        self,
        message_text: str,
        thread_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a Slack message using Claude API.
        
        Args:
            message_text: The Slack message text
            thread_context: Optional context from parent message if this is a reply
            
        Returns:
            Dictionary containing processed information:
                - title: Note title
                - category: Note category
                - base_tags: Suggested tags
                - has_tasks: Whether message contains tasks
                - tasks: List of task objects
                - summary: Brief summary
                - content: Formatted content
                - key_urls: Important URLs
                - code_languages: Detected languages
                - is_question: Whether it's a question
                - detected_urgency: Urgency level
        """
        # Extract URLs for context
        urls = extract_urls(message_text)
        urls_context = "\n".join(urls) if urls else "None"
        
        # Auto-detect code languages from markdown blocks
        auto_detected_languages = detect_all_code_languages(message_text)
        
        # Build the prompt
        prompt = config.CATEGORIZATION_PROMPT.format(
            slack_message=message_text,
            thread_context=thread_context or "None (this is a new message)",
            urls_found=urls_context,
            categories=', '.join(config.VALID_CATEGORIES)
        )
        
        try:
            # Call Claude API
            logger.info(f"Calling Claude API with model: {self.model}")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract text content from response
            response_text = response.content[0].text
            logger.debug(f"Claude response: {response_text}")
            
            # Parse JSON response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks if present
                json_match = self._extract_json_from_markdown(response_text)
                if json_match:
                    result = json.loads(json_match)
                else:
                    raise
            
            # Merge auto-detected languages with Claude's detection
            if auto_detected_languages:
                result['code_languages'] = list(set(
                    result.get('code_languages', []) + auto_detected_languages
                ))
            
            # Validate and set defaults
            result = self._validate_result(result)
            
            logger.info(f"Successfully processed message: {result['title']}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing message with Claude: {e}")
            # Return a fallback result
            return self._create_fallback_result(message_text)
    
    def _extract_json_from_markdown(self, text: str) -> Optional[str]:
        """
        Extract JSON from markdown code blocks.
        
        Args:
            text: Text potentially containing JSON in markdown
            
        Returns:
            JSON string or None
        """
        import re
        # Try to find JSON in code blocks
        pattern = r'```(?:json)?\s*(\{[\s\S]*?\})\s*```'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        
        # Try to find raw JSON
        pattern = r'(\{[\s\S]*\})'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        
        return None
    
    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and set defaults for Claude's result.
        
        Args:
            result: Raw result from Claude
            
        Returns:
            Validated result with defaults
        """
        # Set defaults for required fields
        defaults = {
            'title': 'Untitled Note',
            'category': 'misc',
            'base_tags': [],
            'has_tasks': False,
            'tasks': [],
            'summary': '',
            'content': '',
            'key_urls': [],
            'code_languages': [],
            'is_question': False,
            'detected_urgency': 'normal'
        }
        
        # Merge with defaults
        for key, default_value in defaults.items():
            if key not in result:
                result[key] = default_value
        
        # Validate category
        if result['category'] not in config.VALID_CATEGORIES:
            logger.warning(
                f"Invalid category '{result['category']}', defaulting to 'misc'"
            )
            result['category'] = 'misc'
        
        # Ensure tasks are properly formatted
        if result['has_tasks'] and result['tasks']:
            validated_tasks = []
            for task in result['tasks']:
                if isinstance(task, dict) and 'task' in task:
                    validated_tasks.append({
                        'task': task['task'],
                        'urgency': task.get('urgency', 'normal')
                    })
                elif isinstance(task, str):
                    validated_tasks.append({
                        'task': task,
                        'urgency': 'normal'
                    })
            result['tasks'] = validated_tasks
        
        return result
    
    def _create_fallback_result(self, message_text: str) -> Dict[str, Any]:
        """
        Create a fallback result if Claude processing fails.
        
        Args:
            message_text: Original message text
            
        Returns:
            Basic fallback result
        """
        from utils import truncate_text
        
        logger.warning("Using fallback result due to processing error")
        
        return {
            'title': truncate_text(message_text, max_length=50),
            'category': 'misc',
            'base_tags': ['unprocessed'],
            'has_tasks': False,
            'tasks': [],
            'summary': 'Could not automatically process this message.',
            'content': message_text,
            'key_urls': [{'url': url, 'description': url} for url in extract_urls(message_text)],
            'code_languages': detect_all_code_languages(message_text),
            'is_question': '?' in message_text,
            'detected_urgency': 'normal'
        }
