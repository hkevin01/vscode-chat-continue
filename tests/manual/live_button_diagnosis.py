#!/usr/bin/env python3
"""
Live Button Detection Diagnosis
Check if we can detect Continue buttons in current VS Code windows and analyze why clicking fails.
"""

import logging
import subprocess
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PIL import Image

from core.button_finder import ButtonFinder
from core.click_automator import ClickAutomator


def setup_logging():
    """Setup verbose logging."""
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


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

                    # Extract geometry
                    for part in parts:
                        if "x" in part and "+" in part:
                            try:
                                size_pos = part.split("+")
                                size = size_pos[0].split("x")
                                width, height = int(size[0]), int(size[1])
                                x, y = int(size_pos[1]), int(size_pos[2])

                                # Extract title
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
        temp_path = f"tmp/diagnosis_capture_{window_id.replace('0x', '')}.png"
        Path("tmp").mkdir(exist_ok=True)

        result = subprocess.run(
            ["bash", "-c", f"xwd -id {window_id} | convert xwd:- {temp_path}"], capture_output=True
        )

        if result.returncode == 0 and Path(temp_path).exists():
            return temp_path
        else:
            return None
    except Exception as e:
        print(f"XWD capture error: {e}")
        return None


def analyze_window(window, button_finder, click_automator):
    """Analyze a single window for Continue buttons."""
    print(f"\n🔍 Analyzing window: {window['title'][:50]}...")
    print(f"   Window ID: {window['id']}")
    print(f"   Position: ({window['x']}, {window['y']})")
    print(f"   Size: {window['width']}x{window['height']}")

    # Capture window
    image_path = capture_window_xwd(window["id"])
    if not image_path:
        print("   ❌ Failed to capture window")
        return

    print(f"   ✅ Captured to: {image_path}")

    try:
        # Load and analyze image
        image = Image.open(image_path)
        print(f"   📐 Image size: {image.size}")

        # Find buttons
        buttons = button_finder.find_continue_buttons(image, 0, 0)
        print(f"   🎯 Found {len(buttons)} Continue buttons")

        if buttons:
            for i, button in enumerate(buttons):
                print(f"   Button {i+1}:")
                print(f"     Method: {button.method}")
                print(f"     Position: ({button.x}, {button.y})")
                print(f"     Size: {button.width}x{button.height}")
                print(f"     Center: ({button.center_x}, {button.center_y})")
                print(f"     Confidence: {button.confidence}")
                print(f"     Text: {button.text}")

                # Calculate absolute coordinates
                abs_x = window["x"] + button.center_x
                abs_y = window["y"] + button.center_y
                print(f"     Absolute center: ({abs_x}, {abs_y})")

                # Test click (ask user first)
                response = input(f"     🖱️  Test click button {i+1}? (y/n): ").strip().lower()
                if response == "y":
                    print(f"     🖱️  Clicking at ({abs_x}, {abs_y})...")
                    result = click_automator.click(abs_x, abs_y)
                    if result.success:
                        print(f"     ✅ Click successful using {result.method}")
                    else:
                        print(f"     ❌ Click failed: {result.error}")
                    time.sleep(1)  # Brief pause
        else:
            print("   ❌ No Continue buttons detected")

            # Save image for manual inspection
            print(f"   💾 Image saved for inspection: {image_path}")

    except Exception as e:
        print(f"   ❌ Error analyzing window: {e}")


def main():
    """Main diagnosis function."""
    print("🩺 Live Button Detection Diagnosis")
    print("=" * 50)
    print()

    setup_logging()

    # Create tmp directory
    Path("tmp").mkdir(exist_ok=True)

    # Initialize components
    button_finder = ButtonFinder()
    click_automator = ClickAutomator()

    # Get VS Code windows
    windows = get_vscode_windows()

    if not windows:
        print("❌ No VS Code windows found")
        print("Please open VS Code with the Copilot chat panel visible")
        return

    print(f"✅ Found {len(windows)} VS Code window(s)")

    # Analyze each window
    for window in windows:
        analyze_window(window, button_finder, click_automator)

    print("\n🏁 Diagnosis complete!")
    print("Review the captured images in tmp/ for manual inspection")


if __name__ == "__main__":
    main()
