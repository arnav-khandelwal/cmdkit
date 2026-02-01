"""Storage utilities for cmdkit configuration."""

import json
from pathlib import Path

# Default configuration structure
DEFAULT_CONFIG = {
    "workflows": {}
}


def get_config_path() -> Path:
    """Get the path to the config file.
    
    Returns:
        Path to ~/.cmdkit/config.json
    """
    return Path.home() / ".cmdkit" / "config.json"


def _ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    config_dir = get_config_path().parent
    config_dir.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Load configuration from disk.
    
    If the config file doesn't exist or is corrupted,
    returns the default config structure.
    
    Returns:
        Configuration dictionary
    """
    config_path = get_config_path()
    
    # Return default if file doesn't exist
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()
    
    # Try to load and parse JSON
    try:
        content = config_path.read_text()
        if not content.strip():
            return DEFAULT_CONFIG.copy()
        config = json.loads(content)
        # Validate it's a dict with expected structure
        if not isinstance(config, dict):
            return DEFAULT_CONFIG.copy()
        # Ensure workflows key exists
        if "workflows" not in config:
            config["workflows"] = {}
        return config
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """Save configuration to disk.
    
    Creates the config directory and file if they don't exist.
    
    Args:
        config: Configuration dictionary to save
    """
    _ensure_config_dir()
    config_path = get_config_path()
    
    try:
        config_path.write_text(json.dumps(config, indent=2))
    except OSError:
        # Silently fail - no exceptions to CLI
        pass
