#!/usr/bin/env python3
"""
Test the window detection fix for GUI
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


async def test_window_detection_in_automation():
    """Test window detection through automation engine"""
    print("=== Testing Window Detection in Automation Engine ===")

    try:
        from core.automation_engine import AutomationEngine
        from core.config_manager import ConfigManager

        # Create config and engine
        config = ConfigManager()
        config.set("automation.dry_run", True)  # Safe mode

        engine = AutomationEngine(config)
        engine.running = True

        print("✓ Automation engine created")

        # Test window processing
        await engine._process_vscode_windows()

        # Check stats
        stats = engine.stats
        windows_processed = stats.get("windows_processed", 0)

        print(f"✓ Windows processed: {windows_processed}")

        if windows_processed > 0:
            print("✅ SUCCESS: Window detection is working in automation engine!")
            print(f"   Found and processed {windows_processed} windows")
        else:
            print("⚠️  No windows processed - this might be expected if no VS Code windows are open")

        # Test performance report
        report = engine.get_performance_report()
        runtime = report.get("runtime_seconds", 0)
        print(f"✓ Performance report generated (runtime: {runtime}s)")

        return windows_processed > 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run the test"""
    success = await test_window_detection_in_automation()

    if success:
        print("\n🚀 The GUI should now show window detection!")
        print("   Try: ./run.sh --gui --dry-run")
    else:
        print("\n💡 Open some VS Code windows and try again")
        print("   Or use: ./run.sh --cli --dry-run")


if __name__ == "__main__":
    asyncio.run(main())
