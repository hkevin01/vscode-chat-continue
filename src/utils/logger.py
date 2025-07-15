"""Enhanced logging system for VS Code Chat Continue automation."""

import json
import logging
import logging.handlers
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class AutomationLogger:
    """Enhanced logger with performance monitoring and statistics tracking."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize logger with configuration."""
        self.config = config
        self.logger = self._setup_logger()
        self.stats = {
            "start_time": time.time(),
            "operations": 0,
            "successes": 0,
            "failures": 0,
            "windows_processed": 0,
            "buttons_found": 0,
            "fallback_used": 0,
            "performance_metrics": [],
        }

    def _setup_logger(self) -> logging.Logger:
        """Set up the logging system with file and console handlers."""
        logger = logging.getLogger("vscode_chat_continue")
        logger.setLevel(getattr(logging, self.config.get("level", "INFO")))

        # Clear existing handlers
        logger.handlers.clear()

        # File handler with rotation
        log_path_str = self.config.get("file_path", "automation.log")
        log_path = Path(log_path_str).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=self.config.get("max_file_size_mb", 10) * 1024 * 1024,
            backupCount=self.config.get("backup_count", 5),
        )
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler if enabled
        if self.config.get("console_output", True):
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter("%(levelname)s: %(message)s")
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        return logger

    def log_operation_start(self, operation: str, details: Optional[Dict[str, Any]] = None):
        """Log the start of an automation operation."""
        self.stats["operations"] += 1
        operation_id = f"{operation}_{int(time.time())}"

        if details:
            self.logger.info(f"Starting {operation}: {details}")
        else:
            self.logger.info(f"Starting {operation}")

        if self.config.get("detailed_timing", False):
            self.stats["performance_metrics"].append(
                {
                    "operation_id": operation_id,
                    "operation": operation,
                    "start_time": time.time(),
                    "details": details or {},
                }
            )

        return operation_id

    def log_operation_success(
        self,
        operation: str,
        operation_id: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
    ):
        """Log successful completion of an operation."""
        self.stats["successes"] += 1

        if result:
            self.logger.info(f"Completed {operation} successfully: {result}")
        else:
            self.logger.info(f"Completed {operation} successfully")

        if operation_id and self.config.get("detailed_timing", False):
            self._update_performance_metric(operation_id, "success", result)

    def log_operation_failure(self, operation: str, error: str, operation_id: Optional[str] = None):
        """Log failed operation."""
        self.stats["failures"] += 1
        self.logger.error(f"Operation {operation} failed: {error}")

        if operation_id and self.config.get("detailed_timing", False):
            self._update_performance_metric(operation_id, "failure", {"error": error})

    def log_window_processed(self, window_info: Dict[str, Any]):
        """Log processing of a VS Code window."""
        self.stats["windows_processed"] += 1
        self.logger.debug(f"Processed window: {window_info}")

    def log_button_found(self, button_info: Dict[str, Any]):
        """Log detection of a continue button."""
        self.stats["buttons_found"] += 1
        self.logger.info(f"Continue button found: {button_info}")

    def log_fallback_used(self, fallback_type: str, details: Optional[Dict[str, Any]] = None):
        """Log use of fallback strategy."""
        self.stats["fallback_used"] += 1
        if details:
            msg = f"Fallback strategy used ({fallback_type}): {details}"
            self.logger.info(msg)
        else:
            self.logger.info(f"Fallback strategy used: {fallback_type}")

    def _update_performance_metric(
        self, operation_id: str, status: str, result: Optional[Dict[str, Any]] = None
    ):
        """Update performance tracking for an operation."""
        for metric in self.stats["performance_metrics"]:
            if metric["operation_id"] == operation_id:
                metric["end_time"] = time.time()
                metric["duration"] = metric["end_time"] - metric["start_time"]
                metric["status"] = status
                metric["result"] = result or {}
                break

    def get_statistics(self) -> Dict[str, Any]:
        """Get current automation statistics."""
        runtime = time.time() - self.stats["start_time"]
        ops = self.stats["operations"]
        success_rate = (self.stats["successes"] / max(1, ops)) * 100

        return {
            **self.stats,
            "runtime_seconds": runtime,
            "success_rate_percent": round(success_rate, 2),
            "operations_per_minute": round((ops / max(1, runtime)) * 60, 2),
        }

    def save_statistics(self, file_path: Optional[Path] = None):
        """Save statistics to a JSON file."""
        if not file_path:
            stats_file = self.config.get("stats_file", "automation_stats.json")
            file_path = Path(stats_file).expanduser()

        try:
            stats = self.get_statistics()
            stats_json = json.dumps(stats, indent=2, default=str)
            file_path.write_text(stats_json)
            self.logger.debug(f"Statistics saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save statistics: {e}")

    # Delegate standard logging methods
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    max_file_size_mb: int = 10,
    backup_count: int = 5,
) -> AutomationLogger:
    """Setup basic logging configuration for backwards compatibility."""
    # Use default log path if none provided
    default_log_path = "~/.local/share/vscode-chat-continue/automation.log"

    config = {
        "level": level,
        "file_path": str(log_file) if log_file else default_log_path,
        "max_file_size_mb": max_file_size_mb,
        "backup_count": backup_count,
        "console_output": True,
    }

    # Create a basic logger instance
    return AutomationLogger(config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
