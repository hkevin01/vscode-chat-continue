#!/usr/bin/env python3
"""
Comprehensive debug script for button detection with extensive logging.
This will show exactly what OCR and other methods are detecting.
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.button_finder import ButtonFinder
from core.config_manager import ConfigManager
from core.window_detector import WindowDetector
from utils.screen_capture import ScreenCapture


def setup_debug_logging():
    """Set up detailed debug logging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("/tmp/button_debug.log")],
    )


def debug_button_detection():
    """Test button detection with extensive debugging."""
    setup_debug_logging()
    logger = logging.getLogger(__name__)

    logger.info("=== Starting comprehensive button detection debug ===")

    try:
        # Initialize components
        config_manager = ConfigManager()
        window_detector = WindowDetector()
        button_finder = ButtonFinder(config_manager)
        screen_capture = ScreenCapture()

        # Find VS Code windows
        logger.info("Finding VS Code windows...")
        windows = window_detector.get_vscode_windows()
        logger.info(f"Found {len(windows)} VS Code windows")

        if not windows:
            logger.error("No VS Code windows found!")
            return

        # Test each window
        for i, window in enumerate(windows):
            logger.info(f"\n=== Testing window {i+1}: {window} ===")

            # Capture screenshot
            logger.info("Capturing screenshot...")
            screenshot = screen_capture.capture_window(
                0, window.x, window.y, window.width, window.height
            )

            if screenshot is None:
                logger.error(f"Failed to capture screenshot for window {i+1}")
                continue

            # Save screenshot for manual inspection
            screenshot_path = f"/tmp/vscode_window_{i+1}_debug.png"
            screenshot.save(screenshot_path)
            logger.info(f"Screenshot saved to: {screenshot_path}")

            # Test button detection
            logger.info("Running button detection...")
            buttons = button_finder.find_continue_buttons(screenshot, window.x, window.y)

            logger.info(f"Found {len(buttons)} buttons")
            for j, button in enumerate(buttons):
                logger.info(f"Button {j+1}: {button}")

            # Test OCR specifically with detailed output
            logger.info("\n--- OCR Analysis ---")
            try:
                import pytesseract

                # Test different OCR configurations
                configs = [
                    r"--oem 3 --psm 6",
                    r"--oem 3 --psm 8",
                    r"--oem 3 --psm 7",
                    r"--oem 1 --psm 6",
                ]

                for config in configs:
                    logger.info(f"Testing OCR config: {config}")
                    try:
                        # Get all text with data
                        ocr_data = pytesseract.image_to_data(
                            screenshot, config=config, output_type=pytesseract.Output.DICT
                        )

                        # Log all detected text
                        for k in range(len(ocr_data["text"])):
                            text = ocr_data["text"][k].strip()
                            conf = ocr_data["conf"][k]
                            if text and conf > 10:
                                logger.info(
                                    f"  OCR: '{text}' (conf: {conf}) at "
                                    f"({ocr_data['left'][k]}, {ocr_data['top'][k]})"
                                )

                        # Also get simple text output
                        simple_text = pytesseract.image_to_string(screenshot, config=config)
                        logger.info(f"  Simple OCR output: {repr(simple_text)}")

                    except Exception as e:
                        logger.error(f"  OCR config {config} failed: {e}")

            except ImportError:
                logger.warning("pytesseract not available for detailed OCR analysis")

            # Test color detection specifically
            logger.info("\n--- Color Detection Analysis ---")

            # Sample some pixels from the right side of the image (where Continue button likely is)
            width, height = screenshot.size
            right_third = width * 2 // 3

            logger.info(f"Image size: {width}x{height}")
            logger.info(f"Sampling colors from right third (x >= {right_third})")

            # Sample pixels in a grid on the right side
            for y in range(height // 4, height * 3 // 4, 20):
                for x in range(right_third, width - 10, 20):
                    try:
                        pixel = screenshot.getpixel((x, y))
                        # Check if it's bluish (VS Code button color)
                        if (
                            pixel[2] > pixel[0] and pixel[2] > pixel[1] and pixel[2] > 100
                        ):  # More blue than red/green
                            logger.info(f"  Blue-ish pixel at ({x}, {y}): {pixel}")
                    except Exception:
                        pass

    except Exception as e:
        logger.error(f"Debug script failed: {e}", exc_info=True)


if __name__ == "__main__":
    debug_button_detection()
