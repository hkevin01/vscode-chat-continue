#!/usr/bin/env python3
"""
VS Code Chat Continue Button Automation

Main entry point for the automation tool.
"""

import argparse
import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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
        '--version', '-v',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


async def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Create and start application
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
