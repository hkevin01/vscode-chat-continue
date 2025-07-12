#!/usr/bin/env python3
"""
Debug test without chat panel filtering to see ALL button detections.
"""

import subprocess
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PIL import Image

from core.button_finder import ButtonFinder


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
        temp_path = f"tmp/debug_no_filter_{window_id.replace('0x', '')}.png"
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
    print("🔍 Debug Test - ALL Button Detections (No Filtering)")
    print("=" * 60)
    
    # Get VS Code window
    window = get_vscode_window()
    if not window:
        print("❌ No VS Code window found")
        return 1
    
    print(f"📱 Found window: {window['id']} ({window['width']}x{window['height']})")
    
    # Capture window
    image_path = capture_window_xwd(window['id'])
    if not image_path:
        print("❌ Failed to capture window")
        return 1
    
    print(f"📸 Captured: {image_path}")
    
    # Load image
    image = Image.open(image_path)
    print(f"🖼️  Image: {image.width}x{image.height}")
    
    # Create button finder and monkey-patch to disable filtering
    button_finder = ButtonFinder()
    
    # Temporarily override the chat panel filter to return all buttons
    original_filter = button_finder._filter_chat_panel_buttons
    def no_filter(buttons, width, height):
        print(f"🔓 Filter disabled - returning all {len(buttons)} buttons")
        return buttons
    
    button_finder._filter_chat_panel_buttons = no_filter
    
    # Find buttons
    print("\n🔍 Searching for Continue buttons (no filtering)...")
    buttons = button_finder.find_continue_buttons(image, 0, 0)
    
    if buttons:
        print(f"\n🎯 Found {len(buttons)} button(s) total:")
        
        for i, button in enumerate(buttons):
            abs_x = window['x'] + button.center_x
            abs_y = window['y'] + button.center_y
            
            print(f"\n   {i+1}. Button at ({button.x}, {button.y}) "
                  f"-> screen ({abs_x}, {abs_y})")
            print(f"      Size: {button.width}x{button.height}")
            print(f"      Confidence: {button.confidence:.2f}")
            print(f"      Method: {button.method}")
            print(f"      Text: '{button.text}'")
            
            # Check if this would be in chat panel area
            chat_panel_left = int(image.width * 0.55)
            chat_panel_bottom = int(image.height * 0.75)
            avoid_top = int(image.height * 0.1)
            
            in_chat_area = (button.x > chat_panel_left and
                           button.y > max(chat_panel_bottom, avoid_top) and
                           button.y < image.height - 20)
            
            print(f"      Would pass chat filter: {'✅ YES' if in_chat_area else '❌ NO'}")
    else:
        print("❌ No buttons detected at all")
        print("\nPossible issues:")
        print("- No Continue button currently visible")
        print("- OCR/detection methods not working")
        print("- Button appearance changed")
    
    # Restore original filter
    button_finder._filter_chat_panel_buttons = original_filter
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
