#!/usr/bin/env python3
"""Quick test to check VS Code windows and capture screenshots."""

import subprocess
from pathlib import Path


def capture_all_vscode_windows():
    """Capture all VS Code windows for manual inspection."""
    Path("tmp").mkdir(exist_ok=True)
    
    # Get VS Code windows
    result = subprocess.run(
        ["xwininfo", "-root", "-tree"], 
        capture_output=True, text=True
    )
    
    vscode_windows = []
    for line in result.stdout.split('\n'):
        if 'visual studio code' in line.lower():
            parts = line.strip().split()
            if len(parts) >= 3:
                window_id = parts[0]
                vscode_windows.append(window_id)
    
    print(f"Found {len(vscode_windows)} VS Code windows")
    
    # Capture each window
    for i, window_id in enumerate(vscode_windows):
        temp_path = f"tmp/manual_capture_{i+1}_{window_id.replace('0x', '')}.png"
        
        result = subprocess.run([
            "bash", "-c", 
            f"xwd -id {window_id} | convert xwd:- {temp_path}"
        ], capture_output=True)
        
        if result.returncode == 0:
            print(f"✅ Captured window {i+1}: {temp_path}")
        else:
            print(f"❌ Failed to capture window {i+1}")

if __name__ == "__main__":
    capture_all_vscode_windows()
    print("\nPlease manually check the captured images in tmp/ directory")
    print("Look for blue Continue buttons in the Copilot chat panels")
