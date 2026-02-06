"""
Tag generation logic for Slack-Obsidian Brain Dump application.
"""
from typing import List, Set
import re
import config
from utils import extract_urls, extract_domain, extract_code_blocks


class TagGenerator:
    """Generate tags for notes based on content, URLs, and keywords."""
    
    def __init__(self):
        """Initialize the tag generator with configuration rules."""
        self.tag_rules = config.TAG_RULES
    
    def generate_tags(
        self,
        message_text: str,
        claude_base_tags: List[str],
        code_languages: List[str],
        is_question: bool = False
    ) -> List[str]:
        """
        Generate comprehensive tags for a note.
        
        Args:
            message_text: Original Slack message text
            claude_base_tags: Tags suggested by Claude
            code_languages: Programming languages detected
            is_question: Whether the message contains a question
            
        Returns:
            Sorted list of unique tags
        """
        tags: Set[str] = {'claude'}  # Always include claude tag
        
        # Add Claude's suggested tags
        tags.update(claude_base_tags)
        
        # Add domain-based tags
        tags.update(self._generate_domain_tags(message_text))
        
        # Add code language tags
        tags.update(self._generate_code_language_tags(code_languages))
        
        # Add keyword-based tags
        tags.update(self._generate_keyword_tags(message_text))
        
        # Add content type tags
        tags.update(self._generate_content_type_tags(message_text, is_question))
        
        # Return sorted list
        return sorted(list(tags))
    
    def _generate_domain_tags(self, text: str) -> Set[str]:
        """
        Generate tags based on URLs in the text.
        
        Args:
            text: Text to search for URLs
            
        Returns:
            Set of domain-based tags
        """
        tags = set()
        urls = extract_urls(text)
        
        for url in urls:
            domain = extract_domain(url)
            if not domain:
                continue
            
            # Check if domain has predefined tags
            if domain in self.tag_rules['domains']:
                tags.update(self.tag_rules['domains'][domain])
            else:
                # Generate generic source tag from domain
                clean_domain = self._clean_domain(domain)
                tags.add(f'source/{clean_domain}')
        
        return tags
    
    def _generate_code_language_tags(self, languages: List[str]) -> Set[str]:
        """
        Generate tags based on detected programming languages.
        
        Args:
            languages: List of programming language names
            
        Returns:
            Set of code language tags
        """
        tags = set()
        
        for lang in languages:
            lang_lower = lang.lower()
            if lang_lower in self.tag_rules['code_languages']:
                tags.update(self.tag_rules['code_languages'][lang_lower])
        
        return tags
    
    def _generate_keyword_tags(self, text: str) -> Set[str]:
        """
        Generate tags based on keywords in the text.
        
        Args:
            text: Text to search for keywords
            
        Returns:
            Set of keyword-based tags
        """
        tags = set()
        text_lower = text.lower()
        
        for keyword, keyword_tags in self.tag_rules['keywords'].items():
            # Use word boundaries to avoid partial matches
            if f' {keyword} ' in f' {text_lower} ' or text_lower.startswith(keyword) or text_lower.endswith(keyword):
                tags.update(keyword_tags)
        
        return tags
    
    def _generate_content_type_tags(self, text: str, is_question: bool) -> Set[str]:
        """
        Generate tags based on content type.
        
        Args:
            text: Text to analyze
            is_question: Whether text contains a question
            
        Returns:
            Set of content type tags
        """
        tags = set()
        
        # Check for code blocks
        if '```' in text:
            tags.update(self.tag_rules['content_types']['contains_code_block'])
        
        # Check for URLs
        if 'http' in text:
            tags.update(self.tag_rules['content_types']['contains_url'])
        
        # Check for questions
        if is_question or '?' in text:
            tags.update(self.tag_rules['content_types']['contains_question'])
        
        # Check for lists (bullet points or numbered)
        if re_check_list(text):
            tags.update(self.tag_rules['content_types']['contains_list'])

        return tags

    def _clean_domain(self, domain: str) -> str:
        """
        Clean a domain name by removing common TLDs and www prefix.
        Only strips TLDs from the end to avoid mangling domains like 'common.org'.

        Args:
            domain: Domain name to clean

        Returns:
            Cleaned domain name
        """
        # Remove www. prefix
        domain = re.sub(r'^www\.', '', domain)
        # Remove common TLDs from the end only
        domain = re.sub(r'\.(com|org|io|net|dev|co|ai|edu|gov)$', '', domain)
        return domain


def re_check_list(text: str) -> bool:
    """
    Check if text contains list formatting.
    
    Args:
        text: Text to check
        
    Returns:
        True if text contains lists
    """
    import re
    # Check for markdown lists or numbered lists
    list_patterns = [
        r'^\s*[-*+]\s+',  # Bullet lists
        r'^\s*\d+\.\s+',  # Numbered lists
    ]
    
    for pattern in list_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return True
    
    return False
