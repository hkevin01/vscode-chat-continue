#!/usr/bin/env python3
"""
Comprehensive PyUnit Test Suite for VS Code Chat Continue Automation

This test suite provides comprehensive testing for all components of the
VS Code Chat Continue automation tool using Python's unittest framework.
"""

import argparse
import sys
import unittest
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.integration.test_end_to_end import TestEndToEnd
from tests.integration.test_error_handling import TestErrorHandling
from tests.integration.test_multi_window import TestMultiWindow
from tests.unit.test_automation_engine import TestAutomationEngine
from tests.unit.test_button_finder import TestButtonFinder
from tests.unit.test_click_automator import TestClickAutomator

# Import all test modules
from tests.unit.test_config_manager import TestConfigManager
from tests.unit.test_logger import TestLogger
from tests.unit.test_screen_capture import TestScreenCapture
from tests.unit.test_window_detector import TestWindowDetector


def create_test_suite():
    """Create and return the complete test suite."""
    suite = unittest.TestSuite()
    
    # Unit tests
    suite.addTest(unittest.makeSuite(TestConfigManager))
    suite.addTest(unittest.makeSuite(TestButtonFinder))
    suite.addTest(unittest.makeSuite(TestWindowDetector))
    suite.addTest(unittest.makeSuite(TestScreenCapture))
    suite.addTest(unittest.makeSuite(TestClickAutomator))
    suite.addTest(unittest.makeSuite(TestAutomationEngine))
    suite.addTest(unittest.makeSuite(TestLogger))
    
    # Integration tests
    suite.addTest(unittest.makeSuite(TestEndToEnd))
    suite.addTest(unittest.makeSuite(TestMultiWindow))
    suite.addTest(unittest.makeSuite(TestErrorHandling))
    
    return suite


def run_tests(verbosity=2):
    """Run all tests with the specified verbosity level."""
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Test Results Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    success_rate = (
        (result.testsRun - len(result.failures) - len(result.errors))
        / result.testsRun * 100
    )
    print(f"Success rate: {success_rate:.1f}%")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run VS Code Chat Continue test suite'
    )
    parser.add_argument(
        '-v', '--verbosity', type=int, default=2, choices=[0, 1, 2],
        help='Test output verbosity (0=quiet, 1=normal, 2=verbose)'
    )
    parser.add_argument(
        '--unit-only', action='store_true',
        help='Run only unit tests'
    )
    parser.add_argument(
        '--integration-only', action='store_true',
        help='Run only integration tests'
    )
    
    args = parser.parse_args()
    
    if args.unit_only:
        # Run only unit tests
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestConfigManager))
        suite.addTest(unittest.makeSuite(TestButtonFinder))
        suite.addTest(unittest.makeSuite(TestWindowDetector))
        suite.addTest(unittest.makeSuite(TestScreenCapture))
        suite.addTest(unittest.makeSuite(TestClickAutomator))
        suite.addTest(unittest.makeSuite(TestAutomationEngine))
        suite.addTest(unittest.makeSuite(TestLogger))
        runner = unittest.TextTestRunner(verbosity=args.verbosity)
        result = runner.run(suite)
    elif args.integration_only:
        # Run only integration tests
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestEndToEnd))
        suite.addTest(unittest.makeSuite(TestMultiWindow))
        suite.addTest(unittest.makeSuite(TestErrorHandling))
        runner = unittest.TextTestRunner(verbosity=args.verbosity)
        result = runner.run(suite)
    else:
        # Run all tests
        success = run_tests(args.verbosity)
        sys.exit(0 if success else 1)
