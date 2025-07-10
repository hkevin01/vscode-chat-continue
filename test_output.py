#!/usr/bin/env python3
"""
Simple test script that saves output to a file
"""

import os
import sys
from datetime import datetime

# Save output to file
output_file = "/tmp/vscode_continue_test.log"

try:
    with open(output_file, "w") as f:
        f.write(f"Test started at: {datetime.now()}\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"Current working directory: {os.getcwd()}\n")
        
        # Add src to path
        src_path = os.path.join(os.getcwd(), 'src')
        sys.path.append(src_path)
        f.write(f"Added to path: {src_path}\n")
        
        # Test imports
        try:
            from core.window_detector import WindowDetector
            f.write("✅ WindowDetector imported successfully\n")
            
            from core.button_finder import ButtonFinder
            f.write("✅ ButtonFinder imported successfully\n")
            
            from utils.screen_capture import ScreenCapture
            f.write("✅ ScreenCapture imported successfully\n")
            
            # Test window detection
            window_detector = WindowDetector()
            windows = window_detector.find_vscode_windows()
            f.write(f"Found {len(windows)} VS Code windows\n")
            
            for i, window in enumerate(windows):
                f.write(f"  Window {i+1}: {window['title']} at ({window['x']}, {window['y']})\n")
            
            # Test button detection on first window if available
            if windows:
                f.write("\nTesting button detection on first window...\n")
                screen_capture = ScreenCapture()
                button_finder = ButtonFinder()
                
                screenshot = screen_capture.capture_window_region(windows[0])
                if screenshot is not None:
                    f.write(f"Screenshot captured: {screenshot.shape}\n")
                    
                    buttons = button_finder.find_continue_buttons(screenshot)
                    f.write(f"Found {len(buttons)} Continue buttons\n")
                    
                    for j, button in enumerate(buttons):
                        abs_x = windows[0]['x'] + button['x']
                        abs_y = windows[0]['y'] + button['y']
                        f.write(f"  Button {j+1}: ({abs_x}, {abs_y}) confidence: {button['confidence']:.2f}\n")
                else:
                    f.write("Failed to capture screenshot\n")
            
        except Exception as e:
            f.write(f"❌ Import/execution error: {e}\n")
            import traceback
            f.write(f"Traceback:\n{traceback.format_exc()}\n")
            
except Exception as e:
    print(f"Failed to write to {output_file}: {e}")

print(f"Test completed. Check output in {output_file}")
