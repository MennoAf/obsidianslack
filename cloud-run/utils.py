"""
Utility functions for the Slack-Obsidian Brain Dump application.
"""
import re
from urllib.parse import urlparse
from datetime import datetime
from typing import List, Optional
import pytz


def extract_urls(text: str) -> List[str]:
    """
    Extract all URLs from text.
    
    Args:
        text: Text to search for URLs
        
    Returns:
        List of URLs found in the text
    """
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.findall(text)


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.
    
    Args:
        url: Full URL string
        
    Returns:
        Domain name (e.g., 'github.com') or None if invalid
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return None


def clean_filename(title: str, max_length: int = 50) -> str:
    """
    Clean a title to make it filesystem-safe.
    
    Args:
        title: Original title
        max_length: Maximum length for filename
        
    Returns:
        Cleaned filename-safe string
    """
    # Convert to lowercase
    cleaned = title.lower()
    
    # Replace spaces with hyphens
    cleaned = re.sub(r'\s+', '-', cleaned)
    
    # Remove special characters except hyphens
    cleaned = re.sub(r'[^a-z0-9\-]', '', cleaned)
    
    # Remove multiple consecutive hyphens
    cleaned = re.sub(r'-+', '-', cleaned)
    
    # Trim hyphens from start and end
    cleaned = cleaned.strip('-')
    
    # Limit length
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip('-')
    
    return cleaned or 'untitled'


def generate_filename(title: str, timestamp: datetime) -> str:
    """
    Generate a filename for an Obsidian note.
    
    Args:
        title: Note title
        timestamp: Creation timestamp
        
    Returns:
        Filename in format: YYYY-MM-DD-title.md
    """
    date_prefix = timestamp.strftime('%Y-%m-%d')
    clean_title = clean_filename(title)
    return f"{date_prefix}-{clean_title}.md"


def format_timestamp(timestamp: datetime, timezone: str = 'UTC') -> str:
    """
    Format timestamp for Obsidian frontmatter.
    
    Args:
        timestamp: Datetime object
        timezone: Timezone string (default: UTC)
        
    Returns:
        Formatted timestamp string: YYYY-MM-DD HH:MM
    """
    if timestamp.tzinfo is None:
        timestamp = pytz.utc.localize(timestamp)
    
    tz = pytz.timezone(timezone)
    local_time = timestamp.astimezone(tz)
    return local_time.strftime('%Y-%m-%d %H:%M')


def detect_code_language_from_block(code_block: str) -> Optional[str]:
    """
    Detect programming language from a code block.
    
    Args:
        code_block: Code block text (including ``` markers)
        
    Returns:
        Language name or None
    """
    # Extract language from markdown code fence
    match = re.match(r'^```(\w+)', code_block)
    if match:
        return match.group(1).lower()
    
    # Try to detect from content (basic heuristics)
    code_lower = code_block.lower()
    
    if 'def ' in code_lower or 'import ' in code_lower or '__init__' in code_lower:
        return 'python'
    elif 'function ' in code_lower or 'const ' in code_lower or '=>' in code_lower:
        return 'javascript'
    elif 'interface ' in code_lower and (':' in code_lower or 'extends' in code_lower):
        return 'typescript'
    elif 'fn ' in code_lower or 'let mut' in code_lower:
        return 'rust'
    elif 'func ' in code_lower and ':=' in code_lower:
        return 'go'
    elif 'SELECT ' in code_block or 'INSERT ' in code_block or 'UPDATE ' in code_block:
        return 'sql'
    
    return None


def extract_code_blocks(text: str) -> List[str]:
    """
    Extract all code blocks from markdown text.
    
    Args:
        text: Markdown text
        
    Returns:
        List of code blocks (including ``` markers)
    """
    pattern = re.compile(r'```[\s\S]*?```', re.MULTILINE)
    return pattern.findall(text)


def detect_all_code_languages(text: str) -> List[str]:
    """
    Detect all programming languages in a text.
    
    Args:
        text: Text containing code blocks
        
    Returns:
        List of detected language names
    """
    code_blocks = extract_code_blocks(text)
    languages = []
    
    for block in code_blocks:
        lang = detect_code_language_from_block(block)
        if lang and lang not in languages:
            languages.append(lang)
    
    return languages


def escape_markdown(text: str) -> str:
    """
    Escape markdown special characters for safe inclusion in frontmatter.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    # Escape characters that have special meaning in YAML
    text = text.replace('"', '\\"')
    text = text.replace(':', '\\:')
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rstrip() + suffix


def format_tags_for_frontmatter(tags: List[str]) -> str:
    """
    Format tags for YAML frontmatter.

    Args:
        tags: List of tag strings

    Returns:
        Formatted YAML list of tags
    """
    if not tags:
        return "  - claude"

    formatted_tags = []
    for tag in sorted(tags):
        # Ensure tags don't have leading hashtags
        tag = tag.lstrip('#')

        # Quote tags containing YAML special characters
        if any(c in tag for c in [':', '#', '[', ']', '{', '}', '!', '&', '*', ',', '>', '|', '-', '?', '%']):
            tag = tag.replace('"', '\\"')  # Escape quotes
            tag = f'"{tag}"'

        formatted_tags.append(f"  - {tag}")

    return '\n'.join(formatted_tags)


def parse_slack_timestamp(ts: str) -> datetime:
    """
    Parse Slack timestamp to datetime.

    Args:
        ts: Slack timestamp string (e.g., '1234567890.123456')

    Returns:
        Datetime object

    Raises:
        ValueError: If timestamp is not a valid float
    """
    # Slack timestamps are Unix timestamps with microseconds
    try:
        timestamp_float = float(ts)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid Slack timestamp format: '{ts}'. Expected float string.") from e

    return datetime.fromtimestamp(timestamp_float, tz=pytz.utc)


def is_thread_reply(message: dict) -> bool:
    """
    Check if a Slack message is a thread reply.
    
    Args:
        message: Slack message dict
        
    Returns:
        True if message is a reply in a thread
    """
    return (
        'thread_ts' in message and 
        message.get('thread_ts') != message.get('ts')
    )


def sanitize_for_yaml(value: str) -> str:
    """
    Sanitize a string for safe inclusion in YAML frontmatter.

    Args:
        value: String to sanitize

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value)

    # Always quote if contains newlines, special chars, or is empty
    special = [':', '#', '-', '[', ']', '{', '}', '|', '>', '*', '&', '!', '%', '?', '\n', '\r']

    if any(char in value for char in special) or not value.strip():
        # Escape backslashes first (must be done before other escapes)
        value = value.replace('\\', '\\\\')
        # Escape quotes
        value = value.replace('"', '\\"')
        # Escape newlines
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        return f'"{value}"'

    return value
