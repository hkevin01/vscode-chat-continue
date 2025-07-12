# Test Directory Structure

This directory contains all test files organized into logical subdirectories for better maintainability.

## Directory Structure

### `/tests/unit/`
Unit tests for individual components and modules:
- `test_imports.py` - Import validation tests
- `test_main_import.py` - Main module import tests
- `test_automation_init.py` - Automation initialization tests
- `verify_import_fix.py` - Import fix verification
- `test_cli_gui.py` - CLI/GUI interface tests
- `test_gui_simple.py` - Simple GUI tests
- `test_screenshot.py` - Screenshot functionality tests
- `test_basic.py` - Basic functionality tests
- `test_tesseract.py` - Tesseract OCR tests
- `test_ocr.py` - OCR functionality tests
- `test_button_detection.py` - Button detection tests
- `test_detection.py` - General detection tests
- `test_screenshot_cross_platform.py` - Cross-platform screenshot tests

### `/tests/automation/`
Full automation workflow tests:
- `test_automation_verbose.py` - Verbose automation testing
- `quick_automation_test.py` - Quick automation tests
- `test_automation_debug.py` - Automation debugging tests
- `test_automation_quick.py` - Quick automation validation

### `/tests/debug/`
Debug and troubleshooting scripts:
- `debug_import_test.py` - Import debugging
- `debug_imports.py` - Import validation debugging
- `debug_test.py` - General debugging script
- `debug_button_detection.py` - Button detection debugging
- `debug_button_detection_verbose.py` - Verbose button detection debugging
- `debug_window_detection.py` - Window detection debugging
- `debug_window_simple.py` - Simple window debugging
- `debug_minimal.py` - Minimal debugging script
- `debug_automation_simple.py` - Simple automation debugging

### `/tests/manual/`
Manual testing scripts and interactive tests:
- `manual_click_test.py` - Manual click testing
- `enhanced_button_test.py` - Enhanced button testing
- `coordinate_fallback.py` - Coordinate fallback testing
- `final_screenshot_test.py` - Final screenshot testing

### `/tests/diagnostic/`
System and component diagnostic scripts:
- `diagnostic.py` - General diagnostics
- `test_menu_diagnostic.py` - Menu diagnostic tests
- `quick_diagnostic.py` - Quick diagnostic checks
- `comprehensive_diagnosis.py` - Comprehensive system diagnosis
- `comprehensive_test_suite.py` - Full test suite
- `file_diagnosis.py` - File system diagnostics
- `diagnostic_deep.py` - Deep diagnostic analysis

### `/tests/integration/`
Integration tests for component interactions:
- `test_multi_window.py` - Multi-window scenarios
- `test_end_to_end.py` - End-to-end testing
- `test_error_handling.py` - Error handling tests

## Running Tests

### Unit Tests
```bash
cd tests/unit
python test_imports.py
python test_basic.py
```

### Automation Tests
```bash
cd tests/automation
python test_automation_verbose.py
python quick_automation_test.py
```

### Debug Scripts
```bash
cd tests/debug
python debug_import_test.py
python debug_button_detection.py
```

### Manual Tests
```bash
cd tests/manual
python manual_click_test.py
python enhanced_button_test.py
```

### Diagnostic Tests
```bash
cd tests/diagnostic
python diagnostic.py
python comprehensive_diagnosis.py
```

## Test Guidelines

1. **Unit tests** should test individual components in isolation
2. **Integration tests** should test component interactions
3. **Debug scripts** should help troubleshoot specific issues
4. **Manual tests** require user interaction or visual verification
5. **Diagnostic tests** should provide system health checks

## Adding New Tests

When adding new test files, place them in the appropriate subdirectory:
- Individual component tests → `unit/`
- Full workflow tests → `automation/`
- Troubleshooting scripts → `debug/`
- Interactive tests → `manual/`
- System checks → `diagnostic/`
- Component interaction tests → `integration/`
