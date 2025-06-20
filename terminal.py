import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit
)
from PyQt5.QtCore import Qt


class CustomTerminal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Custom Terminal")
        self.resize(800, 500)

        layout = QVBoxLayout(self)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type your command...")
        self.input.returnPressed.connect(self.handle_input)
        layout.addWidget(self.input)

        self.append_output("<<<Welcome to your steevy terminal!>>>\n", bold=True)

    def append_output(self, text, bold=False, error=False):
        color = "red" if error else "green"
        weight = "bold" if bold else "normal"
        formatted = f'<span style="color:{color}; font-weight:{weight}; white-space:pre-wrap;">{text}</span>'
        self.output.append(formatted)

    def handle_input(self):
        command = self.input.text().strip()
        if not command:
            return

        self.append_output(f"> {command}", bold=True)

        # 🧠 Custom evaluation logic
        try:
            result = self.evaluate_command(command)
            self.append_output(result)
        except Exception as e:
            self.append_output(f"Error: {str(e)}", error=True)

        self.input.clear()
        self.output.moveCursor(self.output.textCursor().End)

    def evaluate_command(self, command: str) -> str:
        """
        🔧 This is where you implement your own interpreter.
        Replace this logic with your own system.
        """
        # 🔸 Example: simple math evaluation
        if command.startswith("print "):
            expr = command[6:]
            return str(eval(expr))  # ⚠️ Don't use eval() in real interpreters — just a placeholder
        elif command == "hello":
            return "Hi there! :)"
        else:
            return f"Unknown command: {command}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    term = CustomTerminal()
    term.show()
    sys.exit(app.exec_())