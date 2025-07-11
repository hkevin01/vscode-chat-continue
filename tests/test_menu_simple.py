#!/usr/bin/env python3
"""
Minimal GUI test to verify menu functionality.
"""

import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

class TestMainWindow(QMainWindow):
    """Minimal test window to verify menu functionality."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_menu_bar()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Menu Test - VS Code Chat Continue Automation")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Test label
        label = QLabel("Menu Test Window")
        layout.addWidget(label)
        
        # Test button
        test_btn = QPushButton("Test Button - Click Me!")
        test_btn.clicked.connect(self.test_button_clicked)
        layout.addWidget(test_btn)
    
    def setup_menu_bar(self):
        """Setup the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        # Test action
        test_action = file_menu.addAction('&Test Action')
        test_action.triggered.connect(self.test_menu_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = file_menu.addAction('E&xit')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        # Refresh action
        refresh_action = view_menu.addAction('&Refresh')
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.test_refresh)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        # About action
        about_action = help_menu.addAction('&About')
        about_action.triggered.connect(self.show_about)
    
    def test_menu_action(self):
        """Test menu action."""
        QMessageBox.information(self, "Test", "File menu action works!")
    
    def test_button_clicked(self):
        """Test button action."""
        QMessageBox.information(self, "Test", "Button click works!")
    
    def test_refresh(self):
        """Test refresh action."""
        QMessageBox.information(self, "Test", "View menu refresh action works!")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About", 
            "Menu Test Application\n\n"
            "Testing menu functionality for\n"
            "VS Code Chat Continue Automation")

def main():
    """Main entry point for test GUI application."""
    # Set DISPLAY environment variable
    os.environ['DISPLAY'] = ':0'
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Menu Test")
    
    # Create and show main window
    window = TestMainWindow()
    window.show()
    
    print("Test window created and shown")
    print("Testing menu functionality...")
    print("If you can see the window with File, View, and Help menus, the menus are working!")
    
    # Run application
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
