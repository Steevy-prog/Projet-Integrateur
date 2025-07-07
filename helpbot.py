import sys
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QThread, pyqtSignal
from pynput import keyboard
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
        self.setWindowTitle("SCA AI help Chatbot")
        self.resize(400, 450)

        # Card frame
        card = QFrame(self)
        card.setStyleSheet("""
            QFrame {
                background-color: #4683B7;
                border-radius: 18px;
                border: 1.5px solid #D3DCE0;
                padding: 18px;
                box-shadow: 0 6px 24px rgba(108,99,255,0.10);
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(18, 18, 18, 18)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background: #fff; border-radius: 8px; padding: 8px;")
        card_layout.addWidget(self.chat_display)

        self.input_line = QLineEdit()
        self.input_line.setStyleSheet("background: #FFFFFF; border-radius: 8px; padding: 8px;")
        card_layout.addWidget(self.input_line)

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #006775;
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #004F5C;
            }
        """)
        card_layout.addWidget(self.send_button)

        # Main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(card)

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

        self.worker_thread = WorkerThread(prompt)
        self.worker_thread.finished.connect(self.handle_response)
        self.worker_thread.start()

    def handle_response(self, answer):
        self.chat_display.undo()
        self.append_message("SAC-Bot", answer)
        self.worker_thread = None


def listen_for_hotkey(app, chatbot):
    def on_press(key):
        try:
            if key == keyboard.Key.space and current_keys.get('alt'):
                if chatbot.isVisible():
                    chatbot.hide()
                else:
                    chatbot.show()
                    chatbot.activateWindow()
                    chatbot.raise_()
        except Exception as e:
            print("Hotkey error:", e)

    def on_release(key):
        if key == keyboard.Key.alt_l:
            current_keys['alt'] = False

    def on_key_down(key):
        if key == keyboard.Key.alt_l:
            current_keys['alt'] = True

    current_keys = {'alt': False}
    with keyboard.Listener(on_press=on_key_down, on_release=on_release) as listener:
        listener2 = keyboard.Listener(on_press=on_press)
        listener2.start()
        listener.join()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chatbot = ChatBot()

    # Start the hotkey listener in a separate thread
    hotkey_thread = threading.Thread(target=listen_for_hotkey, args=(app, chatbot), daemon=True)
    hotkey_thread.start()

    sys.exit(app.exec())