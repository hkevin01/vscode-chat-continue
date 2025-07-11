#!/usr/bin/env python3
"""
Simple automation debug script to test window detection and automation loop.
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.automation_engine import AutomationEngine
from src.core.config_manager import ConfigManager
from src.core.window_detector import WindowDetector
from src.utils.logger import setup_logging


def main():
    print("🔍 VS Code Automation Debug")
    print("=" * 50)
    
    # Setup
    config = ConfigManager()
    setup_logging('DEBUG')
    
    # Set dry run mode
    config.set('automation.dry_run', True)
    config.set('logging.level', 'DEBUG')
    
    print("\n📋 Testing Window Detection:")
    detector = WindowDetector()
    windows = detector.get_vscode_windows()
    
    print(f"Found {len(windows)} VS Code windows:")
    for i, window in enumerate(windows, 1):
        print(f"  {i}. {window.title[:50]}...")
        print(f"     PID: {window.pid}, Position: ({window.x}, {window.y})")
        print(f"     Size: {window.width}x{window.height}")
    
    if len(windows) == 0:
        print("❌ No windows found - automation will not work")
        return
    
    print("\n🤖 Testing Automation Engine:")
    try:
        engine = AutomationEngine(config)
        print("✅ Automation engine created successfully")
        
        # Test one cycle
        print("🔄 Running one automation cycle...")
        import asyncio
        
        async def test_cycle():
            # Don't start the full loop, just test the core logic
            windows = engine.window_detector.get_vscode_windows()
            print(f"Engine detected {len(windows)} windows")
            
            for window in windows:
                print(f"Processing window: {window.title[:50]}...")
                # This would normally take a screenshot and find buttons
                # but we'll skip that for this debug test
        
        asyncio.run(test_cycle())
        print("✅ Automation cycle completed successfully")
        
    except Exception as e:
        print(f"❌ Automation engine error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
