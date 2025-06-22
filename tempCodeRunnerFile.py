import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit
)
from PyQt5.QtCore import Qt


class TerminalWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Terminal Emulator")
        self.resize(800, 500)

        # Layout
        layout = QVBoxLayout(self)

        # Output area (read-only)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        # Input line (like a terminal prompt)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter command and press Enter...")
        self.input.returnPressed.connect(self.run_command)
        layout.addWidget(self.input)

        # Welcome message
        self.output.append("Welcome to the PyQt5 Terminal Emulator!\n")

    def run_command(self):
        command = self.input.text().strip()
        if not command:
            return

        # Show command in output
        self.output.append(f"> {command}")

        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.stdout:
                self.output.append(result.stdout)
            if result.stderr:
                self.output.append(result.stderr)
        except Exception as e:
            self.output.append(f"Error: {str(e)}")

        self.input.clear()
        self.output.moveCursor(self.output.textCursor().End)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    terminal = TerminalWidget()
    terminal.show()
    sys.exit(app.exec_())