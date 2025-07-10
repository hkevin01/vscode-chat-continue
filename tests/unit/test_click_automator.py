"""Unit tests for ClickAutomator module."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.button_finder import ButtonLocation
from src.core.click_automator import ClickAutomator


class TestClickAutomator(unittest.TestCase):
    """Test cases for ClickAutomator class."""
    
    def setUp(self):
        """Set up test environment."""
        self.click_automator = ClickAutomator()
        self.button_location = ButtonLocation(
            x=100, y=200, width=150, height=40,
            confidence=0.9, method='ocr', text='Continue'
        )
        
    def test_click_automator_initialization(self):
        """Test ClickAutomator initialization."""
        self.assertIsNotNone(self.click_automator)
        self.assertEqual(self.click_automator.click_delay, 0.1)
        self.assertEqual(self.click_automator.move_duration, 0.2)
        self.assertFalse(self.click_automator.dry_run)
        
    def test_click_automator_initialization_with_params(self):
        """Test ClickAutomator initialization with custom parameters."""
        automator = ClickAutomator(
            click_delay=0.5, move_duration=1.0, dry_run=True
        )
        
        self.assertEqual(automator.click_delay, 0.5)
        self.assertEqual(automator.move_duration, 1.0)
        self.assertTrue(automator.dry_run)
        
    @patch('pyautogui.moveTo')
    @patch('pyautogui.click')
    @patch('time.sleep')
    def test_click_button_success(self, mock_sleep, mock_click, mock_move_to):
        """Test successful button clicking."""
        result = self.click_automator.click(self.button_location)
        
        self.assertTrue(result)
        
        # Verify move to center of button
        expected_x = self.button_location.center_x
        expected_y = self.button_location.center_y
        mock_move_to.assert_called_once_with(
            expected_x, expected_y, self.click_automator.move_duration
        )
        
        # Verify click
        mock_click.assert_called_once()
        
        # Verify delay
        mock_sleep.assert_called_once_with(
            self.click_automator.click_delay
        )
        
    @patch('pyautogui.moveTo')
    @patch('pyautogui.click')
    def test_click_button_dry_run(self, mock_click, mock_move_to):
        """Test button clicking in dry run mode."""
        self.click_automator.dry_run = True
        
        result = self.click_automator.click(self.button_location)
        
        self.assertTrue(result)
        
        # In dry run, should not actually move or click
        mock_move_to.assert_not_called()
        mock_click.assert_not_called()
        
    @patch('pyautogui.moveTo', side_effect=Exception("Move failed"))
    def test_click_button_move_failure(self, mock_move_to):
        """Test handling of mouse move failure."""
        result = self.click_automator.click(self.button_location)
        
        self.assertFalse(result)
        
    @patch('pyautogui.moveTo')
    @patch('pyautogui.click', side_effect=Exception("Click failed"))
    def test_click_button_click_failure(self, mock_click, mock_move_to):
        """Test handling of mouse click failure."""
        result = self.click_automator.click(self.button_location)
        
        self.assertFalse(result)
        
    def test_click_with_offset(self):
        """Test clicking with offset."""
        offset_x, offset_y = 5, -10
        self.click_automator.offset_x = offset_x
        self.click_automator.offset_y = offset_y
        
        with patch('pyautogui.moveTo') as mock_move_to:
            with patch('pyautogui.click'):
                self.click_automator.click(self.button_location)
                
                expected_x = self.button_location.center_x + offset_x
                expected_y = self.button_location.center_y + offset_y
                mock_move_to.assert_called_once_with(
                    expected_x, expected_y, self.click_automator.move_duration
                )
                
    @patch('pyautogui.moveTo')
    @patch('pyautogui.click')
    def test_click_coordinates_calculation(self, mock_click, mock_move_to):
        """Test that click coordinates are calculated correctly."""
        # Button at x=100, y=200, width=150, height=40
        # Center should be at x=175, y=220
        
        self.click_automator.click(self.button_location)
        
        mock_move_to.assert_called_once_with(175, 220, 0.2)
        
    def test_click_with_zero_size_button(self):
        """Test clicking on zero-size button."""
        zero_button = ButtonLocation(
            x=100, y=200, width=0, height=0,
            confidence=0.9, method='test'
        )
        
        with patch('pyautogui.moveTo') as mock_move_to:
            with patch('pyautogui.click'):
                self.click_automator.click(zero_button)
                
                # Should still click at the x,y position
                mock_move_to.assert_called_once_with(100, 200, 0.2)
                
    @patch('pyautogui.moveTo')
    @patch('pyautogui.click')
    def test_multiple_clicks(self, mock_click, mock_move_to):
        """Test multiple clicks in sequence."""
        buttons = [
            ButtonLocation(100, 100, 50, 20, 0.9, 'test1'),
            ButtonLocation(200, 200, 50, 20, 0.9, 'test2'),
            ButtonLocation(300, 300, 50, 20, 0.9, 'test3')
        ]
        
        results = []
        for button in buttons:
            result = self.click_automator.click(button)
            results.append(result)
            
        # All clicks should succeed
        self.assertTrue(all(results))
        
        # Should have moved and clicked for each button
        self.assertEqual(mock_move_to.call_count, 3)
        self.assertEqual(mock_click.call_count, 3)
        
    @patch('pyautogui.failSafeCheck')
    @patch('pyautogui.moveTo')
    @patch('pyautogui.click')
    def test_pyautogui_fail_safe(self, mock_click, mock_move_to, mock_fail_safe):
        """Test handling of pyautogui fail-safe mechanism."""
        mock_fail_safe.side_effect = Exception("Fail-safe triggered")
        
        result = self.click_automator.click(self.button_location)
        
        self.assertFalse(result)
        
    def test_button_location_validation(self):
        """Test that ButtonLocation objects are handled correctly."""
        # Test with minimal ButtonLocation
        minimal_button = ButtonLocation(
            x=50, y=50, width=100, height=30, confidence=0.5, method='test'
        )
        
        with patch('pyautogui.moveTo') as mock_move_to:
            with patch('pyautogui.click'):
                result = self.click_automator.click(minimal_button)
                
                self.assertTrue(result)
                mock_move_to.assert_called_once_with(100, 65, 0.2)


if __name__ == '__main__':
    unittest.main()
