#!/usr/bin/env python3
"""
Working PyUnit Test Suite for VS Code Chat Continue Automation

This test suite provides comprehensive testing using Python's unittest framework
with proper mocking and avoiding GUI dependencies.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test imports
try:
    from src.core.button_finder import ButtonFinder, ButtonLocation
    from src.core.config_manager import ConfigManager
    from src.utils.logger import AutomationLogger
    IMPORTS_OK = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_OK = False


class TestConfigManagerWorking(unittest.TestCase):
    """Working tests for ConfigManager."""
    
    def setUp(self):
        """Set up test environment."""
        if not IMPORTS_OK:
            self.skipTest("Imports not available")
    
    def test_default_config_load(self):
        """Test loading default configuration."""
        config = ConfigManager()
        # Check actual default values from the source
        self.assertIsNotNone(config.get('automation.interval_seconds'))
        self.assertIsNotNone(config.get('safety.require_confirmation'))
        self.assertIsNotNone(config.get('logging.level'))
    
    def test_config_get_with_default(self):
        """Test get method with default values."""
        config = ConfigManager()
        
        # Test existing key
        value = config.get('automation.interval_seconds')
        self.assertIsNotNone(value)
        
        # Test non-existing key with default
        default_value = config.get('non.existing.key', 'default')
        self.assertEqual(default_value, 'default')
        
        # Test non-existing key without default
        none_value = config.get('non.existing.key')
        self.assertIsNone(none_value)
    
    def test_config_set_method(self):
        """Test setting configuration values."""
        config = ConfigManager()
        
        # Set a value
        config.set('test.setting', 'test_value')
        self.assertEqual(config.get('test.setting'), 'test_value')
        
        # Set nested value
        config.set('test.nested.setting', 42)
        self.assertEqual(config.get('test.nested.setting'), 42)
    
    def test_custom_config_file(self):
        """Test loading from custom config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_config = {
                "automation": {
                    "interval_seconds": 10.0,
                    "custom_setting": "test"
                }
            }
            json.dump(test_config, f)
            config_path = Path(f.name)
        
        try:
            config = ConfigManager(config_path)
            self.assertEqual(config.get('automation.interval_seconds'), 10.0)
            self.assertEqual(config.get('automation.custom_setting'), 'test')
        finally:
            config_path.unlink()


class TestButtonFinderWorking(unittest.TestCase):
    """Working tests for ButtonFinder."""
    
    def setUp(self):
        """Set up test environment."""
        if not IMPORTS_OK:
            self.skipTest("Imports not available")
        
        # Create a mock config manager
        self.mock_config = Mock()
        self.mock_config.get.return_value = {}
    
    def test_button_location_creation(self):
        """Test ButtonLocation dataclass."""
        location = ButtonLocation(
            x=100, y=200, width=50, height=30, 
            confidence=0.8, method="test"
        )
        self.assertEqual(location.x, 100)
        self.assertEqual(location.y, 200)
        self.assertEqual(location.width, 50)
        self.assertEqual(location.height, 30)
        self.assertEqual(location.confidence, 0.8)
        self.assertEqual(location.method, "test")
    
    def test_button_finder_initialization(self):
        """Test ButtonFinder initialization."""
        finder = ButtonFinder(self.mock_config)
        self.assertIsNotNone(finder)
        self.assertEqual(finder.config_manager, self.mock_config)
    
    @patch('src.core.button_finder.HAS_PIL', True)
    def test_find_buttons_no_image(self):
        """Test finding buttons with no image."""
        finder = ButtonFinder(self.mock_config)
        buttons = finder.find_continue_buttons(None, 0, 0)
        self.assertEqual(len(buttons), 0)


class TestLoggerWorking(unittest.TestCase):
    """Working tests for AutomationLogger."""
    
    def setUp(self):
        """Set up test environment."""
        if not IMPORTS_OK:
            self.skipTest("Imports not available")
    
    def test_logger_creation(self):
        """Test logger creation."""
        config = {'logging': {'level': 'INFO'}}
        logger = AutomationLogger(config)
        self.assertIsNotNone(logger)
    
    def test_logger_with_config(self):
        """Test logger with config."""
        config = {
            'logging': {
                'level': 'INFO',
                'console_output': True
            }
        }
        logger = AutomationLogger(config)
        self.assertIsNotNone(logger)


class TestBasicFunctionality(unittest.TestCase):
    """Test basic Python and project functionality."""
    
    def test_python_basics(self):
        """Test basic Python functionality."""
        self.assertEqual(2 + 2, 4)
        self.assertTrue(isinstance([], list))
        self.assertFalse(None)
    
    def test_imports_available(self):
        """Test that core imports work."""
        self.assertTrue(IMPORTS_OK, "Core modules should be importable")
    
    def test_project_structure(self):
        """Test that project structure exists."""
        self.assertTrue(project_root.exists())
        self.assertTrue((project_root / 'src').exists())
        self.assertTrue((project_root / 'config').exists())


def create_test_suite():
    """Create and return the test suite."""
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestBasicFunctionality))
    suite.addTest(unittest.makeSuite(TestConfigManagerWorking))
    suite.addTest(unittest.makeSuite(TestButtonFinderWorking))
    suite.addTest(unittest.makeSuite(TestLoggerWorking))
    
    return suite


def main():
    """Main test runner."""
    print("Running PyUnit Test Suite for VS Code Chat Continue Automation")
    print("=" * 60)
    
    # Create and run test suite
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Test Results Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) 
                       / result.testsRun * 100)
        print(f"Success rate: {success_rate:.1f}%")
    print(f"{'='*60}")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
