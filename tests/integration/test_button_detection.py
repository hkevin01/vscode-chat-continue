#!/usr/bin/env python3
"""
Quick test to see if button detection is working.
"""

import sys
from pathlib import Path

# Add project paths
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.button_finder import ButtonFinder
from core.window_detector import WindowDetector
from utils.screen_capture import ScreenCapture


def main():
    print("🔍 Testing Continue Button Detection")
    print("=" * 50)

    # Initialize components
    detector = WindowDetector()
    button_finder = ButtonFinder()
    screen_capture = ScreenCapture()

    # Get VS Code windows
    print("1. Detecting VS Code windows...")
    windows = detector.get_vscode_windows()
    print(f"   Found {len(windows)} VS Code windows")

    if not windows:
        print("❌ No VS Code windows found!")
        return

    for i, window in enumerate(windows, 1):
        print(f"\n2. Processing Window {i}:")
        print(f"   Title: {window.title}")
        print(f"   Size: {window.width}x{window.height}")
        print(f"   Position: ({window.x}, {window.y})")

        # Try to capture the window
        print("   Capturing window...")
        screenshot = screen_capture.capture_window(
            window.window_id, window.x, window.y, window.width, window.height
        )

        if not screenshot:
            print("   ❌ Window capture failed, trying full screen...")
            screenshot = screen_capture.capture_screen()
            if not screenshot:
                print("   ❌ Full screen capture also failed!")
                continue

        print(f"   ✅ Screenshot captured: {screenshot.size}")

        # Save screenshot for debugging
        debug_path = f"debug_window_{i}.png"
        screenshot.save(debug_path)
        print(f"   💾 Screenshot saved to: {debug_path}")

        # Look for continue buttons
        print("   Searching for Continue buttons...")
        buttons = button_finder.find_continue_buttons(screenshot, window.x, window.y)

        print(f"   Found {len(buttons)} Continue buttons:")
        for j, button in enumerate(buttons, 1):
            print(
                f"     Button {j}: ({button.center_x}, {button.center_y}) "
                f"confidence={button.confidence:.2f} method={button.method}"
            )

        if not buttons:
            print("   ❌ No Continue buttons found in this window")
        else:
            print(f"   ✅ Found {len(buttons)} Continue button(s)!")


if __name__ == "__main__":
    main()
