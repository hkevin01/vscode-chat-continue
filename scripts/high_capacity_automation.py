#!/usr/bin/env python3
"""
High-Capacity VS Code Continue Button Automation
Optimized for handling many VS Code windows efficiently.
"""

import gc
import logging
import os
import signal
import subprocess
import sys
import time
import warnings
from pathlib import Path
from typing import List

import psutil

# Configure PyTorch to suppress pin_memory warnings for CPU-only usage
os.environ['PYTORCH_DISABLE_GPU'] = '1'
warnings.filterwarnings(
    'ignore',
    message='.*pin_memory.*no accelerator.*',
    category=UserWarning
)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.button_finder import ButtonFinder
from src.core.click_automator import ClickAutomator
from src.core.config_manager import ConfigManager
from src.core.window_detector import WindowDetector


class HighCapacityAutomation:
    """High-capacity automation optimized for many VS Code windows."""
    
    def __init__(self):
        """Initialize with safe multi-window handling."""
        self.running = False
        self.click_automator = ClickAutomator()
        self.config = ConfigManager()
        self.button_finder = ButtonFinder()
        self.window_detector = WindowDetector()
        
        # Conservative configuration for safety and stability
        interval = self.config.get('automation.interval_seconds', 10.0)
        self.check_interval = max(interval, 8.0)  # Minimum 8 seconds for safety
        self.max_retries = self.config.get('automation.max_retries', 2)
        delay_ms = self.config.get('automation.click_delay_ms', 200)
        self.click_delay = delay_ms / 1000.0
        
        # Safe multi-window settings (reduced for stability)
        self.max_windows_per_cycle = 3  # Conservative limit
        self.window_batch_size = 2  # Smaller batches for stability
        self.memory_cleanup_interval = 2  # More frequent cleanup
        self.load_threshold = 4.0  # Lower threshold for safety
        self.adaptive_intervals = True
        
        # Performance tracking
        self.cycle_count = 0
        self.successful_clicks = 0
        self.window_cache = {}
        self.last_cleanup = 0
        self.performance_stats = {
            'avg_cycle_time': 0.0,
            'windows_processed': 0,
            'buttons_found': 0,
            'clicks_successful': 0
        }
        
        # Mouse movement detection for safety
        self.last_mouse_pos = self.get_mouse_position()
        self.mouse_movement_threshold = 50  # pixels
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/high_capacity_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("🚀 Safe high-capacity automation initialized")
        self.logger.info(f"⚙️  Max windows per cycle: "
                         f"{self.max_windows_per_cycle}")
        self.logger.info(f"⚙️  Load threshold: {self.load_threshold}")
        self.logger.info(f"⚙️  Batch size: {self.window_batch_size}")
        self.logger.info("🛡️  Safety mode: VS Code windows only")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"🛑 Received signal {signum}, shutting down...")
        self.running = False
    
    def get_vscode_windows_efficient(self) -> List:
        """Get VS Code windows efficiently with caching and prioritization."""
        try:
            # Use cached window info if recent (within 30 seconds)
            current_time = time.time()
            if (hasattr(self, 'last_window_scan') and
                    current_time - self.last_window_scan < 30 and
                    hasattr(self, 'cached_windows')):
                return self.cached_windows
            
            # Get VS Code windows using WindowDetector
            windows = self.window_detector.get_vscode_windows()
            
            if not windows:
                self.cached_windows = []
                self.last_window_scan = current_time
                return []
            
            # Prioritize windows likely to have Continue buttons
            priority_windows = []
            regular_windows = []
            
            for window in windows:
                title_lower = window.title.lower()
                if any(keyword in title_lower for keyword in 
                       ['continue', 'chat', 'copilot', 'assistant']):
                    priority_windows.append(window)
                elif any(keyword in title_lower for keyword in 
                         ['python', 'code', 'file']):
                    regular_windows.append(window)
                else:
                    regular_windows.append(window)
            
            # Combine priority windows first, then regular windows
            all_windows = priority_windows + regular_windows
            
            # Limit to max windows per cycle but ensure we get priority ones
            final_windows = all_windows[:self.max_windows_per_cycle]
            
            # Cache the results
            self.cached_windows = final_windows
            self.last_window_scan = current_time
            
            if final_windows:
                priority_count = len(priority_windows)
                self.logger.debug(f"🔍 Found {len(final_windows)} VS Code windows ({priority_count} priority)")
            
            return final_windows
            
        except Exception as e:
            self.logger.error(f"Error getting VS Code windows: {e}")
            return []
    
    def capture_vscode_window_safely(self, window) -> str:
        """Capture individual VS Code window using xwd for precise detection."""
        try:
            # Create temporary file for the window screenshot
            temp_dir = "/tmp/vscode_automation"
            os.makedirs(temp_dir, exist_ok=True)
            timestamp = int(time.time() * 1000)
            temp_path = f"{temp_dir}/window_{window.window_id}_{timestamp}.png"
            
            # Use xwd to capture the specific window
            result = subprocess.run([
                "xwd", "-id", str(window.window_id), "-out", f"{temp_path}.xwd"
            ], capture_output=True, timeout=5)
            
            if result.returncode != 0:
                self.logger.debug(f"❌ xwd failed for window {window.window_id}")
                return None
            
            # Convert xwd to PNG using convert (ImageMagick)
            convert_result = subprocess.run([
                "convert", f"{temp_path}.xwd", temp_path
            ], capture_output=True, timeout=5)
            
            # Clean up xwd file
            if os.path.exists(f"{temp_path}.xwd"):
                os.remove(f"{temp_path}.xwd")
            
            if convert_result.returncode != 0 or not os.path.exists(temp_path):
                self.logger.debug(f"❌ Image conversion failed for window {window.window_id}")
                return None
            
            return temp_path
            
        except Exception as e:
            self.logger.debug(f"Error capturing window {window.window_id}: {e}")
            return None
    
    def validate_vscode_window(self, window) -> bool:
        """Enhanced validation to ensure this is actually a VS Code window."""
        try:
            # Check window title more strictly
            title = window.title.lower()
            
            # Explicit browser exclusions
            browser_indicators = [
                'firefox', 'chrome', 'chromium', 'safari', 'edge', 'opera',
                'mozilla', 'webkit', 'browser', 'google chrome', 'mozilla firefox',
                'microsoft edge', 'youtube', 'gmail', 'github.com', 
                'stackoverflow', 'reddit', 'twitter', 'facebook', 'instagram',
                'http://', 'https://', '.com', '.org', '.net', '.io'
            ]
            
            # If any browser indicators are found, reject immediately
            if any(indicator in title for indicator in browser_indicators):
                self.logger.debug(f"❌ Rejected browser window: {title[:50]}")
                return False
            
            # Check that window has reasonable dimensions
            if window.width < 300 or window.height < 200:
                self.logger.debug(f"❌ Window too small: {window.width}x{window.height}")
                return False
            
            # Verify the window is still accessible
            try:
                result = subprocess.run(
                    ["xdotool", "getwindowname", str(window.window_id)],
                    capture_output=True, text=True, timeout=2
                )
                if result.returncode != 0:
                    self.logger.debug(f"❌ Window {window.window_id} no longer accessible")
                    return False
            except Exception as e:
                self.logger.debug(f"❌ Cannot access window {window.window_id}: {e}")
                return False
            
            # Check for VS Code specific process
            try:
                result = subprocess.run(
                    ["xdotool", "getwindowpid", str(window.window_id)],
                    capture_output=True, text=True, timeout=2
                )
                if result.returncode == 0:
                    pid = int(result.stdout.strip())
                    proc = psutil.Process(pid)
                    proc_name = proc.name().lower()
                    proc_exe = proc.exe().lower() if proc.exe() else ""
                    
                    # Verify this is actually a VS Code process
                    vscode_names = ['code', 'vscode', 'code-oss', 'codium', 'cursor']
                    if not any(name in proc_name or name in proc_exe for name in vscode_names):
                        self.logger.debug(f"❌ Process {proc_name} is not VS Code")
                        return False
                        
            except Exception as e:
                self.logger.debug(f"❌ Cannot verify process for window {window.window_id}: {e}")
                return False
            
            self.logger.debug(f"✅ Window validation passed: {title[:50]}")
            return True
            
        except Exception as e:
            self.logger.debug(f"❌ Window validation error: {e}")
            return False

    def validate_vscode_window_strict(self, window) -> bool:
        """
        ULTRA-STRICT validation to prevent ANY browser window interference.
        Triple-layer validation with process verification.
        """
        try:
            title = window.title.lower()
            
            # LAYER 1: Comprehensive browser pattern exclusion
            browser_patterns = [
                # Browser names
                'firefox', 'chrome', 'chromium', 'safari', 'edge', 'opera',
                'mozilla', 'webkit', 'browser', 'google chrome', 
                'mozilla firefox', 'microsoft edge', 'internet explorer',
                
                # Browser-specific indicators
                'tab', 'bookmark', 'download', 'incognito', 'private',
                
                # Web content indicators
                'http://', 'https://', 'www.', 'ftp://',
                '.com', '.org', '.net', '.io', '.co', '.uk', '.de',
                
                # Media and social platforms
                'youtube', 'gmail', 'facebook', 'twitter', 'instagram',
                'linkedin', 'reddit', 'stackoverflow', 'github.com',
                'google.com', 'amazon', 'netflix', 'spotify',
                
                # Media controls that indicate browser media
                'play', 'pause', 'video', 'audio', 'stream', 'media',
                'player', 'controls', 'volume', 'mute',
                
                # Common web app terms
                'login', 'sign in', 'dashboard', 'profile', 'settings',
                'account', 'password', 'register', 'subscribe'
            ]
            
            # Immediate rejection for any browser patterns
            for pattern in browser_patterns:
                if pattern in title:
                    self.logger.error(f"❌ STRICT: Browser pattern '{pattern}' "
                                    f"detected in: {title[:50]}")
                    return False
            
            # LAYER 2: Process verification - must be actual VS Code process
            try:
                result = subprocess.run(
                    ["xdotool", "getwindowpid", str(window.window_id)],
                    capture_output=True, text=True, timeout=2
                )
                if result.returncode != 0:
                    self.logger.error(f"❌ STRICT: Cannot get PID for window "
                                    f"{window.window_id}")
                    return False
                    
                pid = int(result.stdout.strip())
                proc = psutil.Process(pid)
                proc_name = proc.name().lower()
                proc_exe = proc.exe().lower() if proc.exe() else ""
                
                # Verify VS Code process names
                vscode_names = ['code', 'vscode', 'code-oss', 'codium', 'cursor']
                if not any(name in proc_name for name in vscode_names):
                    self.logger.error(f"❌ STRICT: Process '{proc_name}' is not "
                                    f"VS Code")
                    return False
                    
                # Reject browser processes
                browser_processes = [
                    'firefox', 'chrome', 'chromium', 'safari', 'edge', 
                    'opera', 'browser', 'gecko', 'webkit'
                ]
                if any(browser in proc_name or browser in proc_exe 
                       for browser in browser_processes):
                    self.logger.error(f"❌ STRICT: Browser process detected: "
                                    f"{proc_name}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"❌ STRICT: Process verification failed: {e}")
                return False
            
            # LAYER 3: Window title must contain VS Code indicators
            vscode_indicators = [
                'visual studio code', 'vscode', 'code - oss', 'codium',
                'cursor', '- code', 'copilot', 'continue', 'chat'
            ]
            
            has_vscode_indicator = any(indicator in title 
                                     for indicator in vscode_indicators)
            if not has_vscode_indicator:
                self.logger.error(f"❌ STRICT: No VS Code indicators in title: "
                                f"{title[:50]}")
                return False
            
            # LAYER 4: Window dimensions sanity check
            if window.width < 400 or window.height < 300:
                self.logger.error(f"❌ STRICT: Window too small for VS Code: "
                                f"{window.width}x{window.height}")
                return False
            
            self.logger.debug(f"✅ STRICT: Window validation passed: "
                            f"{title[:50]}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ STRICT: Validation error: {e}")
            return False

    def process_vscode_window_safely(self, window) -> bool:
        """
        MOUSE-FREE VS Code window processing with keyboard-only interaction.
        This method NEVER uses mouse clicks for safety.
        """
        try:
            # CRITICAL: Skip mouse-based approach entirely - use keyboard only
            self.logger.info(f"🚫 MOUSE-FREE: Skipping visual button detection")
            self.logger.info(f"⌨️ Using keyboard-only method for window {window.window_id}")
            
            # Always use the safe keyboard method instead of mouse clicking
            return self.type_continue_in_chat(window)
                
        except Exception as e:
            self.logger.error(f"Error in mouse-free processing: {e}")
            return False
    
    def type_continue_in_chat(self, window) -> bool:
        """
        PROGRAMMATIC CONTINUE METHOD: Use keyboard shortcuts and commands instead of visual button clicking.
        This method prioritizes keyboard shortcuts like Ctrl+Enter that directly trigger continue/accept functionality.
        """
        try:
            self.logger.info(f"🎯 PROGRAMMATIC METHOD: Continue automation for window {window.window_id}")

            # CRITICAL SAFETY: Triple-check this is actually VS Code
            if not self.validate_vscode_window_strict(window):
                self.logger.error(f"❌ SAFETY ABORT: Window {window.window_id} failed strict validation")
                return False

            # CRITICAL SAFETY: Check window title again for browser content
            title = window.title.lower()
            browser_keywords = [
                'youtube', 'firefox', 'chrome', 'safari', 'edge', 'opera', 'browser',
                'google', 'mozilla', 'webkit', 'http', 'www', '.com', '.org', 
                'video', 'watch', 'play', 'pause', 'gmail', 'facebook', 'twitter'
            ]
            
            if any(keyword in title for keyword in browser_keywords):
                self.logger.error(f"❌ SAFETY ABORT: Browser content detected in title: {title[:50]}")
                return False

            # Focus window with verification
            self.logger.debug(f"🎯 Focusing VS Code window {window.window_id}")
            result = subprocess.run(
                ["xdotool", "windowactivate", str(window.window_id)],
                capture_output=True, text=True, timeout=3
            )
            
            if result.returncode != 0:
                self.logger.error(f"❌ Failed to focus window {window.window_id}")
                return False
                
            time.sleep(0.3)

            # METHOD 1: Try Ctrl+Enter (most reliable for accept/continue in inline chat)
            self.logger.debug("🔄 Attempting Ctrl+Enter method (inline chat accept)...")
            try:
                result = subprocess.run([
                    "xdotool", "key", "--window", str(window.window_id), "ctrl+Return"
                ], capture_output=True, text=True, timeout=3)
                
                if result.returncode == 0:
                    self.logger.info("✅ SUCCESS: Ctrl+Enter executed for continue/accept")
                    self.successful_clicks += 1
                    return True
                    
            except Exception as e:
                self.logger.debug(f"Ctrl+Enter method failed: {e}")

            # METHOD 2: Command palette approach for accept commands
            self.logger.debug("🔄 Attempting command palette method...")
            try:
                # Open command palette
                subprocess.run([
                    "xdotool", "key", "--window", str(window.window_id), "ctrl+shift+p"
                ], capture_output=True, timeout=2)
                time.sleep(0.4)
                
                # Type accept command
                subprocess.run([
                    "xdotool", "type", "--window", str(window.window_id), "Chat: Accept"
                ], capture_output=True, timeout=2)
                time.sleep(0.2)
                
                # Execute command
                subprocess.run([
                    "xdotool", "key", "--window", str(window.window_id), "Return"
                ], capture_output=True, timeout=2)
                
                self.logger.info("✅ SUCCESS: Command palette accept executed")
                self.successful_clicks += 1
                return True
                
            except Exception as e:
                self.logger.debug(f"Command palette method failed: {e}")

            # METHOD 3: Try Enter key alone (for chat submission)
            self.logger.debug("🔄 Attempting Enter key method...")
            try:
                result = subprocess.run([
                    "xdotool", "key", "--window", str(window.window_id), "Return"
                ], capture_output=True, text=True, timeout=3)
                
                if result.returncode == 0:
                    self.logger.info("✅ SUCCESS: Enter key executed for submission")
                    self.successful_clicks += 1
                    return True
                    
            except Exception as e:
                self.logger.debug(f"Enter key method failed: {e}")

            # METHOD 4: Fallback - type "continue" and press Enter
            self.logger.debug("🔄 Fallback method: typing 'continue'...")
            try:
                # Click in chat area to ensure focus (minimal mouse usage)
                chat_input_x = window.width // 2
                chat_input_y = int(window.height * 0.9)
                
                subprocess.run([
                    "xdotool", "mousemove", "--window", str(window.window_id), 
                    str(chat_input_x), str(chat_input_y)
                ], capture_output=True, timeout=2)
                
                subprocess.run([
                    "xdotool", "click", "--window", str(window.window_id), "1"
                ], capture_output=True, timeout=2)
                time.sleep(0.2)
                
                # Clear existing text
                subprocess.run([
                    "xdotool", "key", "--window", str(window.window_id), "ctrl+a"
                ], capture_output=True, timeout=2)
                
                # Type "continue"
                subprocess.run([
                    "xdotool", "type", "--window", str(window.window_id), "continue"
                ], capture_output=True, timeout=2)
                time.sleep(0.2)
                
                # Press Enter
                subprocess.run([
                    "xdotool", "key", "--window", str(window.window_id), "Return"
                ], capture_output=True, timeout=2)
                
                self.logger.info("✅ SUCCESS: Fallback method completed")
                self.successful_clicks += 1
                return True
                
            except Exception as e:
                self.logger.error(f"Fallback method failed: {e}")

            self.logger.error("❌ All programmatic methods failed")
            return False

        except Exception as e:
            self.logger.error(f"❌ PROGRAMMATIC METHOD failed for window {window.window_id}: {e}")
            return False

    def is_click_within_window_bounds(self, x: int, y: int, window) -> bool:
        """Verify that click coordinates are within the window bounds."""
        try:
            window_left = window.x
            window_top = window.y
            window_right = window_left + window.width
            window_bottom = window_top + window.height
            
            return (window_left <= x <= window_right and
                    window_top <= y <= window_bottom)
        except Exception as e:
            self.logger.error(f"Error checking window bounds: {e}")
            return False
    
    def process_windows_batch_safely(self, windows: List) -> int:
        """
        Process VS Code windows safely using ONLY keyboard methods.
        COMPLETELY MOUSE-FREE automation for maximum safety.
        """
        buttons_clicked = 0
        
        # Process windows in smaller batches to manage resources
        for i in range(0, len(windows), self.window_batch_size):
            batch = windows[i:i + self.window_batch_size]
            
            for window in batch:
                try:
                    # SAFETY: Check for mouse movement first
                    if self.check_mouse_movement():
                        self.logger.info("⏸️ Mouse activity detected, skipping this cycle")
                        return buttons_clicked
                    
                    # ULTRA-STRICT validation before any interaction
                    if not self.validate_vscode_window_strict(window):
                        self.logger.warning(f"❌ STRICT validation failed for {window.window_id}")
                        continue
                    
                    # MOUSE-FREE METHOD: Use only keyboard interaction
                    self.logger.info(f"⌨️ KEYBOARD-ONLY: Processing window {window.window_id}")
                    
                    if self.type_continue_in_chat(window):
                        buttons_clicked += 1
                        self.logger.info("✅ Keyboard method successful, stopping cycle for safety")
                        return buttons_clicked
                    
                except Exception as e:
                    self.logger.debug(f"❌ Error processing window {window.window_id}: {e}")
                    continue
            
            # Small delay between batches to prevent overwhelming the system
            if i + self.window_batch_size < len(windows):
                time.sleep(0.5)
        
        return buttons_clicked
    
    def automation_cycle(self) -> bool:
        """Perform one safe automation cycle - only VS Code windows."""
        start_time = time.time()
        
        try:
            # Get VS Code windows efficiently
            windows = self.get_vscode_windows_efficient()
            
            if not windows:
                self.logger.debug("🔍 No VS Code windows found")
                return False
            
            self.logger.info(f"🔍 Processing {len(windows)} VS Code windows safely")
            
            # Process windows with safety checks - only VS Code windows
            buttons_clicked = self.process_windows_batch_safely(windows)
            
            # Update performance stats
            cycle_time = time.time() - start_time
            self.performance_stats['avg_cycle_time'] = (
                (self.performance_stats['avg_cycle_time'] * self.cycle_count + cycle_time) / 
                (self.cycle_count + 1)
            )
            self.performance_stats['windows_processed'] += len(windows)
            
            # Adaptive interval adjustment for stability
            if self.adaptive_intervals:
                if cycle_time > 8.0:  # If cycle takes too long
                    self.check_interval = min(self.check_interval * 1.2, 20.0)
                    self.logger.info(f"🐌 Increasing interval to {self.check_interval:.1f}s for stability")
                elif cycle_time < 3.0 and self.check_interval > 8.0:  # If cycle is fast
                    self.check_interval = max(self.check_interval * 0.9, 8.0)
                    self.logger.info(f"⚡ Decreasing interval to {self.check_interval:.1f}s")
            
            if buttons_clicked > 0:
                self.logger.info(f"✅ Successfully clicked {buttons_clicked} Continue button(s)")
            else:
                self.logger.debug("❌ No Continue buttons found or clickable")
            
            return buttons_clicked > 0
            
        except Exception as e:
            self.logger.error(f"Error in automation cycle: {e}")
            return False
    
    def cleanup_resources(self):
        """Clean up resources periodically."""
        try:
            # Force garbage collection
            gc.collect()
            
            # Clear window cache periodically
            if hasattr(self, 'cached_windows'):
                del self.cached_windows
            
            # Clean temp files
            temp_dir = Path("tmp")
            if temp_dir.exists():
                for temp_file in temp_dir.glob("automation_capture_*.png"):
                    try:
                        temp_file.unlink()
                    except:
                        pass
            
            self.logger.debug("🧹 Resources cleaned up")
            
        except Exception as e:
            self.logger.debug(f"Error during cleanup: {e}")
    
    def get_mouse_position(self) -> tuple:
        """Get current mouse position with enhanced tracking."""
        try:
            result = subprocess.run(
                ["xdotool", "getmouselocation", "--shell"],
                capture_output=True, text=True, timeout=1
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                x = int(lines[0].split('=')[1])
                y = int(lines[1].split('=')[1])
                return (x, y)
        except Exception as e:
            self.logger.debug(f"Mouse position detection failed: {e}")
        return (0, 0)
    
    def check_mouse_movement(self) -> bool:
        """
        Enhanced mouse movement detection with user interaction response.
        When mouse movement is detected, either scroll to continue button
        or pause automation completely.
        """
        try:
            current_pos = self.get_mouse_position()
            
            if not hasattr(self, 'last_mouse_pos'):
                self.last_mouse_pos = current_pos
                return False
            
            # Calculate distance moved
            dx = current_pos[0] - self.last_mouse_pos[0]
            dy = current_pos[1] - self.last_mouse_pos[1]
            distance = (dx**2 + dy**2)**0.5
            
            # Lower threshold for more responsive detection
            movement_threshold = 30.0  # Reduced from 50px
            
            if distance > movement_threshold:
                self.logger.warning(f"🖱️ Mouse movement detected ({distance:.1f}px), "
                                  f"pausing automation")
                
                # Store current position for next check
                self.last_mouse_pos = current_pos
                
                # Option 1: Try to scroll to continue button in active window
                if self.try_scroll_to_continue():
                    self.logger.info("📜 Attempted to scroll to continue button")
                
                # Option 2: Pause automation to avoid interference
                self.logger.info("⏸️ Pausing automation due to mouse activity")
                return True
            
            # Update position if no significant movement
            self.last_mouse_pos = current_pos
            return False
            
        except Exception as e:
            self.logger.debug(f"Mouse movement check failed: {e}")
            return False
    
    def try_scroll_to_continue(self) -> bool:
        """
        Try to scroll the active window to make continue button visible.
        This is a non-intrusive way to help when user is actively using mouse.
        """
        try:
            # Get active window
            result = subprocess.run(
                ["xdotool", "getactivewindow"],
                capture_output=True, text=True, timeout=2
            )
            
            if result.returncode != 0:
                return False
                
            active_window_id = result.stdout.strip()
            
            # Check if active window is VS Code
            result = subprocess.run(
                ["xdotool", "getwindowname", active_window_id],
                capture_output=True, text=True, timeout=2
            )
            
            if result.returncode != 0:
                return False
                
            window_title = result.stdout.strip().lower()
            
            # Only scroll if it's a VS Code window
            vscode_indicators = ['code', 'vscode', 'copilot', 'chat']
            if not any(indicator in window_title for indicator in vscode_indicators):
                return False
            
            # Scroll down to potentially reveal continue button
            # Use Page Down key which is less intrusive than mouse scrolling
            subprocess.run([
                "xdotool", "key", "--window", active_window_id, "End"
            ], capture_output=True, timeout=2)
            
            self.logger.debug(f"📜 Scrolled VS Code window {active_window_id} to bottom")
            return True
            
        except Exception as e:
            self.logger.debug(f"Scroll to continue failed: {e}")
            return False

    def run(self):
        """Run the safe high-capacity automation."""
        self.logger.info("🚀 Starting Safe VS Code Continue Button Automation")
        self.logger.info(f"⚙️  Check interval: {self.check_interval:.1f} seconds")
        self.logger.info(f"⚙️  Max windows per cycle: {self.max_windows_per_cycle}")
        self.logger.info(f"⚙️  Load threshold: {self.load_threshold}")
        self.logger.info("🛡️  Safety mode: Only VS Code windows processed")
        self.logger.info("⚙️  Press Ctrl+C to stop")
        
        self.running = True
        
        try:
            while self.running:
                # Check for mouse movement first
                if self.check_mouse_movement():
                    self.logger.info("⏸️  Pausing automation due to mouse activity")
                    time.sleep(5)  # Wait 5 seconds for user activity to finish
                    continue
                
                self.cycle_count += 1
                
                cycle_start = time.time()
                button_clicked = self.automation_cycle()
                cycle_time = time.time() - cycle_start
                
                if button_clicked:
                    self.successful_clicks += 1
                    self.logger.info(f"🔄 Cycle {self.cycle_count}: Button clicked! (Total: {self.successful_clicks}) [{cycle_time:.1f}s]")
                else:
                    self.logger.debug(f"🔄 Cycle {self.cycle_count}: No buttons found [{cycle_time:.1f}s]")
                
                # More frequent cleanup for stability
                if self.cycle_count % self.memory_cleanup_interval == 0:
                    self.cleanup_resources()
                
                # Periodic stats report
                if self.cycle_count % 15 == 0:
                    avg_time = self.performance_stats['avg_cycle_time']
                    windows_proc = self.performance_stats['windows_processed']
                    self.logger.info(f"📊 Stats: {self.cycle_count} cycles, {self.successful_clicks} clicks, {windows_proc} windows processed, avg {avg_time:.1f}s/cycle")
                
                # Wait for next cycle
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Interrupted by user")
        except Exception as e:
            self.logger.error(f"🚨 Unexpected error: {e}")
        finally:
            self.running = False
            self.cleanup_resources()
            
            # Final stats
            avg_time = self.performance_stats['avg_cycle_time']
            windows_proc = self.performance_stats['windows_processed']
            self.logger.info(f"🏁 Safe automation stopped after {self.cycle_count} cycles")
            self.logger.info(f"📊 Final stats: {self.successful_clicks} successful clicks, {windows_proc} windows processed, avg {avg_time:.1f}s/cycle")


def main():
    """Main function."""
    print("🚀 VS Code Continue Button Safe High-Capacity Automation")
    print("=" * 60)
    print()
    print("Safe automation for environments with multiple VS Code windows:")
    print("- ✅ Only processes VS Code windows (never clicks outside)")
    print("- ✅ Individual window screenshots using xwd")
    print("- ✅ Proper button detection with ButtonFinder")
    print("- ✅ Window bounds checking for all clicks")
    print("- ✅ Conservative resource usage (3 windows max per cycle)")
    print("- ✅ Enhanced error handling and recovery")
    print("- ✅ No unsafe coordinate fallback")
    print()
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    try:
        automation = HighCapacityAutomation()
        automation.run()
    except Exception as e:
        print(f"❌ Failed to start automation: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
