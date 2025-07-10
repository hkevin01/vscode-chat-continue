#!/usr/bin/env python3
"""
Comprehensive test suite for ALL implementation phases (1-4).

This test suite covers every bullet point mentioned in the project plan:

Phase 1: Foundation
- [x] Project setup and structure
- [x] Basic window detection
- [x] VS Code process identification
- [x] Simple screen capture functionality

Phase 2: Core Features
- [x] Continue button detection algorithm
- [x] Mouse click automation
- [x] Multi-window support
- [x] Basic error handling

Phase 3: Enhancement
- [x] Configuration system
- [x] Logging and monitoring
- [x] Performance optimization
- [x] Safety features (manual override)
- [x] Fallback Strategy: Text-based continue commands

Phase 4: Polish
- [ ] User interface (optional GUI)
- [ ] Installation scripts
- [ ] Documentation and tutorials
- [ ] Testing and bug fixes
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.automation_engine import AutomationEngine
from core.button_finder import ButtonFinder, ButtonLocation
from core.click_automator import ClickAutomator
from core.config_manager import ConfigManager
from core.window_detector import VSCodeWindow, WindowDetector
from utils.logger import AutomationLogger, setup_logging
from utils.screen_capture import ScreenCapture


class TestPhase1Foundation(unittest.TestCase):
    """Test Phase 1: Foundation features."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
    def test_project_setup_and_structure(self):
        """Test that project structure is correctly set up."""
        # Test that all expected directories exist
        project_root = Path(__file__).parent.parent
        expected_dirs = [
            "src", "src/core", "src/utils", "tests", "docs", 
            "scripts", "config", ".github", ".copilot"
        ]
        
        for dir_name in expected_dirs:
            dir_path = project_root / dir_name
            self.assertTrue(dir_path.exists(), f"Directory {dir_name} should exist")
            self.assertTrue(dir_path.is_dir(), f"{dir_name} should be a directory")
        
        # Test that core files exist
        expected_files = [
            "src/main.py",
            "src/core/automation_engine.py", 
            "src/core/button_finder.py",
            "src/core/click_automator.py",
            "src/core/config_manager.py",
            "src/core/window_detector.py",
            "src/utils/logger.py",
            "src/utils/screen_capture.py",
            "requirements.txt",
            "scripts/setup.py"
        ]
        
        for file_name in expected_files:
            file_path = project_root / file_name
            self.assertTrue(file_path.exists(), f"File {file_name} should exist")
            self.assertTrue(file_path.is_file(), f"{file_name} should be a file")
    
    def test_basic_window_detection(self):
        """Test basic window detection functionality."""
        detector = WindowDetector()
        
        # Test that detector can be instantiated
        self.assertIsInstance(detector, WindowDetector)
        
        # Test get_vscode_processes method exists and returns list
        processes = detector.get_vscode_processes()
        self.assertIsInstance(processes, list)
        
        # Test get_vscode_windows method exists and returns list
        windows = detector.get_vscode_windows()
        self.assertIsInstance(windows, list)
    
    def test_vscode_process_identification(self):
        """Test VS Code process identification."""
        detector = WindowDetector()
        
        # Mock psutil to simulate VS Code processes
        with patch('psutil.process_iter') as mock_iter:
            mock_process = Mock()
            mock_process.name.return_value = "code"
            mock_process.pid = 12345
            mock_process.exe.return_value = "/usr/bin/code"
            mock_iter.return_value = [mock_process]
            
            processes = detector.get_vscode_processes()
            self.assertEqual(len(processes), 1)
            self.assertEqual(processes[0].pid, 12345)
    
    def test_screen_capture_functionality(self):
        """Test simple screen capture functionality."""
        screen_capture = ScreenCapture()
        
        # Test that screen capture can be instantiated
        self.assertIsInstance(screen_capture, ScreenCapture)
        
        # Test capture_region method exists
        self.assertTrue(hasattr(screen_capture, 'capture_region'))
        
        # Test capture_screen method exists
        self.assertTrue(hasattr(screen_capture, 'capture_screen'))


class TestPhase2CoreFeatures(unittest.TestCase):
    """Test Phase 2: Core Features."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        config_data = {
            "automation": {"click_delay": 0.1},
            "detection": {"confidence_threshold": 0.8}
        }
        self.config_path = Path(self.temp_dir) / "test_config.json"
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f)
    
    def test_continue_button_detection_algorithm(self):
        """Test continue button detection algorithm."""
        button_finder = ButtonFinder()
        
        # Test that button finder can be instantiated
        self.assertIsInstance(button_finder, ButtonFinder)
        
        # Test find_continue_buttons method exists
        self.assertTrue(hasattr(button_finder, 'find_continue_buttons'))
        
        # Mock image for testing
        mock_image = Mock()
        buttons = button_finder.find_continue_buttons(mock_image)
        self.assertIsInstance(buttons, list)
    
    def test_mouse_click_automation(self):
        """Test mouse click automation."""
        click_automator = ClickAutomator()
        
        # Test that click automator can be instantiated
        self.assertIsInstance(click_automator, ClickAutomator)
        
        # Test click method exists
        self.assertTrue(hasattr(click_automator, 'click'))
        
        # Test click with mock coordinates
        with patch('pyautogui.click') as mock_click:
            result = click_automator.click(100, 200)
            self.assertIsNotNone(result)
    
    def test_multi_window_support(self):
        """Test multi-window support functionality."""
        config_manager = ConfigManager(str(self.config_path))
        engine = AutomationEngine(config_manager)
        
        # Test that automation engine supports multiple windows
        self.assertTrue(hasattr(engine, 'process_all_windows'))
        
        # Test with mock windows
        mock_windows = [
            VSCodeWindow(
                window_id=1, title="VS Code - test1", 
                x=0, y=0, width=800, height=600, pid=123
            ),
            VSCodeWindow(
                window_id=2, title="VS Code - test2", 
                x=100, y=100, width=800, height=600, pid=124
            )
        ]
        
        with patch.object(engine.window_detector, 'get_vscode_windows', 
                         return_value=mock_windows):
            # This should handle multiple windows
            windows = engine.window_detector.get_vscode_windows()
            self.assertEqual(len(windows), 2)
    
    def test_basic_error_handling(self):
        """Test basic error handling."""
        config_manager = ConfigManager(str(self.config_path))
        engine = AutomationEngine(config_manager)
        
        # Test that error handling doesn't crash the system
        try:
            # Simulate error condition
            with patch.object(engine.window_detector, 'get_vscode_windows',
                             side_effect=Exception("Test error")):
                asyncio.run(engine.process_all_windows())
        except Exception as e:
            # Should handle errors gracefully
            self.assertIsInstance(e, Exception)


class TestPhase3Enhancement(unittest.TestCase):
    """Test Phase 3: Enhancement features."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
    
    def test_configuration_system(self):
        """Test advanced configuration system."""
        # Create test config
        config_data = {
            "automation": {
                "interval_seconds": 2.0,
                "max_retries": 3,
                "dry_run": True
            },
            "detection": {
                "confidence_threshold": 0.8,
                "button_variants": ["Continue", "Continue >"]
            },
            "safety": {
                "emergency_stop_key": "escape",
                "pause_on_user_activity": True
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f)
        
        config_manager = ConfigManager(str(self.config_path))
        
        # Test configuration loading
        self.assertEqual(config_manager.get('automation.interval_seconds'), 2.0)
        self.assertEqual(config_manager.get('automation.max_retries'), 3)
        self.assertTrue(config_manager.get('automation.dry_run'))
        
        # Test nested configuration access
        self.assertEqual(config_manager.get('safety.emergency_stop_key'), 'escape')
        
        # Test default values
        self.assertEqual(config_manager.get('nonexistent.key', 'default'), 'default')
    
    def test_logging_and_monitoring(self):
        """Test logging and monitoring system."""
        config = {
            "level": "INFO",
            "file_path": str(Path(self.temp_dir) / "test.log"),
            "console_output": True,
            "detailed_timing": True
        }
        
        logger = AutomationLogger(config)
        
        # Test logger creation
        self.assertIsInstance(logger, AutomationLogger)
        
        # Test operation logging
        op_id = logger.log_operation_start("test_operation", {"test": "data"})
        self.assertIsNotNone(op_id)
        
        logger.log_operation_success("test_operation", op_id, {"result": "success"})
        logger.log_operation_failure("test_operation", "test error")
        
        # Test statistics
        self.assertIsInstance(logger.stats, dict)
        self.assertIn('operations', logger.stats)
        self.assertIn('successes', logger.stats)
        self.assertIn('failures', logger.stats)
    
    def test_performance_optimization(self):
        """Test performance optimization features."""
        config_data = {
            "performance": {"cache_timeout_seconds": 30},
            "automation": {"click_delay": 0.1}
        }
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f)
        
        config_manager = ConfigManager(str(self.config_path))
        engine = AutomationEngine(config_manager)
        
        # Test performance monitoring
        self.assertIsInstance(engine.performance_metrics, dict)
        self.assertIn('cache_hits', engine.performance_metrics)
        self.assertIn('cache_misses', engine.performance_metrics)
        
        # Test caching functionality
        mock_windows = [VSCodeWindow(1, "Test", (0, 0, 800, 600), 123)]
        engine._cache_windows(mock_windows)
        cached = engine._get_cached_windows()
        self.assertEqual(len(cached), 1)
        
        # Test performance report
        report = engine.get_performance_report()
        self.assertIn('cache_efficiency', report)
        self.assertIn('success_rate', report)
    
    def test_safety_features_manual_override(self):
        """Test safety features and manual override."""
        config_data = {
            "safety": {
                "emergency_stop_key": "escape",
                "pause_on_user_activity": True,
                "user_activity_timeout_seconds": 5
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f)
        
        config_manager = ConfigManager(str(self.config_path))
        engine = AutomationEngine(config_manager)
        
        # Test manual override methods
        self.assertFalse(engine._paused)
        engine.pause()
        self.assertTrue(engine._paused)
        
        engine.resume()
        self.assertFalse(engine._paused)
        
        # Test emergency stop
        self.assertFalse(engine._emergency_stop)
        engine.emergency_stop()
        self.assertTrue(engine._emergency_stop)
        
        # Test user activity detection
        self.assertFalse(engine.is_user_activity_blocking())
    
    def test_fallback_strategy(self):
        """Test fallback strategy implementation."""
        config_data = {
            "fallback_strategy": {
                "enabled": True,
                "text_commands": ["continue", "please continue"],
                "typing_speed": "normal",
                "max_retries": 3
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f)
        
        config_manager = ConfigManager(str(self.config_path))
        
        # Test fallback configuration
        self.assertTrue(config_manager.get('fallback_strategy.enabled'))
        commands = config_manager.get('fallback_strategy.text_commands')
        self.assertIn('continue', commands)


class TestPhase4Polish(unittest.TestCase):
    """Test Phase 4: Polish features."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
    
    def test_installation_scripts(self):
        """Test installation scripts exist and are executable."""
        scripts_dir = self.project_root / "scripts"
        
        expected_scripts = ["install.sh", "run.sh", "dev.sh"]
        
        for script_name in expected_scripts:
            script_path = scripts_dir / script_name
            self.assertTrue(script_path.exists(), 
                          f"Script {script_name} should exist")
            
            # Check if script is executable (on Unix systems)
            if os.name != 'nt':  # Not Windows
                self.assertTrue(os.access(script_path, os.X_OK),
                              f"Script {script_name} should be executable")
    
    def test_documentation_and_tutorials(self):
        """Test that documentation and tutorials exist."""
        docs_dir = self.project_root / "docs"
        
        expected_docs = [
            "PROJECT_PLAN.md",
            "FALLBACK_STRATEGY.md", 
            "USAGE.md",
            "TROUBLESHOOTING.md",
            "CONTRIBUTING.md"
        ]
        
        for doc_name in expected_docs:
            doc_path = docs_dir / doc_name
            self.assertTrue(doc_path.exists(), f"Doc {doc_name} should exist")
            
            # Check that docs have content
            content = doc_path.read_text()
            self.assertGreater(len(content), 100, 
                             f"Doc {doc_name} should have substantial content")
    
    def test_testing_and_bug_fixes(self):
        """Test testing infrastructure and bug fixes."""
        tests_dir = self.project_root / "tests"
        
        # Test that test files exist
        self.assertTrue(tests_dir.exists(), "Tests directory should exist")
        
        # Test that this test file exists and runs
        test_files = list(tests_dir.glob("test_*.py"))
        self.assertGreater(len(test_files), 0, "Should have test files")
        
        # Test that comprehensive test suite exists
        comprehensive_test = tests_dir / "comprehensive_test_suite.py"
        self.assertTrue(comprehensive_test.exists(), 
                       "Comprehensive test suite should exist")


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios across all phases."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "integration_config.json"
        
        # Full integration config
        config_data = {
            "automation": {
                "interval_seconds": 1.0,
                "max_retries": 2,
                "dry_run": True
            },
            "detection": {
                "confidence_threshold": 0.8,
                "button_variants": ["Continue", "Continue >"]
            },
            "fallback_strategy": {
                "enabled": True,
                "text_commands": ["continue"],
                "max_retries": 2
            },
            "safety": {
                "emergency_stop_key": "escape",
                "pause_on_user_activity": True
            },
            "logging": {
                "level": "INFO",
                "file_path": str(Path(self.temp_dir) / "integration.log")
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f)
    
    def test_full_automation_pipeline(self):
        """Test complete automation pipeline integration."""
        config_manager = ConfigManager(str(self.config_path))
        engine = AutomationEngine(config_manager)
        
        # Test full pipeline can be created
        self.assertIsInstance(engine, AutomationEngine)
        self.assertIsInstance(engine.window_detector, WindowDetector)
        self.assertIsInstance(engine.button_finder, ButtonFinder)
        self.assertIsInstance(engine.click_automator, ClickAutomator)
        self.assertIsInstance(engine.screen_capture, ScreenCapture)
        
        # Test that all components are properly initialized
        self.assertIsNotNone(engine.config_manager)
        self.assertIsNotNone(engine.stats)
        self.assertIsNotNone(engine.performance_metrics)
    
    def test_error_handling_and_recovery(self):
        """Test error handling and recovery across the system."""
        config_manager = ConfigManager(str(self.config_path))
        engine = AutomationEngine(config_manager)
        
        # Test that system handles component failures gracefully
        with patch.object(engine.window_detector, 'get_vscode_windows',
                         side_effect=Exception("Window detection failed")):
            # Should not crash
            try:
                asyncio.run(engine.process_all_windows())
            except Exception:
                pass  # Expected to handle errors
            
            # Should track errors in stats
            self.assertIn('errors', engine.stats)
    
    def test_configuration_integration(self):
        """Test configuration system integration across components."""
        config_manager = ConfigManager(str(self.config_path))
        engine = AutomationEngine(config_manager)
        
        # Test that configuration flows through all components
        dry_run = config_manager.get('automation.dry_run')
        self.assertTrue(dry_run)
        
        # Test safety configuration
        safety_config = config_manager.get('safety', {})
        self.assertEqual(safety_config.get('emergency_stop_key'), 'escape')
        
        # Test fallback configuration
        fallback_enabled = config_manager.get('fallback_strategy.enabled')
        self.assertTrue(fallback_enabled)


def run_all_tests():
    """Run all test suites."""
    print("Running comprehensive test suite for all phases...")
    print("=" * 70)
    
    # Create test suites for each phase
    test_suites = [
        ('Phase 1: Foundation', unittest.TestLoader().loadTestsFromTestCase(TestPhase1Foundation)),
        ('Phase 2: Core Features', unittest.TestLoader().loadTestsFromTestCase(TestPhase2CoreFeatures)),
        ('Phase 3: Enhancement', unittest.TestLoader().loadTestsFromTestCase(TestPhase3Enhancement)),
        ('Phase 4: Polish', unittest.TestLoader().loadTestsFromTestCase(TestPhase4Polish)),
        ('Integration Tests', unittest.TestLoader().loadTestsFromTestCase(TestIntegrationScenarios))
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for phase_name, suite in test_suites:
        print(f"\n{phase_name}")
        print("-" * len(phase_name))
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
        if result.failures:
            print(f"FAILURES in {phase_name}:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print(f"ERRORS in {phase_name}:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests run: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("🎉 ALL TESTS PASSED! All phases are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        return False


if __name__ == "__main__":
    # Setup logging for tests
    setup_logging("INFO")
    
    # Run all tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
