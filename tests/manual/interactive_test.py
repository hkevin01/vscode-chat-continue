#!/usr/bin/env python3
"""
Interactive test for VS Code Copilot Continue button detection.

This script will guide you through testing the automation with a real VS Code Copilot chat.
"""

import sys
import time
from pathlib import Path

# Add project paths
project_root = Path("/home/kevin/Projects/vscode-chat-continue")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print("🤖 VS Code Copilot Continue Button Detection Test")
print("=" * 60)

def wait_for_user(message):
    """Wait for user to complete an action."""
    input(f"\n📋 {message}\nPress Enter when ready...")

def test_detection():
    """Test button detection on current screen."""
    try:
        from src.utils.screen_capture import ScreenCapture
        from src.core.button_finder import ButtonFinder
        from src.core.window_detector import WindowDetector
        
        screen = ScreenCapture()
        finder = ButtonFinder()
        detector = WindowDetector()
        
        print("\n🔍 Analyzing current screen...")
        
        # Capture full screen
        screenshot = screen.capture_screen()
        if not screenshot:
            print("❌ Failed to capture screenshot")
            return False
            
        print(f"✅ Screenshot captured: {screenshot.size[0]}x{screenshot.size[1]}")
        
        # Find VS Code windows
        windows = detector.get_vscode_windows()
        print(f"🪟 Found {len(windows)} VS Code windows")
        
        # Test on full screen first
        print("\n🔍 Testing button detection on full screen...")
        buttons = finder.find_continue_buttons(screenshot)
        print(f"Found {len(buttons)} Continue buttons on full screen")
        
        for i, btn in enumerate(buttons):
            print(f"  Button {i+1}: ({btn.x},{btn.y}) method={btn.method} conf={btn.confidence:.2f}")
            if btn.text:
                print(f"    Text: {repr(btn.text)}")
        
        # Test on each VS Code window
        window_buttons = []
        for i, window in enumerate(windows):
            print(f"\n🪟 Testing window {i+1}: {window.title[:50]}...")
            try:
                window_img = screen.capture_region(window.x, window.y, window.width, window.height)
                if window_img and window_img.size[0] > 100:
                    win_buttons = finder.find_continue_buttons(window_img, window.x, window.y)
                    window_buttons.extend(win_buttons)
                    print(f"   Found {len(win_buttons)} buttons in this window")
                    
                    for j, btn in enumerate(win_buttons):
                        print(f"     Button {j+1}: ({btn.x},{btn.y}) method={btn.method}")
                else:
                    print(f"   ❌ Failed to capture window or too small")
            except Exception as e:
                print(f"   ❌ Window capture error: {e}")
        
        all_buttons = buttons + window_buttons
        print(f"\n📊 TOTAL: {len(all_buttons)} Continue buttons detected")
        
        return len(all_buttons) > 0
        
    except Exception as e:
        print(f"❌ Detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_clicking():
    """Test clicking on detected buttons."""
    try:
        from src.core.click_automator import ClickAutomator
        from src.utils.screen_capture import ScreenCapture
        from src.core.button_finder import ButtonFinder
        
        screen = ScreenCapture()
        finder = ButtonFinder()
        clicker = ClickAutomator()
        
        print("\n🖱️  Testing button clicking...")
        
        # Get current buttons
        screenshot = screen.capture_screen()
        if not screenshot:
            print("❌ Can't capture screenshot for clicking test")
            return False
            
        buttons = finder.find_continue_buttons(screenshot)
        
        if not buttons:
            print("❌ No Continue buttons found to click")
            return False
            
        print(f"🎯 Found {len(buttons)} buttons to test clicking")
        
        for i, button in enumerate(buttons[:3]):  # Test up to 3 buttons
            print(f"\nTesting click on button {i+1}...")
            print(f"  Position: ({button.x}, {button.y})")
            print(f"  Method: {button.method}")
            print(f"  Confidence: {button.confidence:.2f}")
            
            proceed = input("  Click this button? (y/n): ").lower().strip()
            if proceed == 'y':
                print(f"  🖱️  Clicking at ({button.center_x}, {button.center_y})...")
                result = clicker.click(button.center_x, button.center_y)
                if result:
                    print("  ✅ Click executed successfully")
                    time.sleep(2)  # Wait for UI response
                else:
                    print("  ❌ Click failed")
            else:
                print("  ⏭️  Skipped")
        
        return True
        
    except Exception as e:
        print(f"❌ Clicking test failed: {e}")
        return False

def main():
    """Run the interactive test."""
    
    print("\nThis test will help you verify that the Continue button detection works")
    print("with a real VS Code Copilot chat session.")
    print("\nIMPORTANT: You need to have VS Code open with a Copilot chat that shows")
    print("a 'Continue' button before running this test.")
    
    # Step 1: Setup
    wait_for_user("""
🚀 STEP 1: Setup VS Code Copilot Chat
1. Open Visual Studio Code
2. Open the Copilot Chat (Ctrl+Alt+I or from Command Palette)
3. Ask Copilot a question that will result in a long response
4. Wait for the response to be partially displayed
5. Verify you can see a 'Continue' button in the chat
""")
    
    # Step 2: Detection test
    print("\n🔍 STEP 2: Testing Button Detection")
    detection_success = test_detection()
    
    if detection_success:
        print("\n🎉 SUCCESS: Continue buttons detected!")
        
        # Step 3: Click test
        print("\n🖱️  STEP 3: Testing Button Clicking")
        wait_for_user("""
Position your VS Code window so the Continue button is visible.
The test will attempt to click detected Continue buttons.
""")
        
        click_success = test_clicking()
        
        if click_success:
            print("\n🎉 COMPLETE: All tests passed!")
            print("The VS Code Continue button automation should work properly.")
        else:
            print("\n⚠️  PARTIAL: Detection works but clicking had issues")
    else:
        print("\n❌ DETECTION FAILED")
        print("\nPossible reasons:")
        print("1. No Continue button is currently visible")
        print("2. VS Code is not open or Copilot chat is not active")
        print("3. OCR is unable to read the button text (UI styling issues)")
        print("4. The button uses a different text than expected")
        
        print("\nTroubleshooting suggestions:")
        print("1. Ensure VS Code Copilot chat is open and showing a Continue button")
        print("2. Try a different theme (Light theme may work better for OCR)")
        print("3. Make sure the Continue button text is clearly visible")
        print("4. Check if the button says 'Continue', 'Continue response', or similar")

if __name__ == "__main__":
    main()
