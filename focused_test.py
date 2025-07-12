#!/usr/bin/env python3
"""
Focused test for button clicking issues - targets the specific workflow.
"""

import sys
import time
from pathlib import Path

# Setup paths
project_root = Path("/home/kevin/Projects/vscode-chat-continue")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def focused_button_test():
    """Test the specific button detection and clicking workflow."""
    print("🎯 Focused Button Detection & Click Test")
    print("=" * 50)
    
    # Step 1: Setup environment
    print("\n1. Setting up environment...")
    try:
        from src.utils.gnome_screenshot_fix import setup_screenshot_environment
        setup_screenshot_environment()
        print("   ✓ gnome-screenshot protection enabled")
    except Exception as e:
        print(f"   ✗ Environment setup failed: {e}")
        return False
    
    # Step 2: Take screenshot
    print("\n2. Capturing screenshot...")
    try:
        from src.utils.screen_capture import ScreenCapture
        screen_capture = ScreenCapture()
        screenshot = screen_capture.capture_screen()
        
        if not screenshot:
            print("   ✗ No screenshot captured")
            return False
            
        w, h = screenshot.size
        print(f"   ✓ Screenshot: {w}x{h} pixels")
        
        # Check for the tiny screenshot issue
        if w < 100 or h < 100:
            print(f"   ⚠ WARNING: Screenshot too small! This is likely the main issue.")
            print(f"   This suggests window region capture is failing.")
            return False
            
        # Save screenshot for manual inspection
        screenshot.save("/tmp/automation_screenshot.png")
        print("   ✓ Screenshot saved to /tmp/automation_screenshot.png")
        
    except Exception as e:
        print(f"   ✗ Screenshot capture failed: {e}")
        return False
    
    # Step 3: OCR and text detection
    print("\n3. Testing OCR capabilities...")
    try:
        import pytesseract

        # Test basic OCR
        full_text = pytesseract.image_to_string(screenshot)
        print(f"   ✓ OCR extracted {len(full_text)} characters")
        print(f"   Sample text: {repr(full_text[:100])}")
        
        # Check if "Continue" appears in the text
        if "continue" in full_text.lower():
            print("   ✓ Found 'continue' text in OCR output")
        else:
            print("   ⚠ No 'continue' text found in OCR output")
            print("   This suggests the Continue button is not visible or readable")
            
    except Exception as e:
        print(f"   ✗ OCR test failed: {e}")
        return False
    
    # Step 4: Button detection
    print("\n4. Testing button detection...")
    try:
        from src.core.button_finder import ButtonFinder
        button_finder = ButtonFinder()
        
        buttons = button_finder.find_continue_buttons(screenshot)
        print(f"   Found {len(buttons)} Continue buttons")
        
        if buttons:
            for i, btn in enumerate(buttons):
                print(f"   Button {i+1}: ({btn.x}, {btn.y}) size={btn.width}x{btn.height} conf={btn.confidence:.2f}")
        else:
            print("   ⚠ No buttons detected")
            print("   This is the core issue - button detection is failing")
            return False
            
    except Exception as e:
        print(f"   ✗ Button detection failed: {e}")
        return False
    
    # Step 5: Click test
    print("\n5. Testing click functionality...")
    try:
        from src.core.click_automator import ClickAutomator
        click_automator = ClickAutomator()
        
        # Test click at safe location first
        print("   Testing safe click at (50, 50)...")
        safe_result = click_automator.click(50, 50)
        print(f"   Safe click result: {safe_result}")
        
        if buttons and safe_result:
            best_button = buttons[0]
            print(f"   Testing click on detected button at ({best_button.x}, {best_button.y})...")
            
            # Give user time to see what's happening
            print("   Clicking in 3 seconds... (Ctrl+C to cancel)")
            time.sleep(3)
            
            button_result = click_automator.click(best_button.x, best_button.y)
            print(f"   Button click result: {button_result}")
            
            return button_result
        else:
            print("   ⚠ Skipping button click test (no buttons or click failed)")
            return False
            
    except KeyboardInterrupt:
        print("   Test cancelled by user")
        return False
    except Exception as e:
        print(f"   ✗ Click test failed: {e}")
        return False

def main():
    print("VS Code Continue Button - Focused Test")
    print("This test will systematically check each step of the automation.")
    print("\nMake sure:")
    print("- VS Code is running")
    print("- A Copilot chat session is open")
    print("- The Continue button is visible")
    print("\nPress Enter to start or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("Cancelled.")
        return
    
    success = focused_button_test()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: All tests passed!")
        print("The automation should now work correctly.")
    else:
        print("❌ FAILED: One or more tests failed.")
        print("Check the specific error messages above.")
        print("Common issues:")
        print("- Screenshot too small (region capture issue)")
        print("- No Continue button visible")
        print("- OCR not finding button text")
        print("- Click permissions issue")

if __name__ == "__main__":
    main()
