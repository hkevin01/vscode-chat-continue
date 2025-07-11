"""Comprehensive test suite for VS Code Chat Continue automation."""

import asyncio
import logging
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import numpy as np
import psutil
from PIL import Image

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.automation_engine import AutomationEngine
from src.core.button_finder import ButtonFinder, ButtonLocation
from src.core.click_automator import ClickAutomator, ClickResult
from src.core.config_manager import ConfigManager
from src.core.window_detector import VSCodeWindow, WindowDetector


class TestPhase1Foundation(unittest.TestCase):
    """Test Phase 1: Foundation components."""

    def setUp(self):
        """Set up test environment."""
        self.config = ConfigManager()
        self.test_config = {
            "automation": {"interval_seconds": 1.0, "dry_run": True},
            "detection": {"confidence_threshold": 0.8},
            "safety": {"require_confirmation": False},
            "logging": {"level": "DEBUG", "console_output": False},
        }

    def test_project_setup_and_structure(self):
        """Test project setup and structure."""
        project_root = Path(__file__).resolve().parent.parent
        # Verify essential directories exist
        essential_dirs = [
            project_root / "src/core",
            project_root / "src/utils",
            project_root / "tests/unit",
            project_root / "docs",
            project_root / "config",
            project_root / "scripts",
        ]

        for dir_path in essential_dirs:
            self.assertTrue(
                dir_path.exists(), f"Directory {dir_path} should exist"
            )

        # Verify essential files exist
        essential_files = [
            project_root / "src/main.py",
            project_root / "src/core/config_manager.py",
            project_root / "src/core/window_detector.py",
            project_root / "src/core/automation_engine.py",
            project_root / "requirements.txt",
        ]

        for file_path in essential_files:
            self.assertTrue(
                file_path.exists(), f"File {file_path} should exist"
            )

    def test_config_manager_set_get(self):
        """Test setting and getting configuration values."""
        self.config.set('test.value', 123)
        self.assertEqual(self.config.get('test.value'), 123)
        self.config.set('test.nested.value', 'abc')
        self.assertEqual(self.config.get('test.nested.value'), 'abc')
        self.assertIsNone(self.config.get('non.existent.key'))

    @patch('psutil.process_iter')
    def test_vscode_process_identification(self, mock_process_iter):
        """Test VS Code process identification."""
        mock_process = MagicMock(spec=psutil.Process)
        mock_process.info = {
            'pid': 12345,
            'name': 'code',
            'create_time': time.time()
        }
        mock_process.pid = 12345
        mock_process.name.return_value = 'code'
        mock_process_iter.return_value = [mock_process]

        detector = WindowDetector()
        processes = detector.get_vscode_processes()

        self.assertEqual(len(processes), 1)
        self.assertEqual(processes[0].pid, 12345)
        self.assertEqual(processes[0].name(), 'code')

    @patch('src.core.window_detector.EWMH')
    def test_basic_window_detection(self, mock_ewmh_class):
        """Test basic window detection functionality."""
        mock_ewmh = mock_ewmh_class.return_value
        mock_window = MagicMock()
        mock_window.id = 123

        # Configure the mock EWMH object
        def get_wm_pid(win):
            if win == mock_window:
                return 12345
            return None

        def get_wm_name(win):
            if win == mock_window:
                return b'Visual Studio Code'
            return b''

        def get_geometry(win):
            if win == mock_window:
                return (10, 20, 800, 600)
            return None

        mock_ewmh.getClientList.return_value = [mock_window]
        mock_ewmh.getWmPid.side_effect = get_wm_pid
        mock_ewmh.getWmName.side_effect = get_wm_name
        mock_ewmh.getGeometry.side_effect = get_geometry
        mock_ewmh.getActiveWindow.return_value = mock_window

        detector = WindowDetector()

        # Mock the process that will be associated with the window
        mock_proc = MagicMock(spec=psutil.Process)
        mock_proc.name.return_value = "code"
        mock_proc.pid = 12345

        # Patch get_vscode_processes to return our controlled process list
        with patch.object(
            detector, 'get_vscode_processes', return_value=[mock_proc]
        ):
            windows = detector.get_vscode_windows()
            self.assertGreater(
                len(windows), 0, "Should detect at least one VS Code window"
            )
            self.assertEqual(windows[0].pid, 12345)
            self.assertIn('Visual Studio Code', windows[0].title)


class TestPhase2CoreFeatures(unittest.TestCase):
    """Tests for core features like button detection and click automation."""

    def setUp(self):
        """Set up for core feature tests."""
        self.config = ConfigManager()
        self.config.set('detection.template_matching_enabled', False)
        self.config.set('detection.ocr_enabled', True)
        self.config.set('detection.template_path', 'path/to/fake_template.png')
        self.config.set('detection.detection_threshold', 0.8)
        self.config.set('automation.click_delay_seconds', 0.1)
        self.config.set('automation.move_duration', 0.2)

    @patch('src.core.button_finder.pytesseract.image_to_data')
    @patch(
        'src.core.button_finder.ButtonFinder._find_buttons_template',
        return_value=[]
    )
    @patch(
        'src.core.button_finder.ButtonFinder._find_buttons_color',
        return_value=[]
    )
    def test_continue_button_detection_ocr(
        self, mock_color, mock_template, mock_image_to_data
    ):
        """Test continue button detection using OCR."""
        # Mock pytesseract to return string values, as the library does.
        mock_image_to_data.return_value = {
            'level': ['5'], 'page_num': ['1'], 'block_num': ['1'],
            'par_num': ['1'], 'line_num': ['1'], 'word_num': ['1'],
            'left': ['150'], 'top': ['45'], 'width': ['70'], 'height': ['18'],
            'conf': ['96.3'], 'text': ['Continue']
        }
        finder = ButtonFinder(self.config)
        buttons = finder.find_continue_buttons(
            Image.new('RGB', (250, 100)), 0, 0
        )

        self.assertGreater(len(buttons), 0, "Should find one button")
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0].x, 150)
        self.assertEqual(buttons[0].y, 45)
        self.assertIsNotNone(buttons[0].text)
        if buttons[0].text:
            self.assertEqual(buttons[0].text.lower(), 'continue')

    @patch('src.core.button_finder.cv2.imread')
    @patch('src.core.button_finder.cv2.matchTemplate')
    @patch(
        'src.core.button_finder.ButtonFinder._find_buttons_ocr',
        return_value=[]
    )
    @patch(
        'src.core.button_finder.ButtonFinder._find_buttons_color',
        return_value=[]
    )
    def test_continue_button_detection_template(
        self, mock_color, mock_ocr, mock_match_template, mock_imread
    ):
        """Test continue button detection using template matching."""
        mock_imread.return_value = np.zeros((10, 40, 3), dtype=np.uint8)
        
        result_matrix = np.full((91, 61), 0.5, dtype=np.float32)
        result_matrix[35, 25] = 0.98
        mock_match_template.return_value = result_matrix

        self.config.set('detection.template_matching_enabled', True)
        # The code uses 'template_dir', not 'template_path'
        self.config.set('detection.template_dir', '/mock/path/templates')
        self.config.set('detection.detection_threshold', 0.9)

        # Patch glob on the Path object within the module
        with patch('src.core.button_finder.Path.glob') as mock_glob:
            mock_glob.return_value = [
                Path('/mock/path/templates/template.png')
            ]
            finder = ButtonFinder(self.config)
            buttons = finder.find_continue_buttons(
                Image.new('RGB', (100, 100)), 0, 0
            )

        self.assertGreater(
            len(buttons), 0, "Template matching should find a button"
        )
        self.assertEqual(buttons[0].x, 25)
        self.assertEqual(buttons[0].y, 35)
        self.assertEqual(buttons[0].method, 'Template Matching')

    @patch('pyautogui.click')
    def test_mouse_click_automation(self, mock_click):
        """Test mouse click automation."""
        automator = ClickAutomator(
            click_delay=self.config.get('automation.click_delay_seconds'),
            move_duration=self.config.get('automation.move_duration')
        )
        button = ButtonLocation(
            x=100, y=50, width=50, height=30,
            text='Continue', method='Test', confidence=0.99
        )

        result = automator.click(button.center_x, button.center_y)

        mock_click.assert_called_once_with(
            button.center_x,
            button.center_y,
            button='left',
            duration=self.config.get('automation.move_duration')
        )
        self.assertTrue(result.success)

    def test_basic_error_handling(self):
        """Test basic error handling."""
        try:
            self.config.set('detection.detection_threshold', 'invalid')
            finder = ButtonFinder(self.config)
            # We expect this to not raise an unhandled exception
            buttons = finder.find_continue_buttons(
                Image.new('RGB', (100, 100)), 0, 0
            )
            self.assertIsInstance(buttons, list)
        except TypeError as e:
            self.fail(
                "ButtonFinder should handle invalid config gracefully: "
                f"{e.__class__.__name__}: {e}"
            )


class TestPhase3Integration(unittest.TestCase):
    """Tests for integration between different components."""

    def setUp(self):
        """Set up for integration tests."""
        self.config_manager = ConfigManager()
        self.config_manager.set('logging.log_level', 'DEBUG')
        self.config_manager.set(
            'logging.log_file', 'logs/test_integration.log'
        )
        log_file_str = self.config_manager.get('logging.log_file')
        self.log_file_path = Path(log_file_str) if log_file_str else None
        if self.log_file_path and self.log_file_path.exists():
            self.log_file_path.unlink()

    def tearDown(self):
        """Tear down after integration tests."""
        if self.log_file_path and self.log_file_path.exists():
            try:
                self.log_file_path.unlink()
            except OSError:
                pass

    @patch('src.core.automation_engine.AutomationEngine._automation_loop')
    def test_end_to_end_flow(self, mock_automation_loop):
        """Test the main end-to-end automation flow."""
        engine = AutomationEngine(self.config_manager)

        async def run_test():
            start_task = asyncio.create_task(engine.start())
            await asyncio.sleep(0.1)
            self.assertTrue(engine.running)
            mock_automation_loop.assert_called()
            await engine.stop()
            self.assertFalse(engine.running)
            await start_task

        try:
            asyncio.run(run_test())
        except RuntimeError:  # Handles already running event loops
            loop = asyncio.get_event_loop()
            loop.run_until_complete(run_test())


class TestPhase4Polish(unittest.TestCase):
    """Tests for project polish, like docs and scripts."""

    def test_requirements_and_dependencies(self):
        """Test requirements and dependencies."""
        req_path = Path(__file__).parent.parent / 'requirements.txt'
        self.assertTrue(
            req_path.exists(), "requirements.txt should exist"
        )
        with open(req_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn(
            'opencv-python', content,
            "Dependency opencv-python should be in requirements.txt"
        )
        self.assertIn(
            'pytesseract', content,
            "Dependency pytesseract should be in requirements.txt"
        )
        self.assertIn(
            'pyautogui', content,
            "Dependency pyautogui should be in requirements.txt"
        )

    def test_final_cleanup_script(self):
        """Test the final cleanup script."""
        (Path.cwd() / 'tmp').mkdir(exist_ok=True)
        (Path.cwd() / 'logs').mkdir(exist_ok=True)
        (Path.cwd() / 'tmp' / 'test.tmp').touch()
        (Path.cwd() / 'logs' / 'test.log').touch()

        script_path = (
            Path(__file__).parent.parent / 'scripts' / 'final_cleanup.sh'
        )
        self.assertTrue(script_path.exists())
        self.assertTrue(script_path.is_file())


if __name__ == '__main__':
    unittest.main()
