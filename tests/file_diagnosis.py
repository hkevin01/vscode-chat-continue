#!/usr/bin/env python3
"""
File-based diagnostic test (no terminal output dependency)
"""

import os
import sys
import traceback
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def write_log(message):
    """Write to both file and attempt stdout"""
    log_file = "/tmp/vscode_diagnosis.log"
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    
    try:
        with open(log_file, "a") as f:
            f.write(log_line + "\n")
    except:
        pass
    
    try:
        print(log_line)
    except:
        pass

def main():
    write_log("=== VS Code Continue Button Diagnosis ===")
    
    # Clear previous log
    try:
        with open("/tmp/vscode_diagnosis.log", "w") as f:
            f.write("")
    except:
        pass
    
    # Test 1: Check tesseract system installation
    write_log("1. Checking tesseract system installation...")
    try:
        import subprocess
        result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True)
        if result.returncode == 0:
            write_log(f"✅ Tesseract found at: {result.stdout.strip()}")
        else:
            write_log("❌ Tesseract not found in PATH")
    except Exception as e:
        write_log(f"❌ Error checking tesseract: {e}")
    
    # Test 2: Check Python imports
    write_log("2. Testing Python imports...")
    imports = {}
    
    try:
        import pytesseract
        write_log("✅ pytesseract imported")
        imports['pytesseract'] = True
    except Exception as e:
        write_log(f"❌ pytesseract failed: {e}")
        imports['pytesseract'] = False
    
    try:
        from PIL import Image
        write_log("✅ PIL imported")
        imports['PIL'] = True
    except Exception as e:
        write_log(f"❌ PIL failed: {e}")
        imports['PIL'] = False
    
    try:
        import cv2
        write_log("✅ OpenCV imported")
        imports['cv2'] = True
    except Exception as e:
        write_log(f"❌ OpenCV failed: {e}")
        imports['cv2'] = False
    
    # Test 3: Check OCR functionality
    write_log("3. Testing OCR functionality...")
    if imports.get('pytesseract') and imports.get('PIL'):
        try:
            import pytesseract
            from PIL import Image, ImageDraw

            # Create test image
            img = Image.new('RGB', (150, 40), color='#007ACC')
            draw = ImageDraw.Draw(img)
            draw.text((45, 12), "Continue", fill='white')
            img.save('/tmp/test_button.png')
            write_log("Test image created: /tmp/test_button.png")
            
            # Test OCR
            text = pytesseract.image_to_string(img).strip()
            write_log(f"OCR result: '{text}'")
            
            if 'continue' in text.lower():
                write_log("✅ OCR successfully detected Continue text!")
            else:
                write_log("❌ OCR failed to detect Continue text")
        
        except Exception as e:
            write_log(f"❌ OCR test failed: {e}")
            write_log(f"Error details: {traceback.format_exc()}")
    else:
        write_log("❌ Skipping OCR test - missing dependencies")
    
    # Test 4: Window detection
    write_log("4. Testing window detection...")
    try:
        from core.window_detector import WindowDetector
        detector = WindowDetector()
        windows = detector.get_vscode_windows()
        write_log(f"Found {len(windows)} VS Code windows")
        
        for i, window in enumerate(windows):
            write_log(f"  Window {i+1}: {window.title}")
            write_log(f"    Position: ({window.x}, {window.y})")
            write_log(f"    Size: {window.width}x{window.height}")
    
    except Exception as e:
        write_log(f"❌ Window detection failed: {e}")
        write_log(f"Error details: {traceback.format_exc()}")
    
    # Test 5: Screenshot capability
    write_log("5. Testing screenshot capability...")
    try:
        from utils.screen_capture import ScreenCapture
        capturer = ScreenCapture()
        
        # Try to capture full screen
        screenshot = capturer.capture_screen()
        if screenshot:
            write_log(f"✅ Full screen capture: {screenshot.size}")
            screenshot.save('/tmp/fullscreen_test.png')
            write_log("Full screen saved: /tmp/fullscreen_test.png")
        else:
            write_log("❌ Full screen capture failed")
    
    except Exception as e:
        write_log(f"❌ Screenshot test failed: {e}")
        write_log(f"Error details: {traceback.format_exc()}")
    
    write_log("=== Diagnosis Complete ===")
    write_log("Check /tmp/vscode_diagnosis.log for full results")
    write_log("Check /tmp/test_button.png and /tmp/fullscreen_test.png")

if __name__ == "__main__":
    main()
