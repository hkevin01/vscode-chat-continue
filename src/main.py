#!/usr/bin/env python3
"""
VS Code Chat Continue Button Automation

Main entry point for the automation tool.
"""

# IMPORTANT: Apply gnome-screenshot fix BEFORE any other imports that might trigger it
import sys
from pathlib import Path

# Add the project root to Python path for proper imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.gnome_screenshot_fix import setup_screenshot_environment

setup_screenshot_environment()

import argparse
import asyncio
import logging
import signal
from typing import Optional

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
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=Path,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview actions without actually clicking buttons'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch GUI interface (requires PyQt6)'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


def launch_gui(args) -> int:
    """Launch the GUI interface."""
    try:
        print("🎨 Initializing GUI interface...")
        
        # Check environment first
        import os
        display = os.environ.get('DISPLAY')
        wayland_display = os.environ.get('WAYLAND_DISPLAY')
        
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
        gui_args = ['gui']
        if args.config:
            gui_args.extend(['--config', str(args.config)])
        if args.dry_run:
            gui_args.append('--dry-run')
        if args.debug:
            gui_args.append('--debug')
        
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
            app.config_manager.set('automation.dry_run', True)
        
        if args.debug:
            app.config_manager.set('logging.level', 'DEBUG')
        
        await app.start()
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
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
