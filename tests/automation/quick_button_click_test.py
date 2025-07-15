#!/usr/bin/env python3
"""
Quick test specifically for button clicking issues.
"""

import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


def quick_button_test():
    """Quick test of the full button detection and clicking pipeline."""
    print("🚀 Quick Button Detection & Click Test")
    print("=" * 50)

    try:
        # Import everything we need
        from src.core.automation_engine import AutomationEngine
        from src.core.config_manager import ConfigManager
        from src.utils.gnome_screenshot_fix import setup_screenshot_environment

        setup_screenshot_environment()
        print("✓ Environment setup complete")

        # Initialize components
        config_manager = ConfigManager()
        automation_engine = AutomationEngine(config_manager)
        print("✓ Automation engine initialized")

        # Test the actual automation workflow
        print("\n🔍 Testing automation workflow...")

        # Check if VS Code is running
        from src.core.window_detector import WindowDetector

        detector = WindowDetector()
        windows = detector.find_vscode_windows()

        if not windows:
            print("❌ No VS Code windows found!")
            print("   Please start VS Code with a Copilot chat session open")
            return False

        print(f"✓ Found {len(windows)} VS Code window(s)")

        # Test screenshot and button detection
        from src.core.button_finder import ButtonFinder
        from src.utils.screen_capture import ScreenCapture

        screen_capture = ScreenCapture()
        button_finder = ButtonFinder()

        print("\n📸 Taking screenshot...")
        screenshot = screen_capture.capture_screen()

        if not screenshot:
            print("❌ Screenshot capture failed!")
            return False

        print(f"✓ Screenshot captured: {screenshot.size[0]}x{screenshot.size[1]} pixels")

        # Check if screenshot is too small (previous issue)
        if screenshot.size[0] < 100 or screenshot.size[1] < 100:
            print(f"❌ Screenshot too small: {screenshot.size}")
            print("   This indicates a capture region issue")
            return False

        print("\n🔍 Searching for Continue button...")
        locations = button_finder.find_continue_buttons(screenshot)

        if not locations:
            print("❌ No Continue button found!")
            print("   Trying OCR debug mode...")

            # Save screenshot for manual inspection
            screenshot.save("/tmp/debug_screenshot.png")
            print("   Screenshot saved to /tmp/debug_screenshot.png")

            # Try to extract all text to see what OCR finds
            import pytesseract

            text = pytesseract.image_to_string(screenshot)
            print(f"   OCR found text: {repr(text[:200])}")

            return False

        print(f"✓ Found {len(locations)} Continue button(s):")
        for i, loc in enumerate(locations):
            print(f"   Button {i+1}: ({loc.x}, {loc.y}) confidence: {loc.confidence:.2f}")

        # Test clicking the first button found
        best_location = locations[0]
        print(f"\n🖱️  Attempting to click at ({best_location.x}, {best_location.y})...")

        from src.core.click_automator import ClickAutomator

        click_automator = ClickAutomator()

        # Give user a chance to see what's happening
        print("   Clicking in 3 seconds... (Ctrl+C to cancel)")
        time.sleep(3)

        success = click_automator.click(best_location.x, best_location.y)

        if success:
            print("✓ Click executed successfully!")
            return True
        else:
            print("❌ Click failed!")
            return False

    except KeyboardInterrupt:
        print("\n⏹️  Test cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    print("VS Code Continue Button - Quick Click Test")
    print("=" * 50)
    print("This test will:")
    print("1. Check if VS Code is running")
    print("2. Take a screenshot")
    print("3. Search for Continue button")
    print("4. Attempt to click it")
    print("\nMake sure VS Code is open with a Copilot chat session!")
    print("Press Enter to continue or Ctrl+C to cancel...")

    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return

    success = quick_button_test()

    if success:
        print("\n🎉 Test completed successfully!")
        print("The automation should now be working.")
    else:
        print("\n❌ Test failed.")
        print("Check the error messages above for troubleshooting.")


if __name__ == "__main__":
    main()
