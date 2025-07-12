#!/usr/bin/env python3
"""
Simple test to directly run the automation and see what happens.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


async def test_automation():
    """Test the automation directly."""
    print("🚀 Direct Automation Test")
    print("=" * 30)
    
    try:
        from src.core.automation_engine import AutomationEngine
        from src.core.config_manager import ConfigManager
        from src.utils.gnome_screenshot_fix import setup_screenshot_environment

        # Setup
        setup_screenshot_environment()
        config_manager = ConfigManager()
        
        print("✓ Components initialized")
        print("✓ Creating automation engine...")
        
        # Create automation engine
        automation = AutomationEngine(config_manager)
        
        print("✓ Running automation for 10 seconds...")
        
        # Start automation and let it run for a short time
        automation_task = asyncio.create_task(automation.start())
        
        # Let it run for 10 seconds
        await asyncio.sleep(10)
        
        # Stop automation
        await automation.stop()
        
        print("✓ Automation completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_automation())
