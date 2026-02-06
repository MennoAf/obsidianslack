"""
GitHub repository sync for Obsidian notes.

This module handles pushing notes to a GitHub repository,
which can then be synced to local Obsidian vault via git pull.
"""
import os
import logging
import posixpath
from typing import Optional
from pathlib import Path
from github import Github, GithubException

logger = logging.getLogger(__name__)


class GitHubSync:
    """Sync notes to GitHub repository."""
    
    def __init__(self):
        """
        Initialize GitHub client.
        
        Environment variables required:
            GITHUB_TOKEN: Personal access token with repo permissions
            GITHUB_REPO: Repository name (e.g., "username/obsidian-brain-dumps")
            GITHUB_BRANCH: Branch name (default: "main")
        """
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_name = os.getenv('GITHUB_REPO')
        self.branch = os.getenv('GITHUB_BRANCH', 'main')
        
        if not self.github_token or not self.repo_name:
            raise ValueError(
                "GITHUB_TOKEN and GITHUB_REPO environment variables must be set"
            )
        
        self.github = Github(self.github_token)
        
        try:
            self.repo = self.github.get_repo(self.repo_name)
            logger.info(f"Connected to GitHub repo: {self.repo_name}")
        except Exception as e:
            logger.error(f"Failed to connect to GitHub repo: {e}")
            raise
    
    def _safe_path(self, folder: str, filename: str) -> str:
        """Build a repo-relative path, rejecting traversal attempts."""
        path = posixpath.normpath(f"{folder}/{filename}")
        if path.startswith('..') or path.startswith('/'):
            raise ValueError(f"Invalid path: {path}")
        return path

    def write_note(
        self,
        filename: str,
        content: str,
        folder: str = "inbox",
        commit_message: Optional[str] = None
    ) -> bool:
        """
        Write a note to the GitHub repository.
        
        Args:
            filename: Name of the markdown file
            content: Full markdown content
            folder: Subfolder within repo (default: "inbox")
            commit_message: Optional custom commit message
            
        Returns:
            True if successful, False otherwise
        """
        # Construct file path
        file_path = self._safe_path(folder, filename)
        
        # Default commit message
        if not commit_message:
            commit_message = f"Add brain dump: {filename}"
        
        try:
            # Try to get existing file to check if it exists
            try:
                existing_file = self.repo.get_contents(file_path, ref=self.branch)
                
                # File exists - update it
                self.repo.update_file(
                    path=file_path,
                    message=f"Update {filename}",
                    content=content,
                    sha=existing_file.sha,
                    branch=self.branch
                )
                logger.info(f"Updated existing file in GitHub: {file_path}")
                return True
                
            except GithubException as e:
                if e.status == 404:
                    # File doesn't exist - create it
                    self.repo.create_file(
                        path=file_path,
                        message=commit_message,
                        content=content,
                        branch=self.branch
                    )
                    logger.info(f"Created new file in GitHub: {file_path}")
                    return True
                else:
                    raise
                    
        except Exception as e:
            logger.error(f"Error writing to GitHub: {e}")
            return False
    
    def append_to_file(
        self,
        filename: str,
        content: str,
        folder: str = "inbox"
    ) -> bool:
        """
        Append content to an existing file in GitHub.
        
        This is used for adding reply links to parent notes.
        
        Args:
            filename: Name of the file to append to
            content: Content to append
            folder: Subfolder within repo
            
        Returns:
            True if successful, False otherwise
        """
        file_path = self._safe_path(folder, filename)
        
        try:
            # Get existing file
            existing_file = self.repo.get_contents(file_path, ref=self.branch)
            
            # Decode current content
            current_content = existing_file.decoded_content.decode('utf-8')
            
            # Append new content
            updated_content = current_content + "\n" + content
            
            # Update file
            self.repo.update_file(
                path=file_path,
                message=f"Update {filename} - add reply link",
                content=updated_content,
                sha=existing_file.sha,
                branch=self.branch
            )
            
            logger.info(f"Appended to file in GitHub: {file_path}")
            return True
            
        except GithubException as e:
            if e.status == 404:
                logger.warning(f"File not found for append: {file_path}")
            else:
                logger.error(f"Error appending to GitHub file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error appending to GitHub: {e}")
            return False
    
    def file_exists(self, filename: str, folder: str = "inbox") -> bool:
        """
        Check if a file exists in the repository.
        
        Args:
            filename: Name of the file
            folder: Subfolder within repo
            
        Returns:
            True if file exists
        """
        file_path = self._safe_path(folder, filename)
        
        try:
            self.repo.get_contents(file_path, ref=self.branch)
            return True
        except GithubException as e:
            if e.status == 404:
                return False
            raise
    
    def list_files(self, folder: str = "inbox") -> list:
        """
        List all files in a folder.
        
        Args:
            folder: Folder path
            
        Returns:
            List of filenames
        """
        try:
            contents = self.repo.get_contents(folder, ref=self.branch)
            return [item.name for item in contents if item.type == "file"]
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def create_folder_structure(self):
        """
        Create the standard folder structure in the repository.
        
        Creates:
            - inbox/
            - code/
            - news/
            - ideas/
            - tasks/
            - journal/
            - misc/
        """
        folders = ["inbox", "code", "news", "ideas", "tasks", "journal", "misc"]
        
        for folder in folders:
            try:
                # Check if folder exists by trying to get its contents
                try:
                    self.repo.get_contents(folder, ref=self.branch)
                    logger.info(f"Folder already exists: {folder}")
                except GithubException as e:
                    if e.status == 404:
                        # Folder doesn't exist - create it with a .gitkeep file
                        self.repo.create_file(
                            path=f"{folder}/.gitkeep",
                            message=f"Create {folder} directory",
                            content="",
                            branch=self.branch
                        )
                        logger.info(f"Created folder: {folder}")
            except Exception as e:
                logger.error(f"Error creating folder {folder}: {e}")


class GitHubObsidianWriter:
    """
    Wrapper for ObsidianWriter that uses GitHub instead of local filesystem.
    
    This can be used as a drop-in replacement for the standard ObsidianWriter
    when running on Cloud Run or other stateless environments.
    """
    
    def __init__(self):
        """Initialize with GitHub sync."""
        self.github_sync = GitHubSync()
        
        # Create folder structure on first run
        try:
            self.github_sync.create_folder_structure()
        except Exception as e:
            logger.warning(f"Could not create folder structure: {e}")
    
    def write_file(self, filepath: Path, content: str) -> bool:
        """
        Write a file to GitHub repository.
        
        Args:
            filepath: Path object (only filename and parent folder are used)
            content: File content
            
        Returns:
            True if successful
        """
        folder = filepath.parent.name
        filename = filepath.name
        
        return self.github_sync.write_note(
            filename=filename,
            content=content,
            folder=folder
        )
    
    def append_to_file(self, filepath: Path, content: str) -> bool:
        """
        Append content to a file in GitHub.
        
        Args:
            filepath: Path object
            content: Content to append
            
        Returns:
            True if successful
        """
        folder = filepath.parent.name
        filename = filepath.name
        
        return self.github_sync.append_to_file(
            filename=filename,
            content=content,
            folder=folder
        )
    
    def file_exists(self, filepath: Path) -> bool:
        """
        Check if file exists in GitHub.
        
        Args:
            filepath: Path object
            
        Returns:
            True if exists
        """
        folder = filepath.parent.name
        filename = filepath.name
        
        return self.github_sync.file_exists(
            filename=filename,
            folder=folder
        )
