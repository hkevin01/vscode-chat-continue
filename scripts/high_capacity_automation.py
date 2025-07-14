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
from pathlib import Path
from typing import Dict, List, Tuple

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
    
    def process_vscode_window_safely(self, window) -> bool:
        """Process a single VS Code window safely with proper bounds checking."""
        try:
            # Capture window-specific screenshot using xwd
            screenshot_path = self.capture_vscode_window_safely(window)
            if not screenshot_path:
                return False
            
            # Load the image for ButtonFinder
            try:
                from PIL import Image
                image = Image.open(screenshot_path)
            except Exception as e:
                self.logger.debug(f"❌ Failed to load image: {e}")
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
                return False
            
            # Use ButtonFinder to detect Continue button within this window
            buttons = self.button_finder.find_continue_buttons(image, window.x, window.y)
            
            # Clean up temporary screenshot
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            
            if not buttons:
                self.logger.debug(f"❌ No Continue button found in VS Code window {window.window_id}")
                return False
            
            # Use the first detected button
            button = buttons[0]
            
            # Calculate click coordinates (button coordinates are already absolute)
            screen_x = button.x + (button.width // 2)
            screen_y = button.y + (button.height // 2)
            
            # Verify click coordinates are within window bounds
            if not self.is_click_within_window_bounds(screen_x, screen_y, window):
                self.logger.warning(f"❌ Click coordinates ({screen_x}, {screen_y}) outside window bounds")
                return False
            
            # Focus the window
            subprocess.run([
                "xdotool", "windowactivate", str(window.window_id)
            ], capture_output=True, timeout=2)
            
            time.sleep(0.2)  # Brief delay for window focus
            
            # Perform the click
            result = self.click_automator.click(screen_x, screen_y)
            
            if result.success:
                self.logger.info(f"✅ Successfully clicked Continue button in VS Code window")
                self.successful_clicks += 1
                return True
            else:
                self.logger.warning(f"❌ Click failed: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing VS Code window safely: {e}")
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
        """Process VS Code windows safely using proper window screenshots."""
        buttons_clicked = 0
        
        # Process windows in smaller batches to manage resources
        for i in range(0, len(windows), self.window_batch_size):
            batch = windows[i:i + self.window_batch_size]
            
            for window in batch:
                try:
                    # Only process VS Code windows with proper window screenshots
                    if self.process_vscode_window_safely(window):
                        buttons_clicked += 1
                        # Only click one button per cycle for safety
                        self.logger.info(f"✅ Clicked button, stopping cycle for safety")
                        return buttons_clicked
                    
                except Exception as e:
                    self.logger.debug(f"❌ Error processing VS Code window {window.window_id}: {e}")
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
