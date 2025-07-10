"""Screen capture utilities for window and region screenshots."""

import io
import logging
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Union

try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    from PIL import Image, ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

if platform.system() == "Linux":
    try:
        import pyscreenshot as ImageGrab_alt
        HAS_PYSCREENSHOT = True
    except ImportError:
        HAS_PYSCREENSHOT = False


class ScreenCapture:
    """Screen capture utility for taking screenshots of windows and regions."""
    
    def __init__(self):
        """Initialize the screen capture utility."""
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system()
        
        # Check available libraries
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """Check which screen capture libraries are available."""
        available = []
        
        if HAS_PIL:
            available.append("PIL")
        if HAS_PYAUTOGUI:
            available.append("pyautogui")
        if HAS_PYSCREENSHOT:
            available.append("pyscreenshot")
        if HAS_OPENCV:
            available.append("opencv")
        
        if not available:
            self.logger.warning("No screen capture libraries available!")
        else:
            self.logger.debug(f"Available capture methods: {', '.join(available)}")
    
    def capture_screen(self) -> Optional[Image.Image]:
        """Capture the entire screen.
        
        Returns:
            PIL Image object or None if capture failed
        """
        try:
            # For Linux, prefer scrot due to snap conflicts  
            if self.platform == "Linux":
                try:
                    result = subprocess.run(['scrot', '/tmp/fullscreen.png'], 
                                          capture_output=True, timeout=10)
                    if result.returncode == 0:
                        image = Image.open('/tmp/fullscreen.png')
                        Path('/tmp/fullscreen.png').unlink(missing_ok=True)
                        return image
                except Exception as e:
                    self.logger.debug(f"scrot fullscreen failed: {e}")
            
            if HAS_PIL:
                try:
                    return ImageGrab.grab()
                except Exception as e:
                    self.logger.debug(f"PIL fullscreen failed: {e}")
                    
            elif HAS_PYAUTOGUI:
                try:
                    screenshot = pyautogui.screenshot()
                    return screenshot
                except Exception as e:
                    self.logger.debug(f"pyautogui fullscreen failed: {e}")
                    
            elif HAS_PYSCREENSHOT and self.platform == "Linux":
                try:
                    # Force pyscreenshot to use a specific backend that doesn't conflict
                    import pyscreenshot as ImageGrab_alt

                    # Try to use PIL backend first to avoid gnome-screenshot
                    return ImageGrab_alt.grab(backend='pil')
                except Exception as e:
                    self.logger.debug(f"pyscreenshot with PIL backend failed: {e}")
                    try:
                        # Fallback to imagemagick if available
                        return ImageGrab_alt.grab(backend='imagemagick')
                    except Exception as e2:
                        self.logger.debug(f"pyscreenshot with imagemagick backend failed: {e2}")
                    return ImageGrab_alt.grab()
                except Exception as e:
                    self.logger.debug(f"pyscreenshot fullscreen failed: {e}")
            else:
                self.logger.error("No screen capture method available")
                return None
                
        except Exception as e:
            self.logger.error(f"Error capturing screen: {e}")
            return None

    def capture_region(self, x: int, y: int, width: int,
                       height: int) -> Optional[Image.Image]:
        """Capture a specific region of the screen.
        
        Args:
            x: Left coordinate
            y: Top coordinate
            width: Width of region
            height: Height of region
            
        Returns:
            PIL Image object or None if capture failed
        """
        try:
            bbox = (x, y, x + width, y + height)
            
            # For Linux, prefer scrot due to snap conflicts with gnome-screenshot
            if self.platform == "Linux":
                scrot_result = self._capture_with_scrot(x, y, width, height)
                if scrot_result:
                    return scrot_result
            
            # Try other capture methods as backup
            if HAS_PIL:
                try:
                    return ImageGrab.grab(bbox=bbox)
                except Exception as e:
                    self.logger.debug(f"PIL capture failed: {e}")
            
            if HAS_PYAUTOGUI:
                try:
                    return pyautogui.screenshot(region=(x, y, width, height))
                except Exception as e:
                    self.logger.debug(
                        f"pyautogui capture failed: {e}")
            
            if HAS_PYSCREENSHOT and self.platform == "Linux":
                try:
                    # Force pyscreenshot to avoid gnome-screenshot backend
                    import pyscreenshot as ImageGrab_alt
                    return ImageGrab_alt.grab(bbox=bbox, backend='pil')
                except Exception as e:
                    self.logger.debug(f"pyscreenshot region capture failed: {e}")
                    try:
                        return ImageGrab_alt.grab(bbox=bbox, backend='imagemagick')
                    except Exception as e2:
                        self.logger.debug(f"pyscreenshot imagemagick failed: {e2}")
                except Exception as e:
                    self.logger.debug(f"pyscreenshot failed: {e}")
            
            # Last resort: capture full screen and crop
            full_screen = self.capture_screen()
            if full_screen:
                return full_screen.crop(bbox)
            return None
                
        except Exception as e:
            self.logger.error(f"Error capturing region {bbox}: {e}")
            return None
    
    def _capture_with_scrot(self, x: int, y: int, width: int,
                            height: int) -> Optional[Image.Image]:
        """Use scrot to capture a region (Linux fallback)."""
        try:
            with tempfile.NamedTemporaryFile(suffix='.png',
                                             delete=False) as tmp:
                cmd = [
                    'scrot',
                    '-a', f'{x},{y},{width},{height}',
                    tmp.name
                ]
                result = subprocess.run(cmd, capture_output=True, timeout=10)
                
                if result.returncode == 0:
                    image = Image.open(tmp.name)
                    # Clean up temp file
                    Path(tmp.name).unlink(missing_ok=True)
                    return image
                else:
                    self.logger.debug(f"scrot failed: {result.stderr}")
                    Path(tmp.name).unlink(missing_ok=True)
                    return None
                    
        except Exception as e:
            self.logger.debug(f"scrot capture error: {e}")
            return None

    def capture_window(self, window_id: int, x: int, y: int, width: int,
                       height: int) -> Optional[Image.Image]:
        """Capture a specific window.
        
        Args:
            window_id: Window identifier
            x: Window x coordinate
            y: Window y coordinate
            width: Window width
            height: Window height
            
        Returns:
            PIL Image object or None if capture failed
        """
        # For most cases, we'll use region capture since window-specific
        # capture requires platform-specific implementations
        return self.capture_region(x, y, width, height)
    
    def save_image(self, image: Image.Image, filepath: Union[str, Path]) -> bool:
        """Save an image to file.
        
        Args:
            image: PIL Image object
            filepath: Path to save the image
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            image.save(filepath)
            self.logger.debug(f"Saved screenshot to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving image to {filepath}: {e}")
            return False
    
    def image_to_numpy(self, image: Image.Image) -> Optional[np.ndarray]:
        """Convert PIL Image to numpy array for OpenCV processing.
        
        Args:
            image: PIL Image object
            
        Returns:
            Numpy array or None if conversion failed
        """
        if not HAS_OPENCV:
            self.logger.warning("OpenCV not available for image conversion")
            return None
        
        try:
            # Convert PIL to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array and change from RGB to BGR for OpenCV
            numpy_image = np.array(image)
            opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
            return opencv_image
            
        except Exception as e:
            self.logger.error(f"Error converting image to numpy: {e}")
            return None
    
    def numpy_to_image(self, numpy_array: np.ndarray) -> Optional[Image.Image]:
        """Convert numpy array to PIL Image.
        
        Args:
            numpy_array: OpenCV/numpy image array
            
        Returns:
            PIL Image object or None if conversion failed
        """
        if not HAS_PIL:
            self.logger.warning("PIL not available for image conversion")
            return None
        
        try:
            # Convert from BGR to RGB
            if len(numpy_array.shape) == 3:
                rgb_array = cv2.cvtColor(numpy_array, cv2.COLOR_BGR2RGB)
            else:
                rgb_array = numpy_array
            
            return Image.fromarray(rgb_array)
            
        except Exception as e:
            self.logger.error(f"Error converting numpy to image: {e}")
            return None
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get the screen size.
        
        Returns:
            Tuple of (width, height)
        """
        try:
            if HAS_PYAUTOGUI:
                return pyautogui.size()
            elif HAS_PIL:
                # Capture screen and get size
                screen = self.capture_screen()
                if screen:
                    return screen.size
            
            # Fallback default
            return (1920, 1080)
            
        except Exception as e:
            self.logger.error(f"Error getting screen size: {e}")
            return (1920, 1080)
    
    def image_to_bytes(self, image: Image.Image, format: str = 'PNG') -> Optional[bytes]:
        """Convert PIL Image to bytes.
        
        Args:
            image: PIL Image object
            format: Image format (PNG, JPEG, etc.)
            
        Returns:
            Image bytes or None if conversion failed
        """
        try:
            img_buffer = io.BytesIO()
            image.save(img_buffer, format=format)
            return img_buffer.getvalue()
        except Exception as e:
            self.logger.error(f"Error converting image to bytes: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if screen capture is available.
        
        Returns:
            True if at least one capture method is available
        """
        return HAS_PIL or HAS_PYAUTOGUI or HAS_PYSCREENSHOT
