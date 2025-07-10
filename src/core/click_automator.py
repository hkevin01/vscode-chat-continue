"""Mouse automation and click simulation."""

import logging
import time
import platform
from typing import Tuple, Optional
from dataclasses import dataclass

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

try:
    from pynput.mouse import Button, Listener as MouseListener
    from pynput.mouse import Controller as MouseController
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False

if platform.system() == "Linux":
    try:
        import Xlib.display
        import Xlib.X
        import Xlib.ext.xtest
        HAS_XLIB = True
    except ImportError:
        HAS_XLIB = False
elif platform.system() == "Windows":
    try:
        import win32api
        import win32con
        HAS_WIN32 = True
    except ImportError:
        HAS_WIN32 = False


@dataclass
class ClickResult:
    """Result of a click operation."""
    success: bool
    x: int
    y: int
    method: str
    error: Optional[str] = None


class ClickAutomator:
    """Handles mouse automation and clicking."""
    
    def __init__(self, click_delay: float = 0.1, move_duration: float = 0.2):
        """Initialize the click automator.
        
        Args:
            click_delay: Delay between mouse down and up (seconds)
            move_duration: Duration for mouse movement animations (seconds)
        """
        self.logger = logging.getLogger(__name__)
        self.click_delay = click_delay
        self.move_duration = move_duration
        self.platform = platform.system()
        
        # Store original mouse position for restoration
        self.original_position: Optional[Tuple[int, int]] = None
        
        self._check_dependencies()
        self._init_controllers()
    
    def _check_dependencies(self) -> None:
        """Check which click methods are available."""
        methods = []
        
        if HAS_PYAUTOGUI:
            methods.append("pyautogui")
        if HAS_PYNPUT:
            methods.append("pynput")
        if HAS_XLIB and self.platform == "Linux":
            methods.append("xlib")
        if HAS_WIN32 and self.platform == "Windows":
            methods.append("win32")
        
        if not methods:
            self.logger.warning("No click automation methods available!")
        else:
            self.logger.debug(f"Available click methods: {', '.join(methods)}")
    
    def _init_controllers(self) -> None:
        """Initialize mouse controllers."""
        self.mouse_controller = None
        
        if HAS_PYNPUT:
            try:
                self.mouse_controller = MouseController()
            except Exception as e:
                self.logger.debug(f"Failed to initialize pynput controller: {e}")
        
        # Configure pyautogui if available
        if HAS_PYAUTOGUI:
            try:
                # Disable pyautogui's fail-safe (moving mouse to corner)
                pyautogui.FAILSAFE = False
                # Set reasonable pause between actions
                pyautogui.PAUSE = 0.1
            except Exception as e:
                self.logger.debug(f"Failed to configure pyautogui: {e}")
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get the current mouse position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        try:
            if HAS_PYAUTOGUI:
                return pyautogui.position()
            elif self.mouse_controller:
                pos = self.mouse_controller.position
                return (int(pos[0]), int(pos[1]))
            else:
                return (0, 0)
        except Exception as e:
            self.logger.debug(f"Error getting mouse position: {e}")
            return (0, 0)
    
    def click(self, x: int, y: int, button: str = "left", 
              restore_position: bool = True) -> ClickResult:
        """Click at the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button to click ("left", "right", "middle")
            restore_position: Whether to restore mouse position after click
            
        Returns:
            ClickResult object with success status and details
        """
        # Store original position if requested
        if restore_position and self.original_position is None:
            self.original_position = self.get_mouse_position()
        
        try:
            # Try different click methods in order of preference
            methods = self._get_preferred_click_methods()
            
            for method in methods:
                result = self._click_with_method(x, y, button, method)
                if result.success:
                    self.logger.debug(f"Successfully clicked ({x}, {y}) using {method}")
                    
                    # Restore mouse position if requested
                    if restore_position and self.original_position:
                        self._restore_mouse_position()
                    
                    return result
            
            # If all methods failed
            error_msg = "All click methods failed"
            self.logger.error(error_msg)
            return ClickResult(
                success=False,
                x=x,
                y=y,
                method="none",
                error=error_msg
            )
            
        except Exception as e:
            error_msg = f"Click operation failed: {e}"
            self.logger.error(error_msg)
            return ClickResult(
                success=False,
                x=x,
                y=y,
                method="error",
                error=error_msg
            )
    
    def _get_preferred_click_methods(self) -> list:
        """Get click methods in order of preference for current platform.
        
        Returns:
            List of method names
        """
        if self.platform == "Linux":
            return ["pyautogui", "pynput", "xlib"]
        elif self.platform == "Windows":
            return ["pyautogui", "pynput", "win32"]
        elif self.platform == "Darwin":
            return ["pyautogui", "pynput"]
        else:
            return ["pyautogui", "pynput"]
    
    def _click_with_method(self, x: int, y: int, button: str, 
                          method: str) -> ClickResult:
        """Perform click using specific method.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button
            method: Click method to use
            
        Returns:
            ClickResult object
        """
        try:
            if method == "pyautogui" and HAS_PYAUTOGUI:
                return self._click_pyautogui(x, y, button)
            elif method == "pynput" and HAS_PYNPUT:
                return self._click_pynput(x, y, button)
            elif method == "xlib" and HAS_XLIB:
                return self._click_xlib(x, y, button)
            elif method == "win32" and HAS_WIN32:
                return self._click_win32(x, y, button)
            else:
                return ClickResult(
                    success=False,
                    x=x,
                    y=y,
                    method=method,
                    error=f"Method {method} not available"
                )
                
        except Exception as e:
            return ClickResult(
                success=False,
                x=x,
                y=y,
                method=method,
                error=str(e)
            )
    
    def _click_pyautogui(self, x: int, y: int, button: str) -> ClickResult:
        """Click using pyautogui."""
        pyautogui.click(x, y, button=button, duration=self.move_duration)
        return ClickResult(success=True, x=x, y=y, method="pyautogui")
    
    def _click_pynput(self, x: int, y: int, button: str) -> ClickResult:
        """Click using pynput."""
        if not self.mouse_controller:
            raise Exception("Mouse controller not initialized")
        
        # Map button names
        button_map = {
            "left": Button.left,
            "right": Button.right,
            "middle": Button.middle,
        }
        
        if button not in button_map:
            raise Exception(f"Unknown button: {button}")
        
        pynput_button = button_map[button]
        
        # Move to position
        self.mouse_controller.position = (x, y)
        time.sleep(self.move_duration)
        
        # Perform click
        self.mouse_controller.press(pynput_button)
        time.sleep(self.click_delay)
        self.mouse_controller.release(pynput_button)
        
        return ClickResult(success=True, x=x, y=y, method="pynput")
    
    def _click_xlib(self, x: int, y: int, button: str) -> ClickResult:
        """Click using X11 on Linux."""
        try:
            display = Xlib.display.Display()
            
            # Map button names to X11 button numbers
            button_map = {
                "left": 1,
                "right": 3,
                "middle": 2,
            }
            
            if button not in button_map:
                raise Exception(f"Unknown button: {button}")
            
            x11_button = button_map[button]
            
            # Move mouse
            display.warp_pointer(x, y)
            display.sync()
            time.sleep(self.move_duration)
            
            # Click
            Xlib.ext.xtest.fake_input(display, Xlib.X.ButtonPress, x11_button)
            display.sync()
            time.sleep(self.click_delay)
            
            Xlib.ext.xtest.fake_input(display, Xlib.X.ButtonRelease, x11_button)
            display.sync()
            
            return ClickResult(success=True, x=x, y=y, method="xlib")
            
        except Exception as e:
            raise Exception(f"X11 click failed: {e}")
    
    def _click_win32(self, x: int, y: int, button: str) -> ClickResult:
        """Click using Win32 API on Windows."""
        # Move mouse
        win32api.SetCursorPos((x, y))
        time.sleep(self.move_duration)
        
        # Map buttons to Win32 constants
        if button == "left":
            down_event = win32con.MOUSEEVENTF_LEFTDOWN
            up_event = win32con.MOUSEEVENTF_LEFTUP
        elif button == "right":
            down_event = win32con.MOUSEEVENTF_RIGHTDOWN
            up_event = win32con.MOUSEEVENTF_RIGHTUP
        elif button == "middle":
            down_event = win32con.MOUSEEVENTF_MIDDLEDOWN
            up_event = win32con.MOUSEEVENTF_MIDDLEUP
        else:
            raise Exception(f"Unknown button: {button}")
        
        # Perform click
        win32api.mouse_event(down_event, x, y, 0, 0)
        time.sleep(self.click_delay)
        win32api.mouse_event(up_event, x, y, 0, 0)
        
        return ClickResult(success=True, x=x, y=y, method="win32")
    
    def _restore_mouse_position(self) -> None:
        """Restore mouse to original position."""
        if self.original_position:
            try:
                if HAS_PYAUTOGUI:
                    pyautogui.moveTo(self.original_position[0], 
                                   self.original_position[1], 
                                   duration=self.move_duration)
                elif self.mouse_controller:
                    self.mouse_controller.position = self.original_position
                    
                self.original_position = None
                
            except Exception as e:
                self.logger.debug(f"Failed to restore mouse position: {e}")
    
    def double_click(self, x: int, y: int, button: str = "left", 
                    restore_position: bool = True) -> ClickResult:
        """Perform a double click.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button to click
            restore_position: Whether to restore mouse position after click
            
        Returns:
            ClickResult object
        """
        try:
            if HAS_PYAUTOGUI:
                if restore_position:
                    self.original_position = self.get_mouse_position()
                
                pyautogui.doubleClick(x, y, button=button, 
                                    duration=self.move_duration)
                
                if restore_position and self.original_position:
                    self._restore_mouse_position()
                
                return ClickResult(success=True, x=x, y=y, method="pyautogui_double")
            else:
                # Fallback: two single clicks
                result1 = self.click(x, y, button, restore_position=False)
                if result1.success:
                    time.sleep(0.1)
                    result2 = self.click(x, y, button, restore_position)
                    if result2.success:
                        return ClickResult(success=True, x=x, y=y, 
                                         method="double_single")
                
                return ClickResult(success=False, x=x, y=y, method="double_fallback",
                                 error="Double click failed")
                
        except Exception as e:
            return ClickResult(success=False, x=x, y=y, method="double_error",
                             error=str(e))
    
    def is_available(self) -> bool:
        """Check if click automation is available.
        
        Returns:
            True if at least one click method is available
        """
        return HAS_PYAUTOGUI or HAS_PYNPUT or HAS_XLIB or HAS_WIN32
