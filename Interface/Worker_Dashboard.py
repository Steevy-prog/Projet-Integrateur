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
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter
import datetime
import random
import psycopg2
from db_connection import ConnectionDB

Connection = ConnectionDB()
#import login as login

worker_id = 'TR1234'
# global conn
# print("1. online")
# print("2. offline")
# it = input("Enter the number of bd you want to use : ")

# if it == '1':
#     print("You have chosen the online database.")
#     conn = psycopg2.connect(
#         host="dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com",
#         database="projet_integrateur",
#         user="group13",
#         password="nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3",
#         port=5432
#     )
# elif it == '2':
#     print("You have chosen the offline database.")
#     conn = psycopg2.connect(
#         host="localhost",
#         database="USER",
#         user="postgres",
#         password="steevy",
#         port=5432
#     )
    
# elif it == '3':
#     print("You have chosen the Viktor's database.")
#     conn = psycopg2.connect(
#         host="localhost",
#         database="Projet",
#         user="postgres",
#         password="Lune.Hatik123",
#         port=5432
#     )
# cur = con.cursor()

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
            if not self.db_connection:
                self.connection_info = Connection.connection()
                self.db_connection = self.connection_info['db_connection']
            
            cur = self.db_connection.cursor()
            cur.execute("SELECT (p).* FROM \"EMIR\".getlots(%s) AS p;", (self.task_data['Colis'],))
            items_count = cur.fetchall()
            details_text = f"Items: <b>{len(items_count)}</b> &nbsp; | &nbsp; Est: <b>{self.task_data['duree']} min</b>"
            #details_text = f"Items: <b>{0}</b> &nbsp; | &nbsp; Est: <b>{self.task_data['duree']} min</b>"
            due_text = f"Due: <b>{self.task_data['date-ech']}</b>"
        else: # For other card types, adjust details as needed
            details_text = f"Customer: <b>{self.task_data.get('Customer', 'N/A')}</b>"
            due_text = f"Status: <b>{self.task_data.get('status', 'Pending')}</b>"

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
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #333333;")
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
        aisles = sorted(list(set(c[0] for c in self.data.storage_cells.keys())))
        max_rows_per_aisle = max([int(c.split('-')[0][1:]) for c in self.data.storage_cells.keys()])
        max_cols_per_aisle = max([int(c.split('-')[1]) for c in self.data.storage_cells.keys()])

        # Add aisle labels as column headers (horizontal)
        for col, aisle_char in enumerate(aisles):
            aisle_label = QLabel(f"Aisle {aisle_char}")
            aisle_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 5px; color: #333;")
            self.grid_layout.addWidget(aisle_label, 0, col + 1)  # Row 0, columns 1..N

        # Add row labels (row numbers)
        for row in range(1, max_rows_per_aisle + 1):
            row_label = QLabel(f"Row {row}")
            row_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-right: 5px; color: #333;")
            self.grid_layout.addWidget(row_label, row, 0)  # Column 0

        # Place cells in grid: rows = row numbers, columns = aisles
        for col, aisle_char in enumerate(aisles):
            for row in range(1, max_rows_per_aisle + 1):
                for c in range(1, max_cols_per_aisle + 1):
                    cell_id = f"{aisle_char}{row}-{c}"
                    if cell_id in self.data.storage_cells:
                        cell_data = self.data.get_cell_contents(cell_id)
                        cell_button = QPushButton(cell_id)
                        cell_button.setFixedSize(100, 80)
                        cell_button.setCursor(Qt.CursorShape.PointingHandCursor)

                        # Determine color and text for cell
                        if cell_data['products']:
                            bg_color = "#E6E6FF"  # Light blue/purple for occupied
                            text_color = "#232946"
                            # Show product count in button
                            content = "<br>".join([f"{qty}x" for qty in cell_data['products'].values()])
                            cell_button.setText(f"{cell_id}\n{content}")
                        elif cell_data['status'] == 'Available':
                            bg_color = "#E8F5E8"  # Light green
                            text_color = "#232946"
                            cell_button.setText(f"{cell_id}\nEmpty")
                        elif cell_data['status'] == 'Full':
                            bg_color = "#FFEBEE"  # Light red
                            text_color = "#232946"
                            cell_button.setText(f"{cell_id}\nFull")
                        else:
                            bg_color = "#E0E0E0"  # Default grey
                            text_color = "#232946"
                            cell_button.setText(f"{cell_id}\nN/A")

                        cell_button.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {bg_color};
                                border: 1px solid #CCCCCC;
                                border-radius: 8px;
                                font-size: 14px;
                                font-weight: bold;
                                color: {text_color};
                            }}
                            QPushButton:hover {{
                                border: 2px solid #6C63FF;
                            }}
                        """)
                        cell_button.clicked.connect(lambda checked, cid=cell_id: self.on_cell_clicked(cid))
                        # Place in grid: row index = row, column index = col+1 (since col 0 is label)
                        self.grid_layout.addWidget(cell_button, row, col + 1)
        # Stretch for nice layout
        self.grid_layout.setRowStretch(self.grid_layout.rowCount(), 1)
        self.grid_layout.setColumnStretch(self.grid_layout.columnCount(), 1)
    
    def on_cell_clicked(self, cell_id):
        """Emit the cell_clicked signal with the cell ID."""
        self.cell_clicked.emit(cell_id)
        
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
        self.main_layout = QVBoxLayout(self.central_widget) # Change to QVBoxLayout for top navbar

        self.create_navbar()
        self.create_content_area()

        self.apply_global_styles()

        # Set initial view
        self.navigate_to_widget(self.dashboard_widget)
        self.dashboard_btn.setChecked(True) # Ensure dashboard button is highlighted

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
        self.navbar.setFixedHeight(70) # Fixed height for navbar
        self.navbar.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF; /* White navbar background */
                border-bottom: 1px solid #E0E0E0;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666; /* Medium gray text */
                padding: 10px 20px;
                font-size: 16px;
                font-weight: 500;
                border-radius: 5px;
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #F0F2F5; /* Light background on hover */
                color: #333333; /* Darker text on hover */
            }
            QPushButton:checked {
                background-color: #6C63FF; /* Primary accent for selected */
                color: #FFFFFF;
                font-weight: bold;
            }
        """)
        navbar_layout = QHBoxLayout(self.navbar)
        navbar_layout.setContentsMargins(20, 0, 20, 0)
        navbar_layout.setSpacing(15)

        # Logo/Title
        logo_label = QLabel("Warehouse Ops")
        logo_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
            margin-right: 30px;
        """)
        navbar_layout.addWidget(logo_label)

        # Navigation buttons
        self.dashboard_btn = QPushButton("Dashboard")
        self.expedition_btn = QPushButton("Expedition")
        self.movement_btn = QPushButton("Movements")
        self.exceptions_btn = QPushButton("Exceptions")
        self.cells_btn = QPushButton("Cells") # New button for storage cells
        self.logout_btn=QPushButton("logout")

        self.dashboard_btn.setCheckable(True)
        self.expedition_btn.setCheckable(True)
        self.movement_btn.setCheckable(True)
        self.exceptions_btn.setCheckable(True)
        self.cells_btn.setCheckable(True) # Make new button checkable
        self.logout_btn.setCheckable(True)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.dashboard_btn)
        self.button_group.addButton(self.expedition_btn)
        self.button_group.addButton(self.movement_btn)
        self.button_group.addButton(self.exceptions_btn)
        self.button_group.addButton(self.cells_btn)# Add new button to group
        self.button_group.addButton(self.logout_btn)

        self.dashboard_btn.clicked.connect(lambda: self.navigate_to_widget(self.dashboard_widget))
        self.expedition_btn.clicked.connect(lambda: self.navigate_to_widget(self.expedition_widget))
        self.movement_btn.clicked.connect(lambda: self.navigate_to_widget(self.movement_widget))
        self.exceptions_btn.clicked.connect(lambda: self.navigate_to_widget(self.exception_widget))
        self.cells_btn.clicked.connect(lambda: self.navigate_to_widget(self.storage_cell_widget))
        self.logout_btn.clicked.connect(self.logout) # Connect new button

        navbar_layout.addStretch() # Pushes buttons to the center/right
        navbar_layout.addWidget(self.dashboard_btn)
        navbar_layout.addWidget(self.expedition_btn)
        navbar_layout.addWidget(self.movement_btn)
        navbar_layout.addWidget(self.exceptions_btn)
        navbar_layout.addWidget(self.cells_btn) # Add new button to navbar layout
        navbar_layout.addStretch() # For more centered look if desired
        #navbar_layout.addWidget(self.logout.btn)

        self.main_layout.addWidget(self.navbar)

    def create_content_area(self):
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #F0F2F5; padding: 20px;") # Content area background

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
        self.storage_cell_widget = scrollable(StorageCellWidget(self.data)) # Instantiate new widget

        self.content_stack.addWidget(self.dashboard_widget)
        self.content_stack.addWidget(self.expedition_widget)
        self.content_stack.addWidget(self.movement_widget)
        self.content_stack.addWidget(self.exception_widget)
        self.content_stack.addWidget(self.storage_cell_widget) # Add new widget to stack

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
            #self.loginpage = login.FlipCard()
            self.loginpage.show()

    def navigate_to_widget(self, target_widget):
        self.content_stack.setCurrentWidget(target_widget)
        # The QButtonGroup handles the checking, but this ensures initial state or manual calls work
        for button in self.button_group.buttons():
            button.setChecked(False) # Uncheck all first
        
        if target_widget == self.dashboard_widget:
            self.dashboard_btn.setChecked(True)
        elif target_widget == self.expedition_widget:
            self.expedition_btn.setChecked(True)
        elif target_widget == self.movement_widget:
            self.movement_btn.setChecked(True)
        elif target_widget == self.exception_widget:
            self.exceptions_btn.setChecked(True)
        elif target_widget == self.storage_cell_widget: # Handle new button
            self.cells_btn.setChecked(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # A modern style
    
        # --- Set a global palette for dialogs and message boxes ---
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
    # ----------------------------------------------------------

    
    main_window = MainWindow()
    main_window.showMaximized() # Start maximized for a better experience
    sys.exit(app.exec())