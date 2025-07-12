#!/bin/bash
# Organize test files into proper subdirectories

cd /home/kevin/Projects/vscode-chat-continue/tests

echo "🏗️  Organizing test files into subdirectories..."

# Move debug files
echo "📁 Moving debug files..."
for file in debug_*.py; do
    [ -f "$file" ] && mv "$file" debug/ && echo "  ✓ $file → debug/"
done

# Move diagnostic files  
echo "📁 Moving diagnostic files..."
for file in diagnostic*.py comprehensive*.py file_diagnosis.py validate_project.py quick_diagnostic.py; do
    [ -f "$file" ] && mv "$file" diagnostic/ && echo "  ✓ $file → diagnostic/"
done

# Move manual test files
echo "📁 Moving manual test files..."
for file in enhanced_button_test.py coordinate_fallback.py final_screenshot_test.py; do
    [ -f "$file" ] && mv "$file" manual/ && echo "  ✓ $file → manual/"
done

# Move automation test files
echo "📁 Moving automation test files..."
for file in test_automation*.py test_all_phases.py test_phases.py; do
    [ -f "$file" ] && mv "$file" automation/ && echo "  ✓ $file → automation/"
done

# Move test suite files to unit
echo "📁 Moving test suite files..."
for file in pyunit_suite.py run_tests.py test_suite.py; do
    [ -f "$file" ] && mv "$file" unit/ && echo "  ✓ $file → unit/"
done

# Move remaining test files to unit
echo "📁 Moving remaining test files to unit..."
for file in test_*.py; do
    [ -f "$file" ] && mv "$file" unit/ && echo "  ✓ $file → unit/"
done

echo "✅ Test file organization complete!"

# Show final structure
echo ""
echo "📊 Final directory structure:"
echo "Unit tests: $(ls unit/ | wc -l) files"
echo "Automation tests: $(ls automation/ | wc -l) files"  
echo "Debug scripts: $(ls debug/ | wc -l) files"
echo "Manual tests: $(ls manual/ | wc -l) files"
echo "Diagnostic tests: $(ls diagnostic/ | wc -l) files"
echo "Integration tests: $(ls integration/ | wc -l) files"
echo "Script tests: $(ls scripts/ | wc -l) files"
