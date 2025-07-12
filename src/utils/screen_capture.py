"""Screen capture utilities for window and region screenshots."""

import io
import logging
import os
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

    # COMPLETELY disable pyautogui on Linux to prevent gnome-screenshot conflicts
    if platform.system() == "Linux":
        HAS_PYAUTOGUI = False
        pyautogui = None
        # Don't even test pyautogui on Linux - any call could trigger gnome-screenshot
    else:
        # On Windows/macOS, pyautogui should be safe
        HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

# Completely disable pyscreenshot on Linux to avoid gnome-screenshot snap conflicts
HAS_PYSCREENSHOT = False


class ScreenCapture:
    """Screen capture utility for taking screenshots of windows and regions."""
    
    def __init__(self):
        """Initialize the screen capture utility."""
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system()
        
        # Aggressively prevent gnome-screenshot on Linux
        if self.platform == "Linux":
            self._disable_gnome_screenshot()
        
        # Check available libraries
        self._check_dependencies()
    
    def _disable_gnome_screenshot(self) -> None:
        """Aggressively disable gnome-screenshot on Linux to prevent snap conflicts."""
        import os

        # Set environment variables to prevent gnome-screenshot usage
        os.environ['PYSCREENSHOT_BACKEND'] = 'pil'
        os.environ['GNOME_SCREENSHOT_DISABLE'] = '1'
        os.environ['NO_GNOME_SCREENSHOT'] = '1'
        
        # Try to prevent any screenshot tools that might trigger gnome-screenshot
        os.environ['SCROT_DISABLE_GNOME'] = '1'
        
        # Disable any GTK/GNOME screenshot services
        for env_var in ['GNOME_SCREENSHOT_DIR', 'SCREENSHOT_TOOL']:
            if env_var in os.environ:
                del os.environ[env_var]
    
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
            # Linux-specific capture logic
            if self.platform == "Linux":
                # Method 1: ImageMagick 'import' command
                try:
                    with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
                        cmd = ['import', '-window', 'root', tmp.name]
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            self.logger.debug("Screen captured successfully with ImageMagick.")
                            return Image.open(tmp.name)
                        else:
                            self.logger.debug(f"ImageMagick 'import' failed: {result.stderr.strip()}")
                except FileNotFoundError:
                    self.logger.debug("ImageMagick 'import' command not found, trying next method.")
                except Exception as e:
                    self.logger.debug(f"ImageMagick capture failed: {e}")

                # Method 2: scrot
                try:
                    tmp_dir = Path(tempfile.gettempdir())
                    # Create a unique filename to avoid conflicts
                    tmp_path = tmp_dir / f"screenshot_{os.getpid()}_{id(self)}.png"

                    try:
                        cmd = ['scrot', '--silent', str(tmp_path)]
                        env = dict(os.environ)
                        env.update({
                            'DISPLAY': env.get('DISPLAY', ':0'),
                            'GNOME_SCREENSHOT_DISABLE': '1',
                            'NO_GNOME_SCREENSHOT': '1'
                        })
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, env=env)

                        if result.returncode == 0 and tmp_path.exists() and tmp_path.stat().st_size > 0:
                            self.logger.debug("Screen captured successfully with scrot.")
                            image = Image.open(tmp_path)
                            return image
                        else:
                            err_msg = result.stderr.strip() if result.stderr else "No stderr."
                            filesize = tmp_path.stat().st_size if tmp_path.exists() else "File does not exist."
                            self.logger.debug(f"scrot failed. Code: {result.returncode}, Error: {err_msg}, Filesize: {filesize}")
                    finally:
                        # Ensure the temporary file is always cleaned up
                        if tmp_path.exists():
                            tmp_path.unlink()
                
                except FileNotFoundError:
                    self.logger.debug("scrot command not found.")
                except Exception as e:
                    self.logger.debug(f"scrot capture failed: {e}")
                
                self.logger.error("All Linux-native screen capture methods failed. PIL.ImageGrab will not be attempted.")
                return None

            # For Windows/macOS, prefer PIL ImageGrab
            if HAS_PIL:
                try:
                    return ImageGrab.grab()
                except Exception as e:
                    self.logger.debug(f"PIL fullscreen failed: {e}")
                    
            # Fallback to pyautogui on non-Linux platforms
            if HAS_PYAUTOGUI and self.platform != "Linux" and pyautogui is not None:
                try:
                    return pyautogui.screenshot()
                except Exception as e:
                    self.logger.debug(f"pyautogui fullscreen failed: {e}")
            
            self.logger.error("No screen capture method available for this platform.")
            return None
                
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during screen capture: {e}")
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
            # Validate input parameters
            if width <= 0 or height <= 0:
                self.logger.error(f"Invalid region dimensions: {width}x{height}")
                return None
                
            bbox = (x, y, x + width, y + height)
            
            # Linux-specific capture logic
            if self.platform == "Linux":
                # Try direct region capture methods first
                imagemagick_result = self._capture_with_imagemagick(x, y, width, height)
                if imagemagick_result and self._validate_screenshot(imagemagick_result, width//2, height//2):
                    return imagemagick_result
                
                scrot_result = self._capture_with_scrot(x, y, width, height)
                if scrot_result and self._validate_screenshot(scrot_result, width//2, height//2):
                    return scrot_result
                
                # Fallback for Linux: capture full screen and crop
                self.logger.debug("Linux-native region capture failed. Attempting to crop a full screenshot.")
                full_screen = self.capture_screen()
                if full_screen and self._validate_screenshot(full_screen):
                    cropped = full_screen.crop(bbox)
                    if self._validate_screenshot(cropped, width//2, height//2):
                        return cropped
                
                self.logger.error("All region capture methods for Linux failed.")
                return None

            # For Windows/macOS, prefer PIL ImageGrab for region capture
            if HAS_PIL:
                try:
                    result = ImageGrab.grab(bbox=bbox)
                    if self._validate_screenshot(result, width//2, height//2):
                        return result
                except Exception as e:
                    self.logger.debug(f"PIL capture failed: {e}")
            
            # Fallback to pyautogui on non-Linux platforms
            if HAS_PYAUTOGUI and self.platform != "Linux" and pyautogui is not None:
                try:
                    return pyautogui.screenshot(region=(x, y, width, height))
                except Exception as e:
                    self.logger.debug(f"pyautogui capture failed: {e}")
            
            # Last resort for non-Linux: capture full screen and crop
            self.logger.debug("Trying to capture full screen and crop as a last resort.")
            full_screen = self.capture_screen()
            if full_screen:
                return full_screen.crop(bbox)
            
            return None
                
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during region capture {bbox}: {e}")
            return None
    
    def _capture_with_scrot(self, x: int, y: int, width: int,
                            height: int) -> Optional[Image.Image]:
        """Use scrot to capture a region (Linux fallback)."""
        try:
            with tempfile.NamedTemporaryFile(suffix='.png',
                                             delete=False) as tmp:
                # Use scrot with specific options to avoid triggering GNOME services
                cmd = [
                    'scrot',
                    '-a', f'{x},{y},{width},{height}',
                    '--overwrite',  # Prevent any dialog prompts
                    '--silent',     # Suppress any output that might trigger GNOME
                    tmp.name
                ]
                
                # Set environment to prevent any GNOME integration
                env = dict(os.environ)
                env.update({
                    'DISPLAY': env.get('DISPLAY', ':0'),
                    'GNOME_SCREENSHOT_DISABLE': '1',
                    'NO_GNOME_SCREENSHOT': '1'
                })
                
                result = subprocess.run(cmd, capture_output=True, timeout=10,
                                      env=env)
                
                if result.returncode == 0:
                    image = Image.open(tmp.name)
                    # Clean up temp file
                    Path(tmp.name).unlink(missing_ok=True)
                    return image
                else:
                    self.logger.debug(f"scrot failed with code {result.returncode}, stderr: {result.stderr.decode()}")
                    Path(tmp.name).unlink(missing_ok=True)
                    return None
                    
        except Exception as e:
            self.logger.debug(f"scrot capture error: {e}")
            return None
    
    def _capture_with_imagemagick(self, x: int, y: int, width: int,
                                  height: int) -> Optional[Image.Image]:
        """Use ImageMagick import to capture a region (avoids gnome-screenshot issues)."""
        try:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                # Use ImageMagick import command with crop geometry
                cmd = [
                    'import',
                    '-window', 'root',
                    '-crop', f'{width}x{height}+{x}+{y}',
                    tmp.name
                ]
                
                # Set environment to prevent any GNOME integration
                env = dict(os.environ)
                env.update({
                    'DISPLAY': env.get('DISPLAY', ':0'),
                    'GNOME_SCREENSHOT_DISABLE': '1',
                    'NO_GNOME_SCREENSHOT': '1'
                })
                
                result = subprocess.run(cmd, capture_output=True, timeout=10,
                                      env=env)
                
                if result.returncode == 0:
                    image = Image.open(tmp.name)
                    Path(tmp.name).unlink(missing_ok=True)
                    return image
                else:
                    self.logger.debug(f"ImageMagick import failed with code {result.returncode}, stderr: {result.stderr.decode()}")
                    Path(tmp.name).unlink(missing_ok=True)
                    return None
                    
        except Exception as e:
            self.logger.debug(f"ImageMagick capture error: {e}")
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
            # On Linux, use xrandr to avoid pyautogui/gnome-screenshot conflicts
            if self.platform == "Linux":
                try:
                    result = subprocess.run(['xrandr'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if ' connected primary ' in line or ' connected ' in line:
                                # Parse resolution like "1920x1080+0+0"
                                parts = line.split()
                                for part in parts:
                                    if 'x' in part and '+' in part:
                                        resolution = part.split('+')[0]
                                        width, height = map(int, resolution.split('x'))
                                        return (width, height)
                except Exception as e:
                    self.logger.debug(f"xrandr failed: {e}")
            
            # Fallback: try pyautogui if available (Windows/macOS)
            if HAS_PYAUTOGUI and self.platform != "Linux" and pyautogui is not None:
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
    
    def _validate_screenshot(self, screenshot: Optional[Image.Image], min_width: int = 100, min_height: int = 100) -> bool:
        """Validate that a screenshot is reasonable size and not corrupted.
        
        Args:
            screenshot: PIL Image to validate
            min_width: Minimum acceptable width
            min_height: Minimum acceptable height
            
        Returns:
            True if screenshot is valid, False otherwise
        """
        if not screenshot:
            return False
            
        width, height = screenshot.size
        
        # Check for suspiciously small screenshots (like the 16x13 issue)
        if width < min_width or height < min_height:
            self.logger.warning(f"Screenshot too small: {width}x{height} (min: {min_width}x{min_height})")
            return False
            
        # Check for blank or corrupt images
        try:
            # Test if we can access pixel data
            screenshot.getpixel((0, 0))
            return True
        except Exception as e:
            self.logger.warning(f"Screenshot validation failed: {e}")
            return False
