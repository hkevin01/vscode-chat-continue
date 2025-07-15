#!/usr/bin/env python3
"""Quick test of enhanced button finder."""

import logging
import sys
from pathlib import Path

# Add project paths
project_root = Path("/home/kevin/Projects/vscode-chat-continue")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

print("=== Enhanced Button Finder Test ===")

try:
    from src.core.button_finder import ButtonFinder
    from src.utils.screen_capture import ScreenCapture

    print("1. Capturing screenshot...")
    screen = ScreenCapture()
    screenshot = screen.capture_screen()

    if screenshot:
        w, h = screenshot.size
        print(f"   ✓ Screenshot: {w}x{h}")

        print("2. Testing enhanced button finder...")
        finder = ButtonFinder()
        buttons = finder.find_continue_buttons(screenshot)

        print(f"   Found {len(buttons)} buttons")
        for i, btn in enumerate(buttons):
            print(f"   Button {i+1}: ({btn.x},{btn.y}) {btn.width}x{btn.height}")
            print(f"     Method: {btn.method}")
            print(f"     Confidence: {btn.confidence:.2f}")
            if btn.text:
                print(f"     Text: {repr(btn.text)}")

        if not buttons:
            print("   No buttons found - OCR may not be detecting VS Code UI text")
            print("   This is expected if no Continue button is visible")

    else:
        print("   ✗ No screenshot captured")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
