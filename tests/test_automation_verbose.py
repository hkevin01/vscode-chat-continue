#!/usr/bin/env python3
"""
Test automation with verbose logging to see what's happening.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

from core.automation_engine import AutomationEngine
from core.config_manager import ConfigManager

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_automation_verbose():
    """Test automation with verbose logging."""
    print("🔍 Testing Automation with Verbose Logging")
    print("=" * 50)
    
    # Create config manager
    config_manager = ConfigManager()
    
    # Override some settings for testing
    config_manager.config.setdefault('automation', {})
    config_manager.config['automation']['interval_seconds'] = 3.0  # 3 second intervals
    config_manager.config.setdefault('filtering', {})
    config_manager.config['filtering']['require_chat_indicator'] = False  # Don't require chat in title
    
    # Create automation engine
    engine = AutomationEngine(config_manager)
    
    print("🚀 Starting automation engine...")
    
    # Create automation task
    automation_task = asyncio.create_task(engine.start())
    
    # Let it run for 15 seconds
    try:
        await asyncio.wait_for(automation_task, timeout=15.0)
    except asyncio.TimeoutError:
        print("⏰ Test timeout reached, stopping...")
    
    # Stop engine
    await engine.stop()
    
    # Show stats
    stats = engine.get_statistics()
    print("\n📊 Final Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_automation_verbose())
