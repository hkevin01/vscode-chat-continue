#!/usr/bin/env python3
"""
Simple debug script to test VS Code window detection.
"""

import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Test window detection."""
    print("🔍 VS Code Window Detection Debug")
    print("=" * 50)
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        from src.core.config_manager import ConfigManager
        from src.core.window_detector import WindowDetector

        # Create config and window detector
        config = ConfigManager()
        detector = WindowDetector()
        
        print(f"Platform: {detector.platform}")
        
        # Test process detection
        print("\n📋 Testing VS Code Process Detection:")
        processes = detector.get_vscode_processes()
        print(f"Found {len(processes)} VS Code processes:")
        for proc in processes:
            try:
                cmdline = proc.cmdline()
                print(f"  - PID {proc.pid}: {proc.name()}")
                print(f"    Command: {' '.join(cmdline[:3])}...")
            except Exception as e:
                print(f"  - PID {proc.pid}: Error getting details - {e}")
        
        # Test window detection
        print("\n🪟 Testing VS Code Window Detection:")
        windows = detector.get_vscode_windows()
        print(f"Found {len(windows)} VS Code windows:")
        for window in windows:
            print(f"  - {window.title[:50]}...")
            print(f"    PID: {window.pid}, Position: ({window.x}, {window.y})")
            print(f"    Size: {window.width}x{window.height}")
        
        if len(windows) == 0:
            print("\n❌ No VS Code windows found!")
            print("\nTroubleshooting tips:")
            print("1. Make sure VS Code is running")
            print("2. Check if you have multiple VS Code windows open")
            print("3. Try restarting VS Code")
        else:
            print("✅ Window detection working!")
            
    except Exception as e:
        print(f"❌ Error in window detection test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
