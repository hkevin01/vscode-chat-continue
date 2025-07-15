#!/usr/bin/env python3
"""
Final diagnostic: Check if Continue button actually exists and is detectable.
"""

import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PIL import Image, ImageDraw

from core.button_finder import ButtonFinder


def main():
    """Final comprehensive diagnostic."""
    print("🔬 FINAL DIAGNOSTIC: Continue Button Detection")
    print("=" * 60)

    # Capture computer-vision window
    print("Step 1: Capturing computer-vision VS Code window...")

    try:
        result = subprocess.run(["xwininfo", "-root", "-tree"], capture_output=True, text=True)

        cv_window = None
        for line in result.stdout.split("\n"):
            if "computer-vision" in line.lower() and "visual studio code" in line.lower():
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

                                cv_window = {
                                    "id": window_id,
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
            print("❌ Computer-vision window not found")
            return 1

        print(f"✅ Found computer-vision window: {cv_window['id']}")
        print(f"   Size: {cv_window['width']}x{cv_window['height']}")

        # Capture window
        Path("tmp").mkdir(exist_ok=True)
        image_path = "tmp/final_diagnostic.png"

        result = subprocess.run(
            ["bash", "-c", f"xwd -id {cv_window['id']} | convert xwd:- {image_path}"],
            capture_output=True,
        )

        if result.returncode != 0:
            print("❌ Failed to capture window")
            return 1

        print(f"✅ Captured to: {image_path}")

        # Load image
        image = Image.open(image_path)
        print(f"🖼️  Image size: {image.width}x{image.height}")

        # Step 2: Try detection with relaxed filtering
        print("\nStep 2: Testing button detection with relaxed filtering...")

        button_finder = ButtonFinder()

        # Temporarily disable strict filtering
        original_chat_filter = button_finder._is_in_chat_panel_area

        def relaxed_filter(x, y, width, height):
            # Much more permissive - right half of screen
            return x > width * 0.4

        button_finder._is_in_chat_panel_area = relaxed_filter

        buttons = button_finder.find_continue_buttons(image, 0, 0)

        # Restore original filter
        button_finder._is_in_chat_panel_area = original_chat_filter

        print(f"🔍 Result: {len(buttons)} buttons found with relaxed filtering")

        if buttons:
            print("🎯 BUTTONS DETECTED:")
            for i, button in enumerate(buttons):
                abs_x = cv_window["x"] + button.center_x
                abs_y = cv_window["y"] + button.center_y

                print(f"\n   Button {i+1}:")
                print(f"     Position: ({button.x}, {button.y}) -> screen ({abs_x}, {abs_y})")
                print(f"     Size: {button.width}x{button.height}")
                print(f"     Confidence: {button.confidence:.2f}")
                print(f"     Method: {button.method}")
                print(f"     Text: '{button.text}'")

                # Check against original strict filter
                chat_left = int(image.width * 0.55)
                chat_bottom = int(image.height * 0.75)
                avoid_top = int(image.height * 0.1)

                passes_strict = (
                    button.x > chat_left
                    and button.y > max(chat_bottom, avoid_top)
                    and button.y < image.height - 20
                )

                print(f"     Passes strict filter: {'✅ YES' if passes_strict else '❌ NO'}")

                if not passes_strict:
                    print(f"       (needs x > {chat_left}, y > {max(chat_bottom, avoid_top)})")

            # Create annotated image
            draw = ImageDraw.Draw(image)

            # Draw chat panel area
            chat_left = int(image.width * 0.55)
            chat_bottom = int(image.height * 0.75)
            avoid_top = int(image.height * 0.1)

            draw.rectangle(
                [chat_left, max(chat_bottom, avoid_top), image.width, image.height - 20],
                outline="yellow",
                width=3,
            )

            # Draw detected buttons
            for i, button in enumerate(buttons):
                color = "green" if i == 0 else "orange"
                draw.rectangle(
                    [button.x, button.y, button.x + button.width, button.y + button.height],
                    outline=color,
                    width=3,
                )
                draw.text((button.x, button.y - 20), f"#{i+1}", fill=color)

            annotated_path = "tmp/final_diagnostic_annotated.png"
            image.save(annotated_path)
            print(f"\n💾 Annotated image saved: {annotated_path}")
            print("🟡 Yellow box = strict chat panel filter area")
            print("🟢 Green box = best detected button")
            print("🟠 Orange boxes = other detected buttons")

        else:
            print("❌ NO BUTTONS DETECTED even with relaxed filtering")
            print("\nThis means either:")
            print("  1. No Continue button is currently visible")
            print("  2. Button appearance doesn't match detection patterns")
            print("  3. Detection algorithms need fundamental changes")

            # Save the captured image for manual inspection
            print(f"\n🔍 Manual inspection needed:")
            print(f"   Check {image_path} for visible Continue buttons")
            print("   Look for blue buttons with white text saying 'Continue'")

        # Step 3: Summary and next steps
        print(f"\n📊 FINAL SUMMARY:")
        print(f"   Window targeted: ✅ computer-vision VS Code")
        print(f"   Window captured: ✅ {image.width}x{image.height}")
        print(f"   Buttons detected: {'✅' if buttons else '❌'} {len(buttons)} buttons")

        if buttons:
            strict_count = sum(
                1
                for b in buttons
                if b.x > int(image.width * 0.55)
                and b.y > max(int(image.height * 0.75), int(image.height * 0.1))
            )
            print(
                f"   Pass strict filter: {'✅' if strict_count > 0 else '❌'} {strict_count} buttons"
            )

            if strict_count == 0:
                print("\n🔧 RECOMMENDED ACTION:")
                print("   The automation is too restrictive. Consider:")
                print("   1. Relaxing the chat panel area filter")
                print("   2. Adjusting the position thresholds")
                print("   3. Using the relaxed detection temporarily")
        else:
            print("\n🔧 RECOMMENDED ACTION:")
            print("   1. Verify Continue button is actually visible in VS Code")
            print("   2. Check if button appearance has changed")
            print("   3. Consider updating detection patterns")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
