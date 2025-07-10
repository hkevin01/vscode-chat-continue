"""Unit tests for ButtonFinder module."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.button_finder import ButtonFinder, ButtonLocation
from src.core.config_manager import ConfigManager


class TestButtonFinder(unittest.TestCase):
    """Test cases for ButtonFinder class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config_manager = ConfigManager()
        self.config_manager.config = {
            "detection": {
                "confidence_threshold": 0.8,
                "button_text": ["Continue", "继续"],
                "tesseract_config": r'--oem 3 --psm 6'
            }
        }
        self.button_finder = ButtonFinder(self.config_manager)
        self.test_image = Image.new('RGB', (200, 100), color='blue')
        
    def test_button_finder_initialization(self):
        """Test ButtonFinder initialization."""
        self.assertIsNotNone(self.button_finder)
        self.assertEqual(
            self.button_finder.config_manager, self.config_manager
        )
        self.assertIsInstance(
            self.button_finder.continue_patterns, list
        )
        
    def test_button_location_dataclass(self):
        """Test ButtonLocation dataclass."""
        button = ButtonLocation(
            x=10, y=20, width=100, height=30,
            confidence=0.9, method='ocr', text='Continue'
        )
        
        self.assertEqual(button.x, 10)
        self.assertEqual(button.y, 20)
        self.assertEqual(button.width, 100)
        self.assertEqual(button.height, 30)
        self.assertEqual(button.confidence, 0.9)
        self.assertEqual(button.method, 'ocr')
        self.assertEqual(button.text, 'Continue')
        
    def test_button_location_center_properties(self):
        """Test ButtonLocation center coordinate properties."""
        button = ButtonLocation(
            x=10, y=20, width=100, height=30,
            confidence=0.9, method='ocr'
        )
        
        self.assertEqual(button.center_x, 60)  # 10 + 100//2
        self.assertEqual(button.center_y, 35)  # 20 + 30//2
        self.assertEqual(button.center, (60, 35))
        
    @patch('pytesseract.image_to_data')
    def test_find_buttons_ocr_success(self, mock_image_to_data):
        """Test OCR button detection with successful detection."""
        # Mock Tesseract response
        mock_image_to_data.return_value = {
            'level': [1, 2, 3, 4, 5],
            'left': [10, 50, 60, 70, 80],
            'top': [10, 50, 50, 50, 50],
            'width': [30, 40, 50, 60, 70],
            'height': [10, 20, 20, 20, 20],
            'conf': [95, 90, 85, 80, 75],
            'text': ['', 'Continue', '', 'button', '']
        }
        
        buttons = self.button_finder._find_buttons_ocr(
            self.test_image, 0, 0
        )
        
        self.assertGreater(len(buttons), 0)
        self.assertEqual(buttons[0].text, 'continue')
        self.assertEqual(buttons[0].method, 'ocr')
        
    @patch('pytesseract.image_to_data')
    def test_find_buttons_ocr_no_results(self, mock_image_to_data):
        """Test OCR button detection with no results."""
        # Mock Tesseract response with no Continue buttons
        mock_image_to_data.return_value = {
            'level': [1, 2],
            'left': [10, 50],
            'top': [10, 50],
            'width': [30, 40],
            'height': [10, 20],
            'conf': [95, 90],
            'text': ['', 'Other Text']
        }
        
        buttons = self.button_finder._find_buttons_ocr(
            self.test_image, 0, 0
        )
        
        self.assertEqual(len(buttons), 0)
        
    def test_matches_continue_pattern(self):
        """Test continue pattern matching."""
        # Test exact matches
        self.assertTrue(
            self.button_finder._matches_continue_pattern('Continue')
        )
        self.assertTrue(
            self.button_finder._matches_continue_pattern('continue')
        )
        self.assertTrue(
            self.button_finder._matches_continue_pattern('继续')
        )
        
        # Test non-matches
        self.assertFalse(
            self.button_finder._matches_continue_pattern('Cancel')
        )
        self.assertFalse(
            self.button_finder._matches_continue_pattern('Submit')
        )
        
    @patch('cv2.imread')
    @patch('cv2.matchTemplate')
    def test_find_buttons_template_matching(self, mock_match_template, mock_imread):
        """Test template matching button detection."""
        # Mock template loading
        mock_template = np.zeros((20, 80, 3), dtype=np.uint8)
        mock_imread.return_value = mock_template
        
        # Mock template matching result
        mock_result = np.array([[0.95, 0.8], [0.7, 0.6]])
        mock_match_template.return_value = mock_result
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.glob') as mock_glob:
                mock_glob.return_value = [Path('continue.png')]
                
                buttons = self.button_finder._find_buttons_template(
                    self.test_image, 0, 0
                )
                
                self.assertGreater(len(buttons), 0)
                self.assertTrue(
                    any(b.method.startswith('template') for b in buttons)
                )
                
    def test_find_buttons_color_detection(self):
        """Test color-based button detection."""
        with patch('cv2.cvtColor') as mock_cvt_color:
            with patch('cv2.inRange') as mock_in_range:
                with patch('cv2.findContours') as mock_find_contours:
                    # Mock HSV conversion
                    mock_cvt_color.return_value = np.zeros((100, 200, 3))
                    
                    # Mock color range detection
                    mock_in_range.return_value = np.zeros((100, 200))
                    
                    # Mock contour detection
                    mock_contour = np.array([[[50, 50]], [[150, 50]], 
                                           [[150, 80]], [[50, 80]]])
                    mock_find_contours.return_value = ([mock_contour], None)
                    
                    with patch('cv2.contourArea', return_value=2000):
                        with patch('cv2.boundingRect', return_value=(50, 50, 100, 30)):
                            buttons = self.button_finder._find_buttons_color(
                                self.test_image, 0, 0
                            )
                            
                            self.assertGreaterEqual(len(buttons), 0)
                            
    def test_deduplicate_buttons(self):
        """Test button deduplication functionality."""
        # Create overlapping buttons
        button1 = ButtonLocation(
            x=50, y=50, width=100, height=30,
            confidence=0.9, method='ocr', text='Continue'
        )
        button2 = ButtonLocation(
            x=55, y=52, width=95, height=28,
            confidence=0.8, method='template', text='Continue'
        )
        button3 = ButtonLocation(
            x=200, y=200, width=100, height=30,
            confidence=0.7, method='color', text='Continue'
        )
        
        buttons = [button1, button2, button3]
        deduplicated = self.button_finder._deduplicate_buttons(buttons)
        
        # Should keep the highest confidence button from overlapping pair
        # and the non-overlapping button
        self.assertEqual(len(deduplicated), 2)
        self.assertEqual(deduplicated[0].confidence, 0.9)  # Highest confidence
        
    def test_calculate_overlap(self):
        """Test overlap calculation between buttons."""
        button1 = ButtonLocation(
            x=50, y=50, width=100, height=30,
            confidence=0.9, method='ocr'
        )
        button2 = ButtonLocation(
            x=100, y=60, width=100, height=30,
            confidence=0.8, method='template'
        )
        
        overlap = self.button_finder._calculate_overlap(button1, button2)
        
        # These buttons should have some overlap
        self.assertGreater(overlap, 0)
        self.assertLess(overlap, 1)
        
    def test_find_continue_buttons_integration(self):
        """Test the main find_continue_buttons method integration."""
        with patch.object(self.button_finder, '_find_buttons_ocr') as mock_ocr:
            with patch.object(self.button_finder, '_find_buttons_template') as mock_template:
                with patch.object(self.button_finder, '_find_buttons_color') as mock_color:
                    # Mock each detection method
                    mock_ocr.return_value = [
                        ButtonLocation(50, 50, 100, 30, 0.9, 'ocr', 'Continue')
                    ]
                    mock_template.return_value = [
                        ButtonLocation(55, 52, 95, 28, 0.8, 'template', 'Continue')
                    ]
                    mock_color.return_value = [
                        ButtonLocation(200, 200, 100, 30, 0.7, 'color')
                    ]
                    
                    buttons = self.button_finder.find_continue_buttons(
                        self.test_image, 0, 0
                    )
                    
                    # Should find buttons and deduplicate
                    self.assertGreater(len(buttons), 0)
                    # Buttons should be sorted by confidence (highest first)
                    for i in range(len(buttons) - 1):
                        self.assertGreaterEqual(
                            buttons[i].confidence, buttons[i + 1].confidence
                        )


if __name__ == '__main__':
    unittest.main()
