"""Pytest configuration and shared fixtures."""

import asyncio

# Add src to path for testing
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from core.button_finder import ButtonLocation
from core.config_manager import ConfigManager
from core.window_detector import VSCodeWindow


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_data = {
            "automation": {
                "detection_interval": 5,
                "dry_run": True,
                "max_clicks_per_window": 3
            },
            "detection": {
                "ocr_confidence": 80,
                "fallback_strategies": ["coordinate", "text", "color"]
            },
            "safety": {
                "pause_on_user_activity": True,
                "emergency_stop_key": "F12"
            }
        }
        import json
        json.dump(config_data, f, indent=2)
        temp_path = f.name
    
    yield Path(temp_path)
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def config_manager(temp_config_file):
    """Create a ConfigManager instance with test configuration."""
    return ConfigManager(temp_config_file)


@pytest.fixture
def mock_vscode_window():
    """Create a mock VS Code window for testing."""
    return VSCodeWindow(
        window_id=12345,
        title="test_file.py - vscode-chat-continue - Visual Studio Code",
        x=100,
        y=100, 
        width=1920,
        height=1080
    )


@pytest.fixture
def mock_button_location():
    """Create a mock button location for testing."""
    return ButtonLocation(
        x=1800,
        y=900,
        width=120,
        height=32,
        confidence=0.95,
        method="test_method",
        text="Continue"
    )


@pytest.fixture
def mock_image():
    """Create a mock PIL Image for testing."""
    from PIL import Image
    return Image.new('RGB', (100, 100), color='black')


@pytest.fixture
def mock_screenshot():
    """Create a mock screenshot for testing."""
    from PIL import Image
    return Image.new('RGB', (1920, 1080), color='white')


@pytest.fixture
def mock_automation_engine():
    """Create a mock automation engine for testing."""
    mock_engine = Mock()
    mock_engine.running = False
    mock_engine.stats = {
        'windows_processed': 0,
        'buttons_found': 0,
        'clicks_attempted': 0,
        'clicks_successful': 0,
        'errors': 0,
        'start_time': 0
    }
    mock_engine.get_statistics.return_value = mock_engine.stats
    mock_engine.get_performance_report.return_value = {
        'statistics': mock_engine.stats,
        'success_rate': 0.0,
        'runtime_seconds': 0
    }
    return mock_engine


@pytest.fixture(autouse=True)
def suppress_gui_in_tests(monkeypatch):
    """Automatically suppress GUI components during testing."""
    # Mock PyQt6 components that might cause issues in headless testing
    mock_app = Mock()
    mock_widget = Mock()
    
    # This prevents actual GUI creation during tests
    monkeypatch.setattr('PyQt6.QtWidgets.QApplication', lambda *args: mock_app)
    monkeypatch.setattr('PyQt6.QtWidgets.QMainWindow', lambda *args: mock_widget)


@pytest.fixture
def disable_audio():
    """Disable audio/sound during testing."""
    import os

    # Set environment variables to disable audio
    os.environ['PULSE_DISABLE'] = '1'
    os.environ['ALSA_DISABLE'] = '1'
    yield
    # Cleanup
    os.environ.pop('PULSE_DISABLE', None)
    os.environ.pop('ALSA_DISABLE', None)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "gui: marks tests as requiring GUI"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        
        # Mark GUI tests
        if "gui" in str(item.fspath) or "main_window" in str(item.fspath):
            item.add_marker(pytest.mark.gui)
        
        # Mark slow tests
        if any(keyword in item.name.lower() for keyword in ['slow', 'benchmark', 'performance']):
            item.add_marker(pytest.mark.slow)
