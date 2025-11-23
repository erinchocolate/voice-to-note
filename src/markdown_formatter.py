"""Markdown formatting for voice notes."""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MarkdownFormatter:
    """Formats processed text as markdown with frontmatter."""
    
    def __init__(self, add_headings: bool = False):
        """
        Initialize markdown formatter.
        
        Args:
            add_headings: Whether to attempt heading detection (experimental)
        """
        self.add_headings = add_headings
        logger.info("Initialized markdown formatter")
    
    def format(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Format text as markdown document.
        
        Args:
            text: Cleaned text content
            metadata: Metadata for frontmatter
            
        Returns:
            Complete markdown document
        """
        logger.debug("Formatting text as markdown")
        
        # Generate frontmatter
        frontmatter = self._generate_frontmatter(metadata)
        
        # Format body text
        body = self._format_body(text)
        
        # Combine frontmatter and body
        markdown = f"{frontmatter}\n\n{body}\n"
        
        logger.info("Markdown formatting completed")
        return markdown
    
    def _generate_frontmatter(self, metadata: Dict[str, Any]) -> str:
        """
        Generate YAML frontmatter from metadata.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Formatted frontmatter
        """
        lines = ["---"]
        
        # Add creation timestamp (from audio file)
        if 'created' in metadata:
            created = metadata['created']
            if isinstance(created, datetime):
                lines.append(f"created: {created.isoformat()}")
            else:
                lines.append(f"created: {created}")
        
        # Add source filename
        if 'source' in metadata:
            lines.append(f"source: {metadata['source']}")
        
        # Add processing timestamp
        processed = metadata.get('processed', datetime.now())
        if isinstance(processed, datetime):
            lines.append(f"processed: {processed.isoformat()}")
        else:
            lines.append(f"processed: {processed}")
        
        # Add duration
        if 'duration' in metadata:
            lines.append(f"duration: {metadata['duration']}")
        
        # Add any custom metadata
        for key, value in metadata.items():
            if key not in ['created', 'source', 'processed', 'duration']:
                lines.append(f"{key}: {value}")
        
        lines.append("---")
        
        return "\n".join(lines)
    
    def _format_body(self, text: str) -> str:
        """
        Format body text.
        
        Args:
            text: Input text
            
        Returns:
            Formatted text
        """
        # For now, return text as-is
        # GPT has already organized it into paragraphs
        # Future enhancement: detect and add markdown headings
        
        if self.add_headings:
            # Experimental: attempt to detect topics for headings
            # This would require additional GPT processing
            logger.debug("Heading detection not yet implemented")
        
        return text.strip()
    
    @staticmethod
    def generate_filename(
        pattern: str,
        metadata: Dict[str, Any],
        extension: str = ".md"
    ) -> str:
        """
        Generate filename from pattern and metadata.
        
        Args:
            pattern: Filename pattern with placeholders
            metadata: Metadata for substitution
            extension: File extension (default: .md)
            
        Returns:
            Generated filename
        """
        # Get datetime for formatting
        dt = metadata.get('created')
        if not isinstance(dt, datetime):
            dt = datetime.now()
        
        # Build replacements
        replacements = {
            'date': dt.strftime('%Y-%m-%d'),
            'time': dt.strftime('%H%M%S'),
            'datetime': dt.strftime('%Y-%m-%d-%H%M%S'),
            'year': dt.strftime('%Y'),
            'month': dt.strftime('%m'),
            'day': dt.strftime('%d'),
            'hour': dt.strftime('%H'),
            'minute': dt.strftime('%M'),
            'second': dt.strftime('%S'),
        }
        
        # Add original filename if available
        if 'source' in metadata:
            source = Path(metadata['source'])
            replacements['original_name'] = source.stem
            replacements['original_filename'] = source.name
        
        # Apply replacements
        filename = pattern
        for key, value in replacements.items():
            filename = filename.replace(f'{{{key}}}', str(value))
        
        # Ensure it has the correct extension
        if not filename.endswith(extension):
            filename += extension
        
        # Sanitize filename (remove invalid characters)
        filename = MarkdownFormatter._sanitize_filename(filename)
        
        return filename
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing invalid characters.
        
        Args:
            filename: Input filename
            
        Returns:
            Sanitized filename
        """
        # Replace invalid characters with underscore
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Ensure filename is not empty
        if not filename:
            filename = "voice-note.md"
        
        return filename
