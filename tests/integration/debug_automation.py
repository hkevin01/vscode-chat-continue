#!/usr/bin/env python3
"""Debug the automation engine processing."""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent / "src")
sys.path.insert(0, src_path)

from core.automation_engine import AutomationEngine
from core.config_manager import ConfigManager


async def debug_automation():
    """Debug automation step by step."""
    print("🔧 Debugging Automation Engine...")

    # Set up detailed logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Initialize components
    config_manager = ConfigManager()
    config_manager.set("automation.dry_run", True)

    automation = AutomationEngine(config_manager)

    print("\n1. Testing window detection...")
    windows = automation.window_detector.get_vscode_windows()
    print(f"   Found {len(windows)} VS Code windows")

    for i, window in enumerate(windows, 1):
        print(f"   Window {i}: {window.title[:50]}")
        print(f"      Size: {window.width}x{window.height}")
        print(f"      Position: ({window.x}, {window.y})")

    if not windows:
        print("❌ No windows found - stopping debug")
        return

    print("\n2. Testing screenshot capture...")
    window = windows[0]
    screenshot = automation.screen_capture.capture_screen()

    if screenshot:
        print(f"   Screenshot captured: {screenshot.width}x{screenshot.height}")

        print("\n3. Testing button detection...")
        buttons = automation.button_finder.find_continue_buttons(screenshot, window.x, window.y)

        print(f"   Found {len(buttons)} buttons")
        for i, btn in enumerate(buttons, 1):
            print(f"      Button {i}: {btn.method} at ({btn.center_x}, {btn.center_y})")
            print(f"         Confidence: {btn.confidence}, Text: {btn.text}")
    else:
        print("   ❌ No screenshot captured")

    print("\n4. Testing full window processing...")

    # Manually process each window with debug info
    for i, window in enumerate(windows, 1):
        print(f"\n   Processing window {i}: {window.title[:30]}...")

        # Check if window should be processed
        should_process = automation._should_process_window(window)
        print(f"   Should process: {should_process}")

        if should_process:
            await automation._process_window(window)
        else:
            print("   Skipping window due to filters")

    # Get final stats
    stats = automation.get_statistics()
    print(f"\n📊 Final Statistics:")
    print(f"   Windows processed: {stats.get('windows_processed', 0)}")
    print(f"   Buttons found: {stats.get('buttons_found', 0)}")
    print(f"   Clicks attempted: {stats.get('clicks_attempted', 0)}")


if __name__ == "__main__":
    asyncio.run(debug_automation())
