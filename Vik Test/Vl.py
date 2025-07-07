import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QButtonGroup,
    QGroupBox, QScrollArea, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QDialog, QTextEdit, QSpinBox, QListWidget,
    QFormLayout, QSplitter, QMessageBox, QGridLayout, QStatusBar, QMenuBar, QMenu,
    QAction, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal, QSize, QRect
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter, QBrush, QPen, QLinearGradient
import datetime
import random
import psycopg2

# Global variables for database connection (as in original Worker_Dashboard.py)
worker_id = 'TR1234'
global conn
global cur

# Prompt for database choice
print("1. online")
print("2. offline")
it = input("Enter the number of db you want to use : ")

if it == '1':
    print("You have chosen the online database.")
    try:
        conn = psycopg2.connect(
            host="dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com",
            database="projet_integrateur",
            user="group13",
            password="nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3",
            port=5432
        )
        cur = conn.cursor()
    except psycopg2.Error as e:
        print(f"Error connecting to online database: {e}")
        sys.exit(1) # Exit if connection fails
elif it == '2':
    print("You have chosen the offline database.")
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="steevy",
            port=5432
        )
        cur = conn.cursor()
    except psycopg2.Error as e:
        print(f"Error connecting to offline database: {e}")
        sys.exit(1) # Exit if connection fails
else:
    print("Invalid choice. Exiting.")
    sys.exit(1)

class MetricCard(QFrame):
    """Stylized metric card for the dashboard, inspired by Design_Worker.py."""

    def __init__(self, title, value, color="#3498db", icon_text="📊"):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.NoFrame) # No default frame
        self.setFixedSize(220, 130) # Slightly larger for better visual impact

        # Gradient background and rounded corners
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {color}, stop: 1 {self.darken_color(color)});
                border-radius: 15px;
                border: none;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1); /* Soft shadow */
            }}
            QLabel {{
                color: white;
                background: transparent;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20) # More padding

        # Icon and title
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon_text)
        icon_label.setFont(QFont("Arial", 28)) # Larger icon
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold)) # Bolder title
        title_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")

        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        header_layout.addWidget(title_label)

        # Value
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Arial", 36, QFont.Weight.ExtraBold)) # Even bolder value
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) # Align left

        layout.addLayout(header_layout)
        layout.addSpacing(10) # Space between header and value
        layout.addWidget(value_label)
        layout.addStretch()

        self.setLayout(layout)

    def darken_color(self, color):
        """Darkens a hexadecimal color for gradient effect."""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.7)) for c in rgb) # Darken more aggressively
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

class TaskCard(QFrame):
    """Card widget for displaying individual tasks with new design."""

    task_selected = pyqtSignal(dict)

    def __init__(self, task_data, card_type="expedition"):
        super().__init__()
        self.task_data = task_data
        self.card_type = card_type
        self.init_ui()

    def init_ui(self):
        self.setFrameStyle(QFrame.Shape.NoFrame) # Remove default frame
        self.setFixedHeight(120) # Slightly taller cards
        self.setContentsMargins(0, 0, 0, 0)

        color = self.get_priority_color(self.task_data.get('priority', 'Low')) # Handle missing priority

        # Modern card style
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 13px;
                border: 1px solid #D3DCE0;
                margin: 5px 0; /* Reduced vertical margin */
                padding: 0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05); /* Subtle shadow */
                transition: all 0.2s ease-in-out;
            }}
            QFrame:hover {{
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1); /* More pronounced shadow on hover */
                transform: translateY(-2px); /* Slight lift effect */
            }}
        """)

        # Accent bar on the left
        accent_bar = QFrame(self)
        accent_bar.setFixedWidth(6)
        accent_bar.setStyleSheet(f"background-color: {color}; border-top-left-radius: 13px; border-bottom-left-radius: 13px;")
        # No need to set position, layout will handle it

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) # Remove internal margins
        main_layout.setSpacing(0) # Remove spacing between accent bar and content

        main_layout.addWidget(accent_bar) # Add accent bar first

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(15, 10, 15, 10) # Padding for content inside card
        content_layout.setSpacing(20)

        # Left: Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        # Header row
        header_row = QHBoxLayout()
        order_label = QLabel(self.task_data['Task_id'])
        order_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #2D3748;")
        header_row.addWidget(order_label)
        header_row.addStretch()

        if self.card_type == "expedition":
            priority_label = QLabel(self.task_data['priority'].capitalize()) # Capitalize for display
            priority_label.setStyleSheet(f"background-color: {color}; color: #FFFFFF; border-radius: 8px; font-size: 11px; font-weight: bold; padding: 4px 10px;")
            header_row.addWidget(priority_label)
            info_layout.addLayout(header_row)

        # Details row
            try:
                cur.execute("SELECT (p).* FROM \"EMIR\".getlots(%s) AS p;", (self.task_data['Colis'],))
                items_count = cur.fetchall()
                num_items = len(items_count)
            except psycopg2.Error as e:
                print(f"Error fetching lots for colis {self.task_data['Colis']}: {e}")
                num_items = 0 # Default to 0 if there's a DB error

            details_text = f"Items: <b>{num_items}</b> &nbsp; | &nbsp; Est: <b>{self.task_data['duree']} min</b>"
            due_text = f"Due: <b>{self.task_data['date-ech'].strftime('%Y-%m-%d %H:%M')}</b>" # Format datetime
        else: # For other card types, adjust details as needed
            details_text = f"Customer: <b>{self.task_data.get('Customer', 'N/A')}</b>"
            due_text = f"Status: <b>{self.task_data.get('status', 'Pending')}</b>"

        details_label = QLabel(details_text)
        details_label.setStyleSheet("font-size: 13px; color: #4A5568;")
        details_label.setTextFormat(Qt.TextFormat.RichText)
        due_label = QLabel(due_text)
        due_label.setStyleSheet("font-size: 13px; color: #888888;")
        due_label.setTextFormat(Qt.TextFormat.RichText)

        info_layout.addWidget(details_label)
        info_layout.addWidget(due_label)
        info_layout.addStretch()

        # Right: Action button
        action_btn = QPushButton("View Details")
        action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        action_btn.setStyleSheet("""
            QPushButton {
                background-color: #006775;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 14px;
                font-weight: 600;
                color: #FFFFFF;
                box-shadow: 0 2px 8px rgba(108, 99, 255, 0.2);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #004F5C;
            }
        """)
        action_btn.clicked.connect(self.on_action_clicked)

        content_layout.addLayout(info_layout, stretch=3)
        content_layout.addWidget(action_btn, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def get_priority_color(self, priority):
        colors = {
            'high': '#E53E3E', # Red
            'medium': '#E77E23', # Orange
            'low': '#38A169' # Green
        }
        return colors.get(priority.lower(), '#4A5568') # Default color, case-insensitive

    def on_action_clicked(self):
        self.task_selected.emit(self.task_data)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.task_selected.emit(self.task_data)

class TaskDetailDialog(QDialog):
    """Dialog to display details of a selected task with new design."""
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.setWindowTitle(f"Task Details: {self.task_data['Task_id']}")
        self.setFixedSize(500, 550)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)

        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border-radius: 15px;
            }
            QLabel {
                font-size: 15px;
                color: #212121;
                margin-bottom: 7px;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #212121;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #D3DCE0;
            }
            QPushButton {
                background-color: #006775;
                color: white;
                border: none;
                padding: 13px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #004F5C;
            }
            QListWidget {
                border: 1px solid #D3DCE0;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                min-height: 150px;
                color: #2D3748;
            }
            QListWidget::item {
                padding: 5px;
            }
            QFormLayout QLabel {
                font-weight: bold;
                color: #212121;
            }
        """)

        title_label = QLabel(f"Task: {self.task_data['Task_id']}")
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        # Task detail form
        form_layout = QFormLayout()

        # Fetch product names for the colis
        product_names = []
        try:
            cur.execute("SELECT (p).* FROM \"EMIR\".getlots(%s) AS p;", (self.task_data['Colis'],))
            lots = cur.fetchall()
            for lot in lots:
                # Assuming lot structure is (product_id, product_name, ...)
                product_names.append(lot[1]) # Adjust index based on actual data structure
        except psycopg2.Error as e:
            print(f"Error fetching product lots: {e}")
            product_names = ["N/A"]

        form_layout.addRow("Product(s):", QLabel(", ".join(product_names)))
        form_layout.addRow("Items Count:", QLabel(str(len(product_names)))) # Count of unique products
        form_layout.addRow("Estimated Time (min):", QLabel(str(self.task_data['duree'])))

        status_label = QLabel(self.task_data['status'].capitalize())
        status_label.setStyleSheet("color: #000000; font-weight: bold;")
        form_layout.addRow("Status:", status_label)

        form_layout.addRow("Priority:", QLabel(self.task_data['priority'].capitalize()))
        form_layout.addRow("Due Time:", QLabel(self.task_data['date-ech'].strftime('%Y-%m-%d %H:%M')))
        layout.addLayout(form_layout)

        # Items list (example, could be populated from DB if detailed item list is available)
        items_list_label = QLabel("Task Description:")
        layout.addWidget(items_list_label)
        description_text_edit = QTextEdit()
        description_text_edit.setText(self.task_data['description'])
        description_text_edit.setReadOnly(True)
        description_text_edit.setFixedHeight(100)
        layout.addWidget(description_text_edit)


        # Buttons
        button_layout = QHBoxLayout()

        complete_button = QPushButton("Mark as Completed")
        complete_button.setStyleSheet("background-color: #38A169; color: white;")
        complete_button.clicked.connect(self.mark_task_completed)
        button_layout.addWidget(complete_button)

        cancel_button = QPushButton("Cancel Task")
        cancel_button.setStyleSheet("background-color: #E53E3E; color: white;")
        cancel_button.clicked.connect(self.cancel_task)
        button_layout.addWidget(cancel_button)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #4A5568; color: white;")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def mark_task_completed(self):
        try:
            cur.execute("SELECT \"EMIR\".updatetache(%s, %s);", (self.task_data['Task_id'], 'Completed'))
            conn.commit()
            QMessageBox.information(self, "Success", f"Task {self.task_data['Task_id']} marked as Completed.")
            self.accept() # Close dialog
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update task status: {e}")
            conn.rollback()

    def cancel_task(self):
        try:
            cur.execute("SELECT \"EMIR\".updatetache(%s, %s);", (self.task_data['Task_id'], 'Cancelled'))
            conn.commit()
            QMessageBox.information(self, "Success", f"Task {self.task_data['Task_id']} marked as Cancelled.")
            self.accept() # Close dialog
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update task status: {e}")
            conn.rollback()

class NewMovementDialog(QDialog):
    """Dialog to record a new product movement."""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Record New Product Movement")
        self.setFixedSize(450, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            }
            QLabel {
                font-size: 15px;
                color: #2D3748;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 1px solid #006775; /* Teal focus color */
            }
            QPushButton {
                background-color: #006775; /* Teal for primary action */
                color: white;
                border: none;
                padding: 13px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #00897B;
            }
        """)

        form_layout = QFormLayout()

        self.product_combo = QComboBox()
        # Populate product combo from DB
        try:
            cur.execute("SELECT (p).* FROM \"EMIR\".Produit_EVA() AS p;")
            products = cur.fetchall()
            product_names = [p[2] for p in products] # Assuming product name is at index 2
            self.product_combo.addItems(product_names)
        except psycopg2.Error as e:
            print(f"Error fetching products: {e}")
            self.product_combo.addItems(["Error loading products"])

        self.product_combo.setEditable(True)
        self.product_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.product_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        form_layout.addRow("Product:", self.product_combo)

        self.movement_type_combo = QComboBox()
        self.movement_type_combo.addItems(['Pick', 'Pack', 'Move', 'Count'])
        form_layout.addRow("Movement Type:", self.movement_type_combo)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000)
        form_layout.addRow("Quantity:", self.quantity_spin)

        self.from_location_input = QLineEdit()
        self.from_location_input.setPlaceholderText("e.g., A1-15")
        form_layout.addRow("From Location:", self.from_location_input)

        self.to_location_input = QLineEdit()
        self.to_location_input.setPlaceholderText("e.g., Shipping Dock")
        form_layout.addRow("To Location:", self.to_location_input)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        record_button = QPushButton("Record Movement")
        record_button.clicked.connect(self.record_movement)
        button_layout.addWidget(record_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("background-color: #CCCCCC;")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def record_movement(self):
        product_name = self.product_combo.currentText()
        product_id = None
        try:
            cur.execute("SELECT id FROM \"EMIR\".Produit WHERE nom = %s;", (product_name,))
            result = cur.fetchone()
            if result:
                product_id = result[0]
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to retrieve product ID: {e}")
            return

        if not product_id:
            QMessageBox.warning(self, "Invalid Product", "Please select a valid product from the list.")
            return

        movement_type = self.movement_type_combo.currentText()
        quantity = self.quantity_spin.value()
        from_location = self.from_location_input.text()
        to_location = self.to_location_input.text()

        if not all([product_name, movement_type, quantity, from_location, to_location]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            # Assuming a stored procedure or function for adding movement
            # This is a placeholder, adjust to your actual DB function
            cur.execute("SELECT \"EMIR\".add_movement(%s, %s, %s, %s, %s, %s);",
                        (product_id, product_name, movement_type, quantity, from_location, to_location))
            conn.commit()
            QMessageBox.information(self, "Success", "Movement recorded successfully!")
            self.accept()
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to record movement: {e}")
            conn.rollback()


class ExceptionDetailDialog(QDialog):
    """Dialog to display details of an exception and allow status update."""
    def __init__(self, exception_data, parent=None):
        super().__init__(parent)
        self.exception_data = exception_data
        self.setWindowTitle(f"Exception Details: {self.exception_data['ID']}")
        self.setFixedSize(500, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            }
            QLabel {
                font-size: 15px;
                color: #2D3748;
            }
            QLabel.title {
                font-size: 24px;
                font-weight: bold;
                color: #2D3748;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #D3DCE0;
            }
            QTextEdit, QComboBox {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }
            QTextEdit:focus, QComboBox:focus {
                border: 1px solid #E53E3E; /* Red focus color */
            }
            QPushButton {
                background-color: #E53E3E; /* Red for primary action */
                color: white;
                border: none;
                padding: 13px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)

        title_label = QLabel(f"Exception: {self.exception_data['ID']}")
        title_label.setProperty("class", "title")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.addRow("Type:", QLabel(self.exception_data['Type']))
        form_layout.addRow("Product:", QLabel(self.exception_data['Product_Name']))
        form_layout.addRow("Location:", QLabel(self.exception_data['Location']))
        form_layout.addRow("Reported By:", QLabel(self.exception_data['Reported_By']))
        form_layout.addRow("Reported Time:", QLabel(self.exception_data['Reported_Time'].strftime('%Y-%m-%d %H:%M')))

        description_label = QLabel("Description:")
        layout.addWidget(description_label)
        description_text = QTextEdit()
        description_text.setText(self.exception_data['Description'])
        description_text.setReadOnly(True)
        layout.addWidget(description_text)

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Update Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(['Open', 'In Review', 'Resolved'])
        self.status_combo.setCurrentText(self.exception_data['Status'])
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save Status")
        save_button.clicked.connect(self.save_status)
        button_layout.addWidget(save_button)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #CCCCCC;")
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def save_status(self):
        new_status = self.status_combo.currentText()
        if new_status != self.exception_data['Status']:
            try:
                # Assuming a stored procedure or function for updating exception status
                cur.execute("SELECT \"EMIR\".update_exception_status(%s, %s);",
                            (self.exception_data['ID'], new_status))
                conn.commit()
                QMessageBox.information(self, "Status Updated", f"Exception {self.exception_data['ID']} status updated to {new_status}.")
                self.accept()
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", f"Failed to update exception status: {e}")
                conn.rollback()
        else:
            self.accept()

class NewExceptionDialog(QDialog):
    """Dialog to report a new exception."""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Report New Exception")
        self.setFixedSize(450, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            }
            QLabel {
                font-size: 15px;
                color: #2D3748;
            }
            QLineEdit, QComboBox, QTextEdit {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #E53E3E; /* Red focus color */
            }
            QPushButton {
                background-color: #E53E3E; /* Red for primary action */
                color: white;
                border: none;
                padding: 13px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)

        form_layout = QFormLayout()

        self.exception_type_combo = QComboBox()
        self.exception_type_combo.addItems(['Damaged Product', 'Missing Item', 'Location Error', 'Quantity Mismatch', 'System Error', 'Other'])
        form_layout.addRow("Exception Type:", self.exception_type_combo)

        self.product_combo = QComboBox()
        # Populate product combo from DB
        try:
            cur.execute("SELECT (p).* FROM \"EMIR\".Produit_EVA() AS p;")
            products = cur.fetchall()
            product_names = [p[2] for p in products]
            self.product_combo.addItems(product_names)
        except psycopg2.Error as e:
            print(f"Error fetching products: {e}")
            self.product_combo.addItems(["Error loading products"])

        self.product_combo.setEditable(True)
        self.product_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.product_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        form_layout.addRow("Affected Product:", self.product_combo)

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("e.g., A1-15")
        form_layout.addRow("Location:", self.location_input)

        description_label = QLabel("Description:")
        layout.addWidget(description_label)
        self.description_text = QTextEdit()
        self.description_text.setPlaceholderText("Provide detailed information about the exception...")
        layout.addWidget(self.description_text)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        report_button = QPushButton("Report Exception")
        report_button.clicked.connect(self.report_exception)
        button_layout.addWidget(report_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("background-color: #CCCCCC;")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def report_exception(self):
        exception_type = self.exception_type_combo.currentText()
        product_name = self.product_combo.currentText()
        product_id = None
        try:
            cur.execute("SELECT id FROM \"EMIR\".Produit WHERE nom = %s;", (product_name,))
            result = cur.fetchone()
            if result:
                product_id = result[0]
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to retrieve product ID: {e}")
            return

        if not product_id:
            QMessageBox.warning(self, "Invalid Product", "Please select a valid product from the list.")
            return

        location = self.location_input.text()
        description = self.description_text.toPlainText()

        if not all([exception_type, product_name, location, description]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            # Assuming a stored procedure or function for adding exception
            # This is a placeholder, adjust to your actual DB function
            cur.execute("SELECT \"EMIR\".add_exception(%s, %s, %s, %s, %s);",
                        (exception_type, product_id, product_name, location, description))
            conn.commit()
            QMessageBox.information(self, "Success", "Exception reported successfully!")
            self.accept()
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to report exception: {e}")
            conn.rollback()

class WorkerData:
    """Data manager for warehouse worker operations, fetching from PostgreSQL."""

    def __init__(self):
        self.products_df = pd.DataFrame()
        self.expedition_tasks = pd.DataFrame()
        self.movement_history = pd.DataFrame()
        self.exceptions = pd.DataFrame()
        self.storage_cells = {}
        self.load_data_from_db()
        self.initialize_storage_cells() # Initialize based on DB data if possible

    def load_data_from_db(self):
        try:
            # Load Products data
            cur.execute("SELECT id, fournisseur, nom, description, prix_unitaire, marque, modele, categorie FROM \"EMIR\".Produit_EVA();")
            products = cur.fetchall()
            self.products_df = pd.DataFrame(products, columns=['ID', 'Fournisseur', 'Name', 'Description', 'Prix Unitaire', 'Brand', 'Model', 'Category'])
            if self.products_df.empty:
                print("No products loaded from DB. Using dummy data for products.")
                self.products_df = pd.DataFrame(
                    [
                        ('P001', 'SupplierA', 'Dummy Product 1', 'Desc 1', 10.0, 'BrandX', 'ModelA', 'Electronics'),
                        ('P002', 'SupplierB', 'Dummy Product 2', 'Desc 2', 20.0, 'BrandY', 'ModelB', 'Furniture')
                    ],
                    columns=['ID', 'Fournisseur', 'Name', 'Description', 'Prix Unitaire', 'Brand', 'Model', 'Category']
                )

            # Load Expedition Tasks data
            cur.execute("SELECT id, cell, colis, date_creation, date_echeance, duree, description, priorite, statut, type FROM \"EMIR\".Tache_EVA(%s);", (worker_id,))
            tasks = cur.fetchall()
            self.expedition_tasks = pd.DataFrame(tasks, columns=['Task_id', 'Cell', 'Colis', 'date-cre', 'date-ech', 'duree', 'description', 'priority', 'status', 'type'])
            # Convert datetime columns
            self.expedition_tasks['date-cre'] = pd.to_datetime(self.expedition_tasks['date-cre'])
            self.expedition_tasks['date-ech'] = pd.to_datetime(self.expedition_tasks['date-ech'])
            if self.expedition_tasks.empty:
                print("No tasks loaded from DB. Using dummy data for tasks.")
                self.expedition_tasks = pd.DataFrame(
                    [
                        ('T001', 'A1-1', 'C001', datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(hours=2), 30, 'Pick items for order 1', 'high', 'en cours', 'Pick'),
                        ('T002', 'B2-1', 'C002', datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(hours=4), 60, 'Pack items for order 2', 'medium', 'en cours', 'Pack'),
                    ],
                    columns=['Task_id', 'Cell', 'Colis', 'date-cre', 'date-ech', 'duree', 'description', 'priority', 'status', 'type']
                )


            # Load Product Movement History (assuming a view/table for this)
            # Placeholder: Adjust query to your actual movement history table/view
            cur.execute("SELECT id, product_id, product_name, movement_type, quantity, from_location, to_location, timestamp, worker_id FROM \"EMIR\".Movement_History_View;")
            movements = cur.fetchall()
            self.movement_history = pd.DataFrame(movements, columns=['Movement_ID', 'Product_ID', 'Product_Name', 'Movement_Type', 'Quantity', 'From_Location', 'To_Location', 'Timestamp', 'Worker'])
            self.movement_history['Timestamp'] = pd.to_datetime(self.movement_history['Timestamp'])
            if self.movement_history.empty:
                print("No movements loaded from DB. Using dummy data for movements.")
                self.movement_history = pd.DataFrame(
                    [
                        ('MOV001', 'P001', 'Dummy Product 1', 'Pick', 5, 'A1-1', 'Packing Area', datetime.datetime.now() - datetime.timedelta(minutes=30), 'TR1234'),
                        ('MOV002', 'P002', 'Dummy Product 2', 'Move', 10, 'B2-1', 'A1-2', datetime.datetime.now() - datetime.timedelta(hours=1), 'TR1234'),
                    ],
                    columns=['Movement_ID', 'Product_ID', 'Product_Name', 'Movement_Type', 'Quantity', 'From_Location', 'To_Location', 'Timestamp', 'Worker']
                )

            # Load Exceptions (assuming a view/table for this)
            # Placeholder: Adjust query to your actual exceptions table/view
            cur.execute("SELECT id, type, product_id, product_name, location, reported_time, status, reported_by, description FROM \"EMIR\".Exception_Reports_View;")
            exceptions = cur.fetchall()
            self.exceptions = pd.DataFrame(exceptions, columns=['ID', 'Type', 'Product_ID', 'Product_Name', 'Location', 'Reported_Time', 'Status', 'Reported_By', 'Description'])
            self.exceptions['Reported_Time'] = pd.to_datetime(self.exceptions['Reported_Time'])
            if self.exceptions.empty:
                print("No exceptions loaded from DB. Using dummy data for exceptions.")
                self.exceptions = pd.DataFrame(
                    [
                        ('EXC001', 'Damaged Product', 'P001', 'Dummy Product 1', 'A1-1', datetime.datetime.now() - datetime.timedelta(days=1), 'Open', 'TR1234', 'Product packaging damaged during transit.'),
                        ('EXC002', 'Missing Item', 'P002', 'Dummy Product 2', 'B2-1', datetime.datetime.now() - datetime.timedelta(hours=5), 'In Review', 'Supervisor X', 'One unit missing from expected delivery.'),
                    ],
                    columns=['ID', 'Type', 'Product_ID', 'Product_Name', 'Location', 'Reported_Time', 'Status', 'Reported_By', 'Description']
                )

        except psycopg2.Error as e:
            print(f"Database error during data loading: {e}")
            # Fallback to dummy data if DB connection is problematic
            self.generate_dummy_data_if_empty()

    def generate_dummy_data_if_empty(self):
        # This function acts as a fallback if DB loading fails or returns empty
        if self.products_df.empty:
            self.products_df = pd.DataFrame(
                [
                    ('P001', 'SupplierA', 'Dummy Product 1', 'Desc 1', 10.0, 'BrandX', 'ModelA', 'Electronics'),
                    ('P002', 'SupplierB', 'Dummy Product 2', 'Desc 2', 20.0, 'BrandY', 'ModelB', 'Furniture')
                ],
                columns=['ID', 'Fournisseur', 'Name', 'Description', 'Prix Unitaire', 'Brand', 'Model', 'Category']
            )
        if self.expedition_tasks.empty:
            self.expedition_tasks = pd.DataFrame(
                [
                    ('T001', 'A1-1', 'C001', datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(hours=2), 30, 'Pick items for order 1', 'high', 'en cours', 'Pick'),
                    ('T002', 'B2-1', 'C002', datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(hours=4), 60, 'Pack items for order 2', 'medium', 'en cours', 'Pack'),
                ],
                columns=['Task_id', 'Cell', 'Colis', 'date-cre', 'date-ech', 'duree', 'description', 'priority', 'status', 'type']
            )
        if self.movement_history.empty:
            self.movement_history = pd.DataFrame(
                [
                    ('MOV001', 'P001', 'Dummy Product 1', 'Pick', 5, 'A1-1', 'Packing Area', datetime.datetime.now() - datetime.timedelta(minutes=30), 'TR1234'),
                    ('MOV002', 'P002', 'Dummy Product 2', 'Move', 10, 'B2-1', 'A1-2', datetime.datetime.now() - datetime.timedelta(hours=1), 'TR1234'),
                ],
                columns=['Movement_ID', 'Product_ID', 'Product_Name', 'Movement_Type', 'Quantity', 'From_Location', 'To_Location', 'Timestamp', 'Worker']
            )
        if self.exceptions.empty:
            self.exceptions = pd.DataFrame(
                [
                    ('EXC001', 'Damaged Product', 'P001', 'Dummy Product 1', 'A1-1', datetime.datetime.now() - datetime.timedelta(days=1), 'Open', 'TR1234', 'Product packaging damaged during transit.'),
                    ('EXC002', 'Missing Item', 'P002', 'Dummy Product 2', 'B2-1', datetime.datetime.now() - datetime.timedelta(hours=5), 'In Review', 'Supervisor X', 'One unit missing from expected delivery.'),
                ],
                columns=['ID', 'Type', 'Product_ID', 'Product_Name', 'Location', 'Reported_Time', 'Status', 'Reported_By', 'Description']
            )


    def initialize_storage_cells(self):
        self.storage_cells = {}
        # Fetch actual zones/cells from DB if available
        try:
            cur.execute("SELECT id, nom_zone, capacite, statut FROM \"EMIR\".Zone_EVA();") # Assuming a Zone_EVA view/table
            zones = cur.fetchall()
            for zone_id, nom_zone, capacite, statut in zones:
                # For simplicity, map zones directly to cells or create dummy cells within zones
                # If your DB has specific cell IDs, fetch those instead
                self.storage_cells[nom_zone] = { # Using nom_zone as key for simplicity
                    'products': {},
                    'capacity': capacite,
                    'status': statut
                }
            
            # Populate products in cells based on DB data
            for _, product in self.products_df.iterrows():
                try:
                    cur.execute('SELECT nom_zone FROM \"EMIR\".Zone WHERE id = (SELECT id_zone FROM \"EMIR\".Produit WHERE id = %s);', (product['ID'],))
                    zone_result = cur.fetchone()
                    if zone_result:
                        zone_name = zone_result[0]
                        cur.execute('SELECT quantity FROM \"EMIR\".Produit WHERE id = %s;', (product['ID'],))
                        quantity_result = cur.fetchone()
                        quantity = quantity_result[0] if quantity_result else 0

                        if zone_name in self.storage_cells:
                            self.storage_cells[zone_name]['products'][product['ID']] = self.storage_cells[zone_name]['products'].get(product['ID'], 0) + quantity
                            self.storage_cells[zone_name]['status'] = 'Occupied' if self.storage_cells[zone_name]['products'] else 'Available'
                        else:
                            print(f"Warning: Zone '{zone_name}' for product '{product['Name']}' not found in initialized storage cells.")
                except psycopg2.Error as e:
                    print(f"Error populating product {product['ID']} into storage cells: {e}")

        except psycopg2.Error as e:
            print(f"Error initializing storage cells from database: {e}")
            # Fallback to dummy cells if DB fails
            warehouse_layout = {'A': 3, 'B': 3, 'C': 2, 'D': 2}
            for aisle, num_cols in warehouse_layout.items():
                for row in range(1, 4):
                    for col in range(1, num_cols + 1):
                        cell_id = f"{aisle}{row}-{col}"
                        self.storage_cells[cell_id] = {
                            'products': {},
                            'capacity': random.randint(50, 200),
                            'status': 'Available'
                        }
            # Distribute dummy products if no DB products
            if self.products_df.empty:
                for _ in range(10): # Add 10 dummy products to random cells
                    product = self.products_df.sample(1).iloc[0]
                    available_cells = [cid for cid, data in self.storage_cells.items() if data['status'] == 'Available']
                    if available_cells:
                        target_cell_id = random.choice(available_cells)
                        qty = random.randint(1, 20)
                        self.storage_cells[target_cell_id]['products'][product['ID']] = self.storage_cells[target_cell_id]['products'].get(product['ID'], 0) + qty
                        self.storage_cells[target_cell_id]['status'] = 'Occupied'


    def get_cell_contents(self, cell_id):
        return self.storage_cells.get(cell_id, {'products': {}, 'capacity': 0, 'status': 'Unknown'})


class WorkerMainDashboard(QWidget):
    """Main dashboard widget for warehouse workers with a new design."""

    def __init__(self, data, main_window):
        super().__init__()
        self.data = data
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20) # Add some padding around the dashboard content
        layout.setSpacing(25)

        # Hero Section (inspired by Design_Worker.py's header principles)
        hero_frame = QFrame()
        hero_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #006775, stop:1 #006775); /* Gradient background */
                border-radius: 15px;
                padding: 25px;
                color: #FFFFFF;
                box-shadow: 0 8px 25px rgba(108, 99, 255, 0.3);
            }
            QLabel {
                color: #FFFFFF;
            }
        """)
        hero_layout = QVBoxLayout(hero_frame)

        welcome_label = QLabel(f"Welcome Back, Worker {worker_id}!")
        welcome_label.setStyleSheet("font-size: 36px; font-weight: bold;")

        time_label = QLabel(f"Today: {datetime.datetime.now().strftime('%A, %B %d, %Y')}")
        time_label.setStyleSheet("font-size: 16px; margin-top: 5px;")

        hero_layout.addWidget(welcome_label)
        hero_layout.addWidget(time_label)
        hero_layout.addStretch() # Push content to top

        # Dashboard Stat Cards (using MetricCard from Design_Worker.py)
        dashboard_stats_layout = QHBoxLayout()
        dashboard_stats_layout.setSpacing(20)

        my_pending_tasks = len([t for t in self.data.expedition_tasks.to_dict('records') if t['status'].lower() == 'en cours' and t['Task_id']]) # Check for valid Task_id
        completed_today = len([t for t in self.data.expedition_tasks.to_dict('records') if t['status'].lower() == 'completed' and t['date-ech'].date() == datetime.date.today()])
        my_movements = len([m for m in self.data.movement_history.to_dict('records') if m['Worker'] == worker_id]) # Use global worker_id
        open_exceptions = len([e for e in self.data.exceptions.to_dict('records') if e['Status'].lower() == 'open'])

        dashboard_stats_layout.addWidget(MetricCard("My Pending Tasks", my_pending_tasks, "#F6AD55", "📝"))
        dashboard_stats_layout.addWidget(MetricCard("Completed Today", completed_today, "#38A169", "✅"))
        dashboard_stats_layout.addWidget(MetricCard("My Movements", my_movements, "#006775", "🔄"))
        dashboard_stats_layout.addWidget(MetricCard("Open Exceptions", open_exceptions, "#E53E3E", "⚠️"))

        hero_layout.addLayout(dashboard_stats_layout)
        layout.addWidget(hero_frame)


        # Quick Actions
        quick_actions_group = QGroupBox("Quick Actions")
        quick_actions_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #2D3748;
                margin-top: 20px;
                border: 1px solid #D3DCE0;
                border-radius: 10px;
                padding-top: 15px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                margin-left: 10px;
                color: #006775; /* Accent color for title */
            }
        """)
        quick_actions_layout = QHBoxLayout()
        quick_actions_layout.setSpacing(15)
        quick_actions_layout.setContentsMargins(20, 25, 20, 20)

        button_style = """
            QPushButton {
                background-color: #EDF2F7; /* Light background */
                border: none;
                border-radius: 10px;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: 600;
                color: #2D3748;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #006775; /* Primary accent on hover */
                color: #FFFFFF;
                transform: translateY(-2px); /* Slight lift effect */
            }
        """

        pick_pack_btn = QPushButton("View Pick/Pack Tasks")
        pick_pack_btn.setStyleSheet(button_style)
        pick_pack_btn.clicked.connect(lambda: self.main_window.navigate_to_widget(self.main_window.expedition_widget))

        record_movement_btn = QPushButton("Record New Movement")
        record_movement_btn.setStyleSheet(button_style)
        record_movement_btn.clicked.connect(lambda: self.main_window.navigate_to_widget(self.main_window.movement_widget))

        report_exception_btn = QPushButton("Report an Exception")
        report_exception_btn.setStyleSheet(button_style)
        report_exception_btn.clicked.connect(lambda: self.main_window.navigate_to_widget(self.main_window.exception_widget))

        quick_actions_layout.addWidget(pick_pack_btn)
        quick_actions_layout.addWidget(record_movement_btn)
        quick_actions_layout.addWidget(report_exception_btn)
        quick_actions_group.setLayout(quick_actions_layout)
        layout.addWidget(quick_actions_group)

        # Recent activities
        recent_activity_group = QGroupBox("Recent Activities")
        recent_activity_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #2D3748;
                margin-top: 20px;
                border: 1px solid #D3DCE0;
                border-radius: 10px;
                padding-top: 15px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                margin-left: 10px;
                color: #006775; /* Secondary accent for title */
            }
        """)
        recent_activity_layout = QVBoxLayout()
        recent_activity_layout.setContentsMargins(20, 25, 20, 20)
        recent_activity_layout.setSpacing(10)

        latest_movements = sorted(self.data.movement_history.to_dict('records'), key=lambda x: x['Timestamp'], reverse=True)[:5]
        if latest_movements:
            for movement in latest_movements:
                activity_label = QLabel(f"<span style='font-weight:bold;'>{movement['Timestamp'].strftime('%H:%M')}</span> | {movement['Movement_Type']} of <span style='font-weight:bold;'>{movement['Quantity']}x</span> {movement['Product_Name']} by {movement['Worker']}")
                activity_label.setStyleSheet("font-size: 14px; color: #444; padding: 2px 0;")
                activity_label.setTextFormat(Qt.TextFormat.RichText)
                recent_activity_layout.addWidget(activity_label)
        else:
            no_activity_label = QLabel("No recent activities to display.")
            no_activity_label.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
            recent_activity_layout.addWidget(no_activity_label)

        recent_activity_group.setLayout(recent_activity_layout)
        layout.addWidget(recent_activity_group)
        layout.addStretch()

        self.setLayout(layout)

class ExpeditionManagementWidget(QWidget):
    """Widget for managing expedition tasks (picking and packing) with new design."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Expedition Management")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2D3748;")

        refresh_btn = QPushButton("Refresh Tasks")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #006775;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                box-shadow: 0 4px 10px rgba(108, 99, 255, 0.2);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #004F5C;
                transform: translateY(-2px);
            }
        """)
        refresh_btn.clicked.connect(self.refresh_tasks)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)

        # Quick stats (using MetricCard-like styling)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        pending_tasks = len([t for t in self.data.expedition_tasks.to_dict('records') if t['status'].lower() == 'en cours'])
        in_progress_tasks = len([t for t in self.data.expedition_tasks.to_dict('records') if t['status'].lower() == 'progress'])
        completed_today = len([t for t in self.data.expedition_tasks.to_dict('records') if t['status'].lower() == 'completed' and t['date-ech'].date() == datetime.date.today()])

        stats_layout.addWidget(MetricCard("Pending Tasks", pending_tasks, "#F6AD55", "⏳"))
        stats_layout.addWidget(MetricCard("In Progress", in_progress_tasks, "#006775", "🚀"))
        stats_layout.addWidget(MetricCard("Completed Today", completed_today, "#38A169", "✔️"))
        layout.addLayout(stats_layout)

        # Task sections using QSplitter for adjustable layout
        sections_splitter = QSplitter(Qt.Orientation.Horizontal)
        sections_splitter.setHandleWidth(10)
        sections_splitter.setStyleSheet("QSplitter::handle { background-color: #D3DCE0; border-radius: 5px; }")

        # My Current Tasks
        self.my_tasks_section = self.create_task_section("My Current Tasks",
            [t for t in self.data.expedition_tasks.to_dict('records') if t['status'].lower() != 'completed' and t['Task_id']])
        sections_splitter.addWidget(self.my_tasks_section)

        # High Priority Tasks
        self.high_priority_section = self.create_task_section("High Priority Tasks",
            [t for t in self.data.expedition_tasks.to_dict('records') if t['priority'].lower() == 'high' and t['status'].lower() != 'completed' and t['Task_id']])
        sections_splitter.addWidget(self.high_priority_section)

        sections_splitter.setSizes([self.width() // 2, self.width() // 2]) # Initial sizes
        layout.addWidget(sections_splitter)

        self.setLayout(layout)

    def create_task_section(self, title, tasks):
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #D3DCE0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2D3748; margin-bottom: 5px;")
        layout.addWidget(title_label)

        # Scrollable task list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMaximumHeight(600) # Increased height for more tasks

        task_widget = QWidget()
        task_layout = QVBoxLayout(task_widget)
        task_layout.setSpacing(10) # Spacing between task cards

        if tasks:
            for task in tasks:
                task_card = TaskCard(task, "expedition")
                task_card.task_selected.connect(self.on_task_selected)
                task_layout.addWidget(task_card)
        else:
            no_tasks_label = QLabel("No tasks available in this section.")
            no_tasks_label.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
            task_layout.addWidget(no_tasks_label)

        task_layout.addStretch()
        scroll_area.setWidget(task_widget)
        layout.addWidget(scroll_area)

        section.setLayout(layout)
        return section

    def on_task_selected(self, task_data):
        dialog = TaskDetailDialog(task_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_tasks() # Refresh tasks after a task is updated/completed

    def refresh_tasks(self):
        self.data.load_data_from_db() # Reload data
        # Re-create sections to reflect updated data
        self.update_task_section(self.my_tasks_section, "My Current Tasks",
            [t for t in self.data.expedition_tasks.to_dict('records') if t['status'].lower() != 'completed' and t['Task_id']])
        self.update_task_section(self.high_priority_section, "High Priority Tasks",
            [t for t in self.data.expedition_tasks.to_dict('records') if t['priority'].lower() == 'high' and t['status'].lower() != 'completed' and t['Task_id']])

    def update_task_section(self, section_widget, title, tasks):
        # Find the QVBoxLayout within the section_widget
        layout_to_clear = section_widget.layout()
        if layout_to_clear:
            # Remove all existing task cards (except the title label)
            for i in reversed(range(layout_to_clear.count())):
                item = layout_to_clear.itemAt(i)
                if item and item.widget() and not isinstance(item.widget(), QLabel): # Keep the title label
                    item.widget().setParent(None)
                    item.widget().deleteLater()
                elif item and item.layout(): # If it's a layout, clear it too
                    self.clear_layout(item.layout())

            # Re-add title (if it was removed or to ensure it's first)
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2D3748; margin-bottom: 5px;")
            layout_to_clear.insertWidget(0, title_label) # Insert at the beginning

            # Find the QScrollArea and its internal widget's layout
            scroll_area = section_widget.findChild(QScrollArea)
            if scroll_area:
                task_widget = scroll_area.widget()
                task_layout = task_widget.layout()
                if task_layout:
                    self.clear_layout(task_layout) # Clear existing task cards within scroll area

                    if tasks:
                        for task in tasks:
                            task_card = TaskCard(task, "expedition")
                            task_card.task_selected.connect(self.on_task_selected)
                            task_layout.addWidget(task_card)
                    else:
                        no_tasks_label = QLabel("No tasks available in this section.")
                        no_tasks_label.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
                        task_layout.addWidget(no_tasks_label)
                    task_layout.addStretch() # Ensure stretch is at the end

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())


class ProductMovementTrackingWidget(QWidget):
    """Widget for tracking product movements and location updates with new design."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Product Movement Tracking")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2D3748;")

        new_movement_btn = QPushButton("Record Movement")
        new_movement_btn.setStyleSheet("""
            QPushButton {
                background-color: #006775; /* Teal */
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                box-shadow: 0 4px 10px rgba(0, 191, 165, 0.2);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #00897B;
                transform: translateY(-2px);
            }
        """)
        new_movement_btn.clicked.connect(self.record_new_movement)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(new_movement_btn)
        layout.addLayout(header_layout)

        # Filters and Search
        filter_search_layout = QHBoxLayout()
        filter_search_layout.setSpacing(15)

        search_label = QLabel("Search Product:")
        search_label.setStyleSheet("font-size: 15px; color: #666;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter product ID or name...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 1px solid #006775;
            }
        """)
        self.search_input.textChanged.connect(self.filter_movements)

        type_label = QLabel("Filter by type:")
        type_label.setStyleSheet("font-size: 15px; color: #666;")
        self.type_combo = QComboBox()
        self.type_combo.addItems(['All', 'Pick', 'Pack', 'Move', 'Count'])
        self.type_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: #FFFFFF;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down.png); /* Placeholder for an actual icon if you have one */
                width: 13px;
                height: 13px;
            }
        """)
        self.type_combo.currentTextChanged.connect(self.filter_movements)

        filter_search_layout.addWidget(search_label)
        filter_search_layout.addWidget(self.search_input, 3)
        filter_search_layout.addWidget(type_label)
        filter_search_layout.addWidget(self.type_combo, 1)
        filter_search_layout.addStretch() # Push widgets to left

        layout.addLayout(filter_search_layout)

        # Recent movements table
        self.movements_table = self.create_movements_table()
        layout.addWidget(self.movements_table)

        self.setLayout(layout)

    def create_movements_table(self):
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(['Time', 'Product', 'Type', 'Quantity', 'From', 'To', 'Worker'])

        table.verticalHeader().setDefaultSectionSize(40)

        table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #D3DCE0;
                border-radius: 10px;
                font-size: 14px;
                selection-background-color: #E6E6FF; /* Light purple selection */
                selection-color: #2D3748;
                gridline-color: #EDF2F7; /* Lighter grid lines */
            }
            QHeaderView::section {
                background-color: #006775; /* Primary accent for header */
                color: #FFFFFF;
                padding: 13px;
                border: none;
                font-weight: bold;
                font-size: 15px;
                text-align: left; /* Align header text left */
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px;
            }
            QTableWidget::item {
                padding: 8px; /* Padding for cell content */
            }
            QTableWidget::item:selected {
                background-color: #006775;
                color: #2D3748;
            }
        """)

        self.update_movements_table(self.data.movement_history.to_dict('records'))

        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.resizeColumnsToContents()

        return table
    def filter_movements(self):
        search_text = self.search_input.text().lower()
        movement_type = self.type_combo.currentText()

        filtered_movements = []
        for movement in self.data.movement_history.to_dict('records'):
            product_name_lower = movement['Product_Name'].lower()
            product_id_lower = movement['Product_ID'].lower() if movement['Product_ID'] else ''

            if search_text and not (search_text in product_name_lower or search_text in product_id_lower):
                continue
            if movement_type != 'All' and movement['Movement_Type'] != movement_type:
                continue
            filtered_movements.append(movement)

        self.update_movements_table(filtered_movements)

    def update_movements_table(self, movements):
        sorted_movements = sorted(movements, key=lambda x: x['Timestamp'], reverse=True)
        self.movements_table.setRowCount(len(sorted_movements))

        accent_color = "#006775"

        for i, movement in enumerate(sorted_movements):
            self.movements_table.setItem(i, 0, QTableWidgetItem(movement['Timestamp'].strftime('%H:%M %b %d')))
            self.movements_table.setItem(i, 1, QTableWidgetItem(movement['Product_Name']))

            type_item = QTableWidgetItem(movement['Movement_Type'])
            type_item.setBackground(QColor(accent_color))
            type_item.setForeground(QColor('#FFFFFF'))
            self.movements_table.setItem(i, 2, type_item)

            self.movements_table.setItem(i, 3, QTableWidgetItem(str(movement['Quantity'])))
            self.movements_table.setItem(i, 4, QTableWidgetItem(movement['From_Location']))
            self.movements_table.setItem(i, 5, QTableWidgetItem(movement['To_Location']))

            worker_item = QTableWidgetItem(movement['Worker'])
            if movement['Worker'] == worker_id: # Use global worker_id
                worker_item.setBackground(QColor('#E8F5E8'))
                worker_item.setForeground(QColor('#2D3748'))
            self.movements_table.setItem(i, 6, worker_item)

    def record_new_movement(self):
        dialog = NewMovementDialog(self.data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.data.load_data_from_db() # Reload data to get the new movement
            self.update_movements_table(self.data.movement_history.to_dict('records'))
            self.filter_movements() # Re-apply filters after update

class ExceptionReportsWidget(QWidget):
    """Widget for viewing and managing exception reports with new design."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Exception Reports")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2D3748;")

        report_exception_btn = QPushButton("Report Exception")
        report_exception_btn.setStyleSheet("""
            QPushButton {
                background-color: #E53E3E; /* Red */
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                box-shadow: 0 4px 10px rgba(244, 67, 54, 0.2);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #D32F2F;
                transform: translateY(-2px);
            }
        """)
        report_exception_btn.clicked.connect(self.report_new_exception)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(report_exception_btn)
        layout.addLayout(header_layout)

        # Exception stats (using MetricCard-like styling)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        open_exceptions = len([e for e in self.data.exceptions.to_dict('records') if e['Status'].lower() == 'open'])
        in_review = len([e for e in self.data.exceptions.to_dict('records') if e['Status'].lower() == 'in review'])
        resolved_today = len([e for e in self.data.exceptions.to_dict('records') if e['Status'].lower() == 'resolved' and e['Reported_Time'].date() == datetime.date.today()])

        stats_layout.addWidget(MetricCard("Open Reports", open_exceptions, "#E53E3E", "🚨"))
        stats_layout.addWidget(MetricCard("In Review", in_review, "#F6AD55", "🔍"))
        stats_layout.addWidget(MetricCard("Resolved Today", resolved_today, "#38A169", "✔️"))
        layout.addLayout(stats_layout)

        # Exceptions table
        self.exceptions_table = self.create_exceptions_table()
        layout.addWidget(self.exceptions_table)

        self.setLayout(layout)

    def create_exceptions_table(self):
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(['ID', 'Type', 'Product', 'Location', 'Time', 'Status'])

        table.verticalHeader().setDefaultSectionSize(40)

        table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #D3DCE0;
                border-radius: 10px;
                font-size: 14px;
                selection-background-color: #FFEBEE; /* Light red selection */
                selection-color: #2D3748;
                gridline-color: #EDF2F7;
            }
            QHeaderView::section {
                background-color:#006775; /* Primary accent for header */
                color: #FFFFFF;
                padding: 13px;
                border: none;
                font-weight: bold;
                font-size: 15px;
                text-align: left;
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #006775;
                color: #2D3748;
            }
        """)

        self.update_exceptions_table(self.data.exceptions.to_dict('records'))

        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.resizeColumnsToContents()
        table.cellDoubleClicked.connect(self.view_exception_details)

        return table

    def update_exceptions_table(self, exceptions):
        sorted_exceptions = sorted(exceptions, key=lambda x: x['Reported_Time'], reverse=True)
        self.exceptions_table.setRowCount(len(sorted_exceptions))

        for i, exception in enumerate(sorted_exceptions):
            self.exceptions_table.setItem(i, 0, QTableWidgetItem(exception['ID']))
            self.exceptions_table.setItem(i, 1, QTableWidgetItem(exception['Type']))
            self.exceptions_table.setItem(i, 2, QTableWidgetItem(exception['Product_Name']))
            self.exceptions_table.setItem(i, 3, QTableWidgetItem(exception['Location']))
            self.exceptions_table.setItem(i, 4, QTableWidgetItem(exception['Reported_Time'].strftime('%m/%d %H:%M')))

            status_item = QTableWidgetItem(exception['Status'])
            status_colors = {
                'Open': '#E53E3E', # Red
                'In Review': '#F6AD55', # Amber
                'Resolved': '#38A169' # Green
            }
            status_item.setBackground(QColor(status_colors.get(exception['Status'], '#D3DCE0')))
            status_item.setForeground(QColor('#FFFFFF'))
            if exception['Status'] == 'In Review':
                status_item.setForeground(QColor('#2D3748'))
            self.exceptions_table.setItem(i, 5, status_item)

    def view_exception_details(self, row, column):
        exception_id = self.exceptions_table.item(row, 0).text()
        # Find the full exception data from the original DataFrame using the ID
        exception_data = self.data.exceptions[self.data.exceptions['ID'] == exception_id].iloc[0]

        if exception_data is not None:
            dialog = ExceptionDetailDialog(exception_data.to_dict(), self) # Pass as dict
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.data.load_data_from_db() # Reload data to get updated status
                self.update_exceptions_table(self.data.exceptions.to_dict('records'))

    def report_new_exception(self):
        dialog = NewExceptionDialog(self.data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.data.load_data_from_db() # Reload data after new entry
            self.update_exceptions_table(self.data.exceptions.to_dict('records'))

class StorageCellWidget(QWidget):
    """Widget for viewing and managing storage cells in a 2D grid."""
    cell_clicked = pyqtSignal(str) # Signal to emit the cell ID when clicked

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Cellule d'Entreposage (2D View)")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2D3748;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Storage grid area
        grid_scroll_area = QScrollArea()
        grid_scroll_area.setWidgetResizable(True)
        grid_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.setSpacing(10) # Spacing between cells
        self.grid_layout.setContentsMargins(10, 10, 10, 10)

        # Populate the grid with cells
        self.populate_cell_grid()

        grid_scroll_area.setWidget(grid_widget)
        layout.addWidget(grid_scroll_area)

        self.setLayout(layout)

    def populate_cell_grid(self):
        # Clear existing widgets if repopulating
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Get all unique aisles and sort for horizontal layout
        # Assuming cell IDs are like 'A1-1', 'B2-3', or zone names like 'Zone A', 'Zone B'
        # Adapt this logic based on how your storage_cells keys are structured (e.g., 'A1-1' vs 'Zone A')
        # For now, assuming keys are like 'Zone A', 'Zone B' from DB or 'A1-1' from dummy data
        
        # Determine if keys are 'Zone X' or 'A1-1' format
        if self.data.storage_cells:
            sample_key = next(iter(self.data.storage_cells.keys()))
            if 'Zone' in sample_key: # Assuming 'Zone A', 'Zone B' format
                aisles = sorted(list(self.data.storage_cells.keys())) # Use zone names as aisles
                max_rows_per_aisle = 1 # Each zone is a single "cell" in this view
                max_cols_per_aisle = 1
            else: # Assuming 'A1-1' format
                aisles = sorted(list(set(c[0] for c in self.data.storage_cells.keys() if '-' in c)))
                # Dynamically determine max rows/cols if using A1-1 format
                max_rows_per_aisle = 0
                max_cols_per_aisle = 0
                for cell_id in self.data.storage_cells.keys():
                    if '-' in cell_id:
                        try:
                            parts = cell_id.split('-')
                            row_part = parts[0][1:] # e.g., '1' from 'A1'
                            col_part = parts[1] # e.g., '1' from 'A1-1'
                            max_rows_per_aisle = max(max_rows_per_aisle, int(row_part))
                            max_cols_per_aisle = max(max_cols_per_aisle, int(col_part))
                        except (ValueError, IndexError):
                            # Handle cases where cell_id might not match expected format
                            continue
        else:
            aisles = []
            max_rows_per_aisle = 0
            max_cols_per_aisle = 0


        if not aisles:
            no_cells_label = QLabel("No storage cells data available.")
            no_cells_label.setStyleSheet("color: #999; font-style: italic; padding: 50px; text-align: center;")
            self.grid_layout.addWidget(no_cells_label, 0, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
            return


        # Add aisle labels as column headers (horizontal)
        for col, aisle_char in enumerate(aisles):
            aisle_label = QLabel(f"{aisle_char}") # Use the full aisle/zone name
            aisle_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 5px; color: #333;")
            aisle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(aisle_label, 0, col + 1)  # Row 0, columns 1..N

        # For 'A1-1' format, add row labels
        if '-' in sample_key:
            for row_idx in range(1, max_rows_per_aisle + 1):
                row_label = QLabel(f"Row {row_idx}")
                row_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-right: 5px; color: #333;")
                row_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.grid_layout.addWidget(row_label, row_idx, 0)  # Column 0

        # Place cells in grid
        for col_idx, aisle_char in enumerate(aisles):
            for row_idx in range(1, max_rows_per_aisle + 1):
                for c_idx in range(1, max_cols_per_aisle + 1): # Iterate through possible column numbers within a row
                    if 'Zone' in sample_key: # If using 'Zone A' format, each zone is just one "cell"
                        cell_id = aisle_char # The zone name is the cell ID
                        row_to_place = row_idx # Still use row_idx for layout, but it will be 1
                        col_to_place = col_idx + 1
                    else: # If using 'A1-1' format
                        cell_id = f"{aisle_char}{row_idx}-{c_idx}"
                        row_to_place = row_idx
                        col_to_place = col_idx + 1 # This needs to be dynamic per aisle/column in grid

                    if cell_id in self.data.storage_cells:
                        cell_data = self.data.get_cell_contents(cell_id)
                        cell_button = QPushButton(cell_id)
                        cell_button.setFixedSize(120, 100) # Larger buttons
                        cell_button.setCursor(Qt.CursorShape.PointingHandCursor)

                        # Determine color and text for cell
                        product_count = sum(cell_data['products'].values())
                        if product_count > 0:
                            bg_color = "#E6E6FF"  # Light blue/purple for occupied
                            text_color = "#232946"
                            content = f"{product_count} items"
                            cell_button.setText(f"<b>{cell_id}</b><br>{content}")
                        elif cell_data['status'].lower() == 'available':
                            bg_color = "#E8F5E8"  # Light green
                            text_color = "#232946"
                            cell_button.setText(f"<b>{cell_id}</b><br>Empty")
                        elif cell_data['status'].lower() == 'full':
                            bg_color = "#FFEBEE"  # Light red
                            text_color = "#232946"
                            cell_button.setText(f"<b>{cell_id}</b><br>Full")
                        else:
                            bg_color = "#D3DCE0"  # Default grey
                            text_color = "#232946"
                            cell_button.setText(f"<b>{cell_id}</b><br>N/A")

                        cell_button.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {bg_color};
                                border: 1px solid #CCCCCC;
                                border-radius: 10px;
                                font-size: 14px;
                                font-weight: normal;
                                color: {text_color};
                                text-align: center;
                            }}
                            QPushButton:hover {{
                                border: 2px solid #006775;
                                background-color: {self.darken_color(bg_color)};
                            }}
                            QPushButton b {{
                                font-weight: bold;
                            }}
                        """)
                        cell_button.setTextFormat(Qt.TextFormat.RichText)
                        cell_button.clicked.connect(lambda checked, cid=cell_id: self.on_cell_clicked(cid))
                        
                        # Place in grid: row index = row, column index = col+1 (since col 0 is label)
                        # This assumes a fixed grid structure. For dynamic, you might need a map (row, col) to (grid_row, grid_col)
                        self.grid_layout.addWidget(cell_button, row_to_place, col_to_place)
        # Stretch for nice layout
        self.grid_layout.setRowStretch(self.grid_layout.rowCount(), 1)
        self.grid_layout.setColumnStretch(self.grid_layout.columnCount(), 1)

    def darken_color(self, color):
        """Darkens a hexadecimal color for button hover effect."""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.9)) for c in rgb) # Slightly darken
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def on_cell_clicked(self, cell_id):
        """Show details of the clicked cell."""
        cell_data = self.data.get_cell_contents(cell_id)
        products_info = "\n".join([f"- {name} ({qty})" for pid, qty in cell_data['products'].items()
                                    for name in [self.data.products_df[self.data.products_df['ID'] == pid]['Name'].iloc[0] if not self.data.products_df[self.data.products_df['ID'] == pid].empty else f"Unknown Product ({pid})"]])
        if not products_info:
            products_info = "No products in this cell."

        QMessageBox.information(self, f"Cell Details: {cell_id}",
                                f"<b>Capacity:</b> {cell_data['capacity']}<br>"
                                f"<b>Status:</b> {cell_data['status'].capitalize()}<br>"
                                f"<b>Products:</b><br>{products_info}")

class MainWindow(QMainWindow):
    """Main application window with top navigation and modern design."""
    def __init__(self):
        super().__init__()
        self.data = WorkerData() # Initialize data management
        self.setWindowTitle("Warehouse Worker Operations Dashboard")
        self.setGeometry(100, 100, 1400, 900) # Larger default size
        self.current_user = { # User info for header
            "name": "Current Worker",
            "role": "Magasinier",
            "id": worker_id # Use the global worker_id
        }
        self.notifications = 5 # Example notification count
        self.init_ui()
        self.init_timer() # Start time update timer

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.apply_global_styles()
        self.create_header() # Custom header
        self.create_menu_bar() # Menu bar

        self.create_navbar() # Navigation buttons below header
        self.create_content_area()

        # Set initial view
        self.navigate_to_widget(self.dashboard_widget)
        self.dashboard_btn.setChecked(True)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("System Ready")

    def apply_global_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #EDF2F7; /* Light grey background for the whole window */
            }
            QLabel, QGroupBox, QTableWidget, QLineEdit, QComboBox, QPushButton, QTextEdit, QSpinBox, QListWidget {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 15px;
                color: #232946; /* Dark blue-grey text */
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #D3DCE0;
                border-radius: 10px;
                font-size: 15px;
                selection-background-color: #006775;
                selection-color: #FFFFFF;
                gridline-color: #EDF2F7;
                alternate-background-color: #F8F9FA;
            }
            QHeaderView::section {
                background-color: #006775;
                color: #FFFFFF;
                padding: 13px;
                border: none;
                font-weight: bold;
                font-size: 16px;
                text-align: left;
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px;
            }
            QTableWidget::item {
                padding: 8px;
                font-size: 15px;
            }
            QTableWidget::item:selected {
                background-color: #006775;
                color: #FFFFFF;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #EDF2F7;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #B0B0B0;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def create_header(self):
        """Creates the application header with logo, title, time, and user info, inspired by Design_Worker.py."""
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 2px solid #e9ecef;
            }
        """)

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)

        # Logo and title
        logo_layout = QHBoxLayout()
        logo_label = QLabel("�")
        logo_label.setFont(QFont("Arial", 28)) # Larger icon

        title_label = QLabel("SGE - Warehouse Worker Dashboard")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50;")

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(title_label)
        logo_layout.addStretch()

        # User information and time/notifications
        user_info_area = QHBoxLayout()

        # Time
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 11))
        self.time_label.setStyleSheet("color: #666;")

        # Notifications
        notif_btn = QPushButton(f"🔔 {self.notifications}")
        notif_btn.setFixedSize(60, 35) # Slightly larger button
        notif_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 17px; /* Make it a perfect circle/oval */
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        notif_btn.clicked.connect(self.show_notifications)

        user_name_label = QLabel(self.current_user["name"])
        user_name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        user_name_label.setStyleSheet("color: #333;")

        user_role_label = QLabel(self.current_user["role"])
        user_role_label.setFont(QFont("Arial", 10))
        user_role_label.setStyleSheet("color: #777;")

        user_text_layout = QVBoxLayout()
        user_text_layout.addWidget(user_name_label)
        user_text_layout.addWidget(user_role_label)

        user_info_area.addWidget(self.time_label)
        user_info_area.addSpacing(20)
        user_info_area.addWidget(notif_btn)
        user_info_area.addSpacing(15)
        user_info_area.addLayout(user_text_layout)

        header_layout.addLayout(logo_layout)
        header_layout.addLayout(user_info_area)

        self.main_layout.addWidget(header_widget)

    def create_menu_bar(self):
        """Creates the application menu bar."""
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #FFFFFF;
                color: #2D3748;
                font-size: 14px;
            }
            QMenuBar::item:selected {
                background-color: #EDF2F7;
            }
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #D3DCE0;
                border-radius: 5px;
                color: #2D3748;
            }
            QMenu::item {
                padding: 8px 25px;
            }
            QMenu::item:selected {
                background-color: #006775;
                color: #FFFFFF;
            }
        """)

        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = menu_bar.addMenu("Tools")
        settings_action = QAction("Settings", self)
        tools_menu.addAction(settings_action)

        help_menu = menu_bar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def init_timer(self):
        """Initializes timer for real-time clock in header."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000) # Update every second
        self.update_time() # Initial update

    def update_time(self):
        """Updates the current time displayed in the header."""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)

    def show_notifications(self):
        """Displays a notification message box."""
        QMessageBox.information(self, "Notifications",
                                f"You have {self.notifications} new notifications.")

    def show_about_dialog(self):
        """Displays the 'About' dialog."""
        QMessageBox.about(self, "About SGE",
                          "SGE - Warehouse Management System for Workers\n"
                          "Version 1.0\n"
                          "Developed by [Your Name/Organization]\n"
                          "© 2024 All rights reserved.")

    def create_navbar(self):
        self.navbar = QFrame()
        self.navbar.setFixedHeight(60) # Slightly shorter navbar
        self.navbar.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF; /* White navbar background */
                border-bottom: 1px solid #D3DCE0;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03); /* Lighter shadow */
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #4A5568; /* Medium gray text */
                padding: 10px 20px;
                font-size: 16px;
                font-weight: 500;
                border-radius: 8px; /* More rounded buttons */
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #EDF2F7; /* Light background on hover */
                color: #2D3748; /* Darker text on hover */
            }
            QPushButton:checked {
                background-color: #006775; /* Primary accent for selected */
                color: #FFFFFF;
                font-weight: bold;
                box-shadow: 0 2px 8px rgba(108, 99, 255, 0.3); /* Shadow for selected button */
            }
        """)
        navbar_layout = QHBoxLayout(self.navbar)
        navbar_layout.setContentsMargins(20, 0, 20, 0)
        navbar_layout.setSpacing(15)

        # Navigation buttons
        self.dashboard_btn = QPushButton("Dashboard")
        self.expedition_btn = QPushButton("Expedition")
        self.movement_btn = QPushButton("Movements")
        self.exceptions_btn = QPushButton("Exceptions")
        self.cells_btn = QPushButton("Cells")

        self.dashboard_btn.setCheckable(True)
        self.expedition_btn.setCheckable(True)
        self.movement_btn.setCheckable(True)
        self.exceptions_btn.setCheckable(True)
        self.cells_btn.setCheckable(True)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.dashboard_btn)
        self.button_group.addButton(self.expedition_btn)
        self.button_group.addButton(self.movement_btn)
        self.button_group.addButton(self.exceptions_btn)
        self.button_group.addButton(self.cells_btn)

        self.dashboard_btn.clicked.connect(lambda: self.navigate_to_widget(self.dashboard_widget))
        self.expedition_btn.clicked.connect(lambda: self.navigate_to_widget(self.expedition_widget))
        self.movement_btn.clicked.connect(lambda: self.navigate_to_widget(self.movement_widget))
        self.exceptions_btn.clicked.connect(lambda: self.navigate_to_widget(self.exception_widget))
        self.cells_btn.clicked.connect(lambda: self.navigate_to_widget(self.storage_cell_widget))

        navbar_layout.addStretch() # Pushes buttons to the center/right
        navbar_layout.addWidget(self.dashboard_btn)
        navbar_layout.addWidget(self.expedition_btn)
        navbar_layout.addWidget(self.movement_btn)
        navbar_layout.addWidget(self.exceptions_btn)
        navbar_layout.addWidget(self.cells_btn)
        navbar_layout.addStretch()

        self.main_layout.addWidget(self.navbar)

    def create_content_area(self):
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #EDF2F7; padding: 20px;")

        def scrollable(widget):
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(widget)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            return scroll

        self.dashboard_widget = scrollable(WorkerMainDashboard(self.data, self))
        self.expedition_widget = scrollable(ExpeditionManagementWidget(self.data))
        self.movement_widget = scrollable(ProductMovementTrackingWidget(self.data))
        self.exception_widget = scrollable(ExceptionReportsWidget(self.data))
        self.storage_cell_widget = scrollable(StorageCellWidget(self.data))

        self.content_stack.addWidget(self.dashboard_widget)
        self.content_stack.addWidget(self.expedition_widget)
        self.content_stack.addWidget(self.movement_widget)
        self.content_stack.addWidget(self.exception_widget)
        self.content_stack.addWidget(self.storage_cell_widget)

        self.main_layout.addWidget(self.content_stack)

    def navigate_to_widget(self, target_widget):
        self.content_stack.setCurrentWidget(target_widget)
        for button in self.button_group.buttons():
            button.setChecked(False)

        if target_widget == self.dashboard_widget:
            self.dashboard_btn.setChecked(True)
        elif target_widget == self.expedition_widget:
            self.expedition_btn.setChecked(True)
        elif target_widget == self.movement_widget:
            self.movement_btn.setChecked(True)
        elif target_widget == self.exception_widget:
            self.exceptions_btn.setChecked(True)
        elif target_widget == self.storage_cell_widget:
            self.cells_btn.setChecked(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set a global palette for dialogs and message boxes
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#232946"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#F8F9FA"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#232946"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#006775"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#006775"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())
