#!/usr/bin/env python3
"""
Legacy wrapper for terminate_automation.py
This script is kept for backwards compatibility.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Main entry point - delegate to terminate_automation.py"""
    terminator_script = Path(__file__).parent / "terminate_automation.py"
    
    if not terminator_script.exists():
        print("❌ Error: terminate_automation.py not found")
        return 1
    
    try:
        # Run the new terminator script with all arguments
        result = subprocess.run([
            sys.executable, 
            str(terminator_script)
        ] + sys.argv[1:])
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running terminator: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())