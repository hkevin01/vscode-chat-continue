#!/usr/bin/env python3
"""
Target specific VS Code window for Continue button detection.
"""

import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PIL import Image

from core.button_finder import ButtonFinder
from core.click_automator import ClickAutomator


def main():
    """Target the computer-vision VS Code window."""
    print("🎯 Targeting Computer-Vision VS Code Window")
    print("=" * 50)

    # Get VS Code windows
    try:
        result = subprocess.run(["xwininfo", "-root", "-tree"], capture_output=True, text=True)

        target_window = None

        for line in result.stdout.split("\n"):
            if "visual studio code" in line.lower():
                parts = line.strip().split()
                if len(parts) >= 3:
                    window_id = parts[0]

                    # Check if this is the computer-vision window
                    if "computer-vision" in line.lower():
                        print(f"🎯 Found computer-vision window: {window_id}")

                        # Extract geometry
                        for part in parts:
                            if "x" in part and "+" in part:
                                try:
                                    size_pos = part.split("+")
                                    size = size_pos[0].split("x")
                                    width, height = int(size[0]), int(size[1])
                                    x, y = int(size_pos[1]), int(size_pos[2])

                                    target_window = {
                                        "id": window_id,
                                        "x": x,
                                        "y": y,
                                        "width": width,
                                        "height": height,
                                    }
                                    break
                                except (ValueError, IndexError):
                                    continue
                        break

        if not target_window:
            print("❌ Computer-vision VS Code window not found")
            print("Available windows:")
            for line in result.stdout.split("\n"):
                if "visual studio code" in line.lower():
                    print(f"  {line.strip()}")
            return 1

        print(f"📱 Target window: {target_window['id']}")
        print(f"   Size: {target_window['width']}x{target_window['height']}")
        print(f"   Position: ({target_window['x']}, {target_window['y']})")

        # Capture the target window
        Path("tmp").mkdir(exist_ok=True)
        temp_path = f"tmp/target_window_{target_window['id'].replace('0x', '')}.png"

        result = subprocess.run(
            ["bash", "-c", f"xwd -id {target_window['id']} | convert xwd:- {temp_path}"],
            capture_output=True,
        )

        if result.returncode != 0 or not Path(temp_path).exists():
            print("❌ Failed to capture target window")
            return 1

        print(f"📸 Captured: {temp_path}")

        # Load and test for buttons
        image = Image.open(temp_path)
        print(f"🖼️  Image: {image.width}x{image.height}")

        button_finder = ButtonFinder()
        buttons = button_finder.find_continue_buttons(image, 0, 0)

        if buttons:
            print(f"🎯 Found {len(buttons)} Continue button(s)!")

            for i, button in enumerate(buttons):
                abs_x = target_window["x"] + button.center_x
                abs_y = target_window["y"] + button.center_y

                print(f"\n   Button {i+1}:")
                print(f"     Window coords: ({button.x}, {button.y})")
                print(f"     Screen coords: ({abs_x}, {abs_y})")
                print(f"     Size: {button.width}x{button.height}")
                print(f"     Confidence: {button.confidence:.2f}")
                print(f"     Method: {button.method}")
                print(f"     Text: '{button.text}'")

            # Try clicking the best button
            best_button = buttons[0]
            abs_x = target_window["x"] + best_button.center_x
            abs_y = target_window["y"] + best_button.center_y

            print(f"\n🖱️  Attempting to click best button at ({abs_x}, {abs_y})...")

            click_automator = ClickAutomator()
            result = click_automator.click(abs_x, abs_y)

            if result.success:
                print("✅ Successfully clicked Continue button!")
                return 0
            else:
                print(f"❌ Click failed: {result.error}")
                return 1
        else:
            print("❌ No Continue buttons found in target window")
            print("   The computer-vision window may not have a Continue button visible")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
