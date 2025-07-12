# Root Directory Cleanup Guide

## Current Status
The root directory has many files that should be organized into subdirectories for better project structure.

## Files to Keep in Root
- `run.sh` (main entry point)
- `README.md` (project documentation)
- `pyproject.toml` (Python project configuration)
- `requirements.txt` and `requirements-dev.txt` (dependencies)
- `.gitignore` and `.pylintrc` (project configuration)

## Manual Cleanup Commands

### 1. Move Test Files
```bash
cd /home/kevin/Projects/vscode-chat-continue

# Move automation test files
mv test_automation_init.py tests/automation/
mv test_automation_verbose.py tests/automation/
mv quick_automation_test.py tests/automation/

# Move unit test files
mv test_cli_gui.py tests/unit/
mv test_gui_simple.py tests/unit/
mv test_imports.py tests/unit/
mv test_main_import.py tests/unit/
mv test_main_final.py tests/unit/
mv test_screenshot.py tests/unit/
mv verify_import_fix.py tests/unit/

# Move test scripts
mv test_run_enhanced.sh tests/scripts/
mv test_simple.sh tests/scripts/

# Move debug files
mv debug_import_test.py tests/debug/
mv debug_imports.py tests/debug/
mv debug_test.py tests/debug/
mv diagnostic.py tests/diagnostic/

# Move manual test
mv manual_click_test.py tests/manual/
```

### 2. Move Utility Scripts
```bash
# Move cleanup and organization scripts
mv cleanup_files.py scripts/
mv cleanup_root.sh scripts/
mv cleanup_root_comprehensive.sh scripts/
mv final_cleanup.sh scripts/
mv organize_files.sh scripts/
mv organize_test_files.sh scripts/
```

### 3. Move Documentation
```bash
# Move documentation files
mv AUTO_SETUP_ENHANCEMENT.md docs/
mv GUI_STATUS.md docs/
mv PROJECT_STRUCTURE.md docs/
```

## Final Root Directory Structure
After cleanup, the root should contain only:
```
/home/kevin/Projects/vscode-chat-continue/
├── run.sh                 # Main entry point
├── README.md              # Project documentation
├── pyproject.toml         # Python project config
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── .gitignore            # Git ignore rules
├── .pylintrc             # Linting configuration
├── config/               # Configuration directory
├── docs/                 # Documentation
├── logs/                 # Log files
├── scripts/              # Utility scripts
├── src/                  # Source code
├── tests/                # All test files (organized)
├── tmp/                  # Temporary files
└── venv/                 # Virtual environment
```

## Benefits
- ✅ Clean, professional project structure
- ✅ Easy to find files by category
- ✅ Main entry point (`run.sh`) remains accessible
- ✅ All tests organized in logical subdirectories
- ✅ Documentation centralized in `docs/`
- ✅ Utility scripts separated from main code
