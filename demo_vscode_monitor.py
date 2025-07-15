#!/usr/bin/env python3
"""
VS Code Freeze Detection and Recovery Demo

Demonstrates the new VS Code monitoring system that detects frozen windows
and performs automated recovery using programmatic commands.
"""

import asyncio
import json
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.automation_engine import AutomationEngine
from src.core.config_manager import ConfigManager
from src.core.vscode_monitor import VSCodeMonitor


class VSCodeMonitorDemo:
    """Demo application for VS Code freeze detection and recovery."""
    
    def __init__(self):
        """Initialize the demo."""
        self.running = False
        self.monitor: VSCodeMonitor = None
        self.automation: AutomationEngine = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        
    async def run_monitor_demo(self):
        """Run standalone monitor demo."""
        print("🔍 VS Code Freeze Detection and Recovery Demo")
        print("=" * 60)
        print("This demo monitors VS Code windows for freezing and performs automated recovery.")
        print("Frozen windows are detected when they don't change for 60 seconds (demo setting).")
        print("Recovery uses programmatic commands instead of visual button clicking.")
        print("\nPress Ctrl+C to stop monitoring...\n")
        
        # Create monitor with short thresholds for demo
        self.monitor = VSCodeMonitor(
            freeze_threshold=60.0,    # 1 minute for demo (normally 10 minutes)
            recovery_cooldown=30.0    # 30 seconds for demo (normally 5 minutes)
        )
        
        self.running = True
        
        # Start monitoring
        monitor_task = asyncio.create_task(self.monitor.start_monitoring())
        
        # Status display loop
        try:
            while self.running:
                await asyncio.sleep(10)  # Update every 10 seconds
                await self._display_status()
                
        except KeyboardInterrupt:
            self.logger.info("Demo interrupted by user")
        finally:
            await self.monitor.stop_monitoring()
            monitor_task.cancel()
            
    async def run_full_automation_demo(self):
        """Run full automation with integrated monitoring."""
        print("🚀 VS Code Automation with Integrated Monitoring Demo")
        print("=" * 60)
        print("This demo runs the full automation engine with integrated freeze monitoring.")
        print("The automation handles continue buttons while monitoring for freezes.")
        print("\nPress Ctrl+C to stop automation...\n")
        
        # Create config manager
        config_manager = ConfigManager()
        
        # Override some settings for demo
        config_manager.set("monitoring.enabled", True)
        config_manager.set("monitoring.freeze_threshold", 120.0)  # 2 minutes for demo
        config_manager.set("monitoring.recovery_cooldown", 60.0)  # 1 minute for demo
        config_manager.set("automation.interval_seconds", 5.0)    # Check every 5 seconds
        
        # Create automation engine
        self.automation = AutomationEngine(config_manager)
        
        self.running = True
        
        # Start automation
        automation_task = asyncio.create_task(self.automation.start())
        
        # Status display loop
        try:
            while self.running:
                await asyncio.sleep(15)  # Update every 15 seconds
                await self._display_full_status()
                
        except KeyboardInterrupt:
            self.logger.info("Demo interrupted by user")
        finally:
            await self.automation.stop()
            
    async def _display_status(self):
        """Display current monitoring status."""
        if not self.monitor:
            return
            
        status = self.monitor.get_monitoring_status()
        current_time = time.time()
        
        print(f"\n📊 VS Code Monitor Status - {time.strftime('%H:%M:%S')}")
        print(f"   Total Windows: {status['total_windows']}")
        print(f"   Responsive: {status['responsive_windows']}")
        print(f"   Frozen: {status['frozen_windows']}")
        
        if status['windows']:
            print("\n🪟 Window Details:")
            for window in status['windows']:
                status_icon = "✅" if window['responsive'] else "🧊"
                time_since = window['time_since_change']
                
                print(f"   {status_icon} {window['title'][:40]:<40} "
                      f"({time_since:.1f}s since change)")
                
                if not window['responsive'] and window['consecutive_freezes'] > 0:
                    print(f"      ⚠️  Freeze #{window['consecutive_freezes']}")
                    
        else:
            print("   No VS Code windows found")
            
    async def _display_full_status(self):
        """Display full automation and monitoring status."""
        if not self.automation:
            return
            
        # Get automation performance report
        perf_report = self.automation.get_performance_report()
        
        # Get monitoring status
        monitor_status = self.automation.get_monitoring_status()
        
        print(f"\n🚀 Full Automation Status - {time.strftime('%H:%M:%S')}")
        print("=" * 50)
        
        # Automation stats
        stats = perf_report.get('statistics', {})
        print(f"🎯 Automation Statistics:")
        print(f"   Runtime: {perf_report.get('runtime_seconds', 0):.1f} seconds")
        print(f"   Windows Processed: {stats.get('windows_processed', 0)}")
        print(f"   Buttons Found: {stats.get('buttons_found', 0)}")
        print(f"   Successful Clicks: {stats.get('clicks_successful', 0)}")
        
        # Monitoring stats
        print(f"\n🔍 Monitoring Status:")
        print(f"   Total Windows: {monitor_status.get('total_windows', 0)}")
        print(f"   Responsive: {monitor_status.get('responsive_windows', 0)}")
        print(f"   Frozen: {monitor_status.get('frozen_windows', 0)}")
        
        # Window details
        windows = monitor_status.get('windows', [])
        if windows:
            print(f"\n🪟 Active Windows:")
            for window in windows[:5]:  # Show first 5 windows
                status_icon = "✅" if window['responsive'] else "🧊"
                time_since = window['time_since_change']
                
                print(f"   {status_icon} {window['title'][:35]:<35} "
                      f"({time_since:.1f}s)")

async def show_menu():
    """Show demo menu."""
    print("\n🎮 VS Code Monitor Demo Menu")
    print("=" * 40)
    print("1. Monitor Only Demo (detects freezes)")
    print("2. Full Automation Demo (automation + monitoring)")
    print("3. Test Programmatic Continue Methods")
    print("4. Show Configuration Guide")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    return choice

async def test_programmatic_methods():
    """Test programmatic continue methods."""
    print("\n🔧 Testing Programmatic Continue Methods")
    print("=" * 50)
    
    # Import the test script
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 
            str(Path(__file__).parent / "test_programmatic_continue.py")
        ], capture_output=False)
        
        if result.returncode == 0:
            print("✅ Programmatic methods test completed")
        else:
            print("❌ Test failed")
            
    except Exception as e:
        print(f"❌ Error running test: {e}")

def show_configuration_guide():
    """Show configuration guide."""
    print("\n📖 Configuration Guide")
    print("=" * 40)
    
    config_example = {
        "monitoring": {
            "enabled": True,
            "freeze_threshold": 600.0,  # 10 minutes
            "recovery_cooldown": 300.0  # 5 minutes
        },
        "automation": {
            "interval_seconds": 2.0,
            "click_delay": 0.1
        },
        "safety": {
            "user_activity_timeout_seconds": 5,
            "emergency_stop_enabled": True
        }
    }
    
    print("Configuration options for config/default.json:")
    print(json.dumps(config_example, indent=2))
    
    print(f"\n💡 Key Settings:")
    print(f"- freeze_threshold: Time before window considered frozen")
    print(f"- recovery_cooldown: Time between recovery attempts")
    print(f"- interval_seconds: How often to check for buttons")
    
    print(f"\n🔧 Recovery Methods (in order of preference):")
    print(f"1. Ctrl+Enter (inline chat accept)")
    print(f"2. Command palette 'Chat: Accept'")
    print(f"3. Enter key (submit)")
    print(f"4. Type 'continue' + Enter (fallback)")

async def main():
    """Main demo entry point."""
    demo = VSCodeMonitorDemo()
    
    print("🎯 VS Code Freeze Detection and Recovery System")
    print("=" * 60)
    print("This system monitors VS Code windows for freezing and provides automated recovery.")
    print("It uses programmatic commands instead of visual button detection.")
    print("Based on extensive GitHub Copilot extension research.")
    
    while True:
        try:
            choice = await show_menu()
            
            if choice == '1':
                await demo.run_monitor_demo()
            elif choice == '2':
                await demo.run_full_automation_demo()
            elif choice == '3':
                await test_programmatic_methods()
            elif choice == '4':
                show_configuration_guide()
            elif choice == '5':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice, please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            
        if choice in ['1', '2']:
            input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
