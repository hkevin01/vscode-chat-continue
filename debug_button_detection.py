#!/usr/bin/env python3
"""
Test Continue button detection with detailed logging
"""

import logging
import os
import sys
from datetime import datetime

# Set up logging to file
log_file = "/tmp/button_detection_debug.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    logger = logging.getLogger(__name__)
    logger.info("Starting Continue button detection test")
    
    try:
        from core.button_finder import ButtonFinder
        from core.window_detector import WindowDetector
        from utils.screen_capture import ScreenCapture
        
        logger.info("All imports successful")
        
        # Initialize components
        window_detector = WindowDetector()
        button_finder = ButtonFinder()
        screen_capture = ScreenCapture()
        
        # Get VS Code windows
        windows = window_detector.find_vscode_windows()
        logger.info(f"Found {len(windows)} VS Code windows")
        
        if not windows:
            logger.warning("No VS Code windows found!")
            return
        
        # Test on the first window
        window = windows[0]
        logger.info(f"Testing window: {window.title}")
        logger.info(f"Window position: ({window.x}, {window.y})")
        logger.info(f"Window size: {window.width}x{window.height}")
        
        # Capture screenshot
        screenshot = screen_capture.capture_window_region(window)
        if screenshot is None:
            logger.error("Failed to capture screenshot")
            return
        
        logger.info(f"Screenshot captured successfully: {screenshot.size}")
        
        # Save screenshot for manual inspection
        screenshot.save("/tmp/vscode_screenshot_debug.png")
        logger.info("Screenshot saved to /tmp/vscode_screenshot_debug.png")
        
        # Try to find Continue buttons
        logger.info("Searching for Continue buttons...")
        buttons = button_finder.find_continue_buttons(screenshot, window.x, window.y)
        
        logger.info(f"Detection complete. Found {len(buttons)} buttons")
        
        for i, button in enumerate(buttons):
            logger.info(f"Button {i+1}:")
            logger.info(f"  Position: ({button.x}, {button.y})")
            logger.info(f"  Size: {button.width}x{button.height}")
            logger.info(f"  Confidence: {button.confidence:.2f}")
            logger.info(f"  Method: {button.method}")
            logger.info(f"  Text: {button.text}")
        
        if not buttons:
            logger.warning("No Continue buttons detected!")
            logger.info("Check the screenshot at /tmp/vscode_screenshot_debug.png")
            logger.info("and the log file at /tmp/button_detection_debug.log")
        
    except Exception as e:
        logger.error(f"Error during detection: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
    print(f"Test completed. Check logs at: {log_file}")
