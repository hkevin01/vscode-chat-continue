#!/usr/bin/env python3
"""
Multi-window VS Code Continue button detection.
Captures both VS Code windows to find which has the Continue button.
"""

import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PIL import Image

from core.button_finder import ButtonFinder


def get_all_vscode_windows():
    """Get all VS Code windows."""
    try:
        result = subprocess.run(
            ["xwininfo", "-root", "-tree"],
            capture_output=True, text=True
        )
        
        windows = []
        for line in result.stdout.split('\n'):
            if 'visual studio code' in line.lower():
                parts = line.strip().split()
                if len(parts) >= 3:
                    window_id = parts[0]
                    
                    # Extract title
                    if '"' in line:
                        title_start = line.find('"') + 1
                        title_end = line.find('"', title_start)
                        title = line[title_start:title_end]
                    else:
                        title = "Unknown"
                    
                    # Extract geometry
                    for part in parts:
                        if 'x' in part and '+' in part:
                            try:
                                size_pos = part.split('+')
                                size = size_pos[0].split('x')
                                width, height = int(size[0]), int(size[1])
                                x, y = int(size_pos[1]), int(size_pos[2])
                                
                                windows.append({
                                    'id': window_id,
                                    'title': title,
                                    'x': x, 'y': y,
                                    'width': width, 'height': height
                                })
                                break
                            except (ValueError, IndexError):
                                continue
        
        return windows
    except Exception as e:
        print(f"Error getting windows: {e}")
        return []


def capture_window_xwd(window_id, filename):
    """Capture window using XWD."""
    try:
        Path("tmp").mkdir(exist_ok=True)
        temp_path = f"tmp/{filename}"
        
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


def test_window_for_buttons(window, image_path):
    """Test a window for Continue buttons."""
    print(f"\n🔍 Testing window: {window['title'][:60]}...")
    print(f"   ID: {window['id']}")
    print(f"   Size: {window['width']}x{window['height']}")
    print(f"   Position: ({window['x']}, {window['y']})")
    
    try:
        # Load image
        image = Image.open(image_path)
        print(f"   Image: {image.width}x{image.height}")
        
        # Find buttons
        button_finder = ButtonFinder()
        buttons = button_finder.find_continue_buttons(image, 0, 0)
        
        if buttons:
            print(f"   🎯 Found {len(buttons)} Continue button(s)!")
            
            for i, button in enumerate(buttons):
                abs_x = window['x'] + button.center_x
                abs_y = window['y'] + button.center_y
                
                print(f"      {i+1}. Button at ({button.x}, {button.y}) "
                      f"-> screen ({abs_x}, {abs_y})")
                print(f"         Size: {button.width}x{button.height}")
                print(f"         Confidence: {button.confidence:.2f}")
                print(f"         Method: {button.method}")
                print(f"         Text: '{button.text}'")
            
            return True, buttons
        else:
            print("   ❌ No Continue buttons found")
            return False, []
            
    except Exception as e:
        print(f"   ❌ Error testing window: {e}")
        return False, []


def main():
    """Main function."""
    print("🔍 Multi-Window VS Code Continue Button Detection")
    print("=" * 60)
    
    # Get all VS Code windows
    windows = get_all_vscode_windows()
    
    if not windows:
        print("❌ No VS Code windows found")
        return 1
    
    print(f"📱 Found {len(windows)} VS Code window(s):")
    for i, window in enumerate(windows):
        print(f"  {i+1}. {window['id']}: {window['title'][:70]}...")
    
    print("\n📸 Capturing all windows...")
    
    # Test each window
    button_windows = []
    
    for i, window in enumerate(windows):
        filename = f"window_{i+1}_{window['id'].replace('0x', '')}.png"
        
        # Capture window
        image_path = capture_window_xwd(window['id'], filename)
        
        if image_path:
            print(f"✅ Captured window {i+1} to: {image_path}")
            
            # Test for buttons
            has_buttons, buttons = test_window_for_buttons(window, image_path)
            
            if has_buttons:
                button_windows.append({
                    'window': window,
                    'buttons': buttons,
                    'image_path': image_path
                })
        else:
            print(f"❌ Failed to capture window {i+1}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total windows: {len(windows)}")
    print(f"   Windows with Continue buttons: {len(button_windows)}")
    
    if button_windows:
        print(f"\n🎯 Windows with Continue buttons:")
        for i, bw in enumerate(button_windows):
            window = bw['window']
            buttons = bw['buttons']
            print(f"   {i+1}. {window['title'][:50]}...")
            print(f"      ID: {window['id']}")
            print(f"      Buttons: {len(buttons)}")
            print(f"      Image: {bw['image_path']}")
            
            # Show best button coordinates
            if buttons:
                best_button = buttons[0]
                abs_x = window['x'] + best_button.center_x
                abs_y = window['y'] + best_button.center_y
                print(f"      Best button at screen: ({abs_x}, {abs_y})")
        
        print(f"\n💡 The automation should target the window with Continue buttons.")
        print(f"   You can manually test clicking by running:")
        print(f"   python -c \"")
        print(f"import sys; sys.path.insert(0, 'src')")
        print(f"from core.click_automator import ClickAutomator")
        print(f"ca = ClickAutomator()")
        best_window = button_windows[0]
        best_button = best_window['buttons'][0]
        abs_x = best_window['window']['x'] + best_button.center_x
        abs_y = best_window['window']['y'] + best_button.center_y
        print(f"ca.click({abs_x}, {abs_y})")
        print(f"\"")
        
    else:
        print("\n❌ No Continue buttons found in any window.")
        print("   Possible reasons:")
        print("   - No Continue button currently visible")
        print("   - Button appearance doesn't match detection patterns")
        print("   - Need to generate a longer Copilot response")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
