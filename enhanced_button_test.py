#!/usr/bin/env python3
"""
Test the enhanced button detection with fallback methods
"""

import logging
import os
import sys

# Setup file logging
log_file = "/tmp/enhanced_button_test.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    logger = logging.getLogger(__name__)
    logger.info("Starting enhanced Continue button detection test")
    
    try:
        # Import components
        from core.button_finder import ButtonFinder
        from core.window_detector import WindowDetector
        from utils.screen_capture import ScreenCapture
        
        logger.info("Components imported successfully")
        
        # Initialize
        window_detector = WindowDetector()
        button_finder = ButtonFinder()
        screen_capture = ScreenCapture()
        
        # Find VS Code windows  
        windows = window_detector.find_vscode_windows()
        logger.info(f"Found {len(windows)} VS Code windows")
        
        if not windows:
            logger.warning("No VS Code windows found!")
            return
        
        # Test first window
        window = windows[0]
        logger.info(f"Testing window: {window.title}")
        
        # Capture screenshot
        screenshot = screen_capture.capture_window_region(window)
        if screenshot is None:
            logger.error("Failed to capture screenshot")
            return
        
        logger.info(f"Screenshot captured: {screenshot.size}")
        
        # Save for debugging
        screenshot.save("/tmp/debug_screenshot.png")
        logger.info("Screenshot saved to /tmp/debug_screenshot.png")
        
        # Try enhanced button detection
        buttons = button_finder.find_continue_buttons(screenshot, window.x, window.y)
        logger.info(f"Enhanced detection found {len(buttons)} buttons")
        
        if buttons:
            for i, button in enumerate(buttons):
                logger.info(f"Button {i+1}:")
                logger.info(f"  Position: ({button.x}, {button.y})")
                logger.info(f"  Size: {button.width}x{button.height}")
                logger.info(f"  Confidence: {button.confidence:.2f}")
                logger.info(f"  Method: {button.method}")
                logger.info(f"  Text: {button.text}")
        else:
            logger.warning("No Continue buttons detected with enhanced methods")
            
            # Try manual blue detection as last resort
            logger.info("Trying manual blue pixel detection...")
            blue_count = 0
            if screenshot.mode == 'RGB':
                width, height = screenshot.size
                for y in range(0, min(height, 100), 10):
                    for x in range(0, min(width, 200), 10):
                        pixel = screenshot.getpixel((x, y))
                        # Check for VS Code blue-ish colors
                        if (pixel[2] > 150 and pixel[0] < 100 and pixel[1] < 150):
                            blue_count += 1
                            
            logger.info(f"Found {blue_count} blue-ish pixels in sample area")
            
        logger.info("Test completed successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
    print(f"Test completed. Check detailed logs: {log_file}")
