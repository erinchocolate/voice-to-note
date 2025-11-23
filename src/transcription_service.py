"""Transcription service using OpenAI Whisper API."""

import logging
import time
from pathlib import Path
from typing import Optional
from openai import OpenAI, APIError, RateLimitError, APIConnectionError

logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    """Raised when transcription fails."""
    pass


class TranscriptionService:
    """Handles audio transcription using OpenAI Whisper API."""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    def __init__(self, api_key: str, model: str = "whisper-1", language: Optional[str] = None):
        """
        Initialize transcription service.
        
        Args:
            api_key: OpenAI API key
            model: Whisper model to use (default: whisper-1)
            language: Optional language code (e.g., 'en', 'es')
        """
        self.api_key = api_key
        self.model = model
        self.language = language
        self.client = OpenAI(api_key=api_key)
        
        logger.info(f"Initialized transcription service with model {model}")
    
    def transcribe(self, audio_path: Path) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text
            
        Raises:
            TranscriptionError: If transcription fails
        """
        logger.info(f"Starting transcription of {audio_path.name}")
        
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                return self._transcribe_with_retry(audio_path, attempt)
            except RateLimitError as e:
                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * (2 ** (attempt - 1))  # Exponential backoff
                    logger.warning(
                        f"Rate limit hit on attempt {attempt}/{self.MAX_RETRIES}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                else:
                    raise TranscriptionError(
                        f"Rate limit exceeded after {self.MAX_RETRIES} attempts. "
                        "Please try again later."
                    ) from e
            except APIConnectionError as e:
                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * attempt
                    logger.warning(
                        f"Connection error on attempt {attempt}/{self.MAX_RETRIES}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                else:
                    raise TranscriptionError(
                        f"Connection failed after {self.MAX_RETRIES} attempts. "
                        "Please check your internet connection."
                    ) from e
            except APIError as e:
                raise TranscriptionError(
                    f"OpenAI API error: {e}"
                ) from e
            except Exception as e:
                raise TranscriptionError(
                    f"Unexpected error during transcription: {e}"
                ) from e
        
        raise TranscriptionError("Transcription failed after all retry attempts")
    
    def _transcribe_with_retry(self, audio_path: Path, attempt: int) -> str:
        """
        Perform a single transcription attempt.
        
        Args:
            audio_path: Path to audio file
            attempt: Current attempt number
            
        Returns:
            Transcribed text
        """
        logger.debug(f"Transcription attempt {attempt} for {audio_path.name}")
        
        # Open and transcribe file
        with open(audio_path, 'rb') as audio_file:
            # Prepare transcription parameters
            params = {
                'model': self.model,
                'file': audio_file,
            }
            
            # Add optional language parameter
            if self.language:
                params['language'] = self.language
            
            # Call Whisper API
            transcript = self.client.audio.transcriptions.create(**params)
        
        # Extract text from response
        text = transcript.text.strip()
        
        if not text:
            raise TranscriptionError("Transcription returned empty text")
        
        word_count = len(text.split())
        logger.info(
            f"Successfully transcribed {audio_path.name} "
            f"({word_count} words, attempt {attempt})"
        )
        
        return text
    
    def estimate_cost(self, duration_seconds: float) -> float:
        """
        Estimate transcription cost in USD.
        
        Args:
            duration_seconds: Audio duration in seconds
            
        Returns:
            Estimated cost in USD
        """
        # OpenAI Whisper pricing: $0.006 per minute
        minutes = duration_seconds / 60
        return minutes * 0.006
    
    def validate_file_size(self, audio_path: Path) -> None:
        """
        Validate that audio file is within API limits.
        
        Args:
            audio_path: Path to audio file
            
        Raises:
            TranscriptionError: If file is too large
        """
        # OpenAI Whisper API limit is 25 MB
        max_size_mb = 25
        size_mb = audio_path.stat().st_size / (1024 * 1024)
        
        if size_mb > max_size_mb:
            raise TranscriptionError(
                f"Audio file {audio_path.name} is {size_mb:.2f} MB, "
                f"which exceeds the {max_size_mb} MB API limit. "
                "Please use a shorter recording or compress the file."
            )
