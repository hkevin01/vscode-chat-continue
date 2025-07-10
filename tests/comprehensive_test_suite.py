"""Comprehensive test suite for VS Code Chat Continue automation."""

import json
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import cv2
import numpy as np
import pytest

from src.core.automation_engine import AutomationEngine
from src.core.button_finder import ButtonFinder
from src.core.click_automator import ClickAutomator

# Import modules to test
from src.core.config_manager import ConfigManager
from src.core.window_detector import WindowDetector
from src.utils.logger import AutomationLogger
from src.utils.screen_capture import ScreenCapture


class TestPhase1Foundation(unittest.TestCase):
    """Test Phase 1: Foundation components."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_config = {
            "automation": {"interval_seconds": 1.0, "dry_run": True},
            "detection": {"confidence_threshold": 0.8},
            "safety": {"require_confirmation": False},
            "logging": {"level": "DEBUG", "console_output": False}
        }
    
    def test_project_setup_and_structure(self):
        """Test project setup and structure."""
        # Verify essential directories exist
        essential_dirs = [
            "src/core",
            "src/utils", 
            "tests/unit",
            "docs",
            "config",
            "scripts"
        ]
        
        for dir_path in essential_dirs:
            self.assertTrue(Path(dir_path).exists(), 
                          f"Directory {dir_path} should exist")
        
        # Verify essential files exist
        essential_files = [
            "src/main.py",
            "src/core/config_manager.py",
            "src/core/window_detector.py", 
            "src/core/automation_engine.py",
            "requirements.txt"
        ]
        
        for file_path in essential_files:
            self.assertTrue(Path(file_path).exists(),
                          f"File {file_path} should exist")
    
    @patch('psutil.process_iter')
    def test_vscode_process_identification(self, mock_process_iter):
        """Test VS Code process identification."""
        # Mock process objects
        mock_vscode_process = Mock()
        mock_vscode_process.info = {'name': 'code', 'pid': 12345}
        
        mock_other_process = Mock()
        mock_other_process.info = {'name': 'firefox', 'pid': 67890}
        
        mock_process_iter.return_value = [mock_vscode_process, mock_other_process]
        
        detector = WindowDetector(self.test_config)
        processes = detector.find_vscode_processes()
        
        self.assertEqual(len(processes), 1)
        self.assertEqual(processes[0]['name'], 'code')
        self.assertEqual(processes[0]['pid'], 12345)
    
    @patch('src.core.window_detector.WindowDetector._get_x11_windows')
    def test_basic_window_detection(self, mock_get_windows):
        """Test basic window detection functionality."""
        # Mock window data
        mock_windows = [
            {
                'id': 123,
                'title': 'Visual Studio Code',
                'pid': 12345,
                'geometry': {'x': 100, 'y': 100, 'width': 800, 'height': 600}
            },
            {
                'id': 456, 
                'title': 'Firefox',
                'pid': 67890,
                'geometry': {'x': 200, 'y': 200, 'width': 1000, 'height': 700}
            }
        ]
        mock_get_windows.return_value = mock_windows
        
        detector = WindowDetector(self.test_config)
        windows = detector.get_vscode_windows()
        
        self.assertEqual(len(windows), 1)
        self.assertEqual(windows[0]['title'], 'Visual Studio Code')
    
    @patch('pyautogui.screenshot')
    def test_simple_screen_capture(self, mock_screenshot):
        """Test simple screen capture functionality."""
        # Create a mock image
        mock_image = Mock()
        mock_image.size = (1920, 1080)
        mock_screenshot.return_value = mock_image
        
        capturer = ScreenCapture()
        image = capturer.capture_screen()
        
        self.assertIsNotNone(image)
        mock_screenshot.assert_called_once()
    
    def test_configuration_loading(self):
        """Test configuration loading and management."""
        config_manager = ConfigManager()
        
        # Test default configuration loads
        self.assertIsNotNone(config_manager.config)
        self.assertIn('automation', config_manager.config)
        self.assertIn('detection', config_manager.config)
        
        # Test getting configuration values
        interval = config_manager.get('automation.interval_seconds')
        self.assertIsInstance(interval, (int, float))
        
        # Test setting configuration values
        config_manager.set('automation.dry_run', True)
        self.assertTrue(config_manager.get('automation.dry_run'))


class TestPhase2CoreFeatures(unittest.TestCase):
    """Test Phase 2: Core Features."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_config = {
            "detection": {
                "confidence_threshold": 0.8,
                "button_variants": ["Continue", "Continue >"],
                "use_ocr": True,
                "use_template_matching": True
            },
            "automation": {
                "dry_run": True,
                "click_delay_ms": 100
            },
            "logging": {"level": "DEBUG", "console_output": False}
        }
        
        # Create a test image
        self.test_image = np.zeros((600, 800, 3), dtype=np.uint8)
    
    @patch('pytesseract.image_to_data')
    def test_continue_button_detection_ocr(self, mock_ocr):
        """Test continue button detection using OCR."""
        # Mock OCR response
        mock_ocr.return_value = {
            'text': ['', 'Continue', ''],
            'conf': [0, 95, 0],
            'left': [0, 100, 0],
            'top': [0, 200, 0], 
            'width': [0, 80, 0],
            'height': [0, 30, 0]
        }
        
        finder = ButtonFinder(self.test_config)
        buttons = finder.find_continue_buttons_ocr(self.test_image)
        
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0]['text'], 'Continue')
        self.assertEqual(buttons[0]['confidence'], 95)
    
    @patch('cv2.matchTemplate')
    def test_continue_button_detection_template(self, mock_match):
        """Test continue button detection using template matching."""
        # Mock template matching result
        mock_result = np.zeros((520, 720))
        mock_result[200, 100] = 0.95  # High confidence match
        mock_match.return_value = mock_result
        
        finder = ButtonFinder(self.test_config)
        
        # Create a mock template
        template = np.zeros((30, 80, 3), dtype=np.uint8)
        
        with patch('cv2.imread', return_value=template):
            buttons = finder.find_continue_buttons_template(self.test_image, 
                                                          "templates/continue_button.png")
        
        self.assertGreater(len(buttons), 0)
        self.assertGreater(buttons[0]['confidence'], 0.8)
    
    @patch('pyautogui.click')
    def test_mouse_click_automation(self, mock_click):
        """Test mouse click automation."""
        automator = ClickAutomator(self.test_config)
        
        button_info = {
            'center_x': 400,
            'center_y': 300,
            'confidence': 0.9
        }
        
        result = automator.click_button(button_info)
        
        if not self.test_config['automation']['dry_run']:
            mock_click.assert_called_once_with(400, 300)
        
        self.assertTrue(result)
    
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    def test_multi_window_support(self, mock_find_buttons, mock_get_windows):
        """Test multi-window support."""
        # Mock multiple VS Code windows
        mock_windows = [
            {'id': 123, 'title': 'VS Code 1', 'geometry': {'x': 0, 'y': 0, 'width': 800, 'height': 600}},
            {'id': 456, 'title': 'VS Code 2', 'geometry': {'x': 800, 'y': 0, 'width': 800, 'height': 600}}
        ]
        mock_get_windows.return_value = mock_windows
        
        # Mock button detection
        mock_find_buttons.return_value = [
            {'center_x': 400, 'center_y': 300, 'confidence': 0.9}
        ]
        
        engine = AutomationEngine(self.test_config)
        results = engine.process_all_windows()
        
        self.assertEqual(len(results), 2)
        self.assertEqual(mock_find_buttons.call_count, 2)
    
    def test_basic_error_handling(self):
        """Test basic error handling."""
        config_with_errors = {
            "detection": {"confidence_threshold": "invalid"},  # Invalid type
            "logging": {"level": "DEBUG", "console_output": False}
        }
        
        # Should handle invalid configuration gracefully
        try:
            finder = ButtonFinder(config_with_errors)
            # Should use default values for invalid config
            self.assertIsInstance(finder.confidence_threshold, float)
        except Exception as e:
            self.fail(f"ButtonFinder should handle invalid config gracefully: {e}")


class TestPhase3Enhancement(unittest.TestCase):
    """Test Phase 3: Enhancement features."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_config_path = Path("test_config.json")
        self.test_config = {
            "automation": {"interval_seconds": 2.0, "dry_run": True},
            "detection": {"confidence_threshold": 0.8},
            "safety": {"require_confirmation": False, "safe_mode": True},
            "logging": {"level": "INFO", "console_output": False},
            "monitoring": {"enable_metrics": True, "track_success_rate": True}
        }
    
    def tearDown(self):
        """Clean up test files."""
        if self.test_config_path.exists():
            self.test_config_path.unlink()
    
    def test_configuration_system(self):
        """Test advanced configuration system."""
        # Test saving configuration
        config_manager = ConfigManager(self.test_config_path)
        config_manager.config = self.test_config
        config_manager.save_config()
        
        self.assertTrue(self.test_config_path.exists())
        
        # Test loading configuration
        new_config_manager = ConfigManager(self.test_config_path)
        self.assertEqual(new_config_manager.get('automation.interval_seconds'), 2.0)
        
        # Test configuration validation
        config_manager.set('automation.interval_seconds', -1)
        # Should handle invalid values appropriately
    
    def test_logging_and_monitoring(self):
        """Test logging and monitoring system."""
        logger = AutomationLogger(self.test_config['logging'])
        
        # Test operation logging
        op_id = logger.log_operation_start("test_operation", {"detail": "test"})
        self.assertIsNotNone(op_id)
        
        logger.log_operation_success("test_operation", op_id, {"result": "success"})
        
        # Test statistics
        stats = logger.get_statistics()
        self.assertEqual(stats['operations'], 1)
        self.assertEqual(stats['successes'], 1)
        self.assertEqual(stats['failures'], 0)
        
        # Test failure logging
        logger.log_operation_failure("test_operation_2", "Test error")
        stats = logger.get_statistics()
        self.assertEqual(stats['operations'], 2)
        self.assertEqual(stats['failures'], 1)
    
    @patch('time.time')
    def test_performance_optimization(self, mock_time):
        """Test performance optimization features."""
        # Mock time progression
        mock_time.side_effect = [1000, 1001, 1002, 1003]  # 1 second intervals
        
        logger = AutomationLogger({
            "detailed_timing": True,
            "log_performance": True,
            "console_output": False
        })
        
        # Simulate operation with timing
        op_id = logger.log_operation_start("performance_test")
        logger.log_operation_success("performance_test", op_id)
        
        stats = logger.get_statistics()
        self.assertGreater(stats['operations_per_minute'], 0)
    
    @patch('pyautogui.press')
    def test_safety_features(self, mock_press):
        """Test safety features and manual override."""
        config_with_safety = {
            **self.test_config,
            "safety": {
                "safe_mode": True,
                "emergency_stop_key": "escape",
                "preserve_focus": True
            }
        }
        
        automator = ClickAutomator(config_with_safety)
        
        # Test safe mode operation
        button_info = {'center_x': 400, 'center_y': 300, 'confidence': 0.9}
        result = automator.click_button(button_info)
        
        # In safe mode with dry_run, should not actually click
        self.assertTrue(result)
        
        # Test emergency stop (would be triggered by hotkey in real usage)
        engine = AutomationEngine(config_with_safety)
        engine.emergency_stop = True  # Simulate emergency stop
        results = engine.process_all_windows()
        
        # Should stop processing when emergency stop is active
        self.assertEqual(len(results), 0)


class TestPhase4Polish(unittest.TestCase):
    """Test Phase 4: Polish features."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_config = {
            "automation": {"dry_run": True},
            "logging": {"level": "INFO", "console_output": False}
        }
    
    def test_installation_scripts(self):
        """Test installation scripts."""
        # Verify installation scripts exist and are executable
        install_script = Path("scripts/install.sh")
        run_script = Path("scripts/run.sh")
        
        self.assertTrue(install_script.exists(), "Install script should exist")
        self.assertTrue(run_script.exists(), "Run script should exist")
        
        # Check if scripts are executable (on Unix systems)
        import stat
        if install_script.exists():
            mode = install_script.stat().st_mode
            self.assertTrue(mode & stat.S_IEXEC, "Install script should be executable")
    
    def test_documentation_completeness(self):
        """Test documentation completeness."""
        required_docs = [
            "README.md",
            "docs/USAGE.md", 
            "docs/PROJECT_PLAN.md",
            "docs/FALLBACK_STRATEGY.md",
            "docs/EXTENSION_ALTERNATIVE.md"
        ]
        
        for doc_path in required_docs:
            path = Path(doc_path)
            self.assertTrue(path.exists(), f"Documentation {doc_path} should exist")
            
            # Verify non-empty content
            if path.exists():
                content = path.read_text()
                self.assertGreater(len(content.strip()), 100, 
                                 f"Documentation {doc_path} should have substantial content")
    
    def test_testing_coverage(self):
        """Test that tests cover all major components."""
        # Verify test files exist for major components
        test_files = [
            "test_phases.py",  # This file
            "tests/unit/test_config_manager.py"
        ]
        
        for test_file in test_files:
            self.assertTrue(Path(test_file).exists(), 
                          f"Test file {test_file} should exist")
    
    def test_requirements_and_dependencies(self):
        """Test requirements and dependencies."""
        requirements_file = Path("requirements.txt")
        self.assertTrue(requirements_file.exists(), "requirements.txt should exist")
        
        # Verify essential dependencies are listed
        requirements_content = requirements_file.read_text()
        essential_deps = [
            "pyautogui",
            "opencv-python",
            "pytesseract", 
            "psutil",
            "pynput"
        ]
        
        for dep in essential_deps:
            self.assertIn(dep, requirements_content, 
                         f"Dependency {dep} should be in requirements.txt")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete automation system."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.test_config = {
            "automation": {
                "interval_seconds": 0.1,  # Fast for testing
                "dry_run": True,
                "max_retries": 2
            },
            "detection": {
                "confidence_threshold": 0.7,
                "use_ocr": True,
                "use_template_matching": False  # Disable for testing
            },
            "safety": {
                "safe_mode": True,
                "preserve_focus": True
            },
            "logging": {
                "level": "INFO",
                "console_output": False
            }
        }
    
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    @patch('src.core.click_automator.ClickAutomator.click_button')
    def test_end_to_end_automation(self, mock_click, mock_find_buttons, mock_get_windows):
        """Test end-to-end automation workflow."""
        # Mock the complete workflow
        mock_get_windows.return_value = [
            {'id': 123, 'title': 'VS Code', 'geometry': {'x': 0, 'y': 0, 'width': 800, 'height': 600}}
        ]
        
        mock_find_buttons.return_value = [
            {'center_x': 400, 'center_y': 300, 'confidence': 0.9, 'text': 'Continue'}
        ]
        
        mock_click.return_value = True
        
        # Run the automation engine
        engine = AutomationEngine(self.test_config)
        results = engine.process_all_windows()
        
        # Verify the workflow executed correctly
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['success'])
        self.assertEqual(results[0]['buttons_clicked'], 1)
        
        # Verify all components were called
        mock_get_windows.assert_called_once()
        mock_find_buttons.assert_called_once()
        mock_click.assert_called_once()
    
    def test_error_recovery(self):
        """Test error recovery and resilience."""
        # Test with invalid configuration
        invalid_config = {"invalid": "config"}
        
        try:
            engine = AutomationEngine(invalid_config)
            # Should use defaults and not crash
            self.assertIsNotNone(engine.config)
        except Exception as e:
            self.fail(f"System should handle invalid config gracefully: {e}")
    
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    def test_fallback_scenarios(self, mock_find_buttons):
        """Test fallback scenarios when primary detection fails."""
        # Simulate no buttons found
        mock_find_buttons.return_value = []
        
        engine = AutomationEngine(self.test_config)
        
        # With fallback enabled, should attempt text input method
        with patch('src.core.window_detector.WindowDetector.get_vscode_windows') as mock_windows:
            mock_windows.return_value = [
                {'id': 123, 'title': 'VS Code', 'geometry': {'x': 0, 'y': 0, 'width': 800, 'height': 600}}
            ]
            
            results = engine.process_all_windows()
            
            # Should complete without errors even when no buttons found
            self.assertEqual(len(results), 1)
            # Should indicate no buttons were found/clicked
            self.assertEqual(results[0]['buttons_clicked'], 0)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
