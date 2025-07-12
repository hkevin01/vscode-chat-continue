#!/bin/bash
# Comprehensive root directory cleanup script
# Keeps only essential files in root, moves everything else to appropriate subdirectories

cd /home/kevin/Projects/vscode-chat-continue

echo "🧹 Starting root directory cleanup..."

# Files to keep in root (essential project files)
KEEP_IN_ROOT=(
    "run.sh"
    "README.md" 
    "pyproject.toml"
    "requirements.txt"
    "requirements-dev.txt"
    ".gitignore"
    ".pylintrc"
)

# Create a function to check if file should be kept in root
should_keep_in_root() {
    local file="$1"
    for keep_file in "${KEEP_IN_ROOT[@]}"; do
        if [[ "$file" == "$keep_file" ]]; then
            return 0
        fi
    done
    return 1
}

# Move test files
echo "📁 Moving test files to tests/ directory..."
for file in test_*.py test_*.sh debug_*.py diagnostic.py manual_click_test.py verify_import_fix.py quick_automation_test.py; do
    if [[ -f "$file" ]]; then
        if [[ "$file" == test_automation*.py || "$file" == quick_automation_test.py ]]; then
            mv "$file" tests/automation/
            echo "  ✓ $file → tests/automation/"
        elif [[ "$file" == debug_*.py || "$file" == diagnostic.py ]]; then
            mv "$file" tests/debug/
            echo "  ✓ $file → tests/debug/"
        elif [[ "$file" == manual_click_test.py ]]; then
            mv "$file" tests/manual/
            echo "  ✓ $file → tests/manual/"
        elif [[ "$file" == test_*.sh ]]; then
            mv "$file" tests/scripts/
            echo "  ✓ $file → tests/scripts/"
        else
            mv "$file" tests/unit/
            echo "  ✓ $file → tests/unit/"
        fi
    fi
done

# Move utility scripts
echo "📁 Moving utility scripts to scripts/ directory..."
for file in cleanup_*.py cleanup_*.sh final_cleanup.sh organize_*.sh; do
    if [[ -f "$file" ]]; then
        mv "$file" scripts/
        echo "  ✓ $file → scripts/"
    fi
done

# Move documentation files
echo "📁 Moving documentation to docs/ directory..."
for file in AUTO_SETUP_ENHANCEMENT.md GUI_STATUS.md PROJECT_STRUCTURE.md; do
    if [[ -f "$file" ]]; then
        mv "$file" docs/
        echo "  ✓ $file → docs/"
    fi
done

echo "✅ Root directory cleanup complete!"

# Show what remains in root
echo ""
echo "📂 Files remaining in root directory:"
ls -la | grep -E "^-" | awk '{print "  " $9}' | grep -v "^  \.$"

echo ""
echo "🎯 Root directory is now clean and organized!"
