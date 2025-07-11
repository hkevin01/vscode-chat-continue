#!/bin/bash
# Simple test to check if our main.py works
cd /home/kevin/Projects/vscode-chat-continue

echo "Testing main.py..." > test_output.log
echo "Current directory: $(pwd)" >> test_output.log
echo "Python version: $(python3 --version)" >> test_output.log

# Test if main.py can be imported
if python3 -c "import sys; sys.path.append('src'); from main import create_parser; print('SUCCESS: main.py imports work')" 2>>test_output.log; then
    echo "SUCCESS: main.py imports work" >> test_output.log
else
    echo "ERROR: main.py imports failed" >> test_output.log
fi

# Test CLI help
echo "Testing --help:" >> test_output.log
python3 src/main.py --help >> test_output.log 2>&1

echo "Testing --gui --help:" >> test_output.log
python3 src/main.py --gui --help >> test_output.log 2>&1

echo "Test complete. Check test_output.log for results"
