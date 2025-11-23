"""File writing for Obsidian vault integration."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FileWriteError(Exception):
    """Raised when file write operations fail."""
    pass


class FileWriter:
    """Handles writing markdown files to Obsidian vault."""
    
    def __init__(self, vault_path: Path, output_folder: str = "Voice Notes"):
        """
        Initialize file writer.
        
        Args:
            vault_path: Path to Obsidian vault
            output_folder: Subfolder within vault for voice notes
        """
        self.vault_path = Path(vault_path).resolve()
        self.output_folder = output_folder
        self.output_path = self.vault_path / output_folder
        
        logger.info(f"Initialized file writer for vault: {self.vault_path}")
    
    def write(self, content: str, filename: str) -> Path:
        """
        Write markdown content to file in vault.
        
        Args:
            content: Markdown content to write
            filename: Target filename
            
        Returns:
            Path to written file
            
        Raises:
            FileWriteError: If write operation fails
        """
        try:
            # Ensure output directory exists
            self._ensure_output_directory()
            
            # Get final file path, handling conflicts
            file_path = self._get_unique_path(filename)
            
            # Write content
            logger.info(f"Writing file: {file_path.name}")
            file_path.write_text(content, encoding='utf-8')
            
            # Verify write was successful
            if not file_path.exists():
                raise FileWriteError(f"File was not created: {file_path}")
            
            logger.info(f"Successfully wrote file: {file_path}")
            return file_path
            
        except Exception as e:
            raise FileWriteError(f"Failed to write file {filename}: {e}") from e
    
    def _ensure_output_directory(self) -> None:
        """
        Ensure output directory exists.
        
        Raises:
            FileWriteError: If directory cannot be created
        """
        try:
            self.output_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Output directory ready: {self.output_path}")
        except Exception as e:
            raise FileWriteError(
                f"Failed to create output directory {self.output_path}: {e}"
            ) from e
    
    def _get_unique_path(self, filename: str) -> Path:
        """
        Get unique file path, handling naming conflicts.
        
        Args:
            filename: Desired filename
            
        Returns:
            Unique file path
        """
        base_path = self.output_path / filename
        
        # If file doesn't exist, use it
        if not base_path.exists():
            return base_path
        
        # File exists, find a unique name
        stem = base_path.stem
        suffix = base_path.suffix
        counter = 1
        
        while True:
            new_path = self.output_path / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                logger.info(
                    f"File {filename} already exists, using {new_path.name} instead"
                )
                return new_path
            counter += 1
            
            # Safety check to prevent infinite loop
            if counter > 1000:
                raise FileWriteError(
                    f"Could not find unique filename for {filename} after 1000 attempts"
                )
    
    def verify_vault_access(self) -> None:
        """
        Verify vault path is accessible and writable.
        
        Raises:
            FileWriteError: If vault is not accessible
        """
        if not self.vault_path.exists():
            raise FileWriteError(f"Vault path does not exist: {self.vault_path}")
        
        if not self.vault_path.is_dir():
            raise FileWriteError(f"Vault path is not a directory: {self.vault_path}")
        
        # Test write access by attempting to create output folder
        try:
            self.output_path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise FileWriteError(
                f"No write permission for vault: {self.vault_path}"
            ) from e
        
        logger.info("Vault access verified")
    
    def get_output_path_relative(self) -> str:
        """
        Get output path relative to vault.
        
        Returns:
            Relative path string
        """
        try:
            return str(self.output_path.relative_to(self.vault_path))
        except ValueError:
            # Output path is not relative to vault
            return str(self.output_path)
