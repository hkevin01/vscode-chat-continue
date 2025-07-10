#!/bin/bash
# Tidy up the root project directory by moving files to their appropriate subdirectories.

# Move all .md files (except README.md) to the docs/ directory
find . -maxdepth 1 -type f -name "*.md" ! -name "README.md" -exec mv -t docs/ {} +

# Move all test and diagnosis .py files to the tests/ directory
# Note: This is a sample list. Add other test-related files as needed.
declare -a test_files=(
    "comprehensive_diagnosis.py"
    "coordinate_fallback.py"
    "debug_button_detection.py"
    "debug_test.py"
    "debug_window_detection.py"
    "enhanced_button_test.py"
    "file_diagnosis.py"
    "test_detection.py"
    "test_ocr.py"
    "test_output.py"
    "test_tesseract.py"
)
for file in "${test_files[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" tests/
    fi
done

# Move all .sh scripts (except run.sh) to the scripts/ directory
find . -maxdepth 1 -type f -name "*.sh" ! -name "run.sh" -exec mv -t scripts/ {} +

# Move other Python scripts to the scripts/ directory
declare -a script_files=(
    "cleanup_files.py"
)
for file in "${script_files[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" scripts/
    fi
done

echo "Project root directory cleaned up."
