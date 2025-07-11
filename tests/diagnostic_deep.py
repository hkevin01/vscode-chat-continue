#!/usr/bin/env python3
"""
Deep diagnostic for window detection issues.
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set DISPLAY environment variable
os.environ['DISPLAY'] = ':0'

def main():
    print("🔬 Deep Window Detection Diagnostic")
    print("=" * 50)
    
    try:
        print("1. Testing basic imports...")
        from src.core.config_manager import ConfigManager
        from src.core.window_detector import WindowDetector
        from src.utils.logger import setup_logging
        print("   ✅ Imports successful")
        
        print("\n2. Setting up logging...")
        setup_logging('DEBUG')
        print("   ✅ Logging configured")
        
        print("\n3. Creating WindowDetector...")
        detector = WindowDetector()
        print(f"   ✅ WindowDetector created")
        print(f"   Platform: {detector.platform}")
        print(f"   Display: {getattr(detector, 'display', 'None')}")
        print(f"   EWMH: {getattr(detector, 'ewmh', 'None')}")
        
        print("\n4. Testing VS Code process detection...")
        processes = detector.get_vscode_processes()
        print(f"   ✅ Found {len(processes)} VS Code processes")
        
        # Show first few processes
        for i, proc in enumerate(processes[:5]):
            try:
                print(f"      {i+1}. PID {proc.pid}: {proc.name()}")
            except:
                print(f"      {i+1}. PID {proc.pid}: <name unavailable>")
        
        print("\n5. Testing Linux window detection directly...")
        
        # Check if we have X11 components
        if hasattr(detector, 'display') and detector.display:
            print("   ✅ X11 display available")
            
            # Try to get windows with detailed logging
            try:
                print("   Calling _get_linux_windows()...")
                windows = detector._get_linux_windows()
                print(f"   ✅ _get_linux_windows() returned {len(windows)} windows")
                
                for i, window in enumerate(windows):
                    print(f"      {i+1}. {window.title[:60]}...")
                    print(f"         PID: {window.pid}, Pos: ({window.x}, {window.y})")
                    
            except Exception as e:
                print(f"   ❌ _get_linux_windows() failed: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            print("   ❌ X11 display not available")
            print(f"      Display object: {getattr(detector, 'display', 'None')}")
            print(f"      EWMH object: {getattr(detector, 'ewmh', 'None')}")
        
        print("\n6. Testing high-level get_vscode_windows()...")
        try:
            windows = detector.get_vscode_windows()
            print(f"   ✅ get_vscode_windows() returned {len(windows)} windows")
            
            for i, window in enumerate(windows):
                print(f"      {i+1}. {window.title[:60]}...")
                print(f"         PID: {window.pid}, Pos: ({window.x}, {window.y})")
                
        except Exception as e:
            print(f"   ❌ get_vscode_windows() failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n7. Manual X11 test...")
        try:
            import Xlib.display
            from ewmh import EWMH
            
            print("   Creating direct X11 connection...")
            display = Xlib.display.Display()
            ewmh = EWMH()
            
            print("   Getting window list...")
            all_windows = ewmh.getClientList()
            print(f"   Found {len(all_windows) if all_windows else 0} total windows")
            
            # Look for VS Code windows
            vscode_windows = []
            if all_windows:
                for window in all_windows[:10]:  # Check first 10 windows
                    try:
                        title_raw = ewmh.getWmName(window)
                        if title_raw:
                            if isinstance(title_raw, bytes):
                                title = title_raw.decode('utf-8', errors='ignore')
                            else:
                                title = str(title_raw)
                                
                            if 'visual studio code' in title.lower():
                                vscode_windows.append(title)
                                print(f"      Found: {title}")
                    except:
                        continue
            
            print(f"   ✅ Direct X11 found {len(vscode_windows)} VS Code windows")
            
        except Exception as e:
            print(f"   ❌ Direct X11 test failed: {e}")
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 Diagnostic completed")

if __name__ == '__main__':
    main()
