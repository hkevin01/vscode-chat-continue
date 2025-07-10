#!/bin/bash
# VS Code Chat Continue Button Automation - Simple Run Script
# This is a convenience script that delegates to the main run script in scripts/

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if the main run script exists
if [ ! -f "$SCRIPT_DIR/scripts/run.sh" ]; then
    echo "❌ Error: scripts/run.sh not found"
    echo "Please ensure you're in the project root directory"
    exit 1
fi

# Make sure the main run script is executable
chmod +x "$SCRIPT_DIR/scripts/run.sh"

# Delegate to the main run script with all arguments
exec "$SCRIPT_DIR/scripts/run.sh" "$@"
