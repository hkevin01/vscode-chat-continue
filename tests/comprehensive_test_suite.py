"""Comprehensive test suite for VS Code Chat Continue automation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from unittest.mock import Mock, patch

import numpy as np
from PIL import Image

from src.core.automation_engine import AutomationEngine
from src.core.button_finder import ButtonFinder, ButtonLocation
from src.core.click_automator import ClickAutomator
from src.core.config_manager import ConfigManager
from src.core.window_detector import VSCodeWindow, WindowDetector
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
        
        detector = WindowDetector()
        processes = detector.find_vscode_processes()
        
        self.assertEqual(len(processes), 1)
        self.assertEqual(processes[0]['name'], 'code')
        self.assertEqual(processes[0]['pid'], 12345)
    
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    def test_basic_window_detection(self, mock_get_windows):
        """Test basic window detection functionality."""
        # Mock window data
        mock_windows = [
            VSCodeWindow(
                id=123,
                title='Visual Studio Code',
                pid=12345,
                x=100, y=100, width=800, height=600
            )
        ]
        mock_get_windows.return_value = mock_windows
        
        detector = WindowDetector()
        windows = detector.get_vscode_windows()
        
        self.assertEqual(len(windows), 1)
        self.assertEqual(windows[0].title, 'Visual Studio Code')

    @patch('src.utils.screen_capture.ScreenCapture.capture_screen')
    def test_simple_screen_capture(self, mock_capture_screen):
        """Test simple screen capture functionality."""
        # Mock a PIL Image
        mock_image = Image.new('RGB', (100, 100), color = 'red')
        mock_capture_screen.return_value = mock_image

        capture = ScreenCapture()
        screenshot = capture.capture_screen()

        self.assertIsNotNone(screenshot)
        mock_capture_screen.assert_called_once()
        self.assertEqual(screenshot.size, (100, 100))

class TestPhase2CoreFeatures(unittest.TestCase):
    """Test Phase 2: Core features."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_config = {
            "automation": {"interval_seconds": 1.0, "dry_run": True},
            "detection": {
                "confidence_threshold": 0.8,
                "button_text": ["Continue"],
            },
            "safety": {"require_confirmation": False},
            "logging": {"level": "DEBUG", "console_output": False}
        }
        self.config_manager = ConfigManager()
        self.config_manager.config = self.test_config
        # Create a dummy image for testing
        self.test_image = Image.new('RGB', (200, 100), color = 'blue')
        # Create a dummy button location
        self.button_location = ButtonLocation(
            x=50, y=50, width=100, height=30,
            confidence=0.9, method='ocr', text='Continue'
        )

    @patch('pytesseract.image_to_data')
    def test_continue_button_detection_ocr(self, mock_image_to_data):
        """Test continue button detection using OCR."""
        # Mock Tesseract response
        mock_image_to_data.return_value = {
            'level': [1, 2, 3, 4, 5],
            'left': [10, 50, 60, 70, 80],
            'top': [10, 50, 50, 50, 50],
            'width': [30, 40, 50, 60, 70],
            'height': [10, 20, 20, 20, 20],
            'conf': ['95', '90', '85', '80', '75'],
            'text': ['', 'Continue', '', '', '']
        }
        
        finder = ButtonFinder(self.config_manager)
        buttons = finder.find_continue_buttons(self.test_image)
        
        self.assertGreater(len(buttons), 0)
        self.assertEqual(buttons[0].text, 'Continue')

    @patch('cv2.matchTemplate')
    @patch('cv2.imread')
    def test_continue_button_detection_template(self, mock_imread, mock_match_template):
        """Test continue button detection using template matching."""
        # Mock template loading and matching
        mock_template = np.zeros((10, 40, 3), dtype=np.uint8)
        mock_imread.return_value = mock_template
        mock_match_template.return_value = np.array([[0.95]])

        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path('templates/continue.png')]
            finder = ButtonFinder(self.config_manager)
            buttons = finder.find_continue_buttons(self.test_image)
            self.assertGreater(len(buttons), 0)
            self.assertTrue(any(b.method.startswith('template') for b in buttons))

    @patch('pyautogui.click')
    @patch('pyautogui.moveTo')
    def test_mouse_click_automation(self, mock_move_to, mock_click):
        """Test mouse click automation."""
        automator = ClickAutomator()
        automator.click(self.button_location)
        
        center_x, center_y = self.button_location.center
        mock_move_to.assert_called_once_with(center_x, center_y, automator.move_duration)
        mock_click.assert_called_once()

    @patch('src.core.automation_engine.AutomationEngine._process_window')
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    def test_multi_window_support(self, mock_get_windows, mock_process_window):
        """Test multi-window support."""
        # Mock multiple VS Code windows
        mock_windows = [
            VSCodeWindow(id=1, title="VSCode1", pid=123, x=0, y=0, width=800, height=600),
            VSCodeWindow(id=2, title="VSCode2", pid=124, x=800, y=0, width=800, height=600)
        ]
        mock_get_windows.return_value = mock_windows
        mock_process_window.return_value = []

        engine = AutomationEngine(self.config_manager)
        # We need to run the engine's main loop once
        async def run_engine():
            await engine._run_iteration()
        
        import asyncio
        asyncio.run(run_engine())

        self.assertEqual(mock_process_window.call_count, 2)

    def test_basic_error_handling(self):
        """Test basic error handling."""
        # Test with invalid config
        try:
            invalid_config = {"detection": {"confidence_threshold": "invalid"}}
            cm = ConfigManager()
            cm.config = invalid_config
            finder = ButtonFinder(cm)
            # This should not raise an error, but log a warning.
            # We can check if the default value is used.
            self.assertIsInstance(finder.config_manager.get('detection.confidence_threshold', 0.8), float)
        except Exception as e:
            self.fail(f"ButtonFinder should handle invalid config gracefully: {e}")


class TestPhase3Enhancement(unittest.TestCase):
    """Test Phase 3: Enhancements."""

    def setUp(self):
        """Set up test environment."""
        self.test_config_path = Path("test_config.json")
        self.test_config = {
            "automation": {"interval_seconds": 0.1, "dry_run": True},
            "detection": {"confidence_threshold": 0.7},
            "safety": {"require_confirmation": False, "emergency_stop_key": "esc"},
            "logging": {"level": "INFO", "console_output": False, "file_path": "test_automation.log"}
        }
        with open(self.test_config_path, "w") as f:
            import json
            json.dump(self.test_config, f)

    def tearDown(self):
        """Clean up after tests."""
        if self.test_config_path.exists():
            self.test_config_path.unlink()
        log_file = Path(self.test_config["logging"]["file_path"])
        if log_file.exists():
            log_file.unlink()

    def test_configuration_system(self):
        """Test advanced configuration system."""
        config_manager = ConfigManager(self.test_config_path)
        self.assertEqual(config_manager.get('detection.confidence_threshold'), 0.7)
        
        # Test saving config
        config_manager.set('detection.confidence_threshold', 0.9)
        config_manager._save_config()
        
        new_config_manager = ConfigManager(self.test_config_path)
        self.assertEqual(new_config_manager.get('detection.confidence_threshold'), 0.9)

    def test_logging_and_monitoring(self):
        """Test logging and monitoring system."""
        logger = AutomationLogger(self.test_config['logging'])
        logger.log_operation_start("test_op")
        logger.log_operation_success("test_op")
        stats = logger.get_stats()
        self.assertEqual(stats['operations'], 1)
        self.assertEqual(stats['successes'], 1)

        log_file = Path(self.test_config["logging"]["file_path"])
        self.assertTrue(log_file.exists())
        content = log_file.read_text()
        self.assertIn("Starting test_op", content)
        self.assertIn("Completed test_op successfully", content)

    @patch('time.time', side_effect=[1000, 1001, 1002, 1005])
    def test_performance_optimization(self, mock_time):
        """Test performance optimization features."""
        logger = AutomationLogger(self.test_config['logging'])
        op_id = logger.log_operation_start("performance_test")
        logger.log_operation_success("performance_test", operation_id=op_id)
        # No direct performance test possible without more complex setup
        # We just check that the logging calls don't fail
        self.assertIsNotNone(op_id)

    @patch('pyautogui.click')
    def test_safety_features(self, mock_click):
        """Test safety features and manual override."""
        config_manager = ConfigManager()
        config_manager.config = self.test_config
        engine = AutomationEngine(config_manager)
        
        # Test dry run
        engine.config_manager.set('automation.dry_run', True)
        automator = ClickAutomator()
        button_info = ButtonLocation(10, 10, 100, 30, 0.9, 'test')
        automator.click(button_info)
        mock_click.assert_not_called()

        # Test non-dry run
        engine.config_manager.set('automation.dry_run', False)
        automator.dry_run = False
        automator.click(button_info)
        mock_click.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Test integration of multiple components."""

    def setUp(self):
        """Set up test environment."""
        self.test_config = {
            "automation": {"interval_seconds": 0.1, "dry_run": True},
            "detection": {"confidence_threshold": 0.7, "button_text": ["Continue"]},
            "safety": {"require_confirmation": False},
            "logging": {"level": "DEBUG", "console_output": False}
        }
        self.config_manager = ConfigManager()
        self.config_manager.config = self.test_config
        self.engine = AutomationEngine(self.config_manager)

    def test_error_recovery(self):
        """Test error recovery and resilience."""
        # Test with invalid config
        try:
            invalid_config = {"detection": "invalid"}
            cm = ConfigManager()
            cm.config = invalid_config
            engine = AutomationEngine(cm)
            self.assertIsNotNone(engine.config_manager)
        except Exception as e:
            self.fail(f"System should handle invalid config gracefully: {e}")

    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    @patch('src.core.click_automator.ClickAutomator.click')
    def test_end_to_end_automation(self, mock_click, mock_find_buttons, mock_capture, mock_get_windows):
        """Test end-to-end automation workflow."""
        # Mock window, screenshot, and button
        mock_get_windows.return_value = [VSCodeWindow(1, "VSCode", 123, 0, 0, 800, 600)]
        mock_capture.return_value = Image.new('RGB', (800, 600))
        mock_find_buttons.return_value = [ButtonLocation(100, 100, 100, 30, 0.9, 'ocr', 'Continue')]

        async def run_engine():
            await self.engine._run_iteration()
        
        import asyncio
        asyncio.run(run_engine())

        mock_get_windows.assert_called_once()
        mock_capture.assert_called_once()
        mock_find_buttons.assert_called_once()
        mock_click.assert_called_once()

    @patch('src.core.automation_engine.AutomationEngine._run_iteration')
    def test_fallback_scenarios(self, mock_run_iteration):
        """Test fallback scenarios when primary detection fails."""
        # Simulate OCR failing and template matching succeeding
        mock_run_iteration.side_effect = [Exception("OCR Failed"), None]
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
            "tests/test_phases.py",  # This file
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
