"""Window focus management for cross-platform automation."""

import logging
import platform
import time
from dataclasses import dataclass
from typing import Optional

from .window_detector import VSCodeWindow

# Platform-specific imports
HAS_XLIB = False
HAS_WIN32 = False
HAS_PYAUTOGUI = False

if platform.system() == "Linux":
    try:
        import subprocess

        import Xlib.display
        import Xlib.X

        HAS_XLIB = True
    except ImportError:
        HAS_XLIB = False
elif platform.system() == "Windows":
    try:
        import win32con
        import win32gui

        HAS_WIN32 = True
    except ImportError:
        HAS_WIN32 = False

try:
    import pyautogui

    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False


@dataclass
class FocusResult:
    """Result of a window focus operation."""

    success: bool
    method: str
    window_id: str
    error: Optional[str] = None


class WindowFocusManager:
    """Manages window focus for automation."""

    def __init__(self):
        """Initialize the window focus manager."""
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system()
        self._original_focus = None

        self._check_capabilities()

    def _check_capabilities(self) -> None:
        """Check what focus methods are available."""
        methods = []

        if self.platform == "Linux":
            if HAS_XLIB:
                methods.append("xlib")
            methods.append("wmctrl")  # Command-line tool
            methods.append("xdotool")  # Command-line tool
        elif self.platform == "Windows":
            if HAS_WIN32:
                methods.append("win32")

        if HAS_PYAUTOGUI:
            methods.append("pyautogui")

        self.logger.debug(f"Available focus methods: {', '.join(methods)}")

    def focus_window(self, window: VSCodeWindow, timeout: float = 2.0) -> FocusResult:
        """Bring a window into focus.

        Args:
            window: The VSCode window to focus
            timeout: Maximum time to wait for focus

        Returns:
            FocusResult indicating success/failure
        """
        # Store original focus for restoration
        if self._original_focus is None:
            self._original_focus = self._get_focused_window()

        # Try different focus methods in order of preference
        methods = self._get_available_focus_methods()

        for method in methods:
            try:
                self.logger.debug(f"Attempting to focus window using {method}")
                result = self._focus_with_method(window, method, timeout)

                if result.success:
                    self.logger.info(
                        f"Successfully focused window " f"'{window.title}' using {method}"
                    )
                    return result
                else:
                    self.logger.debug(f"Focus method {method} failed: " f"{result.error}")

            except Exception as e:
                self.logger.debug(f"Focus method {method} threw " f"exception: {e}")
                continue

        return FocusResult(
            success=False,
            method="none",
            window_id=window.window_id,
            error="All focus methods failed",
        )

    def _get_available_focus_methods(self) -> list:
        """Get list of available focus methods in order of preference."""
        if self.platform == "Linux":
            return ["xdotool", "wmctrl", "xlib", "pyautogui"]
        elif self.platform == "Windows":
            return ["win32", "pyautogui"]
        else:
            return ["pyautogui"]

    def _focus_with_method(self, window: VSCodeWindow, method: str, timeout: float) -> FocusResult:
        """Focus window using specific method."""
        if method == "xdotool":
            return self._focus_with_xdotool(window, timeout)
        elif method == "wmctrl":
            return self._focus_with_wmctrl(window, timeout)
        elif method == "xlib":
            return self._focus_with_xlib(window, timeout)
        elif method == "win32":
            return self._focus_with_win32(window, timeout)
        elif method == "pyautogui":
            return self._focus_with_pyautogui(window, timeout)
        else:
            return FocusResult(
                success=False,
                method=method,
                window_id=window.window_id,
                error=f"Unknown focus method: {method}",
            )

    def _focus_with_xdotool(self, window: VSCodeWindow, timeout: float) -> FocusResult:
        """Focus window using xdotool command."""
        try:
            # Convert hex window ID to decimal for xdotool
            window_id_decimal = int(window.window_id, 16)

            # Use xdotool to focus the window
            result = subprocess.run(
                ["xdotool", "windowactivate", str(window_id_decimal)],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                # Give window time to actually gain focus
                time.sleep(0.2)
                return FocusResult(success=True, method="xdotool", window_id=window.window_id)
            else:
                return FocusResult(
                    success=False,
                    method="xdotool",
                    window_id=window.window_id,
                    error=f"xdotool failed: {result.stderr}",
                )

        except subprocess.TimeoutExpired:
            return FocusResult(
                success=False,
                method="xdotool",
                window_id=window.window_id,
                error="xdotool command timed out",
            )
        except Exception as e:
            return FocusResult(
                success=False,
                method="xdotool",
                window_id=window.window_id,
                error=f"xdotool error: {e}",
            )

    def _focus_with_wmctrl(self, window: VSCodeWindow, timeout: float) -> FocusResult:
        """Focus window using wmctrl command."""
        try:
            # Use wmctrl to activate the window
            result = subprocess.run(
                ["wmctrl", "-i", "-a", window.window_id],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                time.sleep(0.2)
                return FocusResult(success=True, method="wmctrl", window_id=window.window_id)
            else:
                return FocusResult(
                    success=False,
                    method="wmctrl",
                    window_id=window.window_id,
                    error=f"wmctrl failed: {result.stderr}",
                )

        except subprocess.TimeoutExpired:
            return FocusResult(
                success=False,
                method="wmctrl",
                window_id=window.window_id,
                error="wmctrl command timed out",
            )
        except Exception as e:
            return FocusResult(
                success=False,
                method="wmctrl",
                window_id=window.window_id,
                error=f"wmctrl error: {e}",
            )

    def _focus_with_xlib(self, window: VSCodeWindow, timeout: float) -> FocusResult:
        """Focus window using Xlib."""
        if not HAS_XLIB:
            return FocusResult(
                success=False,
                method="xlib",
                window_id=window.window_id,
                error="Xlib not available",
            )

        try:
            display = Xlib.display.Display()
            window_id_int = int(window.window_id, 16)

            # Get the window object
            win = display.create_resource_object("window", window_id_int)

            # Raise and focus the window
            win.raise_window()
            win.set_input_focus(Xlib.X.RevertToParent, Xlib.X.CurrentTime)

            display.sync()
            time.sleep(0.2)

            return FocusResult(success=True, method="xlib", window_id=window.window_id)

        except Exception as e:
            return FocusResult(
                success=False,
                method="xlib",
                window_id=window.window_id,
                error=f"Xlib error: {e}",
            )

    def _focus_with_win32(self, window: VSCodeWindow, timeout: float) -> FocusResult:
        """Focus window using Win32 API."""
        if not HAS_WIN32:
            return FocusResult(
                success=False,
                method="win32",
                window_id=window.window_id,
                error="Win32 API not available",
            )

        try:
            hwnd = int(window.window_id)

            # Bring window to foreground
            win32gui.SetForegroundWindow(hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            time.sleep(0.2)

            return FocusResult(success=True, method="win32", window_id=window.window_id)

        except Exception as e:
            return FocusResult(
                success=False,
                method="win32",
                window_id=window.window_id,
                error=f"Win32 error: {e}",
            )

    def _focus_with_pyautogui(self, window: VSCodeWindow, timeout: float) -> FocusResult:
        """Focus window using pyautogui (click to focus)."""
        if not HAS_PYAUTOGUI:
            return FocusResult(
                success=False,
                method="pyautogui",
                window_id=window.window_id,
                error="pyautogui not available",
            )

        try:
            # Click on the window to bring it to focus
            # Use the center of the window
            center_x = window.x + window.width // 2
            center_y = window.y + window.height // 2

            # Store current mouse position
            original_pos = pyautogui.position()

            # Click on window to focus it
            pyautogui.click(center_x, center_y)
            time.sleep(0.2)

            # Restore mouse position
            pyautogui.moveTo(original_pos[0], original_pos[1])

            return FocusResult(success=True, method="pyautogui", window_id=window.window_id)

        except Exception as e:
            return FocusResult(
                success=False,
                method="pyautogui",
                window_id=window.window_id,
                error=f"pyautogui error: {e}",
            )

    def _get_focused_window(self) -> Optional[str]:
        """Get the currently focused window ID."""
        try:
            if self.platform == "Linux":
                # Try xdotool first
                try:
                    result = subprocess.run(
                        ["xdotool", "getactivewindow"],
                        capture_output=True,
                        text=True,
                        timeout=1,
                    )
                    if result.returncode == 0:
                        return hex(int(result.stdout.strip()))
                except Exception:
                    pass

                # Try with Xlib
                if HAS_XLIB:
                    try:
                        display = Xlib.display.Display()
                        window = display.get_input_focus().focus
                        return hex(window.id)
                    except Exception:
                        pass

            elif self.platform == "Windows" and HAS_WIN32:
                try:
                    hwnd = win32gui.GetForegroundWindow()
                    return str(hwnd)
                except Exception:
                    pass

        except Exception as e:
            self.logger.debug(f"Error getting focused window: {e}")

        return None

    def restore_original_focus(self) -> bool:
        """Restore focus to the originally focused window.

        Returns:
            True if successful, False otherwise
        """
        if self._original_focus is None:
            return True  # Nothing to restore

        try:
            # Implementation depends on platform and available tools
            # For now, we'll just reset the stored focus
            self._original_focus = None
            return True

        except Exception as e:
            self.logger.debug(f"Error restoring focus: {e}")
            return False

    def cycle_vscode_windows(self, windows: list, max_attempts: int = 3) -> Optional[VSCodeWindow]:
        """Cycle through VS Code windows to find one that can be focused.

        Args:
            windows: List of VSCode windows to cycle through
            max_attempts: Maximum number of focus attempts per window

        Returns:
            The successfully focused window, or None
        """
        for window in windows:
            self.logger.debug(f"Attempting to focus window: {window.title}")

            for attempt in range(max_attempts):
                result = self.focus_window(window, timeout=1.0)

                if result.success:
                    self.logger.info(f"Successfully focused window: {window.title}")
                    return window
                else:
                    self.logger.debug(f"Focus attempt {attempt + 1} failed for {window.title}")
                    time.sleep(0.5)  # Brief pause between attempts

        self.logger.warning("Failed to focus any VS Code windows")
        return None
