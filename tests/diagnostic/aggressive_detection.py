#!/usr/bin/env python3
"""
Aggressive diagnostic to see ALL button detections before filtering.
"""

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.button_finder import ButtonFinder


def capture_vscode_window():
    """Capture the first VS Code window."""
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
        temp_path = f"tmp/aggressive_capture_{window_id.replace('0x', '')}.png"
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
    """Main diagnostic function."""
    print("🔍 AGGRESSIVE Button Detection Diagnostic")
    print("=" * 50)
    
    # Get VS Code window
    window = capture_vscode_window()
    if not window:
        print("❌ No VS Code window found")
        return 1
    
    print(f"Found VS Code window: {window['id']}")
    print(f"Window geometry: {window['width']}x{window['height']} "
          f"at ({window['x']}, {window['y']})")
    
    # Capture the window
    image_path = capture_window_xwd(window['id'])
    if not image_path:
        print("❌ Failed to capture window")
        return 1
    
    print(f"Captured window to: {image_path}")
    
    # Load image
    image = Image.open(image_path)
    print(f"Image size: {image.width}x{image.height}")
    
    # Create button finder and test each method individually
    button_finder = ButtonFinder()
    
    # Test each detection method separately
    print("\n🔍 TESTING EACH DETECTION METHOD:")
    
    all_buttons = []
    
    # OCR detection
    try:
        ocr_buttons = button_finder._find_buttons_ocr(image, 0, 0)
        print(f"📝 OCR detection: {len(ocr_buttons)} buttons")
        for i, btn in enumerate(ocr_buttons):
            print(f"   {i+1}. ({btn.x},{btn.y}) {btn.width}x{btn.height} "
                  f"conf:{btn.confidence:.2f} text:'{btn.text}'")
        all_buttons.extend(ocr_buttons)
    except Exception as e:
        print(f"📝 OCR detection failed: {e}")
    
    # Blue button detection
    try:
        blue_buttons = button_finder._find_blue_buttons(image, 0, 0)
        print(f"🔵 Blue button detection: {len(blue_buttons)} buttons")
        for i, btn in enumerate(blue_buttons):
            print(f"   {i+1}. ({btn.x},{btn.y}) {btn.width}x{btn.height} "
                  f"conf:{btn.confidence:.2f} text:'{btn.text}'")
        all_buttons.extend(blue_buttons)
    except Exception as e:
        print(f"🔵 Blue button detection failed: {e}")
    
    # Color detection
    try:
        color_buttons = button_finder._find_buttons_color(image, 0, 0)
        print(f"🎨 Color detection: {len(color_buttons)} buttons")
        for i, btn in enumerate(color_buttons):
            print(f"   {i+1}. ({btn.x},{btn.y}) {btn.width}x{btn.height} "
                  f"conf:{btn.confidence:.2f} text:'{btn.text}'")
        all_buttons.extend(color_buttons)
    except Exception as e:
        print(f"🎨 Color detection failed: {e}")
    
    print(f"\n📊 TOTAL RAW DETECTIONS: {len(all_buttons)}")
    
    # Now test chat panel filtering
    chat_panel_left = int(image.width * 0.55)
    chat_panel_bottom = int(image.height * 0.75)
    avoid_top = int(image.height * 0.1)
    
    print(f"\n📍 CHAT PANEL AREA:")
    print(f"   Left boundary: x > {chat_panel_left}")
    print(f"   Top boundary: y > {max(chat_panel_bottom, avoid_top)}")
    print(f"   Bottom boundary: y < {image.height - 20}")
    
    # Check each button against chat panel area
    filtered_buttons = []
    for btn in all_buttons:
        in_area = (btn.x > chat_panel_left and 
                  btn.y > max(chat_panel_bottom, avoid_top) and 
                  btn.y < image.height - 20)
        
        print(f"   Button at ({btn.x},{btn.y}): {'✅ IN' if in_area else '❌ OUT'}")
        if in_area:
            filtered_buttons.append(btn)
    
    print(f"\n✅ BUTTONS AFTER FILTERING: {len(filtered_buttons)}")
    
    # Create annotated image
    if all_buttons:
        draw = ImageDraw.Draw(image)
        
        # Draw chat panel area
        draw.rectangle([chat_panel_left, max(chat_panel_bottom, avoid_top),
                       image.width, image.height - 20], 
                      outline="yellow", width=3)
        
        # Draw all detected buttons
        for i, button in enumerate(all_buttons):
            in_area = (button.x > chat_panel_left and 
                      button.y > max(chat_panel_bottom, avoid_top) and 
                      button.y < image.height - 20)
            
            color = "green" if in_area else "red"
            draw.rectangle([button.x, button.y,
                          button.x + button.width, 
                          button.y + button.height],
                         outline=color, width=2)
            
            # Add label
            draw.text((button.x, button.y - 15), 
                     f"{i+1}", fill=color)
        
        annotated_path = "tmp/aggressive_annotated.png"
        image.save(annotated_path)
        print(f"\n💾 Saved annotated image: {annotated_path}")
        print("🟡 Yellow rectangle = chat panel target area")
        print("🟢 Green rectangles = buttons in target area")
        print("🔴 Red rectangles = buttons outside target area")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
