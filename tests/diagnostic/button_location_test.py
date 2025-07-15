#!/usr/bin/env python3
"""
Diagnostic test to show exactly where Continue buttons are being detected.
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
        result = subprocess.run(["xwininfo", "-root", "-tree"], capture_output=True, text=True)

        for line in result.stdout.split("\n"):
            if "visual studio code" in line.lower():
                parts = line.strip().split()
                if len(parts) >= 3:
                    window_id = parts[0]

                    # Extract geometry
                    for part in parts:
                        if "x" in part and "+" in part:
                            try:
                                size_pos = part.split("+")
                                size = size_pos[0].split("x")
                                width, height = int(size[0]), int(size[1])
                                x, y = int(size_pos[1]), int(size_pos[2])

                                return {
                                    "id": window_id,
                                    "x": x,
                                    "y": y,
                                    "width": width,
                                    "height": height,
                                }
                            except (ValueError, IndexError):
                                continue
    except Exception as e:
        print(f"Error getting window: {e}")

    return None


def capture_window_xwd(window_id):
    """Capture window using XWD."""
    try:
        temp_path = f"tmp/diagnostic_capture_{window_id.replace('0x', '')}.png"
        Path("tmp").mkdir(exist_ok=True)

        result = subprocess.run(
            ["bash", "-c", f"xwd -id {window_id} | convert xwd:- {temp_path}"], capture_output=True
        )

        if result.returncode == 0 and Path(temp_path).exists():
            return temp_path
        else:
            return None
    except Exception as e:
        print(f"XWD capture error: {e}")
        return None


def main():
    """Main diagnostic function."""
    print("🔍 VS Code Continue Button Location Diagnostic")
    print("=" * 50)

    # Get VS Code window
    window = capture_vscode_window()
    if not window:
        print("❌ No VS Code window found")
        return 1

    print(f"Found VS Code window: {window['id']} at " f"({window['x']}, {window['y']})")

    # Capture the window
    image_path = capture_window_xwd(window["id"])
    if not image_path:
        print("❌ Failed to capture window")
        return 1

    print(f"Captured window to: {image_path}")

    # Load image and find buttons
    image = Image.open(image_path)
    print(f"Image size: {image.width}x{image.height}")

    # Calculate chat panel area
    chat_panel_left = int(image.width * 0.55)
    chat_panel_bottom = int(image.height * 0.75)
    avoid_top = int(image.height * 0.1)

    print(f"Chat panel area: x > {chat_panel_left}, y > {max(chat_panel_bottom, avoid_top)}")

    # Find buttons
    button_finder = ButtonFinder()
    buttons = button_finder.find_continue_buttons(image, 0, 0)

    print(f"\n🎯 Found {len(buttons)} Continue buttons:")
    for i, button in enumerate(buttons):
        abs_x = window["x"] + button.center_x
        abs_y = window["y"] + button.center_y
        print(f"  {i+1}. ({button.x}, {button.y}) -> screen ({abs_x}, {abs_y})")
        print(f"      Size: {button.width}x{button.height}, Confidence: {button.confidence:.2f}")
        print(f"      Method: {button.method}, Text: '{button.text}'")
        print()

    # Create annotated image
    if buttons:
        draw = ImageDraw.Draw(image)

        # Draw chat panel area
        draw.rectangle(
            [chat_panel_left, max(chat_panel_bottom, avoid_top), image.width, image.height],
            outline="yellow",
            width=2,
        )

        # Draw detected buttons
        for i, button in enumerate(buttons):
            color = "green" if i == 0 else "orange"  # Best button in green
            draw.rectangle(
                [button.x, button.y, button.x + button.width, button.y + button.height],
                outline=color,
                width=3,
            )

            # Add label
            draw.text((button.x, button.y - 20), f"#{i+1} {button.confidence:.2f}", fill=color)

        annotated_path = "tmp/buttons_annotated.png"
        image.save(annotated_path)
        print(f"💾 Saved annotated image to: {annotated_path}")
        print("🟡 Yellow rectangle = chat panel area")
        print("🟢 Green rectangle = best button (will be clicked)")
        print("🟠 Orange rectangles = other detected buttons")

    return 0


if __name__ == "__main__":
    sys.exit(main())
