import os

# Add src to path
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.high_capacity_automation import HighCapacityAutomation
from src.core.window_detector import VSCodeWindow


class TestContinueButtonRecognition(unittest.TestCase):

    def setUp(self):
        """Set up the test environment."""
        self.automation = HighCapacityAutomation()
        # Mock the click automator to prevent actual clicks
        self.automation.click_automator = MagicMock()

    @patch("scripts.high_capacity_automation.subprocess.run")
    @patch("scripts.high_capacity_automation.Image.open")
    def test_recognize_continue_button_in_test_html(self, mock_image_open, mock_subprocess_run):
        """
        Test if the automation can recognize the Continue button in the test HTML file.
        """
        # --- Mocking Setup ---

        # 1. Mock the window
        test_window = VSCodeWindow(
            window_id=12345,
            title="Test Continue Button - VS Code",
            pid=6789,
            x=100,
            y=100,
            width=800,
            height=600,
            is_focused=True,
        )

        # 2. Mock the screenshot process
        # Create a dummy screenshot file that the test can "open"
        dummy_screenshot_path = "/tmp/test_screenshot.png"
        Path(dummy_screenshot_path).touch()

        # Mock `capture_vscode_window_safely` to return the path to our dummy file
        self.automation.capture_vscode_window_safely = MagicMock(return_value=dummy_screenshot_path)

        # Mock `Image.open` to return a mock image object
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image

        # 3. Mock the ButtonFinder
        # Simulate that the button finder successfully finds a button
        mock_button = MagicMock()
        mock_button.x = 200
        mock_button.y = 250
        mock_button.width = 100
        mock_button.height = 40

        self.automation.button_finder.find_continue_buttons = MagicMock(return_value=[mock_button])

        # --- Test Execution ---

        # Run the processing logic for our mock window
        result = self.automation.process_vscode_window_safely(test_window)

        # --- Assertions ---

        # 1. Verify that the automation reported a successful click
        self.assertTrue(result, "Should return True on successful button click")

        # 2. Check that `find_continue_buttons` was called correctly
        self.automation.button_finder.find_continue_buttons.assert_called_once_with(
            mock_image, test_window.x, test_window.y
        )

        # 3. Verify that the click was attempted at the correct coordinates
        expected_x = test_window.x + mock_button.x + (mock_button.width // 2)
        expected_y = test_window.y + mock_button.y + (mock_button.height // 2)

        self.automation.click_automator.click.assert_called_once_with(expected_x, expected_y)

        # 4. Ensure the temporary screenshot was cleaned up
        # We need to patch `os.remove` to check if it was called
        with patch("os.remove") as mock_remove:
            # Rerun the logic to check the cleanup call
            self.automation.process_vscode_window_safely(test_window)
            mock_remove.assert_called_with(dummy_screenshot_path)


if __name__ == "__main__":
    unittest.main()
