#!/usr/bin/env python3
"""Quick window detection test."""

import sys
from pathlib import Path

# Add project paths
project_root = Path("/home/kevin/Projects/vscode-chat-continue")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print("=== Quick Window Detection ===")

try:
    from src.core.window_detector import WindowDetector
    
    detector = WindowDetector()
    windows = detector.get_vscode_windows()
    
    print(f"Found {len(windows)} VS Code windows")
    
    for i, window in enumerate(windows):
        print(f"Window {i+1}:")
        print(f"  Title: {repr(window.title)}")
        print(f"  Position: ({window.x}, {window.y})")
        print(f"  Size: {window.width}x{window.height}")
        print(f"  Visible: {getattr(window, 'visible', 'unknown')}")
        print()
        
    if not windows:
        print("No VS Code windows found. Please:")
        print("1. Open VS Code")
        print("2. Open a Copilot chat")
        print("3. Make sure there's a Continue button visible")
        print("4. Re-run the test")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
