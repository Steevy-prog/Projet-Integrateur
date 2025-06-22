import sys
import psycopg2
from psycopg2 import Error
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QCheckBox, QFrame, QScrollArea,
    QSizePolicy, QSpacerItem, QGridLayout, QMessageBox, QComboBox, QStackedWidget
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

# --- Database Connection Details ---
# IMPORTANT: In a real application, fetch these from environment variables or a secure config.
host = "dpg-d1b612gdl3ps73eapfr0-a.oregon-postgres.render.com"
database = "test_bpdd"
user = "test"
password = "w95g3tjqj0S9DLwNiaFEMb1SACWuuIjh"
port = 5432

db_connection = None
try:
    db_connection = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port
    )
    # Ensure autocommit is off for transaction control
    db_connection.autocommit = False
    print(f"Successfully connected to PostgreSQL database: {database}")
except Error as e:
    print(f"Error connecting to PostgreSQL database: {e}")
    # Exit if connection fails
    # In a real app, you might want to handle this more gracefully (e.g., disable DB-dependent features)
    sys.exit(1) # Exit if database connection fails at startup

def extract_employee_data(connection):
    """
    Extracts employee data from the database.
    Handles potential 'User' reserved keyword issue by quoting "Users".
    """
    try:
        cursor = connection.cursor()
        # Changed to "Users" to avoid PostgreSQL reserved keyword conflict
        query = 'SELECT first_name, last_name, username, access_level FROM "Users"'
        cursor.execute(query)
        rows = cursor.fetchall()
        employee_data = []
        for row in rows:
            employee = {
                "first_name": row[0],
                "last_name": row[1],
                "username": row[2],
                "access_level": row[3],
            }
            employee_data.append(employee)
        return employee_data
    except Error as e:
        print(f"Error extracting user data: {e}")
        return []
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()

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

        # 1. Employee Account List Section (Left Column)
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

        # 2. Right Column Container with Scroll Area
        right_column_container = QWidget()
        right_column_layout = QVBoxLayout(right_column_container)
        right_column_layout.setContentsMargins(0, 0, 0, 0)
        right_column_layout.setSpacing(25) # Spacing between create, edit, delete sections

        # Add Create New Account Section
        self.create_account_frame = self._create_create_account_section()
        right_column_layout.addWidget(self.create_account_frame)

        # Add Edit Employee Account Section
        self.edit_account_frame = self._create_edit_account_section()
        right_column_layout.addWidget(self.edit_account_frame)

        # Add Delete Employee Account Section
        self.delete_account_frame = self._create_delete_account_section()
        right_column_layout.addWidget(self.delete_account_frame)

        right_column_layout.addStretch() # Push sections to the top within the scroll area

        # Wrap the right column content in a QScrollArea
        right_scroll_area = QScrollArea()
        right_scroll_area.setWidgetResizable(True)
        right_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_scroll_area.setWidget(right_column_container)
        right_scroll_area.setObjectName("rightScrollArea") # For QSS

        # Add the scroll area to the grid layout, spanning 2 rows (like the list)
        self.content_grid_layout.addWidget(right_scroll_area, 0, 1, 2, 1) # Row 0, Col 1, Span 2 rows

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
        Loads employee data from the database.
        This method is connected to the "Load Employee List" button.
        """
        self.load_employees_button.setEnabled(False) # Disable button during loading
        self.load_employees_button.setText("Loading...")

        # Hide initial message
        if self.initial_message_label:
            self.initial_message_label.hide()

        # Clear existing cards before loading new data
        self._clear_employee_cards()

        # Perform the actual database query
        employees = extract_employee_data(db_connection)

        if not employees:
            self.initial_message_label.setText("No employees found.")
            self.initial_message_label.show()
            QMessageBox.information(self, "Load Status", "No employee data found in the database.")
        else:
            for emp in employees:
                card = self._create_employee_card_widget(emp)
                # Store the raw employee data directly on the card widget using setProperty
                card.setProperty("employeeData", emp)
                card.mousePressEvent = lambda event, c=card: self._on_employee_card_clicked(event, c)
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
                widget.deleteLater() # Schedule for deletion
        self.employee_cards.clear()
        # Ensure initial message is hidden if we're clearing to load new data
        if self.initial_message_label:
            self.initial_message_label.hide()


    def is_employee_present(self, username):
        """
        Checks if an employee with the given username already exists in the database.
        Returns True if present, False otherwise.
        """
        try:
            cursor = db_connection.cursor()
            # Quoting "Users" table name
            query = 'SELECT username FROM "Users" WHERE username = %s'
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            cursor.close()

            if result:
                return True # Employee exists
        except Error as e:
            print(f"Error checking for existing employee: {e}")
            QMessageBox.critical(self, "Database Error", "Failed to check for existing employee in the database.")
        return False

    def add_employee_to_db(self, first_name, last_name, username, access_level):
        """
        Adds a new employee to the database.
        """
        try:
            cursor = db_connection.cursor()
            # Quoting "Users" table name
            insert_query = """
                INSERT INTO "Users" (first_name, last_name, username, access_level)
                VALUES (%s, %s, %s, %s);
            """
            cursor.execute(insert_query, (first_name, last_name, username, access_level))
            db_connection.commit()
            print(f"Employee {username} added successfully.")
            return True # Indicate success
        except Error as e:
            print(f"Error adding employee: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to add employee: {e}")
            db_connection.rollback() # Rollback on error
            return False # Indicate failure
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def update_employee_in_db(self, original_username, first_name, last_name, username, access_level):
        """
        Updates an existing employee's details in the database.
        """
        try:
            cursor = db_connection.cursor()
            # Quoting "Users" table name
            update_query = """
                UPDATE "Users"
                SET first_name = %s, last_name = %s, username = %s, access_level = %s
                WHERE username = %s;
            """
            cursor.execute(update_query, (first_name, last_name, username, access_level, original_username))
            db_connection.commit()
            print(f"Employee {username} updated successfully.")
            return True # Indicate success
        except Error as e:
            print(f"Error updating employee: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to update employee: {e}")
            db_connection.rollback() # Rollback on error
            return False # Indicate failure
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def delete_employee_from_db(self, username):
        """
        Deletes an employee from the database.
        """
        try:
            cursor = db_connection.cursor()
            # Quoting "Users" table name
            delete_query = 'DELETE FROM "Users" WHERE username = %s;'
            cursor.execute(delete_query, (username,))
            db_connection.commit()
            print(f"Employee {username} deleted successfully.")
            return True # Indicate success
        except Error as e:
            print(f"Error deleting employee: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to delete employee: {e}")
            db_connection.rollback() # Rollback on error
            return False # Indicate failure
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()


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
        card_layout.addWidget(QLabel(f"<b>First Name:</b> {employee_data['first_name']}"))
        card_layout.addWidget(QLabel(f"<b>Last Name:</b> {employee_data['last_name']}"))
        # Using setProperty for raw username data
        username_label = QLabel(f"<b>Username:</b> {employee_data['username']}")
        username_label.setObjectName("username") # For findChild in other places if needed
        username_label.setProperty("rawUsername", employee_data['username']) # Store raw username
        card_layout.addWidget(username_label)
        card_layout.addWidget(QLabel(f"<b>Access Level:</b> {employee_data['access_level']}"))
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

        layout.addLayout(form_layout)

        self.save_changes_button = QPushButton("Save Changes")
        self.save_changes_button.setObjectName("primaryButton")
        self.save_changes_button.clicked.connect(self._save_changes)
        self.save_changes_button.setEnabled(False) # Disable until an employee is selected
        layout.addWidget(self.save_changes_button)

        layout.addStretch() # Push content to top

        return frame

    def _create_delete_account_section(self):
        """
        Creates and returns the QFrame for the Delete Employee Account section.
        """
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Delete Employee Account")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        self.delete_info_label = QLabel("Select an employee from the list to delete.")
        layout.addWidget(self.delete_info_label)

        self.delete_username_display = QLineEdit()
        self.delete_username_display.setPlaceholderText("Selected Username for Deletion")
        self.delete_username_display.setReadOnly(True) # Make it read-only
        layout.addWidget(self.delete_username_display)

        self.delete_account_button = QPushButton("Delete Employee")
        self.delete_account_button.setObjectName("warningButton") # Custom style for delete button
        self.delete_account_button.clicked.connect(self._delete_account)
        self.delete_account_button.setEnabled(False) # Disable until an employee is selected
        layout.addWidget(self.delete_account_button)

        layout.addStretch()
        return frame


    # --- Event Handlers and Logic for AccountSettingsPage ---
    def _on_employee_card_clicked(self, event, clicked_card):
        """
        Handles the click event on an employee card.
        Populates the 'Edit Employee Account' and 'Delete Employee Account' sections
        with the selected employee's data.
        """
        # Retrieve the raw employee data stored on the card
        employee_data = clicked_card.property("employeeData")
        if not employee_data:
            print("Error: No employee data found on clicked card.")
            return

        print(f"Employee card clicked: {employee_data['username']}")

        # Clear previous selection style from all cards
        for card in self.employee_cards:
            card.setProperty("selected", False)
            card.style().polish(card) # Re-apply stylesheet to update visual state

        # Set new selection style for the clicked card
        clicked_card.setProperty("selected", True)
        clicked_card.style().polish(clicked_card) # Re-apply stylesheet

        # Populate the "Edit Employee Account" section's fields
        self.edit_first_name_input.setText(employee_data['first_name'])
        self.edit_last_name_input.setText(employee_data['last_name'])
        self.edit_username_input.setText(employee_data['username'])
        # Set the current access level in the combobox
        index = self.edit_access_level_combobox.findText(employee_data['access_level'])
        if index != -1:
            self.edit_access_level_combobox.setCurrentIndex(index)

        self.save_changes_button.setEnabled(True) # Enable save button
        self.current_selected_employee = employee_data # Store for saving changes

        # Populate the "Delete Employee Account" section's fields
        self.delete_username_display.setText(employee_data['username'])
        self.delete_account_button.setEnabled(True) # Enable delete button
        self.delete_info_label.setText(f"You have selected <b>{employee_data['username']}</b> for deletion.")


    def _create_new_account(self):
        """
        Handles the logic for creating a new account.
        """
        first_name = self.create_first_name_input.text().strip()
        last_name = self.create_last_name_input.text().strip()
        username = self.create_username_input.text().strip()
        password = self.create_password_input.text() # Passwords should be hashed!
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

        # Check if employee exists in DB
        if self.is_employee_present(username):
            QMessageBox.warning(self, "Duplicate Username", f"An employee with username '{username}' already exists in the database.")
            return

        access_level = "Admin" if is_admin else "Employee"
        if self.add_employee_to_db(first_name, last_name, username, access_level):
            QMessageBox.information(self, "Account Created", f"Account for {username} created successfully!")

            # Clear form fields after successful creation
            self.create_first_name_input.clear()
            self.create_last_name_input.clear()
            self.create_username_input.clear()
            self.create_password_input.clear()
            self.create_confirm_password_input.clear()
            self.create_admin_checkbox.setChecked(False)

            # Refresh employee list to show the newly added account
            self._load_employee_data_from_db()


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

        # Check for username change and if new username already exists
        if new_username != original_username and self.is_employee_present(new_username):
            QMessageBox.warning(self, "Duplicate Username", f"The new username '{new_username}' already exists for another employee.")
            return

        if self.update_employee_in_db(original_username, new_first_name, new_last_name, new_username, new_access_level):
            QMessageBox.information(self, "Changes Saved", f"Changes for {new_username} saved successfully!")

            # Refresh the employee list to reflect changes
            self._load_employee_data_from_db()

            # After saving, clear selection and reset edit & delete forms
            self._clear_selection_and_forms()

    def _delete_account(self):
        """
        Handles the logic for deleting an employee account.
        """
        if not self.current_selected_employee:
            QMessageBox.warning(self, "Selection Error", "No employee selected for deletion.")
            return

        username_to_delete = self.current_selected_employee['username']

        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete the account for <b>{username_to_delete}</b>?\n\n"
                                     "This action cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.delete_employee_from_db(username_to_delete):
                QMessageBox.information(self, "Account Deleted", f"Account for {username_to_delete} deleted successfully!")

                # Refresh the employee list to reflect deletion
                self._load_employee_data_from_db()

                # Clear selection and reset edit & delete forms
                self._clear_selection_and_forms()
        else:
            QMessageBox.information(self, "Deletion Canceled", "Employee account deletion was canceled.")

    def _clear_selection_and_forms(self):
        """
        Resets the UI state after an edit or delete operation.
        """
        self.current_selected_employee = None
        for card in self.employee_cards:
            card.setProperty("selected", False)
            card.style().polish(card)

        # Clear Edit form
        self.edit_first_name_input.clear()
        self.edit_last_name_input.clear()
        self.edit_username_input.clear()
        self.edit_access_level_combobox.setCurrentIndex(0) # Reset to default
        self.save_changes_button.setEnabled(False)

        # Clear Delete form
        self.delete_username_display.clear()
        self.delete_account_button.setEnabled(False)
        self.delete_info_label.setText("Select an employee from the list to delete.")


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
            #sectionFrame {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
            }
            #accountSettingsPage, #placeholderPage {
                 background-color: transparent; /* Main page background from QMainWindow */
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

            #warningButton { /* New style for delete button */
                background-color: #e74c3c; /* Red */
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
                margin-top: 15px;
                text-align: center;
            }
            #warningButton:hover {
                background-color: #c0392b;
            }

            QScrollArea {
                border: none; /* No border for the scroll area itself */
            }
            QScrollBar:vertical {
                border: 1px solid #999;
                background: #f0f0f0;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

            #rightScrollArea {
                background-color: transparent; /* Important for scroll area background */
                border: none;
            }
            #employeeListScrollArea {
                border: none;
            }
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())