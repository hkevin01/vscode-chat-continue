#!/usr/bin/env python3
"""
Simple test script to verify screenshot functionality works across platforms.
This tests the core screenshot capture without VS Code detection.
"""

import logging
import platform
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.screen_capture import ScreenCapture


def test_screenshot_functionality():
    """Test basic screenshot functionality."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info(f"Testing screenshot functionality on {platform.system()}")

    screen_capture = ScreenCapture()

    # Test full screen capture
    logger.info("Testing full screen capture...")
    full_screen = screen_capture.capture_screen()

    if full_screen:
        logger.info(f"✅ Full screen capture successful: {full_screen.size}")

        # Save test screenshot
        test_path = "/tmp/test_fullscreen.png"
        if screen_capture.save_image(full_screen, test_path):
            logger.info(f"✅ Screenshot saved to {test_path}")
        else:
            logger.error("❌ Failed to save screenshot")
    else:
        logger.error("❌ Full screen capture failed")
        return False

    # Test region capture (small region in top-left)
    logger.info("Testing region capture...")
    region = screen_capture.capture_region(100, 100, 200, 200)

    if region:
        logger.info(f"✅ Region capture successful: {region.size}")

        # Save test region
        region_path = "/tmp/test_region.png"
        if screen_capture.save_image(region, region_path):
            logger.info(f"✅ Region screenshot saved to {region_path}")
        else:
            logger.error("❌ Failed to save region screenshot")
    else:
        logger.error("❌ Region capture failed")
        return False

    # Test screen size detection
    logger.info("Testing screen size detection...")
    screen_size = screen_capture.get_screen_size()
    logger.info(f"✅ Detected screen size: {screen_size}")

    logger.info("🎉 All screenshot tests passed!")
    return True


if __name__ == "__main__":
    success = test_screenshot_functionality()
    sys.exit(0 if success else 1)
