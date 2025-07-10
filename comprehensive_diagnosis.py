#!/usr/bin/env python3
"""
Comprehensive diagnostic script to debug Continue button detection
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Setup comprehensive logging
log_file = "/tmp/continue_button_diagnosis.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_dependencies():
    """Test all required dependencies"""
    logger = logging.getLogger("dependencies")
    results = {}
    
    # Test Python imports
    deps = {
        'PIL': 'from PIL import Image',
        'cv2': 'import cv2',
        'pytesseract': 'import pytesseract',
        'numpy': 'import numpy as np',
        'psutil': 'import psutil'
    }
    
    for name, import_cmd in deps.items():
        try:
            exec(import_cmd)
            logger.info(f"✅ {name} imported successfully")
            results[name] = True
        except Exception as e:
            logger.error(f"❌ {name} failed: {e}")
            results[name] = False
    
    # Test tesseract specifically
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        logger.info(f"✅ Tesseract version: {version}")
        results['tesseract_version'] = str(version)
    except Exception as e:
        logger.error(f"❌ Tesseract version check failed: {e}")
        results['tesseract_version'] = None
    
    return results

def test_window_detection():
    """Test VS Code window detection"""
    logger = logging.getLogger("window_detection")
    
    try:
        from core.window_detector import WindowDetector
        detector = WindowDetector()
        
        # Get all processes first
        import psutil
        vscode_procs = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'code' in proc.info['name'].lower():
                    vscode_procs.append(proc.info)
            except:
                pass
        
        logger.info(f"Found {len(vscode_procs)} VS Code-like processes")
        for proc in vscode_procs:
            logger.info(f"  Process: {proc['name']} (PID: {proc['pid']})")
        
        # Get VS Code windows
        windows = detector.get_vscode_windows()
        logger.info(f"Detected {len(windows)} VS Code windows")
        
        for i, window in enumerate(windows):
            logger.info(f"  Window {i+1}: {window.title}")
            logger.info(f"    Position: ({window.x}, {window.y})")
            logger.info(f"    Size: {window.width}x{window.height}")
            logger.info(f"    PID: {window.pid}")
        
        return windows
        
    except Exception as e:
        logger.error(f"Window detection failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def test_screenshot_capture(window):
    """Test screenshot capture on a specific window"""
    logger = logging.getLogger("screenshot")
    
    try:
        from utils.screen_capture import ScreenCapture
        capturer = ScreenCapture()
        
        logger.info(f"Testing screenshot capture for window: {window.title}")
        
        # Try to capture the window
        screenshot = capturer.capture_window_region(window)
        
        if screenshot is None:
            logger.error("❌ Screenshot capture returned None")
            return None
        
        logger.info(f"✅ Screenshot captured: {screenshot.size} pixels")
        
        # Save screenshot for manual inspection
        screenshot_path = f"/tmp/debug_window_{window.window_id}.png"
        screenshot.save(screenshot_path)
        logger.info(f"Screenshot saved to: {screenshot_path}")
        
        # Analyze screenshot content
        if screenshot.mode == 'RGB':
            width, height = screenshot.size
            
            # Sample some pixels to see colors
            logger.info("Sampling pixels from screenshot:")
            for y in [height//4, height//2, 3*height//4]:
                for x in [width//4, width//2, 3*width//4]:
                    if x < width and y < height:
                        pixel = screenshot.getpixel((x, y))
                        logger.info(f"  Pixel at ({x},{y}): RGB{pixel}")
        
        return screenshot
        
    except Exception as e:
        logger.error(f"Screenshot capture failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def test_ocr_on_screenshot(screenshot):
    """Test OCR on the captured screenshot"""
    logger = logging.getLogger("ocr")
    
    try:
        import pytesseract
        
        logger.info("Testing OCR on screenshot...")
        
        # Basic OCR test
        text = pytesseract.image_to_string(screenshot).strip()
        logger.info(f"Basic OCR result: '{text}'")
        
        # Detailed OCR test
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
        
        logger.info("Detailed OCR results (confidence > 10):")
        for i in range(len(data['text'])):
            text_item = data['text'][i].strip()
            conf = data['conf'][i]
            if text_item and conf > 10:
                x, y = data['left'][i], data['top'][i]
                w, h = data['width'][i], data['height'][i]
                logger.info(f"  '{text_item}' at ({x},{y}) size {w}x{h} conf:{conf}")
                
                # Check if this could be a continue button
                if 'continue' in text_item.lower():
                    logger.warning(f"🎯 FOUND 'continue' text: '{text_item}' at ({x},{y})")
        
        return True
        
    except Exception as e:
        logger.error(f"OCR test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_button_detection(screenshot, window):
    """Test the actual button detection algorithm"""
    logger = logging.getLogger("button_detection")
    
    try:
        from core.button_finder import ButtonFinder
        finder = ButtonFinder()
        
        logger.info("Testing button detection algorithm...")
        
        # Try to find buttons
        buttons = finder.find_continue_buttons(screenshot, window.x, window.y)
        
        logger.info(f"Button detection found {len(buttons)} buttons")
        
        for i, button in enumerate(buttons):
            logger.info(f"  Button {i+1}:")
            logger.info(f"    Position: ({button.x}, {button.y})")
            logger.info(f"    Size: {button.width}x{button.height}")
            logger.info(f"    Confidence: {button.confidence:.2f}")
            logger.info(f"    Method: {button.method}")
            logger.info(f"    Text: {button.text}")
        
        return buttons
        
    except Exception as e:
        logger.error(f"Button detection failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def main():
    logger = logging.getLogger("main")
    logger.info("=== VS Code Continue Button Detection Diagnosis ===")
    
    # Test 1: Dependencies
    logger.info("\n1. Testing dependencies...")
    deps = test_dependencies()
    
    # Test 2: Window detection
    logger.info("\n2. Testing window detection...")
    windows = test_window_detection()
    
    if not windows:
        logger.error("❌ No VS Code windows found - cannot continue testing")
        return
    
    # Test 3: Screenshot capture
    logger.info("\n3. Testing screenshot capture...")
    window = windows[0]  # Test first window
    screenshot = test_screenshot_capture(window)
    
    if screenshot is None:
        logger.error("❌ Screenshot capture failed - cannot continue testing")
        return
    
    # Test 4: OCR
    logger.info("\n4. Testing OCR...")
    if deps.get('pytesseract', False):
        test_ocr_on_screenshot(screenshot)
    else:
        logger.error("❌ pytesseract not available - skipping OCR test")
    
    # Test 5: Button detection
    logger.info("\n5. Testing button detection...")
    buttons = test_button_detection(screenshot, window)
    
    # Summary
    logger.info("\n=== DIAGNOSIS SUMMARY ===")
    logger.info(f"Dependencies OK: {all(deps.values())}")
    logger.info(f"Windows found: {len(windows)}")
    logger.info(f"Screenshot captured: {screenshot is not None}")
    logger.info(f"Continue buttons found: {len(buttons) if 'buttons' in locals() else 0}")
    
    if not buttons:
        logger.warning("❌ NO CONTINUE BUTTONS DETECTED")
        logger.info("Possible issues:")
        logger.info("  1. Tesseract OCR not working properly")
        logger.info("  2. Continue button text not visible in current VS Code window")
        logger.info("  3. Button styling prevents OCR recognition")
        logger.info("  4. Screenshot not capturing the chat area")
        logger.info(f"\nCheck saved screenshot: /tmp/debug_window_{window.window_id}.png")
    else:
        logger.info("✅ Continue buttons detected successfully!")

if __name__ == "__main__":
    main()
    print(f"\nFull diagnosis log: {log_file}")
    print("Check /tmp/debug_window_*.png for screenshot analysis")
