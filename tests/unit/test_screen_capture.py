"""Unit tests for ScreenCapture module."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.screen_capture import ScreenCapture


class TestScreenCapture(unittest.TestCase):
    """Test cases for ScreenCapture class."""
    
    def setUp(self):
        """Set up test environment."""
        self.screen_capture = ScreenCapture()
        self.test_image = Image.new('RGB', (100, 100), color='red')
        
    def test_screen_capture_initialization(self):
        """Test ScreenCapture initialization."""
        self.assertIsNotNone(self.screen_capture)
        
    @patch('platform.system', return_value='Linux')
    @patch('subprocess.run')
    @patch('PIL.Image.open')
    @patch('pathlib.Path.unlink')
    def test_capture_screen_scrot_success(
        self, mock_unlink, mock_image_open, mock_run, mock_platform
    ):
        """Test screen capture using scrot successfully."""
        # Mock scrot success
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # Mock image loading
        mock_image_open.return_value = self.test_image
        
        result = self.screen_capture.capture_screen()
        
        self.assertIsNotNone(result)
        self.assertEqual(result.size, (100, 100))
        mock_run.assert_called_once()
        mock_unlink.assert_called_once()
        
    @patch('platform.system', return_value='Linux')
    @patch('subprocess.run')
    def test_capture_screen_scrot_failure(self, mock_run, mock_platform):
        """Test screen capture when scrot fails."""
        # Mock scrot failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        with patch('PIL.ImageGrab.grab') as mock_pil_grab:
            mock_pil_grab.return_value = self.test_image
            
            result = self.screen_capture.capture_screen()
            
            self.assertIsNotNone(result)
            mock_pil_grab.assert_called_once()
            
    @patch('PIL.ImageGrab.grab')
    def test_capture_screen_pil_fallback(self, mock_pil_grab):
        """Test screen capture using PIL fallback."""
        mock_pil_grab.return_value = self.test_image
        
        result = self.screen_capture.capture_screen()
        
        self.assertIsNotNone(result)
        self.assertEqual(result.size, (100, 100))
        
    @patch('pyautogui.screenshot')
    def test_capture_screen_pyautogui_fallback(self, mock_pyautogui):
        """Test screen capture using pyautogui fallback."""
        # Mock PIL failure
        with patch('PIL.ImageGrab.grab', side_effect=Exception("PIL failed")):
            mock_pyautogui.return_value = self.test_image
            
            result = self.screen_capture.capture_screen()
            
            self.assertIsNotNone(result)
            mock_pyautogui.assert_called_once()
            
    @patch('platform.system', return_value='Linux')
    @patch('subprocess.run')
    @patch('PIL.Image.open')
    @patch('pathlib.Path.unlink')
    def test_capture_region_scrot_success(
        self, mock_unlink, mock_image_open, mock_run, mock_platform
    ):
        """Test region capture using scrot successfully."""
        # Mock scrot success
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # Mock image loading
        mock_image_open.return_value = self.test_image
        
        result = self.screen_capture.capture_region(10, 20, 100, 50)
        
        self.assertIsNotNone(result)
        mock_run.assert_called_once()
        # Check scrot was called with correct region parameters
        call_args = mock_run.call_args[0][0]
        self.assertIn('-a', call_args)
        self.assertIn('10,20,100,50', call_args)
        
    @patch('PIL.ImageGrab.grab')
    def test_capture_region_pil_fallback(self, mock_pil_grab):
        """Test region capture using PIL fallback."""
        mock_pil_grab.return_value = self.test_image
        
        result = self.screen_capture.capture_region(10, 20, 100, 50)
        
        self.assertIsNotNone(result)
        # Check PIL was called with correct bbox
        mock_pil_grab.assert_called_with(bbox=(10, 20, 110, 70))
        
    @patch('pyautogui.screenshot')
    def test_capture_region_pyautogui_fallback(self, mock_pyautogui):
        """Test region capture using pyautogui fallback."""
        mock_pyautogui.return_value = self.test_image
        
        result = self.screen_capture.capture_region(10, 20, 100, 50)
        
        self.assertIsNotNone(result)
        # Check pyautogui was called with correct region
        mock_pyautogui.assert_called_with(region=(10, 20, 100, 50))
        
    def test_capture_window(self):
        """Test window capture (delegates to region capture)."""
        with patch.object(
            self.screen_capture, 'capture_region'
        ) as mock_capture_region:
            mock_capture_region.return_value = self.test_image
            
            result = self.screen_capture.capture_window(
                123, 10, 20, 800, 600
            )
            
            self.assertIsNotNone(result)
            mock_capture_region.assert_called_once_with(10, 20, 800, 600)
            
    def test_save_image_success(self):
        """Test saving image successfully."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            filepath = Path(f.name)
            
        try:
            result = self.screen_capture.save_image(self.test_image, filepath)
            
            self.assertTrue(result)
            self.assertTrue(filepath.exists())
            
            # Verify the image was saved correctly
            saved_image = Image.open(filepath)
            self.assertEqual(saved_image.size, self.test_image.size)
            
        finally:
            filepath.unlink(missing_ok=True)
            
    def test_save_image_directory_creation(self):
        """Test that save_image creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a nested path that doesn't exist
            filepath = Path(temp_dir) / "subdir" / "test.png"
            
            result = self.screen_capture.save_image(self.test_image, filepath)
            
            self.assertTrue(result)
            self.assertTrue(filepath.exists())
            self.assertTrue(filepath.parent.exists())
            
    def test_save_image_failure(self):
        """Test save_image handling failure."""
        # Try to save to an invalid path
        invalid_path = Path("/invalid/path/test.png")
        
        result = self.screen_capture.save_image(self.test_image, invalid_path)
        
        self.assertFalse(result)
        
    def test_image_to_bytes_success(self):
        """Test converting image to bytes successfully."""
        result = self.screen_capture.image_to_bytes(self.test_image)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, bytes)
        
        # Verify we can load the image back from bytes
        import io
        image_from_bytes = Image.open(io.BytesIO(result))
        self.assertEqual(image_from_bytes.size, self.test_image.size)
        
    def test_image_to_bytes_different_formats(self):
        """Test converting image to different formats."""
        formats = ['PNG', 'JPEG', 'BMP']
        
        for fmt in formats:
            with self.subTest(format=fmt):
                result = self.screen_capture.image_to_bytes(
                    self.test_image, fmt
                )
                
                self.assertIsNotNone(result)
                self.assertIsInstance(result, bytes)
                
    def test_image_to_bytes_failure(self):
        """Test image_to_bytes handling failure."""
        # Mock PIL Image.save to raise an exception
        with patch.object(self.test_image, 'save', side_effect=Exception("Save failed")):
            result = self.screen_capture.image_to_bytes(self.test_image)
            
            self.assertIsNone(result)
            
    @patch('platform.system', return_value='Windows')
    def test_platform_detection_windows(self, mock_platform):
        """Test platform detection for Windows."""
        screen_capture = ScreenCapture()
        self.assertEqual(screen_capture.platform, 'Windows')
        
    @patch('platform.system', return_value='Darwin')
    def test_platform_detection_macos(self, mock_platform):
        """Test platform detection for macOS."""
        screen_capture = ScreenCapture()
        self.assertEqual(screen_capture.platform, 'Darwin')
        
    def test_dependency_checking(self):
        """Test that dependency checking works correctly."""
        # This is mainly to ensure the _check_dependencies method runs
        # without errors during initialization
        screen_capture = ScreenCapture()
        self.assertIsNotNone(screen_capture)


if __name__ == '__main__':
    unittest.main()
