#!/usr/bin/env python3
"""
Quick test to validate core automation components without infinite loops.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.automation_engine import AutomationEngine
from core.config_manager import ConfigManager


async def test_automation_components():
    """Test automation components without starting the main loop."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("🧪 Testing automation components...")

    try:
        # Initialize config and automation engine
        config_manager = ConfigManager()
        automation_engine = AutomationEngine(config_manager)

        logger.info("✅ Components initialized successfully")

        # Test window detection
        logger.info("🔍 Testing window detection...")
        windows = automation_engine.window_detector.get_vscode_windows()
        logger.info(f"✅ Found {len(windows)} VS Code windows")

        if windows:
            # Test screenshot capture on first window
            logger.info("📸 Testing screenshot capture...")
            first_window = windows[0]
            screenshot = automation_engine.screen_capture.capture_window(
                0, first_window.x, first_window.y, first_window.width, first_window.height
            )

            if screenshot:
                logger.info(f"✅ Screenshot captured: {screenshot.size}")

                # Test button detection
                logger.info("🔎 Testing button detection...")
                buttons = automation_engine.button_finder.find_continue_buttons(
                    screenshot, first_window.x, first_window.y
                )
                logger.info(f"✅ Found {len(buttons)} potential Continue buttons")

            else:
                logger.warning("⚠️ Screenshot capture failed")

        logger.info("🎉 All component tests completed successfully!")

    except Exception as e:
        logger.error(f"❌ Component test failed: {e}", exc_info=True)
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(test_automation_components())
    sys.exit(0 if success else 1)
