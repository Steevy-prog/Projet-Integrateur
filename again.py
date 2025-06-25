import sys
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QLabel, QPushButton,
    QVBoxLayout, QStackedLayout, QFrame, QMessageBox, QGraphicsDropShadowEffect, QStackedWidget
)
from PyQt5.QtGui import QFont, QPainter, QPixmap, QColor, QBrush, QLinearGradient
import psycopg2
import hashlib
from yo import interface as dashboard


class BackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg_image = None
        # Try to load the background image, fallback to gradient if not found
        try:
            self.bg_image = QPixmap("A.jpg")
        except:
            self.bg_image = None

    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.bg_image and not self.bg_image.isNull():
            # Scale the image to cover the entire widget while maintaining aspect ratio
            scaled_pixmap = self.bg_image.scaled(
                self.size(), 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            )
            
            # Center the image
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
        else:
            # Fallback to a beautiful gradient background
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QColor(74, 144, 226))  # Blue
            gradient.setColorAt(0.5, QColor(80, 170, 200))  # Light blue
            gradient.setColorAt(1, QColor(46, 204, 113))  # Green
            
            painter.fillRect(self.rect(), QBrush(gradient))
        
        # Add a subtle overlay for better card visibility
        overlay = QColor(0, 0, 0, 30)  # Semi-transparent black
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

        self.addWidget(self.login)    # index 0
        self.addWidget(self.worker)   # index 1
        self.addWidget(self.client)   # index 2
        self.addWidget(self.it)       # index 3
        self.addWidget(self.manager)  # index 4

        self.setCurrentIndex(0)  # Show login first

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
        self.setWindowState(Qt.WindowMaximized)  # Maximize the window
        
        # Set minimum size to prevent issues
        self.setMinimumSize(800, 600)
        
        # Create background widget that covers the entire window
        self.bg_widget = BackgroundWidget(self)
        
        # Initialize card dimensions
        self.card_width = 450
        self.card_height = 550
        
        # Create the card container
        self.container = QFrame(self)
        self.setup_card_style()
        
        # Create the stacked layout for flip animation
        self.stack = QStackedLayout()
        self.front = self.create_login_card()
        self.back = self.create_signup_card()
        self.stack.addWidget(self.front)
        self.stack.addWidget(self.back)

        layout = QVBoxLayout(self.container)
        layout.addLayout(self.stack)
        layout.setContentsMargins(0, 0, 0, 0)

        self.flipped = False
        
        # Position the card initially
        self.position_card()
        
        # Connect resize event to reposition card
        self.resizeEvent = self.on_resize

    def setup_card_style(self):
        """Setup the visual style of the card with modern design"""
        self.container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
        """)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setXOffset(0)
        shadow.setYOffset(25)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.container.setGraphicsEffect(shadow)

    def position_card(self):
        """Center the card in the window"""
        # Get current window size
        window_width = self.width()
        window_height = self.height()
        
        # Calculate center position
        x = (window_width - self.card_width) // 2
        y = (window_height - self.card_height) // 2
        
        # Ensure minimum margins
        x = max(50, x)
        y = max(50, y)
        
        self.container.setGeometry(x, y, self.card_width, self.card_height)

    def on_resize(self, event):
        """Handle window resize events"""
        # Resize background widget to match window
        self.bg_widget.setGeometry(0, 0, self.width(), self.height())
        
        # Reposition the card
        self.position_card()
        
        # Call parent resize event
        super().resizeEvent(event)

    def create_login_card(self):
        card = QWidget()
        layout = QVBoxLayout()

        # Title with better styling
        title = QLabel("Welcome Back")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                margin-bottom: 10px;
                margin-top: 20px;
            }
        """)

        subtitle = QLabel("Sign in to your account")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 30px;")

        # Input fields
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Email Address")
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)

        # Login button
        btn_login = QPushButton("Sign In")
        btn_login.clicked.connect(self.handle_login)

        # Status label
        self.login_status = QLabel()
        self.login_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.login_status.setAlignment(Qt.AlignCenter)

        # Switch to signup
        switch = QPushButton("Don't have an account? Create one")
        switch.clicked.connect(self.flip)

        # Apply styles
        for widget in [self.login_email, self.login_password]:
            widget.setFixedHeight(45)
            widget.setStyleSheet(self.input_style())

        btn_login.setStyleSheet(self.primary_button_style())
        btn_login.setFixedHeight(45)
        
        switch.setStyleSheet(self.link_button_style())

        # Layout setup
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.login_email)
        layout.addWidget(self.login_password)
        layout.addWidget(btn_login)
        layout.addWidget(self.login_status)
        layout.addWidget(switch)

        layout.setSpacing(15)
        layout.setContentsMargins(50, 30, 50, 30)
        card.setLayout(layout)
        return card

    def create_signup_card(self):
        card = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Create Account")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                margin-bottom: 10px;
                margin-top: 20px;
            }
        """)

        subtitle = QLabel("Join us today")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 30px;")

        # Input fields
        self.signup_name = QLineEdit()
        self.signup_name.setPlaceholderText("Full Name")

        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("Email Address")

        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("Password")
        self.signup_password.setEchoMode(QLineEdit.Password)

        # Signup button
        btn_signup = QPushButton("Create Account")
        btn_signup.clicked.connect(self.handle_signup)

        # Status label
        self.signup_status = QLabel()
        self.signup_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.signup_status.setAlignment(Qt.AlignCenter)

        # Switch to login
        switch = QPushButton("Already have an account? Sign in")
        switch.clicked.connect(self.flip)

        # Apply styles
        for widget in [self.signup_name, self.signup_email, self.signup_password]:
            widget.setFixedHeight(45)
            widget.setStyleSheet(self.input_style())

        btn_signup.setStyleSheet(self.primary_button_style())
        btn_signup.setFixedHeight(45)
        
        switch.setStyleSheet(self.link_button_style())

        # Layout setup
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.signup_name)
        layout.addWidget(self.signup_email)
        layout.addWidget(self.signup_password)
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
        """Animate the card flip with improved animation"""
        self.setEnabled(False)
        
        animation = QPropertyAnimation(self.container, b"geometry")
        animation.setDuration(500)
        animation.setEasingCurve(QEasingCurve.InOutCubic)

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
        """Complete the flip animation"""
        self.stack.setCurrentIndex(1 if not self.flipped else 0)
        self.flipped = not self.flipped
        self.setEnabled(True)

    def handle_login(self):
        """Handle login authentication"""
        email = self.login_email.text().strip()
        password = self.login_password.text()
        
        if not email or not password:
            self.login_status.setText("Please fill in all fields.")
            return

        credentials = {
            "worker@example.com": ("workerpass", "worker"),
            "client@example.com": ("clientpass", "client"),
            "it@example.com": ("itpass", "it"),
            "manager@example.com": ("managerpass", "manager")
        }

        if email in credentials and password == credentials[email][0]:
            self.login_status.setText("Login successful! Redirecting...")
            self.login_status.setStyleSheet("color: #27ae60; font-weight: bold;")
            
            # Delay to show success message
            QTimer.singleShot(1000, lambda: self.open_dashboard(credentials[email][1]))
        else:
            self.login_status.setText("Invalid email or password.")
            self.login_status.setStyleSheet("color: #e74c3c; font-weight: bold;")

    def open_dashboard(self, role):
        # Use the parent MainApp to switch dashboard
        parent = self.parent()
        if hasattr(parent, "show_dashboard"):
            parent.show_dashboard(role)

    def handle_signup(self):
        """Handle user registration"""
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
            
            # Hash the password
            hash_object = hashlib.sha256(password.encode())
            hex_dig = hash_object.hexdigest()
            
            # Insert into database
            cursor.execute(
                "INSERT INTO cred (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hex_dig)
            )
            
            conn.commit()
            conn.close()
            
            self.signup_status.setText("Account created successfully!")
            self.signup_status.setStyleSheet("color: #27ae60; font-weight: bold;")
            
            # Switch to login after successful signup
            QTimer.singleShot(2000, self.flip)
            
        except psycopg2.IntegrityError:
            self.signup_status.setText("Email already exists.")
        except Exception as e:
            self.signup_status.setText(f"Error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    main_app = MainApp()
    main_app.showMaximized()
    
    sys.exit(app.exec_())