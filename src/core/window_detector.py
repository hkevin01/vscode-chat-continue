"""Window detection module for finding VS Code windows."""

import logging
import platform
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import psutil

if platform.system() == "Linux":
    try:
        import Xlib
        import Xlib.display
        from ewmh import EWMH
        HAS_X11 = True
    except ImportError:
        HAS_X11 = False
elif platform.system() == "Windows":
    try:
        import win32gui
        import win32process
        HAS_WIN32 = True
    except ImportError:
        HAS_WIN32 = False
elif platform.system() == "Darwin":
    try:
        import AppKit
        from AppKit import NSWorkspace
        HAS_MACOS = True
    except ImportError:
        HAS_MACOS = False


@dataclass
class VSCodeWindow:
    """Represents a VS Code window."""
    window_id: int
    title: str
    pid: int
    x: int
    y: int
    width: int
    height: int
    is_focused: bool = False
    
    def __str__(self) -> str:
        return f"VSCodeWindow(id={self.window_id}, title='{self.title}', pid={self.pid})"


class WindowDetector:
    """Detects VS Code windows across different platforms."""
    
    def __init__(self):
        """Initialize the window detector."""
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system()
        
        # Initialize platform-specific components
        if self.platform == "Linux" and HAS_X11:
            try:
                self.display = Xlib.display.Display()
                self.ewmh = EWMH()
            except Exception as e:
                self.logger.warning(f"Failed to initialize X11: {e}")
                self.display = None
                self.ewmh = None
        
    def get_vscode_processes(self) -> List[psutil.Process]:
        """Get all running VS Code processes.
        
        Returns:
            List of psutil.Process objects for VS Code instances
        """
        vscode_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    proc_info = proc.info
                    name = proc_info.get('name', '').lower()
                    exe = proc_info.get('exe', '').lower()
                    
                    # Check for VS Code process names
                    if any(vscode_name in name for vscode_name in [
                        'code', 'vscode', 'code-oss', 'codium', 'cursor'
                    ]) or any(vscode_name in exe for vscode_name in [
                        'code', 'vscode', 'code-oss', 'codium', 'cursor'
                    ]):
                        # Exclude helper processes
                        cmdline = proc_info.get('cmdline', [])
                        if cmdline and not any(helper in ' '.join(cmdline).lower() for helper in [
                            '--type=gpu-process',
                            '--type=renderer',
                            '--type=utility',
                            '--type=zygote'
                        ]):
                            vscode_processes.append(proc)
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error getting VS Code processes: {e}")
            
        self.logger.debug(f"Found {len(vscode_processes)} VS Code processes")
        return vscode_processes
    
    def get_vscode_windows(self) -> List[VSCodeWindow]:
        """Get all VS Code windows.
        
        Returns:
            List of VSCodeWindow objects
        """
        if self.platform == "Linux":
            return self._get_linux_windows()
        elif self.platform == "Windows":
            return self._get_windows_windows()
        elif self.platform == "Darwin":
            return self._get_macos_windows()
        else:
            self.logger.warning(f"Unsupported platform: {self.platform}")
            return []
    
    def _get_linux_windows(self) -> List[VSCodeWindow]:
        """Get VS Code windows on Linux using X11."""
        if not HAS_X11 or not self.display or not self.ewmh:
            self.logger.warning("X11 not available, cannot detect windows")
            return []
        
        windows = []
        vscode_pids = {proc.pid for proc in self.get_vscode_processes()}
        
        try:
            # Get all windows
            all_windows = self.ewmh.getClientList()
            if not all_windows:
                return windows
            
            for window in all_windows:
                try:
                    # Get window properties
                    title = self.ewmh.getWmName(window) or ""
                    window_pid = self.ewmh.getWmPid(window)
                    
                    # Check if this is a VS Code window
                    if window_pid in vscode_pids and self._is_vscode_window(title):
                        # Get window geometry
                        geometry = window.get_geometry()
                        
                        # Check if window is focused
                        active_window = self.ewmh.getActiveWindow()
                        is_focused = active_window == window
                        
                        vscode_window = VSCodeWindow(
                            window_id=window.id,
                            title=title,
                            pid=window_pid,
                            x=geometry.x,
                            y=geometry.y,
                            width=geometry.width,
                            height=geometry.height,
                            is_focused=is_focused
                        )
                        
                        windows.append(vscode_window)
                        
                except Exception as e:
                    self.logger.debug(f"Error processing window {window}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error getting Linux windows: {e}")
        
        self.logger.debug(f"Found {len(windows)} VS Code windows on Linux")
        return windows
    
    def _get_windows_windows(self) -> List[VSCodeWindow]:
        """Get VS Code windows on Windows."""
        if not HAS_WIN32:
            self.logger.warning("win32gui not available, cannot detect windows")
            return []
        
        windows = []
        vscode_pids = {proc.pid for proc in self.get_vscode_processes()}
        
        def enum_window_callback(hwnd, _):
            try:
                # Get window title
                title = win32gui.GetWindowText(hwnd)
                
                # Get window PID
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                
                # Check if this is a VS Code window
                if window_pid in vscode_pids and self._is_vscode_window(title):
                    # Get window position and size
                    rect = win32gui.GetWindowRect(hwnd)
                    x, y, right, bottom = rect
                    width = right - x
                    height = bottom - y
                    
                    # Check if window is focused
                    is_focused = win32gui.GetForegroundWindow() == hwnd
                    
                    vscode_window = VSCodeWindow(
                        window_id=hwnd,
                        title=title,
                        pid=window_pid,
                        x=x,
                        y=y,
                        width=width,
                        height=height,
                        is_focused=is_focused
                    )
                    
                    windows.append(vscode_window)
                    
            except Exception as e:
                self.logger.debug(f"Error processing window {hwnd}: {e}")
            
            return True
        
        try:
            win32gui.EnumWindows(enum_window_callback, None)
        except Exception as e:
            self.logger.error(f"Error enumerating Windows windows: {e}")
        
        self.logger.debug(f"Found {len(windows)} VS Code windows on Windows")
        return windows
    
    def _get_macos_windows(self) -> List[VSCodeWindow]:
        """Get VS Code windows on macOS."""
        if not HAS_MACOS:
            self.logger.warning("AppKit not available, cannot detect windows")
            return []
        
        windows = []
        
        try:
            workspace = NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()
            
            vscode_apps = [app for app in running_apps 
                          if any(name in app.bundleIdentifier().lower() 
                                for name in ['code', 'vscode', 'cursor'])]
            
            for app in vscode_apps:
                # Note: Getting detailed window info on macOS requires additional permissions
                # This is a simplified implementation
                vscode_window = VSCodeWindow(
                    window_id=app.processIdentifier(),
                    title=app.localizedName(),
                    pid=app.processIdentifier(),
                    x=0,  # Would need accessibility permissions to get actual coordinates
                    y=0,
                    width=800,  # Default values
                    height=600,
                    is_focused=app.isActive()
                )
                windows.append(vscode_window)
                
        except Exception as e:
            self.logger.error(f"Error getting macOS windows: {e}")
        
        self.logger.debug(f"Found {len(windows)} VS Code windows on macOS")
        return windows
    
    def _is_vscode_window(self, title: str) -> bool:
        """Check if a window title indicates it's a VS Code window.
        
        Args:
            title: Window title to check
            
        Returns:
            True if this appears to be a VS Code window
        """
        if not title:
            return False
        
        title_lower = title.lower()
        
        # Common VS Code window title patterns
        vscode_indicators = [
            'visual studio code',
            'vscode',
            'code - oss',
            'codium',
            'cursor',
            '- code',  # Files opened in VS Code often end with "- Code"
        ]
        
        # Exclude certain windows
        exclude_patterns = [
            'devtools',
            'developer tools',
            'extension host',
        ]
        
        # Check if title contains VS Code indicators
        has_vscode_indicator = any(indicator in title_lower for indicator in vscode_indicators)
        
        # Check if title should be excluded
        should_exclude = any(pattern in title_lower for pattern in exclude_patterns)
        
        return has_vscode_indicator and not should_exclude
    
    def get_focused_vscode_window(self) -> Optional[VSCodeWindow]:
        """Get the currently focused VS Code window.
        
        Returns:
            VSCodeWindow object if a VS Code window is focused, None otherwise
        """
        windows = self.get_vscode_windows()
        for window in windows:
            if window.is_focused:
                return window
        return None
