#!/usr/bin/env python3
"""Direct test of full automation pipeline."""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent / "src")
sys.path.insert(0, src_path)

from core.automation_engine import AutomationEngine
from core.config_manager import ConfigManager


async def test_full_automation():
    """Test the complete automation pipeline."""
    print("🤖 Testing Full Automation Pipeline...")

    # Initialize components
    config_manager = ConfigManager()

    # Enable dry run to see what would happen
    config_manager.set("automation.dry_run", True)
    config_manager.set("automation.interval_seconds", 3)

    print("⚙️  Configuration:")
    print(f"   Dry run: {config_manager.is_dry_run()}")
    print(f"   Interval: {config_manager.get('automation.interval_seconds')}s")

    # Initialize automation engine
    automation = AutomationEngine(config_manager)

    print("\n🔍 Testing one automation cycle...")

    try:
        # Run one cycle of window processing
        await automation._process_vscode_windows()

        # Get statistics
        stats = automation.get_statistics()
        print(f"\n📊 Automation Statistics:")
        print(f"   Windows processed: {stats.get('windows_processed', 0)}")
        print(f"   Buttons found: {stats.get('buttons_found', 0)}")
        print(f"   Clicks attempted: {stats.get('clicks_attempted', 0)}")
        print(f"   Clicks successful: {stats.get('clicks_successful', 0)}")
        print(f"   Errors: {stats.get('errors', 0)}")

        if stats.get("buttons_found", 0) > 0:
            print("✅ SUCCESS: Buttons were found!")
            if stats.get("clicks_attempted", 0) > 0:
                print("✅ SUCCESS: Click attempts were made!")
            else:
                print("⚠️  WARNING: No click attempts made")
        else:
            print("❌ ISSUE: No buttons were found")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("Full Automation Pipeline Test")
    print("=" * 60)

    # Run the async test
    asyncio.run(test_full_automation())

    print("\n" + "=" * 60)
    print("Test completed. Check above for results.")
    print("=" * 60)
