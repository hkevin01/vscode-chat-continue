#!/usr/bin/env python3
"""
Lightweight automation runner without GUI for better performance.
Use this instead of the GUI when experiencing slowdowns.
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.automation_engine import AutomationEngine  # noqa: E402
from src.core.config_manager import ConfigManager  # noqa: E402


def cleanup_existing_processes():
    """Kill any existing automation processes to prevent conflicts."""
    import psutil

    try:
        print("🧹 Cleaning up existing automation processes...")

        # List of process patterns to kill
        patterns = [
            "lightweight_automation.py",
            "main_window.py",
            "run.sh",
            "continuous_automation.py",
            "vscode-chat-continue",
        ]

        killed_count = 0
        current_pid = psutil.Process().pid

        # Find and kill matching processes
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                proc_info = proc.info
                cmdline = proc_info.get("cmdline", [])

                if cmdline:
                    cmdline_str = " ".join(str(arg) for arg in cmdline if arg)

                    # Skip our own process
                    if proc.pid == current_pid:
                        continue

                    # Check if this is an automation process
                    for pattern in patterns:
                        if pattern in cmdline_str:
                            try:
                                proc.terminate()
                                proc.wait(timeout=3)
                                killed_count += 1
                                print(f"   ✓ Terminated process {proc.pid}: " f"{pattern}")
                                break
                            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                                try:
                                    proc.kill()
                                    killed_count += 1
                                    print(f"   ⚡ Force killed process " f"{proc.pid}: {pattern}")
                                except psutil.NoSuchProcess:
                                    pass

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if killed_count > 0:
            print(f"   📊 Cleaned up {killed_count} existing automation " f"process(es)")
        else:
            print("   ✓ No existing automation processes found")

    except Exception as e:
        print(f"   ⚠️  Error during process cleanup: {e}")

    print()


def create_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Lightweight VS Code Continue Button Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--config", "-c", type=Path, help="Path to configuration file")

    parser.add_argument(
        "--dry-run", action="store_true", help="Run in dry-run mode (no actual clicking)"
    )

    parser.add_argument(
        "--interval", type=float, default=8.0, help="Detection interval in seconds (default: 8.0)"
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser


async def lightweight_automation(args):
    """Run automation without GUI overhead."""
    print("🚀 Lightweight VS Code Continue Button Automation")
    print("=" * 50)
    print("⚡ Running without GUI for maximum performance")
    print()

    # Kill any existing automation processes first
    cleanup_existing_processes()

    # Create configuration
    config = ConfigManager(args.config) if args.config else ConfigManager()

    # Apply command line overrides
    config.set("automation.interval_seconds", args.interval)
    config.set("automation.dry_run", args.dry_run)
    config.set("automation.auto_focus_windows", True)  # Keep focus feature
    # Ensure audio is disabled to prevent beeping during automation
    config.set("audio.enabled", False)
    # Disable system bell to prevent terminal beeps
    config.set("system.disable_bell", True)

    if args.debug:
        config.set("logging.level", "DEBUG")
    else:
        config.set("logging.level", "INFO")  # Moderate logging
    config.set("automation.dry_run", False)  # Real automation
    config.set("automation.auto_focus_windows", True)  # Keep focus feature
    config.set("logging.level", "INFO")  # Moderate logging

    print("⚙️  Configuration:")
    interval = config.get("automation.interval_seconds")
    auto_focus = config.get("automation.auto_focus_windows")
    dry_run = config.get("automation.dry_run")
    print(f"   • Detection interval: {interval}s")
    print(f"   • Auto focus: {auto_focus}")
    print(f"   • Dry run: {dry_run}")
    print()

    # Initialize automation engine
    engine = AutomationEngine(config)

    print("🔍 Checking VS Code windows...")
    windows = engine.window_detector.get_vscode_windows()
    print(f"   Found {len(windows)} VS Code window(s)")

    if not windows:
        print("❌ No VS Code windows found!")
        print("   Please open VS Code and try again.")
        return

    for i, window in enumerate(windows):
        print(f"   {i+1}. {window.title}")

    print("\n🎯 Starting automation...")
    print("   Press Ctrl+C to stop")
    print()

    cycle = 0
    total_clicks = 0

    try:
        while True:
            cycle += 1
            start_time = time.time()

            print(f"🔄 Cycle {cycle} - Processing {len(windows)} window(s)...")

            # Run automation cycle
            await engine._process_vscode_windows()

            # Get stats
            stats = engine.get_statistics()
            clicks = stats.get("clicks_successful", 0)

            # Check for new clicks
            if clicks > total_clicks:
                new_clicks = clicks - total_clicks
                print(f"   ✅ Clicked {new_clicks} Continue button(s)! " f"Total: {clicks}")
                total_clicks = clicks
            else:
                print(f"   📊 No buttons found. Total clicks: {total_clicks}")

            # Performance info
            cycle_time = time.time() - start_time
            print(f"   ⏱️  Cycle completed in {cycle_time:.1f}s")

            # Sleep between cycles
            interval = config.get("automation.interval_seconds", 8.0)
            print(f"   💤 Waiting {interval}s until next cycle...")
            print()

            await asyncio.sleep(interval)

    except KeyboardInterrupt:
        print("\n🛑 Automation stopped by user")

    except Exception as e:
        print(f"\n💥 Error: {e}")

    finally:
        print("\n📊 Final Statistics:")
        print(f"   • Total cycles: {cycle}")
        print(f"   • Total clicks: {total_clicks}")
        print(f"   • Windows processed: {stats.get('windows_processed', 0)}")
        print("\n✅ Automation complete!")


def main():
    """Main entry point."""
    try:
        parser = create_parser()
        args = parser.parse_args()
        asyncio.run(lightweight_automation(args))
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
