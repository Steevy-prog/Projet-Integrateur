import sys
import re
import rstr
import psycopg2
from psycopg2 import Error
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QCheckBox, QFrame, QScrollArea,
    QSizePolicy, QSpacerItem, QGridLayout, QMessageBox, QComboBox, QStackedWidget,
    QTableWidgetItem,
    QTableWidget,
    QHeaderView,
    QTextEdit,
    QSplitter,
    QSpinBox,
    QAbstractItemView,
    QFileDialog
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QDir, QObject, QThread
from PyQt6.QtGui import QFont, QColor, QPalette

from terminal import TerminalPage, AutomationPage
from db_connection import db_connection


class AccountSettingsPage(QWidget):
    """
    A QWidget that encapsulates the entire Account Settings content,
    including employee list, create account form, and edit account form.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("accountSettingsPage")
        self.current_selected_employee = None
        self.password_policy = {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_number": True,
            "require_special": True,
            "enforce_expiration": False,
            "password_expiration_days": 0
        }
        self.db_connection = db_connection
        self.state = False
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(25)
        self.content_grid_layout = QGridLayout()
        self.content_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.content_grid_layout.setSpacing(30)
        employee_list_container = QWidget()
        employee_list_container_layout = QVBoxLayout(employee_list_container)
        employee_list_container_layout.setContentsMargins(0, 0, 0, 0)
        self.individual_select_frame = self._create_individual_frame()
        employee_list_container_layout.addWidget(self.individual_select_frame)
        self.load_employees_button = QPushButton("Load Employee List")
        self.load_employees_button.setStyleSheet("margin-top: 30px;")
        self.load_employees_button.setObjectName("primaryButton")
        self.load_employees_button.clicked.connect(self._load_employee_data_from_db)
        employee_list_container_layout.addWidget(self.load_employees_button)
        employee_list_container_layout.addSpacing(10)
        self.employee_list_frame = self._create_employee_list_section()
        employee_list_container_layout.addWidget(self.employee_list_frame)
        self.content_grid_layout.addWidget(employee_list_container, 0, 0, 2, 1)
        right_column_container = QWidget()
        right_column_layout = QVBoxLayout(right_column_container)
        right_column_layout.setContentsMargins(0, 0, 0, 0)
        right_column_layout.setSpacing(25)
        self.create_account_frame = self._create_create_account_section()
        right_column_layout.addWidget(self.create_account_frame)
        self.edit_account_frame = self._create_edit_account_section()
        right_column_layout.addWidget(self.edit_account_frame)
        self.delete_account_frame = self._create_delete_account_section()
        right_column_layout.addWidget(self.delete_account_frame)
        right_column_layout.addStretch()
        right_scroll_area = QScrollArea()
        right_scroll_area.setWidgetResizable(True)
        right_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        right_scroll_area.setWidget(right_column_container)
        right_scroll_area.setObjectName("rightScrollArea")
        self.content_grid_layout.addWidget(right_scroll_area, 0, 1, 2, 1)
        self.main_layout.addLayout(self.content_grid_layout)
        self._load_password_policy()

    def generate_id(self, pattern: str, existing_ids: list[str]) -> str:
        """
        Generate a random string that matches the given regex pattern.
        Example pattern: '[A-Z]{3}[0-9]{4}'
        """
        try:
            new_id = rstr.xeger(pattern)
            while new_id in existing_ids:
                new_id = rstr.xeger(pattern)
            return new_id
        except Exception as e:
            QMessageBox.information(self, "Error", f"{e}")
            return None
        
    def extract_employee_data(self, connection):
        try:
            cursor = connection.cursor()
            query = f"SELECT nom, prenom, username, email, niveau_acces, idutilisateur FROM \"EMIR\".lister_utilisateurs()"
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            employee_data = []
            for row in rows:
                employee = {
                    "first_name": row[0],
                    "last_name": row[1],
                    "username": row[2],
                    "email": row[3],
                    "access_level": row[4],
                    "id": row[5]
                }
                employee_data.append(employee)
            return employee_data
        except Error as e:
            QMessageBox.warning(self,"Error", f"Error extracting user data: {e}")
            db_connection.rollback()
            if cursor:
                cursor.close()
            return []
    
    def refresh_individual_list(self):
        self.combobox_refresh_button.setEnabled(False)
        try: 
            self.combobox_refresh_button.setText("Loading...")
            data_set  = self.get_individual_data()
            self.individual_combobox.clear()
            for item in data_set:
                self.individual_combobox.addItem(item)
            if data_set:
                self.create_account_button.setEnabled(True)
            self.combobox_refresh_button.setEnabled(True)
            self.combobox_refresh_button.setText("Reload Individual List")
            
        except Exception as e:
            QMessageBox.information(self, "Refresh Error", f"{e}")
            self.combobox_refresh_button.setEnabled(True)
            self.combobox_refresh_button.setText("Reload Individual List")
    
    
    def get_individual_data(self):
        try:
            if db_connection:
                cursor = db_connection.cursor()
                query = "SELECT id, first_name, last_name FROM \"EMIR\".getnameandid()"
                cursor.execute(query)
                results = cursor.fetchall()
                cursor.close()
                data = []
                self.create_data = []
                if results:   
                    for result in results:
                        line = f"{result[1]} {result[2]} {result[0]}"
                        self.create_data.append(line)
                        data.append(f"{result[1]} {result[2]}")
                    return data
                else:
                    return []
        except Exception as e:
            db_connection.rollback()
            if cursor:
                cursor.close()
            QMessageBox.critical(self, "Database Error", f"Fail to get Individuals' data from the database \n{e}")
        
    
    def _create_individual_frame(self):
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        title = QLabel("Individual's Selection")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        self.individual_combobox = QComboBox()
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        
        form_layout.addWidget(QLabel("Individual"), 0, 0)
        form_layout.addWidget(self.individual_combobox, 1, 0)
        
        layout.addLayout(form_layout)
        
        self.combobox_refresh_button = QPushButton("Load Individual List")
        self.combobox_refresh_button.setObjectName("primaryButton")
        self.combobox_refresh_button.clicked.connect(self.refresh_individual_list)
        layout.addWidget(self.combobox_refresh_button)
        
        return frame
        
        
    def _create_employee_list_section(self):
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        title = QLabel("Employee Account List")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setObjectName("employeeListScrollArea")
        scroll_content = QWidget()
        self.employee_cards_layout = QVBoxLayout(scroll_content)
        self.employee_cards_layout.setContentsMargins(0,0,0,0)
        self.employee_cards_layout.setSpacing(10)
        self.employee_cards = []
        self.initial_message_label = QLabel("Click 'Load Employee List' to retrieve data.")
        self.initial_message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.initial_message_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 20px;")
        self.employee_cards_layout.addWidget(self.initial_message_label)
        self.employee_cards_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        return frame

    def _load_employee_data_from_db(self):
        self.load_employees_button.setEnabled(False)
        self.load_employees_button.setText("Loading...")
        if self.initial_message_label:
            self.initial_message_label.hide()
        self._clear_employee_cards()
        QTimer.singleShot(1500, self._populate_employee_list)

    def _populate_employee_list(self):
        employees = self.extract_employee_data(db_connection)
        if not employees:
            self.initial_message_label.setText("No employees found.")
            self.initial_message_label.show()
            QMessageBox.information(self, "Load Status", "No employee data found in the database.")
            self.load_employees_button.setEnabled(True)
            self.load_employees_button.setText("Reload Employee List")
            return
        for emp in employees:
            card = self._create_employee_card_widget(emp)
            card.mousePressEvent = lambda event, e=emp, c=card: self._on_employee_card_clicked(e, c)
            self.employee_cards_layout.insertWidget(self.employee_cards_layout.count() - 1, card)
            self.employee_cards.append(card)
        QMessageBox.information(self, "Load Status", f"Successfully loaded {len(employees)} employees.")
        self.load_employees_button.setEnabled(True)
        self.load_employees_button.setText("Reload Employee List")

    def _clear_employee_cards(self):
        while self.employee_cards_layout.count() > 1:
            item = self.employee_cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self.employee_cards.clear()

    def is_employee_present(self, username):
        try:

            cursor = db_connection.cursor()
            query = f"SELECT * FROM \"EMIR\".lister_utilisateurs() WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            db_connection.commit()
            cursor.close()
            if result:
                return True
            else:
                return False
        except Exception as e:
            db_connection.rollback()
            if cursor:
                cursor.close()
            QMessageBox.critical(self, "Database Error", f"Failed to check for existing employee in the database.\n {e}")

        

    def add_employee_to_db(self, id, first_name, last_name, username, email, password, access_level):
        try:
           
            cursor = db_connection.cursor()
            insert_query = f"SELECT \"EMIR\".inscrire_utilisateur (%s, %s, %s, %s, %s, %s, %s);"
            cursor.execute(insert_query, (id, username, first_name, last_name, email, password, access_level,))
            db_connection.commit()
            self.state = True
            cursor.close()
        except Exception as e:
            db_connection.rollback()
            if cursor:
                cursor.close()
            QMessageBox.warning(self, "Database Error", f"Error adding employee: {e}")
            self.state = False

    
    def update_employee_in_db(self, original_username, first_name, last_name, username, access_level, email):
        password = first_name + last_name + "mmMM@@7777"
        try:
            cursor = db_connection.cursor()
            update_query = f"""
                CALL "EMIR".Modifier_utilisateur(
            usernameanc    => %s,
            usernamenouv   => %s,
            nom            => %s,
            prenom         => %s,
            email          => %s,
            _niveau_acces  => %s,
            _mot_de_passe  => %s
            """
            cursor.execute(update_query, (original_username, username, first_name, last_name, email, access_level, password,))
            db_connection.commit()
            cursor.close()
            QMessageBox.information(f"Employee {username} updated successfully.")
        except Error as e:
            db_connection.rollback()
            if cursor:
                cursor.close()
            QMessageBox.warning(self, "Database Error", f"Error updating employee: {e}")


    def _delete_account(self):
        if not self.current_selected_employee:
            QMessageBox.warning(self, "Selection Error", "No employee selected for deletion.")
            return
        username_to_delete = self.current_selected_employee['username']
        reply = QMessageBox.question(
            self, 'Confirm Deletion',
            f"Are you sure you want to delete the account for <b>{username_to_delete}</b>?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.delete_employee_from_db(username_to_delete):
                QMessageBox.information(self, "Account Deleted", f"Account for {username_to_delete} deleted successfully!")
                self._load_employee_data_from_db()
                self._clear_selection_and_forms()
        else:
            QMessageBox.information(self, "Deletion Canceled", "Employee account deletion was canceled.")

    def delete_employee_from_db(self, username):
        try:
            cursor = db_connection.cursor()
            delete_query = f"SELECT \"EMIR\".supprimer_utilisateur({username});"
            cursor.execute(delete_query)
            db_connection.commit()
            cursor.close()
            return True
        except Error as e:
            db_connection.rollback()
            if cursor:
                cursor.close()
            QMessageBox.critical(self, "Database Error", f"Error deleting employee: {e}")
            return False
        

    def _clear_selection_and_forms(self):
        self.current_selected_employee = None
        for card in self.employee_cards:
            card.setProperty("selected", False)
            card.style().polish(card)
        self.edit_first_name_input.clear()
        self.edit_last_name_input.clear()
        self.edit_username_input.clear()
        self.edit_access_level_combobox.setCurrentIndex(0)
        self.edit_email_input.clear()
 
        self.edit_password_input.clear()
        self.save_changes_button.setEnabled(False)
        
        self.delete_first_name.clear()
        self.delete_last_name.clear()
        self.delete_username.clear()
        self.delete_access_level.clear()
        self.delete_email.clear()

        
        self.delete_account_button.setEnabled(False)

    def _create_employee_card_widget(self, employee_data):
        card_frame = QFrame()
        card_frame.setObjectName("employeeCard")
        card_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(15, 10, 15, 10)
        card_layout.setSpacing(5)
        card_layout.addWidget(QLabel(f"<b>First Name:</b> {employee_data['first_name']}"))
        card_layout.addWidget(QLabel(f"<b>Last Name:</b> {employee_data['last_name']}"))
        card_layout.addWidget(QLabel(f"<b>Username:</b> {employee_data['username']}"))
        card_layout.addWidget(QLabel(f"<b>Email:</b> {employee_data['email']}"))
        card_layout.addWidget(QLabel(f"<b>Access Level:</b> {employee_data['access_level']}"))
        return card_frame

    def _create_create_account_section(self):
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
        self.create_email_input = QLineEdit()
        self.create_access_level_combobox = QComboBox()
        self.create_access_level_combobox.addItems(["employee", "manager", "admin"])
        form_layout.addWidget(QLabel("First Name :"), 0, 0)
        form_layout.addWidget(self.create_first_name_input, 0, 1)
        form_layout.addWidget(QLabel("Last Name :"), 1, 0)
        form_layout.addWidget(self.create_last_name_input, 1, 1)
        form_layout.addWidget(QLabel("Username :"), 2, 0)
        form_layout.addWidget(self.create_username_input, 2, 1)
        form_layout.addWidget(QLabel("Email :"), 3, 0)
        form_layout.addWidget(self.create_email_input, 3, 1)

        form_layout.addWidget(QLabel("Access Level :"), 4, 0)
        form_layout.addWidget(self.create_access_level_combobox, 4, 1)
        layout.addLayout(form_layout)
        
        self.create_account_button = QPushButton("Create Account")
        self.create_account_button.setObjectName("primaryButton")
        self.create_account_button.clicked.connect(self._create_new_account)
        self.create_account_button.setEnabled(False)
        layout.addWidget(self.create_account_button)
        layout.addStretch()
        return frame

    def _create_edit_account_section(self):
        """
        To Modify
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
        self.edit_password_input = QLineEdit()
        self.edit_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit_first_name_input = QLineEdit()
        self.edit_last_name_input = QLineEdit()
        self.edit_username_input = QLineEdit()
        self.edit_email_input = QLineEdit()
        self.edit_access_level_combobox = QComboBox()
        self.edit_access_level_combobox.addItems(["employee", "manager", "admin"])
        form_layout.addWidget(QLabel("First Name :"), 0, 0)
        form_layout.addWidget(self.edit_first_name_input, 0, 1)
        form_layout.addWidget(QLabel("Last Name :"), 1, 0)
        form_layout.addWidget(self.edit_last_name_input, 1, 1)
        form_layout.addWidget(QLabel("Username :"), 2, 0)
        form_layout.addWidget(self.edit_username_input, 2, 1)
        form_layout.addWidget(QLabel("Email :"), 3, 0)
        form_layout.addWidget(self.edit_email_input, 3, 1)

        form_layout.addWidget(QLabel("Access Level :"), 4, 0)
        form_layout.addWidget(self.edit_access_level_combobox, 4, 1)
        
        layout.addLayout(form_layout)
        self.save_changes_button = QPushButton("Save Changes")
        self.save_changes_button.setObjectName("primaryButton")
        self.save_changes_button.clicked.connect(self._save_changes)
        self.save_changes_button.setEnabled(False)
        layout.addWidget(self.save_changes_button)
        layout.addStretch()
        return frame

    def _create_delete_account_section(self):
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        title = QLabel("Delete Employee Account")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        layout.addWidget(QLabel("Click on an employee card on the left to select an employee account."))
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        self.delete_first_name = QLabel()
        self.delete_last_name = QLabel()
        self.delete_username = QLabel()
        self.delete_access_level = QLabel()
        self.delete_email = QLabel()
        
        form_layout.addWidget(QLabel("First Name :"), 0, 0)
        form_layout.addWidget(self.delete_first_name, 0, 1)
        form_layout.addWidget(QLabel("Last Name :"), 1, 0)
        form_layout.addWidget(self.delete_last_name, 1, 1)
        form_layout.addWidget(QLabel("Username :"), 2, 0)
        form_layout.addWidget(self.delete_username, 2, 1)
        form_layout.addWidget(QLabel("Email :"), 3, 0)
        form_layout.addWidget(self.delete_email, 3, 1)
        form_layout.addWidget(QLabel("Access Level :"), 4, 0)
        form_layout.addWidget(self.delete_access_level, 4, 1)
        layout.addLayout(form_layout)
        self.delete_account_button = QPushButton("Delete Account")
        self.delete_account_button.setObjectName("deleteButton")
        self.delete_account_button.clicked.connect(self._delete_account)
        self.delete_account_button.setEnabled(False)
        layout.addWidget(self.delete_account_button)
        layout.addStretch()
        return frame

    def _on_employee_card_clicked(self, employee_data, clicked_card):
        for card in self.employee_cards:
            card.setProperty("selected", False)
            card.style().polish(card)
        clicked_card.setProperty("selected", True)
        clicked_card.style().polish(clicked_card)
        self.edit_first_name_input.setText(employee_data['first_name'])
        self.edit_last_name_input.setText(employee_data['last_name'])
        self.edit_username_input.setText(employee_data['username'])
        self.edit_email_input.setText(employee_data['email'])
        self.edit_access_level_combobox.setCurrentText(employee_data['access_level'])
        self.save_changes_button.setEnabled(True)
        
        self.delete_first_name.setText(employee_data['first_name'])
        self.delete_last_name.setText(employee_data['last_name'])
        self.delete_username.setText(employee_data['username'])
        self.delete_email.setText(employee_data['email'])
        self.delete_access_level.setText(employee_data['access_level'])
        self.delete_account_button.setEnabled(True)
        
        self.current_selected_employee = employee_data
    
    def is_email_valid(self, email):
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        if email_pattern.match(email):
            return True
        else:
            return False
    def _create_new_account(self):
        first_name = self.create_first_name_input.text().strip()
        last_name = self.create_last_name_input.text().strip()
        username = self.create_username_input.text().strip()
        password = f"{first_name.upper() + last_name.lower() + "mmMM@@7777"}"
        
        access_level = self.create_access_level_combobox.currentText()
        email = self.create_email_input.text().strip()
        text = self.individual_combobox.currentText().strip()
        for line in self.create_data:
            if text in line.strip():
                ID = line.split(' ')[2]
                break
        if not ID:
            QMessageBox.information(self, 'No ID', "No ID")
            return
        if self.is_employee_present(username):
            QMessageBox.warning(self, "Duplicate Username", f"An employee with username '{username}' already exists.")
            return
        if not (first_name and last_name and username and email):
            QMessageBox.warning(self, "Input Error", "All fields must be filled to create an account.")
            return
        if not self.is_email_valid(email):
            QMessageBox.warning(self, "Email Error", "Invalid email format.")
            return
        error_list = self._validate_password(password)
        error_message = ''
        if error_list:
            for error in error_list:
                error_message += error + f"\n"
            QMessageBox.warning(self, "Invalid Password", error_message)
            return
        
        self.add_employee_to_db(ID, first_name, last_name, username, email, password, access_level)
        if self.state:
            QMessageBox.information(self, "Account Created", f"Account for {username} created successfully!")
            self.create_first_name_input.clear()
            self.create_last_name_input.clear()
            self.create_username_input.clear()
            self.create_email_input.clear()
            self._load_employee_data_from_db()

    def _load_password_policy(self):
        cursor = None
        try:
            if db_connection is None or db_connection.closed:
                raise Exception("Database connection is not open.")
            cursor = self.db_connection.cursor()
            query = "SELECT setting_name, setting_value FROM \"CREDENTIALS\".PasswordPolicies WHERE setting_group = 'password_policy';"
            cursor.execute(query)
            rows = cursor.fetchall()
            db_connection.commit()
            cursor.close()
            loaded_settings = {row[0]: row[1] for row in rows}
            self.password_policy["min_length"] = int(loaded_settings.get("min_length", 8))
            self.password_policy["require_uppercase"] = (loaded_settings.get("require_uppercase", "True") == "True")
            self.password_policy["require_lowercase"] = (loaded_settings.get("require_lowercase", "True") == "True")
            self.password_policy["require_number"] = (loaded_settings.get("require_number", "True") == "True")
            self.password_policy["require_special"] = (loaded_settings.get("require_special", "True") == "True")
            self.password_policy["enforce_expiration"] = (loaded_settings.get("enforce_expiration", "False") == "True")
            self.password_policy["password_expiration_days"] = int(loaded_settings.get("password_expiration_days", 0))
        except Error as e:
            db_connection.rollback()
            QMessageBox.warning(self, "Policy Load Error",
                                f"Could not load password policy. Using default settings. Error: {e}")
        except Exception as e:
            db_connection.rollback()
            QMessageBox.warning(self, "Policy Load Error",
                                f"An unexpected error occurred while loading password policy. Error: {e}")
        finally:
            if cursor:
                cursor.close()

    def _validate_password(self, password):
        policy = self.password_policy
        errors = []
        if len(password) < policy["min_length"]:
            errors.append(f"- Must be at least {policy['min_length']} characters long.")
        if policy["require_uppercase"] and not any(c.isupper() for c in password):
            errors.append("- Must contain at least one uppercase letter.")
        if policy["require_lowercase"] and not any(c.islower() for c in password):
            errors.append("- Must contain at least one lowercase letter.")
        if policy["require_number"] and not any(c.isdigit() for c in password):
            errors.append("- Must contain at least one number.")
        if policy["require_special"] and not any(not c.isalnum() for c in password):
            errors.append("- Must contain at least one special character (e.g., !, @, #, $).")
        return errors

    def _save_changes(self):
        if not self.current_selected_employee:
            QMessageBox.warning(self, "Selection Error", "No employee selected for editing.")
            return
        original_username = self.current_selected_employee['username']
        new_first_name = self.edit_first_name_input.text().strip()
        new_last_name = self.edit_last_name_input.text().strip()
        new_username = self.edit_username_input.text().strip()
        new_email = self.edit_email_input.text().strip()
        new_access_level = self.edit_access_level_combobox.currentText()
        
        if not (new_first_name and new_last_name and new_username and  new_email):
            QMessageBox.warning(self, "Input Error", "First Name, Last Name, and Username cannot be empty.")
            return
        self.update_employee_in_db(original_username, new_first_name, new_last_name, new_username, new_access_level, new_email)
        QMessageBox.information(self, "Changes Saved", f"Changes for {new_username} saved successfully!")
        self._load_employee_data_from_db()
        self._clear_selection_and_forms()

class SystemConfigurationPage(QWidget):
    # Signal to emit when custom QSS changes are saved
    custom_qss_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("systemConfigurationPage")

        self.system_settings = {} 

        self._setup_ui()
        self._load_system_settings() # Load settings when the page is initialized

    def _setup_ui(self):
        """
        Sets up the layout and widgets for the System Configuration page.
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)

        title = QLabel("System Configuration")
        title.setObjectName("sectionTitle") # Apply section title style
        main_layout.addWidget(title)

        # Create a scroll area for the content if it grows
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        # PyQt6 Change: ScrollBarAlwaysOff is now in Qt.ScrollBarPolicy
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setObjectName("settingsScrollArea")

        scroll_content_widget = QWidget()
        scroll_content_widget.setObjectName("scrollContentWidget") # Add an object name for styling
        
        # CRITICAL FIX for black backgrounds on plain QWidgets if you're not using stylesheets
        # and rely on the default background.
        scroll_content_widget.setAutoFillBackground(True) 


        content_layout = QVBoxLayout(scroll_content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        # --- Custom Application Theme Section (with Name, Group, QSS) ---
        custom_theme_frame = self._create_custom_theme_section()
        content_layout.addWidget(custom_theme_frame)

        # --- Data Management Settings Section ---
        data_settings_frame = self._create_data_management_section()
        content_layout.addWidget(data_settings_frame)

        # --- Save Button ---
        self.save_button = QPushButton("Save System Settings")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self._save_system_settings)
        # PyQt6 Change: AlignCenter is now in Qt.AlignmentFlag
        content_layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignCenter)

        content_layout.addStretch() # Push content to the top

        scroll_area.setWidget(scroll_content_widget)
        main_layout.addWidget(scroll_area)

    def _create_custom_theme_section(self):
        """
        Creates and returns the QFrame for Custom Application Theme settings.
        Includes fields for Theme Name, Interface's Group, and QSS Content.
        """
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        
        # CRITICAL FIX for black backgrounds on plain QWidgets (like QFrame which inherits QWidget)
        # if you're not using stylesheets and rely on the default background.
        frame.setAutoFillBackground(True)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        section_title = QLabel("Custom Application Theme")
        section_title.setObjectName("sectionSubTitle")
        layout.addWidget(section_title)

        theme_form_layout = QGridLayout()
        theme_form_layout.setSpacing(10)

        # Theme Name
        theme_form_layout.addWidget(QLabel("Theme Name:"), 0, 0)
        self.theme_name_input = QLineEdit()
        self.theme_name_input.setPlaceholderText("e.g., Dark Mode for Admin")
        theme_form_layout.addWidget(self.theme_name_input, 0, 1)

        # Interface's Group
        theme_form_layout.addWidget(QLabel("Interface's Group:"), 1, 0)
        self.interface_group_input = QLineEdit()
        self.interface_group_input.setPlaceholderText("e.g., Admin_UI, Reports_Module")
        theme_form_layout.addWidget(self.interface_group_input, 1, 1)

        # QSS Content
        # PyQt6 Change: AlignTop is now in Qt.AlignmentFlag
        theme_form_layout.addWidget(QLabel("QSS Content:"), 2, 0, Qt.AlignmentFlag.AlignTop) # Align label to top
        self.custom_qss_input = QTextEdit()
        self.custom_qss_input.setPlaceholderText("Paste your custom Qt Style Sheet (QSS) content here...")
        self.custom_qss_input.setMinimumHeight(200) # Give it some height
        theme_form_layout.addWidget(self.custom_qss_input, 2, 1)

        layout.addLayout(theme_form_layout)
        return frame


    def _create_data_management_section(self):
        """
        Creates and returns the QFrame for Data Management Settings.
        """
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        
        # CRITICAL FIX for black backgrounds on plain QWidgets (like QFrame which inherits QWidget)
        # if you're not using stylesheets and rely on the default background.
        frame.setAutoFillBackground(True)
        

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        section_title = QLabel("Data Management")
        section_title.setObjectName("sectionSubTitle")
        layout.addWidget(section_title)

        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # Local Data Backup Path
        form_layout.addWidget(QLabel("Local Backup Path:"), 0, 0)
        self.backup_path_input = QLineEdit()
        self.backup_path_input.setPlaceholderText("e.g., C:/Backups/MyApp")
        form_layout.addWidget(self.backup_path_input, 0, 1)

        self.browse_backup_button = QPushButton("Browse...")
        self.browse_backup_button.setObjectName("secondaryButton")
        self.browse_backup_button.clicked.connect(self._browse_backup_path)
        form_layout.addWidget(self.browse_backup_button, 0, 2)

        layout.addLayout(form_layout)
        return frame

    def _browse_backup_path(self):
        """
        Opens a directory dialog to select the backup path.
        """
        # QDir.homePath() is correct for PyQt6
        current_path = self.backup_path_input.text() if self.backup_path_input.text() else QDir.homePath()
        
        directory = QFileDialog.getExistingDirectory(self, "Select Backup Directory", current_path)
        if directory:
            self.backup_path_input.setText(directory)

    def _load_system_settings(self):
        """
        Loads system configuration settings from the database and populates the UI fields.
        """
        cursor = None
        try:
            # Check for db_connection existence and state
            if db_connection is None:
                raise Exception("Database connection is not initialized.")
            if db_connection.closed:
                db_connection.connect() # Attempt to reconnect if closed
            
            cursor = db_connection.cursor()
            query = "SELECT setting_name, setting_value FROM \"CREDENTIALS\".PasswordPolicies WHERE setting_group = 'system_config';"
            cursor.execute(query)
            rows = cursor.fetchall()
            db_connection.commit()
            cursor.close()
            loaded_settings = {row[0]: row[1] for row in rows}

            self.backup_path_input.setText(loaded_settings.get("backup_path", ""))

            # Load custom theme settings
            self.theme_name_input.setText(loaded_settings.get("custom_theme_name", "Default Custom Theme"))
            self.interface_group_input.setText(loaded_settings.get("custom_theme_interface_group", "General"))
            self.custom_qss_input.setPlainText(loaded_settings.get("custom_theme_qss", ""))

            self.system_settings = loaded_settings # Store for potential internal use

        except Error as e:
            db_connection.rollback()
            QMessageBox.warning(self, "Load Error",
                                 f"Could not load system configuration. Using default settings. Error: {e}",
                                 QMessageBox.StandardButton.Ok) # Added explicit button for consistency
        except Exception as e:
            db_connection.rollback()
            QMessageBox.warning(self, "Load Error",
                                 f"An unexpected error occurred while loading system configuration. Error: {e}",
                                 QMessageBox.StandardButton.Ok) # Added explicit button for consistency
        finally:
            if cursor:
                cursor.close()

    def _save_system_settings(self):
        """
        Saves the current system configuration settings from the UI fields to the database.
        Uses UPSERT (UPDATE or INSERT) logic.
        """
        backup_path = self.backup_path_input.text().strip()
        
        # Get custom theme details
        theme_name = self.theme_name_input.text().strip()
        interface_group = self.interface_group_input.text().strip()
        custom_qss = self.custom_qss_input.toPlainText().strip()

        settings_to_save = {
            "backup_path": backup_path,
            "custom_theme_name": theme_name,
            "custom_theme_interface_group": interface_group,
            "custom_theme_qss": custom_qss
        }

        cursor = None
        try:
            # Check for db_connection existence and state
            if db_connection is None:
                raise Exception("Database connection is not initialized.")
            if db_connection.closed:
                db_connection.connect() # Attempt to reconnect if closed

            cursor = db_connection.cursor()
            
            for setting_name, setting_value in settings_to_save.items():
                upsert_query = """
                    INSERT INTO "CREDENTIALS".PasswordPolicies (setting_group, setting_name, setting_value)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (setting_group, setting_name) DO UPDATE
                    SET setting_value = EXCLUDED.setting_value;
                """
                cursor.execute(upsert_query, ('system_config', setting_name, setting_value))
            
            db_connection.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "System settings saved successfully!", QMessageBox.StandardButton.Ok)
            
            # Emit the signal with the new custom QSS content
            self.custom_qss_changed.emit(custom_qss)

            self._load_system_settings() # Reload to confirm
            
        except Error as e:
            if db_connection: # Ensure db_connection exists before trying to rollback
                db_connection.rollback()
            QMessageBox.critical(self, "Save Error", f"Failed to save system settings: {e}", QMessageBox.StandardButton.Ok)
        except Exception as e:
            if db_connection: # Ensure db_connection exists before trying to rollback
                db_connection.rollback()
            QMessageBox.critical(self, "Save Error", f"An unexpected error occurred while saving system settings: {e}", QMessageBox.StandardButton.Ok)
        finally:
            if cursor:
                cursor.close()

class DatabaseMaintenancePage(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("databaseMaintenancePage")
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)
        title = QLabel("Database Maintenance: Query Execution")
        title.setObjectName("sectionTitle")
        main_layout.addWidget(title)
        security_warning = QLabel(
            "<b style='color: red;'>SECURITY WARNING:</b> This feature allows direct execution of SQL queries "
            "and should only be used by highly authorized administrators. Incorrect queries can lead to "
            "data loss or corruption. Use with extreme caution."
        )
        security_warning.setWordWrap(True)
        security_warning.setStyleSheet("font-size: 14px; padding: 10px; background-color: #ffe6e6; border: 1px solid red; border-radius: 5px;")
        main_layout.addWidget(security_warning)
        main_layout.addSpacing(15)
        query_results_container = QWidget()
        query_results_layout = QVBoxLayout(query_results_container)
        query_results_layout.setContentsMargins(0,0,0,0)
        query_results_layout.setSpacing(15)
        query_input_frame = QFrame()
        query_input_frame.setObjectName("sectionFrame")
        query_input_layout = QVBoxLayout(query_input_frame)
        query_input_layout.setContentsMargins(20,20,20,20)
        query_input_layout.setSpacing(10)
        query_input_layout.addWidget(QLabel("<b>Enter SQL Query:</b>"))
        self.query_text_edit = QTextEdit()
        self.query_text_edit.setObjectName("queryTextEdit")
        self.query_text_edit.setPlaceholderText("e.g., SELECT * FROM \"SCA\".Tache;")
        self.query_text_edit.setMinimumHeight(120)
        self.query_text_edit.setFont(QFont("Monospace", 10))
        query_input_layout.addWidget(self.query_text_edit)
        self.execute_query_button = QPushButton("Execute Query")
        self.execute_query_button.setObjectName("primaryButton")
        self.execute_query_button.clicked.connect(self._execute_sql_query)
        query_input_layout.addWidget(self.execute_query_button)
        results_display_frame = QFrame()
        results_display_frame.setObjectName("sectionFrame")
        results_display_layout = QVBoxLayout(results_display_frame)
        results_display_layout.setContentsMargins(20,20,20,20)
        results_display_layout.setSpacing(10)
        results_display_layout.addWidget(QLabel("<b>Query Results:</b>"))
        self.results_table = QTableWidget()
        self.results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_message_text = QTextEdit()
        self.results_message_text.setPlaceholderText("Results or status messages will appear here.")
        self.results_message_text.setReadOnly(True)
        self.results_message_text.setMaximumHeight(120)
        self.results_message_text.setFont(QFont("Monospace", 9))
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(query_input_frame)
        self.splitter.addWidget(results_display_frame)
        self.splitter.setSizes([300, 400])
        results_display_layout.addWidget(self.results_table)
        results_display_layout.addWidget(self.results_message_text)
        query_results_layout.addWidget(self.splitter)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(query_results_container)
        scroll_area.setObjectName("queryResultScrollArea")
        main_layout.addWidget(scroll_area)

    def _execute_sql_query(self):
        query = self.query_text_edit.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "No Query", "Please enter an SQL query to execute.")
            return
        
        
        self.results_table.clearContents()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)
        self.results_message_text.clear()
        try:
            cursor = db_connection.cursor()
            cursor.execute(query)
            if cursor.description:
                column_names = [desc[0] for desc in cursor.description]
                self.results_table.setColumnCount(len(column_names))
                self.results_table.setHorizontalHeaderLabels(column_names)
                rows = cursor.fetchall()
                self.results_table.setRowCount(len(rows))
                for row_idx, row_data in enumerate(rows):
                    for col_idx, item in enumerate(row_data):
                        self.results_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
                db_connection.commit()
                self.results_message_text.setText(f"Query executed successfully. Fetched {len(rows)} rows.")
            else:
                row_count = cursor.rowcount
                db_connection.commit()
                self.results_message_text.setText(f"Query executed successfully. Affected {row_count} rows.")
            cursor.close()
        except Error as e:
            db_connection.rollback()
            error_message = f"Database Error: {e}"
            QMessageBox.critical(self, "Query Error", error_message)
            self.results_message_text.setText(error_message)
            if cursor:
                cursor.close()
        except Exception as e:
            db_connection.rollback()
            error_message = f"An unexpected error occurred: {e}"
            QMessageBox.critical(self, "Application Error", error_message)
            self.results_message_text.setText(error_message)
            if cursor:
                cursor.close()
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

class SecuritySettingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("securitySettingPage")
        self._setup_ui()
        self.password_policy_settings = {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_number": True,
            "require_special": True,
            "password_expiration_days": 0,
            "enforce_expiration": False
        }
        self._load_password_policy_from_db()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)
        title = QLabel("Security Settings")
        title.setObjectName("sectionTitle")
        main_layout.addWidget(title)
        password_policy_frame = QFrame()
        password_policy_frame.setObjectName("sectionFrame")
        password_policy_layout = QVBoxLayout(password_policy_frame)
        password_policy_layout.setContentsMargins(20, 20, 20, 20)
        password_policy_layout.setSpacing(15)
        policy_title = QLabel("Password Policy Configuration")
        policy_title.setObjectName("sectionSubTitle")
        password_policy_layout.addWidget(policy_title)
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        form_layout.addWidget(QLabel("Minimum Length:"), 0, 0)
        self.min_length_spinbox = QSpinBox()
        self.min_length_spinbox.setMinimum(6)
        self.min_length_spinbox.setMaximum(64)
        self.min_length_spinbox.setValue(8)
        form_layout.addWidget(self.min_length_spinbox, 0, 1)
        self.require_uppercase_checkbox = QCheckBox("Require Uppercase Letter")
        self.require_uppercase_checkbox.setChecked(True)
        form_layout.addWidget(self.require_uppercase_checkbox, 1, 0, 1, 2)
        self.require_lowercase_checkbox = QCheckBox("Require Lowercase Letter")
        self.require_lowercase_checkbox.setChecked(True)
        form_layout.addWidget(self.require_lowercase_checkbox, 2, 0, 1, 2)
        self.require_number_checkbox = QCheckBox("Require Number")
        self.require_number_checkbox.setChecked(True)
        form_layout.addWidget(self.require_number_checkbox, 3, 0, 1, 2)
        self.require_special_checkbox = QCheckBox("Require Special Character")
        self.require_special_checkbox.setChecked(True)
        form_layout.addWidget(self.require_special_checkbox, 4, 0, 1, 2)
        self.enforce_expiration_checkbox = QCheckBox("Enforce Password Expiration")
        self.enforce_expiration_checkbox.setChecked(False)
        form_layout.addWidget(self.enforce_expiration_checkbox, 5, 0, 1, 2)
        form_layout.addWidget(QLabel("Expire after (days):"), 6, 0)
        self.expiration_days_spinbox = QSpinBox()
        self.expiration_days_spinbox.setMinimum(0)
        self.expiration_days_spinbox.setMaximum(365)
        self.expiration_days_spinbox.setValue(90)
        self.expiration_days_spinbox.setEnabled(False)
        form_layout.addWidget(self.expiration_days_spinbox, 6, 1)
        self.enforce_expiration_checkbox.toggled.connect(self.expiration_days_spinbox.setEnabled)
        password_policy_layout.addLayout(form_layout)
        self.save_policy_button = QPushButton("Save Password Policy")
        self.save_policy_button.setObjectName("primaryButton")
        self.save_policy_button.clicked.connect(self._save_password_policy)
        password_policy_layout.addWidget(self.save_policy_button)
        password_policy_layout.addStretch()
        main_layout.addWidget(password_policy_frame)
        main_layout.addStretch()

    def _load_password_policy_from_db(self):
        print("Loading password policy from database...")
        cursor = None
        try:
            if db_connection is None or db_connection.closed:
                raise Exception("Database connection is not open.")
            cursor = db_connection.cursor()
            query = "SELECT setting_name, setting_value FROM \"CREDENTIALS\".PasswordPolicies WHERE setting_group = 'password_policy';"
            cursor.execute(query)
            rows = cursor.fetchall()
            db_connection.commit()
            loaded_settings = {row[0]: row[1] for row in rows}
            self.password_policy_settings["min_length"] = int(loaded_settings.get("min_length", 8))
            self.password_policy_settings["require_uppercase"] = (loaded_settings.get("require_uppercase", "True") == "True")
            self.password_policy_settings["require_lowercase"] = (loaded_settings.get("require_lowercase", "True") == "True")
            self.password_policy_settings["require_number"] = (loaded_settings.get("require_number", "True") == "True")
            self.password_policy_settings["require_special"] = (loaded_settings.get("require_special", "True") == "True")
            self.password_policy_settings["enforce_expiration"] = (loaded_settings.get("enforce_expiration", "False") == "True")
            self.password_policy_settings["password_expiration_days"] = int(loaded_settings.get("password_expiration_days", 0))
            self.min_length_spinbox.setValue(self.password_policy_settings["min_length"])
            self.require_uppercase_checkbox.setChecked(self.password_policy_settings["require_uppercase"])
            self.require_lowercase_checkbox.setChecked(self.password_policy_settings["require_lowercase"])
            self.require_number_checkbox.setChecked(self.password_policy_settings["require_number"])
            self.require_special_checkbox.setChecked(self.password_policy_settings["require_special"])
            self.enforce_expiration_checkbox.setChecked(self.password_policy_settings["enforce_expiration"])
            self.expiration_days_spinbox.setValue(self.password_policy_settings["password_expiration_days"])
        except Error as e:
            db_connection.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to load password policy from database: {e}")
            print(f"Error loading password policy: {e}")
        except Exception as e:
            db_connection.rollback()
            QMessageBox.critical(self, "Application Error", f"An unexpected error occurred while loading password policy: {e}")
            print(f"Unexpected error: {e}")
        finally:
            if cursor:
                cursor.close()

    def _save_password_policy(self):
        self.password_policy_settings["min_length"] = self.min_length_spinbox.value()
        self.password_policy_settings["require_uppercase"] = self.require_uppercase_checkbox.isChecked()
        self.password_policy_settings["require_lowercase"] = self.require_lowercase_checkbox.isChecked()
        self.password_policy_settings["require_number"] = self.require_number_checkbox.isChecked()
        self.password_policy_settings["require_special"] = self.require_special_checkbox.isChecked()
        self.password_policy_settings["enforce_expiration"] = self.enforce_expiration_checkbox.isChecked()
        self.password_policy_settings["password_expiration_days"] = self.expiration_days_spinbox.value() if self.enforce_expiration_checkbox.isChecked() else 0
        print("Attempting to save password policy to database...")
        try:
            if db_connection is None or db_connection.closed:
                raise Exception("Database connection is not open. Cannot save settings.")
            cursor = db_connection.cursor()
            for setting_name, value in self.password_policy_settings.items():
                setting_value_str = str(value)
                query = """
                    INSERT INTO "CREDENTIALS".PasswordPolicies (setting_name, setting_value, setting_group)
                    VALUES (%s, %s, 'password_policy')
                    ON CONFLICT (setting_name) DO UPDATE
                    SET setting_value = EXCLUDED.setting_value;
                """
                cursor.execute(query, (setting_name, setting_value_str))
            db_connection.commit()
            QMessageBox.information(self, "Policy Saved", "Password policy saved successfully!")
            print("Password policy saved to database.")
        except Error as e:
            db_connection.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to save password policy: {e}")
            print(f"Error saving password policy: {e}")
        except Exception as e:
            db_connection.rollback()
            QMessageBox.critical(self, "Application Error", f"An unexpected error occurred while saving password policy: {e}")
            print(f"Unexpected error: {e}")
        finally:
            if cursor:
                cursor.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebarFrame")
        self.sidebar_frame.setFixedWidth(250)
        self.sidebar_layout = QVBoxLayout(self.sidebar_frame)
        self.sidebar_layout.setContentsMargins(20, 20, 20, 20)
        self.sidebar_layout.setSpacing(15)
        self.logged_in_label = QLabel("Logged in as <b>john.smit</b>")
        self.logged_in_label.setObjectName("loggedInLabel")
        self.logged_in_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.sidebar_layout.addWidget(self.logged_in_label)
        self.sidebar_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        self.nav_buttons = {}
        self.pages = []
        self.stacked_content_widget = QStackedWidget()
        nav_items_map = {
            "ACCOUNT SETTINGS": AccountSettingsPage(),
            "SYSTEM CONFIGURATION": SystemConfigurationPage(),
            "DATABASE MAINTENANCE": DatabaseMaintenancePage(),
            "SECURITY SETTINGS": SecuritySettingPage(),
            "TERMINAL": TerminalPage(), # Terminal Page
            "AUTOMATION": AutomationPage(),
        }
        for i, (text, page_widget) in enumerate(nav_items_map.items()):
            self.pages.append(page_widget)
            self.stacked_content_widget.addWidget(page_widget)
            btn = QPushButton(text)
            btn.setObjectName(f"navButton_{text.replace(' ', '')}")
            btn.clicked.connect(lambda checked, idx=i, b=btn: self._on_nav_button_clicked(idx, b))
            self.nav_buttons[text] = btn
            self.sidebar_layout.addWidget(btn)
        self.sidebar_layout.addStretch()
        self.content_area_container = QWidget()
        self.content_area_layout = QVBoxLayout(self.content_area_container)
        self.content_area_layout.setContentsMargins(40, 30, 40, 30)
        self.content_area_layout.setSpacing(25)
        self.main_title_label = QLabel("Account Settings")
        self.main_title_label.setObjectName("mainTitleLabel")
        self.content_area_layout.addWidget(self.main_title_label)
        self.content_area_layout.addWidget(self.stacked_content_widget)
        self.stacked_content_widget.setCurrentIndex(0)
        initial_nav_button_text = list(nav_items_map.keys())[0]
        self.nav_buttons[initial_nav_button_text].setProperty("active", True)
        self.nav_buttons[initial_nav_button_text].style().polish(self.nav_buttons[initial_nav_button_text])
        self.main_title_label.setText(initial_nav_button_text)
        self.main_layout.addWidget(self.sidebar_frame)
        self.main_layout.addWidget(self.content_area_container)

    def _on_nav_button_clicked(self, index, clicked_button):
        self.main_title_label.setText(clicked_button.text())
        self.stacked_content_widget.setCurrentIndex(index)
        for text, btn_widget in self.nav_buttons.items():
            if btn_widget == clicked_button:
                btn_widget.setProperty("active", True)
            else:
                btn_widget.setProperty("active", False)
            btn_widget.style().polish(btn_widget)
    
   
    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            #sidebarFrame {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
            #loggedInLabel {
                color: #ecf0f1;
                font-size: 16px;
                padding-bottom: 10px;
                border-bottom: 1px solid #34495e;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 15px;
                text-align: left;
                font-size: 14px;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton[active="true"] {
                background-color: #f39c12;
                color: #2c3e50;
                font-weight: bold;
                border-left: 5px solid #e67e22; /* Darker orange left border */
            }
            QPushButton[active="true"]:hover {
                background-color: #e67e22;
            }
            #sectionFrame, #accountSettingsPage, #placeholderPage {
                background-color: white;
                border-radius: 8px;
            }
            #accountSettingsPage, #placeholderPage, #databaseMaintenancePage, #securitySettingPage {
                 background-color: transparent;
            }
             QTextEdit#terminalOutputTextEdit, QTextEdit#automationLogTextEdit { /* Applied to both terminal and automation log */
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11pt;
                border-radius: 5px;
                padding: 10px;
                
            }

            QPushButton#executeButton, QPushButton#clearOutputButton {
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                border: none;
            }
            QPushButton#executeButton {
                background-color: #008CBA;
            }
            QPushButton#executeButton:hover {
                background-color: #007bb5;
            }
            QPushButton#clearOutputButton {
                background-color: #f44336;
            }
            QPushButton#clearOutputButton:hover {
                background-color: #da190b;
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
            QLineEdit, QComboBox, QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #3498db;
            }
            QCheckBox {
                font-size: 14px;
                color: #34495e;
            }
            QCheckBox::indicator {
            width: 15px; 
            height: 15px;
            border: 1px solid #348;
            border-radius: 5px;
            background-color: lightgray;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db; 
                border: 1px solid #348;
            }
            QCheckBox::indicator:disabled {
                border: 1px solid #348;
                background-color: #eee;
            }
            #employeeCard {
                background-color: #ecf0f1;
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
            #employeeCard[selected="true"] {
                background-color: #cceeff;
                border: 2px solid #3498db;
            }
            #primaryButton {
                background-color: #2ecc71;
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
            
            #deleteButton {
                background-color: #e74c3c;
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
            #secondaryButton {
                background-color: #95a5a6;
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
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            #placeholderPage h1 {
                color: #34495e;
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
                background-color: transparent;
                border: none;
            }
            #employeeListScrollArea {
                border: none;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #ccc;
                gridline-color: #eee;
                font-size: 13px;
                selection-background-color: #d1eaff;
                selection-color: #333;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #cceeff;
                color: black;
            }
            QHeaderView::section {
                background-color: #e6e6e6;
                padding: 5px;
                border: 1px solid #ccc;
                font-weight: bold;
                color: #333;
            }
            QHeaderView::section:hover {
                background-color: #d9d9d9;
            }
            QHeaderView::section:horizontal {
                border-bottom: 2px solid #aaa;
            }
            QHeaderView::section:vertical {
                border-right: 2px solid #aaa;
            }
            #sectionSubTitle {
                font-size: 18px;
                font-weight: bold;
                color: #555;
                margin-bottom: 10px;
            }
            #queryTextEdit {
                background-color: white;
            }
            QWidget#AutomationPage #sectionTitle {
                font-size: 28px; /* Override for specific title */
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
            }
            QWidget#AutomationPage p {
                text-align: left; /* Align paragraphs normally */
                padding: 0 10px; /* Add some horizontal padding for readability */
            }


            /* Table widget styling (if used in future pages) */
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #ccc;
                gridline-color: #eee;
                font-size: 13px;
                selection-background-color: #d1eaff;
                selection-color: #333;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #cceeff;
                color: black;
            }
            QHeaderView::section {
                background-color: #e6e6e6;
                padding: 5px;
                border: 1px solid #ccc;
                font-weight: bold;
                color: #333;
            }
            QHeaderView::section:horizontal {
                border-bottom: 2px solid #aaa;
            }
            QHeaderView::section:vertical {
                border-right: 2px solid #aaa;
            }
            #sectionSubTitle {
                font-size: 18px;
                font-weight: bold;
                color: #555;
                margin-bottom: 10px;
            }

            /* Buttons inside automation page */
            QPushButton#primaryButton { /* Reused from earlier primaryButton, adjust if needed */
                background-color: #2ecc71; /* Green */
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 10px;
                margin-top: 2px; /* Adjust spacing */
                text-align: center;
            }
            QPushButton#primaryButton:hover {
                background-color: #27ae60;
            }
            QPushButton#secondaryButton {
                background-color: #95a5a6; /* Gray */
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 14px;
                border-radius: 5px;
                margin-top: 10px;
                text-align: center;
            }
            QPushButton#secondaryButton:hover {
                background-color: #7f8c8d;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Arial", 10)
    app.setFont(font)
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))  # Dialog background
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#232946"))  # Dialog text
    palette.setColor(QPalette.ColorRole.Base, QColor("#F8F9FA"))  # Input fields
    palette.setColor(QPalette.ColorRole.Text, QColor("#232946"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#6C63FF"))  # Accent for buttons
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#6C63FF"))  # Selection color
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#EB7A16FF"))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    

