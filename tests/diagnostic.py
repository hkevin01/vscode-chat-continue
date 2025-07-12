#!/usr/bin/env python3
"""
Environment diagnostic for VS Code Chat Continue
"""

import os
import subprocess
import sys


def check_environment():
    """Check the runtime environment"""
    print("=== Environment Diagnostic ===")
    
    # Check Python version
    print(f"Python: {sys.version}")
    
    # Check environment variables
    display = os.environ.get('DISPLAY', 'Not set')
    wayland = os.environ.get('WAYLAND_DISPLAY', 'Not set')
    xdg_session = os.environ.get('XDG_SESSION_TYPE', 'Not set')
    desktop = os.environ.get('DESKTOP_SESSION', 'Not set')
    
    print(f"DISPLAY: {display}")
    print(f"WAYLAND_DISPLAY: {wayland}")
    print(f"XDG_SESSION_TYPE: {xdg_session}")
    print(f"DESKTOP_SESSION: {desktop}")
    
    # Check if we're in SSH
    ssh_client = os.environ.get('SSH_CLIENT', 'Not set')
    ssh_connection = os.environ.get('SSH_CONNECTION', 'Not set')
    print(f"SSH_CLIENT: {ssh_client}")
    print(f"SSH_CONNECTION: {ssh_connection}")
    
    # Check if we have a terminal
    if os.isatty(sys.stdout.fileno()):
        print("TTY: Yes (interactive terminal)")
    else:
        print("TTY: No (non-interactive)")
    
    # Try basic PyQt6 import
    try:
        import PyQt6
        print("PyQt6: Available")
        
        # Try creating QApplication without display
        try:
            from PyQt6.QtWidgets import QApplication

            # Use offscreen platform for headless testing
            app = QApplication(['test', '-platform', 'offscreen'])
            print("QApplication: Can create (offscreen)")
            app.quit()
        except Exception as e:
            print(f"QApplication: Failed - {e}")
            
    except ImportError as e:
        print(f"PyQt6: Not available - {e}")
    
    # Check VS Code processes
    try:
        result = subprocess.run(['pgrep', '-f', 'code'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            count = len(result.stdout.strip().split('\n'))
            print(f"VS Code processes: {count}")
        else:
            print("VS Code processes: None found")
    except:
        print("VS Code processes: Unable to check")
    
    print("\n=== Recommendations ===")
    if ssh_client != 'Not set':
        print("⚠️  Running over SSH - GUI may not work without X11 forwarding")
        print("💡 Try: ssh -X user@host or use --cli mode")
    
    if display == 'Not set' and wayland == 'Not set':
        print("⚠️  No display environment detected")
        print("💡 Use --cli mode for headless operation")
    
    print("✅ Use ./scripts/run.sh --cli for command-line mode")
    print("✅ Use ./scripts/run.sh --gui for GUI mode (if display available)")

if __name__ == '__main__':
    check_environment()
