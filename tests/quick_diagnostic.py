#!/usr/bin/env python3
"""
Quick diagnostic and fix for window detection issues.
"""

import os
import sys
from pathlib import Path

# Set up environment
os.environ['DISPLAY'] = ':0'
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def test_basic_x11():
    """Test basic X11 connectivity."""
    print("🔍 Testing X11 connectivity...")
    try:
        import Xlib.display
        display = Xlib.display.Display()
        print("   ✅ X11 display connection successful")
        
        from ewmh import EWMH
        ewmh = EWMH()
        print("   ✅ EWMH initialization successful")
        
        # Test getting window list
        windows = ewmh.getClientList()
        print(f"   ✅ Found {len(windows) if windows else 0} total windows")
        
        return True, display, ewmh
    except Exception as e:
        print(f"   ❌ X11 error: {e}")
        return False, None, None

def test_vscode_processes():
    """Test VS Code process detection."""
    print("\n🔍 Testing VS Code process detection...")
    try:
        import psutil
        vscode_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                info = proc.info
                name = (info.get('name') or '').lower()
                exe = (info.get('exe') or '').lower()
                
                if any(vs in name or vs in exe for vs in ['code', 'vscode']):
                    vscode_processes.append(proc)
            except:
                continue
        
        print(f"   ✅ Found {len(vscode_processes)} VS Code processes")
        for proc in vscode_processes[:5]:  # Show first 5
            try:
                print(f"      - PID {proc.pid}: {proc.name()}")
            except:
                print(f"      - PID {proc.pid}: <unavailable>")
        
        return vscode_processes
    except Exception as e:
        print(f"   ❌ Process detection error: {e}")
        return []

def test_window_matching(display, ewmh, vscode_processes):
    """Test window matching logic."""
    print("\n🔍 Testing window matching...")
    
    if not display or not ewmh:
        print("   ❌ No X11 connection available")
        return
    
    try:
        vscode_pids = {proc.pid for proc in vscode_processes}
        print(f"   VS Code PIDs: {vscode_pids}")
        
        windows = ewmh.getClientList()
        if not windows:
            print("   ❌ No windows found")
            return
        
        vscode_windows = 0
        
        for window in windows:
            try:
                # Get window info
                pid = ewmh.getWmPid(window)
                name_raw = ewmh.getWmName(window)
                
                if name_raw:
                    if isinstance(name_raw, bytes):
                        title = name_raw.decode('utf-8', errors='ignore')
                    else:
                        title = str(name_raw)
                else:
                    title = ""
                
                # Check if it's a VS Code window
                is_vscode_pid = pid in vscode_pids if pid else False
                is_vscode_title = 'visual studio code' in title.lower() or title.lower().endswith('- code')
                
                if is_vscode_pid and is_vscode_title:
                    vscode_windows += 1
                    print(f"   ✅ VS Code window: '{title[:60]}...'")
                    print(f"      PID: {pid}, Window ID: {window.id}")
                elif is_vscode_pid:
                    print(f"   ⚠️  VS Code PID but not title: '{title[:60]}...' (PID: {pid})")
                elif is_vscode_title:
                    print(f"   ⚠️  VS Code title but not PID: '{title[:60]}...' (PID: {pid})")
                    
            except Exception as e:
                continue
        
        print(f"   ✅ Found {vscode_windows} matching VS Code windows")
        return vscode_windows
        
    except Exception as e:
        print(f"   ❌ Window matching error: {e}")
        return 0

def main():
    print("🚀 VS Code Window Detection Diagnostic & Fix")
    print("=" * 60)
    
    # Test X11
    x11_ok, display, ewmh = test_basic_x11()
    if not x11_ok:
        print("\n❌ Cannot proceed without X11 connection")
        return
    
    # Test processes
    vscode_processes = test_vscode_processes()
    if not vscode_processes:
        print("\n❌ No VS Code processes found - please open VS Code")
        return
    
    # Test window matching
    window_count = test_window_matching(display, ewmh, vscode_processes)
    
    print(f"\n📊 Summary:")
    print(f"   VS Code processes: {len(vscode_processes)}")
    print(f"   VS Code windows: {window_count}")
    
    if window_count > 0:
        print("   ✅ Window detection should work!")
    else:
        print("   ❌ Window detection failing - check window titles")
        
        # Show all VS Code windows for debugging
        print("\n🔍 All windows from VS Code processes:")
        try:
            windows = ewmh.getClientList()
            vscode_pids = {proc.pid for proc in vscode_processes}
            
            for window in windows:
                try:
                    pid = ewmh.getWmPid(window)
                    if pid in vscode_pids:
                        name_raw = ewmh.getWmName(window)
                        if name_raw:
                            if isinstance(name_raw, bytes):
                                title = name_raw.decode('utf-8', errors='ignore')
                            else:
                                title = str(name_raw)
                        else:
                            title = "<no title>"
                        print(f"      - '{title}' (PID: {pid})")
                except:
                    continue
        except Exception as e:
            print(f"      Error listing windows: {e}")

if __name__ == '__main__':
    main()
