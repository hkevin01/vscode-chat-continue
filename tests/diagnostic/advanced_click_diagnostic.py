#!/usr/bin/env python3
"""
Advanced diagnostic script for debugging button clicking failures.
This script provides detailed testing and troubleshooting for the automation system.
"""

import logging
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.automation_engine import AutomationEngine
from core.button_finder import ButtonFinder
from core.click_automator import ClickAutomator
from core.config_manager import ConfigManager
from core.window_detector import WindowDetector
from utils.screen_capture import ScreenCapture


def setup_logging():
    """Setup detailed logging for debugging."""
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def test_click_automation_detailed():
    """Detailed test of click automation methods."""
    print("\n🖱️ Detailed Click Automation Test")
    print("=" * 50)

    try:
        automator = ClickAutomator()

        # Test available methods
        print("Testing available click methods:")

        # Test PyAutoGUI
        try:
            import pyautogui

            print("✅ PyAutoGUI available")

            # Get current mouse position for safe testing
            current_x, current_y = pyautogui.position()
            print(f"Current mouse position: ({current_x}, {current_y})")

            # Test dry run
            result = automator.click(current_x, current_y, dry_run=True)
            print(f"Dry run result: {result.success} - {result.method}")

        except Exception as e:
            print(f"❌ PyAutoGUI test failed: {e}")

        # Test pynput
        try:
            from pynput import mouse

            controller = mouse.Controller()
            pos = controller.position
            print(f"✅ pynput available - Current position: {pos}")

        except Exception as e:
            print(f"❌ pynput test failed: {e}")

        # Test platform-specific methods
        import platform

        system = platform.system()
        print(f"Platform: {system}")

        if system == "Linux":
            try:
                import Xlib.display

                print("✅ Xlib available for Linux")
            except ImportError:
                print("❌ Xlib not available")

        return True

    except Exception as e:
        print(f"❌ Click automation detailed test failed: {e}")
        return False


def test_vscode_detection_detailed():
    """Detailed VS Code window detection test."""
    print("\n🪟 Detailed VS Code Detection Test")
    print("=" * 50)

    try:
        detector = WindowDetector()

        # Test process detection first
        print("Testing VS Code process detection:")
        processes = detector.get_vscode_processes()
        print(f"Found {len(processes)} VS Code processes:")

        for proc in processes:
            try:
                print(f"  PID: {proc.pid}, Name: {proc.name()}, Exe: {proc.exe()}")
            except Exception as e:
                print(f"  PID: {proc.pid}, Error getting details: {e}")

        # Test window detection
        print("\nTesting window detection:")
        windows = detector.get_vscode_windows()
        print(f"Found {len(windows)} VS Code windows:")

        for i, window in enumerate(windows, 1):
            print(f"\nWindow {i}:")
            print(f"  ID: {window.window_id}")
            print(f"  Title: {window.title}")
            print(f"  PID: {window.pid}")
            print(f"  Position: ({window.x}, {window.y})")
            print(f"  Size: {window.width}x{window.height}")
            print(f"  Focused: {window.is_focused}")

        if windows:
            # Test capturing the first window
            window = windows[0]
            print(f"\nTesting capture of window: {window.title[:50]}...")

            capture = ScreenCapture()
            image = capture.capture_window(window.x, window.y, window.width, window.height)

            if image:
                print(f"✅ Window capture successful: {image.size}")

                # Save debug image
                debug_path = Path("tmp/debug_window_capture.png")
                debug_path.parent.mkdir(exist_ok=True)
                image.save(debug_path)
                print(f"Debug image saved to: {debug_path}")

            else:
                print("❌ Window capture failed")

        return len(windows) > 0

    except Exception as e:
        print(f"❌ VS Code detection detailed test failed: {e}")
        return False


def test_button_detection_detailed():
    """Detailed button detection test with debug output."""
    print("\n🎯 Detailed Button Detection Test")
    print("=" * 50)

    try:
        detector = WindowDetector()
        windows = detector.get_vscode_windows()

        if not windows:
            print("❌ No VS Code windows found")
            return False

        window = windows[0]
        print(f"Testing button detection in: {window.title[:50]}...")

        # Capture window
        capture = ScreenCapture()
        image = capture.capture_window(window.x, window.y, window.width, window.height)

        if not image:
            print("❌ Failed to capture window")
            return False

        # Save debug image
        debug_path = Path("tmp/debug_button_search.png")
        debug_path.parent.mkdir(exist_ok=True)
        image.save(debug_path)
        print(f"Window image saved to: {debug_path}")

        # Test button finder
        button_finder = ButtonFinder()

        # Test each detection method individually
        print("\nTesting OCR detection:")
        try:
            import pytesseract

            ocr_buttons = button_finder._find_buttons_ocr(image, window.x, window.y)
            print(f"OCR found {len(ocr_buttons)} buttons")
            for btn in ocr_buttons:
                print(f"  OCR: ({btn.x}, {btn.y}) conf={btn.confidence:.2f} text='{btn.text}'")
        except Exception as e:
            print(f"OCR test failed: {e}")

        print("\nTesting color detection:")
        try:
            color_buttons = button_finder._find_buttons_color(image, window.x, window.y)
            print(f"Color detection found {len(color_buttons)} buttons")
            for btn in color_buttons:
                print(f"  Color: ({btn.x}, {btn.y}) conf={btn.confidence:.2f}")
        except Exception as e:
            print(f"Color detection test failed: {e}")

        print("\nTesting template matching:")
        try:
            import cv2

            template_buttons = button_finder._find_buttons_template(image, window.x, window.y)
            print(f"Template matching found {len(template_buttons)} buttons")
            for btn in template_buttons:
                print(f"  Template: ({btn.x}, {btn.y}) conf={btn.confidence:.2f}")
        except Exception as e:
            print(f"Template matching test failed: {e}")

        # Test combined detection
        print("\nTesting combined detection:")
        all_buttons = button_finder.find_continue_buttons(image, window.x, window.y)
        print(f"Combined detection found {len(all_buttons)} buttons")

        for i, btn in enumerate(all_buttons, 1):
            print(f"  Button {i}: ({btn.x}, {btn.y}) size={btn.width}x{btn.height}")
            print(f"            confidence={btn.confidence:.2f} method={btn.method}")
            if btn.text:
                print(f"            text='{btn.text}'")

        return len(all_buttons) > 0

    except Exception as e:
        print(f"❌ Button detection detailed test failed: {e}")
        return False


def test_full_click_simulation():
    """Test full click simulation in dry run mode."""
    print("\n🤖 Full Click Simulation Test (Dry Run)")
    print("=" * 50)

    try:
        # Setup
        config_manager = ConfigManager()
        config_manager.config_data.setdefault("automation", {})["dry_run"] = True

        detector = WindowDetector()
        windows = detector.get_vscode_windows()

        if not windows:
            print("❌ No VS Code windows found")
            return False

        window = windows[0]
        capture = ScreenCapture()
        button_finder = ButtonFinder()
        click_automator = ClickAutomator()

        print(f"Simulating full automation cycle on: {window.title[:50]}...")

        # Capture window
        image = capture.capture_window(window.x, window.y, window.width, window.height)
        if not image:
            print("❌ Window capture failed")
            return False

        # Find buttons
        buttons = button_finder.find_continue_buttons(image, window.x, window.y)
        if not buttons:
            print("⚠️  No buttons found to click")
            return True  # Not an error, just no buttons

        # Simulate clicking the best button
        best_button = buttons[0]
        print(f"Would click button at ({best_button.center_x}, {best_button.center_y})")
        print(
            f"Button details: {best_button.width}x{best_button.height}, conf={best_button.confidence:.2f}"
        )

        # Dry run click
        result = click_automator.click(best_button.center_x, best_button.center_y, dry_run=True)

        if result.success:
            print(f"✅ Click simulation successful using {result.method}")
        else:
            print("❌ Click simulation failed")
            return False

        return True

    except Exception as e:
        print(f"❌ Full click simulation test failed: {e}")
        return False


def main():
    """Run advanced diagnostic tests."""
    print("🔧 VS Code Chat Continue - Advanced Button Click Diagnostics")
    print("=" * 70)

    setup_logging()

    tests = [
        ("Click Automation Details", test_click_automation_detailed),
        ("VS Code Detection Details", test_vscode_detection_detailed),
        ("Button Detection Details", test_button_detection_detailed),
        ("Full Click Simulation", test_full_click_simulation),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n📊 Advanced Diagnostic Results")
    print("=" * 70)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")

    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All advanced tests passed!")
        print("The automation system components are working correctly.")
        print("If clicking still fails, the issue may be:")
        print("- No Continue buttons visible in VS Code")
        print("- Button appearance changed (update templates)")
        print("- Timing issues (try adjusting scan interval)")
    else:
        print(f"\n⚠️  {total-passed} advanced test(s) failed.")
        print("This provides more specific information about the clicking failure.")


if __name__ == "__main__":
    main()
