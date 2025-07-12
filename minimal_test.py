#!/usr/bin/env python3
"""Minimal test to check if automation components work."""

import sys
from pathlib import Path

# Setup paths
project_root = Path("/home/kevin/Projects/vscode-chat-continue")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def minimal_test():
    """Run minimal automation test."""
    print("Starting minimal automation test...")
    
    try:
        # Import and setup
        from src.utils.gnome_screenshot_fix import setup_screenshot_environment
        setup_screenshot_environment()
        
        from src.core.automation_engine import AutomationEngine
        from src.core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        automation_engine = AutomationEngine(config_manager)
        
        print("✓ Automation engine created successfully")
        
        # Test screenshot capture
        from src.utils.screen_capture import ScreenCapture
        screen_capture = ScreenCapture()
        screenshot = screen_capture.capture_screen()
        
        if screenshot:
            print(f"✓ Screenshot captured: {screenshot.size}")
            
            # Test button detection
            from src.core.button_finder import ButtonFinder
            button_finder = ButtonFinder()
            buttons = button_finder.find_continue_buttons(screenshot)
            
            print(f"✓ Button detection completed: {len(buttons)} buttons found")
            
            if buttons:
                for i, btn in enumerate(buttons):
                    print(f"  Button {i+1}: ({btn.x}, {btn.y}) confidence={btn.confidence:.2f}")
                    
                # Test click on first button
                from src.core.click_automator import ClickAutomator
                click_automator = ClickAutomator()
                
                first_button = buttons[0]
                print(f"✓ Attempting click at ({first_button.x}, {first_button.y})")
                
                success = click_automator.click(first_button.x, first_button.y)
                print(f"✓ Click result: {success}")
                
                return True
            else:
                print("ℹ No Continue buttons found in current screen")
                return False
        else:
            print("✗ Screenshot capture failed")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = minimal_test()
    if result:
        print("🎉 Minimal test passed - automation should work!")
    else:
        print("❌ Minimal test failed - check errors above")
