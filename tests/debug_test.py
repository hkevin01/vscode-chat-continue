#!/usr/bin/env python3
"""Debug script to test window detection."""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_window_detection():
    """Test window detection for VS Code processes."""
    try:
        from core.window_detector import WindowDetector
        
        print("Creating WindowDetector...")
        wd = WindowDetector()
        
        print("Getting VS Code processes...")
        processes = wd.get_vscode_processes()
        print(f"Found {len(processes)} VS Code processes")
        
        for i, proc in enumerate(processes):
            try:
                print(f"Process {i+1}: PID={proc.pid}, name={proc.name()}")
            except Exception as e:
                print(f"Process {i+1}: Error getting info - {e}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting debug test...")
    success = test_window_detection()
    print(f"Test {'PASSED' if success else 'FAILED'}")
