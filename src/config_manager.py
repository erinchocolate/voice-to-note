"""Configuration management for Voice-to-Note application."""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class ConfigManager:
    """Manages application configuration from YAML files and environment variables."""
    
    DEFAULT_CONFIG_PATH = Path.home() / ".config" / "voice-to-note" / "config.yaml"
    
    DEFAULT_CONFIG = {
        "obsidian": {
            "vault_path": None,
            "output_folder": "Voice Notes",
            "filename_pattern": "{date}-{time}-voice-note"
        },
        "llm": {
            "transcription": {
                "provider": "openai_whisper",
                "api_key_env": "OPENAI_API_KEY",
                "model": "whisper-1",
                "language": None
            },
            "text_processing": {
                "provider": "openai_gpt4",
                "api_key_env": "OPENAI_API_KEY",
                "model": "gpt-4-turbo-preview"
            }
        },
        "processing": {
            "filler_words": ["um", "uh", "like", "you know", "sort of", "kind of"],
            "remove_aggressiveness": "moderate",
            "add_headings": False,
            "paragraph_min_sentences": 2
        },
        "logging": {
            "level": "INFO",
            "file": "~/.config/voice-to-note/logs/app.log"
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to config file. If None, uses default location.
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config: Dict[str, Any] = {}
        
        # Load environment variables from .env file if present
        load_dotenv()
        
        # Load configuration
        self._load_config()
        
    def _load_config(self) -> None:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")
                self.config = {}
        else:
            logger.info(f"No config file found at {self.config_path}, using defaults")
            self.config = {}
        
        # Merge with defaults
        self.config = self._merge_with_defaults(self.config, self.DEFAULT_CONFIG)
    
    def _merge_with_defaults(self, config: Dict, defaults: Dict) -> Dict:
        """Recursively merge config with defaults, preferring config values."""
        result = defaults.copy()
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_with_defaults(value, result[key])
            else:
                result[key] = value
        return result
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        # Create directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Saved configuration to {self.config_path}")
        except Exception as e:
            raise ConfigurationError(f"Failed to save config: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path (e.g., "obsidian.vault_path")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path (e.g., "obsidian.vault_path")
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent dictionary
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
    
    def validate(self) -> None:
        """
        Validate that required configuration is present.
        
        Raises:
            ConfigurationError: If required configuration is missing or invalid
        """
        # Check vault path
        vault_path = self.get("obsidian.vault_path")
        if not vault_path:
            raise ConfigurationError(
                "Obsidian vault path not configured. "
                "Run 'voice-to-note setup' or set it in config.yaml"
            )
        
        vault_path = Path(vault_path).expanduser()
        if not vault_path.exists():
            raise ConfigurationError(
                f"Vault path does not exist: {vault_path}"
            )
        
        if not vault_path.is_dir():
            raise ConfigurationError(
                f"Vault path is not a directory: {vault_path}"
            )
        
        # Check API key
        api_key_env = self.get("llm.transcription.api_key_env")
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ConfigurationError(
                f"API key not found in environment variable {api_key_env}. "
                "Please set it in your .env file or environment."
            )
        
        logger.info("Configuration validation successful")
    
    def get_api_key(self, service: str = "transcription") -> str:
        """
        Get API key for a specific service.
        
        Args:
            service: Service name ("transcription" or "text_processing")
            
        Returns:
            API key from environment
            
        Raises:
            ConfigurationError: If API key not found
        """
        api_key_env = self.get(f"llm.{service}.api_key_env")
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            raise ConfigurationError(
                f"API key not found in environment variable {api_key_env}"
            )
        
        return api_key
    
    def get_vault_path(self) -> Path:
        """
        Get the Obsidian vault path as a Path object.
        
        Returns:
            Path to vault
            
        Raises:
            ConfigurationError: If vault path not configured
        """
        vault_path = self.get("obsidian.vault_path")
        if not vault_path:
            raise ConfigurationError("Vault path not configured")
        
        return Path(vault_path).expanduser().resolve()
    
    def get_output_path(self) -> Path:
        """
        Get the full output path (vault + output folder).
        
        Returns:
            Path to output folder within vault
        """
        vault_path = self.get_vault_path()
        output_folder = self.get("obsidian.output_folder", "Voice Notes")
        return vault_path / output_folder
    
    def get_language(self) -> Optional[str]:
        """
        Get the language setting for transcription.
        
        Returns:
            Language code (e.g., 'en', 'zh') or None for auto-detection
        """
        return self.get("llm.transcription.language")
    
    def get_filler_words(self) -> Dict[str, list]:
        """
        Get filler words for both English and Chinese.
        
        Returns:
            Dictionary with 'english' and 'chinese' keys containing filler word lists
        """
        # Handle both old and new config formats
        english_words = self.get("processing.filler_words_english")
        chinese_words = self.get("processing.filler_words_chinese")
        
        # Fallback to old format if new format not found
        if english_words is None:
            english_words = self.get("processing.filler_words", [
                "um", "uh", "like", "you know", "sort of", "kind of"
            ])
        
        if chinese_words is None:
            chinese_words = []
        
        return {
            "english": english_words,
            "chinese": chinese_words
        }
    
    def setup_logging(self) -> None:
        """Configure logging based on config settings."""
        log_level = self.get("logging.level", "INFO")
        log_file = self.get("logging.file")
        
        # Create log directory if needed
        if log_file:
            log_path = Path(log_file).expanduser()
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Configure file handler
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(getattr(logging, log_level))
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            
            # Add to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(file_handler)
        
        # Set console logging level
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(levelname)s: %(message)s'
        )
