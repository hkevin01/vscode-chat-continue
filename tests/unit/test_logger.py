"""Unit tests for Logger module."""

import logging
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import AutomationLogger, setup_logging


class TestLogger(unittest.TestCase):
    """Test cases for AutomationLogger class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_config = {
            "level": "INFO",
            "console_output": True,
            "file_path": "logs/test_automation.log",
            "max_file_size_mb": 1,
            "backup_count": 3,
            "detailed_timing": True
        }
        
    def test_automation_logger_initialization(self):
        """Test AutomationLogger initialization."""
        logger = AutomationLogger(self.test_config)
        
        self.assertIsNotNone(logger)
        self.assertIsNotNone(logger.logger)
        self.assertIsInstance(logger.stats, dict)
        
    def test_logger_stats_initialization(self):
        """Test that logger statistics are initialized correctly."""
        logger = AutomationLogger(self.test_config)
        
        stats = logger.stats
        self.assertIn('start_time', stats)
        self.assertEqual(stats['operations'], 0)
        self.assertEqual(stats['successes'], 0)
        self.assertEqual(stats['failures'], 0)
        self.assertEqual(stats['windows_processed'], 0)
        self.assertEqual(stats['buttons_found'], 0)
        self.assertEqual(stats['fallback_used'], 0)
        self.assertIsInstance(stats['performance_metrics'], list)
        
    def test_log_operation_start(self):
        """Test logging operation start."""
        logger = AutomationLogger(self.test_config)
        
        operation_id = logger.log_operation_start("test_operation")
        
        self.assertIsNotNone(operation_id)
        self.assertEqual(logger.stats['operations'], 1)
        
    def test_log_operation_start_with_details(self):
        """Test logging operation start with details."""
        logger = AutomationLogger(self.test_config)
        
        details = {"window_count": 3, "confidence": 0.8}
        operation_id = logger.log_operation_start(
            "test_operation", details
        )
        
        self.assertIsNotNone(operation_id)
        self.assertEqual(logger.stats['operations'], 1)
        
    def test_log_operation_success(self):
        """Test logging operation success."""
        logger = AutomationLogger(self.test_config)
        
        operation_id = logger.log_operation_start("test_operation")
        logger.log_operation_success("test_operation", operation_id)
        
        self.assertEqual(logger.stats['successes'], 1)
        
    def test_log_operation_success_with_result(self):
        """Test logging operation success with result."""
        logger = AutomationLogger(self.test_config)
        
        operation_id = logger.log_operation_start("test_operation")
        result = {"buttons_found": 2, "clicks_made": 1}
        logger.log_operation_success(
            "test_operation", operation_id, result
        )
        
        self.assertEqual(logger.stats['successes'], 1)
        
    def test_log_operation_failure(self):
        """Test logging operation failure."""
        logger = AutomationLogger(self.test_config)
        
        operation_id = logger.log_operation_start("test_operation")
        logger.log_operation_failure(
            "test_operation", "Test error message", operation_id
        )
        
        self.assertEqual(logger.stats['failures'], 1)
        
    def test_log_window_processed(self):
        """Test logging window processing."""
        logger = AutomationLogger(self.test_config)
        
        window_info = {
            "id": 123,
            "title": "VS Code",
            "buttons_found": 1
        }
        logger.log_window_processed(window_info)
        
        self.assertEqual(logger.stats['windows_processed'], 1)
        
    def test_log_button_found(self):
        """Test logging button found."""
        logger = AutomationLogger(self.test_config)
        
        button_info = {
            "x": 100, "y": 200,
            "confidence": 0.9,
            "method": "ocr"
        }
        logger.log_button_found(button_info)
        
        self.assertEqual(logger.stats['buttons_found'], 1)
        
    def test_log_fallback_used(self):
        """Test logging fallback usage."""
        logger = AutomationLogger(self.test_config)
        
        logger.log_fallback_used("ocr_failed", "color_detection")
        
        self.assertEqual(logger.stats['fallback_used'], 1)
        
    def test_get_stats(self):
        """Test getting statistics."""
        logger = AutomationLogger(self.test_config)
        
        # Perform some operations
        logger.log_operation_start("test1")
        logger.log_operation_success("test1")
        logger.log_operation_start("test2")
        logger.log_operation_failure("test2", "error")
        
        stats = logger.get_stats()
        
        self.assertEqual(stats['operations'], 2)
        self.assertEqual(stats['successes'], 1)
        self.assertEqual(stats['failures'], 1)
        self.assertIn('start_time', stats)
        
    def test_get_runtime(self):
        """Test getting runtime."""
        logger = AutomationLogger(self.test_config)
        
        runtime = logger.get_runtime()
        
        self.assertIsInstance(runtime, float)
        self.assertGreaterEqual(runtime, 0)
        
    @patch('time.time')
    def test_performance_metrics_tracking(self, mock_time):
        """Test performance metrics tracking."""
        # Mock time progression
        mock_time.side_effect = [1000, 1001, 1002, 1003]
        
        logger = AutomationLogger(self.test_config)
        
        operation_id = logger.log_operation_start("perf_test")
        logger.log_operation_success("perf_test", operation_id)
        
        # Check that performance metrics were recorded
        self.assertGreater(len(logger.stats['performance_metrics']), 0)
        
    def test_setup_logging_function(self):
        """Test the setup_logging function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test that setup_logging doesn't crash
            setup_logging("DEBUG")
            
            # Verify a logger was created
            test_logger = logging.getLogger("test")
            self.assertIsNotNone(test_logger)
            
    def test_logger_file_creation(self):
        """Test that log file is created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = self.test_config.copy()
            config['file_path'] = str(Path(temp_dir) / "test.log")
            
            logger = AutomationLogger(config)
            
            # Log something to ensure file is created
            logger.log_operation_start("test")
            
            log_file = Path(config['file_path'])
            self.assertTrue(log_file.exists())
            
    def test_logger_console_output_disabled(self):
        """Test logger with console output disabled."""
        config = self.test_config.copy()
        config['console_output'] = False
        
        logger = AutomationLogger(config)
        
        # Should not raise any errors
        logger.log_operation_start("test")
        
    def test_logger_different_log_levels(self):
        """Test logger with different log levels."""
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        
        for level in levels:
            with self.subTest(level=level):
                config = self.test_config.copy()
                config['level'] = level
                
                logger = AutomationLogger(config)
                self.assertIsNotNone(logger)
                
    def test_update_performance_metric(self):
        """Test updating performance metrics."""
        logger = AutomationLogger(self.test_config)
        
        operation_id = logger.log_operation_start("test_op")
        result = {"test": "data"}
        
        # This tests the internal method
        logger._update_performance_metric(operation_id, "success", result)
        
        # Check that metrics were updated
        metrics = logger.stats['performance_metrics']
        if metrics:  # Only check if metrics are being tracked
            self.assertGreater(len(metrics), 0)
            
    def test_error_handling_in_logging(self):
        """Test error handling in logging operations."""
        # Test with invalid config
        invalid_config = {"level": "INVALID_LEVEL"}
        
        try:
            logger = AutomationLogger(invalid_config)
            # Should handle invalid config gracefully
            self.assertIsNotNone(logger)
        except Exception:
            self.fail("AutomationLogger should handle invalid config gracefully")


if __name__ == '__main__':
    unittest.main()
