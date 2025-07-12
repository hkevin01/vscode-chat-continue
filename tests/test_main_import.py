#!/usr/bin/env python3
"""Simple test to check if main.py imports correctly."""

import os
import sys

print(f"Current working directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path[:3]}...")

try:
    import src.main
    print("✓ Import successful!")
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
