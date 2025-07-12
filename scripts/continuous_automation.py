#!/usr/bin/env python3
"""
Continuous VS Code Continue Button Automation.
Runs in background and automatically clicks Continue buttons when they appear.
"""

import logging
import signal
import subprocess
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PIL import Image

from core.button_finder import ButtonFinder
from core.click_automator import ClickAutomator
from core.config_manager import ConfigManager
from utils.audio_suppressor import enable_audio_suppression


class ContinuousAutomation:
    """Continuous automation for VS Code Continue buttons."""
    
    def __init__(self):
        """Initialize the automation."""
        self.running = False
        self.button_finder = ButtonFinder()
        self.click_automator = ClickAutomator()
        self.config = ConfigManager()
        
        # Configuration
        self.check_interval = self.config.get('automation.interval_seconds', 3.0)
        self.max_retries = self.config.get('automation.max_retries', 3)
        self.click_delay = self.config.get('automation.click_delay_ms', 100) / 1000.0
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/continuous_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Ensure audio is suppressed
        enable_audio_suppression()
        self.logger.info("Audio suppression enabled")
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def get_vscode_windows(self):
        """Get VS Code windows using xwininfo, prioritizing computer-vision window."""
        try:
            result = subprocess.run(
                ["xwininfo", "-root", "-tree"], 
                capture_output=True, text=True
            )
            
            windows = []
            computer_vision_window = None
            
            for line in result.stdout.split('\n'):
                if 'visual studio code' in line.lower():
                    # Parse line format: 0xID "Title": ("class" "Class") WIDTHxHEIGHT+X+Y
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        window_id = parts[0]
                        
                        # Extract geometry (WIDTHxHEIGHT+X+Y)
                        for part in parts:
                            if 'x' in part and '+' in part:
                                try:
                                    # Parse format like "1680x1050+104+0"
                                    size_pos = part.split('+')
                                    size = size_pos[0].split('x')
                                    width, height = int(size[0]), int(size[1])
                                    x, y = int(size_pos[1]), int(size_pos[2])
                                    
                                    # Extract title (between quotes)
                                    title_start = line.find('"') + 1
                                    title_end = line.find('"', title_start)
                                    title = line[title_start:title_end] if title_start > 0 else "Unknown"
                                    
                                    window_info = {
                                        'id': window_id,
                                        'title': title,
                                        'x': x, 'y': y,
                                        'width': width, 'height': height
                                    }
                                    
                                    # Prioritize computer-vision window
                                    if 'computer-vision' in title.lower():
                                        self.logger.info(f"Found computer-vision window: {window_id}")
                                        computer_vision_window = window_info
                                    
                                    windows.append(window_info)
                                    break
                                except (ValueError, IndexError):
                                    continue
            
            # If we found a computer-vision window, prioritize it
            if computer_vision_window:
                # Move computer-vision window to front of list
                windows = [w for w in windows if w['id'] != computer_vision_window['id']]
                windows.insert(0, computer_vision_window)
                self.logger.info("Prioritizing computer-vision window for Continue button detection")
            
            return windows
        except Exception as e:
            self.logger.error(f"Error getting windows: {e}")
            return []
    
    def capture_window_xwd(self, window_id):
        """Capture window using XWD."""
        try:
            temp_path = f"tmp/automation_capture_{window_id.replace('0x', '')}.png"
            Path("tmp").mkdir(exist_ok=True)
            
            result = subprocess.run([
                "bash", "-c", 
                f"xwd -id {window_id} | convert xwd:- {temp_path}"
            ], capture_output=True)
            
            if result.returncode == 0 and Path(temp_path).exists():
                return temp_path
            else:
                return None
        except Exception as e:
            self.logger.debug(f"XWD capture error: {e}")
            return None
    
    def process_window(self, window):
        """Process a single VS Code window for Continue buttons."""
        self.logger.debug(f"Processing window: {window['title'][:50]}...")
        
        # Capture window
        image_path = self.capture_window_xwd(window['id'])
        if not image_path:
            self.logger.debug(f"Failed to capture window {window['id']}")
            return False
        
        try:
            # Load image
            image = Image.open(image_path)
            
            # Find Continue buttons
            buttons = self.button_finder.find_continue_buttons(image, 0, 0)
            
            if buttons:
                self.logger.info(f"Found {len(buttons)} Continue button(s) in window")
                
                # Click the best button
                best_button = buttons[0]  # Highest confidence first
                
                # Calculate absolute screen coordinates
                abs_x = window['x'] + best_button.center_x
                abs_y = window['y'] + best_button.center_y
                
                self.logger.info(f"Clicking Continue button at ({abs_x}, {abs_y})")
                
                # Add small delay before clicking
                time.sleep(self.click_delay)
                
                # Perform click
                result = self.click_automator.click(abs_x, abs_y)
                
                if result.success:
                    self.logger.info("✅ Successfully clicked Continue button!")
                    return True
                else:
                    self.logger.warning(f"Click failed: {result}")
            else:
                self.logger.debug("No Continue buttons found in this window")
                
        except Exception as e:
            self.logger.error(f"Error processing window: {e}")
        
        finally:
            # Clean up temp file
            try:
                Path(image_path).unlink(missing_ok=True)
            except:
                pass
        
        return False
    
    def automation_cycle(self):
        """Perform one automation cycle."""
        try:
            # Get VS Code windows
            windows = self.get_vscode_windows()
            
            if not windows:
                self.logger.debug("No VS Code windows found")
                return False
            
            self.logger.debug(f"Found {len(windows)} VS Code window(s)")
            
            # Process each window
            buttons_clicked = False
            for window in windows:
                if self.process_window(window):
                    buttons_clicked = True
                    # Only click one button per cycle to avoid conflicts
                    break
            
            return buttons_clicked
            
        except Exception as e:
            self.logger.error(f"Error in automation cycle: {e}")
            return False
    
    def run(self):
        """Run the continuous automation."""
        self.logger.info("🚀 Starting VS Code Continue Button Automation")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        self.logger.info("Press Ctrl+C to stop")
        
        self.running = True
        cycles = 0
        buttons_clicked = 0
        
        try:
            while self.running:
                cycles += 1
                
                if self.automation_cycle():
                    buttons_clicked += 1
                    self.logger.info(f"Cycle {cycles}: Button clicked! (Total: {buttons_clicked})")
                else:
                    self.logger.debug(f"Cycle {cycles}: No buttons found")
                
                # Wait for next cycle
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.running = False
            self.logger.info(f"🛑 Automation stopped after {cycles} cycles, {buttons_clicked} buttons clicked")

def main():
    """Main function."""
    print("🤖 VS Code Continue Button Continuous Automation")
    print("=" * 50)
    print()
    print("This will continuously monitor VS Code windows and")
    print("automatically click Continue buttons when they appear.")
    print()
    print("Features:")
    print("- ✅ Silent operation (no beeps)")
    print("- ✅ Blue button detection")
    print("- ✅ Multiple window support")
    print("- ✅ Automatic retry logic")
    print("- ✅ Logging to file and console")
    print()
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    try:
        automation = ContinuousAutomation()
        automation.run()
    except Exception as e:
        print(f"Failed to start automation: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
