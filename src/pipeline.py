"""Processing pipeline orchestrator for Voice-to-Note application."""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from audio_handler import AudioFile, AudioFileError
from transcription_service import TranscriptionService, TranscriptionError
from text_processor import TextProcessor, TextProcessingError
from markdown_formatter import MarkdownFormatter
from file_writer import FileWriter, FileWriteError
from config_manager import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of processing a single audio file."""
    audio_file: AudioFile
    success: bool
    output_path: Optional[Path] = None
    error: Optional[str] = None
    transcript_length: int = 0
    processing_time: float = 0.0


class PipelineError(Exception):
    """Raised when pipeline processing fails."""
    pass


class Pipeline:
    """Orchestrates the complete voice-to-note processing pipeline."""
    
    def __init__(self, config: ConfigManager):
        """
        Initialize pipeline with configuration.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        
        # Initialize components
        logger.info("Initializing pipeline components")
        
        # Transcription service
        transcription_api_key = config.get_api_key("transcription")
        transcription_model = config.get("llm.transcription.model", "whisper-1")
        transcription_language = config.get("llm.transcription.language")
        
        self.transcription_service = TranscriptionService(
            api_key=transcription_api_key,
            model=transcription_model,
            language=transcription_language
        )
        
        # Text processor
        processing_api_key = config.get_api_key("text_processing")
        processing_model = config.get("llm.text_processing.model", "gpt-4-turbo-preview")
        filler_words = config.get("processing.filler_words", [])
        aggressiveness = config.get("processing.remove_aggressiveness", "moderate")
        
        self.text_processor = TextProcessor(
            api_key=processing_api_key,
            model=processing_model,
            filler_words=filler_words,
            aggressiveness=aggressiveness
        )
        
        # Markdown formatter
        add_headings = config.get("processing.add_headings", False)
        self.markdown_formatter = MarkdownFormatter(add_headings=add_headings)
        
        # File writer
        vault_path = config.get_vault_path()
        output_folder = config.get("obsidian.output_folder", "Voice Notes")
        self.file_writer = FileWriter(vault_path, output_folder)
        
        logger.info("Pipeline initialized successfully")
    
    def process_file(self, audio_file: AudioFile) -> ProcessingResult:
        """
        Process a single audio file through the complete pipeline.
        
        Args:
            audio_file: AudioFile to process
            
        Returns:
            ProcessingResult with outcome
        """
        start_time = datetime.now()
        logger.info(f"Processing {audio_file.path.name}")
        
        try:
            # Step 1: Validate file size
            self.transcription_service.validate_file_size(audio_file.path)
            
            # Step 2: Transcribe audio
            logger.info(f"[1/4] Transcribing {audio_file.path.name}")
            raw_transcript = self.transcription_service.transcribe(audio_file.path)
            
            # Step 3: Process text
            logger.info(f"[2/4] Cleaning text for {audio_file.path.name}")
            cleaned_text = self.text_processor.process(raw_transcript)
            
            # Step 4: Generate metadata
            metadata = self._build_metadata(audio_file)
            
            # Step 5: Format as markdown
            logger.info(f"[3/4] Formatting markdown for {audio_file.path.name}")
            markdown_content = self.markdown_formatter.format(cleaned_text, metadata)
            
            # Step 6: Generate filename
            filename_pattern = self.config.get(
                "obsidian.filename_pattern",
                "{date}-{time}-voice-note"
            )
            filename = MarkdownFormatter.generate_filename(filename_pattern, metadata)
            
            # Step 7: Write to vault
            logger.info(f"[4/4] Writing file for {audio_file.path.name}")
            output_path = self.file_writer.write(markdown_content, filename)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"Successfully processed {audio_file.path.name} in {processing_time:.1f}s"
            )
            
            return ProcessingResult(
                audio_file=audio_file,
                success=True,
                output_path=output_path,
                transcript_length=len(cleaned_text),
                processing_time=processing_time
            )
            
        except (TranscriptionError, TextProcessingError, FileWriteError) as e:
            logger.error(f"Failed to process {audio_file.path.name}: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                audio_file=audio_file,
                success=False,
                error=str(e),
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Unexpected error processing {audio_file.path.name}: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                audio_file=audio_file,
                success=False,
                error=f"Unexpected error: {e}",
                processing_time=processing_time
            )
    
    def process_files(self, audio_files: List[AudioFile]) -> List[ProcessingResult]:
        """
        Process multiple audio files.
        
        Args:
            audio_files: List of AudioFile objects to process
            
        Returns:
            List of ProcessingResult objects
        """
        results = []
        total = len(audio_files)
        
        logger.info(f"Processing {total} audio file(s)")
        
        for i, audio_file in enumerate(audio_files, 1):
            logger.info(f"Processing file {i}/{total}: {audio_file.path.name}")
            result = self.process_file(audio_file)
            results.append(result)
        
        # Log summary
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        logger.info(f"Processing complete: {successful} successful, {failed} failed")
        
        return results
    
    def _build_metadata(self, audio_file: AudioFile) -> Dict[str, Any]:
        """
        Build metadata dictionary for an audio file.
        
        Args:
            audio_file: AudioFile object
            
        Returns:
            Metadata dictionary
        """
        return {
            'created': audio_file.metadata.get('modified_date', datetime.now()),
            'source': audio_file.path.name,
            'processed': datetime.now(),
            'duration': audio_file.get_duration_formatted(),
        }
    
    def estimate_cost(self, audio_files: List[AudioFile]) -> Dict[str, float]:
        """
        Estimate processing cost for audio files.
        
        Args:
            audio_files: List of AudioFile objects
            
        Returns:
            Dictionary with cost breakdown
        """
        transcription_cost = 0.0
        text_processing_cost = 0.0
        
        for audio_file in audio_files:
            # Transcription cost
            duration = audio_file.metadata.get('duration_seconds', 0)
            transcription_cost += self.transcription_service.estimate_cost(duration)
            
            # Text processing cost (rough estimate based on duration)
            # Assume ~150 words per minute of speech
            estimated_words = (duration / 60) * 150
            estimated_chars = estimated_words * 6  # Average word length + space
            text_processing_cost += self.text_processor.estimate_cost(
                "x" * int(estimated_chars)
            )
        
        total_cost = transcription_cost + text_processing_cost
        
        return {
            'transcription': round(transcription_cost, 4),
            'text_processing': round(text_processing_cost, 4),
            'total': round(total_cost, 4)
        }
    
    def get_summary(self, results: List[ProcessingResult]) -> Dict[str, Any]:
        """
        Get summary statistics from processing results.
        
        Args:
            results: List of ProcessingResult objects
            
        Returns:
            Summary dictionary
        """
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        total_time = sum(r.processing_time for r in results)
        avg_time = total_time / total if total > 0 else 0
        
        total_chars = sum(r.transcript_length for r in results if r.success)
        
        return {
            'total_files': total,
            'successful': successful,
            'failed': failed,
            'total_processing_time': round(total_time, 2),
            'average_processing_time': round(avg_time, 2),
            'total_characters': total_chars,
            'output_files': [
                str(r.output_path) for r in results if r.success and r.output_path
            ],
            'errors': [
                {'file': r.audio_file.path.name, 'error': r.error}
                for r in results if not r.success
            ]
        }
