import sys
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QLabel, QPushButton,
    QVBoxLayout, QStackedLayout, QFrame, QMessageBox, QGraphicsDropShadowEffect, QStackedWidget
)
from PyQt6.QtGui import QFont, QPainter, QPixmap, QColor, QBrush, QLinearGradient
import psycopg2
import hashlib
from yo import interface as dashboard

global conn
print("1. online")
print("2. offline")
it = input("Enter the number of bd you want to use : ")

if it == '1':
    print("You have chosen the online database.")
    conn = psycopg2.connect(
        host="dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com",
        database="projet_integrateur",
        user="group13",
        password="nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3",
        port=5432
    )
elif it == '2':
    print("You have chosen the offline database.")
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="steevy",
        port=5432
    )
cur = conn.cursor()

class BackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg_image = None
        try:
            self.bg_image = QPixmap("A.jpg")
        except:
            self.bg_image = None

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.bg_image and not self.bg_image.isNull():
            scaled_pixmap = self.bg_image.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
        else:
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QColor(74, 144, 226))
            gradient.setColorAt(0.5, QColor(80, 170, 200))
            gradient.setColorAt(1, QColor(46, 204, 113))
            painter.fillRect(self.rect(), QBrush(gradient))
        overlay = QColor(0, 0, 0, 30)
        painter.fillRect(self.rect(), overlay)


host = "localhost"
port = "5432"
database = "cred"
user = "postgres"
_password = "steevy"


class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.login = FlipCard(self)
        self.worker = dashboard.create_interface(1)
        self.client = dashboard.create_interface(2)
        self.it = dashboard.create_interface(3)
        self.manager = dashboard.create_interface(4)

        self.addWidget(self.login)
        self.addWidget(self.worker)
        self.addWidget(self.client)
        self.addWidget(self.it)
        self.addWidget(self.manager)

        self.setCurrentIndex(0)

    def show_dashboard(self, role):
        if role == "worker":
            self.setCurrentWidget(self.worker)
        elif role == "client":
            self.setCurrentWidget(self.client)
        elif role == "it":
            self.setCurrentWidget(self.it)
        elif role == "manager":
            self.setCurrentWidget(self.manager)

class FlipCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Warehouse Hub - Authentication")
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setMinimumSize(800, 600)
        self.bg_widget = BackgroundWidget(self)
        self.card_width = 450
        self.card_height = 550
        self.container = QFrame(self)
        self.setup_card_style()
        self.stack = QStackedLayout()
        self.front = self.create_login_card()
        self.back = self.create_signup_card()
        self.stack.addWidget(self.front)
        self.stack.addWidget(self.back)
        layout = QVBoxLayout(self.container)
        layout.addLayout(self.stack)
        layout.setContentsMargins(0, 0, 0, 0)
        self.flipped = False
        self.position_card()
        self.resizeEvent = self.on_resize

    def setup_card_style(self):
        self.container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setXOffset(0)
        shadow.setYOffset(25)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.container.setGraphicsEffect(shadow)

    def position_card(self):
        window_width = self.width()
        window_height = self.height()
        x = (window_width - self.card_width) // 2
        y = (window_height - self.card_height) // 2
        x = max(50, x)
        y = max(50, y)
        self.container.setGeometry(x, y, self.card_width, self.card_height)

    def on_resize(self, event):
        self.bg_widget.setGeometry(0, 0, self.width(), self.height())
        self.position_card()
        super().resizeEvent(event)

    def create_login_card(self):
        card = QWidget()
        layout = QVBoxLayout()
        title = QLabel("Welcome Back")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                margin-bottom: 10px;
                margin-top: 20px;
            }
        """)
        subtitle = QLabel("Sign in to your account")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 30px;")
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Email Address")
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        btn_login = QPushButton("Sign In")
        btn_login.clicked.connect(self.handle_login)
        self.login_status = QLabel()
        self.login_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.login_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        switch = QPushButton("Don't have an account? Create one")
        switch.clicked.connect(self.flip)
        for widget in [self.login_email, self.login_password]:
            widget.setFixedHeight(45)
            widget.setStyleSheet(self.input_style())
        btn_login.setStyleSheet(self.primary_button_style())
        btn_login.setFixedHeight(45)
        switch.setStyleSheet(self.link_button_style())
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.login_email)
        layout.addWidget(self.login_password)
        layout.addWidget(btn_login)
        layout.addWidget(self.login_status)
        layout.addWidget(switch)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 10, 30, 10)
        card.setLayout(layout)
        return card

    def create_signup_card(self):
        card = QWidget()
        layout = QVBoxLayout()
        
        subtitle = QLabel("Join us today")
        subtitle.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        self.signup_name = QLineEdit()
        self.signup_name.setPlaceholderText("Full Name")
        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("Email Address")
        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("Password")
        self.signup_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_password_confirm = QLineEdit()
        self.signup_password_confirm.setPlaceholderText("Confirm your password")
        self.signup_password_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.id_entreprise = QLineEdit()
        self.id_entreprise.setPlaceholderText("ID Organisation")
        self.id_entreprise.setEchoMode(QLineEdit.EchoMode.Password)
        self.id_poste = QLineEdit()
        self.id_poste.setPlaceholderText("ID Poste")
        self.id_poste.setEchoMode(QLineEdit.EchoMode.Password)
        


        btn_signup = QPushButton("Create Account")
        btn_signup.clicked.connect(self.handle_signup)
        self.signup_status = QLabel()
        self.signup_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.signup_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        switch = QPushButton("Already have an account? Sign in")
        switch.clicked.connect(self.flip)
        for widget in [self.signup_name, self.signup_email, self.signup_password, self.signup_password_confirm, self.id_entreprise, self.id_poste ]:
            widget.setFixedHeight(45)
            widget.setStyleSheet(self.input_style())
        btn_signup.setStyleSheet(self.primary_button_style())
        btn_signup.setFixedHeight(45)
        switch.setStyleSheet(self.link_button_style())
        layout.addWidget(subtitle)
        layout.addWidget(self.signup_name)
        layout.addWidget(self.signup_email)
        layout.addWidget(self.signup_password)
        layout.addWidget(self.signup_password_confirm)
        layout.addWidget(self.id_entreprise)
        layout.addWidget(self.id_poste)
        layout.addWidget(btn_signup)
        layout.addWidget(self.signup_status)
        layout.addWidget(switch)
        layout.setSpacing(15)
        layout.setContentsMargins(50, 30, 50, 30)
        card.setLayout(layout)
        return card

    def input_style(self):
        return """
        QLineEdit {
            background-color: #ffffff;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding-left: 15px;
            padding-right: 15px;
            font-size: 14px;
            color: #2c3e50;
        }
        QLineEdit:focus {
            border: 2px solid #3498db;
            background-color: #ffffff;
        }
        QLineEdit::placeholder {
            color: #bdc3c7;
        }
        """

    def primary_button_style(self):
        return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #3498db, stop:1 #2980b9);
            color: white;
            font-weight: bold;
            font-size: 16px;
            border: none;
            border-radius: 10px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #5dade2, stop:1 #3498db);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #2980b9, stop:1 #21618c);
        }
        """

    def link_button_style(self):
        return """
        QPushButton {
            background: transparent;
            color: #3498db;
            font-size: 13px;
            border: none;
            text-decoration: underline;
            padding: 10px;
        }
        QPushButton:hover {
            color: #2980b9;
        }
        """

    def flip(self):
        self.setEnabled(False)
        animation = QPropertyAnimation(self.container, b"geometry")
        animation.setDuration(500)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        start_rect = self.container.geometry()
        mid_rect = QRect(
            start_rect.x() + self.container.width() // 2,
            start_rect.y(),
            0,
            start_rect.height()
        )
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
        email = self.login_email.text().strip()
        password = self.login_password.text()
        if not email or not password:
            self.login_status.setText("Please fill in all fields.")
            return
        cur.execute('SELECT "EMIR".connexion_travailleur(%s,%s)',email,password)
        poste = cur.fetchone()[0]
        if poste:
            if poste == 'Administrateur':
            elif poste == 'Manager':
            elif poste == 'Logisticien':
            elif poste == 'Magasinier':
            elif poste == 'Securite':
            
            self.login_status.setText("Login successful! Redirecting...")
            self.login_status.setStyleSheet("color: #27ae60; font-weight: bold;")
            QTimer.singleShot(1000, lambda: self.open_dashboard(credentials[email][1]))
        else:
            self.login_status.setText("Invalid email or password.")
            self.login_status.setStyleSheet("color: #e74c3c; font-weight: bold;")

    def open_dashboard(self, role):
            role.show_dashboard()

    def handle_signup(self):
        name = self.signup_name.text().strip()
        email = self.signup_email.text().strip()
        password = self.signup_password.text()
        if not all([name, email, password]):
            self.signup_status.setText("Please fill in all fields.")
            return
        if len(password) < 6:
            self.signup_status.setText("Password must be at least 6 characters.")
            return
        try:
            conn = psycopg2.connect(
                host=host,
                user=user,
                password=_password,
                database=database
            )
            cursor = conn.cursor()
            hash_object = hashlib.sha256(password.encode())
            hex_dig = hash_object.hexdigest()
            cursor.execute(
                "INSERT INTO cred (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hex_dig)
            )
            conn.commit()
            conn.close()
            self.signup_status.setText("Account created successfully!")
            self.signup_status.setStyleSheet("color: #27ae60; font-weight: bold;")
            QTimer.singleShot(2000, self.flip)
        except psycopg2.IntegrityError:
            self.signup_status.setText("Email already exists.")
        except Exception as e:
            self.signup_status.setText(f"Error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main_app = MainApp()
    main_app.showMaximized()
    sys.exit(app.exec())