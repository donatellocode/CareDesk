"""Clinic Management System - Main Entry Point."""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow


class ClinicApp(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CareDesk - Clinic Management System")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
        
        # Setup UI
        self.main_window = MainWindow()
        self.main_window.setup(self)
        
        # Center on screen
        self.center_on_screen()

    def center_on_screen(self):
        """Center the window on screen."""
        screen = self.screen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create and show main window
    window = ClinicApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()