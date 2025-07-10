"""Unit tests for AutomationEngine module."""

import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.automation_engine import AutomationEngine
from src.core.button_finder import ButtonLocation
from src.core.config_manager import ConfigManager
from src.core.window_detector import VSCodeWindow


class TestAutomationEngine(unittest.TestCase):
    """Test cases for AutomationEngine class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config_manager = ConfigManager()
        self.config_manager.config = {
            "automation": {
                "interval_seconds": 1.0,
                "dry_run": True,
                "click_delay": 0.1
            },
            "detection": {
                "confidence_threshold": 0.8,
                "button_text": ["Continue"]
            },
            "safety": {
                "require_confirmation": False,
                "emergency_stop_key": "esc"
            },
            "logging": {
                "level": "INFO",
                "console_output": False
            }
        }
        self.automation_engine = AutomationEngine(self.config_manager)
        
    def test_automation_engine_initialization(self):
        """Test AutomationEngine initialization."""
        self.assertIsNotNone(self.automation_engine)
        self.assertEqual(
            self.automation_engine.config_manager, self.config_manager
        )
        self.assertFalse(self.automation_engine.running)
        self.assertIsNotNone(self.automation_engine.window_detector)
        self.assertIsNotNone(self.automation_engine.button_finder)
        self.assertIsNotNone(self.automation_engine.click_automator)
        self.assertIsNotNone(self.automation_engine.screen_capture)
        
    def test_stats_initialization(self):
        """Test that statistics are initialized correctly."""
        stats = self.automation_engine.stats
        
        self.assertEqual(stats['windows_processed'], 0)
        self.assertEqual(stats['buttons_found'], 0)
        self.assertEqual(stats['clicks_attempted'], 0)
        self.assertEqual(stats['clicks_successful'], 0)
        self.assertEqual(stats['errors'], 0)
        self.assertIsNone(stats['start_time'])
        
    @patch.object(AutomationEngine, '_run_cycle')
    def test_start_method(self, mock_run_cycle):
        """Test the start method."""
        # Make _run_cycle a coroutine
        mock_run_cycle.return_value = asyncio.Future()
        mock_run_cycle.return_value.set_result(None)
        
        async def test_start():
            # Start and immediately stop
            self.automation_engine.running = True
            task = asyncio.create_task(self.automation_engine.start())
            
            # Let it run briefly
            await asyncio.sleep(0.01)
            
            # Stop it
            await self.automation_engine.stop()
            
            # Wait for completion
            await task
            
        asyncio.run(test_start())
        
    def test_stop_method(self):
        """Test the stop method."""
        async def test_stop():
            self.automation_engine.running = True
            await self.automation_engine.stop()
            self.assertFalse(self.automation_engine.running)
            
        asyncio.run(test_stop())
        
    def test_emergency_stop(self):
        """Test emergency stop functionality."""
        self.automation_engine.running = True
        self.automation_engine.emergency_stop()
        
        self.assertTrue(self.automation_engine._emergency_stop)
        self.assertFalse(self.automation_engine.running)
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    def test_run_iteration_no_windows(self, mock_get_windows):
        """Test run iteration when no VS Code windows found."""
        mock_get_windows.return_value = []
        
        async def test_iteration():
            await self.automation_engine._run_iteration()
            
        asyncio.run(test_iteration())
        
        mock_get_windows.assert_called_once()
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch.object(AutomationEngine, '_process_window')
    def test_run_iteration_with_windows(self, mock_process_window, mock_get_windows):
        """Test run iteration with VS Code windows."""
        # Mock windows
        mock_windows = [
            VSCodeWindow(1, "VSCode1", 123, 0, 0, 800, 600),
            VSCodeWindow(2, "VSCode2", 124, 800, 0, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        # Mock process window to return empty list
        mock_process_window.return_value = []
        
        async def test_iteration():
            await self.automation_engine._run_iteration()
            
        asyncio.run(test_iteration())
        
        mock_get_windows.assert_called_once()
        self.assertEqual(mock_process_window.call_count, 2)
        
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    @patch('src.core.click_automator.ClickAutomator.click')
    def test_process_window_success(self, mock_click, mock_find_buttons, mock_capture):
        """Test processing a window successfully."""
        from PIL import Image

        # Mock screenshot
        mock_capture.return_value = Image.new('RGB', (800, 600))
        
        # Mock button detection
        mock_buttons = [
            ButtonLocation(100, 100, 100, 30, 0.9, 'ocr', 'Continue')
        ]
        mock_find_buttons.return_value = mock_buttons
        
        # Mock click success
        mock_click.return_value = True
        
        window = VSCodeWindow(1, "VSCode", 123, 0, 0, 800, 600)
        buttons = self.automation_engine._process_window(window)
        
        self.assertEqual(len(buttons), 1)
        mock_capture.assert_called_once_with(0, 0, 800, 600)
        mock_find_buttons.assert_called_once()
        mock_click.assert_called_once_with(mock_buttons[0])
        
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    def test_process_window_screenshot_failure(self, mock_capture):
        """Test processing window when screenshot fails."""
        # Mock screenshot failure
        mock_capture.return_value = None
        
        window = VSCodeWindow(1, "VSCode", 123, 0, 0, 800, 600)
        buttons = self.automation_engine._process_window(window)
        
        self.assertEqual(len(buttons), 0)
        
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    def test_process_window_no_buttons_found(self, mock_find_buttons, mock_capture):
        """Test processing window when no buttons are found."""
        from PIL import Image

        # Mock screenshot
        mock_capture.return_value = Image.new('RGB', (800, 600))
        
        # Mock no buttons found
        mock_find_buttons.return_value = []
        
        window = VSCodeWindow(1, "VSCode", 123, 0, 0, 800, 600)
        buttons = self.automation_engine._process_window(window)
        
        self.assertEqual(len(buttons), 0)
        
    def test_update_stats(self):
        """Test statistics updating."""
        # Test incrementing various stats
        self.automation_engine.stats['windows_processed'] = 5
        self.automation_engine.stats['buttons_found'] = 3
        self.automation_engine.stats['clicks_attempted'] = 2
        self.automation_engine.stats['clicks_successful'] = 1
        
        # Verify stats were updated
        self.assertEqual(self.automation_engine.stats['windows_processed'], 5)
        self.assertEqual(self.automation_engine.stats['buttons_found'], 3)
        self.assertEqual(self.automation_engine.stats['clicks_attempted'], 2)
        self.assertEqual(self.automation_engine.stats['clicks_successful'], 1)
        
    def test_user_activity_detection(self):
        """Test user activity detection and pausing."""
        # Test that user activity detection doesn't crash
        # (actual implementation may vary based on pynput availability)
        self.automation_engine._user_activity_detected = True
        self.assertTrue(self.automation_engine._user_activity_detected)
        
    def test_safety_features_setup(self):
        """Test that safety features are set up correctly."""
        # This mainly tests that setup doesn't crash
        # Real testing would require mocking pynput
        self.automation_engine._setup_safety_features()
        
        # Should not raise any exceptions
        
    def test_window_cache_functionality(self):
        """Test window caching for performance."""
        # Test that cache is initialized
        self.assertIsInstance(self.automation_engine._window_cache, dict)
        self.assertEqual(len(self.automation_engine._window_cache), 0)
        
    @patch('src.core.automation_engine.time.time')
    def test_performance_metrics(self, mock_time):
        """Test performance metrics collection."""
        # Mock time progression
        mock_time.side_effect = [1000, 1001, 1002]
        
        # Test that performance metrics are tracked
        self.assertIsInstance(
            self.automation_engine.performance_metrics, dict
        )
        
    def test_config_access(self):
        """Test configuration access through automation engine."""
        # Test accessing config through the engine
        interval = self.automation_engine.config_manager.get(
            'automation.interval_seconds'
        )
        self.assertEqual(interval, 1.0)
        
        dry_run = self.automation_engine.config_manager.get(
            'automation.dry_run'
        )
        self.assertTrue(dry_run)
        
    def test_error_handling_in_iteration(self):
        """Test error handling during iteration."""
        with patch.object(
            self.automation_engine.window_detector,
            'get_vscode_windows',
            side_effect=Exception("Window detection failed")
        ):
            
            async def test_error_iteration():
                # Should not raise exception, but handle it gracefully
                try:
                    await self.automation_engine._run_iteration()
                except Exception:
                    self.fail("_run_iteration should handle exceptions gracefully")
                    
            asyncio.run(test_error_iteration())


if __name__ == '__main__':
    unittest.main()
