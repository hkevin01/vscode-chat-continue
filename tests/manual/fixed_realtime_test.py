#!/usr/bin/env python3
"""
Fixed real-time button test using XWD for proper window capture.
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


def get_vscode_windows():
    """Get VS Code windows using xwininfo."""
    try:
        result = subprocess.run(["xwininfo", "-root", "-tree"], capture_output=True, text=True)

        windows = []
        for line in result.stdout.split("\n"):
            if "visual studio code" in line.lower():
                # Parse line format: 0xID "Title": ("class" "Class") WIDTHxHEIGHT+X+Y
                parts = line.strip().split()
                if len(parts) >= 3:
                    window_id = parts[0]

                    # Extract geometry (WIDTHxHEIGHT+X+Y)
                    for part in parts:
                        if "x" in part and "+" in part:
                            try:
                                # Parse format like "1680x1050+104+0"
                                size_pos = part.split("+")
                                size = size_pos[0].split("x")
                                width, height = int(size[0]), int(size[1])
                                x, y = int(size_pos[1]), int(size_pos[2])

                                # Extract title (between quotes)
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
        temp_path = f"tmp/capture_{window_id.replace('0x', '')}.png"
        Path("tmp").mkdir(exist_ok=True)

        result = subprocess.run(
            ["bash", "-c", f"xwd -id {window_id} | convert xwd:- {temp_path}"], capture_output=True
        )

        if result.returncode == 0 and Path(temp_path).exists():
            return temp_path
        else:
            print(f"XWD capture failed: {result.stderr.decode()}")
            return None
    except Exception as e:
        print(f"XWD capture error: {e}")
        return None


def main():
    print("🚀 Fixed VS Code Continue Button Test")
    print("=" * 50)
    print()
    print("Instructions:")
    print("1. Make sure VS Code is open with a Continue button visible")
    print("2. The button should be in the Copilot chat panel")
    print("3. Press Enter when ready to test")
    print()

    input("Press Enter when VS Code is ready with a Continue button...")

    print("\n🔍 Finding VS Code windows...")

    windows = get_vscode_windows()
    if not windows:
        print("❌ No VS Code windows found!")
        return

    print(f"Found {len(windows)} VS Code windows:")
    for i, window in enumerate(windows, 1):
        print(f"  {i}. {window['title'][:60]}...")
        print(
            f"     Position: ({window['x']}, {window['y']}) Size: {window['width']}x{window['height']}"
        )

    # Choose window
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
    print(f"\nUsing window: {window['title'][:60]}...")

    # Capture using XWD
    for attempt in range(3):
        print(f"\nAttempt {attempt + 1}/3: Capturing window...")

        image_path = capture_window_xwd(window["id"])
        if not image_path:
            print("❌ Failed to capture window")
            continue

        # Load image
        try:
            image = Image.open(image_path)
            print(f"✅ Captured window: {image.size}")
        except Exception as e:
            print(f"❌ Failed to load captured image: {e}")
            continue

        # Find buttons
        finder = ButtonFinder()
        print("🔍 Searching for Continue buttons...")

        buttons = finder.find_continue_buttons(image, 0, 0)

        print(f"Found {len(buttons)} potential Continue buttons:")

        if buttons:
            for i, btn in enumerate(buttons, 1):
                print(f"  {i}. Text: '{btn.text}'")
                print(f"     Position: ({btn.center_x}, {btn.center_y})")
                print(f"     Size: {btn.width}x{btn.height}")
                print(f"     Confidence: {btn.confidence:.2f}")

            # Try to click the first button
            best_button = buttons[0]
            print(f"\n🎯 Attempting to click button: '{best_button.text}'")

            # Calculate absolute screen coordinates
            abs_x = window["x"] + best_button.center_x
            abs_y = window["y"] + best_button.center_y

            print(f"   Absolute coordinates: ({abs_x}, {abs_y})")

            automator = ClickAutomator()
            result = automator.click(abs_x, abs_y)

            if result.success:
                print("✅ Successfully clicked the Continue button!")
                print("🔇 (No audio feedback - beeps are disabled)")
                return
            else:
                print(f"❌ Click failed: {result}")
        else:
            print("❌ No Continue buttons detected")

            # Show OCR analysis
            try:
                import cv2
                import pytesseract

                cv_image = cv2.imread(image_path)
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

                # Focus on right side where Continue button should be
                height, width = gray.shape
                right_region = gray[:, width // 2 :]

                text = pytesseract.image_to_string(right_region, config="--psm 6")
                lines = [line.strip() for line in text.split("\n") if line.strip()]

                print(f"\n📝 OCR found text in right region:")
                for line in lines[:15]:  # Show first 15 lines
                    if any(word in line.lower() for word in ["continue", "cancel", "next"]):
                        print(f"  ⭐ {line}")
                    else:
                        print(f"     {line}")

            except ImportError:
                print("  (Install tesseract-ocr for detailed text analysis)")
            except Exception as e:
                print(f"  OCR analysis failed: {e}")

        if attempt < 2:
            print("Trying again in 2 seconds...")
            time.sleep(2)

    print("\n❌ Could not find or click Continue button after 3 attempts")
    print("\nTroubleshooting:")
    print("1. Make sure a Continue button is actually visible in VS Code")
    print("2. Try a different VS Code theme (dark/light)")
    print("3. Ensure the button text is exactly 'Continue'")
    print("4. Check if the button is in the chat panel on the right side")


if __name__ == "__main__":
    main()
