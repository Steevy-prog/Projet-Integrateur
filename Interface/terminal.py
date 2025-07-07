import sys, os
import datetime
import subprocess
import gzip
import logging
import stat
import shutil
from docx import Document
from docx.shared import Inches
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,QGridLayout,
    QLineEdit, QLabel, QTextEdit, QFileDialog, QMessageBox, QGroupBox, QStackedWidget,
    QFrame, QSizePolicy, QSpacerItem, QScrollArea, QTableWidget, QHeaderView, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QDir, QThread, QCoreApplication, pyqtSlot
from PyQt6.QtGui import QPalette, QColor
import psycopg2
from psycopg2 import Error

# from db_connection import db_connection
# from db_connection import host, database, user, password, port
from db_connection import ConnectionDB
Connection = ConnectionDB()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseBackupManager(QObject):
    """
    Manages PostgreSQL database backup operations.

    This class does not inherit from QMainWindow or QWidget. It uses QFileDialog
    to prompt the user for a backup directory and executes the pg_dump command.
    It emits signals to communicate the backup status back to the GUI.
    """

    # Signals to communicate backup status
    # These signals allow the manager to communicate back to your GUI without
    # directly interacting with GUI elements, promoting better separation of concerns.
    backup_started = pyqtSignal()
    backup_finished = pyqtSignal(bool, str) # bool: success, str: message
    backup_error = pyqtSignal(str) # str: error message

    def __init__(self, parent_widget: QWidget = None, db_host: str = 'localhost',
                 db_port: str = '5432', db_user: str = 'postgres',
                 db_password: str = '', db_name: str = 'your_database_name'):
        """
        Initializes the DatabaseBackupManager.

        Args:
            parent_widget: The parent QWidget that will own the QFileDialog.
                           This is important for ensuring the QFileDialog appears
                           correctly centered and modal relative to your main window.
                           Pass `self` from your main QWidget/QMainWindow.
            db_host (str): PostgreSQL database host (e.g., 'localhost', 'your_remote_ip').
            db_port (str): PostgreSQL database port (default is '5432').
            db_user (str): PostgreSQL database username.
            db_password (str): PostgreSQL database password.
            db_name (str): PostgreSQL database name to backup.
        """
        # QObject can take a parent, which is good for object ownership and cleanup
        super().__init__(parent_widget)
        self.parent_widget = parent_widget

        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name

        # Initialize thread and worker, but don't start them yet
        self.thread = None
        self.worker = None
        
        logger.info(f"DatabaseBackupManager initialized for DB: {db_name}@{db_host}:{db_port}")

    def _get_backup_directory(self) -> str:
        """
        Opens a QFileDialog to let the user choose a directory for the backup.

        Returns:
            str: The selected directory path, or an empty string if the dialog was cancelled.
        """
        logger.info("Opening QFileDialog for backup directory selection...")
        # QFileDialog.getExistingDirectory returns a tuple (directory_path, selected_filter)
        # We only need the directory path.
        directory = QFileDialog.getExistingDirectory(
            self.parent_widget,  # Parent widget for the dialog to ensure proper modality
            "Select Directory for Database Backup", # Dialog title
            os.path.expanduser("~") # Starting directory (e.g., user's home directory)
        )
        if directory:
            logger.info(f"Selected backup directory: {directory}")
        else:
            logger.info("Backup directory selection cancelled by user.")
        return directory

    def _generate_backup_filename(self) -> str:
        """
        Generates a backup filename with the current date.

        Returns:
            str: The generated filename (e.g., "mydatabase_backup_2025-07-04.sql").
        """
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"{self.db_name}_backup_{current_date}.sql"
        logger.info(f"Generated backup filename: {filename}")
        return filename

    def perform_backup(self):
        """
        Initiates the database backup process.

        This method should be connected to a button's `clicked` signal in your GUI.
        It will:
        1. Emit `backup_started` signal.
        2. Prompt the user to select a backup directory using `QFileDialog`.
        3. Generate a date-stamped filename.
        4. Construct and execute the `pg_dump` command as a subprocess.
        5. Emit `backup_finished` (success/failure) or `backup_error` signals
           based on the outcome of the `pg_dump` command.
        """
        
        # self.backup_started.emit()
        logger.info("Backup process initiated.")

        backup_dir = self._get_backup_directory()
        if not backup_dir:
            # If user cancels directory selection, emit error and finish signals
            self.backup_error.emit("Backup cancelled: No directory selected.")
            self.backup_finished.emit(False, "Backup cancelled by user.")
            return

        backup_filename = self._generate_backup_filename()
        backup_filepath = os.path.join(backup_dir, backup_filename)

        self.thread = QThread()
        self.worker = BackupWorker(
            db_host=self.db_host,
            db_port=self.db_port,
            db_user=self.db_user,
            db_password=self.db_password,
            db_name=self.db_name,
            backup_filepath=backup_filepath
        )
        
 
      
        # Move the worker to the new thread
        self.worker.moveToThread(self.thread)

        # Connect signals:
        # 1. When the thread starts, the worker's run_backup_task method should be called.
        self.thread.started.connect(self.worker.run_backup_task)

        # 2. Connect worker's signals to manager's signals (proxy them to the GUI)
        self.worker.backup_started.connect(self.backup_started)
        self.worker.backup_finished.connect(self.backup_finished)
        self.worker.backup_error.connect(self.backup_error)

        # 3. Clean up the thread and worker when the task is finished
        self.worker.backup_finished.connect(self.thread.quit)
        self.worker.backup_finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread
        self.thread.start()
        logger.info("Backup thread started.")



class BackupWorker(QThread):
    """
    A QThread subclass to run the database backup operation in the background,
    preventing the GUI from freezing.
    """
    # Signals to communicate with the main thread (GUI)
    backup_started = pyqtSignal()
    backup_finished = pyqtSignal(bool, str) # bool: success, str: message
    backup_error = pyqtSignal(str) # str: error message
    
    def __init__(self, db_host: str, db_port: str, db_user: str,
                 db_password: str, db_name: str, backup_filepath: str):
        super().__init__()
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.backup_filepath = backup_filepath
        # Ensure the logger is connected to the update_log signal
        # This is a bit tricky as the handler needs to be initialized with the QTextEdit
        # We will make sure the main GUI passes a logger that's already configured.

    def run_backup_task(self):
        """
        The main method of the thread, executed when thread.start() is called.
        It calls the actual backup function.
        """
        self.backup_started.emit()
        logger.info(f"Backup task started in worker thread for {self.db_name}.")

        pg_dump_command = [
            "pg_dump",
            "-h", self.db_host,
            "-p", self.db_port,
            "-U", self.db_user,
            "-d", self.db_name,
            "-F", "p", # Plain-text SQL dump format
            "-f", self.backup_filepath # Output file path
        ]

        env = os.environ.copy()
        if self.db_password:
            env["PGPASSWORD"] = self.db_password
            logger.info("PGPASSWORD environment variable set for pg_dump execution in worker.")

        logger.info(f"Executing pg_dump command in worker: {' '.join(pg_dump_command)}")
        try:
            result = subprocess.run(
                pg_dump_command,
                env=env,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                logger.info(f"Database backup successful: {self.backup_filepath}")
                self.backup_finished.emit(True, f"Backup created at: {self.backup_filepath}")
            else:
                error_message_detail = (f"pg_dump failed with exit code {result.returncode}.\n"
                                        f"STDOUT: {result.stdout.strip()}\n"
                                        f"STDERR: {result.stderr.strip()}")
                logger.error(f"Database backup failed: {error_message_detail}")
                user_error_message = result.stderr.strip() or result.stdout.strip() or "Unknown pg_dump error."
                self.backup_error.emit(f"Backup failed: {user_error_message}")
                self.backup_finished.emit(False, f"Backup failed. Check application logs for details.")

        except FileNotFoundError:
            error_msg = ("Error: 'pg_dump' command not found. "
                         "Please ensure PostgreSQL client tools are installed and 'pg_dump' is in your system's PATH.")
            logger.critical(error_msg)
            self.backup_error.emit(error_msg)
            self.backup_finished.emit(False, "Backup failed: pg_dump not found.")
        except Exception as e:
            error_msg = f"An unexpected Python error occurred during backup: {e}"
            logger.critical(error_msg, exc_info=True)
            self.backup_error.emit(error_msg)
            self.backup_finished.emit(False, "Backup failed due to an unexpected internal error.")
# --- Page Classes ---

class TerminalPage(QWidget):
    """
    Represents the main automation terminal page with command input and output.
    Contains all the core AA logic.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        
        self.connection_info = Connection.connection()
        self.db_connection = self.connection_info['db_connection']
        
      
        self.command_list = {
            'command_list': self.list_command,
            'help': self.display_help,
            'count_product': self.count_product,
            'count_user': self.count_user,
            'list_stock_product': self.list_product,
            'list_user': self.list_user,
            'clear_terminal': self.clear_terminal,
            'start_backup': self.start_backup,
            'display_all_logs': self.display_all_logs,
            'display_pre_logs': self.display_pre_logs,
            'display_post_logs': self.display_post_logs,
            'display_range_logs': self.display_range_logs

        }
        self.command_description = {
            'command_list': 'List of available commands.',
            'help': 'Indications on how to use the terminal.',
            'count_product': 'Display the number of products in stock.',
            'count_user': 'Display the number of users.',
            'list_stock_product': 'List of all products in stock.',
            'list_user': 'List of all users.',
            'clear_terminal': 'Clear the terminal output.',
            'start_backup': 'Start a database backup.',
            'display_all_logs': 'Display all system logs.',
            'display_pre_logs': 'Display previous system logs as from a specific date',
            'display_post_logs': 'Display system logs starting from a specific date',
            'display_range_logs': 'Display system logs generated between two dates'
        }
        # --- End of attribute definitions ---
        
        self.backup_manager = DatabaseBackupManager(
               parent_widget=self, # Pass 'self' (your QWidget/QMainWindow instance) as the parent
               db_host=self.connection_info['host'],
               db_port=self.connection_info['port'],
               db_user=self.connection_info['user'],
               db_password=self.connection_info['password'],
               db_name=self.connection_info['database']
           )

        self.backup_manager.backup_started.connect(self.on_backup_started)
        self.backup_manager.backup_finished.connect(self.on_backup_finished)
        self.backup_manager.backup_error.connect(self.on_backup_error)

        self.init_ui()
        
        
        self.terminal_output.append("Welcome to SGE Warehouse Automation Terminal!")
        self.terminal_output.append("Type 'sac --command_list' in the command input to see available commands.")

       

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
        
        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # Local Data Backup Path
        form_layout.addWidget(QLabel("Local Path To Store Reports:"), 0, 0)
        self.report_path_input = QLineEdit()
        self.report_path_input.setPlaceholderText("e.g., C:/Documents/Reports")
        form_layout.addWidget(self.report_path_input, 0, 1)

        self.browse_report_button = QPushButton("Browse...")
        self.browse_report_button.setObjectName("secondaryButton")
        self.browse_report_button.clicked.connect(self._browse_report_path)
        form_layout.addWidget(self.browse_report_button, 0, 2)

        page_layout.addLayout(form_layout)
 

    # --- Core Automation Application (AA) Logic as methods of TerminalPage ---

    def execute_command(self):
        try:
            command_line = self.command_line_edit.text().strip()
            parameter_1 = None
            parameter_2 = None
            if not command_line:
                return

            self.command_line_edit.clear() # Clear input after execution
            self.terminal_output.append(f"\n> {command_line}") # Echo the command

            parts = command_line.split(' --') # Split by ' --' to separate "sac" from command
            # Check if it starts with 'sac' and has at least one '--' separated part
            command = parts[1].strip()
            if len(parts) < 2 or parts[0].strip().lower() != 'sac':
                self.unknown_command()
                return
            if len(parts) == 3:
                parameter_1 = parts[2].strip()
                self.command_list.get(command, self.unknown_command)(parameter_1)
                return
            elif len(parts) == 4:
                parameter_1 = parts[2].strip()
                parameter_2 = parts[3].strip()
                self.command_list.get(command, self.unknown_command)(parameter_1, parameter_2)
                return
            elif len(parts) == 2:
                self.command_list.get(command, self.unknown_command)()
            else:
                self.unknown_command()
                return
        except Exception as e:
            self.terminal_output.append(f"Error executing command: {e}")

    def list_command(self):
        self.terminal_output.append("\n--- Available commands: ---")
        # Corrected iteration: iterate over items() to get both key and value
        for cmd, description in self.command_description.items():
            self.terminal_output.append(f"- {cmd}: {description}")
        self.terminal_output.append("---------------------------\n")

    def unknown_command(self):
        self.terminal_output.append("Unknown command!")
        self.terminal_output.append("Type 'sac --command_list' for a list of available commands.")
        self.terminal_output.append("Type 'sac --help' for instructions on how to use the terminal.")

    def display_help(self):
        self.terminal_output.append("\n--- Terminal Usage Help ---")
        self.terminal_output.append("Commands start with 'sac --' followed by the command name.")
        self.terminal_output.append("Example: sac --command_list")
        self.terminal_output.append("For commands requiring arguments, specify them after the command name seperating each with '(space)--'. Example: sac --command_name --arguement_1 --argument_2 and so on")
        self.terminal_output.append("---------------------------\n")

            
    def display_all_logs(self):
            try:
                if not self.db_connection:
                    self.connection_info = Connection.connection()
                    self.db_connection = self.connection_info['db_connection']
                else:
                    cursor = self.db_connection.cursor()
                    cursor.execute(f"SELECT TO_CHAR(_timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp, _level, _message FROM \"EMIR\".Logs_EVA() ORDER BY timestamp;")  # Assuming a 'logs' table
                    logs = cursor.fetchall()
                    self.db_connection.commit()
                    self.terminal_output.append("\n--- ALl System Logs ---")
                    if logs:
                        for log in logs:
                            self.terminal_output.append(f"{log[0]} <b>[{log[1]}]</b>: {log[2]}")  # Adjust based on log structure
                    else:
                        self.terminal_output.append("No logs found.")
                    self.terminal_output.append("-------------------\n")
                    if logs:
                        reply = QMessageBox.question(self,'Report Suggestion',
                            f"Do you want a report document of these logs?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No
                                            )
                        if reply == QMessageBox.StandardButton.Yes:
                            self.generate_logs_report(logs)
            except Error as e:
                self.db_connection.rollback()
                self.terminal_output.append(f"Error retrieving logs: {e}")
            finally:
                if cursor:
                    cursor.close()
    
    def display_pre_logs(self, date):
        
            try:
                if not self.db_connection:
                    self.connection_info = Connection.connection()
                    self.db_connection = self.connection_info['db_connection']
                else:
                    cursor = self.db_connection.cursor()
                    cursor.execute(f"SELECT TO_CHAR(_timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp, _level, _message FROM \"EMIR\".Logs_getlower('{date}':: timestamp)")
                    logs = cursor.fetchall()
                    self.terminal_output.append(f"\n--- System Logs before {date} ---")
                    if logs:
                        for log in logs:
                            self.terminal_output.append(f"{log[0]} <b>[{log[1]}]</b>: {log[2]}")  # Adjust based on log structure
                    else:
                        self.terminal_output.append("No logs found.")
                    self.terminal_output.append("-------------------\n")
                    if logs:
                        reply = QMessageBox.question(self,'Report Suggestion',
                            f"Do you want a report document of these logs?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No
                                            )
                        if reply == QMessageBox.StandardButton.Yes:
                            self.generate_logs_report(logs)
            except Exception as e:
                self.db_connection.rollback()
                self.terminal_output.append(f"Error retrieving logs: {e}")
            finally:
                if cursor:
                    cursor.close()
        # else:
        #     self.terminal_output.append("Database connection not established. Cannot retrieve logs.")
    
    def display_post_logs(self, date):
    
            try:
                if not self.db_connection:
                    self.connection_info = Connection.connection()
                    self.db_connection = self.connection_info['db_connection']
                else:
                    cursor = self.db_connection.cursor()
                    cursor.execute(f"SELECT TO_CHAR(_timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp, _level, _message FROM \"EMIR\".Logs_gethigher('{date}':: timestamp)")
                    logs = cursor.fetchall()
                    self.db_connection.commit()
                    self.terminal_output.append(f"\n--- System Logs after {date} ---")
                    if logs:
                        for log in logs:
                            self.terminal_output.append(f"{log[0]} <b>[{log[1]}]</b>: {log[2]}")  # Adjust based on log structure
                    else:
                        self.terminal_output.append("No logs found.")
                    self.terminal_output.append("-------------------\n")
                    if logs:
                        reply = QMessageBox.question(self,'Report Suggestion',
                            f"Do you want a report document of these logs?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No
                                            )
                        if reply == QMessageBox.StandardButton.Yes:
                            self.generate_logs_report(logs)
            except Error as e:
                self.db_connection.rollback()
                self.terminal_output.append(f"Error retrieving logs: {e}")
            finally:
                if cursor:
                    cursor.close()
        # else:
        #     self.terminal_output.append("Database connection not established. Cannot retrieve logs.")
    
    
    def display_range_logs(self, date_1, date_2):
    
            try:
                if not self.db_connection:
                    self.connection_info = Connection.connection()
                    self.db_connection = self.connection_info['db_connection']
                else:
                    cursor = self.db_connection.cursor()
                    cursor.execute(f"SELECT TO_CHAR(_timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp, _level, _message FROM \"EMIR\".Logs_get('{date_1}':: timestamp, '{date_2}':: timestamp)")
                    logs = cursor.fetchall()
                    self.db_connection.commit()
                    self.terminal_output.append(f"\n--- System Logs between {date_1} and {date_2} ---")
                    if logs:
                        for log in logs:
                            self.terminal_output.append(f"{log[0]} <b>[{log[1]}]</b>: {log[2]}")  # Adjust based on log structure
                    else:
                        self.terminal_output.append("No logs found.")
                    self.terminal_output.append("-------------------\n")
                    if logs:
                        reply = QMessageBox.question(self,'Report Suggestion',
                            f"Do you want a report document of these logs?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No
                                            )
                        if reply == QMessageBox.StandardButton.Yes:
                            self.generate_logs_report(logs)
            except Error as e:
                self.db_connection.rollback()
                self.terminal_output.append(f"Error retrieving logs: {e}")
            finally:
                if cursor:
                    cursor.close()
        # else:
        #     self.terminal_output.append("Database connection not established. Cannot retrieve logs.")
    
    def generate_logs_report(self, data):
        current_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"report-{current_date}.docx"
        self._browse_report_path()
        
        if self.report_path_input.text():
            filename = os.path.join(self.report_path_input.text(), filename)
        else:
            QMessageBox.warning(self,'No Path', 'Please select a directory to save the reports')
        try:
            document = Document()
            document.add_heading('Product Report', level=1)
            if not data:
                document.add_paragraph("No data available to generate report.")
                document.save(filename)
                return
            
            table = document.add_table(rows=1, cols=len(data[0]))
            table.style = 'Table Grid' # Apply a basic style

            # Add header row
            hdr_cells = table.rows[0].cells
            headers = ["Date-Time", "Log-Type", "Message"]
            for i, header_text in enumerate(headers):
                hdr_cells[i].text = header_text

            # Add data rows
            for row_data in data:
                row_cells = table.add_row().cells
                for i, cell_value in enumerate(row_data):
                    row_cells[i].text = str(cell_value)

            document.add_paragraph(f'\nReport generated on {current_date}') # You can dynamically add date
            document.save(filename)

            self.terminal_output.append(f'Logs report generated an saved as {filename}')
        except Exception as e:
            # db_connection.rollback()
            QMessageBox.information(self, 'error', f'{e}')
            
            
    def _browse_report_path(self):
        """
        Opens a directory dialog to select the backup path.
        """
        # QDir.homePath() is correct for PyQt6
        current_path = self.report_path_input.text() if self.report_path_input.text() else QDir.homePath()
        
        directory = QFileDialog.getExistingDirectory(self, "Select Report Directory", current_path)
        if directory:
            self.report_path_input.setText(directory)

    def count_product(self):
            try:
                if not self.db_connection:
                    self.connection_info = Connection.connection()
                    self.db_connection = self.connection_info['db_connection']
                else:
                    cursor = self.db_connection.cursor()
                    cursor.execute("SELECT \"EMIR\".produitsnum();") # Assuming a 'products' table
                    count = cursor.fetchone()[0]
                    self.db_connection.commit()
                    self.terminal_output.append(f"Number of products in stock: {count}")
            except Error as e:
                self.db_connection.rollback()
                self.terminal_output.append(f"Error counting products: {e}")
            finally:
                if cursor:
                    cursor.close()
        # else:
        #     self.terminal_output.append("Database connection not established. Cannot count products.")

    def count_user(self):
            try:
                if not self.db_connection:
                    self.connection_info = Connection.connection()
                    self.db_connection = self.connection_info['db_connection']
                else:
                    cursor = self.db_connection.cursor()
                    cursor.execute("SELECT COUNT(*) FROM \"SCA\".individu;") # Assuming a 'users' table
                    count = cursor.fetchone()[0]
                    self.db_connection.commit()
                    self.terminal_output.append(f"Number of users: {count}")
            except Error as e:
                self.db_connection.rollback()
                self.terminal_output.append(f"Error counting users: {e}")
            finally:
                if cursor:
                    cursor.close()
        # else:
        #     self.terminal_output.append("Database connection not established. Cannot count users.")

    def list_product(self):
            try:
                if not self.db_connection:
                    self.connection_info = Connection.connection()
                    self.db_connection = self.connection_info['db_connection']
                else:
                    cursor = self.db_connection.cursor()
                    cursor.execute("SELECT idproduit, nom, prix_unitaire FROM \"SCA\".Produit;") # Assuming 'products' table
                    products = cursor.fetchall()
                    self.db_connection.commit()
                    self.terminal_output.append("\n--- Products in Stock ---")
                    if products:
                        for product in products:
                            self.terminal_output.append(f"""
ID: {product[0]},
Name: {product[1]},
Unit Price: {product[2]}
{'*' * 100}
""")
                    else:
                        self.terminal_output.append("No products found.")
                    self.terminal_output.append("---------------------------\n")
            except Error as e:    
                self.db_connection.rollback()
                self.terminal_output.append(f"Error listing products: {e}")
            finally:
                if cursor:
                    cursor.close()
        # else:
        #     self.terminal_output.append("Database connection not established. Cannot list products.")

    def list_user(self):
            try:
                if not self.db_connection:
                    self.connection_info = Connection.connection()
                    self.db_connection = self.connection_info['db_connection']
                else:
                    cursor = self.db_connection.cursor()
                    cursor.execute("SELECT nom, adresse, telephone, prenom FROM \"SCA\".individu;") # Assuming 'users' table
                    users = cursor.fetchall()
                    self.db_connection.commit()
                    self.terminal_output.append("\n--- Users List ---")
                    if users:
                        for user_data in users:
                            self.terminal_output.append(f"""
first_name: {user_data[0]}, 
Last_name: {user_data[3]}
Address: {user_data[1]},
Phone: {user_data[2]}
{'*' * 100}
""")
                    else:
                        self.terminal_output.append("No users found.")
                    self.terminal_output.append("-------------------\n")
                    cursor.close()
            except Error as e:
                self.db_connection.rollback()
                self.terminal_output.append(f"Error listing users: {e}")
            finally:
                if cursor:
                    cursor.close()
        # else:
        #     self.terminal_output.append("Database connection not established. Cannot list users.")

    def clear_terminal(self):
        self.terminal_output.clear()
        self.terminal_output.append("Terminal cleared.")

    def start_backup(self):
        self.backup_manager.perform_backup()
        
    @pyqtSlot()
    def on_backup_started(self):
         """Slot to handle when the backup process begins."""
         
    @pyqtSlot(bool, str)
    def on_backup_finished(self, success: bool, message: str):
        """Slot to handle when the backup process finishes."""
        
        msg_box = QMessageBox(self) # Pass self as parent for the message box
        msg_box.setWindowTitle("Backup Status")
        msg_box.setText(message)
        if success:
            msg_box.setIcon(QMessageBox.Icon.Information)
        else:
            msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec()

    @pyqtSlot(str)
    def on_backup_error(self, error_message: str):
        """Slot to handle any errors during the backup process."""
        
        msg_box = QMessageBox(self) # Pass self as parent for the message box
        msg_box.setWindowTitle("Backup Error")
        msg_box.setText(f"An error occurred during backup:\n{error_message}")
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.exec()

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
        self.terminal_page = TerminalPage()
        
        self.connection_info = Connection.connection()
        self.db_connection = self.connection_info['db_connection']
                
        self.backup_manager = DatabaseBackupManager(
                parent_widget=self, # Pass 'self' (your QWidget/QMainWindow instance) as the parent
                db_host=self.connection_info['host'],
                db_port=self.connection_info['port'],
                db_user=self.connection_info['user'],
                db_password=self.connection_info['password'],
                db_name=self.connection_info['database'] 
            )

        self.backup_manager.backup_started.connect(self.on_backup_started)
        self.backup_manager.backup_finished.connect(self.on_backup_finished)
        self.backup_manager.backup_error.connect(self.on_backup_error)

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
        self.btn_generate_report = QPushButton("Generate Report")
        self.btn_generate_report.setObjectName("primaryButton")
        self.btn_generate_report.clicked.connect(self._generate_report)
        tasks_layout.addWidget(self.btn_generate_report)

        # Add a few more placeholder buttons to ensure scrolling is evident
        self.btn_data_backup = QPushButton("Perform Database Backup")
        self.btn_data_backup.setObjectName("primaryButton")
        self.btn_data_backup.clicked.connect(self.start_backup)
        tasks_layout.addWidget(self.btn_data_backup)



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
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.automation_log_output.append(f"[{timestamp}] {message}")

    def _generate_report(self):
        self._log_automation_event("Generating Report...")
        QMessageBox.information(self, "Automation Task", "Report generation task initiated. (Check log for details)")
        try:
            if not self.db_connection:
                self.connection_info = Connection.connection()
                self.db_connection = self.connection_info['db_connection']
            else:
                cursor = self.db_connection.cursor()
                cursor.execute(f"SELECT TO_CHAR(_timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp, _level, _message FROM \"EMIR\".Logs_EVA() ORDER BY timestamp;")  # Assuming a 'logs' table
                logs = cursor.fetchall()
                self.db_connection.commit()
                self.automation_log_output.append("\n--- ALl System Logs ---")
                if logs:
                    for log in logs:
                        self.automation_log_output.append(f"{log[0]} <b>[{log[1]}]</b>: {log[2]}")  # Adjust based on log structure
                else:
                    self.automation_log_output.append("No logs found.")
                self.automation_log_output.append("-------------------\n")
                if logs:
                    reply = QMessageBox.question(self,'Report Suggestion',
                        f"Do you want a report document of these logs?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                                            )
                    if reply == QMessageBox.StandardButton.Yes:
                        self.terminal_page.generate_logs_report(logs)
        except Error as e:
            self.db_connection.rollback()
            self._log_automation_event(f"Error retrieving logs: {e}")
        finally:
            if cursor:
                cursor.close()
                    
        self._log_automation_event("Report generated and saved.")
    
    
    def start_backup(self):
        self.backup_manager.perform_backup()
        
    @pyqtSlot()
    def on_backup_started(self):
         """Slot to handle when the backup process begins."""

    @pyqtSlot(bool, str)
    def on_backup_finished(self, success: bool, message: str):
        """Slot to handle when the backup process finishes."""
        
        msg_box = QMessageBox(self) # Pass self as parent for the message box
        msg_box.setWindowTitle("Backup Status")
        msg_box.setText(message)
        if success:
            msg_box.setIcon(QMessageBox.Icon.Information)
        else:
            msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec()

    @pyqtSlot(str)
    def on_backup_error(self, error_message: str):
        """Slot to handle any errors during the backup process."""
        
        msg_box = QMessageBox(self) # Pass self as parent for the message box
        msg_box.setWindowTitle("Backup Error")
        msg_box.setText(f"An error occurred during backup:\n{error_message}")
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.exec()

    def __del__(self):
        """Restore original stdout/stderr when TerminalPage is destroyed."""
        # Check if attributes exist before restoring, for safer shutdown
        if hasattr(self, '_original_stdout') and self._original_stdout is not None:
            sys.stdout = self._original_stdout
        if hasattr(self, '_original_stderr') and self._original_stderr is not None:
            sys.stderr = self._original_stderr
