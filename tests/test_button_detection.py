#!/usr/bin/env python3
"""
Test button detection specifically to see what's happening.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.button_finder import ButtonFinder
from src.core.config_manager import ConfigManager
from src.core.window_detector import WindowDetector
from src.utils.screen_capture import ScreenCapture


def main():
    """Test button detection process."""
    print("🔍 Button Detection Test")
    print("=" * 40)
    
    # Set up components
    config = ConfigManager()
    detector = WindowDetector()
    screen_capture = ScreenCapture()
    button_finder = ButtonFinder(config)
    
    # Get VS Code windows
    windows = detector.get_vscode_windows()
    print(f"Found {len(windows)} VS Code windows")
    
    if not windows:
        print("❌ No windows to test with")
        return
    
    # Test with first window
    window = windows[0]
    print(f"\n🪟 Testing with window: {window.title[:50]}...")
    print(f"   Position: ({window.x}, {window.y})")
    print(f"   Size: {window.width}x{window.height}")
    
    # Try to capture the window
    print("\n📸 Capturing window...")
    try:
        screenshot = screen_capture.capture_window(
            window.window_id, window.x, window.y, window.width, window.height
        )
        
        if screenshot:
            print(f"✅ Screenshot captured: {screenshot.size}")
            
            # Try to find buttons
            print("\n🔍 Looking for Continue buttons...")
            buttons = button_finder.find_continue_buttons(
                screenshot, window.x, window.y
            )
            
            print(f"Found {len(buttons)} Continue buttons:")
            for i, button in enumerate(buttons):
                print(f"  {i+1}. Position: ({button.x}, {button.y})")
                print(f"     Size: {button.width}x{button.height}")
                print(f"     Confidence: {button.confidence:.2f}")
                print(f"     Method: {button.method}")
                if button.text:
                    print(f"     Text: {button.text}")
            
            if len(buttons) == 0:
                print("❌ No Continue buttons found")
                print("💡 This might be normal if no chat conversations are active")
            else:
                print("✅ Button detection working!")
                
        else:
            print("❌ Failed to capture window screenshot")
            
    except Exception as e:
        print(f"❌ Error in button detection test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
