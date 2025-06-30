import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtCore import QThread, pyqtSignal
import google.generativeai as genai

API_KEY = "AIzaSyACCuz2G5YDYs7rmVl9X7Q_Z60Qa1TOq_8"
genai.configure(api_key=API_KEY)

MODEL_NAME = "models/gemini-2.5-pro"
model = genai.GenerativeModel(MODEL_NAME)

HELP_TEXT = """
To reset your password, click 'Forgot Password' on the login screen.
You’ll receive an email with a link to create a new one.
If you don’t receive it, check your spam folder or contact support.
"""

class WorkerThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            response = model.generate_content(self.prompt)
            answer = response.text.strip()
        except Exception as e:
            answer = f"Error: {e}"
        self.finished.emit(answer)


class ChatBot(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gemini Help Chatbot")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.input_line = QLineEdit()
        layout.addWidget(self.input_line)

        self.send_button = QPushButton("Send")
        layout.addWidget(self.send_button)

        self.send_button.clicked.connect(self.on_send)
        self.input_line.returnPressed.connect(self.on_send)

        self.append_message("System", "Welcome! Ask me anything about your app.")

        self.worker_thread = None

    def append_message(self, sender, message):
        self.chat_display.append(f"<b>{sender}:</b> {message}")

    def on_send(self):
        question = self.input_line.text().strip()
        if not question:
            return

        self.append_message("You", question)
        self.input_line.clear()

        # Show loader
        self.append_message("Bot", "<i>Thinking...</i>")

        prompt = f"""
You are a helpful and kind assistant. Use the following help guide to answer the user's question. If he asks about something not in the help guide, say you don't know.
If he greets you or shows any sign of politeness, respond in a friendly manner.

HELP DOCUMENT:
{HELP_TEXT}

QUESTION:
{question}

Answer only based on the HELP DOCUMENT above.
"""

        # Run model call in a background thread
        self.worker_thread = WorkerThread(prompt)
        self.worker_thread.finished.connect(self.handle_response)
        self.worker_thread.start()

    def handle_response(self, answer):
        # Remove the "Thinking..." message (undo last append)
        self.chat_display.undo()
        self.append_message("SAC-Bot", answer)
        self.worker_thread = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chatbot = ChatBot()
    chatbot.show()
    sys.exit(app.exec())