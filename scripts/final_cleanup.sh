#!/bin/bash
"""
Final Cleanup Script for VS Code Chat Continue Automation

This script ensures no files are created in the project root directory
and all temporary/output files are properly organized in subdirectories.
"""

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🧹 Starting final cleanup for VS Code Chat Continue Automation..."
echo "📁 Project root: $PROJECT_ROOT"

# Create necessary directories if they don't exist
echo "📁 Ensuring directory structure..."
mkdir -p logs
mkdir -p tmp
mkdir -p config
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p src/core
mkdir -p src/gui
mkdir -p src/utils

# Remove any files that shouldn't be in root
echo "🗑️  Removing unwanted files from root directory..."
rm -f *.log
rm -f *.tmp
rm -f *.png
rm -f *.jpg
rm -f *.jpeg
rm -f *.json.bak
rm -f screenshot_*.png
rm -f debug_*.txt
rm -f test_output_*.txt

# Move any misplaced files to appropriate directories
echo "📦 Moving misplaced files to appropriate directories..."

# Move log files to logs directory
if ls *.log 1> /dev/null 2>&1; then
    echo "  Moving log files to logs/"
    mv *.log logs/ 2>/dev/null || true
fi

# Move temporary files to tmp directory
if ls *.tmp 1> /dev/null 2>&1; then
    echo "  Moving temporary files to tmp/"
    mv *.tmp tmp/ 2>/dev/null || true
fi

# Move screenshots to tmp directory
if ls screenshot_*.png 1> /dev/null 2>&1; then
    echo "  Moving screenshots to tmp/"
    mv screenshot_*.png tmp/ 2>/dev/null || true
fi

# Clean up Python cache files
echo "🐍 Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Set proper permissions
echo "🔒 Setting proper permissions..."
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x src/main.py 2>/dev/null || true
chmod +x tests/pyunit_suite.py 2>/dev/null || true
chmod +x run.sh 2>/dev/null || true

# Verify directory structure
echo "✅ Verifying directory structure..."
required_dirs=("src" "tests" "config" "logs" "scripts")
for dir in "${required_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        echo "  ✓ $dir/ exists"
    else
        echo "  ❌ $dir/ missing"
        mkdir -p "$dir"
        echo "  ✓ Created $dir/"
    fi
done

# Check for files in root that shouldn't be there
echo "🔍 Checking for unwanted files in root directory..."
unwanted_patterns=("*.log" "*.tmp" "*.png" "*.jpg" "*.jpeg" "screenshot_*" "debug_*" "test_output_*")
found_unwanted=false

for pattern in "${unwanted_patterns[@]}"; do
    if ls $pattern 1> /dev/null 2>&1; then
        echo "  ⚠️  Found unwanted files: $pattern"
        found_unwanted=true
    fi
done

if [[ "$found_unwanted" == false ]]; then
    echo "  ✅ No unwanted files found in root directory"
fi

# Create .copilot/context.md to enforce no files in root policy
echo "📝 Creating .copilot/context.md to enforce no files in root policy..."
mkdir -p .copilot
cat > .copilot/context.md << 'EOF'
# VS Code Chat Continue Automation - Context Rules

## File Organization Policy

**CRITICAL: NO FILES IN ROOT DIRECTORY**

All generated files must be placed in appropriate subdirectories:

- **logs/**: All log files, automation logs, debug output
- **tmp/**: Temporary files, screenshots, cache files
- **config/**: Configuration files, user settings
- **tests/**: All test files, test outputs, test data
- **src/**: Source code only
- **scripts/**: Utility scripts only

## Forbidden in Root Directory

- *.log files
- *.tmp files  
- *.png, *.jpg screenshot files
- *.json.bak backup files
- debug_*.txt files
- test_output_* files
- Any generated content

## Enforcement

All modules must use:
- `logs/` for logging output
- `tmp/` for temporary files
- Proper subdirectories for all generated content

Scripts and modules should check and create necessary subdirectories before writing files.
EOF

echo "📋 Final cleanup summary:"
echo "  ✅ Directory structure verified"
echo "  ✅ Unwanted files removed from root"
echo "  ✅ Python cache cleaned"
echo "  ✅ Permissions set"
echo "  ✅ Context rules created"

echo ""
echo "🎉 Final cleanup completed successfully!"
echo "🔍 To verify no files in root: ls -la | grep -E '\\.(log|tmp|png|jpg)$' || echo 'Root directory clean'"
echo "🧪 To run tests: python tests/pyunit_suite.py"
echo "🚀 To start GUI: python src/gui/main_window.py"
echo "⚙️  To start CLI: python src/main.py"