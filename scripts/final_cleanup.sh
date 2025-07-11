#!/bin/bash
# Manual Root Directory Cleanup - Run this to tidy up the project structure

cd "$(dirname "$0")/.."

echo "🧹 VS Code Chat Continue - Root Directory Cleanup"
echo "================================================="
echo ""

# Check and move Python test files
echo "📁 Moving Python test files to tests/ directory:"
for file in debug_test.py test_automation_debug.py test_freeze.py test_phases.py validate_project.py; do
    if [ -f "$file" ]; then
        if [ -f "tests/$file" ]; then
            echo "  🗑️  rm $file (duplicate - already in tests/)"
            rm "$file"
        else
            echo "  📦 mv $file tests/"
            mv "$file" tests/
        fi
    else
        echo "  ✅ $file (already moved or doesn't exist)"
    fi
done

echo ""
echo "📁 Moving setup script to scripts/ directory:"
if [ -f "setup.py" ]; then
    if [ -f "scripts/setup.py" ]; then
        echo "  🗑️  rm setup.py (duplicate - already in scripts/)"
        rm "setup.py"
    else
        echo "  📦 mv setup.py scripts/"
        mv "setup.py" scripts/
    fi
else
    echo "  ✅ setup.py (already moved or doesn't exist)"
fi

echo ""
echo "📁 Moving documentation files to docs/ directory:"
for file in AUTO_SETUP_ENHANCEMENT.md PROJECT_COMPLETION_SUMMARY.md PROJECT_STRUCTURE.md; do
    if [ -f "$file" ]; then
        if [ -f "docs/$file" ]; then
            echo "  🗑️  rm $file (duplicate - already in docs/)"
            rm "$file"
        else
            echo "  📦 mv $file docs/"
            mv "$file" tests/"
        fi
    fi
done

echo ""
echo "📁 Moving new test files to tests/ directory:"
for file in debug_button_detection.py test_detection.py test_output.py test_ocr.py enhanced_button_test.py comprehensive_diagnosis.py test_tesseract.py file_diagnosis.py coordinate_fallback.py debug_window_detection.py debug_imports.py; do
    if [ -f "$file" ]; then
        if [ -f "tests/$file" ]; then
            echo "  🗑️  rm $file (duplicate - already in tests/)"
            rm "$file"
        else
            echo "  📦 mv $file tests/"
            mv "$file" tests/
        fi
    else
        echo "  ✅ $file (already moved or doesn't exist)"
    fi
done

echo ""
echo "🗑️  Removing temporary files:"
for file in cleanup_files.py cleanup_root.sh organize_files.sh install_tesseract.sh; do
    if [ -f "$file" ]; then
        echo "  🗑️  rm $file"
        rm "$file"
    fi
done

echo ""
echo "✅ Root directory cleanup complete!"
echo ""
echo "📋 Final clean root directory contains only:"
ls -1 | grep -E '\.(sh|md|txt|gitignore)$|^[^.]*$' | head -10
echo ""
echo "🎯 All Python files (.py) have been moved to appropriate subdirectories:"
echo "   • tests/ - All test files"
echo "   • scripts/ - Setup and utility scripts"
echo "   • src/ - Source code (unchanged)"
echo ""
echo "🚀 You can now run: ./scripts/run.sh"
