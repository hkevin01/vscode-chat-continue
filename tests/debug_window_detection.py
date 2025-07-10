#!/usr/bin/env python3
"""
Debug script to test VS Code window detection.
"""

import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.window_detector import WindowDetector
from src.core.config_manager import ConfigManager

def main():
    """Test window detection."""
    print("🔍 VS Code Window Detection Debug")
    print("=" * 50)
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create config and window detector
    config = ConfigManager()
    detector = WindowDetector(config)
    
    print(f"Platform: {detector.platform}")
    print(f"X11 Available: {detector.platform == 'Linux' and hasattr(detector, 'display') and detector.display}")
    
    # Test process detection
    print("\n📋 Testing VS Code Process Detection:")
    processes = detector.get_vscode_processes()
    print(f"Found {len(processes)} VS Code processes:")
    for proc in processes:
        try:
            print(f"  - PID {proc.pid}: {proc.name()} - {' '.join(proc.cmdline()[:3])}")
        except Exception as e:
            print(f"  - PID {proc.pid}: Error getting details - {e}")
    
    # Test window detection
    print("\n🪟 Testing VS Code Window Detection:")
    windows = detector.get_vscode_windows()
    print(f"Found {len(windows)} VS Code windows:")
    for window in windows:
        print(f"  - {window.title[:50]}...")
        print(f"    PID: {window.pid}, Position: ({window.x}, {window.y})")
        print(f"    Size: {window.width}x{window.height}, Focused: {window.is_focused}")
    
    if len(windows) == 0:
        print("\n❌ No VS Code windows found!")
        print("\nTroubleshooting tips:")
        print("1. Make sure VS Code is running")
        print("2. Check if VS Code windows have 'Visual Studio Code' in the title")
        print("3. Try running as different user if permission issues")
        
        # Test manual window listing
        if detector.platform == "Linux" and hasattr(detector, 'display') and detector.display:
            print("\n🔧 Manual X11 Window Listing:")
            try:
                all_windows = detector.ewmh.getClientList()
                print(f"Total X11 windows: {len(all_windows) if all_windows else 0}")
                if all_windows:
                    for i, window in enumerate(all_windows[:10]):  # Show first 10
                        try:
                            title = detector.ewmh.getWmName(window)
                            if isinstance(title, bytes):
                                title = title.decode('utf-8', errors='ignore')
                            pid = detector.ewmh.getWmPid(window)
                            print(f"  {i+1}. PID {pid}: {title}")
                        except Exception as e:
                            print(f"  {i+1}. Error: {e}")
            except Exception as e:
                print(f"Error listing X11 windows: {e}")
    else:
        print("✅ Window detection working!")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
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
