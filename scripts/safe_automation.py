#!/usr/bin/env python3
"""
Lightweight VS Code Continue Button Automation - System-Friendly Version
Optimized to prevent system freezing with minimal resource usage.
"""

import gc
import logging
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.button_finder import ButtonFinder
from src.core.click_automator import ClickAutomator
from src.core.config_manager import ConfigManager


class LightweightAutomation:
    """Ultra-lightweight automation to prevent system freezing."""
    
    def __init__(self):
        """Initialize with minimal resource usage."""
        self.running = False
        self.button_finder = None  # Initialize only when needed
        self.click_automator = None  # Initialize only when needed
        self.config = ConfigManager()
        
        # Conservative configuration to prevent system overload
        self.check_interval = max(10.0, self.config.get('automation.interval_seconds', 10.0))  # Minimum 10 seconds
        self.max_retries = min(2, self.config.get('automation.max_retries', 2))  # Maximum 2 retries
        self.click_delay = self.config.get('automation.click_delay_ms', 200) / 1000.0
        self.max_windows_per_cycle = 2  # Limit windows processed per cycle
        self.memory_cleanup_interval = 5  # Force garbage collection every 5 cycles
        
        # Performance tracking
        self.cycle_count = 0
        self.last_cleanup = 0
        self.process_times = []
        
        # Setup minimal logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[logging.StreamHandler()]  # Only console, no file to reduce I/O
        )
        self.logger = logging.getLogger(__name__)
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("🟢 Lightweight automation initialized (system-friendly mode)")
        self.logger.info(f"⏱️  Check interval: {self.check_interval}s (conservative)")
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"🛑 Received signal {signum}, shutting down...")
        self.running = False
    
    def _lazy_init_components(self):
        """Initialize components only when needed to save memory."""
        if self.button_finder is None:
            self.button_finder = ButtonFinder()
        if self.click_automator is None:
            self.click_automator = ClickAutomator()
    
    def _force_memory_cleanup(self):
        """Force garbage collection to prevent memory leaks."""
        gc.collect()
        self.last_cleanup = self.cycle_count
        
        # Clear any cached data in button finder
        if self.button_finder:
            # Reset any internal caches if they exist
            pass
    
    def _monitor_performance(self, cycle_time: float):
        """Monitor performance and adjust if needed."""
        self.process_times.append(cycle_time)
        
        # Keep only last 10 measurements
        if len(self.process_times) > 10:
            self.process_times.pop(0)
        
        avg_time = sum(self.process_times) / len(self.process_times)
        
        # If average cycle time is too high, warn and increase interval
        if avg_time > 5.0:
            self.logger.warning(f"⚠️  High cycle time detected: {avg_time:.1f}s")
            if self.check_interval < 15.0:
                self.check_interval = min(15.0, self.check_interval + 2.0)
                self.logger.warning(f"🐌 Increasing interval to {self.check_interval}s to prevent system overload")
    
    def get_vscode_windows_minimal(self) -> List[dict]:
        """Get VS Code windows with minimal system impact."""
        try:
            # Use a much faster, simpler window detection
            result = subprocess.run(
                ["wmctrl", "-l"], 
                capture_output=True, 
                text=True,
                timeout=3  # Timeout to prevent hanging
            )
            
            windows = []
            for line in result.stdout.split('\n'):
                if 'code' in line.lower() and len(windows) < self.max_windows_per_cycle:
                    # Simple parsing - just get window ID and title
                    parts = line.split(None, 3)
                    if len(parts) >= 4:
                        window_id = parts[0]
                        title = parts[3]
                        
                        # Prioritize computer-vision window
                        if 'computer-vision' in title.lower():
                            windows.insert(0, {
                                'id': window_id,
                                'title': title,
                                'priority': True
                            })
                        else:
                            windows.append({
                                'id': window_id,
                                'title': title,
                                'priority': False
                            })
            
            return windows[:self.max_windows_per_cycle]  # Limit to prevent overload
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # Fallback to even simpler method
            self.logger.debug("wmctrl not available, using minimal detection")
            return []
    
    def check_system_resources(self) -> bool:
        """Check if system has enough resources to continue safely."""
        try:
            # Check CPU load average (Linux)
            with open('/proc/loadavg', 'r') as f:
                load_avg = float(f.read().split()[0])
            
            # If load average is too high, skip this cycle
            if load_avg > 3.0:
                self.logger.warning(f"⚠️  High system load detected: {load_avg:.1f}, skipping cycle")
                return False
                
        except (FileNotFoundError, ValueError, IndexError):
            # Can't check load, assume it's okay
            pass
        
        return True
    
    def process_window_safe(self, window: dict) -> bool:
        """Process window with maximum safety and minimal resource usage."""
        start_time = time.time()
        
        try:
            # Initialize components only when needed
            self._lazy_init_components()
            
            self.logger.debug(f"🔍 Checking window: {window['title'][:30]}...")
            
            # Use coordinate-based fallback instead of image capture to save resources
            # This assumes user has provided specific coordinates
            coordinates = self.config.get('fallback_coordinates', {})
            
            if coordinates:
                x = coordinates.get('continue_button_x', 1713)
                y = coordinates.get('continue_button_y', 1723)
                
                self.logger.debug(f"🎯 Using coordinate fallback: ({x}, {y})")
                
                # Simple click without image processing
                time.sleep(self.click_delay)
                result = self.click_automator.click(x, y)
                
                if result.success:
                    self.logger.info("✅ Clicked Continue button (coordinate-based)")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error processing window safely: {e}")
            return False
        finally:
            # Track processing time
            process_time = time.time() - start_time
            self._monitor_performance(process_time)
    
    def automation_cycle_safe(self) -> bool:
        """Perform one automation cycle with maximum safety."""
        try:
            self.cycle_count += 1
            
            # Check system resources before proceeding
            if not self.check_system_resources():
                time.sleep(self.check_interval * 2)  # Wait longer if system is busy
                return False
            
            # Force memory cleanup periodically
            if self.cycle_count - self.last_cleanup >= self.memory_cleanup_interval:
                self._force_memory_cleanup()
            
            # Get windows with minimal impact
            windows = self.get_vscode_windows_minimal()
            
            if not windows:
                self.logger.debug("🔍 No VS Code windows found")
                return False
            
            self.logger.debug(f"🪟 Found {len(windows)} window(s)")
            
            # Process only the first (highest priority) window
            for window in windows[:1]:  # Process only one window per cycle
                if self.process_window_safe(window):
                    return True
                
                # Small delay between windows to prevent system overload
                time.sleep(0.5)
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error in safe automation cycle: {e}")
            # Force cleanup on error
            self._force_memory_cleanup()
            return False
    
    def run_safe(self):
        """Run the automation with maximum safety to prevent system freezing."""
        self.logger.info("🚀 Starting SAFE VS Code Continue Button Automation")
        self.logger.info("🛡️  System-friendly mode: Optimized to prevent freezing")
        self.logger.info(f"⏱️  Conservative interval: {self.check_interval}s")
        self.logger.info(f"🪟 Max windows per cycle: {self.max_windows_per_cycle}")
        self.logger.info("Press Ctrl+C to stop")
        
        self.running = True
        buttons_clicked = 0
        
        try:
            while self.running:
                cycle_start = time.time()
                
                if self.automation_cycle_safe():
                    buttons_clicked += 1
                    self.logger.info(f"✅ Cycle {self.cycle_count}: Button clicked! (Total: {buttons_clicked})")
                else:
                    if self.cycle_count % 10 == 0:  # Log every 10 cycles
                        self.logger.info(f"🔄 Cycle {self.cycle_count}: No buttons found")
                
                # Calculate how long to sleep (ensure minimum interval)
                cycle_time = time.time() - cycle_start
                sleep_time = max(self.check_interval - cycle_time, 2.0)  # Minimum 2 second sleep
                
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Interrupted by user")
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}")
        finally:
            self.running = False
            self._force_memory_cleanup()
            self.logger.info(f"🏁 Safe automation stopped after {self.cycle_count} cycles, {buttons_clicked} buttons clicked")


def main():
    """Main function."""
    print("🛡️  VS Code Continue Button Automation - SAFE MODE")
    print("=" * 55)
    print()
    print("🚀 This version is optimized to prevent system freezing:")
    print("   • Conservative resource usage")
    print("   • Minimal memory footprint") 
    print("   • Extended intervals between checks")
    print("   • Automatic performance monitoring")
    print("   • System load detection")
    print()
    
    try:
        automation = LightweightAutomation()
        automation.run_safe()
    except Exception as e:
        print(f"❌ Failed to start safe automation: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
