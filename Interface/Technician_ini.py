import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer # Import QTimer for a slight delay if needed
from PyQt6.QtGui import QPalette, QColor, QFont

from Technician_Login import LoginWindow
from IT_Technician import MainWindow

class ApplicationManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = LoginWindow()
        self.main_window = None # Initialize main_window to None

        # Connect the login_successful signal from LoginWindow to a slot in ApplicationManager
        self.login_window.login_successful.connect(self.show_main_window)

    def run(self):
        self.login_window.show() # Start by showing the login window
        sys.exit(self.app.exec())

    def show_main_window(self):
        # This slot is called when login is successful
        if self.main_window is None: # Create main window only once
            self.main_window = MainWindow()
        
        # The login window is already closed by `self.close()` in `check_login`
        self.main_window.show() # Show the main application window

if __name__ == '__main__':
    manager = ApplicationManager()
    app = QApplication(sys.argv)
    font = QFont("Arial", 10)
    app.setFont(font)
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))  # Dialog background
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#232946"))  # Dialog text
    palette.setColor(QPalette.ColorRole.Base, QColor("#F8F9FA"))  # Input fields
    palette.setColor(QPalette.ColorRole.Text, QColor("#232946"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#6C63FF"))  # Accent for buttons
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#6C63FF"))  # Selection color
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#EB7A16FF"))
    app.setPalette(palette)
    manager.run()