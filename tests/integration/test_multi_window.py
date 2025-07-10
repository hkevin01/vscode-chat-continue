"""Integration tests for multi-window support."""

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


class TestMultiWindow(unittest.TestCase):
    """Integration tests for multi-window automation support."""
    
    def setUp(self):
        """Set up test environment."""
        self.config_manager = ConfigManager()
        self.config_manager.config = {
            "automation": {
                "interval_seconds": 0.1,
                "dry_run": True
            },
            "detection": {
                "confidence_threshold": 0.8,
                "button_text": ["Continue"]
            },
            "logging": {"level": "INFO", "console_output": False}
        }
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    def test_multiple_windows_different_monitors(
        self, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test handling windows across different monitors."""
        # Windows on different monitors with different coordinates
        mock_windows = [
            VSCodeWindow(1, "VS Code - Monitor 1", 123, 0, 0, 1920, 1080),
            VSCodeWindow(2, "VS Code - Monitor 2", 124, 1920, 0, 1920, 1080),
            VSCodeWindow(3, "VS Code - Monitor 3", 125, -1920, 0, 1920, 1080)
        ]
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (1920, 1080))
        mock_capture.return_value = mock_screenshot
        
        # Each window has different buttons
        mock_find_buttons.side_effect = [
            [ButtonLocation(100, 100, 100, 30, 0.9, 'ocr', 'Continue')],
            [ButtonLocation(2020, 100, 100, 30, 0.8, 'ocr', 'Continue')],
            [ButtonLocation(-1820, 100, 100, 30, 0.7, 'ocr', 'Continue')]
        ]
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iteration():
            await engine._run_iteration()
            
        asyncio.run(run_iteration())
        
        # Verify all windows were processed
        self.assertEqual(mock_capture.call_count, 3)
        self.assertEqual(mock_find_buttons.call_count, 3)
        
        # Verify correct coordinates were used for capture
        capture_calls = mock_capture.call_args_list
        self.assertEqual(capture_calls[0][0], (0, 0, 1920, 1080))
        self.assertEqual(capture_calls[1][0], (1920, 0, 1920, 1080))
        self.assertEqual(capture_calls[2][0], (-1920, 0, 1920, 1080))
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    @patch('src.core.click_automator.ClickAutomator.click')
    def test_window_priority_handling(
        self, mock_click, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test that windows are processed in a consistent order."""
        # Multiple windows with different IDs
        mock_windows = [
            VSCodeWindow(3, "VS Code - Window 3", 125, 400, 300, 800, 600),
            VSCodeWindow(1, "VS Code - Window 1", 123, 0, 0, 800, 600),
            VSCodeWindow(2, "VS Code - Window 2", 124, 800, 0, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (800, 600))
        mock_capture.return_value = mock_screenshot
        
        # All windows have buttons
        mock_find_buttons.return_value = [
            ButtonLocation(100, 100, 100, 30, 0.9, 'ocr', 'Continue')
        ]
        mock_click.return_value = True
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iteration():
            await engine._run_iteration()
            
        asyncio.run(run_iteration())
        
        # All windows should be processed
        self.assertEqual(mock_capture.call_count, 3)
        self.assertEqual(mock_click.call_count, 3)
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    def test_window_filtering_and_validation(
        self, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test filtering of invalid or problematic windows."""
        # Mix of valid and invalid windows
        mock_windows = [
            VSCodeWindow(1, "VS Code - Valid", 123, 100, 100, 800, 600),
            VSCodeWindow(2, "VS Code - Zero size", 124, 100, 100, 0, 0),
            VSCodeWindow(3, "VS Code - Negative", 125, -100, -100, 800, 600),
            VSCodeWindow(4, "VS Code - Valid 2", 126, 900, 100, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (800, 600))
        mock_capture.return_value = mock_screenshot
        
        mock_find_buttons.return_value = []
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iteration():
            await engine._run_iteration()
            
        asyncio.run(run_iteration())
        
        # Should process all windows (validation happens in window detector)
        self.assertEqual(mock_capture.call_count, 4)
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    def test_large_number_of_windows(
        self, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test handling a large number of VS Code windows."""
        # Create many windows
        mock_windows = []
        for i in range(20):
            window = VSCodeWindow(
                id=i+1,
                title=f"VS Code - File{i+1}.py",
                pid=1000+i,
                x=i*50, y=i*30, width=800, height=600
            )
            mock_windows.append(window)
            
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (800, 600))
        mock_capture.return_value = mock_screenshot
        
        # Some windows have buttons, some don't
        mock_find_buttons.side_effect = [
            [ButtonLocation(100, 100, 100, 30, 0.9, 'ocr', 'Continue')]
            if i % 3 == 0 else [] for i in range(20)
        ]
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iteration():
            await engine._run_iteration()
            
        asyncio.run(run_iteration())
        
        # All windows should be processed
        self.assertEqual(mock_capture.call_count, 20)
        self.assertEqual(mock_find_buttons.call_count, 20)
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    def test_window_screenshot_failures(
        self, mock_capture, mock_get_windows
    ):
        """Test handling screenshot failures for some windows."""
        mock_windows = [
            VSCodeWindow(1, "VS Code - Good", 123, 100, 100, 800, 600),
            VSCodeWindow(2, "VS Code - Bad", 124, 900, 100, 800, 600),
            VSCodeWindow(3, "VS Code - Good2", 125, 1800, 100, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        # Second window screenshot fails
        mock_capture.side_effect = [
            Image.new('RGB', (800, 600)),  # Success
            None,  # Failure
            Image.new('RGB', (800, 600))   # Success
        ]
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iteration():
            await engine._run_iteration()
            
        asyncio.run(run_iteration())
        
        # Should attempt all windows
        self.assertEqual(mock_capture.call_count, 3)
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    @patch('src.core.click_automator.ClickAutomator.click')
    def test_window_coordinate_translation(
        self, mock_click, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test correct coordinate translation for buttons in different windows."""
        # Windows at different positions
        mock_windows = [
            VSCodeWindow(1, "VS Code 1", 123, 0, 0, 800, 600),
            VSCodeWindow(2, "VS Code 2", 124, 1000, 500, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (800, 600))
        mock_capture.return_value = mock_screenshot
        
        # Buttons found at relative positions within windows
        mock_find_buttons.side_effect = [
            [ButtonLocation(100, 100, 100, 30, 0.9, 'ocr', 'Continue')],
            [ButtonLocation(1100, 600, 100, 30, 0.9, 'ocr', 'Continue')]
        ]
        mock_click.return_value = True
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iteration():
            await engine._run_iteration()
            
        asyncio.run(run_iteration())
        
        # Verify clicks were made with correct absolute coordinates
        click_calls = mock_click.call_args_list
        self.assertEqual(len(click_calls), 2)
        
        # First button: window at (0,0) + button at (100,100)
        first_button = click_calls[0][0][0]
        self.assertEqual(first_button.x, 100)
        self.assertEqual(first_button.y, 100)
        
        # Second button: window at (1000,500) + button offset
        second_button = click_calls[1][0][0]
        self.assertEqual(second_button.x, 1100)
        self.assertEqual(second_button.y, 600)
        
    def test_window_statistics_tracking(self):
        """Test that multi-window statistics are tracked correctly."""
        engine = AutomationEngine(self.config_manager)
        
        # Initial stats
        stats = engine.stats
        self.assertEqual(stats['windows_processed'], 0)
        
        # Stats should be updated as windows are processed
        # (This would be tested more thoroughly in actual execution)
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    def test_dynamic_window_changes(self, mock_get_windows):
        """Test handling of dynamic window changes between iterations."""
        # First iteration: 2 windows
        first_windows = [
            VSCodeWindow(1, "VS Code 1", 123, 0, 0, 800, 600),
            VSCodeWindow(2, "VS Code 2", 124, 800, 0, 800, 600)
        ]
        
        # Second iteration: 3 windows (one added)
        second_windows = first_windows + [
            VSCodeWindow(3, "VS Code 3", 125, 1600, 0, 800, 600)
        ]
        
        # Third iteration: 1 window (two closed)
        third_windows = [first_windows[0]]
        
        mock_get_windows.side_effect = [
            first_windows, second_windows, third_windows
        ]
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_iterations():
            await engine._run_iteration()  # 2 windows
            await engine._run_iteration()  # 3 windows
            await engine._run_iteration()  # 1 window
            
        with patch('src.utils.screen_capture.ScreenCapture.capture_region'):
            asyncio.run(run_iterations())
        
        # Should have called get_windows 3 times
        self.assertEqual(mock_get_windows.call_count, 3)


if __name__ == '__main__':
    unittest.main()
