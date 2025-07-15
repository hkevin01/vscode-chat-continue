#!/usr/bin/env python3
"""
VS Code Chat Continue Button Automation - PyQt6 GUI

Modern GUI interface for the automation tool with dark theme,
tabbed interface, real-time monitoring, and configuration management.
"""

# Apply gnome-screenshot prevention before PyQt6 imports
import sys
from pathlib import Path

# Ensure the src directory is in Python path for imports
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from utils.gnome_screenshot_fix import setup_screenshot_environment

setup_screenshot_environment()

import argparse
import time
from typing import Dict, Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Import core modules (path already set above)
from core.automation_engine import AutomationEngine
from core.config_manager import ConfigManager
from utils.logger import setup_logging


class AutomationWorker(QThread):
    """Worker thread for running automation in the background."""

    status_update = pyqtSignal(str)
    stats_update = pyqtSignal(dict)
    log_message = pyqtSignal(str, str)  # level, message

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.automation_engine: Optional[AutomationEngine] = None
        self.running = False

    def run(self):
        """Run automation in worker thread."""
        try:
            self.running = True
            self.status_update.emit("Starting automation...")

            # Initialize automation engine
            self.automation_engine = AutomationEngine(self.config_manager)

            # Check if demo mode or real automation
            demo_mode = self.config_manager.get("demo_mode", False)
            if demo_mode:
                self.log_message.emit("INFO", "Running in demo mode")
                self._simulate_automation()
            else:
                self.log_message.emit("INFO", "Running real automation")
                self._run_real_automation()

        except Exception as e:
            self.log_message.emit("ERROR", f"Automation error: {e}")
            self.status_update.emit("Error occurred")

    def _run_real_automation(self):
        """Run real automation with actual button detection and clicking."""
        import asyncio

        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run the automation engine
            loop.run_until_complete(self._automation_loop())
        finally:
            loop.close()

    async def _automation_loop(self):
        """Main automation loop running in async context."""
        import asyncio

        cycle_count = 0
        self._last_click_count = 0
        self._last_gui_update = 0
        GUI_UPDATE_INTERVAL = 3  # Update GUI every 3 cycles for performance

        # Start the automation engine
        if self.automation_engine:
            # Don't call start() as it would create a conflicting loop
            # Instead, run the automation manually
            self.automation_engine.running = True
            self.automation_engine.stats["start_time"] = int(time.time())

        while self.running and self.automation_engine:
            try:
                cycle_count += 1

                # Only update status occasionally to reduce GUI overhead
                if cycle_count % GUI_UPDATE_INTERVAL == 0:
                    self.status_update.emit(f"Running cycle {cycle_count}...")

                # Run one automation cycle with enhanced logging
                self.log_message.emit(
                    "DEBUG", f"Starting cycle {cycle_count} - processing windows..."
                )
                await self.automation_engine._process_vscode_windows()

                # Log stats after each cycle
                engine_stats = self.automation_engine.get_statistics()
                if cycle_count % 5 == 0:  # Log detailed stats every 5 cycles
                    windows_count = engine_stats.get("windows_processed", 0)
                    buttons_count = engine_stats.get("buttons_found", 0)
                    clicks_count = engine_stats.get("clicks_attempted", 0)
                    self.log_message.emit(
                        "INFO",
                        f"Cycle {cycle_count}: Windows: {windows_count}, "
                        f"Buttons: {buttons_count}, Clicks: {clicks_count}",
                    )

                # Only update GUI stats every few cycles to improve performance
                if cycle_count % GUI_UPDATE_INTERVAL == 0:
                    # Get current window count (cached to avoid repeated calls)
                    detector = self.automation_engine.window_detector
                    current_windows = detector.get_vscode_windows()
                    current_window_count = len(current_windows)

                    # Get real stats from automation engine
                    report = self.automation_engine.get_performance_report()
                    engine_stats = report["statistics"]

                    # Enhanced stats for GUI display
                    gui_stats = {
                        "cycles": cycle_count,
                        "windows_found": current_window_count,
                        "buttons_clicked": engine_stats.get("clicks_successful", 0),
                        "buttons_attempted": engine_stats.get("clicks_attempted", 0),
                        "success_rate": report.get("success_rate", 0) * 100,
                        "errors": engine_stats.get("errors", 0),
                        "runtime": report.get("runtime_seconds", 0),
                    }

                    self.stats_update.emit(gui_stats)

                    # Log new button clicks (only when GUI updates)
                    clicks = engine_stats.get("clicks_successful", 0)
                    if clicks > self._last_click_count:
                        new_clicks = clicks - self._last_click_count
                        self.log_message.emit(
                            "SUCCESS",
                            f"Clicked {new_clicks} Continue " f"button(s)! Total: {clicks}",
                        )
                        self._last_click_count = clicks

                # Longer sleep interval to reduce CPU usage
                interval = self.config_manager.get("automation.interval_seconds", 5.0)
                await asyncio.sleep(max(interval, 3.0))  # Minimum 3 seconds

            except Exception as e:
                self.log_message.emit("ERROR", f"Cycle error: {e}")
                await asyncio.sleep(10)  # Wait longer before retrying

    def _calculate_success_rate(self, stats: Dict) -> float:
        """Calculate success rate from engine stats."""
        attempted = stats.get("clicks_attempted", 0)
        successful = stats.get("clicks_successful", 0)
        if attempted > 0:
            return (successful / attempted) * 100
        return 0.0

    def _simulate_automation(self):
        """Simulate automation for demo purposes."""
        cycle_count = 0
        windows_found = 0
        buttons_clicked = 0

        while self.running:
            # Simulate detection cycle with longer sleep for performance
            time.sleep(5)  # Increased from 2 to 5 seconds
            cycle_count += 1

            # Simulate finding windows and buttons (less frequently)
            if cycle_count % 4 == 0:  # Every 4th cycle find a window
                windows_found += 1
                self.log_message.emit("INFO", f"Found VS Code window #{windows_found}")

                if cycle_count % 8 == 0:  # Every 8th cycle click a button
                    buttons_clicked += 1
                    self.log_message.emit(
                        "SUCCESS", f"Clicked Continue button " f"#{buttons_clicked}"
                    )

            # Update statistics (less frequently)
            if cycle_count % 2 == 0:  # Update GUI every other cycle
                stats = {
                    "cycles": cycle_count,
                    "windows_found": windows_found,
                    "buttons_clicked": buttons_clicked,
                    "success_rate": (buttons_clicked / max(windows_found, 1)) * 100,
                }
                self.stats_update.emit(stats)

            # Update status (even less frequently)
            if cycle_count % 10 == 0:
                self.status_update.emit(f"Demo Mode... (Cycle {cycle_count})")

    def stop(self):
        """Stop the automation worker."""
        self.running = False
        if self.automation_engine:
            # Clean up automation engine
            self.automation_engine.running = False
            self.automation_engine = None  # Free memory
        self.status_update.emit("Stopped")


class StatisticsWidget(QWidget):
    """Widget displaying real-time automation statistics."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Statistics display
        stats_group = QGroupBox("Real-time Statistics")
        stats_layout = QGridLayout()

        self.cycles_label = QLabel("Detection Cycles: 0")
        self.windows_label = QLabel("Windows Found: 0")
        self.buttons_label = QLabel("Buttons Clicked: 0")
        self.attempts_label = QLabel("Click Attempts: 0")
        self.success_label = QLabel("Success Rate: 0%")
        self.errors_label = QLabel("Errors: 0")

        stats_layout.addWidget(self.cycles_label, 0, 0)
        stats_layout.addWidget(self.windows_label, 0, 1)
        stats_layout.addWidget(self.buttons_label, 1, 0)
        stats_layout.addWidget(self.attempts_label, 1, 1)
        stats_layout.addWidget(self.success_label, 2, 0)
        stats_layout.addWidget(self.errors_label, 2, 1)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Performance metrics
        perf_group = QGroupBox("Performance Metrics")
        perf_layout = QVBoxLayout()

        self.performance_table = QTableWidget(5, 2)
        self.performance_table.setHorizontalHeaderLabels(["Metric", "Value"])

        metrics = ["Avg Detection Time", "Cache Hit Rate", "Memory Usage", "CPU Usage", "Uptime"]

        for i, metric in enumerate(metrics):
            self.performance_table.setItem(i, 0, QTableWidgetItem(metric))
            self.performance_table.setItem(i, 1, QTableWidgetItem("--"))

        perf_layout.addWidget(self.performance_table)
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)

        self.setLayout(layout)

    def update_stats(self, stats: Dict):
        """Update statistics display."""
        cycles = stats.get("cycles", 0)
        windows = stats.get("windows_processed", 0)  # Use correct field name
        clicks = stats.get("clicks_successful", 0)  # Use correct field name
        attempts = stats.get("clicks_attempted", 0)  # Use correct field name
        success_rate = stats.get("success_rate", 0)
        errors = stats.get("errors", 0)

        self.cycles_label.setText(f"Detection Cycles: {cycles}")
        self.windows_label.setText(f"Windows Found: {windows}")
        self.buttons_label.setText(f"Buttons Clicked: {clicks}")
        self.attempts_label.setText(f"Click Attempts: {attempts}")
        self.success_label.setText(f"Success Rate: {success_rate:.1f}%")
        self.errors_label.setText(f"Errors: {errors}")


class ConfigurationWidget(QWidget):
    """Widget for managing automation configuration."""

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.init_ui()
        self.load_config()

    def init_ui(self):
        layout = QVBoxLayout()

        # Automation settings
        auto_group = QGroupBox("Automation Settings")
        auto_layout = QGridLayout()

        auto_layout.addWidget(QLabel("Detection Interval (s):"), 0, 0)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(3, 60)  # Minimum 3 seconds for performance
        self.interval_spin.setValue(8)  # Higher default for better performance
        auto_layout.addWidget(self.interval_spin, 0, 1)

        auto_layout.addWidget(QLabel("Max Retries:"), 1, 0)
        self.retries_spin = QSpinBox()
        self.retries_spin.setRange(1, 10)
        self.retries_spin.setValue(3)
        auto_layout.addWidget(self.retries_spin, 1, 1)

        self.dry_run_check = QCheckBox("Dry Run Mode")
        auto_layout.addWidget(self.dry_run_check, 2, 0, 1, 2)

        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)

        # Detection settings
        detect_group = QGroupBox("Detection Settings")
        detect_layout = QGridLayout()

        detect_layout.addWidget(QLabel("OCR Confidence:"), 0, 0)
        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(50, 100)
        self.confidence_spin.setValue(80)
        detect_layout.addWidget(self.confidence_spin, 0, 1)

        detect_layout.addWidget(QLabel("Search Method:"), 1, 0)
        self.method_combo = QComboBox()
        self.method_combo.addItems(["OCR + Template", "OCR Only", "Template Only"])
        detect_layout.addWidget(self.method_combo, 1, 1)

        detect_group.setLayout(detect_layout)
        layout.addWidget(detect_group)

        # Safety settings
        safety_group = QGroupBox("Safety Settings")
        safety_layout = QGridLayout()

        self.user_activity_check = QCheckBox("Pause on User Activity")
        self.user_activity_check.setChecked(True)
        safety_layout.addWidget(self.user_activity_check, 0, 0, 1, 2)

        safety_layout.addWidget(QLabel("Emergency Stop Key:"), 1, 0)
        self.emergency_combo = QComboBox()
        self.emergency_combo.addItems(["F12", "ESC", "CTRL+C"])
        safety_layout.addWidget(self.emergency_combo, 1, 1)

        safety_group.setLayout(safety_layout)
        layout.addWidget(safety_group)

        # Config file management
        file_group = QGroupBox("Configuration File")
        file_layout = QHBoxLayout()

        self.config_path_edit = QLineEdit()
        self.config_path_edit.setReadOnly(True)
        file_layout.addWidget(self.config_path_edit)

        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_config_file)
        file_layout.addWidget(load_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_config_file)
        file_layout.addWidget(save_btn)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Apply button
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self.apply_config)
        layout.addWidget(apply_btn)

        self.setLayout(layout)

    def load_config(self):
        """Load current configuration into UI."""
        config = self.config_manager.config

        # Load automation settings
        automation = config.get("automation", {})
        self.interval_spin.setValue(automation.get("detection_interval", 5))
        self.retries_spin.setValue(automation.get("max_retries", 3))
        self.dry_run_check.setChecked(automation.get("dry_run", False))

        # Load detection settings
        detection = config.get("detection", {})
        self.confidence_spin.setValue(detection.get("ocr_confidence", 80))

        # Load safety settings
        safety = config.get("safety", {})
        self.user_activity_check.setChecked(safety.get("pause_on_user_activity", True))

        # Update config path
        self.config_path_edit.setText(str(self.config_manager.config_path))

    def apply_config(self):
        """Apply UI settings to configuration."""
        # Update automation settings
        self.config_manager.set("automation.detection_interval", self.interval_spin.value())
        self.config_manager.set("automation.max_retries", self.retries_spin.value())
        self.config_manager.set("automation.dry_run", self.dry_run_check.isChecked())

        # Update detection settings
        self.config_manager.set("detection.ocr_confidence", self.confidence_spin.value())

        # Update safety settings
        self.config_manager.set(
            "safety.pause_on_user_activity", self.user_activity_check.isChecked()
        )

        QMessageBox.information(self, "Settings Applied", "Configuration has been updated.")

    def load_config_file(self):
        """Load configuration from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                # Create a new config manager with the selected file
                new_config = ConfigManager(Path(file_path))
                # Copy the config data
                self.config_manager.config = new_config.config.copy()
                self.load_config()
                QMessageBox.information(self, "Success", "Configuration loaded successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load configuration: {e}")

    def save_config_file(self):
        """Save configuration to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                # Apply current settings first
                self.apply_config()
                # Save to the specified file
                with open(file_path, "w") as f:
                    import json

                    json.dump(self.config_manager.config, f, indent=2)
                QMessageBox.information(self, "Success", "Configuration saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")


class LogWidget(QWidget):
    """Widget for displaying application logs."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Log controls
        controls_layout = QHBoxLayout()

        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        controls_layout.addWidget(clear_btn)

        export_btn = QPushButton("Export Logs")
        export_btn.clicked.connect(self.export_logs)
        controls_layout.addWidget(export_btn)

        controls_layout.addStretch()

        # Log level filter
        controls_layout.addWidget(QLabel("Level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR"])
        controls_layout.addWidget(self.level_combo)

        layout.addLayout(controls_layout)

        # Log display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.log_text)

        self.setLayout(layout)

    def add_log_message(self, level: str, message: str):
        """Add a log message to the display."""
        timestamp = time.strftime("%H:%M:%S")
        color_map = {
            "DEBUG": "#888888",
            "INFO": "#ffffff",
            "SUCCESS": "#00ff00",
            "WARNING": "#ffaa00",
            "ERROR": "#ff0000",
        }

        color = color_map.get(level, "#ffffff")
        formatted_message = (
            f'<span style="color: {color}">[{timestamp}] {level}: ' f"{message}</span><br>"
        )

        self.log_text.insertHtml(formatted_message)
        self.log_text.ensureCursorVisible()

    def clear_logs(self):
        """Clear all log messages."""
        self.log_text.clear()

    def export_logs(self):
        """Export logs to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", "automation_logs.txt", "Text Files (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(self.log_text.toPlainText())
                QMessageBox.information(self, "Success", "Logs exported successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export logs: {e}")


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""

    def __init__(self, config_path: Optional[Path] = None):
        super().__init__()
        self.config_manager = ConfigManager(config_path)
        self.automation_worker: Optional[AutomationWorker] = None
        self.init_ui()
        self.setup_logging()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("VS Code Chat Continue Automation")
        self.setGeometry(100, 100, 1000, 700)

        # Apply dark theme
        self.apply_dark_theme()

        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Status bar
        self.status_label = QLabel("Ready")
        self.status_progress = QProgressBar()
        self.status_progress.setVisible(False)

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.status_progress)

        layout.addLayout(status_layout)

        # Main control buttons
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("🚀 Start Automation")
        self.start_btn.clicked.connect(self.start_automation)
        self.start_btn.setMinimumHeight(40)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹️ Stop Automation")
        self.stop_btn.clicked.connect(self.stop_automation)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(40)
        button_layout.addWidget(self.stop_btn)

        self.demo_btn = QPushButton("🎭 Demo Mode")
        self.demo_btn.clicked.connect(self.start_demo)
        self.demo_btn.setMinimumHeight(40)
        button_layout.addWidget(self.demo_btn)

        layout.addLayout(button_layout)

        # Tab widget
        self.tab_widget = QTabWidget()

        # Control tab
        self.control_tab = self.create_control_tab()
        self.tab_widget.addTab(self.control_tab, "🎮 Control")

        # Statistics tab
        self.stats_tab = StatisticsWidget()
        self.tab_widget.addTab(self.stats_tab, "📊 Statistics")

        # Configuration tab
        self.config_tab = ConfigurationWidget(self.config_manager)
        self.tab_widget.addTab(self.config_tab, "⚙️ Configuration")

        # Logs tab
        self.log_tab = LogWidget()
        self.tab_widget.addTab(self.log_tab, "📋 Logs")

        layout.addWidget(self.tab_widget)

        # Emergency stop button
        emergency_btn = QPushButton("🚨 EMERGENCY STOP")
        emergency_btn.clicked.connect(self.emergency_stop)
        emergency_btn.setStyleSheet(
            "QPushButton { background-color: #ff4444; color: white; " "font-weight: bold; }"
        )
        emergency_btn.setMinimumHeight(30)
        layout.addWidget(emergency_btn)

    def create_control_tab(self) -> QWidget:
        """Create the main control tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Welcome message
        welcome_group = QGroupBox("Welcome to VS Code Chat Continue Automation")
        welcome_layout = QVBoxLayout()

        welcome_text = QLabel(
            """
        <h3>🤖 Intelligent Continue Button Detection</h3>
        <p>This tool automatically detects and clicks "Continue" buttons in
        VS Code Copilot Chat sessions.</p>
        
        <h4>Features:</h4>
        <ul>
        <li>🔍 Multi-method detection (OCR + Template matching)</li>
        <li>🪟 Multi-window support for all VS Code instances</li>
        <li>⚡ Real-time performance monitoring</li>
        <li>🛡️ Safety features with user activity detection</li>
        <li>🎯 Fallback strategies for maximum reliability</li>
        </ul>
        
        <h4>Quick Start:</h4>
        <ol>
        <li>Ensure VS Code is running with Copilot Chat sessions</li>
        <li>Click "Start Automation" to begin</li>
        <li>Monitor progress in the Statistics tab</li>
        <li>Use "Demo Mode" to test without automation components</li>
        </ol>
        """
        )
        welcome_text.setWordWrap(True)
        welcome_layout.addWidget(welcome_text)

        welcome_group.setLayout(welcome_layout)
        layout.addWidget(welcome_group)

        # Quick settings
        quick_group = QGroupBox("Quick Settings")
        quick_layout = QGridLayout()

        quick_layout.addWidget(QLabel("Detection Interval:"), 0, 0)
        self.quick_interval = QSpinBox()
        self.quick_interval.setRange(3, 60)  # Minimum 3 seconds for performance
        self.quick_interval.setValue(8)  # Higher default for better performance
        self.quick_interval.setSuffix(" seconds")
        quick_layout.addWidget(self.quick_interval, 0, 1)

        self.quick_dry_run = QCheckBox("Dry Run Mode (Preview Only)")
        quick_layout.addWidget(self.quick_dry_run, 1, 0, 1, 2)

        self.quick_demo_mode = QCheckBox("Demo Mode (Simulated Stats)")
        quick_layout.addWidget(self.quick_demo_mode, 2, 0, 1, 2)

        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def apply_dark_theme(self):
        """Apply dark theme to the application."""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #3c3c3c;
            }
            QTabBar::tab {
                background-color: #555555;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #4c4c4c;
                color: #ffffff;
                border: 1px solid #666666;
                padding: 4px;
                border-radius: 3px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #666666;
            }
            QTableWidget {
                background-color: #3c3c3c;
                color: #ffffff;
                gridline-color: #666666;
            }
            QCheckBox {
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
        """
        )

    def setup_logging(self):
        """Setup logging integration with GUI."""
        setup_logging(self.config_manager.get_log_level())

        # Add initial log message
        self.log_tab.add_log_message("INFO", "Application started")

    def _cleanup_existing_processes(self):
        """Kill any existing automation processes to prevent conflicts."""
        import psutil

        try:
            self.log_tab.add_log_message("INFO", "Cleaning up existing automation processes...")

            # List of process patterns to kill
            patterns = [
                "lightweight_automation.py",
                "main_window.py",
                "run.sh",
                "continuous_automation.py",
                "vscode-chat-continue",
            ]

            killed_count = 0

            # Find and kill matching processes
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    proc_info = proc.info
                    cmdline = proc_info.get("cmdline", [])

                    if cmdline:
                        cmdline_str = " ".join(str(arg) for arg in cmdline if arg)

                        # Skip our own process
                        if proc.pid == psutil.Process().pid:
                            continue

                        # Check if this is an automation process
                        for pattern in patterns:
                            if pattern in cmdline_str:
                                try:
                                    proc.terminate()
                                    proc.wait(timeout=3)
                                    killed_count += 1
                                    self.log_tab.add_log_message(
                                        "INFO", f"Terminated process {proc.pid}: " f"{pattern}"
                                    )
                                    break
                                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                                    try:
                                        proc.kill()
                                        killed_count += 1
                                        self.log_tab.add_log_message(
                                            "WARNING",
                                            f"Force killed process " f"{proc.pid}: {pattern}",
                                        )
                                    except psutil.NoSuchProcess:
                                        pass

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if killed_count > 0:
                msg = f"Cleaned up {killed_count} existing automation " f"process(es)"
                self.log_tab.add_log_message("INFO", msg)
            else:
                msg = "No existing automation processes found"
                self.log_tab.add_log_message("INFO", msg)

        except Exception as e:
            msg = f"Error during process cleanup: {e}"
            self.log_tab.add_log_message("WARNING", msg)

    def start_automation(self):
        """Start the automation process."""
        if self.automation_worker and self.automation_worker.isRunning():
            return

        self.log_tab.add_log_message("INFO", "Starting automation...")

        # Kill any existing automation processes first
        self._cleanup_existing_processes()

        # Apply quick settings to config
        self.config_manager.set("automation.detection_interval", self.quick_interval.value())
        self.config_manager.set("automation.dry_run", self.quick_dry_run.isChecked())
        self.config_manager.set("demo_mode", self.quick_demo_mode.isChecked())
        # Ensure audio is disabled to prevent beeping
        self.config_manager.set("audio.enabled", False)

        # Disable system bell/beep to prevent terminal beeps
        self.config_manager.set("system.disable_bell", True)

        # Start worker thread
        self.automation_worker = AutomationWorker(self.config_manager)
        self.automation_worker.status_update.connect(self.update_status)
        self.automation_worker.stats_update.connect(self.stats_tab.update_stats)
        self.automation_worker.log_message.connect(self.log_tab.add_log_message)

        self.automation_worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_progress.setVisible(True)
        self.status_progress.setRange(0, 0)  # Indeterminate progress

    def stop_automation(self):
        """Stop the automation process."""
        if self.automation_worker:
            self.log_tab.add_log_message("INFO", "Stopping automation...")
            self.automation_worker.stop()
            self.automation_worker.wait()  # Wait for thread to finish

        self.update_status("Stopped")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_progress.setVisible(False)

    def start_demo(self):
        """Start demo mode."""
        self.log_tab.add_log_message("INFO", "Starting demo mode...")
        self.config_manager.set("automation.dry_run", True)
        self.quick_dry_run.setChecked(True)
        self.start_automation()

    def emergency_stop(self):
        """Emergency stop function."""
        self.log_tab.add_log_message("WARNING", "EMERGENCY STOP activated!")
        self.stop_automation()

        # Show emergency dialog
        QMessageBox.warning(
            self,
            "Emergency Stop",
            "Automation has been stopped immediately.\n\n"
            "All automation processes have been terminated.",
        )

    def update_status(self, status: str):
        """Update status display."""
        self.status_label.setText(status)

    def closeEvent(self, event):
        """Handle application close event."""
        if self.automation_worker and self.automation_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Automation is still running. Do you want to stop it " "and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.stop_automation()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser for GUI."""
    parser = argparse.ArgumentParser(
        description="VS Code Chat Continue Automation - GUI Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--config", "-c", type=Path, help="Path to configuration file")

    parser.add_argument("--dry-run", action="store_true", help="Start in dry-run mode")

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser


def main():
    """Main entry point for GUI application."""
    try:
        print("GUI: Starting main function...")

        # Parse arguments
        parser = create_parser()
        args = parser.parse_args()
        print("GUI: Arguments parsed")

        # Test display
        import os

        print(f"GUI: DISPLAY = {os.environ.get('DISPLAY', 'Not set')}")
        # Create application with clean argv to avoid conflicts
        print("GUI: Creating QApplication...")
        # Check if QApplication already exists

        app = QApplication.instance()
        if app is None:
            app = QApplication(["gui-app"])
            app.setApplicationName("VS Code Chat Continue Automation")
            app.setApplicationVersion("1.0.0")
            print("GUI: QApplication created")
        else:
            print("GUI: Using existing QApplication instance")

        # Create and show main window
        print("GUI: Creating MainWindow...")
        window = MainWindow(args.config)
        print("GUI: MainWindow created")

        # Apply command line overrides
        if args.dry_run:
            window.config_manager.set("automation.dry_run", True)
            window.quick_dry_run.setChecked(True)

        if args.debug:
            window.config_manager.set("logging.level", "DEBUG")

        print("GUI: Showing window...")
        window.show()
        print("GUI: Window shown, starting event loop...")

        # Run application (don't use sys.exit to allow graceful return)
        return app.exec()

    except Exception as e:
        print(f"GUI: Error in main: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
