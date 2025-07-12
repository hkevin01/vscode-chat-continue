#!/usr/bin/env python3
"""Simple import test to check basic functionality."""

import sys
from pathlib import Path

# Add project paths
project_root = Path("/home/kevin/Projects/vscode-chat-continue")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print("=== VS Code Continue Button Automation - Quick Test ===")

# Test 1: Basic imports
print("\n1. Testing imports...")
try:
    from src.utils.gnome_screenshot_fix import setup_screenshot_environment
    setup_screenshot_environment()
    print("   ✓ gnome-screenshot fix")
    
    from src.core.config_manager import ConfigManager
    config = ConfigManager()
    print("   ✓ ConfigManager")
    
    from src.utils.screen_capture import ScreenCapture
    screen = ScreenCapture()
    print("   ✓ ScreenCapture")
    
    from src.core.button_finder import ButtonFinder
    finder = ButtonFinder()
    print("   ✓ ButtonFinder")
    
    from src.core.click_automator import ClickAutomator
    clicker = ClickAutomator()
    print("   ✓ ClickAutomator")
    
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Screenshot capture
print("\n2. Testing screenshot...")
try:
    screenshot = screen.capture_screen()
    if screenshot:
        w, h = screenshot.size
        print(f"   ✓ Screenshot captured: {w}x{h} pixels")
        
        # Check if screenshot is reasonable size
        if w < 100 or h < 100:
            print(f"   ⚠ WARNING: Screenshot very small ({w}x{h})")
        else:
            print(f"   ✓ Screenshot size looks good")
            
        # Save for inspection
        screenshot.save("/tmp/test_screenshot.png")
        print("   ✓ Screenshot saved to /tmp/test_screenshot.png")
        
    else:
        print("   ✗ Screenshot capture returned None")
        
except Exception as e:
    print(f"   ✗ Screenshot failed: {e}")

# Test 3: Button detection
print("\n3. Testing button detection...")
try:
    if screenshot:
        buttons = finder.find_continue_buttons(screenshot)
        print(f"   Found {len(buttons)} Continue buttons")
        
        for i, btn in enumerate(buttons):
            print(f"   Button {i+1}: x={btn.x}, y={btn.y}, conf={btn.confidence:.2f}")
            
        if not buttons:
            print("   No buttons found - this is likely the main issue")
            
            # Try OCR debug
            try:
                import pytesseract
                text = pytesseract.image_to_string(screenshot)
                print(f"   OCR text sample: {repr(text[:100])}")
            except Exception as ocr_e:
                print(f"   OCR test failed: {ocr_e}")
                
    else:
        print("   ✗ No screenshot to test with")
        
except Exception as e:
    print(f"   ✗ Button detection failed: {e}")

# Test 4: Click test (safe coordinates)
print("\n4. Testing click functionality...")
try:
    result = clicker.click(10, 10)  # Safe corner click
    if result:
        print("   ✓ Click function works")
    else:
        print("   ✗ Click function failed")
except Exception as e:
    print(f"   ✗ Click test failed: {e}")

print("\n=== Test Complete ===")
print("Check the results above to identify issues.")
print("Screenshot saved to /tmp/test_screenshot.png for manual inspection.")
