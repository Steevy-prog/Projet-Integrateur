# import sys
# from datetime import datetime
# from PyQt5.QtWidgets import (
#     QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
#     QLineEdit, QLabel, QTextEdit, QFileDialog, QMessageBox, QGroupBox, QStackedWidget,
#     QFrame, QSizePolicy, QSpacerItem, QScrollArea, QTableWidget, QHeaderView, QTableWidgetItem
# )
# from PyQt5.QtCore import Qt, QObject, pyqtSignal
# import psycopg2
# from psycopg2 import Error

# # --- Database Connection (Global for simplicity in mock, could be passed to pages) ---
# # IMPORTANT: For a production app, manage connection lifecycle more carefully
# # (e.g., passing connection pool/manager to pages, or using a singleton pattern).
# # Keeping it global as in your provided code for now.
    
# host = "dpg-d1b612gdl3ps73eapfr0-a.oregon-postgres.render.com"  # Replace with your database host
# database = "test_bpdd"  # Replace with your database name
# user = "test"  # Replace with your database username
# password = "w95g3tjqj0S9DLwNiaFEMb1SACWuuIjh"  # Replace with your database password
# port = 5432  # Default PostgreSQL port, change if necessary

# db_connection = None
# try:
#     db_connection = psycopg2.connect(
#         host=host,
#         database=database,
#         user=user,
#         password=password,
#         port=port
#     )
#     print(f"Successfully connected to PostgreSQL database: {database}")

# except Error as e:
#     print(f"Error connecting to PostgreSQL database: {e}")
    

# # --- Custom Stream for QTextEdit (Our 'Terminal') ---
# class QTextEditLogger(QObject):
#     append_text = pyqtSignal(str)

#     def __init__(self, text_edit):
#         super().__init__()
#         self.text_edit = text_edit
#         self.append_text.connect(self.text_edit.append)

#     def write(self, text):
#         if text.strip():
#             self.append_text.emit(text.strip())

#     def flush(self):
#         pass

# # --- Page Classes ---

# class TerminalPage(QWidget):
#     """
#     Represents the main automation terminal page with command input and output.
#     Contains all the core AA logic.
#     """
    
#     def __init__(self, parent=None):
#         super().__init__(parent)
        
#         # --- CRITICAL FIX: Define command_list and command_description as instance attributes HERE ---
#         # This ensures they exist BEFORE init_ui() is called or any initial terminal messages
#         # that might indirectly trigger command parsing.
#         self.command_list = {
#             'command_list': self.list_command,
#             'help': self.display_help,
#             'count_product': self.count_product,
#             'count_user': self.count_user,
#             'list_stock_product': self.list_product,
#             'list_user': self.list_user,
#             'clear_terminal': self.clear_terminal,
#             # 'set_report_settings': self.set_report_settings,
#             # 'generate_report': self.generate_report,
#             # 'start_backup': self.backup_database,
#             # 'display_logs': self.display_logs,
            
#         }
#         self.command_description = {
#             'command_list': 'List of available commands.',
#             'help': 'Indictions on how to use the terminal.',
#             'count_product': 'Display the number of products in stock.',
#             'count_user': 'Display the number of users.',
#             'list_stock_product': 'List of all products in stock.',
#             'list_user': 'List of all users.',
#             'clear_terminal': 'Clear the terminal output.',
#             # 'set_report_settings': 'Set report generation settings (not implemented).',
#             # 'generate_report': 'Generate a report based on current settings (not implemented).'
#             # 'start_backup': 'Start a database backup.',
#             # 'display_logs': 'Display system logs.'
#         }
#         # --- End of attribute definitions ---

#         self.init_ui() # Now it's safe to call init_ui()

#         # Redirect stdout and stderr for this specific page's terminal output
#         self.text_edit_logger = QTextEditLogger(self.terminal_output)
#         self._original_stdout = sys.stdout
#         self._original_stderr = sys.stderr
#         sys.stdout = self.text_edit_logger
#         sys.stderr = self.text_edit_logger

#         self.terminal_output.append("Welcome to SGE Warehouse Automation Terminal!")
#         self.terminal_output.append("Type 'A --command_list' in the command input to see available commands.")


#     def init_ui(self):
#         page_layout = QVBoxLayout(self) # Layout directly on the widget
#         page_layout.setContentsMargins(0, 0, 0, 0) # Managed by parent container layout
#         page_layout.setSpacing(15)

#         # --- Command Input GroupBox ---
#         command_group_box = QGroupBox("Command Input")
#         command_group_box.setObjectName("commandInputGroupBox") # For QSS
#         command_layout = QHBoxLayout(command_group_box) # Layout directly on QGroupBox
        
#         self.command_line_edit = QLineEdit()
#         self.command_line_edit.setPlaceholderText("Type command (e.g., sac --command_list)")
#         self.command_line_edit.setObjectName("commandLineEdit") # For QSS
#         self.command_line_edit.returnPressed.connect(self.execute_command)
#         command_layout.addWidget(self.command_line_edit)

#         execute_button = QPushButton("Execute Command")
#         execute_button.setObjectName("executeButton") # For QSS
#         execute_button.clicked.connect(self.execute_command)
#         command_layout.addWidget(execute_button)
        
#         page_layout.addWidget(command_group_box)

#         # --- Terminal Output GroupBox ---
#         output_group_box = QGroupBox("Output (Terminal)")
#         output_group_box.setObjectName("terminalOutputGroupBox") # For QSS
#         output_layout = QVBoxLayout(output_group_box) # Layout directly on QGroupBox

#         self.terminal_output = QTextEdit()
#         self.terminal_output.setReadOnly(True)
#         self.terminal_output.setObjectName("terminalOutputTextEdit") # For QSS
#         output_layout.addWidget(self.terminal_output)

#         clear_button = QPushButton("Clear Output")
#         clear_button.setObjectName("clearOutputButton") # For QSS
#         clear_button.clicked.connect(self.clear_terminal)
#         output_layout.addWidget(clear_button, alignment=Qt.AlignRight)
        
#         page_layout.addWidget(output_group_box)
        
#     # --- Core Automation Application (AA) Logic as methods of TerminalPage ---
    
#     def execute_command(self):
#         command_line = self.command_line_edit.text().strip()
        
#         if not command_line:
#             return
        
#         self.command_line_edit.clear() # Clear input after execution
#         self.terminal_output.append(f"\n> {command_line}") # Echo the command

#         parts = command_line.split(' --') # Split by ' --' to separate "sac" from command
#         # Check if it starts with 'sac' and has at least one '--' separated part
#         if len(parts) < 2 or parts[0].strip().lower() != 'sac':
#             self.unknown_command()
#             return
        
#         command = parts[1].strip() # The actual command part after 'sac --'
        
#         # Execute the command using the dictionary mapping
#         # .get(key, default_value_if_not_found)
#         self.command_list.get(command, self.unknown_command)()
    
#     def list_command(self):
#         self.terminal_output.append("\n--- Available commands: ---")
#         # Corrected iteration: iterate over items() to get both key and value
#         for cmd, description in self.command_description.items():
#             self.terminal_output.append(f"- {cmd}:\t{description}")
#         self.terminal_output.append("---------------------------\n")
            
#     def unknown_command(self):
#         self.terminal_output.append("Unknown command!")
#         self.terminal_output.append("Type 'sac --command_list' for a list of available commands.")
#         self.terminal_output.append("Type 'sac --help' for instructions on how to use the terminal.")
        
#     def display_help(self):
#         self.terminal_output.append("\n--- Terminal Usage Help ---")
#         self.terminal_output.append("Commands start with 'sac --' followed by the command name.")
#         self.terminal_output.append("Example: sac --command_list")
#         self.terminal_output.append("For commands requiring arguments, specify them after the command name.")
#         self.terminal_output.append("---------------------------\n")

#     def count_product(self):
#         if db_connection:
#             try:
#                 cursor = db_connection.cursor()
#                 cursor.execute("SELECT total();") # Assuming a 'products' table
#                 count = cursor.fetchone()[0]
#                 self.terminal_output.append(f"Number of products in stock: {count}")
#             except Error as e:
#                 self.terminal_output.append(f"Error counting products: {e}")
#             finally:
#                 if cursor:
#                     cursor.close()
#         else:
#             self.terminal_output.append("Database connection not established. Cannot count products.")

#     def count_user(self):
#         if db_connection:
#             try:
#                 cursor = db_connection.cursor()
#                 cursor.execute("SELECT COUNT(*) FROM users;") # Assuming a 'users' table
#                 count = cursor.fetchone()[0]
#                 self.terminal_output.append(f"Number of users: {count}")
#             except Error as e:
#                 self.terminal_output.append(f"Error counting users: {e}")
#             finally:
#                 if cursor:
#                     cursor.close()
#         else:
#             self.terminal_output.append("Database connection not established. Cannot count users.")

#     def list_product(self):
#         if db_connection:
#             try:
#                 cursor = db_connection.cursor()
#                 cursor.execute("SELECT product_id, name, quantity FROM products;") # Assuming 'products' table
#                 products = cursor.fetchall()
#                 self.terminal_output.append("\n--- Products in Stock ---")
#                 if products:
#                     for product in products:
#                         self.terminal_output.append(f"ID: {product[0]}, Name: {product[1]}, Quantity: {product[2]}")
#                 else:
#                     self.terminal_output.append("No products found.")
#                 self.terminal_output.append("---------------------------\n")
#             except Error as e:
#                 self.terminal_output.append(f"Error listing products: {e}")
#             finally:
#                 if cursor:
#                     cursor.close()
#         else:
#             self.terminal_output.append("Database connection not established. Cannot list products.")

#     def list_user(self):
#         if db_connection:
#             try:
#                 cursor = db_connection.cursor()
#                 cursor.execute("SELECT username, email FROM users;") # Assuming 'users' table
#                 users = cursor.fetchall()
#                 self.terminal_output.append("\n--- Users List ---")
#                 if users:
#                     for user_data in users:
#                         self.terminal_output.append(f"Username: {user_data[0]}, Email: {user_data[1]}")
#                 else:
#                     self.terminal_output.append("No users found.")
#                 self.terminal_output.append("-------------------\n")
#                 cursor.close()
#             except Error as e:
#                 self.terminal_output.append(f"Error listing users: {e}")
#             finally:
#                 if cursor:
#                     cursor.close()
#         else:
#             self.terminal_output.append("Database connection not established. Cannot list users.")

#     def clear_terminal(self):
#         self.terminal_output.clear()
#         self.terminal_output.append("Terminal cleared.")


#     def __del__(self):
#         """Restore original stdout/stderr when TerminalPage is destroyed."""
#         # Check if attributes exist before restoring, for safer shutdown
#         if hasattr(self, '_original_stdout') and self._original_stdout is not None:
#              sys.stdout = self._original_stdout
#         if hasattr(self, '_original_stderr') and self._original_stderr is not None:
#              sys.stderr = self._original_stderr


# # Placeholder Page Classes
# class AutomationPage(QWidget):
    # def __init__(self, parent=None):
    #     super().__init__(parent)
    #     self.setObjectName("AutomationPage")
    #     self.init_ui()

    # def init_ui(self):
    #     main_layout = QVBoxLayout(self)
    #     main_layout.setContentsMargins(0, 0, 0, 0)
    #     main_layout.setSpacing(20)

    #     # Create a QScrollArea
    #     scroll_area = QScrollArea(self)
    #     scroll_area.setWidgetResizable(True) # Allow the widget inside to resize with the scroll area
    #     scroll_area.setObjectName("automationPageScrollArea") # For QSS if needed
        
    #     # Create a container widget for the scroll area's content
    #     scroll_content_widget = QWidget()
    #     scroll_content_layout = QVBoxLayout(scroll_content_widget)
    #     scroll_content_layout.setContentsMargins(0, 0, 0, 0) # Control padding via content_area_layout in MainWindow
    #     scroll_content_layout.setSpacing(20) # Spacing between elements within the scrollable area

    #     # Title
    #     title_label = QLabel("<h3>Warehouse Automation Workflows</h3>")
    #     title_label.setObjectName("sectionTitle") # Reusing QSS ID for a section title
    #     title_label.setAlignment(Qt.AlignCenter)
    #     scroll_content_layout.addWidget(title_label)

    #     # Description
    #     description_label = QLabel(
    #         "<p>Manage and initiate automated tasks within the warehouse management system.</p>"
    #         "<p>Select an automation task below to view its details or trigger its execution.</p>"
    #     )
    #     description_label.setAlignment(Qt.AlignCenter)
    #     description_label.setWordWrap(True)
    #     scroll_content_layout.addWidget(description_label)

    #     # Automation Tasks Section
    #     tasks_group_box = QGroupBox("Available Automation Tasks")
    #     tasks_group_box.setObjectName("automationTasksGroupBox") # Unique ID for QSS
    #     tasks_layout = QVBoxLayout(tasks_group_box)
    #     tasks_layout.setSpacing(10)

    #     # Automation Buttons
    #     self.btn_generate_monthly_report = QPushButton("Generate Report")
    #     self.btn_generate_monthly_report.setObjectName("primaryButton")
    #     self.btn_generate_monthly_report.clicked.connect(self._generate_monthly_report)
    #     tasks_layout.addWidget(self.btn_generate_monthly_report)

    #     self.btn_low_stock_notification = QPushButton("Trigger Low Stock Notifications")
    #     self.btn_low_stock_notification.setObjectName("primaryButton")
    #     self.btn_low_stock_notification.clicked.connect(self._trigger_low_stock_notifications)
    #     tasks_layout.addWidget(self.btn_low_stock_notification)
        
    #     # Add a few more placeholder buttons to ensure scrolling is evident
    #     self.btn_data_backup = QPushButton("Perform Database Backup")
    #     self.btn_data_backup.setObjectName("primaryButton")
    #     self.btn_data_backup.clicked.connect(lambda: self._log_automation_event("Database backup initiated."))
    #     tasks_layout.addWidget(self.btn_data_backup)

    #     self.btn_audit_log_cleanup = QPushButton("Clean Up Old Audit Logs")
    #     self.btn_audit_log_cleanup.setObjectName("primaryButton")
    #     self.btn_audit_log_cleanup.clicked.connect(lambda: self._log_automation_event("Old audit logs cleanup initiated."))
    #     tasks_layout.addWidget(self.btn_audit_log_cleanup)


    #     scroll_content_layout.addWidget(tasks_group_box)

    #     # Automation Log/Status Area
    #     log_group_box = QGroupBox("Automation Log")
    #     log_group_box.setObjectName("automationLogGroupBox")
    #     log_layout = QVBoxLayout(log_group_box)
        
    #     self.automation_log_output = QTextEdit()
    #     self.automation_log_output.setReadOnly(True)
    #     self.automation_log_output.setObjectName("automationLogTextEdit") # Specific ID for QSS
    #     log_layout.addWidget(self.automation_log_output)

    #     clear_log_button = QPushButton("Clear Automation Log")
    #     clear_log_button.setObjectName("secondaryButton") # Reusing secondaryButton style
    #     clear_log_button.clicked.connect(self.automation_log_output.clear)
    #     log_layout.addWidget(clear_log_button, alignment=Qt.AlignRight)

    #     scroll_content_layout.addWidget(log_group_box)

    #     # scroll_content_layout.addStretch(1) # Pushes content to the top within the scroll area

    #     # Set the content widget for the scroll area
    #     scroll_area.setWidget(scroll_content_widget)
        
    #     # Add the scroll area to the main layout of the AutomationPage
    #     main_layout.addWidget(scroll_area)

    # # --- Automation Task Methods (placeholders) ---
    # def _log_automation_event(self, message):
    #     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     self.automation_log_output.append(f"[{timestamp}] {message}")

    # def _generate_monthly_report(self):
    #     self._log_automation_event("Generating monthly sales report...")
    #     QMessageBox.information(self, "Automation Task", "Monthly Sales Report generation task initiated. (Check log for details)")
    #     # Simulate report generation time
    #     QApplication.processEvents() # Keep UI responsive
    #     # In a real app, this would involve data querying and report formatting
    #     self._log_automation_event("Monthly sales report generated and saved.")

    # def _trigger_low_stock_notifications(self):
    #     self._log_automation_event("Triggering low stock notifications...")
    #     QMessageBox.information(self, "Automation Task", "Low Stock Notifications triggered. (Check log for details)")
    #     # This would typically involve checking inventory levels and sending alerts
    #     self._log_automation_event("Low stock notifications sent to relevant personnel.")



# # --- Main Application Window ---

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Automation Dashboard")
#         self.setGeometry(100, 100, 1200, 800)

#         self.central_widget = QWidget()
#         self.setCentralWidget(self.central_widget)
#         self.main_layout = QHBoxLayout(self.central_widget)
#         self.main_layout.setContentsMargins(20, 20, 20, 20)
#         self.main_layout.setSpacing(15)

#         self._setup_ui()
#         self._apply_styles()

#     def _setup_ui(self):
#         """
#         Sets up the main window's layout, sidebar, and stacked widget for content.
#         """
#         # 1. Left Sidebar
#         self.sidebar_frame = QFrame()
#         self.sidebar_frame.setObjectName("sidebarFrame")
#         self.sidebar_frame.setFixedWidth(250)
#         self.sidebar_layout = QVBoxLayout(self.sidebar_frame)
#         self.sidebar_layout.setContentsMargins(20, 20, 20, 20)
#         self.sidebar_layout.setSpacing(15)

#         self.logged_in_label = QLabel("Logged in as <b>john.smit</b>")
#         self.logged_in_label.setObjectName("loggedInLabel")
#         self.logged_in_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
#         self.sidebar_layout.addWidget(self.logged_in_label)

#         self.sidebar_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))

#         # Navigation buttons and their corresponding page instances
#         self.nav_buttons = {}
#         self.pages = [] # List to hold instances of QWidget pages (matched to stacked_content_widget indices)

#         self.stacked_content_widget = QStackedWidget()

#         # Define navigation items and create their pages
#         nav_items_map = {
#             "TERMINAL": TerminalPage(), # Terminal Page
#             "AUTOMATION": AutomationPage(),
#         }

#         for i, (text, page_widget) in enumerate(nav_items_map.items()):
#             self.pages.append(page_widget)
#             self.stacked_content_widget.addWidget(page_widget)

#             btn = QPushButton(text)
#             btn.setObjectName(f"navButton_{text.replace(' ', '')}")
#             btn.clicked.connect(lambda checked, idx=i, b=btn: self._on_nav_button_clicked(idx, b))
#             self.nav_buttons[text] = btn
#             self.sidebar_layout.addWidget(btn)

#         self.sidebar_layout.addStretch()

#         # 2. Main Content Area
#         self.content_area_container = QWidget()
#         self.content_area_container.setObjectName("contentAreaContainer")
#         self.content_area_layout = QVBoxLayout(self.content_area_container)
#         self.content_area_layout.setContentsMargins(40, 30, 40, 30)
#         self.content_area_layout.setSpacing(25)

#         self.main_title_label = QLabel("Account Settings")
#         self.main_title_label.setObjectName("mainTitleLabel")
#         self.content_area_layout.addWidget(self.main_title_label)

#         self.content_area_layout.addWidget(self.stacked_content_widget)

#         # Set initial page and active button
#         self.stacked_content_widget.setCurrentIndex(0)
#         initial_nav_button_text = list(nav_items_map.keys())[0]
#         self.nav_buttons[initial_nav_button_text].setProperty("active", True)
#         self.nav_buttons[initial_nav_button_text].style().polish(self.nav_buttons[initial_nav_button_text])
#         self.main_title_label.setText(initial_nav_button_text)

#         self.main_layout.addWidget(self.sidebar_frame)
#         self.main_layout.addWidget(self.content_area_container)

#     def _on_nav_button_clicked(self, index, clicked_button):
#         """
#         Handles navigation button clicks, switching the QStackedWidget page
#         and updating button active states.
#         """
#         self.main_title_label.setText(clicked_button.text())
#         self.stacked_content_widget.setCurrentIndex(index)

#         for text, btn_widget in self.nav_buttons.items():
#             if btn_widget == clicked_button:
#                 btn_widget.setProperty("active", True)
#             else:
#                 btn_widget.setProperty("active", False)
#             btn_widget.style().polish(btn_widget)

    # def _apply_styles(self):
    #     """
    #     Applies Qt Style Sheets (QSS) for the application's look and feel.
    #     """
    #     self.setStyleSheet("""
    #         QMainWindow {
    #             background-color: #f0f2f5;
    #         }

    #         #sidebarFrame {
    #             background-color: #2c3e50;
    #             border-right: 1px solid #34495e;
    #         }

    #         #loggedInLabel {
    #             color: #ecf0f1;
    #             font-size: 16px;
    #             padding-bottom: 10px;
    #             border-bottom: 1px solid #34495e;
    #         }

    #         /* General QPushButton styles for navigation buttons */
    #         QPushButton {
    #             background-color: #3498db;
    #             color: white;
    #             border: none;
    #             padding: 10px 15px;
    #             text-align: left;
    #             font-size: 14px;
    #             border-radius: 5px;
    #             min-width: 150px;
    #         }

    #         QPushButton:hover {
    #             background-color: #2980b9;
    #             color: white;
    #         }

    #         QPushButton[active="true"] {
    #             background-color: #f39c12;
    #             color: #2c3e50;
    #             font-weight: bold;
    #             border-left: 5px solid #e67e22;
    #         }
    #         QPushButton[active="true"]:hover {
    #             background-color: #e67e22;
    #         }

    #         #mainTitleLabel {
    #             font-size: 28px;
    #             font-weight: bold;
    #             color: #2c3e50;
    #             margin-bottom: 20px;
    #         }

    #         QGroupBox {
    #             border: 1px solid #ccc;
    #             border-radius: 8px;
    #             margin-top: 1.5em;
    #             font-size: 16px;
    #             font-weight: bold;
    #             color: #34495e;
    #         }
    #         QGroupBox::title {
    #             subcontrol-origin: margin;
    #             left: 15px;
    #             padding: 0 5px;
    #         }

            # QLineEdit#commandLineEdit {
            #     background-color: #ffffff;
            #     border: 1px solid #ccc;
            #     border-radius: 5px;
            #     padding: 10px;
            #     font-size: 14px;
            # }
            # QLineEdit#commandLineEdit:focus {
            #     border: 1px solid #3498db;
            # }

    #         QTextEdit#terminalOutputTextEdit, QTextEdit#automationLogTextEdit { /* Applied to both terminal and automation log */
    #             background-color: #1e1e1e;
    #             color: #00ff00;
    #             font-family: 'Consolas', 'Monaco', monospace;
    #             font-size: 11pt;
    #             border-radius: 5px;
    #             padding: 10px;
    #         }

    #         QPushButton#executeButton, QPushButton#clearOutputButton {
    #             color: white;
    #             padding: 10px 20px;
    #             border-radius: 5px;
    #             font-size: 14px;
    #             border: none;
    #         }
    #         QPushButton#executeButton {
    #             background-color: #008CBA;
    #         }
    #         QPushButton#executeButton:hover {
    #             background-color: #007bb5;
    #         }
    #         QPushButton#clearOutputButton {
    #             background-color: #f44336;
    #         }
    #         QPushButton#clearOutputButton:hover {
    #             background-color: #da190b;
    #         }

    #         /* Placeholder Page Content Styling */
    #         QWidget#systemConfigurationPage QLabel,
    #         QWidget#databaseMaintenancePage QLabel,
    #         QWidget#securitySettingPage QLabel {
    #             font-size: 24px;
    #             color: #555;
    #             text-align: center;
    #             padding-top: 50px;
    #         }
    #         QWidget#systemConfigurationPage p,
    #         QWidget#databaseMaintenancePage p,
    #         QWidget#securitySettingPage p {
    #             font-size: 16px;
    #             color: #777;
    #             text-align: center;
    #         }
    #         /* Specific adjustments for AutomationPage's new title/description */
    #         QWidget#AutomationPage #sectionTitle {
    #             font-size: 28px; /* Override for specific title */
    #             font-weight: bold;
    #             color: #2c3e50;
    #             margin-bottom: 20px;
    #         }
    #         QWidget#AutomationPage p {
    #             text-align: left; /* Align paragraphs normally */
    #             padding: 0 10px; /* Add some horizontal padding for readability */
    #         }


    #         /* Table widget styling (if used in future pages) */
    #         QTableWidget {
    #             background-color: #ffffff;
    #             border: 1px solid #ccc;
    #             gridline-color: #eee;
    #             font-size: 13px;
    #             selection-background-color: #d1eaff;
    #             selection-color: #333;
    #             border-radius: 8px;
    #         }
    #         QTableWidget::item {
    #             padding: 5px;
    #         }
    #         QTableWidget::item:selected {
    #             background-color: #cceeff;
    #             color: black;
    #         }
    #         QHeaderView::section {
    #             background-color: #e6e6e6;
    #             padding: 5px;
    #             border: 1px solid #ccc;
    #             font-weight: bold;
    #             color: #333;
    #         }
    #         QHeaderView::section:horizontal {
    #             border-bottom: 2px solid #aaa;
    #         }
    #         QHeaderView::section:vertical {
    #             border-right: 2px solid #aaa;
    #         }
    #         #sectionSubTitle {
    #             font-size: 18px;
    #             font-weight: bold;
    #             color: #555;
    #             margin-bottom: 10px;
    #         }

    #         /* Buttons inside automation page */
    #         QPushButton#primaryButton { /* Reused from earlier primaryButton, adjust if needed */
    #             background-color: #2ecc71; /* Green */
    #             color: white;
    #             border: none;
    #             padding: 10px 20px;
    #             font-size: 16px;
    #             border-radius: 5px;
    #             margin-top: 5px; /* Adjust spacing */
    #             text-align: center;
    #         }
    #         QPushButton#primaryButton:hover {
    #             background-color: #27ae60;
    #         }
    #         QPushButton#secondaryButton {
    #             background-color: #95a5a6; /* Gray */
    #             color: white;
    #             border: none;
    #             padding: 8px 15px;
    #             font-size: 14px;
    #             border-radius: 5px;
    #             margin-top: 10px;
    #             text-align: center;
    #         }
    #         QPushButton#secondaryButton:hover {
    #             background-color: #7f8c8d;
    #         }


    #         /* Scrollbar styling */
    #         QScrollBar:vertical {
    #             border: 1px solid #999;
    #             background: #f0f0f0;
    #             width: 10px;
    #             margin: 0px 0px 0px 0px;
    #         }
    #         QScrollBar::handle:vertical {
    #             background: #c0c0c0;
    #             min-height: 20px;
    #             border-radius: 4px;
    #         }
    #         QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    #             background: none;
    #         }
    #         QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    #             background: none;
    #         }
    #         #automationPageScrollArea{
    #             border: none;
    #         }
    #     """)
# # --- Main Application Execution ---
# if __name__ == "__main__":
#     # Create sample files if they don't exist for easy testing
#     # These are only needed for the file-based operations in TerminalPage

#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())



import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QTextEdit, QFileDialog, QMessageBox, QGroupBox, QStackedWidget,
    QFrame, QSizePolicy, QSpacerItem, QScrollArea, QTableWidget, QHeaderView, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
import psycopg2
from psycopg2 import Error



# --- Database Connection (Global for simplicity in mock, could be passed to pages) ---
# IMPORTANT: For a production app, manage connection lifecycle more carefully
# (e.g., passing connection pool/manager to pages, or using a singleton pattern).
# Keeping it global as in your provided code for now.

host = "dpg-d1b612gdl3ps73eapfr0-a.oregon-postgres.render.com"  # Replace with your database host
database = "test_bpdd"  # Replace with your database name
user = "test"  # Replace with your database username
password = "w95g3tjqj0S9DLwNiaFEMb1SACWuuIjh"  # Replace with your database password
port = 5432  # Default PostgreSQL port, change if necessary

db_connection = None
try:
    db_connection = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port
    )
    print(f"Successfully connected to PostgreSQL database: {database}")

except Error as e:
    print(f"Error connecting to PostgreSQL database: {e}")


# --- Custom Stream for QTextEdit (Our 'Terminal') ---
class QTextEditLogger(QObject):
    append_text = pyqtSignal(str)

    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.append_text.connect(self.text_edit.append)

    def write(self, text):
        if text.strip():
            self.append_text.emit(text.strip())

    def flush(self):
        pass

# --- Page Classes ---

class TerminalPage(QWidget):
    """
    Represents the main automation terminal page with command input and output.
    Contains all the core AA logic.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- CRITICAL FIX: Define command_list and command_description as instance attributes HERE ---
        # This ensures they exist BEFORE init_ui() is called or any initial terminal messages
        # that might indirectly trigger command parsing.
        self.command_list = {
            'command_list': self.list_command,
            'help': self.display_help,
            'count_product': self.count_product,
            'count_user': self.count_user,
            'list_stock_product': self.list_product,
            'list_user': self.list_user,
            'clear_terminal': self.clear_terminal,
            # 'set_report_settings': self.set_report_settings,
            # 'generate_report': self.generate_report,
            # 'start_backup': self.backup_database,
            # 'display_logs': self.display_logs,

        }
        self.command_description = {
            'command_list': 'List of available commands.',
            'help': 'Indications on how to use the terminal.',
            'count_product': 'Display the number of products in stock.',
            'count_user': 'Display the number of users.',
            'list_stock_product': 'List of all products in stock.',
            'list_user': 'List of all users.',
            'clear_terminal': 'Clear the terminal output.',
            # 'set_report_settings': 'Set report generation settings (not implemented).',
            # 'generate_report': 'Generate a report based on current settings (not implemented).'
            # 'start_backup': 'Start a database backup.',
            # 'display_logs': 'Display system logs.'
        }
        # --- End of attribute definitions ---

        self.init_ui() # Now it's safe to call init_ui()

        # Redirect stdout and stderr for this specific page's terminal output
        self.text_edit_logger = QTextEditLogger(self.terminal_output)
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = self.text_edit_logger
        sys.stderr = self.text_edit_logger

        self.terminal_output.append("Welcome to SGE Warehouse Automation Terminal!")
        self.terminal_output.append("Type 'A --command_list' in the command input to see available commands.")


    def init_ui(self):
        page_layout = QVBoxLayout(self) # Layout directly on the widget
        page_layout.setContentsMargins(0, 0, 0, 0) # Managed by parent container layout
        page_layout.setSpacing(15)

        # --- Command Input GroupBox ---
        command_group_box = QGroupBox("Command Input")
        command_group_box.setObjectName("commandInputGroupBox") # For QSS
        command_layout = QHBoxLayout(command_group_box) # Layout directly on QGroupBox

        self.command_line_edit = QLineEdit()
        self.command_line_edit.setPlaceholderText("Type command (e.g., sac --command_list)")
        self.command_line_edit.setObjectName("commandLineEdit") # For QSS
        self.command_line_edit.returnPressed.connect(self.execute_command)
        command_layout.addWidget(self.command_line_edit)

        execute_button = QPushButton("Execute Command")
        execute_button.setObjectName("executeButton") # For QSS
        execute_button.clicked.connect(self.execute_command)
        command_layout.addWidget(execute_button)

        page_layout.addWidget(command_group_box)

        # --- Terminal Output GroupBox ---
        output_group_box = QGroupBox("Output (Terminal)")
        output_group_box.setObjectName("terminalOutputGroupBox") # For QSS
        output_layout = QVBoxLayout(output_group_box) # Layout directly on QGroupBox

        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setObjectName("terminalOutputTextEdit") # For QSS
        output_layout.addWidget(self.terminal_output)

        clear_button = QPushButton("Clear Output")
        clear_button.setObjectName("clearOutputButton") # For QSS
        clear_button.clicked.connect(self.clear_terminal)
        output_layout.addWidget(clear_button, alignment=Qt.AlignmentFlag.AlignRight)

        page_layout.addWidget(output_group_box)

    # --- Core Automation Application (AA) Logic as methods of TerminalPage ---

    def execute_command(self):
        command_line = self.command_line_edit.text().strip()

        if not command_line:
            return

        self.command_line_edit.clear() # Clear input after execution
        self.terminal_output.append(f"\n> {command_line}") # Echo the command

        parts = command_line.split(' --') # Split by ' --' to separate "sac" from command
        # Check if it starts with 'sac' and has at least one '--' separated part
        if len(parts) < 2 or parts[0].strip().lower() != 'sac':
            self.unknown_command()
            return

        command = parts[1].strip() # The actual command part after 'sac --'

        # Execute the command using the dictionary mapping
        # .get(key, default_value_if_not_found)
        self.command_list.get(command, self.unknown_command)()

    def list_command(self):
        self.terminal_output.append("\n--- Available commands: ---")
        # Corrected iteration: iterate over items() to get both key and value
        for cmd, description in self.command_description.items():
            self.terminal_output.append(f"- {cmd}:\t{description}")
        self.terminal_output.append("---------------------------\n")

    def unknown_command(self):
        self.terminal_output.append("Unknown command!")
        self.terminal_output.append("Type 'sac --command_list' for a list of available commands.")
        self.terminal_output.append("Type 'sac --help' for instructions on how to use the terminal.")

    def display_help(self):
        self.terminal_output.append("\n--- Terminal Usage Help ---")
        self.terminal_output.append("Commands start with 'sac --' followed by the command name.")
        self.terminal_output.append("Example: sac --command_list")
        self.terminal_output.append("For commands requiring arguments, specify them after the command name.")
        self.terminal_output.append("---------------------------\n")

    def count_product(self):
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute("SELECT total();") # Assuming a 'products' table
                count = cursor.fetchone()[0]
                self.terminal_output.append(f"Number of products in stock: {count}")
            except Error as e:
                self.terminal_output.append(f"Error counting products: {e}")
            finally:
                if cursor:
                    cursor.close()
        else:
            self.terminal_output.append("Database connection not established. Cannot count products.")

    def count_user(self):
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM users;") # Assuming a 'users' table
                count = cursor.fetchone()[0]
                self.terminal_output.append(f"Number of users: {count}")
            except Error as e:
                self.terminal_output.append(f"Error counting users: {e}")
            finally:
                if cursor:
                    cursor.close()
        else:
            self.terminal_output.append("Database connection not established. Cannot count users.")

    def list_product(self):
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute("SELECT product_id, name, quantity FROM products;") # Assuming 'products' table
                products = cursor.fetchall()
                self.terminal_output.append("\n--- Products in Stock ---")
                if products:
                    for product in products:
                        self.terminal_output.append(f"ID: {product[0]}, Name: {product[1]}, Quantity: {product[2]}")
                else:
                    self.terminal_output.append("No products found.")
                self.terminal_output.append("---------------------------\n")
            except Error as e:
                self.terminal_output.append(f"Error listing products: {e}")
            finally:
                if cursor:
                    cursor.close()
        else:
            self.terminal_output.append("Database connection not established. Cannot list products.")

    def list_user(self):
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute("SELECT username, email FROM users;") # Assuming 'users' table
                users = cursor.fetchall()
                self.terminal_output.append("\n--- Users List ---")
                if users:
                    for user_data in users:
                        self.terminal_output.append(f"Username: {user_data[0]}, Email: {user_data[1]}")
                else:
                    self.terminal_output.append("No users found.")
                self.terminal_output.append("-------------------\n")
                cursor.close()
            except Error as e:
                self.terminal_output.append(f"Error listing users: {e}")
            finally:
                if cursor:
                    cursor.close()
        else:
            self.terminal_output.append("Database connection not established. Cannot list users.")

    def clear_terminal(self):
        self.terminal_output.clear()
        self.terminal_output.append("Terminal cleared.")


    def __del__(self):
        """Restore original stdout/stderr when TerminalPage is destroyed."""
        # Check if attributes exist before restoring, for safer shutdown
        if hasattr(self, '_original_stdout') and self._original_stdout is not None:
            sys.stdout = self._original_stdout
        if hasattr(self, '_original_stderr') and self._original_stderr is not None:
            sys.stderr = self._original_stderr


# Placeholder Page Classes
class AutomationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AutomationPage")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # Create a QScrollArea
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True) # Allow the widget inside to resize with the scroll area
        scroll_area.setObjectName("automationPageScrollArea") # For QSS if needed

        # Create a container widget for the scroll area's content
        scroll_content_widget = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content_widget)
        scroll_content_layout.setContentsMargins(10, 10, 10, 10) # Control padding via content_area_layout in MainWindow
        scroll_content_layout.setSpacing(10) # Spacing between elements within the scrollable area

        # Title
        title_label = QLabel("<h3>Warehouse Automation Workflows</h3>")
        title_label.setObjectName("sectionTitle") # Reusing QSS ID for a section title
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # PyQt6 change: Qt.AlignCenter -> Qt.AlignmentFlag.AlignCenter
        scroll_content_layout.addWidget(title_label)

        # Description
        description_label = QLabel(
            "<p>Manage and initiate automated tasks within the warehouse management system.</p>"
            "<p>Select an automation task below to view its details or trigger its execution.</p>"
        )
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # PyQt6 change: Qt.AlignCenter -> Qt.AlignmentFlag.AlignCenter
        description_label.setWordWrap(True)
        scroll_content_layout.addWidget(description_label)

        # Automation Tasks Section
        tasks_group_box = QGroupBox("Available Automation Tasks")
        tasks_group_box.setObjectName("automationTasksGroupBox") # Unique ID for QSS
        tasks_layout = QVBoxLayout(tasks_group_box)
        tasks_layout.setSpacing(10)

        # Automation Buttons
        self.btn_generate_monthly_report = QPushButton("Generate Report")
        self.btn_generate_monthly_report.setObjectName("primaryButton")
        self.btn_generate_monthly_report.clicked.connect(self._generate_monthly_report)
        tasks_layout.addWidget(self.btn_generate_monthly_report)

        self.btn_low_stock_notification = QPushButton("Trigger Low Stock Notifications")
        self.btn_low_stock_notification.setObjectName("primaryButton")
        self.btn_low_stock_notification.clicked.connect(self._trigger_low_stock_notifications)
        tasks_layout.addWidget(self.btn_low_stock_notification)

        # Add a few more placeholder buttons to ensure scrolling is evident
        self.btn_data_backup = QPushButton("Perform Database Backup")
        self.btn_data_backup.setObjectName("primaryButton")
        self.btn_data_backup.clicked.connect(lambda: self._log_automation_event("Database backup initiated."))
        tasks_layout.addWidget(self.btn_data_backup)

        self.btn_audit_log_cleanup = QPushButton("Clean Up Old Audit Logs")
        self.btn_audit_log_cleanup.setObjectName("primaryButton")
        self.btn_audit_log_cleanup.clicked.connect(lambda: self._log_automation_event("Old audit logs cleanup initiated."))
        tasks_layout.addWidget(self.btn_audit_log_cleanup)

        scroll_content_layout.addWidget(tasks_group_box)

        # Automation Log/Status Area
        log_group_box = QGroupBox("Automation Log")
        log_group_box.setObjectName("automationLogGroupBox")
        log_layout = QVBoxLayout(log_group_box)

        self.automation_log_output = QTextEdit()
        self.automation_log_output.setReadOnly(True)
        self.automation_log_output.setObjectName("automationLogTextEdit") # Specific ID for QSS
        self.automation_log_output.setPlaceholderText("Automation log will appear here...")
        log_layout.addWidget(self.automation_log_output)

        clear_log_button = QPushButton("Clear Automation Log")
        clear_log_button.setObjectName("clearOutputButton") # Reusing secondaryButton style
        clear_log_button.clicked.connect(self.automation_log_output.clear)
        log_layout.addWidget(clear_log_button, alignment=Qt.AlignmentFlag.AlignRight) # PyQt6 change: Qt.AlignRight -> Qt.AlignmentFlag.AlignRight

        scroll_content_layout.addWidget(log_group_box)

        # scroll_content_layout.addStretch(1) # Pushes content to the top within the scroll area

        # Set the content widget for the scroll area
        scroll_area.setWidget(scroll_content_widget)

        # Add the scroll area to the main layout of the AutomationPage
        main_layout.addWidget(scroll_area)

    # --- Automation Task Methods (placeholders) ---
    def _log_automation_event(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.automation_log_output.append(f"[{timestamp}] {message}")

    def _generate_monthly_report(self):
        self._log_automation_event("Generating monthly sales report...")
        QMessageBox.information(self, "Automation Task", "Monthly Sales Report generation task initiated. (Check log for details)")
        # Simulate report generation time
        QApplication.processEvents() # Keep UI responsive
        # In a real app, this would involve data querying and report formatting
        self._log_automation_event("Monthly sales report generated and saved.")

    def _trigger_low_stock_notifications(self):
        self._log_automation_event("Triggering low stock notifications...")
        QMessageBox.information(self, "Automation Task", "Low Stock Notifications triggered. (Check log for details)")
        # This would typically involve checking inventory levels and sending alerts
        self._log_automation_event("Low stock notifications sent to relevant personnel.")

# --- Main Application Window ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automation Dashboard")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

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
        self.logged_in_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.sidebar_layout.addWidget(self.logged_in_label)

        self.sidebar_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # Navigation buttons and their corresponding page instances
        self.nav_buttons = {}
        self.pages = [] # List to hold instances of QWidget pages (matched to stacked_content_widget indices)

        self.stacked_content_widget = QStackedWidget()

        # Define navigation items and create their pages
        nav_items_map = {
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

        # 2. Main Content Area
        self.content_area_container = QWidget()
        self.content_area_container.setObjectName("contentAreaContainer")
        self.content_area_layout = QVBoxLayout(self.content_area_container)
        self.content_area_layout.setContentsMargins(40, 30, 40, 30)
        self.content_area_layout.setSpacing(25)

        self.main_title_label = QLabel("Account Settings")
        self.main_title_label.setObjectName("mainTitleLabel")
        self.content_area_layout.addWidget(self.main_title_label)

        self.content_area_layout.addWidget(self.stacked_content_widget)

        # Set initial page and active button
        self.stacked_content_widget.setCurrentIndex(0)
        initial_nav_button_text = list(nav_items_map.keys())[0]
        self.nav_buttons[initial_nav_button_text].setProperty("active", True)
        self.nav_buttons[initial_nav_button_text].style().polish(self.nav_buttons[initial_nav_button_text])
        self.main_title_label.setText(initial_nav_button_text)

        self.main_layout.addWidget(self.sidebar_frame)
        self.main_layout.addWidget(self.content_area_container)

    def _on_nav_button_clicked(self, index, clicked_button):
        """
        Handles navigation button clicks, switching the QStackedWidget page
        and updating button active states.
        """
        self.main_title_label.setText(clicked_button.text())
        self.stacked_content_widget.setCurrentIndex(index)

        for text, btn_widget in self.nav_buttons.items():
            if btn_widget == clicked_button:
                btn_widget.setProperty("active", True)
            else:
                btn_widget.setProperty("active", False)
            btn_widget.style().polish(btn_widget)

    def _apply_styles(self):
        """
        Applies Qt Style Sheets (QSS) for the application's look and feel.
        """
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

            /* General QPushButton styles for navigation buttons */
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
                color: white;
            }

            QPushButton[active="true"] {
                background-color: #f39c12;
                color: #2c3e50;
                font-weight: bold;
                border-left: 5px solid #e67e22;
            }
            QPushButton[active="true"]:hover {
                background-color: #e67e22;
            }

            #mainTitleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
            }

            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 8px;
                margin-top: 1.5em;
                font-size: 16px;
                font-weight: bold;
                color: #34495e;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }

            QLineEdit#commandLineEdit {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                color: #2c3e50;
            }
            QLineEdit#commandLineEdit:focus {
                border: 1px solid #3498db;
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

            /* Placeholder Page Content Styling */
            QWidget#systemConfigurationPage QLabel,
            QWidget#databaseMaintenancePage QLabel,
            QWidget#securitySettingPage QLabel {
                font-size: 24px;
                color: #555;
                text-align: center;
                padding-top: 50px;
            }
            QWidget#systemConfigurationPage p,
            QWidget#databaseMaintenancePage p,
            QWidget#securitySettingPage p {
                font-size: 16px;
                color: #777;
                text-align: center;
            }
            /* Specific adjustments for AutomationPage's new title/description */
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


            /* Scrollbar styling */
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
            #automationPageScrollArea{
                border: none;
            }
        """)
# --- Main Application Execution ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))  # Dialog background
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#232946"))  # Dialog text
    palette.setColor(QPalette.ColorRole.Base, QColor("#F8F9FA"))  # Input fields
    palette.setColor(QPalette.ColorRole.Text, QColor("#232946"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#6C63FF"))  # Accent for buttons
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#6C63FF"))  # Selection color
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())