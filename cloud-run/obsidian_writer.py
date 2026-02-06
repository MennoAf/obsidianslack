"""
Obsidian note generation and file writing.
"""
import logging
import os
from filelock import FileLock
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import config
from utils import (
    generate_filename,
    format_timestamp,
    format_tags_for_frontmatter,
    sanitize_for_yaml,
    extract_domain
)
from tag_generator import TagGenerator

logger = logging.getLogger(__name__)


class ObsidianWriter:
    """Generate and write Obsidian notes."""

    def __init__(self):
        """Initialize the Obsidian writer."""
        self.tag_generator = TagGenerator()
        self.vault_path = config.CLAUDE_FOLDER_PATH
        self.template_env = None
        self.use_templates = self._setup_template_engine()

    def _setup_template_engine(self) -> bool:
        """
        Set up Jinja2 template environment.

        Returns:
            True if templates loaded successfully, False to use fallback
        """
        # Determine template directory
        template_dir = Path(__file__).parent / 'templates'

        # Allow environment variable override
        env_dir = os.getenv('NOTE_TEMPLATE_DIR')
        if env_dir:
            template_dir = Path(env_dir)

        if not template_dir.exists():
            logger.warning(f"Template directory not found: {template_dir}")
            logger.info("Using fallback note generation")
            return False

        try:
            self.template_env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                trim_blocks=True,
                lstrip_blocks=True
            )
            logger.info(f"✓ Loaded Jinja2 templates from: {template_dir}")
            return True
        except Exception as e:
            logger.warning(f"Failed to setup template engine: {e}")
            logger.info("Using fallback note generation")
            return False

    def create_note(
        self,
        processed_data: Dict[str, Any],
        slack_message: Dict[str, Any],
        parent_note_filename: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create an Obsidian note from processed data.
        
        Args:
            processed_data: Data from Claude processor
            slack_message: Original Slack message dict
            parent_note_filename: If this is a reply, the parent note's filename
            
        Returns:
            Dictionary with 'filepath' and 'filename'
        """
        timestamp = datetime.now()
        
        # Generate comprehensive tags
        tags = self.tag_generator.generate_tags(
            message_text=processed_data['content'],
            claude_base_tags=processed_data['base_tags'],
            code_languages=processed_data['code_languages'],
            is_question=processed_data['is_question']
        )
        
        # Extract source domain if URLs present
        source_domain = None
        if processed_data['key_urls']:
            first_url = processed_data['key_urls'][0].get('url', '')
            source_domain = extract_domain(first_url)
        
        # Generate filename
        filename = generate_filename(processed_data['title'], timestamp)
        
        # Determine priority
        priority = self._determine_priority(
            processed_data['detected_urgency'],
            processed_data['has_tasks']
        )
        
        # Build note using Jinja2 template or fallback
        if self.use_templates:
            full_note = self._render_note_from_template(
                title=processed_data['title'],
                timestamp=timestamp,
                tags=tags,
                category=processed_data['category'],
                source_domain=source_domain,
                slack_ts=slack_message.get('ts'),
                slack_thread_ts=slack_message.get('thread_ts'),
                priority=priority,
                parent_note=parent_note_filename,
                summary=processed_data['summary'],
                content=processed_data['content'],
                has_tasks=processed_data['has_tasks'],
                tasks=processed_data['tasks'],
                key_urls=processed_data['key_urls']
            )
        else:
            # Fallback to original method
            frontmatter = self._build_frontmatter(
                title=processed_data['title'],
                timestamp=timestamp,
                tags=tags,
                category=processed_data['category'],
                source_domain=source_domain,
                slack_ts=slack_message.get('ts'),
                slack_thread_ts=slack_message.get('thread_ts'),
                priority=priority,
                parent_note=parent_note_filename
            )

            content = self._build_content(
                title=processed_data['title'],
                summary=processed_data['summary'],
                content=processed_data['content'],
                has_tasks=processed_data['has_tasks'],
                tasks=processed_data['tasks'],
                key_urls=processed_data['key_urls'],
                parent_note=parent_note_filename
            )

            full_note = frontmatter + "\n" + content
        
        # Determine where to save (inbox folder)
        filepath = self.vault_path / 'inbox' / filename
        
        # Write file
        self._write_file(filepath, full_note)
        
        # If this is a reply, update parent note
        if parent_note_filename:
            self._append_reply_to_parent(parent_note_filename, filename, timestamp)
        
        logger.info(f"Created note: {filename}")
        
        return {
            'filepath': str(filepath),
            'filename': filename
        }

    def _render_note_from_template(
        self,
        title: str,
        timestamp: datetime,
        tags: list,
        category: str,
        source_domain: Optional[str],
        slack_ts: str,
        slack_thread_ts: Optional[str],
        priority: str,
        parent_note: Optional[str],
        summary: str,
        content: str,
        has_tasks: bool,
        tasks: list,
        key_urls: list
    ) -> str:
        """
        Render note using Jinja2 template.

        Returns:
            Rendered note content
        """
        try:
            # Get template name from env var or use default
            template_name = os.getenv('NOTE_TEMPLATE', 'note_template.md.j2')
            template = self.template_env.get_template(template_name)

            # Prepare parent note name (remove .md extension for wikilink)
            parent_note_name = None
            if parent_note:
                parent_note_name = parent_note.replace('.md', '')

            # Render template
            return template.render(
                created=format_timestamp(timestamp),
                title=sanitize_for_yaml(title),
                tags=tags,
                category=sanitize_for_yaml(category),
                source_domain=sanitize_for_yaml(source_domain) if source_domain else None,
                slack_ts=sanitize_for_yaml(str(slack_ts)),
                slack_thread_ts=sanitize_for_yaml(str(slack_thread_ts)) if slack_thread_ts else None,
                priority=sanitize_for_yaml(str(priority)),
                parent_note=parent_note_name,
                summary=summary,
                content=content,
                has_tasks=has_tasks,
                tasks=tasks,
                key_urls=key_urls
            )
        except TemplateNotFound as e:
            logger.error(f"Template not found: {e}. Falling back to default.")
            # Fall back to original methods
            self.use_templates = False
            frontmatter = self._build_frontmatter(
                title, timestamp, tags, category, source_domain,
                slack_ts, slack_thread_ts, priority, parent_note
            )
            content_section = self._build_content(
                title, summary, content, has_tasks, tasks, key_urls, parent_note
            )
            return frontmatter + "\n" + content_section
        except Exception as e:
            logger.error(f"Error rendering template: {e}. Falling back to default.")
            # Fall back to original methods
            self.use_templates = False
            frontmatter = self._build_frontmatter(
                title, timestamp, tags, category, source_domain,
                slack_ts, slack_thread_ts, priority, parent_note
            )
            content_section = self._build_content(
                title, summary, content, has_tasks, tasks, key_urls, parent_note
            )
            return frontmatter + "\n" + content_section

    def _build_frontmatter(
        self,
        title: str,
        timestamp: datetime,
        tags: list,
        category: str,
        source_domain: Optional[str],
        slack_ts: str,
        slack_thread_ts: Optional[str],
        priority: str,
        parent_note: Optional[str]
    ) -> str:
        """
        Build YAML frontmatter for the note.
        
        Args:
            title: Note title
            timestamp: Creation timestamp
            tags: List of tags
            category: Note category
            source_domain: Domain of primary URL
            slack_ts: Slack message timestamp
            slack_thread_ts: Slack thread timestamp
            priority: Priority level
            parent_note: Parent note filename if reply
            
        Returns:
            Formatted YAML frontmatter
        """
        frontmatter = "---\n"
        frontmatter += f"created: {format_timestamp(timestamp)}\n"
        frontmatter += f"title: {sanitize_for_yaml(title)}\n"
        frontmatter += "tags:\n"
        frontmatter += format_tags_for_frontmatter(tags) + "\n"
        frontmatter += f"category: {sanitize_for_yaml(category)}\n"
        frontmatter += "source: slack\n"

        if source_domain:
            frontmatter += f"source_domain: {sanitize_for_yaml(source_domain)}\n"

        frontmatter += f"slack_ts: {sanitize_for_yaml(str(slack_ts))}\n"

        if slack_thread_ts:
            frontmatter += f"slack_thread_ts: {sanitize_for_yaml(str(slack_thread_ts))}\n"

        frontmatter += "status: unprocessed\n"
        frontmatter += f"priority: {sanitize_for_yaml(str(priority))}\n"
        
        if parent_note:
            # Remove .md extension for wikilink
            parent_name = parent_note.replace('.md', '')
            frontmatter += f"reply_to: \"[[{parent_name}]]\"\n"
        
        frontmatter += "---"
        
        return frontmatter
    
    def _build_content(
        self,
        title: str,
        summary: str,
        content: str,
        has_tasks: bool,
        tasks: list,
        key_urls: list,
        parent_note: Optional[str]
    ) -> str:
        """
        Build the main content of the note.
        
        Args:
            title: Note title
            summary: Brief summary
            content: Main content
            has_tasks: Whether note has tasks
            tasks: List of task objects
            key_urls: List of important URLs
            parent_note: Parent note filename if reply
            
        Returns:
            Formatted note content
        """
        note_content = f"\n# {title}\n\n"
        
        # Add reply indicator if this is a reply
        if parent_note:
            parent_name = parent_note.replace('.md', '')
            note_content += f"**In response to:** [[{parent_name}]]\n\n"
        
        # Add summary
        if summary:
            note_content += f"## Summary\n{summary}\n\n"
        
        # Add main content
        note_content += f"## Content\n{content}\n"
        
        # Add tasks section
        if has_tasks and tasks:
            note_content += "\n## Tasks\n"
            for task_obj in tasks:
                task_text = task_obj.get('task', '')
                urgency = task_obj.get('urgency', 'normal')
                
                # Add fire emoji for high priority
                prefix = "🔥 " if urgency == 'high' else ""
                note_content += f"- [ ] {prefix}{task_text}\n"
        
        # Add key references
        if key_urls:
            note_content += "\n## Key References\n"
            for url_obj in key_urls:
                url = url_obj.get('url', '')
                description = url_obj.get('description', url)
                note_content += f"- [{description}]({url})\n"
        
        return note_content
    
    def _determine_priority(self, detected_urgency: str, has_tasks: bool) -> str:
        """
        Determine priority level for the note.
        
        Args:
            detected_urgency: Urgency detected by Claude
            has_tasks: Whether note contains tasks
            
        Returns:
            Priority level: high, medium, low, or normal
        """
        if detected_urgency == 'high':
            return 'high'
        elif detected_urgency == 'medium' and has_tasks:
            return 'medium'
        elif detected_urgency == 'low':
            return 'low'
        else:
            return 'normal'
    
    def _write_file(self, filepath: Path, content: str):
        """
        Write content to a file, handling filename collisions.

        Args:
            filepath: Path to write to
            content: Content to write
        """
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Check for filename collision
            original_filepath = filepath
            counter = 2
            while filepath.exists():
                # Append counter before extension
                stem = original_filepath.stem
                suffix = original_filepath.suffix
                filepath = original_filepath.parent / f"{stem}_{counter}{suffix}"
                counter += 1

            if filepath != original_filepath:
                logger.warning(f"Filename collision detected. Writing to {filepath.name} instead of {original_filepath.name}")

            filepath.write_text(content, encoding='utf-8')
            logger.info(f"Wrote file: {filepath}")
        except Exception as e:
            logger.error(f"Error writing file {filepath}: {e}")
            raise
    
    def _append_reply_to_parent(
        self,
        parent_filename: str,
        reply_filename: str,
        timestamp: datetime
    ):
        """
        Append a reply reference to the parent note.
        
        Args:
            parent_filename: Parent note filename
            reply_filename: Reply note filename
            timestamp: Reply timestamp
        """
        # Search for parent file in inbox and other folders
        parent_path = None
        for subfolder in config.OBSIDIAN_SUBFOLDERS:
            potential_path = self.vault_path / subfolder / parent_filename
            if potential_path.exists():
                parent_path = potential_path
                break
        
        if not parent_path:
            logger.warning(f"Could not find parent note: {parent_filename}")
            return
        
        try:
            # Use cross-platform file locking to prevent race conditions
            lock_path = f"{parent_path}.lock"
            lock = FileLock(lock_path, timeout=10)

            with lock:
                # Read existing content
                content = parent_path.read_text(encoding='utf-8')

                # Add reply link
                reply_name = reply_filename.replace('.md', '')
                reply_line = (
                    f"- [[{reply_name}]] - "
                    f"*{format_timestamp(timestamp)}*\n"
                )

                # Find or create Replies section and insert reply
                replies_header = "## Replies\n"
                if replies_header in content:
                    # Find position right after "## Replies\n"
                    pos = content.index(replies_header) + len(replies_header)
                    # Insert reply at that position
                    content = content[:pos] + reply_line + content[pos:]
                else:
                    # Create Replies section at end
                    content += "\n\n" + replies_header + reply_line

                # Write back
                parent_path.write_text(content, encoding='utf-8')

                logger.info(f"Updated parent note with reply: {parent_filename}")

        except Exception as e:
            logger.error(f"Error updating parent note {parent_filename}: {e}")
    
    def get_note_by_slack_ts(self, slack_ts: str) -> Optional[str]:
        """
        Find a note by its Slack timestamp.
        
        Args:
            slack_ts: Slack message timestamp
            
        Returns:
            Note filename or None if not found
        """
        # Search all subfolders
        for subfolder in config.OBSIDIAN_SUBFOLDERS:
            folder_path = self.vault_path / subfolder
            if not folder_path.exists():
                continue
            
            for note_path in folder_path.glob('*.md'):
                try:
                    content = note_path.read_text(encoding='utf-8')
                    if f"slack_ts: {slack_ts}" in content:
                        return note_path.name
                except Exception:
                    continue
        
        return None
