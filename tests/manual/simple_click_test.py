#!/usr/bin/env python3
"""
Simple VS Code Continue Button Clicker Test

Run this script when you have a Continue button visible in VS Code.
It will find and click the button if detected.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    print("🎯 VS Code Continue Button Clicker")
    print("=" * 40)
    print()
    print("Make sure you have:")
    print("1. VS Code open")
    print("2. Copilot chat panel open")
    print("3. A visible 'Continue' button")
    print()

    input("Press Enter when ready...")

    try:
        # Import modules
        from core.button_finder import ButtonFinder
        from core.click_automator import ClickAutomator
        from core.window_detector import WindowDetector
        from utils.screen_capture import ScreenCapture

        print("\n🔍 Finding VS Code...")
        detector = WindowDetector()
        windows = detector.get_vscode_windows()

        if not windows:
            print("❌ No VS Code windows found!")
            return

        window = windows[0]  # Use first window
        print(f"✅ Found VS Code: {window.title[:50]}...")

        print("\n📸 Capturing window...")
        capture = ScreenCapture()
        image = capture.capture_window(
            window.window_id, window.x, window.y, window.width, window.height
        )

        if not image:
            print("❌ Failed to capture window!")
            return

        # Save for debugging
        Path("tmp").mkdir(exist_ok=True)
        image.save("tmp/last_capture.png")
        print("✅ Window captured (saved to tmp/last_capture.png)")

        print("\n🎯 Looking for Continue buttons...")
        finder = ButtonFinder()
        buttons = finder.find_continue_buttons(image, window.x, window.y)

        if not buttons:
            print("❌ No Continue buttons found!")
            print("\n💡 Possible solutions:")
            print("- Make sure the Continue button is visible")
            print("- Check tmp/last_capture.png to see what was captured")
            print("- Try a different VS Code theme")
            print("- Ask a longer question in Copilot chat")
            return

        print(f"✅ Found {len(buttons)} Continue button(s)!")

        best_button = buttons[0]
        print(f"\nBest button:")
        print(f"  Position: ({best_button.center_x}, {best_button.center_y})")
        print(f"  Confidence: {best_button.confidence:.2f}")
        print(f"  Method: {best_button.method}")
        if best_button.text:
            print(f"  Text: '{best_button.text}'")

        # Ask before clicking
        click_now = input("\n🖱️  Click this button? (y/N): ").lower().strip()

        if click_now == "y":
            print("\nClicking in 3 seconds...")
            for i in range(3, 0, -1):
                print(f"{i}...")
                time.sleep(1)

            clicker = ClickAutomator()
            result = clicker.click(best_button.center_x, best_button.center_y)

            if result.success:
                print(f"✅ Successfully clicked using {result.method}!")
                print("Check VS Code to see if it worked!")
            else:
                print("❌ Click failed!")
        else:
            print("Click cancelled.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
