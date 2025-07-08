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
            self.bg_image = QPixmap("Interface\IT.jpg")  # IT-themed background
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
            # IT-themed gradient: dark blue to cyan
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QColor(13, 71, 161))  # Deep blue
            gradient.setColorAt(0.5, QColor(21, 101, 192))  # Medium blue
            gradient.setColorAt(1, QColor(0, 188, 212))  # Cyan
            painter.fillRect(self.rect(), QBrush(gradient))
        overlay = QColor(0, 0, 0, 40)  # Slightly darker overlay for IT theme
        painter.fillRect(self.rect(), overlay)


# Database configuration
host = "localhost"
port = "5432"
database = "it_admin_db"
user = "postgres"
_password = "admin_password"


class ITAdminApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.login = ITAdminFlipCard(self)
        # Add dashboard widget here when available
        # self.dashboard = ITAdminDashboard(self)
        
        self.addWidget(self.login)
        # self.addWidget(self.dashboard)
        
        self.setCurrentIndex(0)

    def show_dashboard(self):
        # Implement dashboard switching logic
        print("Redirecting to IT Admin Dashboard...")
        # self.setCurrentWidget(self.dashboard)


class ITAdminFlipCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IT Admin Portal - Secure Access")
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setMinimumSize(900, 700)
        
        self.bg_widget = BackgroundWidget(self)
        self.card_width = 480
        self.card_height = 600
        
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
                background-color: rgba(255, 255, 255, 0.97);
                border-radius: 15px;
                border: 2px solid rgba(13, 71, 161, 0.3);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(60)
        shadow.setXOffset(0)
        shadow.setYOffset(30)
        shadow.setColor(QColor(13, 71, 161, 120))
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
        
        # Title with IT theme
        title = QLabel("IT Admin Portal")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))  # Placeholder for font
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #0d47a1;
                margin-bottom: 8px;
                margin-top: 25px;
            }
        """)
        
        subtitle = QLabel("System Administrator Access")
        subtitle.setFont(QFont("Segoe UI", 13))  # Placeholder for font
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #424242; margin-bottom: 35px; font-weight: 500;")
        
        # Input fields
        self.login_admin_id = QLineEdit()
        self.login_admin_id.setPlaceholderText("Admin ID")
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Admin Password")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.login_security_code = QLineEdit()
        self.login_security_code.setPlaceholderText("Security Code")
        self.login_security_code.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Login button
        btn_login = QPushButton("Access System")
        btn_login.clicked.connect(self.handle_login)
        
        # Status label
        self.login_status = QLabel()
        self.login_status.setStyleSheet("color: #d32f2f; font-weight: bold;")
        self.login_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Switch to signup
        switch = QPushButton("Need admin access? Request Account")
        switch.clicked.connect(self.flip)
        
        # Apply styles
        for widget in [self.login_admin_id, self.login_password, self.login_security_code]:
            widget.setFixedHeight(50)
            widget.setStyleSheet(self.input_style())
        
        btn_login.setStyleSheet(self.primary_button_style())
        btn_login.setFixedHeight(50)
        switch.setStyleSheet(self.link_button_style())
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.login_admin_id)
        layout.addWidget(self.login_password)
        layout.addWidget(self.login_security_code)
        layout.addWidget(btn_login)
        layout.addWidget(self.login_status)
        layout.addWidget(switch)
        
        layout.setSpacing(12)
        layout.setContentsMargins(35, 15, 35, 15)
        card.setLayout(layout)
        return card

    def create_signup_card(self):
        card = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Request Admin Access")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))  # Placeholder for font
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #0d47a1;
                margin-bottom: 15px;
                margin-top: 20px;
            }
        """)
        
        subtitle = QLabel("Fill out the form for admin privileges")
        subtitle.setFont(QFont("Segoe UI", 12))  # Placeholder for font
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #424242; margin-bottom: 20px;")
        
        # Input fields
        self.signup_full_name = QLineEdit()
        self.signup_full_name.setPlaceholderText("Full Name")
        
        self.signup_employee_id = QLineEdit()
        self.signup_employee_id.setPlaceholderText("Employee ID")
        
        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("Corporate Email")
        
        self.signup_department = QLineEdit()
        self.signup_department.setPlaceholderText("Department")
        
        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("Create Password")
        self.signup_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.signup_confirm_password = QLineEdit()
        self.signup_confirm_password.setPlaceholderText("Confirm Password")
        self.signup_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.signup_security_code = QLineEdit()
        self.signup_security_code.setPlaceholderText("Security Authorization Code")
        self.signup_security_code.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Signup button
        btn_signup = QPushButton("Submit Request")
        btn_signup.clicked.connect(self.handle_signup)
        
        # Status label
        self.signup_status = QLabel()
        self.signup_status.setStyleSheet("color: #d32f2f; font-weight: bold;")
        self.signup_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Switch back to login
        switch = QPushButton("Already have admin access? Sign In")
        switch.clicked.connect(self.flip)
        
        # Apply styles
        for widget in [self.signup_full_name, self.signup_employee_id, self.signup_email, 
                      self.signup_department, self.signup_password, self.signup_confirm_password,
                      self.signup_security_code]:
            widget.setFixedHeight(45)
            widget.setStyleSheet(self.input_style())
        
        btn_signup.setStyleSheet(self.primary_button_style())
        btn_signup.setFixedHeight(45)
        switch.setStyleSheet(self.link_button_style())
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.signup_full_name)
        layout.addWidget(self.signup_employee_id)
        layout.addWidget(self.signup_email)
        layout.addWidget(self.signup_department)
        layout.addWidget(self.signup_password)
        layout.addWidget(self.signup_confirm_password)
        layout.addWidget(self.signup_security_code)
        layout.addWidget(btn_signup)
        layout.addWidget(self.signup_status)
        layout.addWidget(switch)
        
        layout.setSpacing(10)
        layout.setContentsMargins(35, 20, 35, 20)
        card.setLayout(layout)
        return card

    def input_style(self):
        return """
        QLineEdit {
            background-color: #ffffff;
            border: 2px solid #e3f2fd;
            border-radius: 12px;
            padding-left: 15px;
            padding-right: 15px;
            font-size: 14px;
            color: #0d47a1;
            font-family: "Segoe UI", Arial, sans-serif;
        }
        QLineEdit:focus {
            border: 2px solid #1976d2;
            background-color: #f8fffe;
        }
        QLineEdit::placeholder {
            color: #90a4ae;
        }
        """

    def primary_button_style(self):
        return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #1976d2, stop:1 #0d47a1);
            color: white;
            font-weight: bold;
            font-size: 16px;
            border: none;
            border-radius: 12px;
            font-family: "Segoe UI", Arial, sans-serif;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #42a5f5, stop:1 #1976d2);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #0d47a1, stop:1 #01579b);
        }
        """

    def link_button_style(self):
        return """
        QPushButton {
            background: transparent;
            color: #1976d2;
            font-size: 13px;
            border: none;
            text-decoration: underline;
            padding: 12px;
            font-family: "Segoe UI", Arial, sans-serif;
        }
        QPushButton:hover {
            color: #0d47a1;
        }
        """

    def flip(self):
        self.setEnabled(False)
        animation = QPropertyAnimation(self.container, b"geometry")
        animation.setDuration(600)
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
        admin_id = self.login_admin_id.text().strip()
        password = self.login_password.text()
        security_code = self.login_security_code.text().strip()
        
        if not admin_id or not password or not security_code:
            self.login_status.setText("Please fill in all fields.")
            return
        
        # Demo credentials for IT Admin
        if admin_id == "admin001" and password == "ITadmin123" and security_code == "SEC2024":
            self.login_status.setText("Access granted! Loading system...")
            self.login_status.setStyleSheet("color: #2e7d32; font-weight: bold;")
            QTimer.singleShot(1500, self.open_dashboard)
        else:
            self.login_status.setText("Invalid credentials or security code.")
            self.login_status.setStyleSheet("color: #d32f2f; font-weight: bold;")

    def open_dashboard(self):
        parent = self.parent()
        if hasattr(parent, "show_dashboard"):
            parent.show_dashboard()

    def handle_signup(self):
        full_name = self.signup_full_name.text().strip()
        employee_id = self.signup_employee_id.text().strip()
        email = self.signup_email.text().strip()
        department = self.signup_department.text().strip()
        password = self.signup_password.text()
        confirm_password = self.signup_confirm_password.text()
        security_code = self.signup_security_code.text().strip()
        
        if not all([full_name, employee_id, email, department, password, confirm_password, security_code]):
            self.signup_status.setText("Please fill in all fields.")
            return
        
        if password != confirm_password:
            self.signup_status.setText("Passwords do not match.")
            return
        
        if len(password) < 8:
            self.signup_status.setText("Password must be at least 8 characters.")
            return
        
        # For demo purposes - replace with actual database logic
        if security_code == "ADMIN2024":
            self.signup_status.setText("Request submitted successfully! Awaiting approval.")
            self.signup_status.setStyleSheet("color: #2e7d32; font-weight: bold;")
            QTimer.singleShot(3000, self.flip)
        else:
            self.signup_status.setText("Invalid security authorization code.")
            self.signup_status.setStyleSheet("color: #d32f2f; font-weight: bold;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    main_app = ITAdminApp()
    main_app.showMaximized()
    
    sys.exit(app.exec())