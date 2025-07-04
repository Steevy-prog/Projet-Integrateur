
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

from db_connection import db_connection
from db_connection import host, database, user, password

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
        self.backup_started.emit()
        logger.info("Backup process initiated.")

        backup_dir = self._get_backup_directory()
        if not backup_dir:
            # If user cancels directory selection, emit error and finish signals
            self.backup_error.emit("Backup cancelled: No directory selected.")
            self.backup_finished.emit(False, "Backup cancelled by user.")
            return

        backup_filename = self._generate_backup_filename()
        backup_filepath = os.path.join(backup_dir, backup_filename)

        # Construct the pg_dump command.
        # Ensure 'pg_dump' is in your system's PATH, or provide its full path.
        # Example for Windows: pg_dump_path = "C:\\Program Files\\PostgreSQL\\14\\bin\\pg_dump.exe"
        # For Linux/macOS, if installed via package manager, "pg_dump" is usually sufficient.
        pg_dump_command = [
            "pg_dump",
            "-h", self.db_host,
            "-p", self.db_port,
            "-U", self.db_user,
            "-d", self.db_name,
            "-F", "p", # Plain-text SQL dump format
            "-f", backup_filepath # Output file path
        ]

        # Set PGPASSWORD environment variable for non-interactive password input.
        # Be aware of the security implications: the password is in the environment
        # for the duration of the subprocess call. For highly secure environments,
        # consider using a .pgpass file or other authentication methods.
        env = os.environ.copy()
        if self.db_password:
            env["PGPASSWORD"] = self.db_password
            logger.info("PGPASSWORD environment variable set for pg_dump execution.")
        else:
            logger.warning("No database password provided. pg_dump might prompt for password interactively.")

        logger.info(f"Attempting to execute pg_dump command: {' '.join(pg_dump_command)}")
        try:
            # Execute the pg_dump command as a subprocess.
            # capture_output=True: Captures stdout and stderr.
            # text=True: Decodes stdout/stderr as text.
            # check=False: Prevents subprocess.run from raising CalledProcessError
            #              for non-zero exit codes; we handle it manually.
            result = subprocess.run(
                pg_dump_command,
                env=env,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                logger.info(f"Database backup successful: {backup_filepath}")
                self.backup_finished.emit(True, f"Backup created at: {backup_filepath}")
            else:
                # Log detailed error information from pg_dump's output
                error_message_detail = (f"pg_dump failed with exit code {result.returncode}.\n"
                                        f"STDOUT: {result.stdout.strip()}\n"
                                        f"STDERR: {result.stderr.strip()}")
                logger.error(f"Database backup failed: {error_message_detail}")
                # Emit a more user-friendly error message
                user_error_message = result.stderr.strip() or result.stdout.strip() or "Unknown pg_dump error."
                self.backup_error.emit(f"Backup failed: {user_error_message}")
                self.backup_finished.emit(False, f"Backup failed. Check application logs for details.")

        except FileNotFoundError:
            # This error occurs if 'pg_dump' command is not found in PATH
            error_msg = ("Error: 'pg_dump' command not found. "
                         "Please ensure PostgreSQL client tools are installed and 'pg_dump' is in your system's PATH.")
            logger.critical(error_msg)
            self.backup_error.emit(error_msg)
            self.backup_finished.emit(False, "Backup failed: pg_dump not found.")
        except Exception as e:
            # Catch any other unexpected Python exceptions
            error_msg = f"An unexpected Python error occurred during backup: {e}"
            logger.critical(error_msg, exc_info=True) # Log exception traceback
            self.backup_error.emit(error_msg)
            self.backup_finished.emit(False, "Backup failed due to an unexpected internal error.")

# --- Database Connection (Global for simplicity in mock, could be passed to pages) ---
# IMPORTANT: For a production app, manage connection lifecycle more carefully
# (e.g., passing connection pool/manager to pages, or using a singleton pattern).
# Keeping it global as in your provided code for now.

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


# --- Custom Stream for QTextEdit (Our 'Terminal') ---

# log_type = 'all'
# class QTextEditLogger(QObject, logging.Handler):
#     append_text = pyqtSignal(str)

#     def __init__(self, text_edit):
#         super().__init__()
#         self.text_edit = text_edit
#         self.append_text.connect(self.text_edit)

#     def write(self, text):
#         if text.strip():
#             self.append_text.emit(text.strip())

#     def flush(self):
#         pass

# class BackupWorker(QThread):
#     """
#     A QThread subclass to run the database backup operation in the background,
#     preventing the GUI from freezing.
#     """
#     # Signals to communicate with the main thread (GUI)
#     backup_finished = pyqtSignal(bool, str) # bool: success, str: message
#     update_log = pyqtSignal(str) # For detailed logging messages

#     def __init__(self, db_params: dict, output_dir: str, compress: bool, dump_options: list, dump_binary_path: str):
#         super().__init__()
#         self.db_params = db_params
#         self.output_dir = output_dir
#         self.compress = compress
#         self.dump_options = dump_options
#         self.dump_binary_path = dump_binary_path
#         self.logger = logging.getLogger(__name__)

#         # Ensure the logger is connected to the update_log signal
#         # This is a bit tricky as the handler needs to be initialized with the QTextEdit
#         # We will make sure the main GUI passes a logger that's already configured.

#     def run(self):
#         """
#         The main method of the thread, executed when thread.start() is called.
#         It calls the actual backup function.
#         """
#         # Inside the worker thread, direct logging output to our signal
#         # This requires setting up a dedicated logger for this thread
#         worker_logger = logging.getLogger('backup_worker')
#         worker_logger.setLevel(logging.INFO)
#         # Remove any existing handlers to prevent duplicate output
#         for handler in list(worker_logger.handlers):
#             worker_logger.removeHandler(handler)
        
#         # Add a handler that emits to our update_log signal
#         class WorkerSignalHandler(logging.Handler):
#             def __init__(self, signal_emitter):
#                 super().__init__()
#                 self.signal_emitter = signal_emitter
#                 self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

#             def emit(self, record):
#                 msg = self.format(record)
#                 self.signal_emitter.emit(msg)

#         worker_logger.addHandler(WorkerSignalHandler(self.update_log))

#         # Call the backup function
#         success, message = self._perform_backup(worker_logger)
#         self.backup_finished.emit(success, message)

#     def _perform_backup(self, logger_instance: logging.Logger):
#         """
#         Performs the PostgreSQL backup operation.
#         This function is similar to the standalone one, but uses the logger_instance
#         passed from the worker thread's run method.
#         """
#         db_name = self.db_params['db_name']
#         host = self.db_params['host']
#         user = self.db_params['user']
#         port = self.db_params['port']
#         password = self.db_params['password']

#         if not os.path.isdir(self.output_dir):
#             logger_instance.error(f"Output directory does not exist: {self.output_dir}")
#             return False, "Output directory does not exist."

#         timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#         backup_filename_base = f"{db_name}_backup_{timestamp}"
#         backup_file_ext = "sql"

#         if self.dump_options and ('-Fc' in self.dump_options or '--format=c' in self.dump_options):
#             backup_file_ext = "dump"
#         elif self.dump_options and ('-Ft' in self.dump_options or '--format=t' in self.dump_options):
#             backup_file_ext = "tar"

#         backup_file_path = os.path.join(self.output_dir, f"{backup_filename_base}.{backup_file_ext}")
        
#         # Use the provided dump_binary_path
#         cmd = [self.dump_binary_path]
#         cmd.extend(["-h", host])
#         cmd.extend(["-p", str(port)])
#         cmd.extend(["-U", user])
#         cmd.append(db_name)

#         if self.dump_options:
#             cmd.extend(self.dump_options)

#         logger_instance.info(f"Starting online PostgreSQL backup for '{db_name}' on '{host}:{port}'...")
#         logger_instance.info(f"Executing command: {' '.join(cmd)} > {os.path.basename(backup_file_path)}")

#         env = os.environ.copy()
#         if password:
#             env['PGPASSWORD'] = password

#         try:
#             with open(backup_file_path, 'wb') as f:
#                 process = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, env=env, check=False)

#             if process.returncode == 0:
#                 logger_instance.info(f"PostgreSQL backup successful for '{db_name}'.")
#             else:
#                 error_msg = f"PostgreSQL backup failed for '{db_name}'.\n" \
#                             f"Command: {' '.join(cmd)}\n" \
#                             f"Error output: {process.stderr.decode('utf-8')}"
#                 logger_instance.error(error_msg)
#                 if os.path.exists(backup_file_path):
#                     os.remove(backup_file_path)
#                 return False, error_msg

#             if self.compress:
#                 compressed_file_path = f"{backup_file_path}.gz"
#                 logger_instance.info(f"Compressing backup file to: {os.path.basename(compressed_file_path)}")
#                 with open(backup_file_path, 'rb') as f_in:
#                     with gzip.open(compressed_file_path, 'wb') as f_out:
#                         shutil.copyfileobj(f_in, f_out)
#                 os.remove(backup_file_path)
#                 logger_instance.info("Compression successful.")
#                 os.chmod(compressed_file_path, stat.S_IREAD | stat.S_IWRITE)
#                 logger_instance.info(f"Set permissions for {os.path.basename(compressed_file_path)} to 0o600.")
#                 return True, f"Backup successful to {os.path.basename(compressed_file_path)}"
            
#             return True, f"Backup successful to {os.path.basename(backup_file_path)}"

#         except FileNotFoundError as e:
#             error_msg = f"Backup failed: '{e.filename}' command not found.\n" \
#                         "Please ensure 'pg_dump' is installed and accessible in your system's PATH, " \
#                         "or provide its full path using the 'pg_dump Binary Path' field." # Updated error message
#             logger_instance.error(error_msg)
#             return False, error_msg
#         except subprocess.CalledProcessError as e:
#             error_msg = f"Backup failed with a command error: {e}\n" \
#                         f"Command: {e.cmd}\n" \
#                         f"Return Code: {e.returncode}\n" \
#                         f"Output: {e.stdout.decode('utf-8')}\n" \
#                         f"Error: {e.stderr.decode('utf-8')}"
#             logger_instance.error(error_msg)
#             return False, error_msg
#         except Exception as e:
#             error_msg = f"An unexpected error occurred during backup: {e}"
#             logger_instance.error(error_msg, exc_info=True)
#             if os.path.exists(backup_file_path):
#                 os.remove(backup_file_path)
#             return False, error_msg
# --- Page Classes ---

class TerminalPage(QWidget):
    """
    Represents the main automation terminal page with command input and output.
    Contains all the core AA logic.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # self.worker_thread = None
        
        # self.log_text_handler = QTextEditLogger(self)
        # self.log_text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        # logging.getLogger().addHandler(self.log_text_handler) # Add to root logger
        # logging.getLogger().setLevel(logging.INFO) # Set default logging level
        
        # A specific logger for the worker, which will be connected to self.log_output directly
        # self.worker_logger = logging.getLogger('backup_worker')
        # self.worker_logger.setLevel(logging.INFO)
        # # Ensure it doesn't propagate to the root logger if we are handling it directly
        # self.worker_logger.propagate = False 

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
            # 'set_report_settings': 'Set report generation settings (not implemented).',
            # 'generate_report': 'Generate a report based on current settings (not implemented).',
            'start_backup': 'Start a database backup.',
            'display_all_logs': 'Display all system logs.',
            'display_pre_logs': 'Display previous system logs as from a specific date',
            'display_post_logs': 'Display system logs starting from a specific date',
            'display_range_logs': 'Display system logs generated between two dates'
        }
        # --- End of attribute definitions ---
        
        self.backup_manager = DatabaseBackupManager(
               parent_widget=self, # Pass 'self' (your QWidget/QMainWindow instance) as the parent
               db_host=host,
               db_port='5432',
               db_user=user,
               db_password=password, # <--- CHANGE THIS TO YOUR ACTUAL DB PASSWORD!
               db_name=database # <--- CHANGE THIS TO YOUR ACTUAL DB NAME!
           )

        self.backup_manager.backup_started.connect(self.on_backup_started)
        self.backup_manager.backup_finished.connect(self.on_backup_finished)
        self.backup_manager.backup_error.connect(self.on_backup_error)

        self.init_ui()
        
        # self.worker_thread = None
        
        # self.log_text_handler = QTextEditLogger(self.terminal_output)
        # self.log_text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        # logging.getLogger().addHandler(self.log_text_handler) # Add to root logger
        # logging.getLogger().setLevel(logging.INFO) # Set default logging level
        
        # # A specific logger for the worker, which will be connected to self.log_output directly
        # self.worker_logger = logging.getLogger('backup_worker')
        # self.worker_logger.setLevel(logging.INFO)
        # # Ensure it doesn't propagate to the root logger if we are handling it directly
        # self.worker_logger.propagate = False

         # Now it's safe to call init_ui()

        # Redirect stdout and stderr for this specific page's terminal output
        # self.text_edit_logger = QTextEditLogger(self.terminal_output)
        # self._original_stdout = sys.stdout
        # self._original_stderr = sys.stderr
        # sys.stdout = self.text_edit_logger
        # sys.stderr = self.text_edit_logger

        self.terminal_output.append("Welcome to SGE Warehouse Automation Terminal!")
        self.terminal_output.append("Type 'sac --command_list' in the command input to see available commands.")

    # def start_backup(self):
    #     """Gathers input and starts the backup process in a new thread."""
    #     # db_name = self.db_name_input.text().strip()
    #     # host = self.host_input.text().strip()
    #     # user = self.user_input.text().strip()
    #     # port_str = self.port_input.text().strip()
    #     # password = self.password_input.text() # Keep as is, it's read by the worker
    #     # output_dir = self.output_dir_input.text().strip()
    #     # pg_dump_path = self.pg_dump_path_input.text().strip() # Get the pg_dump path

    #     # Basic input validation
    #     QMessageBox.information(self, 'Okay', 'okay1')
    #     self.backup_directory = QFileDialog.getExistingDirectory(self, "Select Backup Directory")
    #     if not os.path.isdir(self.backup_directory):
    #         return
        
    #     file_filter = "Executable Files (*.exe);;All Files (*)" if os.name == 'nt' else "All Files (*)"

    #     self.file_path, _ = QFileDialog.getOpenFileName(
    #         self,
    #         "Select pg_dump Executable",
    #         file_filter
    #     )
    #     if self.file_path:
    #         logging.info(f"pg_dump binary path set to: {self.file_path}")
  
        
    #     if not all([database, host, user, port, self.file_path, self.backup_directory]):
    #         QMessageBox.warning(self, "Missing Information", "Please fill in all required database details, select an output directory, and provide the pg_dump binary path.")
    #         return

    #     try:
    #         port = int(port)
    #         if not (1 <= port <= 65535):
    #             raise ValueError("Port must be between 1 and 65535.")
    #     except ValueError:
    #         QMessageBox.warning(self, "Invalid Port", "Port must be a valid number.")
    #         return

    #     if not os.path.isdir(self.backup_directory):
    #         QMessageBox.critical(self, "Invalid Output Directory", "The selected output directory does not exist. Please create it or choose another.")
    #         return
        
    #     # Check if pg_dump path is valid
    #     if not (os.path.isfile(self.file_path) or self.file_path == "pg_dump"): # Allow "pg_dump" if it's expected to be in PATH
    #         QMessageBox.critical(self, "Invalid pg_dump Path", "The specified pg_dump binary path does not exist or is not a valid file. Please check the path.")
    #         return

    #     if self.worker_thread and self.worker_thread.isRunning():
    #         QMessageBox.information(self, "Backup in Progress", "A backup is already running. Please wait for it to finish.")
    #         return

    #     db_params = {
    #         'db_name': database,
    #         'host': host,
    #         'user': user,
    #         'port': port,
    #         'password': password
    #     }

    #     # Create and start the worker thread
    #     self.worker_thread = BackupWorker(
    #         db_params=db_params,
    #         output_dir=self.backup_directory,
    #         compress=True, # Always compress in this GUI example
    #         dump_options=['--format=c'], # Example: Always use custom format
    #         dump_binary_path=self.file_path # Use the path provided by the user
    #     )
    #     self.worker_thread.backup_finished.connect(self.on_backup_finished)
    #     self.worker_thread.start()

    # def on_backup_finished(self, success: bool, message: str):
    #     """Slot to handle the backup_finished signal from the worker thread."""

    #     if success:
    #         QMessageBox.information(self, "Backup Complete", message)
    #     else:
    #         QMessageBox.critical(self, "Backup Failed", message)
        
    #     # Clean up the worker thread
    #     self.worker_thread.quit()
    #     self.worker_thread.wait() # Wait for the thread to actually finish


    # def closeEvent(self, event):
    #     """Handle application close event to ensure worker thread is terminated."""
    #     if self.worker_thread and self.worker_thread.isRunning():
    #         reply = QMessageBox.question(self, 'Confirm Exit',
    #                                      "A backup is in progress. Are you sure you want to exit?",
    #                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    #                                      QMessageBox.StandardButton.No)
    #         if reply == QMessageBox.StandardButton.Yes:
    #             self.worker_thread.quit()
    #             self.worker_thread.wait(5000) # Wait up to 5 seconds for thread to finish
    #             if self.worker_thread.isRunning():
    #                 logging.warning("Backup thread did not terminate gracefully.")
    #             event.accept()
    #         else:
    #             event.ignore()
    #     else:
    #         event.accept()
        

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

    # def set_report_settings(self):
    #     self.terminal_output.append("Setting report generation settings is not implemented yet.")
    #     self.terminal_output.append("This feature will be available in a future update.")
    
    # def generate_report(self):
    #     self.terminal_output.append("Generating report is not implemented yet.")
    #     self.terminal_output.append("This feature will be available in a future update.")  
    
    # def backup_database(self):
    #     if db_connection:
    #         try:
    #             cursor = db_connection.cursor()
    #             # Placeholder for actual backup logic
    #             cursor.execute("SELECT pg_start_backup('backup');")  # Example command, adjust as needed
    #             db_connection.commit()
    #             self.terminal_output.append("Database backup started successfully.")
    #         except Error as e:
    #             self.terminal_output.append(f"Error starting database backup: {e}")
    #         finally:
    #             if cursor:
    #                 cursor.close()
    #     else:
    #         self.terminal_output.append("Database connection not established. Cannot start backup.")
            
    def display_all_logs(self):
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute(f"SELECT TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp, level, message FROM \"SCA\".Logs ORDER BY timestamp;")  # Assuming a 'logs' table
                logs = cursor.fetchall()
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
                self.terminal_output.append(f"Error retrieving logs: {e}")
            finally:
                if cursor:
                    cursor.close()
    
    def display_pre_logs(self, date):
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute(f"SELECT TO_CHAR(_timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp, level, message FROM \"EMIR\".Logs_getlower('{date}':: timestamp)")
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
                self.terminal_output.append(f"Error retrieving logs: {e}")
            finally:
                if cursor:
                    cursor.close()
        else:
            self.terminal_output.append("Database connection not established. Cannot retrieve logs.")
    
    def display_post_logs(self, date):
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute(f"SELECT TO_CHAR(_timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp, level, message FROM \"EMIR\".Logs_gethigher('{date}':: timestamp)")
                logs = cursor.fetchall()
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
                self.terminal_output.append(f"Error retrieving logs: {e}")
            finally:
                if cursor:
                    cursor.close()
        else:
            self.terminal_output.append("Database connection not established. Cannot retrieve logs.")
    
    
    def display_range_logs(self, date_1, date_2):
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute(f"SELECT TO_CHAR(_timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp, level, message FROM \"EMIR\".Logs_get('{date_1}':: timestamp, '{date_2}':: timestamp)")
                logs = cursor.fetchall()
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
                self.terminal_output.append(f"Error retrieving logs: {e}")
            finally:
                if cursor:
                    cursor.close()
        else:
            self.terminal_output.append("Database connection not established. Cannot retrieve logs.")
    
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
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute("SELECT \"EMIR\".produitsnum();") # Assuming a 'products' table
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
                cursor.execute("SELECT COUNT(*) FROM \"SCA\".individu;") # Assuming a 'users' table
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
                cursor.execute("SELECT idproduit, nom, prix_unitaire FROM \"SCA\".Produit;") # Assuming 'products' table
                products = cursor.fetchall()
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
                cursor.execute("SELECT nom, adresse, telephone, prenom FROM \"SCA\".individu;") # Assuming 'users' table
                users = cursor.fetchall()
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
                self.terminal_output.append(f"Error listing users: {e}")
            finally:
                if cursor:
                    cursor.close()
        else:
            self.terminal_output.append("Database connection not established. Cannot list users.")

    def clear_terminal(self):
        self.terminal_output.clear()
        self.terminal_output.append("Terminal cleared.")

    def start_backup(self):
        self.backup_manager.perform_backup()
    @pyqtSlot()
    def on_backup_started(self):
        """Slot to handle when the backup process begins."""
        # Example: Disable the backup button and update a status label
        # self.my_backup_button.setEnabled(False)
        # self.status_label.setText("Backup in progress... Please select a directory.")
        # Force GUI update if the operation is long
        QCoreApplication.processEvents()

    @pyqtSlot(bool, str)
    def on_backup_finished(self, success: bool, message: str):
        """Slot to handle when the backup process finishes."""
        # Example: Re-enable button, update status, show message box
        # self.my_backup_button.setEnabled(True)
        # self.status_label.setText(f"Backup finished: {message}")
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
        # Example: Re-enable button, update status, show error message box
        # self.my_backup_button.setEnabled(True)
        # self.status_label.setText(f"Backup failed: {error_message}")
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
        self.btn_data_backup.clicked.connect(lambda: self.terminal_page.start_backup)
        tasks_layout.addWidget(self.btn_data_backup)

        # self.btn_audit_log_cleanup = QPushButton("Clean Up Old Audit Logs")
        # self.btn_audit_log_cleanup.setObjectName("primaryButton")
        # self.btn_audit_log_cleanup.clicked.connect(lambda: self._log_automation_event("Old audit logs cleanup initiated."))
        # tasks_layout.addWidget(self.btn_audit_log_cleanup)

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
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute(f"SELECT TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp, level, message FROM \"SCA\".Logs ORDER BY timestamp;")  # Assuming a 'logs' table
                logs = cursor.fetchall()
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
                self._log_automation_event(f"Error retrieving logs: {e}")
            finally:
                if cursor:
                    cursor.close()
                    
        self._log_automation_event("Report generated and saved.")
    # def _trigger_low_stock_notifications(self):
    #     self._log_automation_event("Triggering low stock notifications...")
    #     QMessageBox.information(self, "Automation Task", "Low Stock Notifications triggered. (Check log for details)")
    #     # This would typically involve checking inventory levels and sending alerts
    #     self._log_automation_event("Low stock notifications sent to relevant personnel.")

# --- Main Application Window ---

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
#         self.logged_in_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
#         self.sidebar_layout.addWidget(self.logged_in_label)

#         self.sidebar_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

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

#     def _apply_styles(self):
#         """
#         Applies Qt Style Sheets (QSS) for the application's look and feel.
#         """
#         self.setStyleSheet("""
#             QMainWindow {
#                 background-color: #f0f2f5;
#             }

#             #sidebarFrame {
#                 background-color: #2c3e50;
#                 border-right: 1px solid #34495e;
#             }

#             #loggedInLabel {
#                 color: #ecf0f1;
#                 font-size: 16px;
#                 padding-bottom: 10px;
#                 border-bottom: 1px solid #34495e;
#             }

#             /* General QPushButton styles for navigation buttons */
#             QPushButton {
#                 background-color: #3498db;
#                 color: white;
#                 border: none;
#                 padding: 10px 15px;
#                 text-align: left;
#                 font-size: 14px;
#                 border-radius: 5px;
#                 min-width: 150px;
#             }

#             QPushButton:hover {
#                 background-color: #2980b9;
#                 color: white;
#             }

#             QPushButton[active="true"] {
#                 background-color: #f39c12;
#                 color: #2c3e50;
#                 font-weight: bold;
#                 border-left: 5px solid #e67e22;
#             }
#             QPushButton[active="true"]:hover {
#                 background-color: #e67e22;
#             }

#             #mainTitleLabel {
#                 font-size: 28px;
#                 font-weight: bold;
#                 color: #2c3e50;
#                 margin-bottom: 20px;
#             }

#             QGroupBox {
#                 border: 1px solid #ccc;
#                 border-radius: 8px;
#                 margin-top: 1.5em;
#                 font-size: 16px;
#                 font-weight: bold;
#                 color: #34495e;
#             }
#             QGroupBox::title {
#                 subcontrol-origin: margin;
#                 left: 15px;
#                 padding: 0 5px;
#             }

#             QLineEdit#commandLineEdit {
#                 background-color: #ffffff;
#                 border: 1px solid #ccc;
#                 border-radius: 5px;
#                 padding: 10px;
#                 font-size: 14px;
#                 color: #2c3e50;
#             }
#             QLineEdit#commandLineEdit:focus {
#                 border: 1px solid #3498db;
#             }

            # QTextEdit#terminalOutputTextEdit, QTextEdit#automationLogTextEdit { /* Applied to both terminal and automation log */
            #     background-color: #1e1e1e;
            #     color: #00ff00;
            #     font-family: 'Consolas', 'Monaco', monospace;
            #     font-size: 11pt;
            #     border-radius: 5px;
            #     padding: 10px;
                
            # }

            # QPushButton#executeButton, QPushButton#clearOutputButton {
            #     color: white;
            #     padding: 10px 20px;
            #     border-radius: 5px;
            #     font-size: 14px;
            #     border: none;
            # }
            # QPushButton#executeButton {
            #     background-color: #008CBA;
            # }
            # QPushButton#executeButton:hover {
            #     background-color: #007bb5;
            # }
            # QPushButton#clearOutputButton {
            #     background-color: #f44336;
            # }
            # QPushButton#clearOutputButton:hover {
            #     background-color: #da190b;
            # }

#             /* Placeholder Page Content Styling */
#             QWidget#systemConfigurationPage QLabel,
#             QWidget#databaseMaintenancePage QLabel,
#             QWidget#securitySettingPage QLabel {
#                 font-size: 24px;
#                 color: #555;
#                 text-align: center;
#                 padding-top: 50px;
#             }
#             QWidget#systemConfigurationPage p,
#             QWidget#databaseMaintenancePage p,
#             QWidget#securitySettingPage p {
#                 font-size: 16px;
#                 color: #777;
#                 text-align: center;
#             }
#             /* Specific adjustments for AutomationPage's new title/description */
#             QWidget#AutomationPage #sectionTitle {
#                 font-size: 28px; /* Override for specific title */
#                 font-weight: bold;
#                 color: #2c3e50;
#                 margin-bottom: 20px;
#             }
#             QWidget#AutomationPage p {
#                 text-align: left; /* Align paragraphs normally */
#                 padding: 0 10px; /* Add some horizontal padding for readability */
#             }


#             /* Table widget styling (if used in future pages) */
#             QTableWidget {
#                 background-color: #ffffff;
#                 border: 1px solid #ccc;
#                 gridline-color: #eee;
#                 font-size: 13px;
#                 selection-background-color: #d1eaff;
#                 selection-color: #333;
#                 border-radius: 8px;
#             }
#             QTableWidget::item {
#                 padding: 5px;
#             }
#             QTableWidget::item:selected {
#                 background-color: #cceeff;
#                 color: black;
#             }
#             QHeaderView::section {
#                 background-color: #e6e6e6;
#                 padding: 5px;
#                 border: 1px solid #ccc;
#                 font-weight: bold;
#                 color: #333;
#             }
#             QHeaderView::section:horizontal {
#                 border-bottom: 2px solid #aaa;
#             }
#             QHeaderView::section:vertical {
#                 border-right: 2px solid #aaa;
#             }
#             #sectionSubTitle {
#                 font-size: 18px;
#                 font-weight: bold;
#                 color: #555;
#                 margin-bottom: 10px;
#             }

#             /* Buttons inside automation page */
#             QPushButton#primaryButton { /* Reused from earlier primaryButton, adjust if needed */
#                 background-color: #2ecc71; /* Green */
#                 color: #ffffff;
#                 border: none;
#                 padding: 10px 20px;
#                 font-size: 14px;
#                 border-radius: 10px;
#                 margin-top: 2px; /* Adjust spacing */
#                 text-align: center;
#             }
#             QPushButton#primaryButton:hover {
#                 background-color: #27ae60;
#             }
#             QPushButton#secondaryButton {
#                 background-color: #95a5a6; /* Gray */
#                 color: white;
#                 border: none;
#                 padding: 8px 15px;
#                 font-size: 14px;
#                 border-radius: 5px;
#                 margin-top: 10px;
#                 text-align: center;
#             }
#             QPushButton#secondaryButton:hover {
#                 background-color: #7f8c8d;
#             }


#             /* Scrollbar styling */
#             QScrollBar:vertical {
#                 border: 1px solid #999;
#                 background: #f0f0f0;
#                 width: 10px;
#                 margin: 0px 0px 0px 0px;
#             }
#             QScrollBar::handle:vertical {
#                 background: #c0c0c0;
#                 min-height: 20px;
#                 border-radius: 4px;
#             }
#             QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
#                 background: none;
#             }
#             QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
#                 background: none;
#             }
#             #automationPageScrollArea{
#                 border: none;
#             }
#         """)
# # --- Main Application Execution ---
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     palette = QPalette()
#     palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))  # Dialog background
#     palette.setColor(QPalette.ColorRole.WindowText, QColor("#232946"))  # Dialog text
#     palette.setColor(QPalette.ColorRole.Base, QColor("#F8F9FA"))  # Input fields
#     palette.setColor(QPalette.ColorRole.Text, QColor("#232946"))
#     palette.setColor(QPalette.ColorRole.Button, QColor("#6C63FF"))  # Accent for buttons
#     palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
#     palette.setColor(QPalette.ColorRole.Highlight, QColor("#6C63FF"))  # Selection color
#     palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
#     app.setPalette(palette)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec())