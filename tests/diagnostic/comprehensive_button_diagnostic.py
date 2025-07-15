#!/usr/bin/env python3
"""
Comprehensive diagnostic test for button detection and clicking issues.
"""

import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Create log file for results
LOG_FILE = project_root / "diagnostic_results.log"


def log_and_print(message):
    """Print message and also log it to file."""
    print(message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def test_imports():
    """Test if all required modules can be imported."""
    log_and_print("🔍 Testing imports...")
    try:
        from src.utils.gnome_screenshot_fix import setup_screenshot_environment

        setup_screenshot_environment()
        log_and_print("  ✓ gnome-screenshot fix applied")

        from src.core.config_manager import ConfigManager

        log_and_print("  ✓ ConfigManager imported")

        from src.core.automation_engine import AutomationEngine

        log_and_print("  ✓ AutomationEngine imported")

        from src.core.window_detector import WindowDetector

        log_and_print("  ✓ WindowDetector imported")

        from src.core.button_finder import ButtonFinder

        log_and_print("  ✓ ButtonFinder imported")

        from src.core.click_automator import ClickAutomator

        log_and_print("  ✓ ClickAutomator imported")

        from src.utils.screen_capture import ScreenCapture

        log_and_print("  ✓ ScreenCapture imported")

        return True
    except Exception as e:
        log_and_print(f"  ✗ Import failed: {e}")
        return False


def test_screenshot_capture():
    """Test screenshot capture functionality."""
    log_and_print("\n📸 Testing screenshot capture...")
    try:
        from src.utils.screen_capture import ScreenCapture

        screen_capture = ScreenCapture()

        # Test full screen capture
        log_and_print("  Testing full screen capture...")
        screenshot = screen_capture.capture_screen()
        if screenshot and screenshot.size[0] > 0 and screenshot.size[1] > 0:
            log_and_print(f"  ✓ Full screen capture: {screenshot.size[0]}x{screenshot.size[1]}")
        else:
            log_and_print("  ✗ Full screen capture failed")
            return False

        return True
    except Exception as e:
        log_and_print(f"  ✗ Screenshot capture failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_window_detection():
    """Test VS Code window detection."""
    log_and_print("\n🪟 Testing window detection...")
    try:
        from src.core.window_detector import WindowDetector

        detector = WindowDetector()
        windows = detector.find_vscode_windows()

        log_and_print(f"  Found {len(windows)} VS Code windows")
        for i, window in enumerate(windows):
            log_and_print(f"    Window {i+1}: {window.title}")
            log_and_print(f"      Position: ({window.x}, {window.y})")
            log_and_print(f"      Size: {window.width}x{window.height}")

        return len(windows) > 0
    except Exception as e:
        log_and_print(f"  ✗ Window detection failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_button_detection():
    """Test button detection with current screenshot."""
    log_and_print("\n🔍 Testing button detection...")
    try:
        from src.core.button_finder import ButtonFinder
        from src.utils.screen_capture import ScreenCapture

        screen_capture = ScreenCapture()
        button_finder = ButtonFinder()

        # Capture current screen
        screenshot = screen_capture.capture_screen()
        if not screenshot:
            log_and_print("  ✗ Could not capture screenshot for button detection")
            return False

        log_and_print(f"  Screenshot captured: {screenshot.size[0]}x{screenshot.size[1]}")

        # Search for Continue button
        log_and_print("  Searching for 'Continue' button...")
        locations = button_finder.find_continue_buttons(screenshot)

        if locations:
            log_and_print(f"  ✓ Found {len(locations)} button(s):")
            for i, loc in enumerate(locations):
                log_and_print(
                    f"    Button {i+1}: ({loc.x}, {loc.y}) confidence: {loc.confidence:.2f}"
                )
        else:
            log_and_print("  ✗ No 'Continue' buttons found")

        return len(locations) > 0
    except Exception as e:
        log_and_print(f"  ✗ Button detection failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_click_functionality():
    """Test basic click functionality."""
    log_and_print("\n🖱️  Testing click functionality...")
    try:
        from src.core.click_automator import ClickAutomator

        click_automator = ClickAutomator()

        log_and_print("  Testing click at safe coordinates (10, 10)...")
        result = click_automator.click(10, 10)

        if result:
            log_and_print("  ✓ Click function executed successfully")
        else:
            log_and_print("  ✗ Click function failed")

        return result
    except Exception as e:
        log_and_print(f"  ✗ Click functionality failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run comprehensive diagnostic tests."""
    log_and_print("🏥 VS Code Continue Button Automation - Diagnostic Test")
    log_and_print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Screenshot Capture", test_screenshot_capture),
        ("Window Detection", test_window_detection),
        ("Button Detection", test_button_detection),
        ("Click Functionality", test_click_functionality),
    ]

    results = {}

    for test_name, test_func in tests:
        log_and_print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            log_and_print(f"  ✗ {test_name} crashed: {e}")
            results[test_name] = False
        time.sleep(1)  # Brief pause between tests

    # Summary
    log_and_print(f"\n{'='*20} SUMMARY {'='*20}")
    passed = sum(results.values())
    total = len(results)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        log_and_print(f"  {test_name}: {status}")

    log_and_print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        log_and_print("🎉 All tests passed! The automation should work.")
    else:
        log_and_print("❌ Some tests failed. Check the errors above for troubleshooting.")

    # Specific recommendations
    log_and_print(f"\n{'='*20} RECOMMENDATIONS {'='*20}")
    if not results.get("Screenshot Capture", False):
        log_and_print("📷 Screenshot capture is failing. Check:")
        log_and_print("   - X11/Wayland display environment")
        log_and_print("   - Screen capture permissions")
        log_and_print("   - scrot/gnome-screenshot installation")

    if not results.get("Window Detection", False):
        log_and_print("🪟 Window detection is failing. Check:")
        log_and_print("   - VS Code is running")
        log_and_print("   - X11 libraries are installed")
        log_and_print("   - Window manager compatibility")

    if not results.get("Button Detection", False):
        log_and_print("🔍 Button detection is failing. Check:")
        log_and_print("   - Tesseract OCR is installed and working")
        log_and_print("   - Continue button is visible on screen")
        log_and_print("   - Button text is clear and readable")

    if not results.get("Click Functionality", False):
        log_and_print("🖱️  Click functionality is failing. Check:")
        log_and_print("   - pynput library is installed")
        log_and_print("   - Mouse/input permissions")
        log_and_print("   - Desktop environment compatibility")


if __name__ == "__main__":
    main()
