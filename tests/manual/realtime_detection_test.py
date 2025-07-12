#!/usr/bin/env python3
"""
Real-time Continue button detection test.
Shows exactly what happens during detection.
"""

import subprocess
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PIL import Image

from core.button_finder import ButtonFinder
from core.click_automator import ClickAutomator


def get_vscode_window():
    """Get the first VS Code window."""
    try:
        result = subprocess.run(
            ["xwininfo", "-root", "-tree"],
            capture_output=True, text=True
        )
        
        for line in result.stdout.split('\n'):
            if 'visual studio code' in line.lower():
                parts = line.strip().split()
                if len(parts) >= 3:
                    window_id = parts[0]
                    
                    for part in parts:
                        if 'x' in part and '+' in part:
                            try:
                                size_pos = part.split('+')
                                size = size_pos[0].split('x')
                                width, height = int(size[0]), int(size[1])
                                x, y = int(size_pos[1]), int(size_pos[2])
                                
                                return {
                                    'id': window_id,
                                    'x': x, 'y': y,
                                    'width': width, 'height': height
                                }
                            except (ValueError, IndexError):
                                continue
    except Exception as e:
        print(f"Error getting window: {e}")
    
    return None


def capture_window_xwd(window_id):
    """Capture window using XWD."""
    try:
        temp_path = f"tmp/realtime_capture_{window_id.replace('0x', '')}.png"
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
        print(f"XWD capture error: {e}")
        return None


def main():
    """Main function."""
    print("🔄 Real-time Continue Button Detection Test")
    print("=" * 50)
    print("This will continuously scan for Continue buttons...")
    print("Press Ctrl+C to stop\n")
    
    button_finder = ButtonFinder()
    click_automator = ClickAutomator()
    
    try:
        cycle = 0
        while True:
            cycle += 1
            print(f"\n--- Cycle {cycle} ---")
            
            # Get VS Code window
            window = get_vscode_window()
            if not window:
                print("❌ No VS Code window found")
                time.sleep(3)
                continue
            
            print(f"📱 Found window: {window['id']} at "
                  f"({window['x']}, {window['y']})")
            
            # Capture window
            image_path = capture_window_xwd(window['id'])
            if not image_path:
                print("❌ Failed to capture window")
                time.sleep(3)
                continue
            
            print(f"📸 Captured: {image_path}")
            
            # Load image and find buttons
            image = Image.open(image_path)
            print(f"🖼️  Image: {image.width}x{image.height}")
            
            # Find buttons with detailed logging
            print("🔍 Searching for Continue buttons...")
            buttons = button_finder.find_continue_buttons(image, 0, 0)
            
            if buttons:
                print(f"🎯 Found {len(buttons)} Continue button(s)!")
                
                for i, button in enumerate(buttons):
                    abs_x = window['x'] + button.center_x
                    abs_y = window['y'] + button.center_y
                    
                    print(f"   {i+1}. Button at ({button.x}, {button.y}) "
                          f"-> screen ({abs_x}, {abs_y})")
                    print(f"      Size: {button.width}x{button.height}")
                    print(f"      Confidence: {button.confidence:.2f}")
                    print(f"      Method: {button.method}")
                    print(f"      Text: '{button.text}'")
                
                # Try clicking the best button
                best_button = buttons[0]
                abs_x = window['x'] + best_button.center_x
                abs_y = window['y'] + best_button.center_y
                
                print(f"\n🖱️  Attempting to click at ({abs_x}, {abs_y})...")
                
                result = click_automator.click(abs_x, abs_y)
                
                if result.success:
                    print("✅ Click successful!")
                    print("Waiting 5 seconds before next scan...")
                    time.sleep(5)
                else:
                    print(f"❌ Click failed: {result.error}")
            else:
                print("❌ No Continue buttons detected")
            
            # Clean up
            try:
                Path(image_path).unlink(missing_ok=True)
            except:
                pass
            
            print("⏰ Waiting 3 seconds...")
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
