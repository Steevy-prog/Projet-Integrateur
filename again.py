import sys
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QLabel, QPushButton,
    QVBoxLayout, QStackedLayout, QFrame, QMessageBox, QWidget, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QPainter, QPixmap, QColor
import psycopg2
import hashlib
from Worker_Dashboard import MainWindow as window1
from Client_Dashboard import MainWindow as window2
from IT_Technician import MainWindow as window3


class BackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg = QPixmap("v.jpg")  # Use your image path

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.bg)

host = "localhost"
port = "5432"
database = "cred"
user = "postgres"
_password = "steevy"

class FlipCard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warehouse Hub - Auth")
        self.setFixedSize(1200, 900)

        # Add a background widget
        self.bg_widget = BackgroundWidget(self)
        self.bg_widget.setGeometry(0, 0, 1200, 900)
        self.bg_widget.lower()  # Make sure it's behind other widgets

        # Center the card in the window
        card_width, card_height = 500, 500  # Increased card size
        x = (self.width() - card_width) // 2
        y = (self.height() - card_height) // 2

        self.container = QFrame(self)
        self.container.setGeometry(x, y, card_width, card_height)
        self.container.setStyleSheet("""
            background-color: rgba(255,255,255,0.7);
            border-radius: 15px;
            border: 1.5px solid rgba(0,0,0,0.08);
        """)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(20)
        shadow.setColor(QColor(0, 0, 0, 120))  # semi-transparent black
        self.container.setGraphicsEffect(shadow)

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
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Email")

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)

        self.login_password.setFixedHeight(40)
        self.login_password.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 15px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #2ecc71;
                background-color: #ffffff;
            }
        """)

        btn_login = QPushButton("Login")
        btn_login.setStyleSheet("rgba(255,255,255,0.2); color: white; font-weight: bold; border-radius: 5px; font-size: 15px;")
        btn_login.setFixedHeight(40)


        self.login_status = QLabel()
        self.login_status.setStyleSheet("color: red;")

        btn_login = QPushButton("Login")
        btn_login.clicked.connect(self.handle_login)

        switch = QPushButton("No account? Sign up")
        switch.setStyleSheet("background: none; color: rgba(200,200,200); font-size: 13px;")
        switch.clicked.connect(self.flip)

        for widget in [self.login_email, self.login_password]:
            widget.setFixedHeight(35)
            widget.setStyleSheet(self.input_style())

        btn_login.setStyleSheet(self.button_style())

        layout.addWidget(title)
        layout.addWidget(self.login_email)
        layout.addWidget(self.login_password)
        layout.addWidget(btn_login)
        layout.addWidget(switch)
        layout.addWidget(self.login_status)

        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        card.setLayout(layout)
        return card

    def create_signup_card(self):
        card = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Sign Up")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.signup_name = QLineEdit()
        self.signup_name.setPlaceholderText("Full Name")

        self.signup_name.setFixedHeight(40)
        self.signup_name.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 15px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #2ecc71;
                background-color: #ffffff;
            }
        """)

        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("Email")
        self.signup_email.setFixedHeight(40)
        self.signup_email.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 15px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #2ecc71;
                background-color: #ffffff;
            }
        """)
        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("Email")


        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("Email")

        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("Password")
        self.signup_password.setEchoMode(QLineEdit.Password)

        self.signup_status = QLabel()
        self.signup_status.setStyleSheet("color: red;")

        btn_signup = QPushButton("Create Account")
        btn_signup.clicked.connect(self.handle_signup)

        switch = QPushButton("Already have an account? Log in")
        switch.setStyleSheet("background: none; color: rgba(200,200,200); font-size: 13px;")
        switch.clicked.connect(self.flip)

        for widget in [self.signup_name, self.signup_email, self.signup_password]:
            widget.setFixedHeight(35)
            widget.setStyleSheet(self.input_style())

        btn_signup.setStyleSheet(self.button_style())

        layout.addWidget(title)
        layout.addWidget(self.signup_name)
        layout.addWidget(self.signup_email)
        layout.addWidget(self.signup_password)
        layout.addWidget(btn_signup)
        layout.addWidget(switch)
        layout.addWidget(self.signup_status)

        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        card.setLayout(layout)
        return card

    def input_style(self):
        return """
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
        """

    def button_style(self):
        return """
        QPushButton {
            background-color: #2ecc71;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            height: 35px;
        }
        QPushButton:hover {
            background-color: #27ae60;
        }
        """

    def flip(self):
        self.setEnabled(False)  # désactiver temporairement les clics
        animation = QPropertyAnimation(self.container, b"geometry")
        animation.setDuration(400)
        animation.setEasingCurve(QEasingCurve.InOutQuad)

        start_rect = self.container.geometry()
        mid_rect = QRect(start_rect.x() + self.container.width() // 2, start_rect.y(), 0, start_rect.height())
        end_rect = start_rect

        animation.setKeyValueAt(0, start_rect)
        animation.setKeyValueAt(0.5, mid_rect)
        animation.setKeyValueAt(1, end_rect)

        animation.finished.connect(self.enable_after_flip)
        animation.start()
        self.animation = animation

    def enable_after_flip(self):
        self.stack.setCurrentIndex(1 if not self.flipped else 0)
        self.flipped = not self.flipped
        self.setEnabled(True)

    def handle_login(self):
        email = self.login_email.text()
        password = self.login_password.text()
        if email == "worker@example.com" and password == "workerpass":
            self.close()  # Close the login window
            self.login_status.setText("Login successful! Redirecting...")
            # Here you would typically redirect to the main application window
            return window1().show()  # Corresponds to Worker_Dashboard (window1) in yo.py
        
        elif email == "client@example.com" and password == "clientpass":
            self.close()  # Close the login window
            self.login_status.setText("Login successful! Redirecting...")
            return window2().show()  # Corresponds to Client_Dashboard (window2) in yo.py
        
        elif email == "it@example.com" and password == "itpass":
            self.close()  # Close the login window
            self.login_status.setText("Login successful! Redirecting...")
            return window3().show()  # Corresponds to IT_Technician (window3) in yo.py
        else:
            self.login_status.setText("Invalid email or password.")
            return

    def handle_signup(self):

        conn = psycopg2.connect(
            host=host,
            user=user,
            password=_password,
            database=database
        )
        cursor = conn.cursor()
        name = self.signup_name.text()
        email = self.signup_email.text()
        if self.signup_password.text() == self.vsignup_password.text():
            password = self.signup_password.text()
            hash_object = hashlib.sha256(password.encode())
            hex_dig = hash_object.hexdigest()
            cursor.execute(""" INSERT INTO cred (email, password) VALUES (%s, %s)""", (email, hex_dig))
            print("stored!!!!!!")

        else:
            print("SIGNUP: Passwords do not match")
        conn.commit()
        conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlipCard()
    window.show()
    sys.exit(app.exec_())
