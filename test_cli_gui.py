#!/usr/bin/env python3
"""
Test GUI mode detection without actually launching GUI
"""

import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_cli_mode():
    """Test CLI mode works"""
    print("Testing CLI mode...")
    try:
        # Test imports
        from main import create_parser
        print("✓ Parser created")
        
        # Test parsing with --help
        parser = create_parser()
        print("✓ Parser works")
        
        # Test that --gui flag exists
        help_text = parser.format_help()
        if '--gui' in help_text:
            print("✓ --gui flag available")
        else:
            print("✗ --gui flag missing")
            return False
            
        print("✓ CLI mode test passed")
        return True
        
    except Exception as e:
        print(f"✗ CLI mode test failed: {e}")
        return False

def test_gui_import():
    """Test if GUI can be imported"""
    print("\nTesting GUI import...")
    try:
        from gui.main_window import main as gui_main
        print("✓ GUI import successful")
        return True
    except ImportError as e:
        print(f"✗ GUI import failed: {e}")
        return False

if __name__ == '__main__':
    print("=== Testing GUI Mode Support ===")
    
    success = True
    success &= test_cli_mode()
    success &= test_gui_import()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    print("\nTesting argument parsing:")
    from main import create_parser
    parser = create_parser()
    
    # Test different argument combinations
    test_args = [
        [],
        ['--gui'],
        ['--dry-run'],
        ['--gui', '--dry-run'],
        ['--debug'],
    ]
    
    for args in test_args:
        try:
            parsed = parser.parse_args(args)
            print(f"✓ Args {args} -> gui={getattr(parsed, 'gui', False)}")
        except Exception as e:
            print(f"✗ Args {args} failed: {e}")
    
    sys.exit(0 if success else 1)
