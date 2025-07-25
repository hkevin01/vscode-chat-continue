"""Configuration management for VS Code Chat Continue automation."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union


class ConfigManager:
    """Manages configuration settings for the automation tool."""

    DEFAULT_CONFIG = {
        "automation": {
            "interval_seconds": 2.0,
            "max_retries": 3,
            "enable_audio_feedback": True,
            "dry_run": False,
            "click_delay_ms": 100,
            "typing_delay_ms": 50,
            "focus_delay_ms": 200,
        },
        "detection": {
            "confidence_threshold": 0.8,
            "ocr_language": "eng",
            "button_variants": ["Continue", "Continue >", "Continue...", "Generate more"],
            "search_regions": [],
            "template_matching_threshold": 0.9,
            "use_ocr": True,
            "use_template_matching": True,
            "use_accessibility_api": False,
        },
        "fallback_strategy": {
            "enabled": True,
            "text_commands": ["continue", "please continue", "go on"],
            "typing_speed": "normal",
            "max_retries": 3,
            "timeout_seconds": 5,
            "use_clipboard": False,
            "prefer_buttons": True,
        },
        "input_detection": {
            "methods": ["ocr", "visual", "position"],
            "confidence_threshold": 0.8,
            "search_regions": ["bottom_panel", "side_panel", "editor"],
            "chat_indicators": ["Ask Copilot", "Type a message", "Chat with Copilot"],
        },
        "safety": {
            "require_confirmation": False,
            "emergency_stop_key": "escape",
            "pause_on_user_activity": True,
            "max_automation_time_minutes": 60,
            "preserve_focus": True,
            "backup_clipboard": True,
            "safe_mode": False,
        },
        "performance": {
            "screenshot_region_optimization": True,
            "cache_window_positions": True,
            "parallel_window_processing": False,
            "max_screenshot_size": "1920x1080",
            "compression_quality": 85,
        },
        "monitoring": {
            "enable_metrics": True,
            "log_performance": True,
            "track_success_rate": True,
            "alert_on_failures": False,
            "stats_file": "automation_stats.json",
        },
        "logging": {
            "level": "INFO",
            "file_path": "~/.local/share/vscode-chat-continue/automation.log",
            "max_file_size_mb": 10,
            "backup_count": 5,
            "console_output": True,
            "detailed_timing": False,
        },
        "windows": {
            "vscode_process_names": ["code", "code-oss", "codium", "cursor"],
            "chat_window_patterns": ["Copilot Chat", "GitHub Copilot", "AI Assistant"],
            "exclude_patterns": ["Settings", "Extensions", "Terminal"],
            "minimum_window_size": [300, 200],
            "focus_timeout_seconds": 2.0,
        },
        "hotkeys": {
            "trigger_automation": "ctrl+alt+c",
            "emergency_stop": "ctrl+alt+s",
            "toggle_pause": "ctrl+alt+p",
            "dry_run_mode": "ctrl+alt+d",
        },
    }

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_path: Optional path to configuration file.
                        Defaults to ~/.config/vscode-chat-continue/config.json
        """
        self.logger = logging.getLogger(__name__)

        if config_path is None:
            config_path = Path.home() / ".config" / "vscode-chat-continue" / "config.json"

        self.config_path = Path(config_path).expanduser()
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()

        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)

                # Merge user config with defaults
                self._merge_config(self.config, user_config)
                self.logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.logger.info("Using default configuration")
                self._save_config()  # Save default config for user reference
        except Exception as e:
            self.logger.warning(f"Failed to load config from {self.config_path}: {e}")
            self.logger.info("Using default configuration")

    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Recursively merge source config into target config."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value

    def _save_config(self) -> None:
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            self.logger.debug(f"Configuration saved to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Failed to save config to {self.config_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.

        Args:
            key: Configuration key in dot notation (e.g., 'automation.interval_seconds')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        try:
            keys = key.split(".")
            value = self.config

            for k in keys:
                value = value[k]

            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation.

        Args:
            key: Configuration key in dot notation
            value: Value to set
        """
        keys = key.split(".")
        config = self.config

        # Navigate to parent dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value
        self.logger.debug(f"Configuration updated: {key} = {value}")

    def get_automation_config(self) -> Dict[str, Any]:
        """Get automation-specific configuration."""
        return self.config.get("automation", {})

    def get_detection_config(self) -> Dict[str, Any]:
        """Get detection-specific configuration."""
        return self.config.get("detection", {})

    def get_safety_config(self) -> Dict[str, Any]:
        """Get safety-specific configuration."""
        return self.config.get("safety", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging-specific configuration."""
        return self.config.get("logging", {})

    def get_windows_config(self) -> Dict[str, Any]:
        """Get windows-specific configuration."""
        return self.config.get("windows", {})

    def get_log_level(self) -> str:
        """Get logging level."""
        return self.get("logging.level", "INFO")

    def is_dry_run(self) -> bool:
        """Check if dry run mode is enabled."""
        return self.get("automation.dry_run", False)

    def requires_confirmation(self) -> bool:
        """Check if user confirmation is required."""
        return self.get("safety.require_confirmation", True)

    def save(self) -> None:
        """Save current configuration to file."""
        self._save_config()

    def reload(self) -> None:
        """Reload configuration from file."""
        self.config = self.DEFAULT_CONFIG.copy()
        self._load_config()

    def __str__(self) -> str:
        """String representation of configuration."""
        return json.dumps(self.config, indent=2)
