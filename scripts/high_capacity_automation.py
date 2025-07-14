#!/usr/bin/env python3
"""
High-Capacity VS Code Continue Button Automation
Optimized for handling many VS Code windows efficiently.
"""

import gc
import logging
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.click_automator import ClickAutomator
from src.core.config_manager import ConfigManager


class HighCapacityAutomation:
    """High-capacity automation optimized for many VS Code windows."""
    
    def __init__(self):
        """Initialize with efficient multi-window handling."""
        self.running = False
        self.click_automator = ClickAutomator()
        self.config = ConfigManager()
        
        # Optimized configuration for many windows
        interval = self.config.get('automation.interval_seconds', 8.0)
        self.check_interval = interval  # Reasonable interval
        self.max_retries = self.config.get('automation.max_retries', 2)
        delay_ms = self.config.get('automation.click_delay_ms', 150)
        self.click_delay = delay_ms / 1000.0
        
        # Multi-window optimization settings
        self.max_windows_per_cycle = 10  # Process more windows per cycle
        self.window_batch_size = 3  # Process windows in smaller batches
        self.memory_cleanup_interval = 3  # More frequent cleanup
        self.load_threshold = 8.0  # Higher threshold for many windows
        self.adaptive_intervals = True  # Adjust intervals based on performance
        
        # Performance tracking
        self.cycle_count = 0
        self.successful_clicks = 0
        self.window_cache = {}  # Cache window information
        self.last_cleanup = 0
        self.performance_stats = {
            'avg_cycle_time': 0.0,
            'windows_processed': 0,
            'buttons_found': 0,
            'clicks_successful': 0
        }
        
        # Coordinate-based fallback positions
        self.fallback_coordinates = [
            (1713, 723),   # Primary coordinate
            (1700, 720),   # Slight variations
            (1720, 730),
            (1710, 715)
        ]
        self.fallback_index = 0
        
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
        
        self.logger.info("🚀 High-capacity automation initialized")
        self.logger.info(f"⚙️  Max windows per cycle: "
                         f"{self.max_windows_per_cycle}")
        self.logger.info(f"⚙️  Load threshold: {self.load_threshold}")
        self.logger.info(f"⚙️  Batch size: {self.window_batch_size}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"🛑 Received signal {signum}, shutting down...")
        self.running = False
    
    def check_system_resources(self) -> Tuple[bool, float]:
        """Check system resources with higher tolerance for many windows."""
        try:
            # Check CPU load average
            with open('/proc/loadavg', 'r') as f:
                load_avg = float(f.read().split()[0])
            
            # More tolerant threshold for environments with many windows
            if load_avg > self.load_threshold:
                msg = (f"⚠️  High system load: {load_avg:.1f}, "
                       "will use coordinate fallback")
                self.logger.warning(msg)
                return False, load_avg
            
            return True, load_avg
            
        except Exception as e:
            self.logger.debug(f"Could not check system load: {e}")
            return True, 0.0  # Assume OK if we can't check
    
    def get_vscode_windows_efficient(self) -> List[Dict]:
        """Get VS Code windows efficiently with caching and prioritization."""
        try:
            # Use cached window info if recent (within 30 seconds)
            current_time = time.time()
            if (hasattr(self, 'last_window_scan') and
                    current_time - self.last_window_scan < 30 and
                    hasattr(self, 'cached_windows')):
                return self.cached_windows
            
            result = subprocess.run(
                ["xwininfo", "-root", "-tree"], 
                capture_output=True, text=True, timeout=5
            )
            
            windows = []
            priority_windows = []  # Windows with 'continue' or 'chat' in title
            
            for line in result.stdout.split('\n'):
                if 'visual studio code' in line.lower():
                    try:
                        # Parse window information
                        parts = line.strip().split()
                        if len(parts) >= 3:
                            window_id = parts[0]
                            
                            # Extract geometry
                            for part in parts:
                                if 'x' in part and '+' in part:
                                    size_pos = part.split('+')
                                    size = size_pos[0].split('x')
                                    width, height = int(size[0]), int(size[1])
                                    x, y = int(size_pos[1]), int(size_pos[2])
                                    
                                    # Extract title
                                    title_start = line.find('"') + 1
                                    title_end = line.find('"', title_start)
                                    title = line[title_start:title_end] if title_start > 0 else "Unknown"
                                    
                                    window_info = {
                                        'id': window_id,
                                        'title': title,
                                        'x': x, 'y': y,
                                        'width': width, 'height': height,
                                        'priority': 0
                                    }
                                    
                                    # Prioritize windows likely to have Continue buttons
                                    title_lower = title.lower()
                                    if any(keyword in title_lower for keyword in ['continue', 'chat', 'copilot', 'assistant']):
                                        window_info['priority'] = 10
                                        priority_windows.append(window_info)
                                    elif any(keyword in title_lower for keyword in ['python', 'code', 'file']):
                                        window_info['priority'] = 5
                                        windows.append(window_info)
                                    else:
                                        window_info['priority'] = 1
                                        windows.append(window_info)
                                    
                                    break
                    except (ValueError, IndexError) as e:
                        self.logger.debug(f"Failed to parse window line: {e}")
                        continue
            
            # Combine priority windows first, then regular windows
            all_windows = priority_windows + windows
            
            # Limit to max windows per cycle but ensure we get priority ones
            final_windows = all_windows[:self.max_windows_per_cycle]
            
            # Cache the results
            self.cached_windows = final_windows
            self.last_window_scan = current_time
            
            if final_windows:
                priority_count = len([w for w in final_windows if w['priority'] >= 5])
                self.logger.debug(f"🔍 Found {len(final_windows)} VS Code windows ({priority_count} priority)")
            
            return final_windows
            
        except Exception as e:
            self.logger.error(f"Error getting VS Code windows: {e}")
            return []
    
    def use_coordinate_fallback(self) -> bool:
        """Use coordinate-based clicking when image processing isn't viable."""
        try:
            # Cycle through fallback coordinates
            coord_x, coord_y = self.fallback_coordinates[self.fallback_index]
            self.fallback_index = (self.fallback_index + 1) % len(self.fallback_coordinates)
            
            self.logger.info(f"🎯 Using coordinate fallback: ({coord_x}, {coord_y})")
            
            # Add small delay
            time.sleep(self.click_delay)
            
            # Perform click
            result = self.click_automator.click(coord_x, coord_y)
            
            if result.success:
                self.logger.info("✅ Coordinate fallback click successful!")
                self.successful_clicks += 1
                return True
            else:
                self.logger.warning(f"❌ Coordinate fallback failed: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in coordinate fallback: {e}")
            return False
    
    def process_windows_batch(self, windows: List[Dict]) -> int:
        """Process windows in batches for efficiency."""
        buttons_clicked = 0
        
        # Process windows in smaller batches
        for i in range(0, len(windows), self.window_batch_size):
            batch = windows[i:i + self.window_batch_size]
            
            for window in batch:
                try:
                    # For high-capacity mode, we primarily use coordinate fallback
                    # to avoid the overhead of image processing with many windows
                    
                    self.logger.debug(f"🔍 Processing window: {window['title'][:40]}...")
                    
                    # Focus the window briefly
                    subprocess.run([
                        "xdotool", "windowactivate", window['id']
                    ], capture_output=True, timeout=2)
                    
                    # Small delay to ensure window is active
                    time.sleep(0.1)
                    
                    # Use coordinate fallback for clicking
                    if self.use_coordinate_fallback():
                        buttons_clicked += 1
                        # Only click one button per cycle to avoid conflicts
                        return buttons_clicked
                    
                except Exception as e:
                    self.logger.debug(f"Error processing window {window['id']}: {e}")
                    continue
            
            # Small delay between batches
            if i + self.window_batch_size < len(windows):
                time.sleep(0.2)
        
        return buttons_clicked
    
    def automation_cycle(self) -> bool:
        """Perform one optimized automation cycle."""
        start_time = time.time()
        
        try:
            # Check system resources
            can_proceed, load_avg = self.check_system_resources()
            
            if not can_proceed:
                # Use coordinate fallback even under high load
                return self.use_coordinate_fallback()
            
            # Get VS Code windows efficiently
            windows = self.get_vscode_windows_efficient()
            
            if not windows:
                self.logger.debug("🔍 No VS Code windows found")
                return False
            
            self.logger.debug(f"🔍 Processing {len(windows)} VS Code windows (load: {load_avg:.1f})")
            
            # Process windows in batches
            buttons_clicked = self.process_windows_batch(windows)
            
            # Update performance stats
            cycle_time = time.time() - start_time
            self.performance_stats['avg_cycle_time'] = (
                (self.performance_stats['avg_cycle_time'] * self.cycle_count + cycle_time) / 
                (self.cycle_count + 1)
            )
            self.performance_stats['windows_processed'] += len(windows)
            
            # Adaptive interval adjustment
            if self.adaptive_intervals:
                if cycle_time > 5.0:  # If cycle takes too long
                    self.check_interval = min(self.check_interval * 1.1, 15.0)
                    self.logger.info(f"🐌 Increasing interval to {self.check_interval:.1f}s due to slow cycle")
                elif cycle_time < 2.0 and self.check_interval > 5.0:  # If cycle is fast
                    self.check_interval = max(self.check_interval * 0.9, 5.0)
                    self.logger.info(f"⚡ Decreasing interval to {self.check_interval:.1f}s due to fast cycle")
            
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
        """Run the high-capacity automation."""
        self.logger.info("🚀 Starting High-Capacity VS Code Continue Button Automation")
        self.logger.info(f"⚙️  Check interval: {self.check_interval:.1f} seconds")
        self.logger.info(f"⚙️  Max windows per cycle: {self.max_windows_per_cycle}")
        self.logger.info(f"⚙️  Load threshold: {self.load_threshold}")
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
                
                # Periodic cleanup
                if self.cycle_count % self.memory_cleanup_interval == 0:
                    self.cleanup_resources()
                
                # Periodic stats report
                if self.cycle_count % 20 == 0:
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
            self.logger.info(f"🏁 High-capacity automation stopped after {self.cycle_count} cycles")
            self.logger.info(f"📊 Final stats: {self.successful_clicks} successful clicks, {windows_proc} windows processed, avg {avg_time:.1f}s/cycle")


def main():
    """Main function."""
    print("🚀 VS Code Continue Button High-Capacity Automation")
    print("=" * 55)
    print()
    print("Optimized for environments with many VS Code windows:")
    print("- ✅ Handles 10+ windows per cycle")
    print("- ✅ Intelligent window prioritization")
    print("- ✅ Coordinate-based fallback under load")
    print("- ✅ Adaptive performance tuning")
    print("- ✅ Higher load tolerance")
    print("- ✅ Batch processing for efficiency")
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
