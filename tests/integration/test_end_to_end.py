"""Integration tests for end-to-end automation workflow."""

import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.automation_engine import AutomationEngine
from src.core.button_finder import ButtonLocation
from src.core.config_manager import ConfigManager
from src.core.window_detector import VSCodeWindow


class TestEndToEnd(unittest.TestCase):
    """Integration tests for end-to-end automation workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.config_manager = ConfigManager()
        self.config_manager.config = {
            "automation": {
                "interval_seconds": 0.1,
                "dry_run": True,
                "click_delay": 0.01
            },
            "detection": {
                "confidence_threshold": 0.8,
                "button_text": ["Continue", "继续"]
            },
            "safety": {
                "require_confirmation": False
            },
            "logging": {
                "level": "INFO",
                "console_output": False
            }
        }
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    @patch('src.core.click_automator.ClickAutomator.click')
    def test_complete_automation_workflow(
        self, mock_click, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test complete automation workflow from window detection to clicking."""
        # Setup mocks
        mock_windows = [
            VSCodeWindow(1, "VS Code - main.py", 123, 100, 100, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (800, 600), color='blue')
        mock_capture.return_value = mock_screenshot
        
        mock_buttons = [
            ButtonLocation(200, 300, 100, 30, 0.9, 'ocr', 'Continue')
        ]
        mock_find_buttons.return_value = mock_buttons
        
        mock_click.return_value = True
        
        # Create and run automation engine
        engine = AutomationEngine(self.config_manager)
        
        async def run_single_iteration():
            await engine._run_iteration()
            
        asyncio.run(run_single_iteration())
        
        # Verify the complete workflow
        mock_get_windows.assert_called_once()
        mock_capture.assert_called_once_with(100, 100, 800, 600)
        mock_find_buttons.assert_called_once()
        mock_click.assert_called_once_with(mock_buttons[0])
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    def test_workflow_with_multiple_windows(
        self, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test workflow with multiple VS Code windows."""
        # Setup multiple windows
        mock_windows = [
            VSCodeWindow(1, "VS Code - file1.py", 123, 0, 0, 800, 600),
            VSCodeWindow(2, "VS Code - file2.py", 124, 800, 0, 800, 600),
            VSCodeWindow(3, "VS Code - file3.py", 125, 0, 600, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (800, 600))
        mock_capture.return_value = mock_screenshot
        
        # First window has a button, others don't
        mock_find_buttons.side_effect = [
            [ButtonLocation(100, 100, 100, 30, 0.9, 'ocr', 'Continue')],
            [],  # No buttons in second window
            []   # No buttons in third window
        ]
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_single_iteration():
            await engine._run_iteration()
            
        asyncio.run(run_single_iteration())
        
        # Verify all windows were processed
        mock_get_windows.assert_called_once()
        self.assertEqual(mock_capture.call_count, 3)
        self.assertEqual(mock_find_buttons.call_count, 3)
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    def test_workflow_with_no_windows(self, mock_get_windows):
        """Test workflow when no VS Code windows are found."""
        mock_get_windows.return_value = []
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_single_iteration():
            await engine._run_iteration()
            
        asyncio.run(run_single_iteration())
        
        mock_get_windows.assert_called_once()
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    def test_workflow_with_screenshot_failure(
        self, mock_capture, mock_get_windows
    ):
        """Test workflow when screenshot capture fails."""
        mock_windows = [
            VSCodeWindow(1, "VS Code", 123, 100, 100, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        # Screenshot fails
        mock_capture.return_value = None
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_single_iteration():
            await engine._run_iteration()
            
        asyncio.run(run_single_iteration())
        
        mock_get_windows.assert_called_once()
        mock_capture.assert_called_once()
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    @patch('src.core.click_automator.ClickAutomator.click')
    def test_workflow_with_click_failure(
        self, mock_click, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test workflow when button click fails."""
        mock_windows = [
            VSCodeWindow(1, "VS Code", 123, 100, 100, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (800, 600))
        mock_capture.return_value = mock_screenshot
        
        mock_buttons = [
            ButtonLocation(200, 300, 100, 30, 0.9, 'ocr', 'Continue')
        ]
        mock_find_buttons.return_value = mock_buttons
        
        # Click fails
        mock_click.return_value = False
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_single_iteration():
            await engine._run_iteration()
            
        asyncio.run(run_single_iteration())
        
        # Workflow should complete even with click failure
        mock_click.assert_called_once()
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    @patch('src.core.click_automator.ClickAutomator.click')
    def test_workflow_with_multiple_buttons(
        self, mock_click, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test workflow when multiple buttons are found."""
        mock_windows = [
            VSCodeWindow(1, "VS Code", 123, 100, 100, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (800, 600))
        mock_capture.return_value = mock_screenshot
        
        # Multiple buttons found
        mock_buttons = [
            ButtonLocation(200, 300, 100, 30, 0.9, 'ocr', 'Continue'),
            ButtonLocation(400, 300, 100, 30, 0.8, 'template', 'Continue'),
            ButtonLocation(600, 300, 100, 30, 0.7, 'color', 'Continue')
        ]
        mock_find_buttons.return_value = mock_buttons
        
        mock_click.return_value = True
        
        engine = AutomationEngine(self.config_manager)
        
        async def run_single_iteration():
            await engine._run_iteration()
            
        asyncio.run(run_single_iteration())
        
        # Should click all buttons found
        self.assertEqual(mock_click.call_count, 3)
        
    def test_configuration_integration(self):
        """Test integration with configuration system."""
        # Test that all components respect configuration
        custom_config = {
            "automation": {
                "interval_seconds": 5.0,
                "dry_run": False,
                "click_delay": 0.5
            },
            "detection": {
                "confidence_threshold": 0.9,
                "button_text": ["Continue", "Next", "Proceed"]
            }
        }
        
        config_manager = ConfigManager()
        config_manager.config = custom_config
        
        engine = AutomationEngine(config_manager)
        
        # Verify configuration is properly passed to components
        self.assertEqual(
            engine.config_manager.get('automation.interval_seconds'), 5.0
        )
        self.assertFalse(
            engine.config_manager.get('automation.dry_run')
        )
        
    @patch('src.core.window_detector.WindowDetector.get_vscode_windows')
    @patch('src.utils.screen_capture.ScreenCapture.capture_region')
    @patch('src.core.button_finder.ButtonFinder.find_continue_buttons')
    def test_error_recovery_integration(
        self, mock_find_buttons, mock_capture, mock_get_windows
    ):
        """Test error recovery across the workflow."""
        mock_windows = [
            VSCodeWindow(1, "VS Code", 123, 100, 100, 800, 600)
        ]
        mock_get_windows.return_value = mock_windows
        
        mock_screenshot = Image.new('RGB', (800, 600))
        mock_capture.return_value = mock_screenshot
        
        # First call fails, second succeeds
        mock_find_buttons.side_effect = [
            Exception("Button detection failed"),
            [ButtonLocation(200, 300, 100, 30, 0.9, 'ocr', 'Continue')]
        ]
        
        engine = AutomationEngine(self.config_manager)
        
        # First iteration should handle error gracefully
        async def run_iterations():
            await engine._run_iteration()  # Should handle error
            await engine._run_iteration()  # Should succeed
            
        asyncio.run(run_iterations())
        
        # Should have attempted button detection twice
        self.assertEqual(mock_find_buttons.call_count, 2)


if __name__ == '__main__':
    unittest.main()
