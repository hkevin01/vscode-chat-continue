#!/usr/bin/env python3
"""
Quick test script to check Continue button detection
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.button_finder import ButtonFinder
from core.window_detector import WindowDetector
from utils.screen_capture import ScreenCapture


def main():
    print("Testing Continue button detection...")
    
    # Initialize components
    window_detector = WindowDetector()
    button_finder = ButtonFinder()
    screen_capture = ScreenCapture()
    
    # Get VS Code windows
    vscode_windows = window_detector.find_vscode_windows()
    print(f"Found {len(vscode_windows)} VS Code windows")
    
    for i, window in enumerate(vscode_windows):
        print(f"\nTesting window {i+1}: {window['title']}")
        print(f"Window position: ({window['x']}, {window['y']})")
        print(f"Window size: {window['width']}x{window['height']}")
        
        # Capture screenshot
        screenshot = screen_capture.capture_window_region(window)
        if screenshot is not None:
            print(f"Screenshot captured: {screenshot.shape}")
            
            # Look for Continue buttons
            buttons = button_finder.find_continue_buttons(screenshot)
            print(f"Found {len(buttons)} Continue buttons")
            
            for j, button in enumerate(buttons):
                abs_x = window['x'] + button['x']
                abs_y = window['y'] + button['y']
                print(f"  Button {j+1}: ({abs_x}, {abs_y}) confidence: {button['confidence']:.2f}")
                
                # Save debug image if we found buttons
                if buttons:
                    import cv2
                    debug_image = screenshot.copy()
                    cv2.rectangle(debug_image, 
                                (button['x'], button['y']), 
                                (button['x'] + button['width'], button['y'] + button['height']),
                                (0, 255, 0), 2)
                    cv2.imwrite(f'/tmp/continue_button_debug_{i}_{j}.png', debug_image)
                    print(f"  Debug image saved: /tmp/continue_button_debug_{i}_{j}.png")
        else:
            print("Failed to capture screenshot")

if __name__ == "__main__":
    main()
