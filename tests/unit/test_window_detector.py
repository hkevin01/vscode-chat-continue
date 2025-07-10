"""Unit tests for WindowDetector module."""

import sys
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.window_detector import VSCodeWindow, WindowDetector


class TestWindowDetector(unittest.TestCase):
    """Test cases for WindowDetector class."""
    
    def setUp(self):
        """Set up test environment."""
        self.window_detector = WindowDetector()
        
    def test_window_detector_initialization(self):
        """Test WindowDetector initialization."""
        self.assertIsNotNone(self.window_detector)
        
    def test_vscode_window_dataclass(self):
        """Test VSCodeWindow dataclass."""
        window = VSCodeWindow(
            id=123,
            title="Visual Studio Code",
            pid=456,
            x=100, y=200, width=800, height=600
        )
        
        self.assertEqual(window.id, 123)
        self.assertEqual(window.title, "Visual Studio Code")
        self.assertEqual(window.pid, 456)
        self.assertEqual(window.x, 100)
        self.assertEqual(window.y, 200)
        self.assertEqual(window.width, 800)
        self.assertEqual(window.height, 600)
        
    @patch('psutil.process_iter')
    def test_find_vscode_processes(self, mock_process_iter):
        """Test finding VS Code processes."""
        # Mock process objects
        mock_vscode_process = Mock()
        mock_vscode_process.info = {'name': 'code', 'pid': 12345}
        
        mock_other_process = Mock()
        mock_other_process.info = {'name': 'firefox', 'pid': 67890}
        
        mock_electron_process = Mock()
        mock_electron_process.info = {'name': 'electron', 'pid': 11111}
        
        mock_process_iter.return_value = [
            mock_vscode_process, mock_other_process, mock_electron_process
        ]
        
        processes = self.window_detector.find_vscode_processes()
        
        # Should find VS Code processes
        self.assertGreater(len(processes), 0)
        vscode_process = next(
            (p for p in processes if p['name'] == 'code'), None
        )
        self.assertIsNotNone(vscode_process)
        self.assertEqual(vscode_process['pid'], 12345)
        
    @patch('subprocess.run')
    def test_get_x11_window_info_success(self, mock_run):
        """Test getting X11 window info successfully."""
        # Mock xwininfo output
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '''
        xwininfo: Window id: 0x123 "Visual Studio Code"
        
          Absolute upper-left X:  100
          Absolute upper-left Y:  200
          Width: 800
          Height: 600
        '''
        mock_run.return_value = mock_result
        
        window_info = self.window_detector._get_x11_window_info(0x123)
        
        self.assertIsNotNone(window_info)
        self.assertEqual(window_info['id'], 0x123)
        self.assertEqual(window_info['title'], "Visual Studio Code")
        self.assertEqual(window_info['x'], 100)
        self.assertEqual(window_info['y'], 200)
        self.assertEqual(window_info['width'], 800)
        self.assertEqual(window_info['height'], 600)
        
    @patch('subprocess.run')
    def test_get_x11_window_info_failure(self, mock_run):
        """Test getting X11 window info with failure."""
        # Mock xwininfo failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        window_info = self.window_detector._get_x11_window_info(0x123)
        
        self.assertIsNone(window_info)
        
    @patch('subprocess.run')
    def test_find_windows_by_process_success(self, mock_run):
        """Test finding windows by process ID successfully."""
        # Mock xdotool output
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "0x1000001\n0x1000002\n"
        mock_run.return_value = mock_result
        
        with patch.object(
            self.window_detector, '_get_x11_window_info'
        ) as mock_get_info:
            mock_get_info.side_effect = [
                {
                    'id': 0x1000001,
                    'title': 'Visual Studio Code - File1',
                    'x': 100, 'y': 200, 'width': 800, 'height': 600
                },
                {
                    'id': 0x1000002,
                    'title': 'Visual Studio Code - File2',
                    'x': 900, 'y': 200, 'width': 800, 'height': 600
                }
            ]
            
            windows = self.window_detector._find_windows_by_process(12345)
            
            self.assertEqual(len(windows), 2)
            self.assertEqual(windows[0]['id'], 0x1000001)
            self.assertEqual(windows[1]['id'], 0x1000002)
            
    @patch('subprocess.run')
    def test_find_windows_by_process_failure(self, mock_run):
        """Test finding windows by process ID with failure."""
        # Mock xdotool failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        windows = self.window_detector._find_windows_by_process(12345)
        
        self.assertEqual(len(windows), 0)
        
    def test_filter_vscode_windows(self):
        """Test filtering windows to only VS Code windows."""
        windows = [
            {
                'id': 1,
                'title': 'Visual Studio Code - main.py',
                'x': 100, 'y': 200, 'width': 800, 'height': 600
            },
            {
                'id': 2,
                'title': 'Firefox - Google',
                'x': 900, 'y': 200, 'width': 800, 'height': 600
            },
            {
                'id': 3,
                'title': 'Code - settings.json',
                'x': 0, 'y': 0, 'width': 1200, 'height': 800
            }
        ]
        
        filtered = self.window_detector._filter_vscode_windows(windows)
        
        self.assertEqual(len(filtered), 2)
        titles = [w['title'] for w in filtered]
        self.assertIn('Visual Studio Code - main.py', titles)
        self.assertIn('Code - settings.json', titles)
        
    def test_convert_to_vscode_window(self):
        """Test converting window dict to VSCodeWindow object."""
        window_dict = {
            'id': 123,
            'title': 'Visual Studio Code - main.py',
            'pid': 456,
            'x': 100, 'y': 200, 'width': 800, 'height': 600
        }
        
        vscode_window = self.window_detector._convert_to_vscode_window(
            window_dict
        )
        
        self.assertIsInstance(vscode_window, VSCodeWindow)
        self.assertEqual(vscode_window.id, 123)
        self.assertEqual(vscode_window.title, 'Visual Studio Code - main.py')
        self.assertEqual(vscode_window.pid, 456)
        self.assertEqual(vscode_window.x, 100)
        self.assertEqual(vscode_window.y, 200)
        self.assertEqual(vscode_window.width, 800)
        self.assertEqual(vscode_window.height, 600)
        
    @patch.object(WindowDetector, 'find_vscode_processes')
    @patch.object(WindowDetector, '_find_windows_by_process')
    @patch.object(WindowDetector, '_filter_vscode_windows')
    def test_get_vscode_windows_integration(
        self, mock_filter, mock_find_windows, mock_find_processes
    ):
        """Test the main get_vscode_windows method integration."""
        # Mock the process finding
        mock_find_processes.return_value = [
            {'name': 'code', 'pid': 12345}
        ]
        
        # Mock window finding
        mock_find_windows.return_value = [
            {
                'id': 123,
                'title': 'Visual Studio Code - main.py',
                'pid': 12345,
                'x': 100, 'y': 200, 'width': 800, 'height': 600
            }
        ]
        
        # Mock filtering (pass through)
        mock_filter.side_effect = lambda x: x
        
        windows = self.window_detector.get_vscode_windows()
        
        self.assertEqual(len(windows), 1)
        self.assertIsInstance(windows[0], VSCodeWindow)
        self.assertEqual(windows[0].title, 'Visual Studio Code - main.py')
        
    def test_window_validation(self):
        """Test window validation for reasonable coordinates."""
        # Valid window
        valid_window = {
            'id': 123,
            'title': 'Visual Studio Code',
            'pid': 456,
            'x': 100, 'y': 200, 'width': 800, 'height': 600
        }
        
        self.assertTrue(
            self.window_detector._is_valid_window(valid_window)
        )
        
        # Invalid windows (negative coordinates, zero size)
        invalid_windows = [
            {'x': -100, 'y': 200, 'width': 800, 'height': 600},
            {'x': 100, 'y': -200, 'width': 800, 'height': 600},
            {'x': 100, 'y': 200, 'width': 0, 'height': 600},
            {'x': 100, 'y': 200, 'width': 800, 'height': 0}
        ]
        
        for window in invalid_windows:
            window.update({
                'id': 123, 'title': 'Test', 'pid': 456
            })
            self.assertFalse(
                self.window_detector._is_valid_window(window)
            )


if __name__ == '__main__':
    unittest.main()
