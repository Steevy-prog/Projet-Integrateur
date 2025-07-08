import sys
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QLabel, QPushButton,
    QVBoxLayout, QStackedLayout, QFrame, QMessageBox, QGraphicsDropShadowEffect, QStackedWidget
)
from PyQt6.QtGui import QFont, QPainter, QPixmap, QColor, QBrush, QLinearGradient
import psycopg2
import hashlib


class BackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg_image = None
        try:
            self.bg_image = QPixmap("Interface\Cllient.jpg")  # Client-themed background
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
            # Client-themed gradient: warm colors (orange to purple)
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QColor(255, 152, 0))  # Orange
            gradient.setColorAt(0.5, QColor(233, 30, 99))  # Pink
            gradient.setColorAt(1, QColor(156, 39, 176))  # Purple
            painter.fillRect(self.rect(), QBrush(gradient))
        overlay = QColor(0, 0, 0, 25)  # Light overlay for readability
        painter.fillRect(self.rect(), overlay)


# Database configuration
host = "localhost"
port = "5432"
database = "client_db"
user = "postgres"
_password = "client_password"


class ClientApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.login = ClientFlipCard(self)
        # Add dashboard widget here when available
        # self.dashboard = ClientDashboard(self)
        
        self.addWidget(self.login)
        # self.addWidget(self.dashboard)
        
        self.setCurrentIndex(0)

    def show_dashboard(self):
        # Implement dashboard switching logic
        print("Redirecting to Client Dashboard...")
        # self.setCurrentWidget(self.dashboard)


class ClientFlipCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Client Portal - Welcome")
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setMinimumSize(850, 650)
        
        self.bg_widget = BackgroundWidget(self)
        self.card_width = 420
        self.card_height = 580
        
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
                background-color: rgba(255, 255, 255, 0.98);
                border-radius: 25px;
                border: 2px solid rgba(255, 152, 0, 0.2);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(45)
        shadow.setXOffset(0)
        shadow.setYOffset(20)
        shadow.setColor(QColor(156, 39, 176, 100))
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
        
        # Title with client theme
        title = QLabel("Client Portal")
        title.setFont(QFont("Roboto", 28, QFont.Weight.Bold))  # Placeholder for font
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #e91e63;
                margin-bottom: 10px;
                margin-top: 30px;
            }
        """)
        
        subtitle = QLabel("Welcome to your dashboard")
        subtitle.setFont(QFont("Roboto", 14))  # Placeholder for font
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #424242; margin-bottom: 40px; font-weight: 400;")
        
        # Input fields
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Email Address")
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.login_company_code = QLineEdit()
        self.login_company_code.setPlaceholderText("Company Code")
        
        # Login button
        btn_login = QPushButton("Sign In")
        btn_login.clicked.connect(self.handle_login)
        
        # Status label
        self.login_status = QLabel()
        self.login_status.setStyleSheet("color: #f44336; font-weight: bold;")
        self.login_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Switch to signup
        switch = QPushButton("New client? Create account")
        switch.clicked.connect(self.flip)
        
        # Apply styles
        for widget in [self.login_email, self.login_password, self.login_company_code]:
            widget.setFixedHeight(48)
            widget.setStyleSheet(self.input_style())
        
        btn_login.setStyleSheet(self.primary_button_style())
        btn_login.setFixedHeight(48)
        switch.setStyleSheet(self.link_button_style())
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.login_email)
        layout.addWidget(self.login_password)
        layout.addWidget(self.login_company_code)
        layout.addWidget(btn_login)
        layout.addWidget(self.login_status)
        layout.addWidget(switch)
        
        layout.setSpacing(15)
        layout.setContentsMargins(40, 20, 40, 20)
        card.setLayout(layout)
        return card

    def create_signup_card(self):
        card = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("✨ Join Our Platform")
        title.setFont(QFont("Roboto", 24, QFont.Weight.Bold))  # Placeholder for font
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #e91e63;
                margin-bottom: 8px;
                margin-top: 25px;
            }
        """)
        
        subtitle = QLabel("Start your journey with us")
        subtitle.setFont(QFont("Roboto", 12))  # Placeholder for font
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #424242; margin-bottom: 25px;")
        
        # Input fields
        self.signup_company_name = QLineEdit()
        self.signup_company_name.setPlaceholderText(" Company Name")
        
        self.signup_contact_person = QLineEdit()
        self.signup_contact_person.setPlaceholderText(" Contact Person")
        
        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText(" Business Email")
        
        self.signup_phone = QLineEdit()
        self.signup_phone.setPlaceholderText(" Phone Number")
        
        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText(" Create Password")
        self.signup_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.signup_confirm_password = QLineEdit()
        self.signup_confirm_password.setPlaceholderText(" Confirm Password")
        self.signup_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.signup_industry = QLineEdit()
        self.signup_industry.setPlaceholderText(" Industry/Sector")
        
        # Signup button
        btn_signup = QPushButton(" Create Account")
        btn_signup.clicked.connect(self.handle_signup)
        
        # Status label
        self.signup_status = QLabel()
        self.signup_status.setStyleSheet("color: #f44336; font-weight: bold;")
        self.signup_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Switch back to login
        switch = QPushButton("Already have an account? Sign in")
        switch.clicked.connect(self.flip)
        
        # Apply styles
        for widget in [self.signup_company_name, self.signup_contact_person, self.signup_email, 
                      self.signup_phone, self.signup_password, self.signup_confirm_password,
                      self.signup_industry]:
            widget.setFixedHeight(42)
            widget.setStyleSheet(self.input_style())
        
        btn_signup.setStyleSheet(self.primary_button_style())
        btn_signup.setFixedHeight(42)
        switch.setStyleSheet(self.link_button_style())
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.signup_company_name)
        layout.addWidget(self.signup_contact_person)
        layout.addWidget(self.signup_email)
        layout.addWidget(self.signup_phone)
        layout.addWidget(self.signup_password)
        layout.addWidget(self.signup_confirm_password)
        layout.addWidget(self.signup_industry)
        layout.addWidget(btn_signup)
        layout.addWidget(self.signup_status)
        layout.addWidget(switch)
        
        layout.setSpacing(8)
        layout.setContentsMargins(40, 15, 40, 15)
        card.setLayout(layout)
        return card

    def input_style(self):
        return """
        QLineEdit {
            background-color: #ffffff;
            border: 2px solid #fce4ec;
            border-radius: 15px;
            padding-left: 15px;
            padding-right: 15px;
            font-size: 14px;
            color: #e91e63;
            font-family: "Roboto", Arial, sans-serif;
        }
        QLineEdit:focus {
            border: 2px solid #e91e63;
            background-color: #fef7ff;
        }
        QLineEdit::placeholder {
            color: #9c27b0;
        }
        """

    def primary_button_style(self):
        return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #ff9800, stop:1 #e91e63);
            color: white;
            font-weight: bold;
            font-size: 16px;
            border: none;
            border-radius: 15px;
            font-family: "Roboto", Arial, sans-serif;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #ffb74d, stop:1 #f06292);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #f57c00, stop:1 #c2185b);
        }
        """

    def link_button_style(self):
        return """
        QPushButton {
            background: transparent;
            color: #e91e63;
            font-size: 13px;
            border: none;
            text-decoration: underline;
            padding: 10px;
            font-family: "Roboto", Arial, sans-serif;
        }
        QPushButton:hover {
            color: #c2185b;
        }
        """

    def flip(self):
        self.setEnabled(False)
        animation = QPropertyAnimation(self.container, b"geometry")
        animation.setDuration(550)
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
        company_code = self.login_company_code.text().strip()
        
        if not email or not password or not company_code:
            self.login_status.setText("Please fill in all fields.")
            return
        
        # Demo credentials for Client
        if email == "client@company.com" and password == "client123" and company_code == "COMP001":
            self.login_status.setText("Welcome! Loading your dashboard...")
            self.login_status.setStyleSheet("color: #4caf50; font-weight: bold;")
            QTimer.singleShot(1500, self.open_dashboard)
        else:
            self.login_status.setText("Invalid credentials or company code.")
            self.login_status.setStyleSheet("color: #f44336; font-weight: bold;")

    def open_dashboard(self):
        parent = self.parent()
        if hasattr(parent, "show_dashboard"):
            parent.show_dashboard()

    def handle_signup(self):
        company_name = self.signup_company_name.text().strip()
        contact_person = self.signup_contact_person.text().strip()
        email = self.signup_email.text().strip()
        phone = self.signup_phone.text().strip()
        password = self.signup_password.text()
        confirm_password = self.signup_confirm_password.text()
        industry = self.signup_industry.text().strip()
        
        if not all([company_name, contact_person, email, phone, password, confirm_password, industry]):
            self.signup_status.setText("Please fill in all fields.")
            return
        
        if password != confirm_password:
            self.signup_status.setText("Passwords do not match.")
            return
        
        if len(password) < 6:
            self.signup_status.setText("Password must be at least 6 characters.")
            return
        
        if "@" not in email:
            self.signup_status.setText("Please enter a valid email address.")
            return
        
        try:
            # Demo database save - replace with actual database logic
            conn = psycopg2.connect(
                host=host,
                user=user,
                password=_password,
                database=database
            )
            cursor = conn.cursor()
            
            # Hash password
            hash_object = hashlib.sha256(password.encode())
            hex_dig = hash_object.hexdigest()
            
            # Insert client data
            cursor.execute(
                """INSERT INTO clients (company_name, contact_person, email, phone, password, industry) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (company_name, contact_person, email, phone, hex_dig, industry)
            )
            
            conn.commit()
            conn.close()
            
            self.signup_status.setText("Account created successfully!")
            self.signup_status.setStyleSheet("color: #4caf50; font-weight: bold;")
            QTimer.singleShot(2500, self.flip)
            
        except psycopg2.IntegrityError:
            self.signup_status.setText("Email already registered.")
            self.signup_status.setStyleSheet("color: #f44336; font-weight: bold;")
        except Exception as e:
            self.signup_status.setText(f"Error: {str(e)}")
            self.signup_status.setStyleSheet("color: #f44336; font-weight: bold;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    main_app = ClientApp()
    main_app.showMaximized()
    
    sys.exit(app.exec())