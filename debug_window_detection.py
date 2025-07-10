#!/usr/bin/env python3
"""
Debug window detection specifically
"""

import os
import subprocess
import sys
from datetime import datetime

import psutil

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def log_to_file(message):
    """Log to file with timestamp"""
    with open("/tmp/window_detection_debug.log", "a") as f:
        timestamp = datetime.now().strftime("%H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def check_vscode_processes():
    """Check VS Code processes using psutil"""
    log_to_file("=== Checking VS Code Processes ===")
    
    vscode_processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                info = proc.info
                name = (info.get('name') or '').lower()
                exe = (info.get('exe') or '').lower()
                
                # Check for VS Code
                if any(vscode_name in name for vscode_name in ['code', 'vscode']) or \
                   any(vscode_name in exe for vscode_name in ['code', 'vscode']):
                    
                    cmdline = info.get('cmdline', [])
                    cmdline_str = ' '.join([str(arg) for arg in cmdline if arg])
                    
                    # Filter out helper processes
                    if not any(helper in cmdline_str.lower() for helper in [
                        '--type=gpu-process', '--type=renderer', '--type=utility'
                    ]):
                        vscode_processes.append(proc)
                        log_to_file(f"Found VS Code process: PID={proc.pid}, name={name}")
                        log_to_file(f"  Exe: {exe}")
                        log_to_file(f"  Cmdline: {cmdline_str[:100]}...")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    except Exception as e:
        log_to_file(f"Error checking processes: {e}")
    
    log_to_file(f"Total VS Code processes found: {len(vscode_processes)}")
    return vscode_processes

def check_x11_windows():
    """Check X11 window detection"""
    log_to_file("=== Checking X11 Windows ===")
    
    try:
        # Try using wmctrl command first (simpler than X11 Python)
        result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            log_to_file("wmctrl available - listing windows:")
            lines = result.stdout.strip().split('\n')
            vscode_windows = []
            for line in lines:
                if line and ('code' in line.lower() or 'vscode' in line.lower()):
                    vscode_windows.append(line)
                    log_to_file(f"  VS Code window: {line}")
            log_to_file(f"Found {len(vscode_windows)} VS Code windows via wmctrl")
            return len(vscode_windows)
        else:
            log_to_file("wmctrl not available or failed")
    except FileNotFoundError:
        log_to_file("wmctrl command not found")
    except Exception as e:
        log_to_file(f"wmctrl error: {e}")
    
    # Try X11 Python approach
    try:
        import Xlib
        import Xlib.display
        from ewmh import EWMH
        
        log_to_file("X11 Python libraries available")
        
        display = Xlib.display.Display()
        ewmh = EWMH()
        
        log_to_file("X11 connection established")
        
        # Get all windows
        all_windows = ewmh.getClientList()
        log_to_file(f"Total windows from X11: {len(all_windows) if all_windows else 0}")
        
        if all_windows:
            vscode_count = 0
            for window in all_windows:
                try:
                    title_raw = ewmh.getWmName(window)
                    if title_raw:
                        if isinstance(title_raw, bytes):
                            title = title_raw.decode('utf-8', errors='ignore')
                        else:
                            title = str(title_raw)
                        
                        if 'code' in title.lower() or 'vscode' in title.lower():
                            vscode_count += 1
                            log_to_file(f"  VS Code window: {title}")
                            
                            # Get geometry
                            try:
                                geom = window.get_geometry()
                                log_to_file(f"    Position: ({geom.x}, {geom.y})")
                                log_to_file(f"    Size: {geom.width}x{geom.height}")
                            except:
                                log_to_file("    Could not get geometry")
                except Exception as e:
                    log_to_file(f"    Error processing window: {e}")
            
            log_to_file(f"Found {vscode_count} VS Code windows via X11")
            return vscode_count
        
    except ImportError:
        log_to_file("X11 Python libraries not available")
    except Exception as e:
        log_to_file(f"X11 Python error: {e}")
    
    return 0

def test_window_detector_class():
    """Test the actual WindowDetector class"""
    log_to_file("=== Testing WindowDetector Class ===")
    
    try:
        from core.window_detector import WindowDetector
        
        detector = WindowDetector()
        log_to_file(f"WindowDetector created, platform: {detector.platform}")
        
        # Test process detection
        processes = detector.get_vscode_processes()
        log_to_file(f"WindowDetector found {len(processes)} VS Code processes")
        
        # Test window detection
        windows = detector.get_vscode_windows()
        log_to_file(f"WindowDetector found {len(windows)} VS Code windows")
        
        for i, window in enumerate(windows):
            log_to_file(f"  Window {i+1}: {window.title}")
            log_to_file(f"    Position: ({window.x}, {window.y})")
            log_to_file(f"    Size: {window.width}x{window.height}")
            log_to_file(f"    PID: {window.pid}")
        
        return len(windows)
        
    except Exception as e:
        log_to_file(f"WindowDetector error: {e}")
        import traceback
        log_to_file(f"Traceback: {traceback.format_exc()}")
        return 0

def main():
    # Clear log file
    with open("/tmp/window_detection_debug.log", "w") as f:
        f.write("")
    
    log_to_file("VS Code Window Detection Debug")
    log_to_file("=" * 40)
    
    # Test 1: Process detection
    processes = check_vscode_processes()
    
    # Test 2: X11 window detection
    x11_windows = check_x11_windows()
    
    # Test 3: WindowDetector class
    detector_windows = test_window_detector_class()
    
    # Summary
    log_to_file("=" * 40)
    log_to_file("SUMMARY:")
    log_to_file(f"VS Code processes found: {len(processes)}")
    log_to_file(f"X11 windows found: {x11_windows}")
    log_to_file(f"WindowDetector windows found: {detector_windows}")
    
    if len(processes) > 0 and detector_windows == 0:
        log_to_file("ISSUE: VS Code processes exist but no windows detected!")
        log_to_file("This suggests a problem with X11 window detection.")

if __name__ == "__main__":
    main()
    print("\nDebug complete. Check /tmp/window_detection_debug.log for details.")
