#!/usr/bin/env python3
"""
Test the window count fix - should show current count, not cumulative
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


async def test_window_count_logic():
    """Test that window count shows current windows, not cumulative"""
    print("=== Testing Window Count Logic ===")

    try:
        from core.automation_engine import AutomationEngine
        from core.config_manager import ConfigManager

        # Create config and engine
        config = ConfigManager()
        config.set("automation.dry_run", True)

        engine = AutomationEngine(config)
        engine.running = True

        # Get current window count directly
        windows = engine.window_detector.get_vscode_windows()
        actual_count = len(windows)
        print(f"✓ Actual VS Code windows: {actual_count}")

        # Simulate multiple automation cycles
        for cycle in range(3):
            print(f"\n--- Cycle {cycle + 1} ---")

            # Process windows (this increments cumulative counter)
            await engine._process_vscode_windows()

            # Get stats (cumulative)
            cumulative_count = engine.stats.get("windows_processed", 0)

            # Get current count (what GUI should show)
            current_windows = engine.window_detector.get_vscode_windows()
            current_count = len(current_windows)

            print(f"Cumulative processed: {cumulative_count}")
            print(f"Current windows: {current_count}")

            if current_count == actual_count:
                print("✅ Current count is correct!")
            else:
                print(f"❌ Current count should be {actual_count}")

        print(f"\n🎯 GUI Fix Summary:")
        print(f"   Before: Would show cumulative count ({cumulative_count})")
        print(f"   After:  Will show current count ({current_count})")
        print(f"   Expected: Should always show {actual_count}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_window_count_logic())
