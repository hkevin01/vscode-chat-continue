#!/usr/bin/env python3
"""
Real-time button detection and clicking test for VS Code Chat Continue.
Use this script to test the automation while VS Code is open with a Continue button.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.button_finder import ButtonFinder
from core.click_automator import ClickAutomator
from core.window_detector import WindowDetector
from utils.screen_capture import ScreenCapture


def main():
    print("🚀 VS Code Continue Button - Real-Time Test")
    print("=" * 50)
    print()
    print("Instructions:")
    print("1. Open VS Code")
    print("2. Start a Copilot chat session")
    print("3. Ask a question that shows a 'Continue' button")
    print("4. Press Enter when ready to test")
    print()

    input("Press Enter when VS Code is ready with a Continue button...")

    print("\n🔍 Starting detection...")

    # Find VS Code windows
    detector = WindowDetector()
    windows = detector.get_vscode_windows()

    if not windows:
        print("❌ No VS Code windows found!")
        print("Make sure VS Code is open and visible.")
        return

    print(f"Found {len(windows)} VS Code windows:")
    for i, window in enumerate(windows, 1):
        print(f"  {i}. {window.title[:60]}...")

    # Use the first window or let user choose
    if len(windows) > 1:
        try:
            choice = input(f"\nChoose window (1-{len(windows)}) or press Enter for first: ")
            if choice.strip():
                window_index = int(choice) - 1
            else:
                window_index = 0
        except ValueError:
            window_index = 0
    else:
        window_index = 0

    window = windows[window_index]
    print(f"\nUsing window: {window.title[:60]}...")
    print(f"Position: ({window.x}, {window.y})")
    print(f"Size: {window.width}x{window.height}")

    # Capture and analyze
    capture = ScreenCapture()
    finder = ButtonFinder()

    for attempt in range(3):
        print(f"\nAttempt {attempt + 1}/3: Capturing and analyzing...")

        # Capture window
        image = capture.capture_window(
            window.window_id, window.x, window.y, window.width, window.height
        )

        if not image:
            print("❌ Failed to capture window")
            continue

        print(f"✅ Captured window: {image.size}")

        # Save debug image
        debug_path = f"tmp/debug_attempt_{attempt + 1}.png"
        Path("tmp").mkdir(exist_ok=True)
        image.save(debug_path)
        print(f"Debug image saved: {debug_path}")

        # Find buttons
        buttons = finder.find_continue_buttons(image, window.x, window.y)

        print(f"Found {len(buttons)} potential Continue buttons:")

        if buttons:
            for i, btn in enumerate(buttons, 1):
                print(f"  {i}. Position: ({btn.center_x}, {btn.center_y})")
                print(f"     Size: {btn.width}x{btn.height}")
                print(f"     Confidence: {btn.confidence:.2f}")
                print(f"     Method: {btn.method}")
                if btn.text:
                    print(f"     Text: '{btn.text}'")

            # Ask if user wants to test clicking
            best_button = buttons[0]
            print(f"\nBest button: ({best_button.center_x}, {best_button.center_y})")

            test_click = input("Test click on this button? (y/N): ").lower().strip()

            if test_click == "y":
                print("Testing click in 3 seconds...")
                time.sleep(1)
                print("3...")
                time.sleep(1)
                print("2...")
                time.sleep(1)
                print("1...")

                # Perform the click
                clicker = ClickAutomator()
                result = clicker.click(best_button.center_x, best_button.center_y)

                if result.success:
                    print(f"✅ Click executed successfully using {result.method}")
                    print("Check VS Code to see if the Continue button was clicked!")
                    return
                else:
                    print(f"❌ Click failed")
            else:
                print("Skipping click test")

        else:
            print("❌ No Continue buttons detected")

            if attempt < 2:
                print("Trying again in 2 seconds...")
                time.sleep(2)

    print("\n🔍 Detection completed")
    print("\nIf no buttons were found:")
    print("1. Make sure a Continue button is visible in VS Code")
    print("2. Check that the button says 'Continue' or similar text")
    print("3. Try different VS Code themes (some may affect detection)")
    print("4. Look at the debug images in tmp/ to see what was captured")


if __name__ == "__main__":
    main()
