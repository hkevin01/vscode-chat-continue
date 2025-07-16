#!/usr/bin/env python3
"""
Test Production Mode Configuration

This script demonstrates switching between test mode (10s) and production mode (180s).
"""

import json
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.config_manager import ConfigManager


def test_mode_switching():
    """Test switching between test and production modes."""
    print("🧪 Testing Mode Switching Functionality")
    print("=" * 50)
    
    # Initialize config manager
    config_manager = ConfigManager()
    
    # Test current mode
    current_mode = config_manager.get("freeze_detection.current_mode")
    print(f"📊 Current mode: {current_mode}")
    
    # Get test mode settings
    test_interval = config_manager.get("freeze_detection.test_mode.check_interval")
    test_threshold = config_manager.get("freeze_detection.test_mode.freeze_threshold")
    print(f"🧪 Test mode: {test_interval}s interval, {test_threshold}s threshold")
    
    # Get production mode settings
    prod_interval = config_manager.get("freeze_detection.production_mode.check_interval")
    prod_threshold = config_manager.get("freeze_detection.production_mode.freeze_threshold")
    print(f"🏭 Production mode: {prod_interval}s interval, {prod_threshold}s threshold")
    
    print("\n🔄 Testing mode switching...")
    
    # Switch to production mode
    print("   → Switching to production mode...")
    config_manager.set("freeze_detection.current_mode", "production_mode")
    new_mode = config_manager.get("freeze_detection.current_mode")
    print(f"   ✅ New mode: {new_mode}")
    
    # Get current active settings
    if new_mode == "production_mode":
        active_interval = prod_interval
        active_threshold = prod_threshold
        mode_desc = "3-minute intervals for production"
    else:
        active_interval = test_interval
        active_threshold = test_threshold
        mode_desc = "10-second intervals for testing"
    
    print(f"   📈 Active settings: {active_interval}s check, {active_threshold}s freeze threshold")
    print(f"   📝 Description: {mode_desc}")
    
    # Switch back to test mode
    print("\n   → Switching back to test mode...")
    config_manager.set("freeze_detection.current_mode", "test_mode")
    final_mode = config_manager.get("freeze_detection.current_mode")
    print(f"   ✅ Final mode: {final_mode}")
    
    # Verify recovery methods
    recovery_methods = config_manager.get("freeze_detection.recovery_methods")
    print(f"\n🔧 Recovery methods available: {len(recovery_methods)}")
    for i, method in enumerate(recovery_methods, 1):
        print(f"   {i}. {method}")
    
    max_attempts = config_manager.get("freeze_detection.max_recovery_attempts")
    cooldown = config_manager.get("freeze_detection.recovery_cooldown")
    print(f"\n⚙️ Recovery settings:")
    print(f"   • Max attempts: {max_attempts}")
    print(f"   • Cooldown: {cooldown}s")
    
    print(f"\n✅ Mode switching test completed!")
    print(f"💡 Use 'python src/main.py --test-freeze' for 10-second testing")
    print(f"💡 Switch to production mode in config for 3-minute intervals")


if __name__ == "__main__":
    test_mode_switching()
