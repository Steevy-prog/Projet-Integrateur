import sys
import psycopg2
from psycopg2 import Error
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QCheckBox, QFrame, QScrollArea,
    QSizePolicy, QSpacerItem, QGridLayout, QMessageBox, QComboBox, QStackedWidget
)
from PyQt5.QtCore import Qt, QSize, QTimer # Import QTimer for simulating delay
from PyQt5.QtGui import QFont, QColor, QPalette


def connect_to_db(host, database, user, password, port=5432):
    """
    Connects to a PostgreSQL database and returns the connection object.
    """
    connection = None
    try:
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        print(f"Successfully connected to PostgreSQL database: {database}")
        return connection
    except Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None


# --- Start of AccountSettingsPage Class ---
class AccountSettingsPage(QWidget):
    """
    A QWidget that encapsulates the entire Account Settings content,
    including employee list, create account form, and edit account form.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("accountSettingsPage") # For QSS targeting

        self.current_selected_employee = None # To store data of the currently selected employee

        self._setup_ui()
        # self._load_employee_data() # REMOVED: Data loading is now triggered by button click

    def _setup_ui(self):
        """
        Sets up the layout and widgets for the Account Settings page.
        """
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0) # No extra margins for the page itself
        self.main_layout.setSpacing(25) # Spacing between sections

        # Content sub-sections using a grid layout for better alignment
        self.content_grid_layout = QGridLayout()
        self.content_grid_layout.setContentsMargins(0, 0, 0, 0) # No extra margins within the grid
        self.content_grid_layout.setSpacing(30) # Spacing between the three main columns

        # 1. Employee Account List Section
        # This section will now include a button to trigger loading
        employee_list_container = QWidget()
        employee_list_container_layout = QVBoxLayout(employee_list_container)
        employee_list_container_layout.setContentsMargins(0, 0, 0, 0) # No extra margins

        # Add the Load Employees button
        self.load_employees_button = QPushButton("Load Employee List")
        self.load_employees_button.setObjectName("primaryButton") # Use primary button style
        self.load_employees_button.clicked.connect(self._load_employee_data_from_db)
        employee_list_container_layout.addWidget(self.load_employees_button)
        employee_list_container_layout.addSpacing(15) # Space between button and list frame

        self.employee_list_frame = self._create_employee_list_section()
        employee_list_container_layout.addWidget(self.employee_list_frame)


        # Span 2 rows (for list, and aligning with create/edit sections)
        self.content_grid_layout.addWidget(employee_list_container, 0, 0, 2, 1)

        # 2. Create New Account Section
        self.create_account_frame = self._create_create_account_section()
        self.content_grid_layout.addWidget(self.create_account_frame, 0, 1, 1, 1) # Row 0, Col 1

        # 3. Edit Employee Account Section
        self.edit_account_frame = self._create_edit_account_section()
        self.content_grid_layout.addWidget(self.edit_account_frame, 1, 1, 1, 1) # Row 1, Col 1

        self.main_layout.addLayout(self.content_grid_layout)
        self.main_layout.addStretch() # Push content to top

    def _create_employee_list_section(self):
        """
        Creates and returns the QFrame for the Employee Account List.
        Initially, it will be empty or show a placeholder message.
        """
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Employee Account List")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        # Use a QScrollArea for the list of employee cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # No horizontal scrollbar
        scroll_area.setObjectName("employeeListScrollArea") # For QSS

        scroll_content = QWidget()
        self.employee_cards_layout = QVBoxLayout(scroll_content)
        self.employee_cards_layout.setContentsMargins(0,0,0,0) # No extra margins within scroll content
        self.employee_cards_layout.setSpacing(10) # Spacing between individual employee cards

        self.employee_cards = [] # List to hold references to the employee card QFrames

        # Initial placeholder message
        self.initial_message_label = QLabel("Click 'Load Employee List' to retrieve data.")
        self.initial_message_label.setAlignment(Qt.AlignCenter)
        self.initial_message_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 20px;")
        self.employee_cards_layout.addWidget(self.initial_message_label)


        self.employee_cards_layout.addStretch() # Pushes content to top as they are added
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        return frame

    def _load_employee_data_from_db(self):
        """
        Simulates loading employee data from a database with a delay.
        This method is connected to the "Load Employee List" button.
        """
        self.load_employees_button.setEnabled(False) # Disable button during loading
        self.load_employees_button.setText("Loading...")

        # Hide initial message
        if self.initial_message_label:
            self.initial_message_label.hide()

        # Clear existing cards before loading new data
        self._clear_employee_cards()

        # Simulate a network request/database query delay
        QTimer.singleShot(1500, self._populate_employee_list) # Call _populate_employee_list after 1.5 seconds

    def _populate_employee_list(self):
        """
        Populates the employee list section with data (after simulated delay).
        """
        # Example employee data - in a real app, this would be the actual data from your database
        employees = [
            {"first": "John", "last": "Smith", "username": "john.smit", "access": "Employee"},
            {"first": "Mary", "last": "Jane", "username": "mary.jane", "access": "Employee"},
            {"first": "Jack", "last": "Bulls", "username": "jack.bull", "access": "Employee"},
            {"first": "Noel", "last": "King", "username": "noel.king", "access": "Admin"},
            {"first": "Alice", "last": "Wonder", "username": "a.wonder", "access": "Employee"},
            {"first": "Bob", "last": "Builder", "username": "b.builder", "access": "Employee"},
            {"first": "Charlie", "last": "Chaplin", "username": "c.chaplin", "access": "Admin"},
            {"first": "Diana", "last": "Prince", "username": "d.prince", "access": "Employee"},
            {"first": "Eve", "last": "Adams", "username": "e.adams", "access": "Employee"},
        ]

        if not employees:
            self.initial_message_label.setText("No employees found.")
            self.initial_message_label.show()
            QMessageBox.information(self, "Load Status", "No employee data found in the database.")
            return

        for emp in employees:
            card = self._create_employee_card_widget(emp)
            card.mousePressEvent = lambda event, e=emp, c=card: self._on_employee_card_clicked(e, c)
            # Insert before the stretch to keep content at the top
            self.employee_cards_layout.insertWidget(self.employee_cards_layout.count() - 1, card)
            self.employee_cards.append(card)

        QMessageBox.information(self, "Load Status", f"Successfully loaded {len(employees)} employees.")
        self.load_employees_button.setEnabled(True) # Re-enable button
        self.load_employees_button.setText("Reload Employee List") # Change text for subsequent loads


    def _clear_employee_cards(self):
        """
        Helper function to clear all employee cards from the layout.
        """
        while self.employee_cards_layout.count() > 1: # Keep the stretch item
            item = self.employee_cards_layout.takeAt(0) # Take the first item (a card)
            widget = item.widget()
            if widget:
                widget.setParent(None) # Remove it from the layout and delete
        self.employee_cards.clear()


    def _create_employee_card_widget(self, employee_data):
        """
        Creates a QFrame widget representing a single employee card.
        """
        card_frame = QFrame()
        card_frame.setObjectName("employeeCard")
        card_frame.setCursor(Qt.PointingHandCursor) # Indicate it's clickable
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(15, 10, 15, 10)
        card_layout.setSpacing(5)
        card_layout.addWidget(QLabel(f"<b>First Name:</b> {employee_data['first']}"))
        card_layout.addWidget(QLabel(f"<b>Last Name:</b> {employee_data['last']}"))
        card_layout.addWidget(QLabel(f"<b>Username:</b> {employee_data['username']}"))
        card_layout.addWidget(QLabel(f"<b>Access Level:</b> {employee_data['access']}"))
        return card_frame

    def _create_create_account_section(self):
        """
        Creates and returns the QFrame for the Create New Account section.
        """
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Create New Account")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        self.create_first_name_input = QLineEdit()
        self.create_last_name_input = QLineEdit()
        self.create_username_input = QLineEdit()
        self.create_password_input = QLineEdit()
        self.create_password_input.setEchoMode(QLineEdit.Password) # Hide password characters
        self.create_confirm_password_input = QLineEdit()
        self.create_confirm_password_input.setEchoMode(QLineEdit.Password) # Hide password characters
        self.create_admin_checkbox = QCheckBox("Create as admin account")

        form_layout.addWidget(QLabel("First Name :"), 0, 0)
        form_layout.addWidget(self.create_first_name_input, 0, 1)
        form_layout.addWidget(QLabel("Last Name :"), 1, 0)
        form_layout.addWidget(self.create_last_name_input, 1, 1)
        form_layout.addWidget(QLabel("Username :"), 2, 0)
        form_layout.addWidget(self.create_username_input, 2, 1)
        form_layout.addWidget(QLabel("Password :"), 3, 0)
        form_layout.addWidget(self.create_password_input, 3, 1)
        form_layout.addWidget(QLabel("Confirm :"), 4, 0)
        form_layout.addWidget(self.create_confirm_password_input, 4, 1)

        layout.addLayout(form_layout)
        layout.addWidget(self.create_admin_checkbox)

        self.create_account_button = QPushButton("Create Account")
        self.create_account_button.setObjectName("primaryButton")
        self.create_account_button.clicked.connect(self._create_new_account)
        layout.addWidget(self.create_account_button)

        layout.addStretch() # Push content to top

        return frame

    def _create_edit_account_section(self):
        """
        Creates and returns the QFrame for the Edit Employee Account section.
        """
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Edit Employee Account")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        layout.addWidget(QLabel("Click on an employee card on the left to select an employee account."))

        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        self.edit_first_name_input = QLineEdit()
        self.edit_last_name_input = QLineEdit()
        self.edit_username_input = QLineEdit()
        # Changed to QComboBox for access level for better control
        self.edit_access_level_combobox = QComboBox()
        self.edit_access_level_combobox.addItems(["Employee", "Admin"])

        form_layout.addWidget(QLabel("First Name :"), 0, 0)
        form_layout.addWidget(self.edit_first_name_input, 0, 1)
        form_layout.addWidget(QLabel("Last Name :"), 1, 0)
        form_layout.addWidget(self.edit_last_name_input, 1, 1)
        form_layout.addWidget(QLabel("Username :"), 2, 0)
        form_layout.addWidget(self.edit_username_input, 2, 1)
        form_layout.addWidget(QLabel("Access Level :"), 3, 0)
        form_layout.addWidget(self.edit_access_level_combobox, 3, 1)

        self.change_password_button = QPushButton("Change Password")
        self.change_password_button.setObjectName("secondaryButton")
        self.change_password_button.clicked.connect(self._change_password)
        form_layout.addWidget(self.change_password_button, 4, 1) # Aligned right

        layout.addLayout(form_layout)

        self.save_changes_button = QPushButton("Save Changes")
        self.save_changes_button.setObjectName("primaryButton")
        self.save_changes_button.clicked.connect(self._save_changes)
        self.save_changes_button.setEnabled(False) # Disable until an employee is selected
        layout.addWidget(self.save_changes_button)

        layout.addStretch() # Push content to top

        return frame

    # --- Event Handlers and Logic for AccountSettingsPage ---
    def _on_employee_card_clicked(self, employee_data, clicked_card):
        """
        Handles the click event on an employee card.
        Populates the 'Edit Employee Account' section with the selected employee's data.
        """
        print(f"Employee card clicked: {employee_data['username']}")

        # Clear previous selection style from all cards
        for card in self.employee_cards:
            card.setProperty("selected", False)
            card.style().polish(card) # Re-apply stylesheet to update visual state

        # Set new selection style for the clicked card
        clicked_card.setProperty("selected", True)
        clicked_card.style().polish(clicked_card) # Re-apply stylesheet

        # Populate the "Edit Employee Account" section's fields
        self.edit_first_name_input.setText(employee_data['first'])
        self.edit_last_name_input.setText(employee_data['last'])
        self.edit_username_input.setText(employee_data['username'])
        # Set the current access level in the combobox
        index = self.edit_access_level_combobox.findText(employee_data['access'])
        if index != -1:
            self.edit_access_level_combobox.setCurrentIndex(index)

        self.save_changes_button.setEnabled(True) # Enable save button
        self.current_selected_employee = employee_data # Store for saving changes

    def _create_new_account(self):
        """
        Handles the logic for creating a new account.
        In a real application, this would involve sending data to a backend.
        """
        first_name = self.create_first_name_input.text().strip()
        last_name = self.create_last_name_input.text().strip()
        username = self.create_username_input.text().strip()
        password = self.create_password_input.text()
        confirm_password = self.create_confirm_password_input.text()
        is_admin = self.create_admin_checkbox.isChecked()

        if not (first_name and last_name and username and password and confirm_password):
            QMessageBox.warning(self, "Input Error", "All fields must be filled to create an account.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Input Error", "Passwords do not match.")
            return

        if len(password) < 6: # Example validation
            QMessageBox.warning(self, "Input Error", "Password must be at least 6 characters long.")
            return

        print(f"Creating New Account:")
        print(f"  First Name: {first_name}")
        print(f"  Last Name: {last_name}")
        print(f"  Username: {username}")
        # NEVER print actual password in logs in a real app
        print(f"  Is Admin: {is_admin}")

        # Simulate success
        QMessageBox.information(self, "Account Created", f"Account for {username} created successfully!")

        # Clear form fields after successful creation
        self.create_first_name_input.clear()
        self.create_last_name_input.clear()
        self.create_username_input.clear()
        self.create_password_input.clear()
        self.create_confirm_password_input.clear()
        self.create_admin_checkbox.setChecked(False)

        # In a real app, you would refresh your employee list here after adding the new account to your data source
        self._load_employee_data_from_db() # Refresh list after creating new account


    def _save_changes(self):
        """
        Handles the logic for saving changes to an existing employee account.
        """
        if not self.current_selected_employee:
            QMessageBox.warning(self, "Selection Error", "No employee selected for editing.")
            return

        original_username = self.current_selected_employee['username']
        new_first_name = self.edit_first_name_input.text().strip()
        new_last_name = self.edit_last_name_input.text().strip()
        new_username = self.edit_username_input.text().strip()
        new_access_level = self.edit_access_level_combobox.currentText()

        if not (new_first_name and new_last_name and new_username):
            QMessageBox.warning(self, "Input Error", "First Name, Last Name, and Username cannot be empty.")
            return

        print(f"Saving changes for {original_username}:")
        print(f"  New First Name: {new_first_name}")
        print(f"  New Last Name: {new_last_name}")
        print(f"  New Username: {new_username}")
        print(f"  New Access Level: {new_access_level}")

        # Simulate success
        QMessageBox.information(self, "Changes Saved", f"Changes for {new_username} saved successfully!")

        # In a real app:
        # 1. Update the data in your backend/database
        # 2. Refresh the employee list to reflect changes
        self._load_employee_data_from_db() # Reload all data to update list

        # After saving, clear selection and reset edit form
        self.current_selected_employee = None
        for card in self.employee_cards:
            card.setProperty("selected", False)
            card.style().polish(card)
        self.edit_first_name_input.clear()
        self.edit_last_name_input.clear()
        self.edit_username_input.clear()
        self.edit_access_level_combobox.setCurrentIndex(0) # Reset to default
        self.save_changes_button.setEnabled(False)


    def _change_password(self):
        """
        Placeholder for initiating a password change process.
        """
        if not self.current_selected_employee:
            QMessageBox.warning(self, "Selection Error", "No employee selected to change password.")
            return
        
        QMessageBox.information(self, "Change Password", 
                                f"Initiating password change for {self.current_selected_employee['username']}. "
                                "This would typically open a new dialog.")
# --- End of AccountSettingsPage Class ---


# --- Start of Placeholder Page Classes ---
class SystemConfigurationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("placeholderPage")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel("<h1>Site Settings Content</h1>"))
        layout.addWidget(QLabel("This is where site-wide configurations would go."))

class DatabaseMaintenancePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("placeholderPage")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel("<h1>Inventory Overview</h1>"))
        layout.addWidget(QLabel("Displays summaries and reports of inventory."))

class SecuritySettingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("placeholderPage")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel("<h1>View Reports</h1>"))
        layout.addWidget(QLabel("Generate and view various reports here."))

# --- End of Placeholder Page Classes ---


# --- Main Application Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application Dashboard")
        self.setGeometry(100, 100, 1200, 800) # Initial window size

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """
        Sets up the main window's layout, sidebar, and stacked widget for content.
        """
        # 1. Left Sidebar
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebarFrame")
        self.sidebar_frame.setFixedWidth(250)
        self.sidebar_layout = QVBoxLayout(self.sidebar_frame)
        self.sidebar_layout.setContentsMargins(20, 20, 20, 20)
        self.sidebar_layout.setSpacing(15)

        self.logged_in_label = QLabel("Logged in as <b>john.smit</b>")
        self.logged_in_label.setObjectName("loggedInLabel")
        self.logged_in_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sidebar_layout.addWidget(self.logged_in_label)

        self.sidebar_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Navigation buttons and their corresponding page instances/indices
        self.nav_buttons = {}
        self.pages = [] # List to hold instances of QWidget pages

        self.stacked_content_widget = QStackedWidget() # The QStackedWidget for main content

        # Define navigation items and create their pages
        # The order here defines the index in QStackedWidget
        nav_items_map = {
            "ACCOUNT SETTINGS": AccountSettingsPage(),
            "SYSTEM CONFIGURATION": SystemConfigurationPage(),
            "DATABASE MAINTENANCE": DatabaseMaintenancePage(),
            "SECURITY SETTINGS": SecuritySettingPage()
        }

        # Add pages to stacked widget and create sidebar buttons
        for i, (text, page_widget) in enumerate(nav_items_map.items()):
            self.pages.append(page_widget)
            self.stacked_content_widget.addWidget(page_widget) # Add page to stack

            btn = QPushButton(text)
            btn.setObjectName(f"navButton_{text.replace(' ', '')}") # For QSS
            btn.clicked.connect(lambda checked, idx=i, b=btn: self._on_nav_button_clicked(idx, b))
            self.nav_buttons[text] = btn
            self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addStretch() # Pushes content to the top

        # 2. Main Content Area
        self.content_area_container = QWidget()
        self.content_area_layout = QVBoxLayout(self.content_area_container)
        self.content_area_layout.setContentsMargins(40, 30, 40, 30)
        self.content_area_layout.setSpacing(25)

        self.main_title_label = QLabel("Account Settings") # This label will change with page
        self.main_title_label.setObjectName("mainTitleLabel")
        self.content_area_layout.addWidget(self.main_title_label)

        # Add the QStackedWidget to the main content area
        self.content_area_layout.addWidget(self.stacked_content_widget)
        self.content_area_layout.addStretch()

        # Set initial page and active button
        self.stacked_content_widget.setCurrentIndex(0)
        initial_nav_button_text = list(nav_items_map.keys())[0] # Get first key
        self.nav_buttons[initial_nav_button_text].setProperty("active", True)
        self.nav_buttons[initial_nav_button_text].style().polish(self.nav_buttons[initial_nav_button_text])
        self.main_title_label.setText(initial_nav_button_text) # Set initial title

        # Add parts to main layout
        self.main_layout.addWidget(self.sidebar_frame)
        self.main_layout.addWidget(self.content_area_container)

    def _on_nav_button_clicked(self, index, clicked_button):
        """
        Handles navigation button clicks, switching the QStackedWidget page
        and updating button active states.
        """
        # Update the main title label to match the selected page
        self.main_title_label.setText(clicked_button.text())

        # Switch the current page in the QStackedWidget
        self.stacked_content_widget.setCurrentIndex(index)

        # Update active state for sidebar buttons
        for text, btn_widget in self.nav_buttons.items():
            if btn_widget == clicked_button:
                btn_widget.setProperty("active", True)
            else:
                btn_widget.setProperty("active", False)
            btn_widget.style().polish(btn_widget) # Re-apply stylesheet to update active state

    def _apply_styles(self):
        """
        Applies Qt Style Sheets (QSS) for the application's look and feel.
        """
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5; /* Light gray background */
            }

            #sidebarFrame {
                background-color: #2c3e50; /* Dark blue */
                border-right: 1px solid #34495e;
            }

            #loggedInLabel {
                color: #ecf0f1; /* Light gray for text */
                font-size: 16px;
                padding-bottom: 10px;
                border-bottom: 1px solid #34495e;
            }

            /* General QPushButton styles */
            QPushButton {
                background-color: #3498db; /* Blue */
                color: white;
                border: none;
                padding: 10px 15px;
                text-align: left; /* Align text left for nav */
                font-size: 14px;
                border-radius: 5px;
                min-width: 150px;
            }

            QPushButton:hover {
                background-color: #2980b9;
            }

            /* Specific style for active nav buttons */
            QPushButton[active="true"] {
                background-color: #f39c12; /* Orange for active */
                color: #2c3e50; /* Dark text for active */
                font-weight: bold;
            }
            QPushButton[active="true"]:hover {
                background-color: #e67e22; /* Darker orange on hover */
            }

            /* Generic styling for all main content sections (frames) */
            #sectionFrame, #accountSettingsPage, #placeholderPage {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
            }

            #mainTitleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
            }

            #sectionTitle {
                font-size: 20px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 15px;
            }

            QLineEdit, QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #3498db;
            }

            QCheckBox {
                font-size: 14px;
                color: #34495e;
            }

            /* Employee Card Styling */
            #employeeCard {
                background-color: #ecf0f1; /* Light background for cards */
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
            }
            #employeeCard QLabel {
                font-size: 13px;
                color: #34495e;
            }
            #employeeCard:hover {
                background-color: #dbe2e9;
                border: 1px solid #3498db;
            }
            #employeeCard[selected="true"] { /* Custom property for selected state */
                background-color: #cceeff; /* Lighter blue for selected */
                border: 2px solid #3498db;
            }

            #primaryButton {
                background-color: #2ecc71; /* Green */
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
                margin-top: 15px;
                text-align: center;
            }
            #primaryButton:hover {
                background-color: #27ae60;
            }
            #primaryButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }

            #secondaryButton {
                background-color: #95a5a6; /* Gray */
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 14px;
                border-radius: 5px;
                margin-top: 10px;
                text-align: center;
            }
            #secondaryButton:hover {
                background-color: #7f8c8d;
            }

            QScrollArea {
                border: none; /* Remove default scroll area border */
            }
            QScrollArea > QWidget > QWidget { /* The actual content widget inside scroll area */
                background-color: transparent;
            }
            #placeholderPage h1 {
                color: #34495e;
            }
        """)


if __name__ == "__main__":
    
    host = "dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com"  # Replace with your database host
    database = "projet_integrateur"  # Replace with your database name
    user = "group13"  # Replace with your database username
    password = "nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3"  # Replace with your database password
    port = 5432  # Default PostgreSQL port, change if necessary

    db_connection = connect_to_db(host, database, user, password, port)
    
    app = QApplication(sys.argv)

    # Set default font for consistency (optional)
    font = QFont("Arial", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
