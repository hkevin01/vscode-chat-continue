#!/bin/bash
"""
Automation runner script that sets up the proper environment.
"""

# Set up environment for GUI access
export DISPLAY=:0

# Ensure we're in the project directory
cd "$(dirname "$0")/.."

echo "🔍 VS Code Chat Continue Automation Test"
echo "Project directory: $(pwd)"
echo "DISPLAY: $DISPLAY"

# Check for VS Code processes
echo ""
echo "📋 VS Code processes running:"
ps aux | grep -i code | grep -v grep | wc -l

# Check for VS Code windows
echo ""
echo "🪟 VS Code windows (via xwininfo):"
xwininfo -root -tree 2>/dev/null | grep -i "visual studio code" | wc -l

# Run our window detection
echo ""
echo "🐍 Running Python window detection..."
python tests/debug_window_simple.py

echo ""
echo "✅ Test completed"
