import sys
import uuid # For generating UUIDs for new records
import psycopg2 # PostgreSQL adapter
from psycopg2 import sql
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QCheckBox, QFrame, QScrollArea,
    QSizePolicy, QSpacerItem, QGridLayout, QMessageBox, QComboBox, QStackedWidget
)
from PyQt5.QtCore import Qt, QSize, QTimer, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

# --- Database Configuration ---
# IMPORTANT: Replace with your actual PostgreSQL credentials for your ONLINE database.
# NEVER hardcode sensitive credentials like this in production applications.
# Consider using environment variables or a secure configuration management system.
DB_CONFIG = {
    "host": "your_online_database_host.com", # e.g., 'ec2-54-123-456-789.compute-1.amazonaws.com'
    "database": "your_online_database_name", # The database name you created online
    "user": "your_online_database_user",     # The user for your online database
    "password": "your_online_database_password", # The password for your online database user
    "port": "5432"                           # Default PostgreSQL port (could be different for some cloud providers)
    # You might also need 'sslmode' for some cloud databases, e.g., "sslmode": "require"
}

# --- Database Worker (Runs in a separate thread) ---
class DatabaseManager(QObject):
    # Signals for communicating results back to the GUI thread
    employees_loaded = pyqtSignal(list)
    account_created = pyqtSignal(dict)
    account_updated = pyqtSignal(dict)
    account_deleted = pyqtSignal(str) # Emits the ID of the deleted employee
    error = pyqtSignal(str)

    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config
        self.conn = None # Database connection object

    def _connect(self):
        """Establishes and returns a database connection."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            print("Database connected successfully.")
            return self.conn
        except psycopg2.Error as e:
            self.error.emit(f"Database connection error: {e}")
            return None

    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Helper to execute a query and handle connection/cursor."""
        if not self.conn:
            self.conn = self._connect()
            if not self.conn:
                return None

        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                if fetch_one:
                    return cur.fetchone()
                if fetch_all:
                    # Get column names for dictionary conversion
                    col_names = [desc[0] for desc in cur.description]
                    return [dict(zip(col_names, row)) for row in cur.fetchall()]
                self.conn.commit() # Commit changes for INSERT, UPDATE, DELETE
            return True
        except psycopg2.Error as e:
            self.conn.rollback() # Rollback on error
            self.error.emit(f"Database query error: {e}")
            return False
        except Exception as e:
            self.error.emit(f"An unexpected error occurred during query: {e}")
            return False

    def create_employees_table(self):
        """Ensures the employees table exists."""
        query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS employees (
                id VARCHAR(255) PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL,
                access_level VARCHAR(50) NOT NULL
            );
        """)
        print("Attempting to create employees table...")
        if self._execute_query(query):
            print("Employees table checked/created.")
        else:
            print("Failed to create/check employees table.")

    def load_employees(self):
        """Loads all employees from the database."""
        query = sql.SQL("SELECT id, first_name, last_name, username, access_level FROM employees;")
        print("Loading employees from database...")
        employees = self._execute_query(query, fetch_all=True)
        if employees is not False: # Check against False (error)
            self.employees_loaded.emit(employees)
        else:
            print("Error loading employees.")

    def add_employee(self, data):
        """Adds a new employee to the database."""
        # Generate a UUID for the new record
        new_id = str(uuid.uuid4())
        query = sql.SQL("""
            INSERT INTO employees (id, first_name, last_name, username, access_level)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """)
        params = (new_id, data['first'], data['last'], data['username'], data['access'])
        print(f"Adding employee: {data['username']} with ID: {new_id} to database...")
        result_id = self._execute_query(query, params, fetch_one=True)
        if result_id:
            data['id'] = result_id[0] # Add the returned ID to the data
            self.account_created.emit(data)
        else:
            print("Failed to add employee.")

    def update_employee(self, employee_id, data):
        """Updates an existing employee's data."""
        query = sql.SQL("""
            UPDATE employees
            SET first_name = %s, last_name = %s, username = %s, access_level = %s
            WHERE id = %s;
        """)
        params = (data['first'], data['last'], data['username'], data['access'], employee_id)
        print(f"Updating employee ID: {employee_id} in database...")
        if self._execute_query(query, params):
            data['id'] = employee_id # Ensure ID is in the emitted data
            self.account_updated.emit(data)
        else:
            print("Failed to update employee.")

    def delete_employee(self, employee_id):
        """Deletes an employee from the database."""
        query = sql.SQL("DELETE FROM employees WHERE id = %s;")
        print(f"Deleting employee ID: {employee_id} from database...")
        if self._execute_query(query, (employee_id,)):
            self.account_deleted.emit(employee_id)
        else:
            print("Failed to delete employee.")

    def close_connection(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

# --- End of Database Worker ---


# --- Start of AccountSettingsPage Class ---
class AccountSettingsPage(QWidget):
    """
    A QWidget that encapsulates the entire Account Settings content,
    including employee list, create account form, and edit account form.
    """
    def __init__(self, db_manager, user_id, parent=None):
        super().__init__(parent)
        self.setObjectName("accountSettingsPage") # For QSS targeting

        self.db_manager = db_manager
        self.user_id = user_id # Passed for display, not directly used in DB path anymore

        self.current_selected_employee = None # To store data of the currently selected employee

        self._setup_ui()
        self._connect_db_manager_signals() # Connect signals from db_manager

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
        employee_list_container = QWidget()
        employee_list_container_layout = QVBoxLayout(employee_list_container)
        employee_list_container_layout.setContentsMargins(0, 0, 0, 0) # No extra margins

        # Add the Load Employees button
        self.load_employees_button = QPushButton("Load Employee List")
        self.load_employees_button.setObjectName("primaryButton") # Use primary button style
        self.load_employees_button.clicked.connect(self._request_load_employees)
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

    def _connect_db_manager_signals(self):
        """Connects signals from the DatabaseManager to slots in this page."""
        self.db_manager.employees_loaded.connect(self._populate_employee_list)
        self.db_manager.account_created.connect(self._handle_account_created)
        self.db_manager.account_updated.connect(self._handle_account_updated)
        self.db_manager.account_deleted.connect(self._handle_account_deleted)
        self.db_manager.error.connect(self._handle_db_error)

    # --- Slots to receive signals from DatabaseManager ---
    def _request_load_employees(self):
        """Requests DatabaseManager to load employees."""
        self.load_employees_button.setEnabled(False)
        self.load_employees_button.setText("Loading...")
        if self.initial_message_label:
            self.initial_message_label.hide()
        self._clear_employee_cards()
        self.db_manager.load_employees() # Call method on worker thread

    def _populate_employee_list(self, employees):
        """Populates the employee list UI with data received from DatabaseManager."""
        if not employees:
            self.initial_message_label.setText("No employees found.")
            self.initial_message_label.show()
            QMessageBox.information(self, "Load Status", "No employee data found in the database.")
        else:
            for emp in employees:
                card = self._create_employee_card_widget(emp)
                card.mousePressEvent = lambda event, e=emp, c=card: self._on_employee_card_clicked(e, c)
                self.employee_cards_layout.insertWidget(self.employee_cards_layout.count() - 1, card)
                self.employee_cards.append(card)
            QMessageBox.information(self, "Load Status", f"Successfully loaded {len(employees)} employees.")
        
        self.load_employees_button.setEnabled(True)
        self.load_employees_button.setText("Reload Employee List")

    def _handle_account_created(self, new_employee_data):
        """Handles successful account creation."""
        QMessageBox.information(self, "Account Created", f"Account for {new_employee_data['username']} created successfully!")
        # Clear form fields
        self.create_first_name_input.clear()
        self.create_last_name_input.clear()
        self.create_username_input.clear()
        self.create_password_input.clear()
        self.create_confirm_password_input.clear()
        self.create_admin_checkbox.setChecked(False)
        # Refresh the list
        self._request_load_employees()

    def _handle_account_updated(self, updated_employee_data):
        """Handles successful account update."""
        QMessageBox.information(self, "Changes Saved", f"Changes for {updated_employee_data['username']} saved successfully!")
        # Refresh the list and clear edit form
        self._request_load_employees()
        self._reset_edit_form()

    def _handle_account_deleted(self, deleted_id):
        """Handles successful account deletion."""
        QMessageBox.information(self, "Account Deleted", f"Account (ID: {deleted_id[:8]}...) deleted successfully!")
        # Refresh the list and clear edit form
        self._request_load_employees()
        self._reset_edit_form()

    def _handle_db_error(self, error_message):
        """Handles errors reported by the DatabaseManager."""
        QMessageBox.critical(self, "Database Error", error_message)
        self.load_employees_button.setEnabled(True)
        self.load_employees_button.setText("Load Employee List")
        if self.initial_message_label:
            self.initial_message_label.setText("Error loading data. Please try again.")
            self.initial_message_label.show()


    def _clear_employee_cards(self):
        """
        Helper function to clear all employee cards from the layout.
        """
        # Ensure we don't remove the stretch item which is always at the end (index -1)
        # Iterate from the element before the stretch item (which is at layout.count() - 1)
        # down to the first widget (index 0).
        for i in reversed(range(self.employee_cards_layout.count() - 1)):
            item = self.employee_cards_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    self.employee_cards_layout.removeWidget(widget)
                    widget.deleteLater() # Important to properly delete the widget
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
        
        # Display ID for debugging/identification purposes (optional in final app)
        card_layout.addWidget(QLabel(f"<small>ID: {employee_data.get('id', 'N/A')[:8]}...</small>")) # Show truncated ID
        card_layout.addWidget(QLabel(f"<b>First Name:</b> {employee_data.get('first_name', 'N/A')}"))
        card_layout.addWidget(QLabel(f"<b>Last Name:</b> {employee_data.get('last_name', 'N/A')}"))
        card_layout.addWidget(QLabel(f"<b>Username:</b> {employee_data.get('username', 'N/A')}"))
        card_layout.addWidget(QLabel(f"<b>Access Level:</b> {employee_data.get('access_level', 'N/A')}"))
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
        self.create_account_button.clicked.connect(self._create_new_account_request)
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

        # Buttons for Save and Delete
        button_layout = QHBoxLayout()
        self.save_changes_button = QPushButton("Save Changes")
        self.save_changes_button.setObjectName("primaryButton")
        self.save_changes_button.clicked.connect(self._save_changes_request)
        self.save_changes_button.setEnabled(False) # Disable until an employee is selected
        button_layout.addWidget(self.save_changes_button)

        self.delete_account_button = QPushButton("Delete Account")
        self.delete_account_button.setObjectName("secondaryButton") # Use secondary style
        self.delete_account_button.setStyleSheet("background-color: #e74c3c;") # Red for delete
        self.delete_account_button.clicked.connect(self._delete_employee_request)
        self.delete_account_button.setEnabled(False) # Disable until an employee is selected
        button_layout.addWidget(self.delete_account_button)

        layout.addLayout(button_layout)
        layout.addStretch() # Push content to top

        return frame

    def _reset_edit_form(self):
        """Resets the edit account form to its initial state."""
        self.current_selected_employee = None
        for card in self.employee_cards:
            card.setProperty("selected", False)
            card.style().polish(card)
        self.edit_first_name_input.clear()
        self.edit_last_name_input.clear()
        self.edit_username_input.clear()
        self.edit_access_level_combobox.setCurrentIndex(0) # Reset to default
        self.save_changes_button.setEnabled(False)
        self.delete_account_button.setEnabled(False)


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
        self.edit_first_name_input.setText(employee_data.get('first_name', ''))
        self.edit_last_name_input.setText(employee_data.get('last_name', ''))
        self.edit_username_input.setText(employee_data.get('username', ''))
        # Set the current access level in the combobox
        index = self.edit_access_level_combobox.findText(employee_data.get('access_level', 'Employee'))
        if index != -1:
            self.edit_access_level_combobox.setCurrentIndex(index)

        self.save_changes_button.setEnabled(True) # Enable save button
        self.delete_account_button.setEnabled(True) # Enable delete button
        self.current_selected_employee = employee_data # Store for saving changes

    def _create_new_account_request(self):
        """Validates input and requests DatabaseManager to create a new account."""
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

        new_employee_data = {
            "first": first_name,
            "last": last_name,
            "username": username,
            "access": "Admin" if is_admin else "Employee",
            # Note: Password handling should be done securely on a backend server, not here.
        }
        self.db_manager.add_employee(new_employee_data) # Request add to worker thread

    def _save_changes_request(self):
        """Validates input and requests DatabaseManager to save changes."""
        if not self.current_selected_employee:
            QMessageBox.warning(self, "Selection Error", "No employee selected for editing.")
            return

        employee_id = self.current_selected_employee.get('id')
        if not employee_id:
            QMessageBox.critical(self, "Error", "Selected employee has no ID. Cannot update.")
            return

        new_first_name = self.edit_first_name_input.text().strip()
        new_last_name = self.edit_last_name_input.text().strip()
        new_username = self.edit_username_input.text().strip()
        new_access_level = self.edit_access_level_combobox.currentText()

        if not (new_first_name and new_last_name and new_username):
            QMessageBox.warning(self, "Input Error", "First Name, Last Name, and Username cannot be empty.")
            return

        updated_employee_data = {
            "first": new_first_name,
            "last": new_last_name,
            "username": new_username,
            "access": new_access_level,
        }
        self.db_manager.update_employee(employee_id, updated_employee_data) # Request update to worker thread


    def _delete_employee_request(self):
        """Confirms and requests DatabaseManager to delete an employee."""
        if not self.current_selected_employee:
            QMessageBox.warning(self, "Selection Error", "No employee selected for deletion.")
            return

        employee_id = self.current_selected_employee.get('id')
        username = self.current_selected_employee.get('username')

        if not employee_id:
            QMessageBox.critical(self, "Error", "Selected employee has no ID. Cannot delete.")
            return

        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete account for '{username}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.db_manager.delete_employee(employee_id) # Request delete to worker thread
        else:
            print("Deletion cancelled.")


    def _change_password(self):
        """
        Placeholder for initiating a password change process.
        """
        if not self.current_selected_employee:
            QMessageBox.warning(self, "Selection Error", "No employee selected to change password.")
            return
        
        QMessageBox.information(self, "Change Password", 
                                f"Initiating password change for {self.current_selected_employee.get('username', 'N/A')}. "
                                "This would typically open a new dialog.")
# --- End of AccountSettingsPage Class ---


# --- Start of Placeholder Page Classes ---
class SystemConfigurationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("placeholderPage")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel("<h1>System Configuration Content</h1>"))
        layout.addWidget(QLabel("This is where system-wide configurations would go."))

class DatabaseMaintenancePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("placeholderPage")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel("<h1>Database Maintenance</h1>"))
        layout.addWidget(QLabel("Perform database backups, optimizations, and other maintenance tasks here."))

class SecuritySettingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("placeholderPage")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel("<h1>Security Settings</h1>"))
        layout.addWidget(QLabel("Configure user roles, permissions, and security policies."))
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

        self.user_id = "your_authenticated_user" # Placeholder for user ID
        self._auth_ready = False # Flag to indicate when DB connection is ready

        # 1. Setup Database Thread and Manager
        self.db_thread = QThread()
        self.db_manager = DatabaseManager(DB_CONFIG)
        self.db_manager.moveToThread(self.db_thread)

        # Connect thread start/stop signals
        self.db_thread.started.connect(self.db_manager.create_employees_table)
        self.db_thread.finished.connect(self.db_manager.close_connection)

        # Connect error signal from DB manager to main window
        self.db_manager.error.connect(self._handle_db_error_from_thread)

        self.db_thread.start() # Start the database thread

        self._setup_ui()
        self._apply_styles()

        # After thread starts and table is created, set auth_ready.
        # In a real app, this might depend on a login process.
        # For this demo, we'll assume it's ready after thread starts.
        QTimer.singleShot(1000, self._set_auth_ready) # Give DB thread time to initialize

    def _set_auth_ready(self):
        """Sets the authentication ready flag and enables nav buttons."""
        self._auth_ready = True
        self.logged_in_label.setText(f"Logged in as <b>{self.user_id[:8]}...</b>")
        for btn in self.nav_buttons.values():
            btn.setEnabled(True)
        # Set initial page and active button after auth is ready
        initial_nav_button_text = "ACCOUNT SETTINGS"
        self.nav_buttons[initial_nav_button_text].setProperty("active", True)
        self.nav_buttons[initial_nav_button_text].style().polish(self.nav_buttons[initial_nav_button_text])
        self.main_title_label.setText(initial_nav_button_text)
        self.stacked_content_widget.setCurrentIndex(0)


    def _handle_db_error_from_thread(self, error_message):
        QMessageBox.critical(self, "Database Error", f"An error occurred in the database thread: {error_message}")


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

        self.logged_in_label = QLabel("Connecting to database...") # Initial message
        self.logged_in_label.setObjectName("loggedInLabel")
        self.logged_in_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sidebar_layout.addWidget(self.logged_in_label)

        self.sidebar_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Navigation buttons and their corresponding page instances/indices
        self.nav_buttons = {}
        # Pages are now initialized with the db_manager
        self.stacked_content_widget = QStackedWidget() # The QStackedWidget for main content

        # Create actual page instances, passing the db_manager
        self.account_settings_page = AccountSettingsPage(self.db_manager, self.user_id)
        self.system_config_page = SystemConfigurationPage()
        self.db_maintenance_page = DatabaseMaintenancePage()
        self.security_settings_page = SecuritySettingPage()

        # Add pages to stacked widget in order
        self.stacked_content_widget.addWidget(self.account_settings_page) # Index 0
        self.stacked_content_widget.addWidget(self.system_config_page) # Index 1
        self.stacked_content_widget.addWidget(self.db_maintenance_page) # Index 2
        self.stacked_content_widget.addWidget(self.security_settings_page) # Index 3

        nav_items_order = [
            "ACCOUNT SETTINGS",
            "SYSTEM CONFIGURATION",
            "DATABASE MAINTENANCE",
            "SECURITY SETTINGS"
        ]

        # Initially disable navigation until DB connection is ready
        self._create_nav_buttons(nav_items_order, enabled=False)

        self.sidebar_layout.addStretch() # Pushes content to the top

        # 2. Main Content Area
        self.content_area_container = QWidget()
        self.content_area_layout = QVBoxLayout(self.content_area_container)
        self.content_area_layout.setContentsMargins(40, 30, 40, 30)
        self.content_area_layout.setSpacing(25)

        self.main_title_label = QLabel("Connecting to Database...") # Initial title
        self.main_title_label.setObjectName("mainTitleLabel")
        self.content_area_layout.addWidget(self.main_title_label)

        # Add the QStackedWidget to the main content area
        self.content_area_layout.addWidget(self.stacked_content_widget)
        self.content_area_layout.addStretch()

        # Add parts to main layout
        self.main_layout.addWidget(self.sidebar_frame)
        self.main_layout.addWidget(self.content_area_container)

    def _create_nav_buttons(self, nav_items_order, enabled=True):
        """Creates or re-creates navigation buttons."""
        # Remove old buttons if they exist
        for i in reversed(range(self.sidebar_layout.count())):
            item = self.sidebar_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QPushButton) and "navButton_" in item.widget().objectName():
                widget = item.widget()
                self.sidebar_layout.removeWidget(widget)
                widget.deleteLater() # Safely delete the widget

        self.nav_buttons.clear()
        for i, text in enumerate(nav_items_order):
            btn = QPushButton(text)
            btn.setObjectName(f"navButton_{text.replace(' ', '')}") # For QSS
            btn.setEnabled(enabled)
            btn.clicked.connect(lambda checked, idx=i, b=btn: self._on_nav_button_clicked(idx, b))
            self.nav_buttons[text] = btn
            # Insert after logged_in_label and spacer (indices 0 and 1)
            self.sidebar_layout.insertWidget(2 + i, btn)

    def _on_nav_button_clicked(self, index, clicked_button):
        """
        Handles navigation button clicks, switching the QStackedWidget page
        and updating button active states.
        """
        if not self._auth_ready:
            QMessageBox.warning(self, "Initialization Pending", "Please wait while the application connects to the database.")
            return

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
            
            QPushButton:disabled {
                background-color: #5a6d7f; /* Darker gray for disabled nav buttons */
                color: #b0bec5;
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

            /* Primary Button (Green) */
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

            /* Secondary Button (Gray) */
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
            #secondaryButton:disabled {
                background-color: #cccccc;
                color: #666666;
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
    app = QApplication(sys.argv)

    # Set default font for consistency (optional)
    font = QFont("Arial", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(window.db_thread.wait()) # Ensure database thread finishes on app exit
