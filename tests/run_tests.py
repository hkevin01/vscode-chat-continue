#!/usr/bin/env python3
"""
PyUnit Test Runner for VS Code Chat Continue Automation

This script provides a comprehensive test runner using Python's unittest framework.
"""

import argparse
import sys
import unittest
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def discover_tests(test_dir='tests', pattern='test_*.py'):
    """Discover and return test suite from specified directory."""
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent / test_dir.replace('tests/', '')
    suite = loader.discover(start_dir, pattern=pattern, top_level_dir=project_root)
    return suite


def run_unit_tests():
    """Run only unit tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Manually add unit test modules
    unit_test_dir = Path(__file__).parent / 'unit'
    if unit_test_dir.exists():
        unit_suite = loader.discover(unit_test_dir, pattern='test_*.py', top_level_dir=project_root)
        suite.addTest(unit_suite)
    
    return suite


def run_integration_tests():
    """Run only integration tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Manually add integration test modules
    integration_test_dir = Path(__file__).parent / 'integration'
    if integration_test_dir.exists():
        integration_suite = loader.discover(integration_test_dir, pattern='test_*.py', top_level_dir=project_root)
        suite.addTest(integration_suite)
    
    return suite


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='VS Code Chat Continue Test Runner')
    parser.add_argument('-v', '--verbosity', type=int, default=2, choices=[0, 1, 2],
                        help='Test output verbosity (0=quiet, 1=normal, 2=verbose)')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--pattern', default='test_*.py', help='Test file pattern')
    
    args = parser.parse_args()
    
    # Create test suite based on arguments
    if args.unit:
        suite = run_unit_tests()
        print("Running Unit Tests...")
    elif args.integration:
        suite = run_integration_tests()
        print("Running Integration Tests...")
    else:
        suite = discover_tests(pattern=args.pattern)
        print("Running All Tests...")
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=args.verbosity, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Test Results Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) 
                       / result.testsRun * 100)
        print(f"Success rate: {success_rate:.1f}%")
    print(f"{'='*60}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
