"""
A test script to validate the screen capture functionality and ensure the gnome-screenshot error is resolved.
"""

import os
import sys
import traceback

# Ensure the gnome_screenshot_fix is applied before any other imports
try:
    import gnome_screenshot_fix
except ImportError:
    # If the fix is not in the path, add the project root to the path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    try:
        import gnome_screenshot_fix
    except ImportError:
        print("CRITICAL: Could not import gnome_screenshot_fix. The test may not run correctly.")
        # Decide if you want to exit or continue without the fix
        # For this test, we'll continue to see if the error still occurs
        pass


from src.utils.helpers import get_project_root
from src.utils.screen_capture import ScreenCapture


def run_test():
    """
    Runs the screen capture test.
    """
    print("Starting final screenshot test...")
    try:
        # Initialize ScreenCapture
        capture = ScreenCapture()
        
        # Define a path for the screenshot
        project_root = get_project_root()
        if not project_root:
            print("Error: Could not determine project root.")
            return

        output_dir = os.path.join(project_root, "tmp")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        screenshot_path = os.path.join(output_dir, "final_test_screenshot.png")

        # Take a screenshot
        print(f"Attempting to capture a screenshot to: {screenshot_path}")
        path = capture.capture_screen(output_path=screenshot_path)

        if path and os.path.exists(path):
            print(f"SUCCESS: Screenshot captured successfully at {path}")
            print(f"File size: {os.path.getsize(path)} bytes")
        else:
            print("ERROR: Screenshot capture failed. No file was created.")

        # Test region capture
        region = (100, 100, 400, 400) # x, y, width, height
        region_screenshot_path = os.path.join(output_dir, "final_test_region_screenshot.png")
        print(f"Attempting to capture a region {region} to: {region_screenshot_path}")
        region_path = capture.capture_region(region, output_path=region_screenshot_path)

        if region_path and os.path.exists(region_path):
            print(f"SUCCESS: Region screenshot captured successfully at {region_path}")
            print(f"File size: {os.path.getsize(region_path)} bytes")
        else:
            print("ERROR: Region screenshot capture failed.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
