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
