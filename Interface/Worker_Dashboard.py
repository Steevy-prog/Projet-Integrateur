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
    QFormLayout, QSplitter, QMessageBox, QGridLayout # Added QGridLayout
)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal,QPoint, QMimeData
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter, QPen, QDrag
import datetime
import random
import psycopg2
from db_connection import ConnectionDB

import json
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple
from functools import partial

Connection = ConnectionDB()
#import login as login

worker_id = 'TR0002'
global conn
print("1. online")
print("2. offline")
# it = input("Enter the number of bd you want to use : ")
it = '1'

if it == '1':
     print("You have chosen the online database.")
     conn = psycopg2.connect(
         host="dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com",
         database="projet_integrateur",
         user="group13",
         password="nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3",
         port=5432
   )
elif it == '2':
     print("You have chosen the offline database.")
     conn = psycopg2.connect(
         host="localhost",
         database="projet",
         user="postgres",
         password="postgres",
         port=5432
     )
    
elif it == '3':
     print("You have chosen the Viktor's database.")
     conn = psycopg2.connect(
         host="localhost",
         database="Projet",
         user="postgres",
         password="Lune.Hatik123",
         port=5432
     )
cur = conn.cursor()

class WorkerData:
    """Data generator and manager for warehouse worker operations"""

    def __init__(self):
        self.connection_info = Connection.connection()
        self.db_connection = self.connection_info['db_connection']
        self.generate_sample_data()
        self.initialize_storage_cells()

    def generate_sample_data(self):
        # Products data
        if not self.db_connection:
                self.connection_info = Connection.connection()
                self.db_connection = self.connection_info['db_connection']
        
        cur = self.db_connection.cursor()
        cur.execute("SELECT (p).* FROM \"EMIR\".Produit_EVA() AS p;")
        products = cur.fetchall()
        if len(products) == 0:
            # Handle case where no products are loaded, e.g., create dummy data or log
            print("No products loaded from the database. Generating dummy product data.")
            self.products_df = pd.DataFrame(
                [
                    ('P001', 'SupplierA', 'Dummy Product 1', 'Desc 1', 10.0, 'BrandX', 'ModelA', 'Electronics'),
                    ('P002', 'SupplierB', 'Dummy Product 2', 'Desc 2', 20.0, 'BrandY', 'ModelB', 'Furniture')
                ],
                columns=['ID', 'Fourniseur', 'Name', 'Description', 'Prix Unitaire', 'Brand', 'Model', 'Category']
            )
        else:
            self.products_df = pd.DataFrame(products, columns=['ID', 'Fourniseur', 'Name', 'Description', 'Prix Unitaire','idModel', 'Category'])

        # Expedition Tasks data
        task_statuses = ['Pending', 'In Progress', 'Completed', 'Cancelled']
        task_priorities = ['Low', 'Medium', 'High']
        expedition_tasks_data = []
        cur.execute("SELECT (p).* FROM \"EMIR\".Tache_EVA(%s) AS p;", (worker_id,))
        tasks = cur.fetchall()
        self.expedition_tasks = pd.DataFrame(tasks,columns=['Task_id','Cell','Colis','date-cre','date-ech','duree','description','priority','status','type'])
        for i in self.expedition_tasks.itertuples():
            expedition_tasks_data.append({
                'Task_id': i[0],
                'Product_ID': i[2],
                'Cell': i[1],
                'Date-Creation': i[3],
                'Date-Echeance': i[4],
                'Duree': i[5],
                'Description': i[6],
                'Status': i[8],
                'Priority': i[7],
                'Type': i[9]
            })


        # Product Movement History
        movement_types = ['Pick', 'Pack', 'Move', 'Count']
        # locations = ['A1-15', 'B2-08', 'A2-22', 'C1-05', 'A1-33', 'A2-18', 'B3-01', 'A1-10', 'A1-07', 'A2-05', 'D1-01', 'Loading Dock', 'Shipping']
        movement_history_data = []
        #for i in range(1, 51):
        #    product = self.products_df.sample(1).iloc[0]
        #    movement_type = random.choice(movement_types)
        #    quantity = random.randint(1, product['Stock'] // 2 if product['Stock'] > 1 else 1)
        #    from_loc = random.choice(self.products['Location'].unique().tolist() + ['Loading Dock'])
        #    to_loc = random.choice(self.products['Location'].unique().tolist() + ['Shipping'])
        #    timestamp = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(1, 1440))
        #    worker = random.choice(['Current Worker', 'Worker A', 'Worker B'])
        #    movement_history_data.append({
        #        'Movement_ID': f"MOV{i:05d}",
        #        'Product_ID': product['Product_ID'],
        #        'Product_Name': product['Product_Name'],
        #        'Movement_Type': movement_type,
        #        'Quantity': quantity,
        #        'From_Location': from_loc,
        #        'To_Location': to_loc,
        #        'Timestamp': timestamp,
        #        'Worker': worker
        #    })
        #self.movement_history = pd.DataFrame(movement_history_data)

        # Exceptions
        #exception_types = ['Damaged Product', 'Missing Item', 'Location Error', 'Quantity Mismatch', 'System Error']
        #exception_statuses = ['Open', 'In Review', 'Resolved']
        #exceptions_data = []
        #for i in range(1, 11):
        #    product = self.products_df.sample(1).iloc[0]
        #    exception_type = random.choice(exception_types)
        #    reported_time = datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 72))
        #    status = random.choice(exception_statuses)
        #    reported_by = random.choice(['Current Worker', 'Supervisor X', 'Worker B'])
        #    description = f"Detailed description for {exception_type} concerning {product['Product_Name']}."
        #    exceptions_data.append({
        #        'ID': f"EXC{i:03d}",
        #        'Type': exception_type,
        #        'Product_ID': product['Product_ID'],
        #        'Product_Name': product['Product_Name'],
        #        'Location': product['Location'],
        #        'Reported_Time': reported_time,
        #        'Status': status,
        #        'Reported_By': reported_by,
        #        'Description': description
        #    })
        #self.exceptions = pd.DataFrame(exceptions_data)

    def initialize_storage_cells(self):
        if not self.db_connection:
                self.connection_info = Connection.connection()
                self.db_connection = self.connection_info['db_connection']

        cur = self.db_connection.cursor()
        # Create a dictionary to hold the state of each storage cell
        # For a more robust system, this would be loaded from a database or config
        self.storage_cells = {}
        warehouse_layout = {
            'A': 3, 'B': 3, 'C': 2, 'D': 2 # Rows and columns for each aisle
        }
        cell_counter = 1
        for aisle, num_cols in warehouse_layout.items():
            for row in range(1, 4): # Example: 3 rows per aisle
                for col in range(1, num_cols + 1):
                    cell_id = f"{aisle}{row}-{col}"
                    self.storage_cells[cell_id] = {
                        'products': {}, # Dictionary of {product_id: quantity}
                        'capacity': random.randint(50, 200), # Example capacity
                        'status': 'Available' # e.g., Available, Full, Restricted
                    }
                    cell_counter += 1

        # Distribute some products into cells initially for demonstration
        for _, product in self.products_df.iterrows():
            cur.execute('SELECT "EMIR".findzone(%s);', (product['ID'],))
            zone = cur.fetchone()[0]
            cur.execute('SELECT "EMIR".quantityproduct(%s);', (product['ID'],))
            quantity = cur.fetchone()[0]
            product_id = product['ID']
            product_name = product['Name']
            stock = quantity
            if stock is None:
                stock = 0
            initial_location = zone

            if initial_location in self.storage_cells:
                # Add product to its initial specified location
                self.storage_cells[initial_location]['products'][product_id] = self.storage_cells[initial_location]['products'].get(product_id, 0) + stock
                self.storage_cells[initial_location]['status'] = 'Occupied'
            else:
                # If product's location isn't a defined cell, find a random available cell
                available_cells = [cid for cid, data in self.storage_cells.items() if data['status'] == 'Available']
                if available_cells:
                    target_cell_id = random.choice(available_cells)
                    self.storage_cells[target_cell_id]['products'][product_id] = self.storage_cells[target_cell_id]['products'].get(product_id, 0) + stock
                    self.storage_cells[target_cell_id]['status'] = 'Occupied'

    def get_cell_contents(self, cell_id):
        return self.storage_cells.get(cell_id, {'products': {}, 'capacity': 0, 'status': 'Unknown'})

    def move_product_between_cells(self, product_id, quantity, from_cell_id, to_cell_id):
        # Basic validation and movement logic
        if from_cell_id not in self.storage_cells or to_cell_id not in self.storage_cells:
            return False, "Invalid source or destination cell."

        from_cell = self.storage_cells[from_cell_id]
        to_cell = self.storage_cells[to_cell_id]

        if product_id not in from_cell['products'] or from_cell['products'][product_id] < quantity:
            return False, "Not enough product in source cell."

        # Simulate capacity check (simplified)
        # In a real system, you'd check volume/weight vs. remaining capacity
        current_to_cell_fill = sum(to_cell['products'].values())
        if (current_to_cell_fill + quantity) > to_cell['capacity']:
            return False, "Destination cell does not have enough capacity."

        # Perform the move
        from_cell['products'][product_id] -= quantity
        if from_cell['products'][product_id] == 0:
            del from_cell['products'][product_id]
            if not from_cell['products']:
                from_cell['status'] = 'Available'

        to_cell['products'][product_id] = to_cell['products'].get(product_id, 0) + quantity
        to_cell['status'] = 'Occupied'

        # Log this as a movement in movement_history
        product_name = self.products_df[self.products_df['Product_ID'] == product_id]['Product_Name'].iloc[0] if product_id in self.products_df['Product_ID'].values else "Unknown Product"
        self.add_movement(product_id, product_name, "Move", quantity, from_cell_id, to_cell_id)

        return True, "Product moved successfully."


    def add_movement(self, product_id, product_name, movement_type, quantity, from_location, to_location):
        new_id = f"MOV{len(self.movement_history) + 1:05d}"
        new_movement = {
            'Movement_ID': new_id,
            'Product_ID': product_id,
            'Product_Name': product_name,
            'Movement_Type': movement_type,
            'Quantity': quantity,
            'From_Location': from_location,
            'To_Location': to_location,
            'Timestamp': datetime.datetime.now(),
            'Worker': 'Current Worker' # Assuming a logged-in user
        }
        # Append as a new row to the DataFrame
        self.movement_history = pd.concat([self.movement_history, pd.DataFrame([new_movement])], ignore_index=True)
        print(f"Added new movement: {new_movement}")

    def add_exception(self, exception_type, product_id, product_name, location, description):
        new_id = f"EXC{len(self.exceptions) + 1:03d}"
        new_exception = {
            'ID': new_id,
            'Type': exception_type,
            'Product_ID': product_id,
            'Product_Name': product_name,
            'Location': location,
            'Reported_Time': datetime.datetime.now(),
            'Status': 'Open',
            'Reported_By': 'Current Worker', # Assuming a logged-in user
            'Description': description
        }
        self.exceptions = pd.concat([self.exceptions, pd.DataFrame([new_exception])], ignore_index=True)
        print(f"Added new exception: {new_exception}")



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

        color = self.get_priority_color(self.task_data.get('Priority', 'Low')) # Handle missing priority

        # Modern card style
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
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
        accent_bar.setStyleSheet(f"background-color: {color}; border-top-left-radius: 12px; border-bottom-left-radius: 12px;")
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
        order_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #333333;")
        header_row.addWidget(order_label)
        header_row.addStretch()

        if self.card_type == "expedition":
            priority_label = QLabel(self.task_data['priority'])
            priority_label.setStyleSheet(f"background-color: {color}; color: #FFFFFF; border-radius: 8px; font-size: 11px; font-weight: bold; padding: 4px 10px;")
            header_row.addWidget(priority_label)
            info_layout.addLayout(header_row)

        # Details row
        details_text = f"<b>Product:</b> {self.task_data['Colis']}<br><b>Items Count:</b> {self.task_data.get('items_count', 0)}"
        details_label = QLabel(details_text)
        details_label.setStyleSheet("font-size: 13px; color: #666666;")
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
                background-color: #6C63FF;
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
                background-color: #5247D6;
            }
        """)
        action_btn.clicked.connect(self.on_action_clicked)

        content_layout.addLayout(info_layout, stretch=3)
        content_layout.addWidget(action_btn, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def get_priority_color(self, priority):
        colors = {
            'High': '#F44336', # Red
            'Medium': '#FF9800', # Orange
            'Low': '#4CAF50' # Green
        }
        return colors.get(priority, '#666666') # Default color

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
                border-bottom: 1px solid #E0E0E0;
            }
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #5247D6;
            }
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                min-height: 150px;
                color: #333333;
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
        # Simulated product name list

        product_names = ["Box", "Tape", "Scissors"]
        form_layout.addRow("Product(s):", QLabel(", ".join(product_names)))
        form_layout.addRow("Items Count:", QLabel(str(0)))
        form_layout.addRow("Estimated Time (min):", QLabel(str(self.task_data['duree'])))

        status_label = QLabel(self.task_data['status'])
        status_label.setStyleSheet("color: #000000; font-weight: bold;")
        form_layout.addRow("Status:", status_label)

        form_layout.addRow("Priority:", QLabel(self.task_data['priority']))
        form_layout.addRow("Due Time:", QLabel(str(self.task_data['date-ech'])))
        layout.addLayout(form_layout)

        # Items list
        items_list_label = QLabel("Items to Pick/Pack:")
        layout.addWidget(items_list_label)
        items_list = QListWidget()
        items_list.addItem("- Check quality")
        items_list.addItem("- Scan barcode")
        layout.addWidget(items_list)

        # Buttons
        button_layout = QHBoxLayout()

        complete_button = QPushButton("Mark as Completed")
        complete_button.setStyleSheet("background-color: #4CAF50; color: white;")
        button_layout.addWidget(complete_button)

        cancel_button = QPushButton("Cancel Task")
        cancel_button.setStyleSheet("background-color: #F44336; color: white;")
        button_layout.addWidget(cancel_button)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #999999; color: white;")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

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
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            }
            QLabel {
                font-size: 15px;
                color: #333333;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 1px solid #00BFA5; /* Teal focus color */
            }
            QPushButton {
                background-color: #00BFA5; /* Teal for primary action */
                color: white;
                border: none;
                padding: 12px 25px;
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
        self.product_combo.addItems(self.data.products_df['Product_Name'].tolist())
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
        product_id = self.data.products[self.data.products['Product_Name'] == product_name]['Product_ID'].values
        if not product_id.size > 0:
            QMessageBox.warning(self, "Invalid Product", "Please select a valid product from the list.")
            return

        movement_type = self.movement_type_combo.currentText()
        quantity = self.quantity_spin.value()
        from_location = self.from_location_input.text()
        to_location = self.to_location_input.text()

        if not all([product_name, movement_type, quantity, from_location, to_location]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        self.data.add_movement(product_id[0], product_name, movement_type, quantity, from_location, to_location)
        QMessageBox.information(self, "Success", "Movement recorded successfully!")
        self.accept()

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
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            }
            QLabel {
                font-size: 15px;
                color: #333333;
            }
            QLabel.title {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #E0E0E0;
            }
            QTextEdit, QComboBox {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }
            QTextEdit:focus, QComboBox:focus {
                border: 1px solid #F44336; /* Red focus color */
            }
            QPushButton {
                background-color: #F44336; /* Red for primary action */
                color: white;
                border: none;
                padding: 12px 25px;
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
            exception_index = self.exception_data.name # Get the index of the current exception in the DataFrame
            # Find the actual dataframe row by index
            if exception_index in self.parent().data.exceptions.index:
                self.parent().data.exceptions.loc[exception_index, 'Status'] = new_status
                QMessageBox.information(self, "Status Updated", f"Exception {self.exception_data['ID']} status updated to {new_status}.")
                self.accept() # Close dialog and signal acceptance
            else:
                QMessageBox.warning(self, "Error", "Could not find exception in data to update.")
        else:
            self.accept() # No change, just close

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
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            }
            QLabel {
                font-size: 15px;
                color: #333333;
            }
            QLineEdit, QComboBox, QTextEdit {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #F44336; /* Red focus color */
            }
            QPushButton {
                background-color: #F44336; /* Red for primary action */
                color: white;
                border: none;
                padding: 12px 25px;
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
        self.product_combo.addItems(self.data.products['Product_Name'].tolist())
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
        product_id = self.data.products[self.data.products['Product_Name'] == product_name]['Product_ID'].values
        if not product_id.size > 0:
            QMessageBox.warning(self, "Invalid Product", "Please select a valid product from the list.")
            return
        location = self.location_input.text()
        description = self.description_text.toPlainText()

        if not all([exception_type, product_name, location, description]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        self.data.add_exception(exception_type, product_id[0], product_name, location, description)
        QMessageBox.information(self, "Success", "Exception reported successfully!")
        self.accept()

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

        # Hero Section
        hero_frame = QFrame()
        hero_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6C63FF, stop:1 #00BFA5); /* Gradient background */
                border-radius: 15px;
                padding: 30px;
                color: #FFFFFF;
                box-shadow: 0 8px 30px rgba(108, 99, 255, 0.3);
            }
            QLabel {
                color: #FFFFFF;
            }
        """)
        hero_layout = QVBoxLayout(hero_frame)

        welcome_label = QLabel(f"Welcome Back, Current Worker!")
        welcome_label.setStyleSheet("font-size: 32px; font-weight: bold;")

        time_label = QLabel(f"Today: {datetime.datetime.now().strftime('%A, %B %d, %Y')}")
        time_label.setStyleSheet("font-size: 16px; margin-top: 5px;")

        hero_layout.addWidget(welcome_label)
        hero_layout.addWidget(time_label)
        hero_layout.addStretch() # Push content to top

        # Dashboard Stat Cards (within hero section or below)
        dashboard_stats_layout = QHBoxLayout()
        dashboard_stats_layout.setSpacing(20)

        my_pending_tasks = len([t for t in self.data.expedition_tasks.to_dict('records') if  t['status'] == 'en cours'])
        completed_today = len([t for t in self.data.expedition_tasks.to_dict('records') if  t['status'] == 'Completed']) # Check if completed today
        #my_movements = len([m for m in self.data.movement_history.to_dict('records') if m['Worker'] == 'Current Worker'])
        #open_exceptions = len([e for e in self.data.exceptions.to_dict('records') if e['Status'] == 'Open'])

        dashboard_stats_layout.addWidget(self.create_dashboard_card("My Pending Tasks", my_pending_tasks, "#FFC107", "Tasks assigned to me"))
        dashboard_stats_layout.addWidget(self.create_dashboard_card("Completed Today", completed_today, "#4CAF50", "Tasks finished today"))
        #dashboard_stats_layout.addWidget(self.create_dashboard_card("My Movements", my_movements, "#6C63FF", "Product movements logged"))
        #dashboard_stats_layout.addWidget(self.create_dashboard_card("Open Exceptions", open_exceptions, "#F44336", "Issues requiring attention"))

        hero_layout.addLayout(dashboard_stats_layout)
        layout.addWidget(hero_frame)


        # Quick Actions
        quick_actions_group = QGroupBox("Quick Actions")
        quick_actions_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                margin-top: 20px;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding-top: 15px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                margin-left: 10px;
                color: #6C63FF; /* Accent color for title */
            }
        """)
        quick_actions_layout = QHBoxLayout()
        quick_actions_layout.setSpacing(15)
        quick_actions_layout.setContentsMargins(20, 25, 20, 20)

        button_style = """
            QPushButton {
                background-color: #F0F2F5; /* Light background */
                border: none;
                border-radius: 10px;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: 600;
                color: #333333;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #6C63FF; /* Primary accent on hover */
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
        #report_exception_btn.clicked.connect(lambda: self.main_window.navigate_to_widget(self.main_window.exception_widget))

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
                color: #333333;
                margin-top: 20px;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding-top: 15px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                margin-left: 10px;
                color: #6C63FF; /* Secondary accent for title */
            }
        """)
        recent_activity_layout = QVBoxLayout()
        recent_activity_layout.setContentsMargins(20, 25, 20, 20)
        recent_activity_layout.setSpacing(10)

        #latest_movements = sorted(self.data.movement_history.to_dict('records'), key=lambda x: x['Timestamp'], reverse=True)[:5]
        #if latest_movements:
        #    for movement in latest_movements:
        #        activity_label = QLabel(f"<span style='font-weight:bold;'>{movement['Timestamp'].strftime('%H:%M')}</span> | {movement['Movement_Type']} of <span style='font-weight:bold;'>{movement['Quantity']}x</span> {movement['Product_Name']} by {movement['Worker']}")
        #        activity_label.setStyleSheet("font-size: 14px; color: #444; padding: 2px 0;")
        #        activity_label.setTextFormat(Qt.TextFormat.RichText)
        #        recent_activity_layout.addWidget(activity_label)
        no_activity_label = QLabel("No recent activities to display.")
        no_activity_label.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
        recent_activity_layout.addWidget(no_activity_label)

        recent_activity_group.setLayout(recent_activity_layout)
        layout.addWidget(recent_activity_group)
        layout.addStretch()

        self.setLayout(layout)

    def create_dashboard_card(self, title, value, color, description):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setFrameShadow(QFrame.Shadow.Raised)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666666; font-weight: bold;")

        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")

        description_label = QLabel(description)
        description_label.setStyleSheet("font-size: 12px; color: #999999;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(description_label)
        layout.addStretch() # Pushes content to top

        card.setLayout(layout)
        return card

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
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #333333;")

        refresh_btn = QPushButton("Refresh Tasks")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C63FF;
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
                background-color: #5247D6;
                transform: translateY(-2px);
            }
        """)
        # refresh_btn.clicked.connect(self.refresh_tasks) # Implement refresh logic if needed

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)

        # Quick stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        pending_tasks = len([t for t in self.data.expedition_tasks.to_dict('records') if t['status'] == 'en cours'])
        in_progress_tasks = len([t for t in self.data.expedition_tasks.to_dict('records') if t['status'] == 'Progress'])
        completed_today = len([t for t in self.data.expedition_tasks.to_dict('records') if t['status'] == 'Completed']) # Example of checking "today"

        stats_layout.addWidget(self.create_stat_card("Pending Tasks", pending_tasks, "#FFC107"))
        stats_layout.addWidget(self.create_stat_card("In Progress", in_progress_tasks, "#6C63FF"))
        stats_layout.addWidget(self.create_stat_card("Completed Today", completed_today, "#4CAF50"))
        layout.addLayout(stats_layout)

        # Task sections using QSplitter for adjustable layout
        sections_splitter = QSplitter(Qt.Orientation.Horizontal)
        sections_splitter.setHandleWidth(10)
        sections_splitter.setStyleSheet("QSplitter::handle { background-color: #E0E0E0; border-radius: 5px; }")

        # My Current Tasks
        my_tasks_section = self.create_task_section("My Current Tasks",
            [t for t in self.data.expedition_tasks.to_dict('records') if  t['status'] != 'Completed'])
        sections_splitter.addWidget(my_tasks_section)

        # High Priority Tasks
        high_priority_section = self.create_task_section("High Priority Tasks",
            [t for t in self.data.expedition_tasks.to_dict('records') if t['priority'] == 'high' and t['status'] != 'Completed'])
        sections_splitter.addWidget(high_priority_section)

        sections_splitter.setSizes([self.width() // 2, self.width() // 2]) # Initial sizes
        layout.addWidget(sections_splitter)

        self.setLayout(layout)

    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setFrameShadow(QFrame.Shadow.Raised)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 18px 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666666; font-weight: bold;")

        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)

        return card

    def create_task_section(self, title, tasks):
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #E0E0E0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333; margin-bottom: 5px;")
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
                cur = self.data.db_connection.cursor()
                cur.execute('SELECT (p).* FROM "EMIR".getlots(%s) AS p;', (task['Colis'],))
                items_count = cur.fetchall()
                task['items_count'] = len(items_count)

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
        dialog.exec()

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
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #333333;")

        new_movement_btn = QPushButton("Record Movement")
        new_movement_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C63FF; /* Teal */
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
                border: 1px solid #6C63FF;
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
                width: 12px;
                height: 12px;
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

        # Set default row height
        table.verticalHeader().setDefaultSectionSize(40) # Adjust row height

        # Table styling
        table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                font-size: 14px;
                selection-background-color: #E6E6FF; /* Light purple selection */
                selection-color: #333333;
                gridline-color: #F0F2F5; /* Lighter grid lines */
            }
            QHeaderView::section {
                background-color: #6C63FF; /* Primary accent for header */
                color: #FFFFFF;
                padding: 12px;
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
                background-color: #E6E6FF;
                color: #333333;
            }
        """)

        self.movements_table = table  # <-- Assign before update
        #self.update_movements_table(self.data.movement_history.to_dict('records'))

        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True) # Make last column stretch
        table.verticalHeader().setVisible(False) # Hide vertical header (row numbers)
        table.resizeColumnsToContents()

        return table
    def filter_movements(self):
        search_text = self.search_input.text().lower()
        movement_type = self.type_combo.currentText()

        filtered_movements = []
        #for movement in self.data.movement_history.to_dict('records'):
        #    if search_text and search_text not in movement['Product_Name'].lower() and search_text not in movement['Product_ID'].lower():
        #        continue
        #    if movement_type != 'All' and movement['Movement_Type'] != movement_type:
        #        continue
        #    filtered_movements.append(movement)

        self.update_movements_table(filtered_movements)

    def update_movements_table(self, movements):
        sorted_movements = sorted(movements, key=lambda x: x['Timestamp'], reverse=True)
        self.movements_table.setRowCount(len(sorted_movements))

        # Use a single accent color for all movement types
        accent_color = "#2921C5"  # Your primary accent color

        for i, movement in enumerate(sorted_movements):
            self.movements_table.setItem(i, 0, QTableWidgetItem(movement['Timestamp'].strftime('%H:%M %b %d')))
            self.movements_table.setItem(i, 1, QTableWidgetItem(movement['Product_Name']))

            # Uniform color for all movement types
            type_item = QTableWidgetItem(movement['Movement_Type'])
            type_item.setBackground(QColor(accent_color))
            type_item.setForeground(QColor('#FFFFFF'))  # Always white text for contrast
            self.movements_table.setItem(i, 2, type_item)

            self.movements_table.setItem(i, 3, QTableWidgetItem(str(movement['Quantity'])))
            self.movements_table.setItem(i, 4, QTableWidgetItem(movement['From_Location']))
            self.movements_table.setItem(i, 5, QTableWidgetItem(movement['To_Location']))

            worker_item = QTableWidgetItem(movement['Worker'])
            if movement['Worker'] == 'Current Worker':
                worker_item.setBackground(QColor('#E8F5E8'))  # Light green highlight
                worker_item.setForeground(QColor('#333333'))
            self.movements_table.setItem(i, 6, worker_item)
    def record_new_movement(self):
        dialog = NewMovementDialog(self.data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update_movements_table(self.data.movement_history.to_dict('records')) # Refresh table after new entry
            # Re-apply filters after update if necessary (optional)
            self.filter_movements()

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
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #333333;")

        report_exception_btn = QPushButton("Report Exception")
        report_exception_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336; /* Red */
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
        #report_exception_btn.clicked.connect(self.report_new_exception)

        header_layout.addWidget(title)
        header_layout.addStretch()
        #header_layout.addWidget(report_exception_btn)
        layout.addLayout(header_layout)

        # Exception stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        #open_exceptions = len([e for e in self.data.exceptions.to_dict('records') if e['Status'] == 'Open'])
        #in_review = len([e for e in self.data.exceptions.to_dict('records') if e['Status'] == 'In Review'])
        #resolved_today = len([e for e in self.data.exceptions.to_dict('records') if e['Status'] == 'Resolved' and (datetime.datetime.now() - e['Reported_Time']).total_seconds() < 86400])

        #stats_layout.addWidget(self.create_exception_stat_card("Open Reports", open_exceptions, "#F44336"))
        #stats_layout.addWidget(self.create_exception_stat_card("In Review", in_review, "#FFC107"))
        #stats_layout.addWidget(self.create_exception_stat_card("Resolved Today", resolved_today, "#4CAF50"))
        layout.addLayout(stats_layout)

        # Exceptions table
        self.exceptions_table = self.create_exceptions_table()
        layout.addWidget(self.exceptions_table)

        self.setLayout(layout)

    def create_exception_stat_card(self, title, value, color):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setFrameShadow(QFrame.Shadow.Raised)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 18px 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666666; font-weight: bold;")

        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)

        return card

    def create_exceptions_table(self):
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(['ID', 'Type', 'Product', 'Location', 'Time', 'Status'])

        table.verticalHeader().setDefaultSectionSize(40)

        table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                font-size: 14px;
                selection-background-color: #FFEBEE; /* Light red selection */
                selection-color: #333333;
                gridline-color: #F0F2F5;
            }
            QHeaderView::section {
                background-color:#6C63FF; /* Red for header */
                color: #FFFFFF;
                padding: 12px;
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
                background-color: #6C63FF;
                color: #333333;
            }
        """)

        self.exceptions_table = table  # <-- Assign before update
        #self.update_exceptions_table(self.data.exceptions.to_dict('records'))

        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.resizeColumnsToContents()
        #table.cellDoubleClicked.connect(self.view_exception_details)

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
                'Open': '#F44336', # Red
                'In Review': '#FFC107', # Amber
                'Resolved': '#4CAF50' # Green
            }
            status_item.setBackground(QColor(status_colors.get(exception['Status'], '#E0E0E0')))
            status_item.setForeground(QColor('#FFFFFF')) # White text for better contrast
            if exception['Status'] == 'In Review':
                status_item.setForeground(QColor('#333333')) # Darker text for Amber background
            self.exceptions_table.setItem(i, 5, status_item)

    #def view_exception_details(self, row, column):
    #    exception_id = self.exceptions_table.item(row, 0).text()
    #    # Find the full exception data from the original DataFrame using the ID
    #    exception_data = self.data.exceptions[self.data.exceptions['ID'] == exception_id].iloc[0]

    #    if exception_data is not None:
    #        dialog = ExceptionDetailDialog(exception_data, self)
    #        if dialog.exec() == QDialog.DialogCode.Accepted:
    #            self.update_exceptions_table(self.data.exceptions.to_dict('records')) # Refresh table if status changed

    #def report_new_exception(self):
    #    dialog = NewExceptionDialog(self.data, self)
    #    if dialog.exec() == QDialog.DialogCode.Accepted:
    #        self.update_exceptions_table(self.data.exceptions.to_dict('records')) # Refresh table after new entry

class CellDetailDialog(QDialog):
    """Dialog to display details of a selected storage cell."""
    def __init__(self, cell_id, cell_data, parent=None):
        super().__init__(parent)
        self.cell_id = cell_id
        self.cell_data = cell_data
        self.setWindowTitle(f"Cell Details: {cell_id}")
        self.setFixedSize(450, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border-radius: 15px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            }
            QLabel {
                font-size: 15px;
                color: #333333;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #232946;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #E0E0E0;
            }
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                min-height: 100px;
                color: #333333;
            }
            QListWidget::item {
                padding: 5px;
            }
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #5247D6;
            }
        """)

        title_label = QLabel(f"Cell: {self.cell_id}")
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.addRow("Status:", QLabel(self.cell_data['status']))
        form_layout.addRow("Capacity:", QLabel(f"{self.cell_data['capacity']} units"))

        current_fill = sum(self.cell_data['products'].values())
        utilization_percent = (current_fill / self.cell_data['capacity']) * 100 if self.cell_data['capacity'] > 0 else 0
        form_layout.addRow("Current Fill:", QLabel(f"{current_fill} units ({utilization_percent:.1f}%)"))
        layout.addLayout(form_layout)

        products_label = QLabel("Products in Cell:")
        layout.addWidget(products_label)

        products_list_widget = QListWidget()
        if self.cell_data['products']:
            # Assuming self.parent().data.products_df is accessible for product names
            # Need to ensure parent is StorageCellWidget, which has a 'data' attribute
            worker_data = self.parent().data # Access worker_data from parent StorageCellWidget
            for prod_id, quantity in self.cell_data['products'].items():
                product_info = worker_data.products_df[worker_data.products_df['ID'] == prod_id]
                product_name = product_info['Name'].iloc[0] if not product_info.empty else f"Unknown Product ({prod_id})"
                products_list_widget.addItem(f"{product_name}: {quantity} units")
        else:
            products_list_widget.addItem("No products in this cell.")
        layout.addWidget(products_list_widget)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

class CellDetailDialog(QDialog):
    """Dialog to display details of a selected storage cell."""
    def __init__(self, cell_id, cell_data, worker_data_instance, parent=None): # Added worker_data_instance
        super().__init__(parent)
        self.cell_id = cell_id
        self.cell_data = cell_data
        self.worker_data = worker_data_instance # Store the WorkerData instance
        self.setWindowTitle(f"Cell Details: {cell_id}")
        self.setFixedSize(450, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border-radius: 15px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            }
            QLabel {
                font-size: 15px;
                color: #333333;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #232946;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #E0E0E0;
            }
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                min-height: 100px;
                color: #333333;
            }
            QListWidget::item {
                padding: 5px;
            }
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #5247D6;
            }
        """)

        title_label = QLabel(f"Cell: {self.cell_id}")
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.addRow("Status:", QLabel(self.cell_data['status']))
        form_layout.addRow("Capacity:", QLabel(f"{self.cell_data['capacity']} units"))

        current_fill = sum(self.cell_data['products'].values())
        utilization_percent = (current_fill / self.cell_data['capacity']) * 100 if self.cell_data['capacity'] > 0 else 0
        form_layout.addRow("Current Fill:", QLabel(f"{current_fill} units ({utilization_percent:.1f}%)"))
        layout.addLayout(form_layout)

        products_label = QLabel("Products in Cell:")
        layout.addWidget(products_label)

        products_list_widget = QListWidget()
        if self.cell_data['products']:
            for prod_id, quantity in self.cell_data['products'].items():
                # Use the passed worker_data_instance to get product names
                product_info = self.worker_data.products_df[self.worker_data.products_df['ID'] == prod_id]
                product_name = product_info['Name'].iloc[0] if not product_info.empty else f"Unknown Product ({prod_id})"
                products_list_widget.addItem(f"{product_name}: {quantity} units")
        else:
            products_list_widget.addItem("No products in this cell.")
        layout.addWidget(products_list_widget)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

class MoveProductDialog(QDialog):
    """Dialog to move products between storage cells."""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data # WorkerData instance
        self.setWindowTitle("Move Product Between Cells")
        self.setFixedSize(500, 450)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border-radius: 15px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            }
            QLabel {
                font-size: 15px;
                color: #333333;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 1px solid #00BFA5;
            }
            QPushButton {
                background-color: #00BFA5;
                color: white;
                border: none;
                padding: 12px 25px;
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
        # Populate with all products from WorkerData
        self.product_combo.addItems(self.data.products_df['Name'].tolist())
        self.product_combo.setEditable(True)
        self.product_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.product_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        form_layout.addRow("Product:", self.product_combo)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000)
        form_layout.addRow("Quantity:", self.quantity_spin)

        self.from_cell_combo = QComboBox()
        self.to_cell_combo = QComboBox()
        # Populate with all storage cell IDs
        all_cell_ids = sorted(list(self.data.storage_cells.keys()))
        self.from_cell_combo.addItems(all_cell_ids)
        self.to_cell_combo.addItems(all_cell_ids)
        form_layout.addRow("From Cell:", self.from_cell_combo)
        form_layout.addRow("To Cell:", self.to_cell_combo)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        move_button = QPushButton("Move Product")
        move_button.clicked.connect(self.perform_move)
        button_layout.addWidget(move_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("background-color: #CCCCCC;")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def perform_move(self):
        product_name = self.product_combo.currentText()
        # Get product ID from name
        product_info = self.data.products_df[self.data.products_df['Name'] == product_name]
        if product_info.empty:
            QMessageBox.warning(self, "Input Error", "Please select a valid product.")
            return
        product_id = product_info['ID'].iloc[0]

        quantity = self.quantity_spin.value()
        from_cell_id = self.from_cell_combo.currentText()
        to_cell_id = self.to_cell_combo.currentText()

        if not all([product_id, quantity, from_cell_id, to_cell_id]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        success, message = self.data.move_product_between_cells(product_id, quantity, from_cell_id, to_cell_id)

        if success:
            QMessageBox.information(self, "Success", message)
            self.accept() # Close dialog on success
        else:
            QMessageBox.warning(self, "Move Failed", message)
            



class CellStatus(Enum):
    """Enum for cell status types"""
    EMPTY = "empty"
    LOW_FILL = "low_fill"
    MEDIUM_FILL = "medium_fill"
    HIGH_FILL = "high_fill"
    CRITICAL_FILL = "critical_fill"


class DragDropStorageCellButton(QPushButton):
    """Storage cell button with drag and drop capabilities"""

    # Custom signals for drag and drop operations
    product_dropped = pyqtSignal(str, str, str, int)  # from_cell, to_cell, product_id, quantity
    cell_hovered = pyqtSignal(str, bool)  # cell_id, is_hovered

    def __init__(self, cell_id: str, cell_data: Dict, parent=None):
        super().__init__(parent)
        self.cell_id = cell_id
        self.cell_data = cell_data
        self.parent_widget = parent # This will be the DragDropStorageWidget
        self.drag_start_position = QPoint()
        self.is_drop_target = False
        self.is_dragging = False

        # Enable drag and drop
        self.setAcceptDrops(True)
        self.setMouseTracking(True)

        self._setup_cell()

    def _setup_cell(self):
        """Setup cell appearance and behavior"""
        self.setFixedSize(140, 110)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        #self.setTextFormat(Qt.TextFormat.RichText) # THIS LINE IS CRUCIAL FOR HTML RENDERING

        # Calculate utilization
        current_fill = sum(self.cell_data['products'].values())
        utilization_percent = (current_fill / self.cell_data['capacity']) * 100 if self.cell_data['capacity'] > 0 else 0

        # Set cell content and styling
        self._update_cell_display(utilization_percent)
        self._set_cell_styling(utilization_percent)

    def _update_cell_display(self, utilization_percent: float):
        """Update cell display text and tooltip"""
        current_fill = sum(self.cell_data['products'].values())

        if current_fill > 0:
            # Create product summary
            product_lines = []
            # Access parent_widget.data (which is WorkerData) to get product names
            worker_data = self.parent_widget.data
            for prod_id, qty in list(self.cell_data['products'].items())[:2]:
                product_info = worker_data.products_df[worker_data.products_df['ID'] == prod_id]
                product_name = product_info['Name'].iloc[0] if not product_info.empty else f"Unknown ({prod_id})"
                product_lines.append(f"{qty}x {product_name}")

            if len(self.cell_data['products']) > 2:
                product_lines.append(f"...+{len(self.cell_data['products']) - 2} more")

            display_text = f"{self.cell_id}\n{'\n'.join(product_lines)}\n{utilization_percent:.0f}% filled"

            # Detailed tooltip with drag instructions
            tooltip_lines = [
                f"<b>{self.cell_id}</b>",
                f"Capacity: {self.cell_data['capacity']}",
                f"Current fill: {current_fill}",
                "",
                "<b>🖱️ Drag & Drop:</b>",
                "• Right-click to select products to move",
                "• Drag to another cell to move products",
                "• Left-click for detailed view",
                ""
            ]
            for prod_id, qty in self.cell_data['products'].items():
                product_info = worker_data.products_df[worker_data.products_df['ID'] == prod_id]
                product_name = product_info['Name'].iloc[0] if not product_info.empty else f"Unknown ({prod_id})"
                tooltip_lines.append(f"• {qty}x {product_name}")
            tooltip_lines.append(f"<br>Utilization: {utilization_percent:.1f}%")

            self.setToolTip("<br>".join(tooltip_lines))
        else:
            # Modified this section to remove the span if you don't like it,
            # or keep it if you want specific styling for 'Empty'
            
            # OR, for simpler text:
            # display_text = f"<b>{self.cell_id}</b><br>Empty<br><small>Drop products here</small>"

            self.setToolTip(f"<b>{self.cell_id}</b><br>Empty cell<br>Capacity: {self.cell_data['capacity']}<br><br>💡 You can drop products here!")

        #self.setText(display_text)
#        print(f"DEBUG: Cell {self.cell_id} - Text set. Current text format is: {self.textFormat()}") # Debug print

    def _set_cell_styling(self, utilization_percent: float):
        """Set cell styling based on utilization"""
        status = self._get_cell_status(utilization_percent)
        colors = self._get_status_colors(status)

        # Add drop target styling if needed
        border_color = "#00BCD4" if self.is_drop_target else colors['border']
        border_width = "3px" if self.is_drop_target else "2px"

        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['bg_light']}, stop: 1 {colors['bg_dark']});
                border: {border_width} solid {border_color};
                border-radius: 12px;
                font-size: 12px;
                color: {colors['text']};
                padding: 8px;
                text-align: center;
                {"box-shadow: 0 0 15px rgba(0, 188, 212, 0.5);" if self.is_drop_target else ""}
            }}
            QPushButton:hover {{
                border: {border_width} solid {"#00BCD4" if self.is_drop_target else "#6C63FF"};
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['hover_light']}, stop: 1 {colors['hover_dark']});
            }}
            QPushButton:pressed {{
                background: {colors['pressed']};
            }}
            /* Specific styles for rich text elements within the button */
            QPushButton b {{ /* For <b> tags */
                font-weight: bold;
                color: #232946; /* Darker color for cell ID */
            }}
            QPushButton small {{ /* For <small> tags */
                font-size: 10px;
                color: #888888; /* Lighter color for utilization text */
            }}
            QPushButton span {{ /* For <span> tags, specifically for 'Empty' */
                color: #999999; /* Grey for empty text */
                font-style: italic;
            }}
        """)

    def _get_cell_status(self, utilization_percent: float) -> CellStatus:
        """Determine cell status based on utilization"""
        if utilization_percent == 0:
            return CellStatus.EMPTY
        elif utilization_percent < 30:
            return CellStatus.LOW_FILL
        elif utilization_percent < 70:
            return CellStatus.MEDIUM_FILL
        elif utilization_percent < 90:
            return CellStatus.HIGH_FILL
        else:
            return CellStatus.CRITICAL_FILL

    def _get_status_colors(self, status: CellStatus) -> Dict[str, str]:
        """Get colors for cell status"""
        color_schemes = {
            CellStatus.EMPTY: {
                'bg_light': '#F5F5F5', 'bg_dark': '#E0E0E0',
                'hover_light': '#EEEEEE', 'hover_dark': '#D5D5D5',
                'pressed': '#CCCCCC', 'border': '#BDBDBD', 'text': '#666666'
            },
            CellStatus.LOW_FILL: {
                'bg_light': '#E8F5E8', 'bg_dark': '#C8E6C9',
                'hover_light': '#DCEDC8', 'hover_dark': '#AED581',
                'pressed': '#9CCC65', 'border': '#81C784', 'text': '#2E7D32'
            },
            CellStatus.MEDIUM_FILL: {
                'bg_light': '#FFF3E0', 'bg_dark': '#FFCC02',
                'hover_light': '#FFE0B2', 'hover_dark': '#FFB74D',
                'pressed': '#FFA726', 'border': '#FF9800', 'text': '#E65100'
            },
            CellStatus.HIGH_FILL: {
                'bg_light': '#FFF3E0', 'bg_dark': '#FFAB91',
                'hover_light': '#FFCCBC', 'hover_dark': '#FF8A65',
                'pressed': '#FF7043', 'border': '#FF5722', 'text': '#BF360C'
            },
            CellStatus.CRITICAL_FILL: {
                'bg_light': '#FFEBEE', 'bg_dark': '#FFCDD2',
                'hover_light': '#FFCDD2', 'hover_dark': '#EF9A9A',
                'pressed': '#E57373', 'border': '#F44336', 'text': '#C62828'
            }
        }
        return color_schemes[status]

    def mousePressEvent(self, event):
        """Handle mouse press events for drag initiation"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            # Right-click for product selection menu
            self._show_product_menu(event.globalPosition().toPoint())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move events for drag operations"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        if ((event.pos() - self.drag_start_position).manhattanLength() <
            QApplication.startDragDistance()):
            return

        # Only start drag if cell has products
        if sum(self.cell_data['products'].values()) > 0:
            self._start_drag()

    def _show_product_menu(self, global_pos):
        """Show context menu for product selection"""
        if not self.cell_data['products']:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #6C63FF;
                color: white;
            }
        """)

        # Add menu items for each product
        for prod_id, qty in self.cell_data['products'].items():
            # Get product name from parent_widget.data
            worker_data = self.parent_widget.data
            product_info = worker_data.products_df[worker_data.products_df['ID'] == prod_id]
            product_name = product_info['Name'].iloc[0] if not product_info.empty else f"Unknown ({prod_id})"
            action = menu.addAction(f"📦 Move {qty}x {product_name}")
            action.triggered.connect(lambda checked, pid=prod_id: self._prepare_product_drag(pid))

        menu.addSeparator()
        move_all_action = menu.addAction("📦 Move All Products")
        move_all_action.triggered.connect(self._prepare_all_products_drag)

        menu.exec(global_pos)

    def _prepare_product_drag(self, product_id: str):
        """Prepare to drag a specific product"""
        self.selected_products = {product_id: self.cell_data['products'][product_id]}
        self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def _prepare_all_products_drag(self):
        """Prepare to drag all products"""
        self.selected_products = self.cell_data['products'].copy()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def _start_drag(self):
        """Start the drag operation"""
        # Get products to drag (either selected or all)
        products_to_drag = getattr(self, 'selected_products', self.cell_data['products'].copy())

        if not products_to_drag:
            return

        # Create drag object
        drag = QDrag(self)
        mime_data = QMimeData()

        # Create drag data
        drag_data = {
            'source_cell': self.cell_id,
            'products': products_to_drag
        }
        mime_data.setText(json.dumps(drag_data))
        drag.setMimeData(mime_data)

        # Create drag pixmap
        pixmap = self._create_drag_pixmap(products_to_drag)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))

        # Set visual feedback
        self.is_dragging = True
        self.setStyleSheet(self.styleSheet() + """
            QPushButton {
                opacity: 0.7;
                border: 2px dashed #6C63FF;
            }
        """)

        # Execute drag
        drop_action = drag.exec(Qt.DropAction.MoveAction)

        # Reset after drag
        self.is_dragging = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if hasattr(self, 'selected_products'):
            delattr(self, 'selected_products')
        self._setup_cell()  # Reset styling

    def _create_drag_pixmap(self, products: Dict[str, int]) -> QPixmap:
        """Create visual representation for drag operation"""
        pixmap = QPixmap(100, 80)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background
        painter.fillRect(0, 0, 100, 80, QColor(108, 99, 255, 180))
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawRoundedRect(2, 2, 96, 76, 8, 8)

        # Draw text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        y_offset = 20
        total_items = sum(products.values())
        painter.drawText(10, y_offset, f"📦 {total_items} items")

        y_offset += 20
        # Access parent_widget.data to get product names for drag pixmap
        worker_data = self.parent_widget.data
        for prod_id, qty in list(products.items())[:2]:  # Show max 2 products
            product_info = worker_data.products_df[worker_data.products_df['ID'] == prod_id]
            product_name = product_info['Name'].iloc[0] if not product_info.empty else f"Unknown ({prod_id})"
            painter.drawText(10, y_offset, f"{qty}x {product_name}")
            y_offset += 15

        if len(products) > 2:
            painter.drawText(10, y_offset, f"...+{len(products) - 2} more")

        painter.end()
        return pixmap

    def dragEnterEvent(self, event):
        """Handle drag enter events"""
        if event.mimeData().hasText():
            try:
                drag_data = json.loads(event.mimeData().text())
                if drag_data['source_cell'] != self.cell_id:
                    self.is_drop_target = True
                    self._set_cell_styling(sum(self.cell_data['products'].values()) / self.cell_data['capacity'] * 100)
                    event.acceptProposedAction()
                    self.cell_hovered.emit(self.cell_id, True)
            except (json.JSONDecodeError, KeyError):
                event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move events"""
        if self.is_drop_target:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Handle drag leave events"""
        self.is_drop_target = False
        self._set_cell_styling(sum(self.cell_data['products'].values()) / self.cell_data['capacity'] * 100)
        self.cell_hovered.emit(self.cell_id, False)

    def dropEvent(self, event):
        """Handle drop events"""
        if event.mimeData().hasText():
            try:
                drag_data = json.loads(event.mimeData().text())
                source_cell = drag_data['source_cell']
                products = drag_data['products']

                if source_cell != self.cell_id:
                    # Check if drop is possible
                    total_incoming = sum(products.values())
                    current_fill = sum(self.cell_data['products'].values())

                    if current_fill + total_incoming <= self.cell_data['capacity']:
                        # Emit signal for each product
                        for prod_id, qty in products.items():
                            self.product_dropped.emit(source_cell, self.cell_id, prod_id, qty)
                        event.acceptProposedAction()

                        # Show success feedback
                        self._show_drop_success_feedback()
                    else:
                        # Show capacity exceeded message
                        self._show_capacity_error(total_incoming, current_fill)
                        event.ignore()
                else:
                    event.ignore()
            except (json.JSONDecodeError, KeyError):
                event.ignore()

        # Reset drop target state
        self.is_drop_target = False
        self._set_cell_styling(sum(self.cell_data['products'].values()) / self.cell_data['capacity'] * 100)
        self.cell_hovered.emit(self.cell_id, False)

    def _show_drop_success_feedback(self):
        """Show visual feedback for successful drop"""
        # Temporary green glow effect
        self.setStyleSheet(self.styleSheet() + """
            QPushButton {
                border: 3px solid #4CAF50;
                box-shadow: 0 0 20px rgba(76, 175, 80, 0.6);
            }
        """)

        # Reset after a short delay
        QTimer.singleShot(1000, lambda: self._setup_cell())

    def _show_capacity_error(self, incoming: int, current: int):
        """Show capacity exceeded error"""
        QMessageBox.warning(
            self,
            "Capacity Exceeded",
            f"Cannot drop {incoming} items in {self.cell_id}.\n"
            f"Current: {current}/{self.cell_data['capacity']}\n"
            f"Available space: {self.cell_data['capacity'] - current}"
        )

class DragDropStorageWidget(QWidget):
    """Enhanced storage widget with drag and drop capabilities"""

    cell_clicked = pyqtSignal(str)
    product_moved = pyqtSignal(str, str, str, int)  # from_cell, to_cell, product_id, quantity

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.cell_buttons = {}
        self.logger = logging.getLogger(__name__)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # Header with drag & drop instructions
        header_widget = self._create_header()
        main_layout.addWidget(header_widget)

        # Storage grid area
        grid_scroll_area = self._create_scroll_area()
        main_layout.addWidget(grid_scroll_area)

        # Footer with drag & drop tips
        footer_widget = self._create_footer()
        main_layout.addWidget(footer_widget)

        self.setLayout(main_layout)

    def _create_header(self) -> QWidget:
        """Create header with drag & drop instructions"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)

        # Title
        title_layout = QHBoxLayout()
        title = QLabel("Storage System")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #232946;
            padding: 10px 0;
        """)
        title_layout.addWidget(title)
        title_layout.addStretch()

        # Instructions
        instructions = QLabel("💡 <b>How to use:</b> Right-click cells to select products • Left-click for details")
        instructions.setStyleSheet("""
            font-size: 14px;
            color: #666666;
            padding: 5px 0;
            background-color: #F0F8FF;
            border-radius: 5px;
            padding: 10px;
        """)
        instructions.setWordWrap(True)

        header_layout.addLayout(title_layout)
        header_layout.addWidget(instructions)

        return header_widget

    def _create_scroll_area(self) -> QScrollArea:
        """Create scrollable area for storage zones"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
            }
        """)

        # Main zones container
        self.zones_container = QWidget()
        self.zones_layout = QVBoxLayout(self.zones_container)
        self.zones_layout.setSpacing(25)
        self.zones_layout.setContentsMargins(20, 20, 20, 20)

        self.populate_zones_and_cells() # This is the call that was failing

        scroll_area.setWidget(self.zones_container)
        return scroll_area

    def _create_footer(self) -> QWidget:
        """Create footer with drag & drop tips"""
        footer_widget = QFrame()
        footer_widget.setFrameStyle(QFrame.Shape.Box)
        footer_widget.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        footer_layout = QVBoxLayout(footer_widget)

        # Drag & drop tips
        tips_label = QLabel("🎯 <b>Pro Tips:</b> • Use right-click for precise product selection • Drag multiple products at once • Visual feedback shows drop zones • Capacity limits are enforced")
        tips_label.setStyleSheet("font-size: 12px; color: #666666;")
        tips_label.setWordWrap(True)

        footer_layout.addWidget(tips_label)

        return footer_widget

    def _clear_layout(self, layout):
        """Helper to clear all widgets and layouts from a layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self._clear_layout(item.layout())

    def populate_zones_and_cells(self):
        print("DEBUG: populate_zones_and_cells called.") # Debug print

        # Clear existing widgets if repopulating
        self._clear_layout(self.zones_layout) # Use the helper function

        zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D']
        cells_per_zone = 10 # Hardcoded as per requirement

        for zone_name in zones:
            zone_group_box = QGroupBox(zone_name)
            zone_group_box.setStyleSheet("""
                QGroupBox {
                    font-size: 20px;
                    font-weight: bold;
                    color: #232946;
                    margin-top: 20px;
                    border: 1px solid #D0D0D0;
                    border-radius: 12px;
                    padding-top: 25px;
                    background-color: #FFFFFF;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 10px;
                    margin-left: 10px;
                    color: #6C63FF;
                }
            """)
            zone_grid_layout = QGridLayout()
            zone_grid_layout.setSpacing(10)
            zone_grid_layout.setContentsMargins(20, 20, 20, 20)

            # Populate cells within each zone
            for i in range(cells_per_zone):
                cell_num = i + 1
                cell_id = f"{zone_name}-{cell_num}"

                # Ensure cell_data exists for the button
                cell_data = self.data.get_cell_contents(cell_id)

                # Create drag & drop enabled cell button
                cell_button = DragDropStorageCellButton(cell_id, cell_data, self) # Pass 'self' (DragDropStorageWidget) as parent_widget

                # Connect signals
                cell_button.clicked.connect(partial(self.cell_clicked.emit, cell_id)) # Direct emit
                cell_button.product_dropped.connect(self.on_product_dropped)
                cell_button.cell_hovered.connect(self.on_cell_hovered)

                self.cell_buttons[cell_id] = cell_button

                # Arrange cells in a 2x5 grid within each zone
                row = i // 5 # 0 for first 5 cells, 1 for next 5
                col = i % 5  # 0 to 4
                zone_grid_layout.addWidget(cell_button, row, col)

            zone_group_box.setLayout(zone_grid_layout)
            self.zones_layout.addWidget(zone_group_box)

        self.zones_layout.addStretch() # Push zones to top

    def on_cell_clicked(self, cell_id: str):
        """Handle cell click events"""
        # This method is no longer directly connected if using partial(self.cell_clicked.emit, cell_id)
        # However, it's good practice to keep it if you might connect other things to it later,
        # or if you want to perform additional internal logic before emitting.
        # For now, the signal is emitted directly from the button.
        pass # The signal is already emitted directly by the partial connect

    def on_product_dropped(self, from_cell: str, to_cell: str, product_id: str, quantity: int):
        """Handle product drop events"""
        try:
            # Update data model
            success, message = self.data.move_product_between_cells(product_id, quantity, from_cell, to_cell)

            if success:
                # Update UI for both source and destination cells
                self.update_cell_display(from_cell)
                self.update_cell_display(to_cell)

                # Emit signal for external handling (e.g., to MainWindow)
                self.product_moved.emit(from_cell, to_cell, product_id, quantity)

                self.logger.info(f"Moved {quantity}x {product_id} from {from_cell} to {to_cell}")
            else:
                QMessageBox.warning(self, "Move Failed", message)

        except Exception as e:
            self.logger.error(f"Error moving product: {e}")
            QMessageBox.critical(self, "Error", f"Failed to move product: {e}")

    def on_cell_hovered(self, cell_id: str, is_hovered: bool):
        """Handle cell hover events during drag operations"""
        # You can add additional visual feedback here if needed
        pass

    def update_cell_display(self, cell_id: str):
        """Update specific cell display"""
        if cell_id in self.cell_buttons:
            cell_data = self.data.get_cell_contents(cell_id)
            self.cell_buttons[cell_id].cell_data = cell_data
            self.cell_buttons[cell_id]._setup_cell() # Re-runs setup to update display and styling

    def refresh_all_cells(self):
        """Refresh all cell displays"""
        for cell_id in self.cell_buttons:
            self.update_cell_display(cell_id)

# --- Other Widgets (from your original code, included for completeness) ---

        
        self.zones_layout.addStretch() # Push zones to top     
class MainWindow(QMainWindow):
    """Main application window with top navigation and modern design."""
    def __init__(self):
        super().__init__()
        self.data = WorkerData()
        self.setWindowTitle("Warehouse Worker Operations Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.create_navbar()
        self.create_content_area()

        self.apply_global_styles()

        self.navigate_to_widget(self.dashboard_widget)
        self.dashboard_btn.setChecked(True)

    def apply_global_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F2F5;
            }
            QLabel, QGroupBox, QTableWidget, QLineEdit, QComboBox, QPushButton, QTextEdit, QSpinBox, QListWidget {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 15px;
                color: #232946;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                font-size: 15px;
                selection-background-color: #6C63FF;
                selection-color: #FFFFFF;
                gridline-color: #F0F2F5;
                alternate-background-color: #F8F9FA;
            }
            QHeaderView::section {
                background-color: #2921C5;
                color: #FFFFFF;
                padding: 12px;
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
                background-color: #6C63FF;
                color: #FFFFFF;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #F0F2F5;
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

    def create_navbar(self):
        self.navbar = QFrame()
        self.navbar.setFixedHeight(70)
        self.navbar.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E0E0E0;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: 500;
                border-radius: 5px;
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #F0F2F5;
                color: #333333;
            }
            QPushButton:checked {
                background-color: #6C63FF;
                color: #FFFFFF;
                font-weight: bold;
            }
        """)
        navbar_layout = QHBoxLayout(self.navbar)
        navbar_layout.setContentsMargins(20, 0, 20, 0)
        navbar_layout.setSpacing(15)

        logo_label = QLabel("Warehouse Ops")
        logo_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
            margin-right: 30px;
        """)
        navbar_layout.addWidget(logo_label)

        self.dashboard_btn = QPushButton("Dashboard")
        self.expedition_btn = QPushButton("Expedition")
        self.movement_btn = QPushButton("Movements")
        self.exceptions_btn = QPushButton("Exceptions")
        self.cells_btn = QPushButton("Cells")
        self.logout_btn=QPushButton("Logout")

        self.dashboard_btn.setCheckable(True)
        self.expedition_btn.setCheckable(True)
        self.movement_btn.setCheckable(True)
        self.exceptions_btn.setCheckable(True)
        self.cells_btn.setCheckable(True)
        self.logout_btn.setCheckable(True)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.dashboard_btn)
        self.button_group.addButton(self.expedition_btn)
        self.button_group.addButton(self.movement_btn)
        self.button_group.addButton(self.exceptions_btn)
        self.button_group.addButton(self.cells_btn)
        self.button_group.addButton(self.logout_btn)

        self.dashboard_btn.clicked.connect(lambda: self.navigate_to_widget(self.dashboard_widget))
        self.expedition_btn.clicked.connect(lambda: self.navigate_to_widget(self.expedition_widget))
        self.movement_btn.clicked.connect(lambda: self.navigate_to_widget(self.movement_widget))
        self.exceptions_btn.clicked.connect(lambda: self.navigate_to_widget(self.exception_widget))
        self.cells_btn.clicked.connect(lambda: self.navigate_to_widget(self.storage_cell_widget))
        self.logout_btn.clicked.connect(self.logout)

        navbar_layout.addStretch()
        navbar_layout.addWidget(self.dashboard_btn)
        navbar_layout.addWidget(self.expedition_btn)
        navbar_layout.addWidget(self.movement_btn)
        navbar_layout.addWidget(self.exceptions_btn)
        navbar_layout.addWidget(self.cells_btn)
        navbar_layout.addStretch()

        self.main_layout.addWidget(self.navbar)

    def create_content_area(self):
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #F0F2F5; padding: 20px;")

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

        # Instantiate new widget for storage cells
        self.storage_cell_widget = scrollable(DragDropStorageWidget(self.data))
        # Connect the cell_clicked signal from the storage widget to your new method
        self.storage_cell_widget.widget().cell_clicked.connect(self._show_cell_details)


        self.content_stack.addWidget(self.dashboard_widget)
        self.content_stack.addWidget(self.expedition_widget)
        self.content_stack.addWidget(self.movement_widget)
        self.content_stack.addWidget(self.exception_widget)
        self.content_stack.addWidget(self.storage_cell_widget)

        self.main_layout.addWidget(self.content_stack)

    def logout(self):
        response = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if response == QMessageBox.StandardButton.Yes:
            self.close()
            # self.loginpage = login.FlipCard() # Assuming login is handled externally
            # self.loginpage.show()

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

    def _show_cell_details(self, cell_id: str):
        """
        Displays detailed information about the clicked cell.
        """
        cell_data = self.data.get_cell_contents(cell_id)
        # Pass self.data (WorkerData instance) to CellDetailDialog
        detail_dialog = CellDetailDialog(cell_id, cell_data, self.data, self)
        detail_dialog.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#232946"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#F8F9FA"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#232946"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#6C63FF"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#6C63FF"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())
