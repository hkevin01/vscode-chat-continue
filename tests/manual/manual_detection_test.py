#!/usr/bin/env python3
"""
Manual Continue button test.
This will help debug if Continue buttons are actually visible.
"""

import subprocess
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PIL import Image

from core.button_finder import ButtonFinder


def main():
    """Manual test for Continue button detection."""
    print("🔍 Manual Continue Button Detection Test")
    print("=" * 50)
    print()
    print("This test will help debug Continue button detection.")
    print()
    print("STEPS TO TEST:")
    print("1. Open VS Code with Copilot chat panel")
    print("2. Start a conversation that will show a Continue button")
    print("3. Make sure the Continue button is visible")
    print("4. Press Enter here to capture and analyze")
    print()

    input("Press Enter when Continue button is visible...")

    # Capture current VS Code window
    print("\n📸 Capturing VS Code window...")

    try:
        # Get VS Code window
        result = subprocess.run(["xwininfo", "-root", "-tree"], capture_output=True, text=True)

        window_id = None
        for line in result.stdout.split("\n"):
            if "visual studio code" in line.lower():
                parts = line.strip().split()
                if len(parts) >= 3:
                    window_id = parts[0]
                    break

        if not window_id:
            print("❌ No VS Code window found")
            return 1

        # Capture window
        Path("tmp").mkdir(exist_ok=True)
        temp_path = "tmp/manual_test_capture.png"

        result = subprocess.run(
            ["bash", "-c", f"xwd -id {window_id} | convert xwd:- {temp_path}"], capture_output=True
        )

        if result.returncode != 0 or not Path(temp_path).exists():
            print("❌ Failed to capture window")
            return 1

        print(f"✅ Captured to: {temp_path}")

        # Load and analyze image
        image = Image.open(temp_path)
        print(f"🖼️  Image size: {image.width}x{image.height}")

        # Test button detection
        print("\n🔍 Running button detection...")
        button_finder = ButtonFinder()
        buttons = button_finder.find_continue_buttons(image, 0, 0)

        if buttons:
            print(f"🎯 Found {len(buttons)} button(s):")

            for i, button in enumerate(buttons):
                print(f"\n   Button {i+1}:")
                print(f"     Position: ({button.x}, {button.y})")
                print(f"     Size: {button.width}x{button.height}")
                print(f"     Confidence: {button.confidence:.2f}")
                print(f"     Method: {button.method}")
                print(f"     Text: '{button.text}'")

                # Check location
                chat_left = int(image.width * 0.55)
                chat_bottom = int(image.height * 0.75)
                avoid_top = int(image.height * 0.1)

                in_chat = (
                    button.x > chat_left
                    and button.y > max(chat_bottom, avoid_top)
                    and button.y < image.height - 20
                )

                print(f"     In chat area: {'✅ YES' if in_chat else '❌ NO'}")

                if i == 0:  # Best button
                    print(f"     👆 This would be clicked!")
        else:
            print("❌ No Continue buttons detected")
            print("\nPossible reasons:")
            print("- Continue button not currently visible")
            print("- Button appearance doesn't match detection patterns")
            print("- Detection methods need adjustment")

            print(f"\n🔧 DEBUG INFO:")
            print(f"   Chat panel area: x > {int(image.width * 0.55)}")
            print(f"   Bottom area: y > {int(image.height * 0.75)}")
            print(f"   Image saved to: {temp_path}")
            print("   You can manually inspect this image")

        # Ask user for feedback
        print(f"\n❓ FEEDBACK:")
        if buttons:
            feedback = input("Did the automation find the correct Continue button? (y/n): ")
            if feedback.lower() == "n":
                print("Please describe what you see that should be detected:")
                description = input("Description: ")
                print(f"User feedback: {description}")
        else:
            has_button = input("Do you see a Continue button in VS Code right now? (y/n): ")
            if has_button.lower() == "y":
                location = input("Where is it? (e.g., 'bottom right of chat panel'): ")
                print(f"Button location: {location}")
                print("The detection algorithms may need adjustment")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
