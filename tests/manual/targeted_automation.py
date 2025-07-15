#!/usr/bin/env python3
"""
Targeted Continue Button Automation - Only runs when you confirm a button is visible.
This ensures we only try to click when there's actually a Continue button present.
"""

import subprocess
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PIL import Image

from core.button_finder import ButtonFinder
from core.click_automator import ClickAutomator
from utils.audio_suppressor import enable_audio_suppression


def get_vscode_windows():
    """Get VS Code windows using xwininfo."""
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
        temp_path = "tmp/targeted_capture.png"
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
    print("🎯 Targeted Continue Button Automation")
    print("=" * 45)
    print()
    print("This automation only runs when you confirm")
    print("that a Continue button is currently visible.")
    print()

    # Ensure audio is disabled
    enable_audio_suppression()
    print("🔇 Audio suppression enabled")

    # Get user confirmation
    print("\n📋 Pre-flight checklist:")
    print("1. ✅ VS Code is open with Copilot chat")
    print("2. ✅ A blue Continue button is visible")
    print("3. ✅ The button text says 'Continue'")
    print()

    confirm = input("Is a Continue button currently visible in VS Code? (y/n): ").lower().strip()
    if confirm != "y":
        print("❌ Please start a Copilot chat and get a Continue button visible first.")
        return

    print("\n🔍 Searching for Continue buttons...")

    # Get VS Code windows
    windows = get_vscode_windows()
    if not windows:
        print("❌ No VS Code windows found!")
        return

    finder = ButtonFinder()
    automator = ClickAutomator()

    buttons_found = False

    for window in windows:
        print(f"\n📱 Checking window: {window['title'][:50]}...")

        # Capture window
        image_path = capture_window_xwd(window["id"])
        if not image_path:
            print("❌ Failed to capture window")
            continue

        try:
            # Load and analyze
            image = Image.open(image_path)
            buttons = finder.find_continue_buttons(image, 0, 0)

            if buttons:
                print(f"🎯 Found {len(buttons)} potential Continue button(s):")

                # Filter for higher confidence buttons or those with Continue text
                good_buttons = []
                for btn in buttons:
                    print(
                        f"   • Text: '{btn.text}' | Confidence: {btn.confidence:.2f} | Method: {btn.method}"
                    )

                    # Consider it a good button if:
                    # 1. High confidence (>0.7), OR
                    # 2. Contains "continue" text, OR
                    # 3. Blue button detection method
                    if (
                        btn.confidence > 0.7
                        or (btn.text and "continue" in btn.text.lower())
                        or "blue" in btn.method.lower()
                    ):
                        good_buttons.append(btn)

                if good_buttons:
                    best_button = good_buttons[0]
                    abs_x = window["x"] + best_button.center_x
                    abs_y = window["y"] + best_button.center_y

                    print(f"\n🎯 Clicking best button at ({abs_x}, {abs_y})...")

                    result = automator.click(abs_x, abs_y)

                    if result.success:
                        print("✅ Successfully clicked Continue button!")
                        print("🔇 (No audio feedback - beeps disabled)")
                        buttons_found = True
                        break
                    else:
                        print(f"❌ Click failed: {result}")
                else:
                    print("⚠️ Found buttons but none meet quality criteria")
            else:
                print("❌ No Continue buttons detected in this window")

        except Exception as e:
            print(f"❌ Error processing window: {e}")

    if not buttons_found:
        print("\n❌ No suitable Continue buttons found to click")
        print("\n💡 Troubleshooting:")
        print("   • Make sure the Continue button is clearly visible")
        print("   • Try a different VS Code theme (dark/light)")
        print("   • Ensure the button text is exactly 'Continue'")
        print("   • Check if the button is blue with white text")
    else:
        print("\n🎉 Continue button automation completed successfully!")


if __name__ == "__main__":
    main()
