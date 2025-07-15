#!/usr/bin/env python3
"""
Test the specific Continue button detection for the blue VS Code button.
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
    """Test the specific Continue button detection."""
    print("🎯 Testing Specific Continue Button Detection")
    print("=" * 60)

    # Get computer-vision VS Code window
    try:
        result = subprocess.run(["xwininfo", "-root", "-tree"], capture_output=True, text=True)

        cv_window = None
        for line in result.stdout.split("\n"):
            if "visual studio code" in line.lower():
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

                    for part in parts:
                        if "x" in part and "+" in part:
                            try:
                                size_pos = part.split("+")
                                size = size_pos[0].split("x")
                                width, height = int(size[0]), int(size[1])
                                x, y = int(size_pos[1]), int(size_pos[2])

                                cv_window = {
                                    "id": window_id,
                                    "title": title,
                                    "x": x,
                                    "y": y,
                                    "width": width,
                                    "height": height,
                                }
                                break
                            except (ValueError, IndexError):
                                continue
                    break

        if not cv_window:
            print("❌ Computer-vision VS Code window not found")
            print("Available windows:")
            for line in result.stdout.split("\n"):
                if "visual studio code" in line.lower():
                    print(f"  {line.strip()}")
            return 1

        print(f"✅ Found VS Code window: {cv_window['id']}")
        print(f"   Title: {cv_window['title']}")
        print(f"   Size: {cv_window['width']}x{cv_window['height']}")
        print(f"   Position: ({cv_window['x']}, {cv_window['y']})")

        # Capture the window
        Path("tmp").mkdir(exist_ok=True)
        image_path = f"tmp/specific_test_{cv_window['id'].replace('0x', '')}.png"

        result = subprocess.run(
            ["bash", "-c", f"xwd -id {cv_window['id']} | convert xwd:- {image_path}"],
            capture_output=True,
        )

        if result.returncode != 0 or not Path(image_path).exists():
            print("❌ Failed to capture window")
            return 1

        print(f"📸 Captured: {image_path}")

        # Load image and test specific detection
        image = Image.open(image_path)
        print(f"🖼️  Image: {image.width}x{image.height}")

        # Test the new specific detection method
        print("\n🔍 Testing specific Continue button detection...")
        button_finder = ButtonFinder()

        # Test the specific method directly
        specific_buttons = button_finder._detect_specific_continue_button(image, 0, 0)

        print(f"🎯 Specific detection found: {len(specific_buttons)} buttons")

        if specific_buttons:
            for i, button in enumerate(specific_buttons):
                abs_x = cv_window["x"] + button.center_x
                abs_y = cv_window["y"] + button.center_y

                print(f"\n   Button {i+1}:")
                print(f"     Position: ({button.x}, {button.y}) " f"-> screen ({abs_x}, {abs_y})")
                print(f"     Size: {button.width}x{button.height}")
                print(f"     Confidence: {button.confidence:.2f}")
                print(f"     Method: {button.method}")
                print(f"     Text: '{button.text}'")

            # Test full detection pipeline
            print(f"\n🔍 Testing full detection pipeline...")
            all_buttons = button_finder.find_continue_buttons(image, 0, 0)
            print(f"Full pipeline found: {len(all_buttons)} buttons")

            if all_buttons:
                best_button = all_buttons[0]
                abs_x = cv_window["x"] + best_button.center_x
                abs_y = cv_window["y"] + best_button.center_y

                print(f"\n🖱️  Best button to click:")
                print(
                    f"   Position: ({best_button.x}, {best_button.y}) "
                    f"-> screen ({abs_x}, {abs_y})"
                )
                print(f"   Confidence: {best_button.confidence:.2f}")
                print(f"   Method: {best_button.method}")

                # Ask if user wants to test clicking
                response = input(f"\nClick this button? (y/n): ")
                if response.lower() == "y":
                    print(f"🖱️  Clicking at ({abs_x}, {abs_y})...")

                    click_automator = ClickAutomator()
                    result = click_automator.click(abs_x, abs_y)

                    if result.success:
                        print("✅ Successfully clicked Continue button!")
                    else:
                        print(f"❌ Click failed: {result.error}")
                else:
                    print("Skipping click test")
        else:
            print("❌ No specific Continue buttons detected")
            print("\nPossible reasons:")
            print("1. No Continue button currently visible")
            print("2. Button color doesn't match expected blue range")
            print("3. Button size outside expected range (50-100w, 20-45h)")
            print("4. OCR not recognizing 'Continue' text")

            print(f"\n🔍 Debug info:")
            print(f"   Image saved: {image_path}")
            print("   Check this image manually for blue Continue buttons")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
