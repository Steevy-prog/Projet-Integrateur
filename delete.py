# import psycopg2    
# from psycopg2 import Error

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
#   print(f"Error connecting to PostgreSQL database: {e}")

# query_1 = """
#             DROP TABLE IF EXISTS Users;
#             CREATE TABLE Users (
#                 first_name VARCHAR(100) NOT NULL,
#                 last_name VARCHAR(100) NOT NULL,
#                 username VARCHAR(50) UNIQUE NOT NULL,
#                 access_level VARCHAR(20) NOT NULL
#             );
#             """
# try:
#   cursor = db_connection.cursor()
#   cursor.execute(query_1)
#   db_connection.commit()
#   print("Table 'user' created successfully.")
# except Error as e:
#   print(f"Error creating table 'User': {e}")
#   db_connection.rollback()
# finally:
#   cursor.close()

# sample_users_data = [
#                 {
#                     'first_name': 'John',
#                     'last_name': 'Doe',
#                     'username': 'johndoe',
#                     'access_level': 'Employee'
#                 },
#                 {
#                     'first_name': 'Jane',
#                     'last_name': 'Smith',
#                     'username': 'janesmith',
#                     'access_level': 'Employee'
#                 },
#                 {
#                     'first_name': 'Peter',
#                     'last_name': 'Jones',
#                     'username': 'pjones',
#                     'access_level': 'Admin'
#                 },
#                 {
#                     'first_name': 'Alice',
#                     'last_name': 'Williams',
#                     'username': 'alicew',
#                     'access_level': 'Employee'
#                 },
#                 {
#                     'first_name': 'Bob',
#                     'last_name': 'Brown',
#                     'username': 'bbrown',
#                     'access_level': 'Employee'
#                 },
#                 {
#                     'first_name': 'Charlie',
#                     'last_name': 'Davis',
#                     'username': 'cdavis',
#                     'access_level': 'Admin'
#                 }
#             ]
# for user in sample_users_data:
#     query_2 = f"""
#                 INSERT INTO Users (first_name, last_name, username, access_level)
#                 VALUES ('{user['first_name']}', '{user['last_name']}', '{user['username']}', '{user['access_level']}')
#                 """
#     try:
#         cursor = db_connection.cursor()
#         cursor.execute(query_2)
#         db_connection.commit()
#         print(f"User {user['username']} added successfully.")
#     except Error as e:
#         print(f"Error inserting User {user['username']}: {e}")
#     finally:
#         cursor.close()



import sys
import time
import datetime
import os
from docx import Document # pip install python-docx

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QProgressBar
)
from PyQt6.QtCore import (
    QObject, QThread, pyqtSignal, Qt
)

# For timezone handling (optional but good practice for WAT)
try:
    import pytz
except ImportError:
    pytz = None
    print("Warning: 'pytz' not installed. Timezone handling will be basic.")


# --- Worker Thread Class ---
# This class contains the long-running task
class ReportGeneratorWorker(QObject):
    # Signals to communicate with the GUI thread
    progress_updated = pyqtSignal(str, int) # message, percentage
    task_finished = pyqtSignal(bool, str)   # success, message
    
    def __init__(self, filename, save_directory):
        super().__init__()
        self._filename = filename
        self._save_directory = save_directory
        self._is_cancelled = False # Flag to control abortion

    def cancel(self):
        """Sets the cancellation flag."""
        self._is_cancelled = True
        print("Cancellation requested by GUI.")

    def run(self):
        """This method will be executed in the separate thread."""
        try:
            self.progress_updated.emit("Starting report generation...", 0)
            
            # Step 1: Simulate Data Retrieval
            if not self._simulate_step("Retrieving data", 5, 0, 33):
                self.task_finished.emit(False, "Task cancelled during data retrieval.")
                return

            # Step 2: Simulate Data Analysis
            if not self._simulate_step("Analyzing data", 7, 33, 66):
                self.task_finished.emit(False, "Task cancelled during data analysis.")
                return

            # Step 3: Simulate Report Document Generation and Saving
            if not self._generate_and_save_report(66, 100):
                self.task_finished.emit(False, "Task cancelled or failed during report generation.")
                return

            self.task_finished.emit(True, f"Report saved successfully to:\n{os.path.join(self._save_directory, self._filename)}")

        except Exception as e:
            # Catch any unexpected errors
            self.task_finished.emit(False, f"An unexpected error occurred: {e}")

    def _simulate_step(self, step_name, duration_seconds, start_progress, end_progress):
        """Helper to simulate a step with progress updates and cancellation check."""
        print(f"Worker: {step_name} started.")
        for i in range(duration_seconds):
            if self._is_cancelled:
                print(f"Worker: {step_name} cancelled.")
                return False # Indicate cancellation
            
            progress = start_progress + int((i / duration_seconds) * (end_progress - start_progress))
            self.progress_updated.emit(f"Step: {step_name} ({i+1}/{duration_seconds}s)", progress)
            time.sleep(1) # Simulate work

        print(f"Worker: {step_name} completed.")
        return True # Indicate success

    def _generate_and_save_report(self, start_progress, end_progress):
        """Generates and saves the Word document."""
        if self._is_cancelled:
            print("Worker: Report generation cancelled before starting.")
            return False

        try:
            document = Document()
            document.add_heading('Product Report', level=1)
            
            # Get current time in Cameroon (WAT)
            if pytz:
                cameroon_timezone = pytz.timezone('Africa/Douala')
                current_time_str = datetime.datetime.now(cameroon_timezone).strftime("%A, %B %d, %Y at %I:%M:%S %p %Z")
            else:
                current_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S (Local Time)")

            document.add_paragraph(f'Generated on: {current_time_str}')
            
            # Simulate fetching data (or pass real data to worker's __init__)
            # For this demo, we'll just put some placeholder data directly
            data = [
                (101, "Product A", 120.50, 10),
                (102, "Product B", 25.00, 75),
                (103, "Product C", 300.75, 20),
                (104, "Product D", 15.20, 120)
            ]
            
            if not data:
                document.add_paragraph("No data available to generate report.")
            else:
                table = document.add_table(rows=1, cols=len(data[0]))
                table.style = 'Table Grid'
                hdr_cells = table.rows[0].cells
                headers = ["ID", "Product Name", "Price", "Quantity"]
                for i, header_text in enumerate(headers):
                    hdr_cells[i].text = header_text
                for row_data in data:
                    row_cells = table.add_row().cells
                    for i, cell_value in enumerate(row_data):
                        row_cells[i].text = str(cell_value)
                        
            # Simulate saving time with cancellation check
            save_duration_seconds = 3
            for i in range(save_duration_seconds):
                if self._is_cancelled:
                    print("Worker: Report saving cancelled during write.")
                    return False
                progress = start_progress + int((i / save_duration_seconds) * (end_progress - start_progress))
                self.progress_updated.emit(f"Saving report ({i+1}/{save_duration_seconds}s)", progress)
                time.sleep(1)
            
            # Ensure directory exists before saving
            if not os.path.exists(self._save_directory):
                os.makedirs(self._save_directory)
            
            full_path = os.path.join(self._save_directory, self._filename)
            document.save(full_path)
            self.progress_updated.emit("Report generated successfully!", 100)
            print("Worker: Report saved.")
            return True

        except Exception as e:
            print(f"Worker: Error during report generation/save: {e}")
            return False # Indicate failure


# --- PyQt6 Application ---
class ReportGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.worker_thread = None # Reference to the QThread instance
        self.worker = None        # Reference to the QObject worker
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Abortable Product Report Generator')
        self.setGeometry(300, 300, 500, 250)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel('Click "Generate Report" to start.')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        button_layout = QHBoxLayout()
        self.generate_button = QPushButton('Generate Report')
        self.generate_button.clicked.connect(self.start_report_generation)
        button_layout.addWidget(self.generate_button)

        self.cancel_button = QPushButton('Cancel Report')
        self.cancel_button.clicked.connect(self.cancel_report_generation)
        self.cancel_button.setEnabled(False) # Disable until task starts
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def start_report_generation(self):
        # Disable buttons and reset UI
        self.generate_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.status_label.setText("Starting...")
        self.progress_bar.setValue(0)

        # 1. Prepare save path and filename
        default_filename = f"Product_Report_{datetime.date.today().strftime('%Y%m%d')}.docx"
        
        # In a real app, you'd use QFileDialog here to get the path from user
        # For simplicity in this demo, we'll hardcode a temporary directory
        save_directory = os.path.join(os.path.expanduser('~'), 'Desktop', 'GeneratedReports')
        # os.makedirs(save_directory, exist_ok=True) # Ensure it exists for the demo
        
        # If you wanted to use QFileDialog:
        # file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", os.path.join(os.path.expanduser('~'), 'Documents', default_filename), "Word Documents (*.docx)")
        # if not file_path:
        #     self.reset_ui()
        #     return
        # save_directory = os.path.dirname(file_path)
        # actual_filename = os.path.basename(file_path)
        actual_filename = default_filename # Using default for this demo without dialog


        # 2. Create a QThread instance
        self.worker_thread = QThread()
        # 3. Create an instance of our worker object
        self.worker = ReportGeneratorWorker(actual_filename, save_directory)

        # 4. Move the worker object to the thread
        self.worker.moveToThread(self.worker_thread)

        # 5. Connect signals and slots
        # When thread starts, run the worker's .run() method
        self.worker_thread.started.connect(self.worker.run)
        # When worker emits progress, update UI
        self.worker.progress_updated.connect(self.update_progress)
        # When worker finishes, handle result and clean up
        self.worker.task_finished.connect(self.report_generation_finished)
        # When worker finishes, terminate and quit the thread
        self.worker.task_finished.connect(self.worker_thread.quit)
        self.worker.task_finished.connect(self.worker.deleteLater) # Clean up worker object
        self.worker_thread.finished.connect(self.worker_thread.deleteLater) # Clean up thread object

        # 6. Start the thread!
        self.worker_thread.start()
        print("Report generation thread started.")

    def update_progress(self, message, percentage):
        self.status_label.setText(message)
        self.progress_bar.setValue(percentage)

    def report_generation_finished(self, success, message):
        self.reset_ui() # Re-enable buttons, etc.
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Task Outcome", message) # Use warning for cancelled/failed

        print("Report generation thread finished.")
        self.worker_thread = None # Clear references
        self.worker = None

    def cancel_report_generation(self):
        if self.worker:
            self.worker.cancel() # Tell the worker to stop
            self.status_label.setText("Cancellation requested...")
            self.cancel_button.setEnabled(False) # Prevent multiple cancel clicks
            print("Cancellation signal sent to worker.")
        else:
            print("No active worker to cancel.")

    def reset_ui(self):
        self.generate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.status_label.setText("Ready to generate report.")
        # self.progress_bar.setValue(0) # Keep final progress for user to see

    # Handle window close to ensure thread is terminated cleanly
    def closeEvent(self, event):
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(self, 'Confirm Exit',
                                         "A report is being generated. Do you want to cancel and exit?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.cancel() # Request cancellation
                self.worker_thread.wait(5000) # Wait up to 5 seconds for thread to finish
                if self.worker_thread.isRunning():
                    print("Worker thread did not terminate gracefully, forcing quit.")
                    self.worker_thread.terminate() # Force terminate if it doesn't stop
                    self.worker_thread.wait() # Wait for it to terminate
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ReportGeneratorApp()
    ex.show()
    sys.exit(app.exec())