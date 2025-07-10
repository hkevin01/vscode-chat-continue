#!/usr/bin/env python3
"""
Test script to run automation engine directly and see the output.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.automation_engine import AutomationEngine
from src.core.config_manager import ConfigManager


async def main():
    """Test automation engine."""
    print("🤖 Testing Automation Engine")
    print("=" * 50)
    
    # Set up logging to console
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create config manager
    config = ConfigManager()
    
    # Override some settings for testing
    config.set('automation.interval_seconds', 3.0)
    config.set('automation.dry_run', True)
    config.set('logging.level', 'DEBUG')
    config.set('logging.console_output', True)
    
    # Create automation engine
    engine = AutomationEngine(config)
    
    print("✅ Automation engine created")
    print("📊 Starting automation for 10 seconds...")
    
    try:
        # Start automation for 10 seconds
        automation_task = asyncio.create_task(engine.start())
        
        # Let it run for 10 seconds
        await asyncio.sleep(10)
        
        # Stop automation
        await engine.stop()
        
        print("🛑 Automation stopped")
        
        # Print statistics
        stats = engine.get_stats()
        print("\n📈 Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
