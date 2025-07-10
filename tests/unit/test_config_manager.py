"""Unit tests for configuration manager."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class."""
    
    def test_default_config_initialization(self):
        """Test that default configuration is loaded correctly."""
        with patch.object(Path, 'exists', return_value=False):
            config = ConfigManager()
            
            self.assertEqual(config.get('automation.interval_seconds'), 2.0)
            self.assertTrue(config.get('safety.require_confirmation'))
            self.assertEqual(config.get('logging.level'), 'INFO')
    
    def test_custom_config_path(self, tmp_path):
        """Test initialization with custom config path."""
        config_file = tmp_path / "custom_config.json"
        custom_config = {
            "automation": {
                "interval_seconds": 5.0
            }
        }
        
        config_file.write_text(json.dumps(custom_config))
        
        config = ConfigManager(config_file)
        assert config.get('automation.interval_seconds') == 5.0
    
    def test_config_merging(self, tmp_path):
        """Test that user config merges correctly with defaults."""
        config_file = tmp_path / "config.json"
        user_config = {
            "automation": {
                "interval_seconds": 3.0,
                "custom_setting": "test"
            },
            "new_section": {
                "new_option": True
            }
        }
        
        config_file.write_text(json.dumps(user_config))
        
        config = ConfigManager(config_file)
        
        # User setting should override default
        assert config.get('automation.interval_seconds') == 3.0
        
        # Default setting should remain
        assert config.get('automation.max_retries') == 3
        
        # Custom settings should be preserved
        assert config.get('automation.custom_setting') == "test"
        assert config.get('new_section.new_option') is True
    
    def test_get_with_dot_notation(self):
        """Test getting config values with dot notation."""
        config = ConfigManager()
        
        assert config.get('automation.interval_seconds') == 2.0
        assert config.get('detection.confidence_threshold') == 0.8
        assert config.get('nonexistent.key', 'default') == 'default'
    
    def test_set_with_dot_notation(self):
        """Test setting config values with dot notation."""
        config = ConfigManager()
        
        config.set('automation.interval_seconds', 5.0)
        assert config.get('automation.interval_seconds') == 5.0
        
        config.set('new.nested.key', 'value')
        assert config.get('new.nested.key') == 'value'
    
    def test_helper_methods(self):
        """Test helper methods for specific config sections."""
        config = ConfigManager()
        
        automation_config = config.get_automation_config()
        assert 'interval_seconds' in automation_config
        
        assert config.get_log_level() == 'INFO'
        assert config.is_dry_run() is False
        assert config.requires_confirmation() is True
    
    def test_invalid_config_file(self, tmp_path):
        """Test handling of invalid config file."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("invalid json content")
        
        # Should fall back to defaults without crashing
        config = ConfigManager(config_file)
        assert config.get('automation.interval_seconds') == 2.0
