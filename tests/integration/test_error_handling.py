"""Integration tests for error handling and recovery."""

import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.automation_engine import AutomationEngine
from src.core.button_finder import ButtonLocation
from src.core.config_manager import ConfigManager
from src.core.window_detector import VSCodeWindow


class TestErrorHandling(unittest.TestCase):
    """Integration tests for error handling and recovery scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.config_manager = ConfigManager()
        self.config_manager.config = {
            "automation": {
                "interval_seconds": 0.1,
                "dry_run": True,
                "retry_attempts": 3
            },
            "detection": {
                "confidence_threshold": 0.8,
                "button_text": ["Continue"]
            },
            "logging": {"level": "DEBUG", "console_output": False}
        }
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    def test_window_detection_failure_recovery(self, mock_get_windows):
        """Test recovery from window detection failures."""
        # First call fails, second succeeds
        mock_get_windows.side_effect = [
            Exception("Window detection failed"),
            [VSCodeWindow(1, "VS Code", 123, 100, 100, 800, 600)]
        ]
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iterations():
            # First iteration should handle error gracefully
            await engine._run_iteration()
            # Second iteration should succeed
            await engine._run_iteration()
            
        asyncio.run(run_iterations())
        
        # Should have attempted window detection twice
        self.assertEqual(mock_get_windows.call_count, 2)
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    def test_screenshot_failure_recovery(
        self, mock_capture, mock_get_windows
    ):
        """Test recovery from screenshot capture failures."""
        mock_windows = [
            VSCodeWindow(1, "VS Code", 123, 100, 100, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        # First capture fails, second succeeds
        mock_capture.side_effect = [
            Exception("Screenshot failed"),
            Image.new('RGB', (800, 600))
        ]
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iterations():
            await engine._run_iteration()  # Should handle error
            await engine._run_iteration()  # Should succeed
            
        asyncio.run(run_iterations())
        
        # Should have attempted capture twice
        self.assertEqual(mock_capture.call_count, 2)
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    def test_button_detection_failure_recovery(
        self, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test recovery from button detection failures."""
        mock_windows = [
            VSCodeWindow(1, "VS Code", 123, 100, 100, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (800, 600))
        mock_capture.return_value = mock_screenshot
        
        # First detection fails, second succeeds
        mock_find_buttons.side_effect = [
            Exception("OCR failed"),
            [ButtonLocation(100, 100, 100, 30, 0.9, 'ocr', 'Continue')]
        ]
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iterations():
            await engine._run_iteration()  # Should handle error
            await engine._run_iteration()  # Should succeed
            
        asyncio.run(run_iterations())
        
        # Should have attempted button detection twice
        self.assertEqual(mock_find_buttons.call_count, 2)
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    @patch('src.core.click_automator.ClickAutomator.click')
    def test_click_failure_recovery(
        self, mock_click, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test recovery from click automation failures."""
        mock_windows = [
            VSCodeWindow(1, "VS Code", 123, 100, 100, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (800, 600))
        mock_capture.return_value = mock_screenshot
        
        mock_buttons = [
            ButtonLocation(100, 100, 100, 30, 0.9, 'ocr', 'Continue')
        ]
        mock_find_buttons.return_value = mock_buttons
        
        # First click fails, second succeeds
        mock_click.side_effect = [
            Exception("Click failed"),
            True
        ]
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iterations():
            await engine._run_iteration()  # Should handle error
            await engine._run_iteration()  # Should succeed
            
        asyncio.run(run_iterations())
        
        # Should have attempted click twice
        self.assertEqual(mock_click.call_count, 2)
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    @patch('src.core.click_automator.ClickAutomator.click')
    def test_partial_failure_handling(
        self, mock_click, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test handling partial failures across multiple windows."""
        mock_windows = [
            VSCodeWindow(1, "VS Code 1", 123, 0, 0, 800, 600),
            VSCodeWindow(2, "VS Code 2", 124, 800, 0, 800, 600),
            VSCodeWindow(3, "VS Code 3", 125, 1600, 0, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        # Screenshot succeeds for all, but processing varies
        mock_screenshot = Image.new('RGB', (800, 600))
        mock_capture.return_value = mock_screenshot
        
        # Button detection: success, failure, success
        mock_find_buttons.side_effect = [
            [ButtonLocation(100, 100, 100, 30, 0.9, 'ocr', 'Continue')],
            Exception("Detection failed for window 2"),
            [ButtonLocation(1700, 100, 100, 30, 0.8, 'ocr', 'Continue')]
        ]
        
        # Clicks: success for windows 1 and 3
        mock_click.side_effect = [True, True]
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iteration():
            await engine._run_iteration()
            
        asyncio.run(run_iteration())
        
        # Should process all windows despite one failure
        self.assertEqual(mock_capture.call_count, 3)
        self.assertEqual(mock_find_buttons.call_count, 3)
        self.assertEqual(mock_click.call_count, 2)  # Only successful detections
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    def test_complete_system_failure_recovery(self, mock_get_windows):
        """Test recovery from complete system failures."""
        # Simulate various types of failures
        mock_get_windows.side_effect = [
            Exception("System error 1"),
            Exception("System error 2"),
            [VSCodeWindow(1, "VS Code", 123, 100, 100, 800, 600)]
        ]
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iterations():
            # Multiple failures followed by success
            await engine._run_iteration()  # Fail
            await engine._run_iteration()  # Fail
            await engine._run_iteration()  # Success
            
        asyncio.run(run_iterations())
        
        # Should have attempted all iterations despite failures
        self.assertEqual(mock_get_windows.call_count, 3)
        
    def test_configuration_error_handling(self):
        """Test handling of invalid configuration."""
        # Test with invalid configuration
        invalid_config = {
            "automation": {
                "interval_seconds": "invalid",  # Should be float
                "dry_run": "maybe"  # Should be boolean
            },
            "detection": {
                "confidence_threshold": 2.0  # Should be <= 1.0
            }
        }
        
        config_manager = ConfigManager()
        config_manager.config = invalid_config
        
        # Should create engine without crashing
        try:
            engine = AutomationEngine(config_manager)
            self.assertIsNotNone(engine)
        except Exception:
            self.fail("AutomationEngine should handle invalid config gracefully")
            
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    def test_memory_and_resource_error_handling(
        self, mock_capture, mock_get_windows
    ):
        """Test handling of memory and resource errors."""
        mock_windows = [
            VSCodeWindow(1, "VS Code", 123, 100, 100, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        # Simulate memory error during screenshot
        mock_capture.side_effect = MemoryError("Out of memory")
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iteration():
            # Should handle memory error gracefully
            await engine._run_iteration()
            
        asyncio.run(run_iteration())
        
        mock_capture.assert_called_once()
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    def test_timeout_error_handling(
        self, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test handling of timeout errors."""
        mock_windows = [
            VSCodeWindow(1, "VS Code", 123, 100, 100, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (800, 600))
        mock_capture.return_value = mock_screenshot
        
        # Simulate timeout during button detection
        mock_find_buttons.side_effect = TimeoutError("Operation timed out")
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iteration():
            # Should handle timeout gracefully
            await engine._run_iteration()
            
        asyncio.run(run_iteration())
        
        mock_find_buttons.assert_called_once()
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    @patch('src.core.click_automator.ClickAutomator.click')
    def test_error_statistics_tracking(
        self, mock_click, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test that errors are properly tracked in statistics."""
        mock_windows = [
            VSCodeWindow(1, "VS Code", 123, 100, 100, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (800, 600))
        mock_capture.return_value = mock_screenshot
        
        # Mix of successes and failures
        mock_find_buttons.side_effect = [
            Exception("Error 1"),
            [ButtonLocation(100, 100, 100, 30, 0.9, 'ocr', 'Continue')],
            Exception("Error 2")
        ]
        
        mock_click.return_value = True
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iterations():
            await engine._run_iteration()  # Error
            await engine._run_iteration()  # Success
            await engine._run_iteration()  # Error
            
        asyncio.run(run_iterations())
        
        # Check that error statistics are tracked
        stats = engine.stats
        self.assertGreaterEqual(stats['errors'], 2)
        
    def test_emergency_stop_functionality(self):
        """Test emergency stop error handling."""
        engine = AutomationEngine(self.config_manager)
        
        # Trigger emergency stop
        engine.emergency_stop()
        
        # Should set emergency stop flag and stop running
        self.assertTrue(engine._emergency_stop)
        self.assertFalse(engine.running)


if __name__ == '__main__':
    unittest.main()
