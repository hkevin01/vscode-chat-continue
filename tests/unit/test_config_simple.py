"""Simple unit tests for ConfigManager."""

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
    
    def test_custom_config_path(self):
        """Test initialization with custom config path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            custom_config = {
                "automation": {
                    "interval_seconds": 5.0
                }
            }
            json.dump(custom_config, f)
            config_path = Path(f.name)
        
        try:
            config = ConfigManager(config_path)
            self.assertEqual(config.get('automation.interval_seconds'), 5.0)
        finally:
            config_path.unlink()
    
    def test_config_merging(self):
        """Test that user config merges correctly with defaults."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            user_config = {
                "automation": {
                    "interval_seconds": 3.0,
                    "custom_setting": "test"
                },
                "new_section": {
                    "new_option": True
                }
            }
            json.dump(user_config, f)
            config_path = Path(f.name)
        
        try:
            config = ConfigManager(config_path)
            
            # Check that user settings override defaults
            self.assertEqual(config.get('automation.interval_seconds'), 3.0)
            
            # Check that default settings are still present
            self.assertEqual(config.get('logging.level'), 'INFO')
            
            # Check that custom settings are added
            self.assertEqual(config.get('automation.custom_setting'), 'test')
            self.assertTrue(config.get('new_section.new_option'))
        finally:
            config_path.unlink()
    
    def test_get_method_with_default(self):
        """Test get method with default value."""
        config = ConfigManager()
        
        # Test existing key
        self.assertEqual(config.get('logging.level'), 'INFO')
        
        # Test non-existing key with default
        self.assertEqual(config.get('non.existing.key', 'default'), 'default')
        
        # Test non-existing key without default
        self.assertIsNone(config.get('non.existing.key'))
    
    def test_set_method(self):
        """Test set method for updating configuration."""
        config = ConfigManager()
        
        # Set a new value
        config.set('automation.interval_seconds', 10.0)
        self.assertEqual(config.get('automation.interval_seconds'), 10.0)
        
        # Set a nested value
        config.set('new.nested.setting', 'test_value')
        self.assertEqual(config.get('new.nested.setting'), 'test_value')
    
    def test_invalid_config_file(self):
        """Test handling of invalid JSON config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            config_path = Path(f.name)
        
        try:
            # Should fallback to default config
            config = ConfigManager(config_path)
            self.assertEqual(config.get('automation.interval_seconds'), 2.0)
        finally:
            config_path.unlink()


if __name__ == '__main__':
    unittest.main()
