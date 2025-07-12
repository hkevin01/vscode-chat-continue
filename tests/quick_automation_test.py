#!/usr/bin/env python3
"""
Quick test to check if the automation engine is processing windows and finding buttons.
This will run for a short time and show detailed debugging information.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.automation_engine import AutomationEngine
from src.core.config_manager import ConfigManager

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_automation():
    """Test the automation engine for a short period."""
    print("🤖 Testing Automation Engine")
    print("=" * 40)
    
    # Initialize config manager
    config_manager = ConfigManager()
    
    # Override confidence threshold for testing
    config_manager.config['detection']['confidence_threshold'] = 0.1  # Very low for testing
    config_manager.config['automation']['click_delay'] = 1.0  # Slower for observation
    
    # Initialize automation engine
    engine = AutomationEngine(config_manager)
    
    print("🔄 Running automation for 10 seconds...")
    
    # Run automation task
    automation_task = asyncio.create_task(engine.start())
    
    # Let it run for 10 seconds
    try:
        await asyncio.wait_for(automation_task, timeout=10.0)
    except asyncio.TimeoutError:
        print("⏰ Test timeout reached")
    
    # Stop the engine
    await engine.stop()
    
    # Show statistics
    stats = engine.get_statistics()
    print("\n📊 Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_automation())
