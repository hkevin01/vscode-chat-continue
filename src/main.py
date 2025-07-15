#!/usr/bin/env python3
"""
VS Code Chat Continue Button Automation

Main entry point for the automation tool.
"""

# IMPORTANT: Apply gnome-screenshot fix BEFORE any other imports that might trigger it
import argparse
import asyncio
import logging
import os
import signal
import sys
import warnings
from pathlib import Path
from typing import Optional

# Add the project root to Python path for proper imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.gnome_screenshot_fix import setup_screenshot_environment

setup_screenshot_environment()

# Configure PyTorch to suppress pin_memory warnings for CPU-only usage
os.environ["PYTORCH_DISABLE_GPU"] = "1"
warnings.filterwarnings("ignore", message=".*pin_memory.*no accelerator.*", category=UserWarning)

from src.core.automation_engine import AutomationEngine
from src.core.config_manager import ConfigManager
from src.utils.logger import setup_logging


class VSCodeContinueAutomation:
    """Main application class for VS Code Chat Continue automation."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the automation application.

        Args:
            config_path: Optional path to configuration file
        """
        self.config_manager = ConfigManager(config_path)
        self.automation_engine: Optional[AutomationEngine] = None
        self.running = False

        # Setup logging
        setup_logging(self.config_manager.get_log_level())
        self.logger = logging.getLogger(__name__)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    async def start(self) -> None:
        """Start the automation engine."""
        try:
            self.logger.info("Starting VS Code Chat Continue automation...")

            # Initialize automation engine
            self.automation_engine = AutomationEngine(self.config_manager)

            # Start automation
            self.running = True

            # Start automation task
            automation_task = asyncio.create_task(self.automation_engine.start())

            # Keep running until stopped
            while self.running:
                await asyncio.sleep(0.1)

                # Check if automation task completed
                if automation_task.done():
                    break

        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            raise
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop the automation engine."""
        if self.running:
            self.running = False
            self.logger.info("Stopping automation engine...")

            if self.automation_engine:
                await self.automation_engine.stop()

            self.logger.info("Automation stopped")


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Automate VS Code Copilot Chat Continue buttons",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Start with default settings
  %(prog)s --config custom.json     # Use custom configuration
  %(prog)s --dry-run                # Preview actions without clicking
  %(prog)s --debug                  # Enable debug logging
        """,
    )

    parser.add_argument("--config", "-c", type=Path, help="Path to configuration file")

    parser.add_argument(
        "--dry-run", action="store_true", help="Preview actions without actually clicking buttons"
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    parser.add_argument("--test-freeze", action="store_true", help="Run 10-second freeze detection test mode")

    parser.add_argument("--gui", action="store_true", help="Launch GUI interface (requires PyQt6)")

    parser.add_argument("--version", "-v", action="version", version="%(prog)s 1.0.0")

    return parser


def launch_gui(args) -> int:
    """Launch the GUI interface."""
    try:
        print("🎨 Initializing GUI interface...")

        # Check environment first
        import os

        display = os.environ.get("DISPLAY")
        wayland_display = os.environ.get("WAYLAND_DISPLAY")

        if not display and not wayland_display:
            print("❌ No display environment detected (DISPLAY or WAYLAND_DISPLAY)")
            print("💡 You might be running on a headless system or over SSH without X11 forwarding")
            print("💡 Try: ssh -X user@host or use --cli mode instead")
            return 1

        print(f"✓ Display environment: {display or wayland_display}")

        # Test PyQt6 availability
        try:
            from PyQt6.QtWidgets import QApplication

            print("✓ PyQt6 imported successfully")
        except ImportError as e:
            print(f"❌ PyQt6 not available: {e}")
            print("💡 Install PyQt6 with: pip install PyQt6")
            return 1

        # Import GUI components
        from gui.main_window import main as gui_main

        print("✓ GUI components imported")

        # Modify sys.argv to pass arguments to GUI
        import sys

        original_argv = sys.argv.copy()

        # Build GUI arguments
        gui_args = ["gui"]
        if args.config:
            gui_args.extend(["--config", str(args.config)])
        if args.dry_run:
            gui_args.append("--dry-run")
        if args.debug:
            gui_args.append("--debug")

        sys.argv = gui_args

        print("🚀 Launching GUI...")
        # Launch GUI
        exit_code = gui_main()

        # Restore original argv
        sys.argv = original_argv
        return exit_code or 0

    except ImportError as e:
        print(f"❌ GUI not available: {e}", file=sys.stderr)
        print("💡 Install PyQt6 with: pip install PyQt6", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ GUI error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


async def run_freeze_detection_test() -> int:
    """Run the 10-second freeze detection test mode."""
    print("🔍 Starting 10-Second Freeze Detection Test Mode")
    print("=" * 50)
    print("This test simulates VS Code window monitoring without X11 dependencies")
    print("Interval: 10 seconds (vs 3 minutes in production)")
    print("=" * 50)

    import hashlib
    import time
    from typing import Dict

    # Simple simulation without X11 dependencies
    class MockWindowState:
        def __init__(self, window_id: str):
            self.window_id = window_id
            self.last_hash = ""
            self.unchanged_duration = 0
            self.last_change_time = time.time()

    # Mock VS Code windows
    windows = {
        "vscode_1": MockWindowState("vscode_1"),
        "vscode_2": MockWindowState("vscode_2"),
    }

    freeze_threshold = 10  # 10 seconds for testing
    check_interval = 10    # 10 seconds between checks

    stats = {
        "checks": 0,
        "freezes_detected": 0,
        "continue_actions": 0,
    }

    print(f"\n🚀 Starting monitoring (Ctrl+C to stop)...")

    try:
        for cycle in range(1, 10):  # Run for 9 cycles (90 seconds)
            print(f"\n📊 Cycle #{cycle} - {time.strftime('%H:%M:%S')}")
            stats["checks"] += 1

            for window_id, window in windows.items():
                # Simulate window content (changes for window_2, static for window_1)
                current_time = int(time.time())
                if window_id == "vscode_1":
                    # This window will appear "frozen" after 15 seconds
                    content = f"static_content_{current_time // 15}"
                else:
                    # This window changes every 8 seconds
                    content = f"changing_content_{current_time // 8}"

                current_hash = hashlib.md5(content.encode()).hexdigest()[:8]

                print(f"  {window_id}: hash={current_hash}", end="")

                if current_hash == window.last_hash:
                    window.unchanged_duration += check_interval
                    print(f" (unchanged for {window.unchanged_duration}s)", end="")

                    if window.unchanged_duration >= freeze_threshold:
                        print(" 🚨 FREEZE DETECTED!")
                        stats["freezes_detected"] += 1

                        # Simulate continue action
                        print(f"    🔧 Triggering continue action for {window_id}")
                        print(f"    → Focus window and send Ctrl+Enter")
                        print(f"    → Type 'continue' + Enter")
                        stats["continue_actions"] += 1

                        # Reset after recovery
                        window.unchanged_duration = 0
                        window.last_change_time = time.time()
                    else:
                        print()
                else:
                    if window.unchanged_duration > 0:
                        print(" ✅ Content changed - reset freeze timer")
                    else:
                        print(" ✅ Active")
                    window.unchanged_duration = 0
                    window.last_change_time = time.time()

                window.last_hash = current_hash

            print(f"⏱️  Waiting {check_interval} seconds...")
            time.sleep(check_interval)

    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")

    print(f"\n📈 Test Results:")
    print(f"  • Monitoring cycles: {stats['checks']}")
    print(f"  • Freeze events detected: {stats['freezes_detected']}")
    print(f"  • Continue actions triggered: {stats['continue_actions']}")
    print(f"\n✅ Freeze detection test completed!")

    return 0


async def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Check if GUI mode is requested
    if args.gui:
        return launch_gui(args)

    try:
        # Create and start CLI application
        app = VSCodeContinueAutomation(args.config)

        # Override config with command line arguments
        if args.dry_run:
            app.config_manager.set("automation.dry_run", True)

        if args.debug:
            app.config_manager.set("logging.level", "DEBUG")

        # Run freeze detection test if requested
        if args.test_freeze:
            return await run_freeze_detection_test()

        await app.start()
        return 0

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required", file=sys.stderr)
        sys.exit(1)

    # Run the application
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
