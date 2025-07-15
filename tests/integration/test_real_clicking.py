#!/usr/bin/env python3
"""Test real automation with actual clicking."""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent / "src")
sys.path.insert(0, src_path)

from core.automation_engine import AutomationEngine
from core.config_manager import ConfigManager


async def test_real_clicking():
    """Test real automation with actual clicking."""
    print("🖱️  Testing REAL Automation with Clicking...")
    print("⚠️  WARNING: This will actually click on your screen!")
    print("   Make sure VS Code is positioned correctly.")

    # Wait for user confirmation
    input("Press ENTER to continue, or Ctrl+C to cancel...")

    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Initialize components
    config_manager = ConfigManager()
    config_manager.set("automation.dry_run", False)  # REAL CLICKING
    config_manager.set("automation.max_clicks_per_window", 1)  # Only 1 click per window

    automation = AutomationEngine(config_manager)

    print("\n🎯 Running ONE automation cycle with REAL clicking...")
    print("   (Only 1 click per window to avoid spam)")

    try:
        # Run one cycle
        await automation._process_vscode_windows()

        # Get statistics
        stats = automation.get_statistics()
        print(f"\n📊 Results:")
        print(f"   Windows processed: {stats.get('windows_processed', 0)}")
        print(f"   Buttons found: {stats.get('buttons_found', 0)}")
        print(f"   Clicks attempted: {stats.get('clicks_attempted', 0)}")
        print(f"   Clicks successful: {stats.get('clicks_successful', 0)}")
        print(f"   Errors: {stats.get('errors', 0)}")

        if stats.get("clicks_attempted", 0) > 0:
            print("✅ SUCCESS: Real clicks were attempted!")
            if stats.get("clicks_successful", 0) > 0:
                print("🎉 AMAZING: Some clicks were successful!")
            else:
                print("⚠️  Note: Click success tracking may need adjustment")
        else:
            print("❌ No clicks were attempted")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("REAL Automation Test - WILL ACTUALLY CLICK!")
    print("=" * 60)

    try:
        # Run the async test
        asyncio.run(test_real_clicking())
    except KeyboardInterrupt:
        print("\n⏹️  Test cancelled by user")

    print("\n" + "=" * 60)
    print("Real automation test completed.")
    print("=" * 60)
