import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QStackedWidget, QCheckBox, QFrame
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt, QTimer

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intuitive Login")
        # Updated geometry for a larger window
        self.setGeometry(100, 100, 1200, 800) # x, y, width, height
        # Removed setFixedSize to allow the window to be resizable,
        # but the content itself is still designed for a fixed maximum width.
        # If you want the content to scale, more complex layout management would be needed.

        self.init_ui()

    def init_ui(self):
        # Set a modern font for the entire application
        font = QFont("Segoe UI", 10)
        self.setFont(font)

        # Set a custom palette for a modern look
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f0f2f5")) # Light gray background
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#333333")) # Dark text
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#4285F4")) # Google blue for highlights
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        self.setPalette(palette)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20) # Spacing between widgets

        # Add stretch to push content to the center vertically
        main_layout.addStretch(1)

        # Title Label
        title_label = QLabel("Welcome!")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50;") # Darker blue-gray
        main_layout.addWidget(title_label)

        # Create a container widget for the stacked widget to control its max width and center it
        form_container_widget = QWidget()
        form_container_layout = QHBoxLayout()
        form_container_layout.setContentsMargins(0, 0, 0, 0)
        form_container_layout.addStretch(1) # Push stacked widget to center horizontally

        # Stacked Widget to switch between Login and Sign Up forms
        self.stacked_widget = QStackedWidget()
        # Set a maximum width for the forms to keep them centralized and readable on a larger window
        self.stacked_widget.setMaximumWidth(400)
        form_container_layout.addWidget(self.stacked_widget)
        form_container_layout.addStretch(1) # Push stacked widget to center horizontally
        form_container_widget.setLayout(form_container_layout)
        main_layout.addWidget(form_container_widget)


        # Create Login Form
        self.login_form_widget = self.create_login_form()
        self.stacked_widget.addWidget(self.login_form_widget)

        # Create Sign Up Form
        self.signup_form_widget = self.create_signup_form()
        self.stacked_widget.addWidget(self.signup_form_widget)

        # Status message label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 9))
        self.status_label.setStyleSheet("color: #d35400;") # Orange for errors/messages
        main_layout.addWidget(self.status_label)

        # Add stretch to push content to the center vertically
        main_layout.addStretch(2) # Give more stretch below to center better visually

        self.setLayout(main_layout)

    def create_login_form(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Email Input
        email_label = QLabel("Email Address")
        self.login_email_input = QLineEdit()
        self.login_email_input.setPlaceholderText("you@example.com")
        self.login_email_input.setStyleSheet(self.get_input_style())
        layout.addWidget(email_label)
        layout.addWidget(self.login_email_input)

        # Password Input
        password_label = QLabel("Password")
        self.login_password_input = QLineEdit()
        self.login_password_input.setPlaceholderText("••••••••")
        self.login_password_input.setEchoMode(QLineEdit.EchoMode.Password) # Hide password
        self.login_password_input.setStyleSheet(self.get_input_style())
        layout.addWidget(password_label)
        layout.addWidget(self.login_password_input)

        # Show Password Checkbox
        show_password_checkbox = QCheckBox("Show Password")
        show_password_checkbox.setStyleSheet("QCheckBox { color: #555; }")
        show_password_checkbox.stateChanged.connect(self.toggle_login_password_visibility)
        layout.addWidget(show_password_checkbox)

        # Login Button
        login_button = QPushButton("Log In")
        login_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        login_button.setStyleSheet(self.get_button_style("#4285F4", "#3367D6")) # Google Blue
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

        # Forgot Password Link
        forgot_password_button = QPushButton("Forgot Password?")
        forgot_password_button.setStyleSheet("QPushButton { border: none; color: #4285F4; text-decoration: underline; padding: 5px; } QPushButton:hover { color: #3367D6; }")
        forgot_password_button.clicked.connect(self.handle_forgot_password)
        layout.addWidget(forgot_password_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("margin-top: 10px; margin-bottom: 10px;")
        layout.addWidget(separator)

        # Google Sign-In Button (Icon not included in this basic example, but can be added)
        google_login_button = QPushButton("Sign in with Google")
        google_login_button.setFont(QFont("Segoe UI", 11))
        google_login_button.setStyleSheet(self.get_button_style("#DB4437", "#C53929")) # Google Red
        google_login_button.clicked.connect(self.handle_google_login)
        layout.addWidget(google_login_button)

        # Switch to Sign Up
        switch_to_signup_layout = QHBoxLayout()
        switch_to_signup_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        switch_to_signup_layout.addWidget(QLabel("Don't have an account?"))
        signup_link = QPushButton("Sign Up")
        signup_link.setStyleSheet("QPushButton { border: none; color: #4285F4; text-decoration: underline; } QPushButton:hover { color: #3367D6; }")
        signup_link.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1)) # Switch to signup form
        switch_to_signup_layout.addWidget(signup_link)
        layout.addLayout(switch_to_signup_layout)

        layout.addStretch() # Push content to top

        widget.setLayout(layout)
        return widget

    def create_signup_form(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Email Input
        email_label = QLabel("Email Address")
        self.signup_email_input = QLineEdit()
        self.signup_email_input.setPlaceholderText("you@example.com")
        self.signup_email_input.setStyleSheet(self.get_input_style())
        layout.addWidget(email_label)
        layout.addWidget(self.signup_email_input)

        # Password Input
        password_label = QLabel("Password")
        self.signup_password_input = QLineEdit()
        self.signup_password_input.setPlaceholderText("••••••••")
        self.signup_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_password_input.setStyleSheet(self.get_input_style())
        layout.addWidget(password_label)
        layout.addWidget(self.signup_password_input)

        # Confirm Password Input
        confirm_password_label = QLabel("Confirm Password")
        self.signup_confirm_password_input = QLineEdit()
        self.signup_confirm_password_input.setPlaceholderText("••••••••")
        self.signup_confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_confirm_password_input.setStyleSheet(self.get_input_style())
        layout.addWidget(confirm_password_label)
        layout.addWidget(self.signup_confirm_password_input)

        # Show Password Checkbox
        show_password_checkbox = QCheckBox("Show Password")
        show_password_checkbox.setStyleSheet("QCheckBox { color: #555; }")
        show_password_checkbox.stateChanged.connect(self.toggle_signup_password_visibility)
        layout.addWidget(show_password_checkbox)

        # Sign Up Button
        signup_button = QPushButton("Sign Up")
        signup_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        signup_button.setStyleSheet(self.get_button_style("#34A853", "#2C8B44")) # Google Green
        signup_button.clicked.connect(self.handle_signup)
        layout.addWidget(signup_button)

        # Switch to Login
        switch_to_login_layout = QHBoxLayout()
        switch_to_login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        switch_to_login_layout.addWidget(QLabel("Already have an account?"))
        login_link = QPushButton("Log In")
        login_link.setStyleSheet("QPushButton { border: none; color: #4285F4; text-decoration: underline; } QPushButton:hover { color: #3367D6; }")
        login_link.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0)) # Switch to login form
        switch_to_login_layout.addWidget(login_link)
        layout.addLayout(switch_to_login_layout)

        layout.addStretch() # Push content to top

        widget.setLayout(layout)
        return widget

    def get_input_style(self):
        return """
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px 12px;
                background-color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4285F4;
                outline: none;
            }
        """

    def get_button_style(self, bg_color, hover_color):
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border-radius: 10px;
                padding: 12px 20px;
                border: none;
                font-weight: bold;
                transition: background-color 0.3s ease;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            }}
            QPushButton:pressed {{
                background-color: {bg_color};
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
        """

    def toggle_login_password_visibility(self, state):
        if state == Qt.CheckState.Checked.value:
            self.login_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.login_password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def toggle_signup_password_visibility(self, state):
        if state == Qt.CheckState.Checked.value:
            self.signup_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.signup_confirm_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.signup_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.signup_confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def show_message(self, message, is_error=False):
        self.status_label.setText(message)
        if is_error:
            self.status_label.setStyleSheet("color: #c0392b; font-weight: bold;") # Red for errors
        else:
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;") # Green for success

        # Clear message after a few seconds
        QTimer.singleShot(5000, lambda: self.status_label.setText(""))
        QTimer.singleShot(5000, lambda: self.status_label.setStyleSheet("color: #d35400;")) # Reset style

    def handle_login(self):
        email = self.login_email_input.text().strip()
        password = self.login_password_input.text()

        if not email or not password:
            self.show_message("Please enter both email and password.", is_error=True)
            return

        # --- Placeholder for actual authentication logic ---
        # In a real app, you would send these credentials to your backend/Firebase
        # and handle the response.
        if email == "test@example.com" and password == "password123":
            self.show_message("Login successful! Welcome.", is_error=False)
            # Here you would typically transition to the main application window
            # self.close() # Close login window
            # self.main_app_window = MainApplicationWindow()
            # self.main_app_window.show()
        else:
            self.show_message("Invalid email or password.", is_error=True)

    def handle_signup(self):
        email = self.signup_email_input.text().strip()
        password = self.signup_password_input.text()
        confirm_password = self.signup_confirm_password_input.text()

        if not email or not password or not confirm_password:
            self.show_message("Please fill in all fields.", is_error=True)
            return

        if password != confirm_password:
            self.show_message("Passwords do not match.", is_error=True)
            return

        if len(password) < 6:
            self.show_message("Password must be at least 6 characters long.", is_error=True)
            return

        # --- Placeholder for actual signup logic ---
        # In a real app, you would send these details to your backend/Firebase
        # to create a new user account.
        if "@" not in email or "." not in email:
            self.show_message("Please enter a valid email address.", is_error=True)
            return

        self.show_message(f"Sign up successful for {email}! Please log in.", is_error=False)
        # Optionally clear fields and switch to login view
        self.signup_email_input.clear()
        self.signup_password_input.clear()
        self.signup_confirm_password_input.clear()
        self.stacked_widget.setCurrentIndex(0) # Switch back to login form

    def handle_forgot_password(self):
        email = self.login_email_input.text().strip() # Use the email from the login field

        if not email:
            self.show_message("Please enter your email to reset password.", is_error=True)
            return

        # --- Placeholder for actual password reset logic ---
        # In a real app, you would send a password reset email via your backend/Firebase
        self.show_message(f"Password reset link sent to {email} (simulated).", is_error=False)
        # In a real app, you might show a confirmation dialog or switch to a dedicated reset screen

    def handle_google_login(self):
        # --- Placeholder for Google Sign-In logic ---
        # This would typically involve opening a browser for OAuth flow or using a dedicated
        # Google Sign-In SDK for desktop apps if available.
        self.show_message("Google Sign-In initiated (simulated).", is_error=False)
        # On successful Google login, you would then authenticate the user in your system.

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec())
