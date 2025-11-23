"""Tests for configuration manager."""

import pytest
from pathlib import Path
from src.config_manager import ConfigManager, ConfigurationError


def test_config_manager_initialization():
    """Test that config manager initializes with defaults."""
    config = ConfigManager()
    assert config.config is not None
    assert isinstance(config.config, dict)


def test_get_with_dot_notation():
    """Test getting config values with dot notation."""
    config = ConfigManager()
    
    # Test getting nested value
    output_folder = config.get("obsidian.output_folder")
    assert output_folder == "Voice Notes"
    
    # Test getting with default
    missing = config.get("nonexistent.key", "default_value")
    assert missing == "default_value"


def test_set_with_dot_notation():
    """Test setting config values with dot notation."""
    config = ConfigManager()
    
    # Set a value
    config.set("obsidian.vault_path", "/test/path")
    assert config.get("obsidian.vault_path") == "/test/path"
    
    # Set a nested value
    config.set("new.nested.value", "test")
    assert config.get("new.nested.value") == "test"


def test_validation_requires_vault_path(monkeypatch):
    """Test that validation fails without vault path."""
    config = ConfigManager()
    
    # Should raise error without vault path set
    with pytest.raises(ConfigurationError):
        config.validate()


def test_validation_requires_api_key(tmp_path, monkeypatch):
    """Test that validation fails without API key."""
    # Create a temporary vault directory
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir()
    
    config = ConfigManager()
    config.set("obsidian.vault_path", str(vault_path))
    
    # Clear any existing API key
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    
    # Should raise error without API key
    with pytest.raises(ConfigurationError):
        config.validate()
