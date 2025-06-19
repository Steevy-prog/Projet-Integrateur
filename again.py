import sys
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QLabel, QPushButton,
    QVBoxLayout, QStackedLayout, QFrame
)
from PyQt5.QtGui import QFont

class FlipCard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warehouse Hub - Auth")
        self.setFixedSize(400, 400)
        self.setStyleSheet("background-color: #f0f2f5;")

        self.container = QFrame(self)
        self.container.setGeometry(50, 30, 300, 330)
        self.container.setStyleSheet("background-color: white; border-radius: 15px;")

        self.stack = QStackedLayout()
        self.front = self.create_login_card()
        self.back = self.create_signup_card()
        self.stack.addWidget(self.front)
        self.stack.addWidget(self.back)

        layout = QVBoxLayout(self.container)
        layout.addLayout(self.stack)

        self.flipped = False

    def create_login_card(self):
        card = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Login")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: black;
            }
        """)

        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Email")
        self.login_email.setFixedHeight(35)
        self.login_email.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 13px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #2ecc71;
                background-color: #ffffff;
            }
        """)

        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Email")
        self.login_email.setFixedHeight(35)
        self.login_email.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 13px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #2ecc71;
                background-color: #ffffff;
            }
        """)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setFixedHeight(35)
        self.login_password.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 13px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #2ecc71;
                background-color: #ffffff;
            }
        """)

        btn_login = QPushButton("Login")
        btn_login.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; border-radius: 5px;")
        btn_login.setFixedHeight(35)
        btn_login.clicked.connect(self.handle_login)

        switch = QPushButton("No account? Sign up")
        switch.setStyleSheet("background: none; color: #3498db;")
        switch.clicked.connect(self.flip)

        layout.addWidget(title)
        layout.addWidget(self.login_email)
        layout.addWidget(self.login_password)
        layout.addWidget(btn_login)
        layout.addWidget(switch)

        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        card.setLayout(layout)
        return card

    def create_signup_card(self):
        card = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Sign Up")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #2ecc71;
                background-color: #ffffff;
            }
        """)

        self.signup_name = QLineEdit()
        self.signup_name.setPlaceholderText("Full Name")
        self.signup_name.setFixedHeight(35)
        self.signup_name.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 13px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #2ecc71;
                background-color: #ffffff;
            }
        """)

        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("Email")
        self.signup_email.setFixedHeight(35)
        self.signup_email.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 13px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #2ecc71;
                background-color: #ffffff;
            }
        """)

        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("Password")
        self.signup_password.setEchoMode(QLineEdit.Password)
        self.signup_password.setFixedHeight(35)
        self.signup_password.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 13px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #2ecc71;
                background-color: #ffffff;
            }
        """)

        btn_signup = QPushButton("Create Account")
        btn_signup.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; border-radius: 5px;")
        btn_signup.setFixedHeight(35)
        btn_signup.clicked.connect(self.handle_signup)

        switch = QPushButton("Already have an account? Log in")
        switch.setStyleSheet("background: none; color: #3498db;")
        switch.clicked.connect(self.flip)

        layout.addWidget(title)
        layout.addWidget(self.signup_name)
        layout.addWidget(self.signup_email)
        layout.addWidget(self.signup_password)
        layout.addWidget(btn_signup)
        layout.addWidget(switch)

        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        card.setLayout(layout)
        return card

    def flip(self):
        self.animation = QPropertyAnimation(self.container, b"geometry")
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        start_rect = self.container.geometry()
        mid_rect = QRect(start_rect.x() + 150, start_rect.y(), 0, start_rect.height())
        end_rect = start_rect

        self.animation.setKeyValueAt(0, start_rect)
        self.animation.setKeyValueAt(0.5, mid_rect)
        self.animation.setKeyValueAt(1, end_rect)

        self.animation.finished.connect(self.toggle_card)
        self.animation.start()

    def toggle_card(self):
        self.stack.setCurrentIndex(1 if not self.flipped else 0)
        self.flipped = not self.flipped

    def handle_login(self):
        email = self.login_email.text()
        password = self.login_password.text()
        print(f"LOGIN: Email={email}, Password={password}")

    def handle_signup(self):
        name = self.signup_name.text()
        email = self.signup_email.text()
        password = self.signup_password.text()
        print(f"SIGNUP: Name={name}, Email={email}, Password={password}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlipCard()
    window.show()
    sys.exit(app.exec_())