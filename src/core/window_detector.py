"""Window detection module for finding VS Code windows."""

import logging
import platform
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import psutil

# Initialize all platform flags to False first
HAS_X11 = False
HAS_WIN32 = False
HAS_MACOS = False

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
        self.display = None
        self.ewmh = None
        
        if self.platform == "Linux" and HAS_X11:
            import os

            # Check if we have a valid DISPLAY
            display_env = os.environ.get('DISPLAY')
            if not display_env:
                self.logger.warning(
                    "No DISPLAY environment variable set - "
                    "X11 window detection unavailable"
                )
                return
            
            try:
                self.display = Xlib.display.Display()
                self.ewmh = EWMH()
                self.logger.debug("X11 components initialized successfully")
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
                    if not proc_info:
                        continue
                        
                    # Safely get name and exe, handling None values
                    name = proc_info.get('name')
                    exe = proc_info.get('exe')
                    
                    name = (name or '').lower() if name is not None else ''
                    exe = (exe or '').lower() if exe is not None else ''
                    
                    # Check for VS Code process names
                    if any(vscode_name in name for vscode_name in [
                        'code', 'vscode', 'code-oss', 'codium', 'cursor'
                    ]) or any(vscode_name in exe for vscode_name in [
                        'code', 'vscode', 'code-oss', 'codium', 'cursor'
                    ]):
                        # Exclude helper processes
                        cmdline = proc_info.get('cmdline', [])
                        if cmdline:
                            # Filter out None values from cmdline and safely join
                            cmdline_filtered = [str(arg) for arg in cmdline if arg is not None]
                            cmdline_str = ' '.join(cmdline_filtered)
                            if not any(helper in cmdline_str.lower() for helper in [
                                '--type=gpu-process',
                                '--type=renderer',
                                '--type=utility',
                                '--type=zygote'
                            ]):
                                vscode_processes.append(proc)
                        else:
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
        try:
            if self.platform == "Linux":
                return self._get_linux_windows()
            elif self.platform == "Windows":
                return self._get_windows_windows()
            elif self.platform == "Darwin":
                return self._get_macos_windows()
            else:
                self.logger.warning(f"Unsupported platform: {self.platform}")
                return []
        except Exception as e:
            self.logger.error(f"Error in get_vscode_windows: {e}")
            # Return empty list as fallback to prevent crashes
            return []
    
    def _get_linux_windows(self) -> List[VSCodeWindow]:
        """Get VS Code windows on Linux using X11."""
        if not HAS_X11 or not self.display or not self.ewmh:
            self.logger.warning("X11 not available, cannot detect windows")
            return []
        
        windows = []
        try:
            vscode_pids = {proc.pid for proc in self.get_vscode_processes()}
            self.logger.debug(f"VS Code PIDs to look for: {vscode_pids}")
        except Exception as e:
            self.logger.error(f"Failed to get VS Code processes: {e}")
            return []
        
        try:
            # Simplified approach - get all windows without complex timeouts
            all_windows = self.ewmh.getClientList()
            if not all_windows:
                self.logger.debug("No windows found via X11")
                return windows
            
            self.logger.debug(f"Found {len(all_windows)} total windows via X11")
            
            for window in all_windows:
                try:
                    # Skip if window is None or invalid
                    if not window:
                        continue
                        
                    # Get window properties with error handling
                    title = ""
                    try:
                        title_raw = self.ewmh.getWmName(window)
                        if title_raw:
                            if isinstance(title_raw, bytes):
                                title = title_raw.decode('utf-8', errors='ignore')
                            else:
                                title = str(title_raw)
                    except Exception as e:
                        self.logger.debug(f"Could not get window title: {e}")
                        continue
                    
                    # Get window PID
                    window_pid = None
                    try:
                        window_pid = self.ewmh.getWmPid(window)
                    except Exception as e:
                        self.logger.debug(f"Could not get window PID: {e}")
                        continue
                    
                    # Debug: Log all windows to see what we're getting
                    self.logger.debug(f"Window: PID={window_pid}, Title='{title}'")
                    
                    # Check if this is a VS Code window
                    is_vscode_pid = window_pid in vscode_pids if window_pid else False
                    is_vscode_title = self._is_vscode_window(title)
                    
                    self.logger.debug(f"  VS Code PID match: {is_vscode_pid}")
                    self.logger.debug(f"  VS Code title match: {is_vscode_title}")
                    
                    if is_vscode_pid and is_vscode_title:
                        try:
                            # Get window geometry
                            geometry = window.get_geometry()
                            
                            # Get absolute coordinates
                            abs_x, abs_y = geometry.x, geometry.y
                            try:
                                root = self.display.screen().root
                                translated = window.translate_coords(root, 0, 0)
                                if (translated.x >= 0 and translated.y >= 0 and 
                                    translated.x < 10000 and translated.y < 10000):
                                    abs_x, abs_y = translated.x, translated.y
                                else:
                                    self.logger.debug(f"Using geometry coords instead of translated: ({translated.x}, {translated.y})")
                            except Exception:
                                pass  # Use geometry coordinates
                                
                            # Check if window is focused
                            is_focused = False
                            try:
                                active_window = self.ewmh.getActiveWindow()
                                is_focused = active_window == window
                            except Exception:
                                pass  # Default to not focused
                            
                            # Create VSCodeWindow object
                            vscode_window = VSCodeWindow(
                                window_id=getattr(window, 'id', 0),
                                title=title,
                                pid=window_pid,
                                x=abs_x,
                                y=abs_y,
                                width=geometry.width,
                                height=geometry.height,
                                is_focused=is_focused
                            )
                            
                            windows.append(vscode_window)
                            self.logger.info(f"Found VS Code window: {title[:50]}... at ({abs_x},{abs_y})")
                            
                        except Exception as e:
                            self.logger.debug(f"Could not process window geometry: {e}")
                            continue
                        
                except Exception as e:
                    self.logger.debug(f"Error processing window: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error getting Linux windows: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        self.logger.info(f"Found {len(windows)} VS Code windows on Linux")
        return windows
    
    def _get_windows_windows(self) -> List[VSCodeWindow]:
        """Get VS Code windows on Windows."""
        if not HAS_WIN32:
            self.logger.warning(
                "win32gui not available, cannot detect windows")
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
            
            vscode_apps = [
                app for app in running_apps
                if any(name in (app.bundleIdentifier() or '').lower()
                       for name in ['code', 'vscode', 'cursor'])
            ]
            
            for app in vscode_apps:
                # Note: Getting detailed window info on macOS requires
                # additional permissions
                # This is a simplified implementation
                vscode_window = VSCodeWindow(
                    window_id=app.processIdentifier(),
                    title=app.localizedName(),
                    pid=app.processIdentifier(),
                    x=0,  # Would need accessibility permissions
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
        has_vscode_indicator = any(
            indicator in title_lower for indicator in vscode_indicators)
        
        # Check if title should be excluded
        should_exclude = any(
            pattern in title_lower for pattern in exclude_patterns)
        
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
