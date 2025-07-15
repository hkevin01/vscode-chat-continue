#!/usr/bin/env python3
"""
Window position debugging script.
Check actual window positions and capture them correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.window_detector import WindowDetector
from utils.screen_capture import ScreenCapture


def main():
    print("🪟 Window Position Debugging")
    print("=" * 40)

    # Find VS Code windows
    detector = WindowDetector()
    windows = detector.get_vscode_windows()

    if not windows:
        print("❌ No VS Code windows found!")
        return

    print(f"Found {len(windows)} VS Code windows:")

    for i, window in enumerate(windows, 1):
        print(f"\n--- Window {i} ---")
        print(f"Title: {window.title}")
        print(f"Position: ({window.x}, {window.y})")
        print(f"Size: {window.width}x{window.height}")
        print(f"Window ID: {window.window_id}")

        # Test capture at reported coordinates
        capture = ScreenCapture()

        # Method 1: Using reported window coordinates
        print(f"\n🔍 Testing capture at reported coordinates...")
        image1 = capture.capture_region(window.x, window.y, window.width, window.height)

        if image1:
            test_path = f"tmp/window_{i}_reported.png"
            Path("tmp").mkdir(exist_ok=True)
            image1.save(test_path)
            print(f"✅ Captured using reported coords: {image1.size}")
            print(f"💾 Saved to: {test_path}")

            # Check if image has content (not black)
            import cv2
            import numpy as np

            cv_image = cv2.imread(test_path)
            if cv_image is not None:
                mean_intensity = cv_image.mean()
                print(f"📊 Mean intensity: {mean_intensity:.1f}")
                if mean_intensity < 5:
                    print("⚠️ Image appears to be mostly black - coordinates may be wrong")
                else:
                    print("✅ Image has content - coordinates look correct")
        else:
            print("❌ Failed to capture using reported coordinates")

        # Method 2: Try to capture full screen and show where window should be
        print(f"\n🌍 Checking full screen context...")
        full_screen = capture.capture_screen()
        if full_screen:
            screen_w, screen_h = full_screen.size
            print(f"Full screen size: {screen_w}x{screen_h}")

            # Check if window coordinates are within screen bounds
            if (
                window.x >= 0
                and window.y >= 0
                and window.x + window.width <= screen_w
                and window.y + window.height <= screen_h
            ):
                print("✅ Window coordinates are within screen bounds")

                # Crop the region where window should be
                cropped = full_screen.crop(
                    (window.x, window.y, window.x + window.width, window.y + window.height)
                )
                test_path2 = f"tmp/window_{i}_cropped.png"
                cropped.save(test_path2)
                print(f"💾 Cropped region saved to: {test_path2}")

            else:
                print("⚠️ Window coordinates are outside screen bounds!")
                print(f"   Window: ({window.x}, {window.y}) + {window.width}x{window.height}")
                print(f"   Screen: {screen_w}x{screen_h}")

        print("-" * 40)


if __name__ == "__main__":
    main()
