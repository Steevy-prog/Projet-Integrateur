

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
This interface define the limit of oprations that the IT technician can perform
It principally consist of 5 pages for strong management.

From the Account Setting page the IT technician can perform the following;
- Create users accounts from individuals
- View the different individuals in the system
- View the different users in the system
- Perform account Deletion to remove a user.
- Edit the user information such as email an username.

From the Database Maintenace page the IT technician can perform the following any tasks
that relates to databse interaction;
From basic select queries to complex queries that involve multiple tables.
 
From the Security Settings page the IT technician can define security policies presently for just the password policy. thus enforcing the following;
- Password minimum length
- Presence of special characters
- Presence of numbers
- Presence of uppercase and lowercase characters
- Password expiration time

From the Terminal page, the IT technician have access to a built-in terminal that allows them to run
any command that is available on the system. This is useful for running scripts, checking system status via logs, and performing other administrative tasks.
The terminal is a powerful tool that can be used to manage the system effectively.
Despite the fact that it includes commands for generating logs report, the IT technician can also lunch the database backup service.

From the Automation page, the IT technician can set up automated tasks that can be run at specific intervals or triggered by specific events.
This allows the IT technician to automate repetitive tasks and ensure that the system is always up-to-date and running smoothly.
The automation page is a powerful tool that can be used to manage the system effectively.
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
                border: 1.5px solid #E0E0E0;
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
                background-color: #6C63FF;
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #5247D6;
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