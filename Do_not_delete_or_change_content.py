import sys
import os
import subprocess
import datetime
import logging

# PyQt6 Imports
from PyQt6.QtWidgets import (
    QApplication, QWidget, QFileDialog, QMessageBox
)
from PyQt6.QtCore import QObject, pyqtSignal, Qt, QCoreApplication, QThread # Import QThread

# Configure basic logging to console for demonstration purposes.
# You might want to integrate this with your application's existing logging setup.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackupWorker(QObject):
    """
    Worker object to perform the PostgreSQL backup in a separate thread.
    This class handles the blocking operation (subprocess.run).
    """
    # Signals to communicate backup status
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

    def run_backup_task(self):
        """
        Executes the pg_dump command. This method will run in a separate thread.
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

class DatabaseBackupManager(QObject):
    """
    Manages PostgreSQL database backup operations.

    This class now orchestrates the backup process by creating a worker thread
    to perform the actual pg_dump operation, keeping the GUI responsive.
    It uses QFileDialog to prompt the user for a backup directory and
    emits signals to communicate the backup status back to the GUI.
    """

    # Signals to communicate backup status (proxied from the worker)
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
        This part still runs on the main thread as QFileDialog is a GUI element.

        Returns:
            str: The selected directory path, or an empty string if the dialog was cancelled.
        """
        logger.info("Opening QFileDialog for backup directory selection...")
        directory = QFileDialog.getExistingDirectory(
            self.parent_widget,
            "Select Directory for Database Backup",
            os.path.expanduser("~")
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
        Initiates the database backup process by creating and starting a new thread.
        This method is called from the GUI thread.
        """
        logger.info("Backup process initiated from main thread.")

        # First, get the backup directory on the main thread (QFileDialog must be on main thread)
        backup_dir = self._get_backup_directory()
        if not backup_dir:
            self.backup_error.emit("Backup cancelled: No directory selected.")
            self.backup_finished.emit(False, "Backup cancelled by user.")
            return

        backup_filename = self._generate_backup_filename()
        backup_filepath = os.path.join(backup_dir, backup_filename)

        # Create a QThread and a BackupWorker instance
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


# --- How to integrate this into your existing PyQt6 QWidget/QMainWindow ---
#
# 1. In your existing QWidget or QMainWindow class's __init__ method:
#
#    from your_module_name import DatabaseBackupManager # Assuming you save this class in a file
#
#    class MyExistingApp(QMainWindow): # Or QWidget
#        def __init__(self):
#            super().__init__()
#            # ... your existing GUI setup ...
#
#            # Instantiate the DatabaseBackupManager
#            # IMPORTANT: Replace these with your actual PostgreSQL database credentials
#            self.backup_manager = DatabaseBackupManager(
#                parent_widget=self, # Pass 'self' (your QWidget/QMainWindow instance) as the parent
#                db_host='localhost',
#                db_port='5432',
#                db_user='postgres',
#                db_password='your_db_password', # <--- CHANGE THIS TO YOUR ACTUAL DB PASSWORD!
#                db_name='your_database_name' # <--- CHANGE THIS TO YOUR ACTUAL DB NAME!
#            )
#
#            # Connect your existing backup button to the perform_backup method
#            # Assuming you have a QPushButton named 'self.my_backup_button'
#            self.my_backup_button.clicked.connect(self.backup_manager.perform_backup)
#
#            # Connect the signals from the backup manager to your GUI update slots
#            self.backup_manager.backup_started.connect(self.on_backup_started)
#            self.backup_manager.backup_finished.connect(self.on_backup_finished)
#            self.backup_manager.backup_error.connect(self.on_backup_error)
#
# 2. Define the corresponding slots in your existing QWidget/QMainWindow class:
#
#    class MyExistingApp(QMainWindow): # Or QWidget
#        # ... __init__ and other methods ...
#
#        @pyqtSlot()
#        def on_backup_started(self):
#            """Slot to handle when the backup process begins."""
#            # Example: Disable the backup button and update a status label
#            self.my_backup_button.setEnabled(False)
#            self.status_label.setText("Backup in progress... Please select a directory.")
#            # No need for QCoreApplication.processEvents() here, as the blocking
#            # operation is now in a separate thread. The GUI will remain responsive.
#
#        @pyqtSlot(bool, str)
#        def on_backup_finished(self, success: bool, message: str):
#            """Slot to handle when the backup process finishes."""
#            # Example: Re-enable button, update status, show message box
#            self.my_backup_button.setEnabled(True)
#            self.status_label.setText(f"Backup finished: {message}")
#            msg_box = QMessageBox(self) # Pass self as parent for the message box
#            msg_box.setWindowTitle("Backup Status")
#            msg_box.setText(message)
#            if success:
#                msg_box.setIcon(QMessageBox.Icon.Information)
#            else:
#                msg_box.setIcon(QMessageBox.Icon.Warning)
#            msg_box.exec()
#
#        @pyqtSlot(str)
#        def on_backup_error(self, error_message: str):
#            """Slot to handle any errors during the backup process."""
#            # Example: Re-enable button, update status, show error message box
#            self.my_backup_button.setEnabled(True)
#            self.status_label.setText(f"Backup failed: {error_message}")
#            msg_box = QMessageBox(self) # Pass self as parent for the message box
#            msg_box.setWindowTitle("Backup Error")
#            msg_box.setText(f"An error occurred during backup:\n{error_message}")
#            msg_box.setIcon(QMessageBox.Icon.Critical)
#            msg_box.exec()
