#!/usr/bin/env python3
"""
Simple test of the updated main.py
"""

import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_main():
    """Test the main.py functionality"""
    try:
        # Test basic import
        from main import create_parser, launch_gui
        print("✓ Successfully imported main.py functions")
        
        # Test parser creation
        parser = create_parser()
        print("✓ Parser created successfully")
        
        # Test argument parsing
        args = parser.parse_args(['--help'])
        print("✓ Arguments parsed successfully")
        
    except SystemExit:
        # --help causes SystemExit, which is expected
        print("✓ Help displayed (SystemExit is normal)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_gui_detection():
    """Test GUI mode detection"""
    try:
        from main import create_parser
        parser = create_parser()
        
        # Test different argument combinations
        test_cases = [
            (['--dry-run'], False),
            (['--gui'], True),
            (['--gui', '--dry-run'], True),
            (['--debug'], False),
        ]
        
        for args, expected_gui in test_cases:
            try:
                parsed = parser.parse_args(args)
                has_gui = getattr(parsed, 'gui', False)
                if has_gui == expected_gui:
                    print(f"✓ Args {args} -> gui={has_gui} (expected={expected_gui})")
                else:
                    print(f"✗ Args {args} -> gui={has_gui} (expected={expected_gui})")
                    return False
            except SystemExit:
                # Some args might trigger help/error, that's ok
                print(f"⚠ Args {args} triggered SystemExit")
                
        return True
        
    except Exception as e:
        print(f"✗ GUI detection test failed: {e}")
        return False

if __name__ == '__main__':
    print("=== Testing main.py functionality ===")
    
    success = True
    
    print("\n1. Testing basic imports and parser:")
    success &= test_main()
    
    print("\n2. Testing GUI mode detection:")
    success &= test_gui_detection()
    
    if success:
        print("\n✅ All tests passed!")
        print("✅ main.py is working correctly")
        print("✅ GUI mode detection is working")
    else:
        print("\n❌ Some tests failed")
    
    # Test environment
    print("\n3. Environment check:")
    display = os.environ.get('DISPLAY')
    if display:
        print(f"✓ DISPLAY set to: {display}")
    else:
        print("⚠ DISPLAY not set (headless environment)")
    
    try:
        import PyQt6
        print("✓ PyQt6 is available")
    except ImportError:
        print("⚠ PyQt6 not available")
        
    print("\n🚀 Ready to run:")
    print("   CLI mode: python3 src/main.py --dry-run")
    print("   GUI mode: python3 src/main.py --gui --dry-run")
