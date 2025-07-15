#!/usr/bin/env python3
"""
Quick Continue button detection test.
Check if buttons are currently visible and test clicking.
"""

import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PIL import Image

from core.button_finder import ButtonFinder
from core.click_automator import ClickAutomator


def get_vscode_windows():
    """Get VS Code windows."""
    try:
        result = subprocess.run(["xwininfo", "-root", "-tree"], capture_output=True, text=True)

        windows = []
        for line in result.stdout.split("\n"):
            if "visual studio code" in line.lower():
                parts = line.strip().split()
                if len(parts) >= 3:
                    window_id = parts[0]

                    for part in parts:
                        if "x" in part and "+" in part:
                            try:
                                size_pos = part.split("+")
                                size = size_pos[0].split("x")
                                width, height = int(size[0]), int(size[1])
                                x, y = int(size_pos[1]), int(size_pos[2])

                                title_start = line.find('"') + 1
                                title_end = line.find('"', title_start)
                                title = (
                                    line[title_start:title_end] if title_start > 0 else "Unknown"
                                )

                                windows.append(
                                    {
                                        "id": window_id,
                                        "title": title,
                                        "x": x,
                                        "y": y,
                                        "width": width,
                                        "height": height,
                                    }
                                )
                                break
                            except (ValueError, IndexError):
                                continue
        return windows
    except Exception as e:
        print(f"Error getting windows: {e}")
        return []


def capture_window_xwd(window_id):
    """Capture window using XWD."""
    try:
        temp_path = f"tmp/test_continue_button.png"
        Path("tmp").mkdir(exist_ok=True)

        result = subprocess.run(
            ["bash", "-c", f"xwd -id {window_id} | convert xwd:- {temp_path}"], capture_output=True
        )

        if result.returncode == 0 and Path(temp_path).exists():
            return temp_path
        return None
    except Exception as e:
        print(f"Capture error: {e}")
        return None


def main():
    print("🔍 Quick Continue Button Detection Test")
    print("=" * 45)

    # Get VS Code windows
    windows = get_vscode_windows()
    if not windows:
        print("❌ No VS Code windows found!")
        return

    print(f"Found {len(windows)} VS Code window(s):")
    for i, window in enumerate(windows, 1):
        print(f"  {i}. {window['title'][:60]}...")

    # Test each window
    finder = ButtonFinder()
    automator = ClickAutomator()

    total_buttons = 0

    for i, window in enumerate(windows, 1):
        print(f"\n--- Testing Window {i} ---")
        print(f"Title: {window['title'][:50]}...")
        print(f"Position: ({window['x']}, {window['y']})")
        print(f"Size: {window['width']}x{window['height']}")

        # Capture window
        image_path = capture_window_xwd(window["id"])
        if not image_path:
            print("❌ Failed to capture window")
            continue

        print("✅ Window captured")

        # Load and analyze
        try:
            image = Image.open(image_path)
            print(f"📊 Image size: {image.size}")

            # Find buttons
            buttons = finder.find_continue_buttons(image, 0, 0)

            if buttons:
                print(f"🎯 Found {len(buttons)} Continue button(s):")
                total_buttons += len(buttons)

                for j, btn in enumerate(buttons, 1):
                    print(f"  {j}. Text: '{btn.text}'")
                    print(f"     Position: ({btn.center_x}, {btn.center_y})")
                    print(f"     Size: {btn.width}x{btn.height}")
                    print(f"     Confidence: {btn.confidence:.2f}")
                    print(f"     Method: {btn.method}")

                    # Calculate absolute coordinates
                    abs_x = window["x"] + btn.center_x
                    abs_y = window["y"] + btn.center_y
                    print(f"     Absolute coords: ({abs_x}, {abs_y})")

                # Ask if user wants to click the first button
                if buttons:
                    choice = input(f"\nClick the first button? (y/n): ").lower().strip()
                    if choice == "y":
                        best_button = buttons[0]
                        abs_x = window["x"] + best_button.center_x
                        abs_y = window["y"] + best_button.center_y

                        print(f"🎯 Clicking at ({abs_x}, {abs_y})...")
                        result = automator.click(abs_x, abs_y)

                        if result.success:
                            print("✅ Click successful!")
                        else:
                            print(f"❌ Click failed: {result}")
            else:
                print("❌ No Continue buttons found")

        except Exception as e:
            print(f"❌ Error analyzing window: {e}")

    print(f"\n📊 Summary: Found {total_buttons} Continue buttons total")

    if total_buttons == 0:
        print("\n💡 No Continue buttons detected. This could mean:")
        print("   • No Continue button is currently visible")
        print("   • Button detection needs improvement")
        print("   • VS Code theme affects button appearance")
        print("\n🔧 Try:")
        print("   • Start a Copilot chat that shows a Continue button")
        print("   • Try a different VS Code theme")
        print("   • Check if the button text is exactly 'Continue'")


if __name__ == "__main__":
    main()
