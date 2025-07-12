#!/usr/bin/env python3
"""
Simple screenshot test to verify gnome-screenshot is not being called
"""

import os
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_screenshot_methods():
    """Test different screenshot methods"""
    log_file = "/tmp/screenshot_test.log"
    
    with open(log_file, "w") as f:
        f.write("=== Screenshot Method Test ===\n")
        
        # Test 1: Check if scrot is available
        try:
            result = subprocess.run(['which', 'scrot'], capture_output=True, text=True)
            if result.returncode == 0:
                f.write(f"✅ scrot found at: {result.stdout.strip()}\n")
            else:
                f.write("❌ scrot not found\n")
        except Exception as e:
            f.write(f"❌ scrot check failed: {e}\n")
        
        # Test 2: Test scrot screenshot
        try:
            result = subprocess.run(['scrot', '/tmp/scrot_test.png'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                f.write("✅ scrot screenshot successful\n")
                if os.path.exists('/tmp/scrot_test.png'):
                    size = os.path.getsize('/tmp/scrot_test.png')
                    f.write(f"  Screenshot size: {size} bytes\n")
                    os.remove('/tmp/scrot_test.png')
            else:
                f.write(f"❌ scrot failed: {result.stderr}\n")
        except Exception as e:
            f.write(f"❌ scrot test failed: {e}\n")
        
        # Test 3: Test our screen capture module
        try:
            from utils.screen_capture import ScreenCapture
            capturer = ScreenCapture()
            f.write("✅ ScreenCapture module imported\n")
            
            # Test full screen capture
            screenshot = capturer.capture_screen()
            if screenshot:
                f.write(f"✅ Full screen capture: {screenshot.size}\n")
                screenshot.save('/tmp/test_fullscreen.png')
                f.write("  Screenshot saved to /tmp/test_fullscreen.png\n")
            else:
                f.write("❌ Full screen capture failed\n")
                
        except Exception as e:
            f.write(f"❌ ScreenCapture test failed: {e}\n")
            import traceback
            f.write(f"Traceback: {traceback.format_exc()}\n")
        
        # Test 4: Test window detection and capture
        try:
            from core.window_detector import WindowDetector
            detector = WindowDetector()
            windows = detector.get_vscode_windows()
            f.write(f"✅ Found {len(windows)} VS Code windows\n")
            
            if windows:
                window = windows[0]
                f.write(f"Testing window: {window.title}\n")
                
                screenshot = capturer.capture_window_region(window)
                if screenshot:
                    f.write(f"✅ Window capture: {screenshot.size}\n")
                    screenshot.save('/tmp/test_window.png')
                    f.write("  Window screenshot saved to /tmp/test_window.png\n")
                else:
                    f.write("❌ Window capture failed\n")
                    
        except Exception as e:
            f.write(f"❌ Window capture test failed: {e}\n")
        
        f.write("\n=== Test Complete ===\n")
    
    print(f"Screenshot test completed. Check: {log_file}")

if __name__ == "__main__":
    test_screenshot_methods()
