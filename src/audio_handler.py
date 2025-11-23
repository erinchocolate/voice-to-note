"""Audio file handling and validation for Voice-to-Note application."""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

logger = logging.getLogger(__name__)


class AudioFileError(Exception):
    """Raised when audio file is invalid or cannot be processed."""
    pass


class AudioFile:
    """Represents an audio file with metadata."""
    
    def __init__(self, path: Path):
        """
        Initialize audio file.
        
        Args:
            path: Path to audio file
            
        Raises:
            AudioFileError: If file is invalid or cannot be read
        """
        self.path = Path(path).resolve()
        self.metadata: Dict[str, Any] = {}
        
        # Validate and extract metadata
        self._validate()
        self._extract_metadata()
    
    def _validate(self) -> None:
        """
        Validate audio file exists and is accessible.
        
        Raises:
            AudioFileError: If file is invalid
        """
        if not self.path.exists():
            raise AudioFileError(f"Audio file not found: {self.path}")
        
        if not self.path.is_file():
            raise AudioFileError(f"Path is not a file: {self.path}")
        
        if self.path.stat().st_size == 0:
            raise AudioFileError(f"Audio file is empty: {self.path}")
        
        # Check file extension
        allowed_extensions = {'.m4a', '.mp3', '.wav', '.flac', '.ogg'}
        if self.path.suffix.lower() not in allowed_extensions:
            logger.warning(
                f"File {self.path.name} has unexpected extension {self.path.suffix}. "
                f"Supported: {allowed_extensions}"
            )
    
    def _extract_metadata(self) -> None:
        """Extract metadata from audio file using pydub."""
        try:
            # Load audio file
            audio = AudioSegment.from_file(str(self.path))
            
            # Extract metadata
            self.metadata = {
                'duration_ms': len(audio),
                'duration_seconds': len(audio) / 1000,
                'channels': audio.channels,
                'sample_width': audio.sample_width,
                'frame_rate': audio.frame_rate,
                'frame_width': audio.frame_width,
                'file_size_bytes': self.path.stat().st_size,
                'file_size_mb': self.path.stat().st_size / (1024 * 1024),
                'filename': self.path.name,
                'stem': self.path.stem,
                'extension': self.path.suffix,
            }
            
            # Add modification time
            mtime = self.path.stat().st_mtime
            self.metadata['modified_date'] = datetime.fromtimestamp(mtime)
            
            logger.info(
                f"Loaded audio file: {self.path.name} "
                f"({self.get_duration_formatted()}, "
                f"{self.metadata['file_size_mb']:.2f} MB)"
            )
            
        except CouldntDecodeError as e:
            raise AudioFileError(
                f"Could not decode audio file {self.path.name}. "
                "Ensure ffmpeg is installed and the file is a valid audio file."
            ) from e
        except Exception as e:
            raise AudioFileError(
                f"Failed to extract metadata from {self.path.name}: {e}"
            ) from e
    
    def get_duration_formatted(self) -> str:
        """
        Get formatted duration string.
        
        Returns:
            Duration in format "5m 23s" or "1h 2m 30s"
        """
        duration_seconds = int(self.metadata.get('duration_seconds', 0))
        td = timedelta(seconds=duration_seconds)
        
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        seconds = td.seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_size_formatted(self) -> str:
        """
        Get formatted file size string.
        
        Returns:
            Size in format "5.2 MB" or "523 KB"
        """
        size_bytes = self.metadata.get('file_size_bytes', 0)
        
        if size_bytes >= 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes} bytes"
    
    def __repr__(self) -> str:
        """String representation of audio file."""
        return (
            f"AudioFile(path={self.path.name}, "
            f"duration={self.get_duration_formatted()}, "
            f"size={self.get_size_formatted()})"
        )


class AudioHandler:
    """Handles audio file validation and queue management."""
    
    def __init__(self):
        """Initialize audio handler."""
        self.queue: list[AudioFile] = []
    
    def add_file(self, path: Path) -> AudioFile:
        """
        Add an audio file to the processing queue.
        
        Args:
            path: Path to audio file
            
        Returns:
            AudioFile object
            
        Raises:
            AudioFileError: If file is invalid
        """
        audio_file = AudioFile(path)
        self.queue.append(audio_file)
        logger.info(f"Added {audio_file.path.name} to processing queue")
        return audio_file
    
    def add_files(self, paths: list[Path]) -> list[AudioFile]:
        """
        Add multiple audio files to the processing queue.
        
        Args:
            paths: List of paths to audio files
            
        Returns:
            List of successfully added AudioFile objects
        """
        added_files = []
        failed_files = []
        
        for path in paths:
            try:
                audio_file = self.add_file(path)
                added_files.append(audio_file)
            except AudioFileError as e:
                logger.error(f"Failed to add {path}: {e}")
                failed_files.append((path, str(e)))
        
        if failed_files:
            logger.warning(
                f"Failed to add {len(failed_files)} of {len(paths)} files"
            )
        
        return added_files
    
    def clear_queue(self) -> None:
        """Clear the processing queue."""
        self.queue.clear()
        logger.info("Cleared processing queue")
    
    def get_queue_size(self) -> int:
        """
        Get number of files in queue.
        
        Returns:
            Queue size
        """
        return len(self.queue)
    
    def get_total_duration(self) -> float:
        """
        Get total duration of all files in queue.
        
        Returns:
            Total duration in seconds
        """
        return sum(f.metadata.get('duration_seconds', 0) for f in self.queue)
    
    def get_queue_summary(self) -> Dict[str, Any]:
        """
        Get summary of queue contents.
        
        Returns:
            Dictionary with queue statistics
        """
        total_duration = self.get_total_duration()
        total_size = sum(f.metadata.get('file_size_bytes', 0) for f in self.queue)
        
        return {
            'file_count': len(self.queue),
            'total_duration_seconds': total_duration,
            'total_duration_formatted': self._format_seconds(total_duration),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'files': [
                {
                    'name': f.path.name,
                    'duration': f.get_duration_formatted(),
                    'size': f.get_size_formatted()
                }
                for f in self.queue
            ]
        }
    
    @staticmethod
    def _format_seconds(seconds: float) -> str:
        """Format seconds into human-readable string."""
        seconds = int(seconds)
        td = timedelta(seconds=seconds)
        
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        secs = td.seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
