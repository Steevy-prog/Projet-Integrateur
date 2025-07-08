import sys, os
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QCheckBox, QFrame, QScrollArea,
    QSizePolicy, QSpacerItem, QGridLayout, QMessageBox, QComboBox, QStackedWidget,
    QTableWidgetItem, QTableWidget, QHeaderView, QTextEdit, QSplitter, QSpinBox,
    QAbstractItemView, QGroupBox, QListWidget, QListWidgetItem, QRadioButton, QDoubleSpinBox, QButtonGroup, QStyle,
    QDialog
)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter
import datetime
import random
import psycopg2
#import login as login
from helpbot import ChatBot
from db_connection import ConnectionDB
# Assuming 'id.py' exists and contains idgenerator
# from id import idgenerator 
# Mock idgenerator for standalone execution if id.py is not available
class MockIdGenerator:
    def generate_id(self, pattern, existing_ids):
        prefix = pattern[0:pattern.find('[')]
        while True:
            new_id = prefix + ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))
            if new_id not in existing_ids:
                return new_id
idgenerator = MockIdGenerator()

# Mock external modules for standalone execution
class MockChatBot:
    def show(self):
        QMessageBox.information(None, "ChatBot", "Chatbot functionality would open here.")
class MockSendScaMail:
    def send_email(self, *args):
        print("Mock send_sca_mail called.")
class MockInternalMail:
    def send_email(self, *args):
        print("Mock internalmail called.")

ChatBot = ChatBot
send_sca_mail = MockSendScaMail()
internalmail = MockInternalMail()


# Global organization ID for the client currently logged in
# In a real application, this would come from a login system
client_org_id = 'OFIRST' # Example client organization ID
emballeur_org_id = 'OEMB' # Example emballeur organization ID

# --- START OF BACKEND/DATABASE INITIALIZATION (DO NOT TOUCH) ---
# This section establishes the database connection and fetches initial data.
# It is intended to remain as provided in its initial configuration.
# global conn
# print("1. online")
# print("2. offline")
# # In a real application, this input would be handled differently (e.g., config file)
# # For this example, we'll default to offline for easier testing.
# it='2' # input("Enter the number of bd you want to use : ") 

# if it == '1':
#     print("You have chosen the online database.")
#     try:
#         conn = psycopg2.connect(
#             host="dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com",
#             database="projet_integrateur",
#             user="group13",
#             password="nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3",
#             port=5432
#         )
#     except psycopg2.OperationalError as e:
#         print(f"Could not connect to online database: {e}. Falling back to offline.")
#         it = '2' # Fallback to offline if online fails
# elif it == '2':
#     print("You have chosen the Steevy's database.")
#     conn = psycopg2.connect(
#         host="localhost",
#         database="postgres",
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

Connection = ConnectionDB()
connection_info = Connection.connection()
db_connection = connection_info['db_connection']

  
cur = db_connection.cursor()

# Fetch initial data for product, lot, and package IDs to ensure uniqueness
# These queries fetch existing data from the database at startup.
try:
    cur.execute("SELECT (p).* FROM \"EMIR\".Organisation_EVA() AS p;")
    orgs = cur.fetchall() # All organizations from the database

    cur.execute("SELECT (p).* FROM \"EMIR\".PColis_EVA(%s) AS p;",(client_org_id,))
    colis_db = cur.fetchall() # Existing packages from the database

    cur.execute("SELECT (p).* FROM \"EMIR\".PContenuColis_EVA(%s) AS p;",(client_org_id,))
    contenu = cur.fetchall() # Existing packages from the database

    cur.execute("SELECT (p).* FROM \"EMIR\".PLot_EVA(%s) AS p;",(client_org_id,))
    lots_db = cur.fetchall() # Existing products from the database

    cur.execute("SELECT (p).* FROM \"EMIR\".Produit_EVA() AS p;")
    produits_db = cur.fetchall() # Existing products from the database

    cur.execute("SELECT (p).* FROM \"EMIR\".inquiries_eva(\"SCA\".idorg_conv(%s)) AS p;",(client_org_id,))
    inq_db = cur.fetchall() # Existing products from the database

except psycopg2.Error as e:
    print(f"Database query error during initialization: {e}")
    print("Populating with dummy data for demonstration.")
    orgs = [('OFIRST', 'Client Org A'), ('OSEC', 'Supplier B'), ('OTHRD', 'Transporter C'), ('OEMB', 'Emballeur D')]
    colis_db = []
    contenu = []
    lots_db = []
    produits_db = [
        ('P001', 'OSEC', 'Product A', 'Description A', 10.0, 'Brand1', 'Model1', 'Electronics'),
        ('P002', 'OSEC', 'Product B', 'Description B', 20.0, 'Brand2', 'Model2', 'Packaging'),
        ('P003', 'OSEC', 'Product C', 'Description C', 5.0, 'Brand3', 'Model3', 'Non-Electronic')
    ]
    inq_db = []


# Global lists to keep track of generated IDs for uniqueness checks
# Populated with existing IDs from the database to prevent collisions.
productids = [l[0] for l in produits_db]
lotids = [l[0] for l in lots_db] 
packageids = [c[0] for c in colis_db] 

# Dictionaries to store in-memory additions (for demonstration purposes only)
# These are not persisted to the database automatically by these dictionaries.
added_products = {}
added_lots = {}
added_packages = {}
names = []
# --- END OF BACKEND/DATABASE INITIALIZATION ---

class Product:
    """Base class for product types."""
    def __init__(self, name, fournisseur, description="", prix_unitaire=0.0, brand="", model="", category=""):
        self.name = name
        self.fournisseur = fournisseur
        self.description = description
        self.prix_unitaire = prix_unitaire
        self.brand = brand
        self.model = model
        self.category = category

class MaterialProduct(Product):
    """Represents a physical product."""
    def __init__(self, name, fournisseur, length, width, height, mass, **kwargs):
        super().__init__(name, fournisseur, **kwargs)
        self.length = length
        self.width = width
        self.height = height
        self.mass = mass

class SoftwareProduct(Product):
    """Represents a software product."""
    def __init__(self, name, fournisseur, version, license_key, **kwargs):
        super().__init__(name, fournisseur, **kwargs)
        self.version = version
        self.license_key = license_key

class Lot:
    """Represents a lot of a specific product."""
    def __init__(self, product_id, product_name, quantity):
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"
            
class Colis:
    """Represents packages"""
    def __init__(self,idcolis,statut,items,orderdate,estimated_delivery,Customer_id,totalvalue):
        self.idcolis = idcolis
        self.statut = statut
        self.items = items
        self.orderdate = orderdate
        self.estimated_delivery = estimated_delivery
        self.customerid = Customer_id
        self.totalvaule = totalvalue
    

class EmballeurData:
    """Manages data relevant to the emballeur dashboard."""

    def __init__(self, emballeur_id):
        self.emballeur_id = emballeur_id
        self.connection_info = Connection.connection()
        self.db_connection = self.connection_info['db_connection']

        self.generate_sample_data()

    def generate_sample_data(self):
        """Generates or fetches sample data for emballeur's view."""
        # Fetch products relevant to the client's organization
        if not self.db_connection:
            self.connection_info = Connection.connection()
            self.db_connection = self.connection_info['db_connection']
        cur = self.db_connection.cursor()
        cur.execute("SELECT (p).* FROM \"EMIR\".Produit_EVA() AS p;")
        products = cur.fetchall()
        if not products:
            print("No products loaded from the database. Generating dummy product data.")
            products = [
                ('P001', 'SupplierA', 'Dummy Product 1', 'Desc 1', 10.0, 'BrandX', 'ModelA', 'Electronics'),
                ('P002', 'SupplierB', 'Dummy Product 2', 'Desc 2', 20.0, 'BrandY', 'ModelB', 'Packaging')
            ]
        self.products_df = pd.DataFrame(products, columns=['ID', 'Fourniseur', 'Name', 'Description', 'Prix Unitaire', 'IdModel', 'Category'])

        # Simulate pending shipping orders for the emballeur
        self.shipping_orders = []
        order_statuses = ['Pending', 'Ready for Picking', 'In Progress', 'Ready for Dispatch', 'Dispatched']
        for i in range(15):
            order_id = f'ORD{i+1:04d}'
            status = random.choice(order_statuses[:4]) # Emballeur mostly deals with pre-dispatch statuses
            items_count = random.randint(1, 5)
            order_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 7))
            
            # Simulate items for the order
            items = []
            total_value = 0.0
            for _ in range(items_count):
                product = random.choice(products)
                qty = random.randint(1, 10)
                items.append({
                    'product_id': product[0],
                    'product_name': product[2],
                    'quantity': qty,
                    'location': random.choice(['E0-A1', 'E1-B2', 'E2-C3', 'E3-D4']) # Mock locations
                })
                total_value += product[4] * qty # product[4] is 'Prix Unitaire'

            self.shipping_orders.append({
                'Order_ID': order_id,
                'Status': status,
                'Items_Count': items_count,
                'Order_Date': order_date,
                'Customer_Org_ID': random.choice([o[0] for o in orgs if o[0] != self.emballeur_id]), # Random customer
                'Items': items,
                'Total_Value': total_value
            })

        # Simulate packaging material inventory
        self.packaging_materials = [
            {'Name': 'Small Box', 'ID': 'PM001', 'Quantity': 150, 'Unit': 'pcs'},
            {'Name': 'Medium Box', 'ID': 'PM002', 'Quantity': 100, 'Unit': 'pcs'},
            {'Name': 'Large Box', 'ID': 'PM003', 'Quantity': 50, 'Unit': 'pcs'},
            {'Name': 'Packing Tape', 'ID': 'PM004', 'Quantity': 200, 'Unit': 'rolls'},
            {'Name': 'Bubble Wrap', 'ID': 'PM005', 'Quantity': 75, 'Unit': 'meters'}
        ]

        # Simulate recent activities for emballeur
        self.recent_activities = []
        activity_types = ['Order Prepared', 'Material Used', 'Package Dispatched', 'Material Restocked']
        for i in range(20):
            activity_time = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(1, 120))
            activity_type = random.choice(activity_types)
            description = f"Activity {i+1} related to {activity_type}."
            if activity_type == 'Order Prepared':
                order_id = random.choice(self.shipping_orders)['Order_ID']
                description = f"Order {order_id} marked as '{activity_type}'."
            elif activity_type == 'Material Used':
                material = random.choice(self.packaging_materials)
                qty_used = random.randint(1, 10)
                description = f"{qty_used} {material['Unit']} of {material['Name']} used."
            self.recent_activities.append({
                'Timestamp': activity_time,
                'Type': activity_type,
                'Description': description
            })

class EmballeurTaskCard(QFrame):
    """Card widget for displaying individual shipping orders."""

    order_selected = pyqtSignal(dict) 

    def __init__(self, order_data):
        super().__init__()
        self.order_data = order_data
        self.init_ui()

    def init_ui(self):
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setFixedHeight(120)
        self.setContentsMargins(0, 0, 0, 0)

        color = self.get_status_color(self.order_data.get('Status', 'Pending'))

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
                margin: 5px 0;
                padding: 0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
                transition: all 0.2s ease-in-out;
            }}
            QFrame:hover {{
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
                transform: translateY(-2px);
                border: 1px solid {color};
            }}
        """)

        accent_bar = QFrame(self)
        accent_bar.setFixedWidth(6)
        accent_bar.setStyleSheet(f"background-color: {color}; border-top-left-radius: 12px; border-bottom-left-radius: 12px;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(accent_bar)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(15, 10, 15, 10)
        content_layout.setSpacing(20)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        header_row = QHBoxLayout()
        order_label = QLabel(self.order_data['Order_ID'])
        order_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #343A40;")
        header_row.addWidget(order_label)
        header_row.addStretch()

        status_label = QLabel(self.order_data['Status'])
        status_label.setStyleSheet(f"background-color: {color}; color: #FFFFFF; border-radius: 8px; font-size: 12px; font-weight: bold; padding: 3px 8px;")
        header_row.addWidget(status_label)
        info_layout.addLayout(header_row)

        details_text = f"Items: <b>{self.order_data['Items_Count']}</b> &nbsp; | &nbsp; Value: <b>${self.order_data['Total_Value']:.2f}</b>"
        due_text = f"Order Date: <b>{self.order_data['Order_Date'].strftime('%Y-%m-%d')}</b>"

        details_label = QLabel(details_text)
        details_label.setStyleSheet("font-size: 13px; color: #6C757D;")
        details_label.setTextFormat(Qt.TextFormat.RichText)
        due_label = QLabel(due_text)
        due_label.setStyleSheet("font-size: 13px; color: #888888;")
        due_label.setTextFormat(Qt.TextFormat.RichText)

        info_layout.addWidget(details_label)
        info_layout.addWidget(due_label)
        info_layout.addStretch()

        action_btn = QPushButton("Prepare Order")
        action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 14px;
                font-weight: 600;
                color: #FFFFFF;
                box-shadow: 0 2px 8px rgba(40, 167, 69, 0.2);
                transition: all 0.2s ease-in-out;
            }}
            QPushButton:hover {{
                background-color: #218838;
            }}
        """)
        action_btn.clicked.connect(self.on_action_clicked)

        content_layout.addLayout(info_layout, stretch=3)
        content_layout.addWidget(action_btn, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def get_status_color(self, status):
        colors = {
            'Pending': "#FFC107",           # Amber
            'Ready for Picking': "#007BFF", # Blue
            'In Progress': "#17A2B8",       # Cyan
            'Ready for Dispatch': "#28A745",# Green
            'Dispatched': "#6C757D",        # Gray
        }
        return colors.get(status, '#6C757D') # Default gray

    def on_action_clicked(self):
        self.order_selected.emit(self.order_data)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.order_selected.emit(self.order_data)

class PrepareOrderDialog(QDialog):
    """Dialog for emballeur to prepare a selected order."""
    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.setWindowTitle(f"Prepare Order: {self.order_data['Order_ID']}")
        self.setFixedSize(700, 650)
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
                color: #343A40;
                margin-bottom: 7px;
            }
            QLabel.title {
                font-size: 26px;
                font-weight: bold;
                color: #343A40;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #E0E0E0;
            }
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                min-height: 150px;
            }
            QHeaderView::section {
                background-color: #007BFF;
                color: #FFFFFF;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QCheckBox {
                spacing: 8px;
                color: #343A40;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #007BFF;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #007BFF;
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNGRkZGRkYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiI+PC9wb2x5bGluZT48L3N2Zz4=); /* Checkmark SVG */
            }
        """)

        title_label = QLabel(f"Order: {self.order_data['Order_ID']}")
        title_label.setProperty("class", "title")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.addRow("Status:", QLabel(self.order_data['Status']))
        form_layout.addRow("Items Count:", QLabel(str(self.order_data['Items_Count'])))
        form_layout.addRow("Total Value:", QLabel(f"${self.order_data['Total_Value']:.2f}"))
        form_layout.addRow("Order Date:", QLabel(self.order_data['Order_Date'].strftime('%Y-%m-%d %H:%M')))
        form_layout.addRow("Customer Org ID:", QLabel(self.order_data['Customer_Org_ID']))
        layout.addLayout(form_layout)

        items_table_label = QLabel("Items to Pick:")
        layout.addWidget(items_table_label)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(['Product Name', 'Quantity', 'Location', 'Picked'])
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.horizontalHeader().setStretchLastSection(True)
        self.items_table.setAlternatingRowColors(True)

        self.items_table.setRowCount(len(self.order_data['Items']))
        self.picked_checkboxes = []

        for i, item_data in enumerate(self.order_data['Items']):
            self.items_table.setItem(i, 0, QTableWidgetItem(item_data.get('product_name', 'N/A')))
            self.items_table.setItem(i, 1, QTableWidgetItem(str(item_data.get('quantity', 'N/A'))))
            self.items_table.setItem(i, 2, QTableWidgetItem(item_data.get('location', 'N/A')))
            
            checkbox = QCheckBox()
            checkbox.setChecked(False) # Initially not picked
            self.items_table.setCellWidget(i, 3, checkbox)
            self.picked_checkboxes.append(checkbox)

        layout.addWidget(self.items_table)

        button_layout = QHBoxLayout()
        self.mark_prepared_button = QPushButton("Mark as Ready for Dispatch")
        self.mark_prepared_button.clicked.connect(self.mark_order_prepared)
        
        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #6C757D;")
        close_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.mark_prepared_button)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def mark_order_prepared(self):
        all_picked = all(cb.isChecked() for cb in self.picked_checkboxes)
        if not all_picked:
            QMessageBox.warning(self, "Incomplete Picking", "Please confirm all items are picked before marking as ready for dispatch.")
            return

        # In a real application, update the database here
        self.order_data['Status'] = 'Ready for Dispatch'
        QMessageBox.information(self, "Order Status Updated", f"Order {self.order_data['Order_ID']} is now 'Ready for Dispatch'.")
        self.accept()

class EmballeurOrderPreparationWidget(QWidget):
    """Widget for managing and preparing shipping orders."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        header_layout = QHBoxLayout()
        title = QLabel("Shipping Order Preparation")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #28A745;")

        refresh_btn = QPushButton("Refresh Orders")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                box-shadow: 0 4px 10px rgba(0, 123, 255, 0.2);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #0056B3;
                transform: translateY(-2px);
            }
        """)
        refresh_btn.clicked.connect(self.refresh_orders) 

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)

        # Filter and Search
        filter_search_layout = QHBoxLayout()
        filter_search_layout.setSpacing(15)

        search_label = QLabel("Search Order:")
        search_label.setStyleSheet("font-size: 15px; color: #343A40;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter order ID or customer ID...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #28A745;
            }
        """)
        self.search_input.textChanged.connect(self.filter_orders)

        status_label = QLabel("Filter by Status:")
        status_label.setStyleSheet("font-size: 15px; color: #343A40;")
        self.status_combo = QComboBox()
        self.status_combo.addItems(['All', 'Pending', 'Ready for Picking', 'In Progress', 'Ready for Dispatch', 'Dispatched'])
        self.status_combo.setStyleSheet("""
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
        """)
        self.status_combo.currentTextChanged.connect(self.filter_orders)

        filter_search_layout.addWidget(search_label)
        filter_search_layout.addWidget(self.search_input, 3)
        filter_search_layout.addWidget(status_label)
        filter_search_layout.addWidget(self.status_combo, 1)
        filter_search_layout.addStretch()
        layout.addLayout(filter_search_layout)

        # Orders List
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.orders_list_widget = QWidget()
        self.orders_list_layout = QVBoxLayout(self.orders_list_widget)
        self.orders_list_layout.setSpacing(10)
        self.orders_list_layout.addStretch() # Push cards to top
        scroll_area.setWidget(self.orders_list_widget)
        layout.addWidget(scroll_area)

        self.setLayout(layout)
        self.update_orders_list(self.data.shipping_orders) # Initial population

    def refresh_orders(self):
        # In a real app, re-fetch data from DB
        self.data.generate_sample_data() # Regenerate dummy data for demo
        self.filter_orders() # Re-apply filters

    def filter_orders(self):
        search_text = self.search_input.text().lower()
        selected_status = self.status_combo.currentText()

        filtered_orders = []
        for order in self.data.shipping_orders:
            if search_text and search_text not in order['Order_ID'].lower() and search_text not in order['Customer_Org_ID'].lower():
                continue
            if selected_status != 'All' and order['Status'] != selected_status:
                continue
            filtered_orders.append(order)
        
        self.update_orders_list(filtered_orders)

    def update_orders_list(self, orders):
        # Clear existing cards
        while self.orders_list_layout.count() > 0:
            item = self.orders_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new cards
        if orders:
            sorted_orders = sorted(orders, key=lambda x: x['Order_Date'], reverse=True)
            for order in sorted_orders:
                order_card = EmballeurTaskCard(order)
                order_card.order_selected.connect(self.on_order_selected)
                self.orders_list_layout.addWidget(order_card)
        else:
            no_orders_label = QLabel("No orders matching your criteria.")
            no_orders_label.setStyleSheet("color: #999; font-style: italic; padding: 20px; text-align: center;")
            self.orders_list_layout.addWidget(no_orders_label)
        
        self.orders_list_layout.addStretch() # Ensure stretch is always at the end

    def on_order_selected(self, order_data):
        dialog = PrepareOrderDialog(order_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.filter_orders() # Refresh list after status update

class PackagingMaterialCard(QFrame):
    """Card widget for displaying individual packaging materials."""
    def __init__(self, material_data):
        super().__init__()
        self.material_data = material_data
        self.init_ui()

    def init_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
            QLabel {
                color: #343A40;
            }
            QLabel.name {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            QLabel.qty {
                font-size: 28px;
                font-weight: bold;
                color: #007BFF;
            }
            QLabel.unit {
                font-size: 14px;
                color: #6C757D;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        name_label = QLabel(self.material_data['Name'])
        name_label.setProperty("class", "name")
        
        qty_layout = QHBoxLayout()
        qty_label = QLabel(str(self.material_data['Quantity']))
        qty_label.setProperty("class", "qty")
        unit_label = QLabel(self.material_data['Unit'])
        unit_label.setProperty("class", "unit")
        qty_layout.addWidget(qty_label)
        qty_layout.addWidget(unit_label)
        qty_layout.addStretch()

        layout.addWidget(name_label)
        layout.addLayout(qty_layout)
        layout.addStretch()

        self.setLayout(layout)

class UpdateMaterialDialog(QDialog):
    """Dialog to update packaging material quantity."""
    def __init__(self, material_data, parent=None):
        super().__init__(parent)
        self.material_data = material_data
        self.setWindowTitle(f"Update {self.material_data['Name']}")
        self.setFixedSize(400, 250)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border-radius: 15px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            }
            QLabel {
                font-size: 15px;
                color: #343A40;
            }
            QSpinBox {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 25px;
                height: 25px;
                border-radius: 4px;
                background-color: #007BFF;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNGRkZGRkYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSI1IDEyIDEyIDUgMTkgMTIiPjwvcG9seWxpbmU+PC9zdmc+);
            }
            QSpinBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNGRkZGRkYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSI1IDEyIDEyIDE5IDE5IDEyIj48L3BvbHlsaW5lPjwvc3ZnPg==);
            }
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        layout.addRow("Material:", QLabel(self.material_data['Name']))
        layout.addRow("Current Quantity:", QLabel(f"{self.material_data['Quantity']} {self.material_data['Unit']}"))
        
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(0, 9999)
        self.quantity_spinbox.setValue(self.material_data['Quantity'])
        layout.addRow("New Quantity:", self.quantity_spinbox)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_changes)
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("background-color: #6C757D;")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)

        self.setLayout(layout)

    def save_changes(self):
        new_qty = self.quantity_spinbox.value()
        if new_qty != self.material_data['Quantity']:
            self.material_data['Quantity'] = new_qty # Update in-memory data
            QMessageBox.information(self, "Success", f"Quantity for {self.material_data['Name']} updated to {new_qty}.")
            self.accept()
        else:
            self.reject() # No changes, just close

class EmballeurPackagingMaterialWidget(QWidget):
    """Widget for managing packaging material inventory."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        header_layout = QHBoxLayout()
        title = QLabel("Packaging Material Inventory")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #007BFF;")

        refresh_btn = QPushButton("Refresh Inventory")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                box-shadow: 0 4px 10px rgba(0, 123, 255, 0.2);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #0056B3;
                transform: translateY(-2px);
            }
        """)
        refresh_btn.clicked.connect(self.refresh_inventory)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)

        # Material display area
        self.material_grid_layout = QGridLayout()
        self.material_grid_layout.setSpacing(20)
        layout.addLayout(self.material_grid_layout)
        layout.addStretch()

        self.update_material_display()

        self.setLayout(layout)

    def refresh_inventory(self):
        # In a real app, re-fetch data from DB
        self.data.generate_sample_data() # Regenerate dummy data for demo
        self.update_material_display()

    def update_material_display(self):
        # Clear existing cards
        while self.material_grid_layout.count():
            item = self.material_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, material in enumerate(self.data.packaging_materials):
            card = PackagingMaterialCard(material)
            # Add a button or make card clickable to open update dialog
            update_btn = QPushButton("Update")
            update_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17A2B8;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            update_btn.clicked.connect(lambda checked, m=material: self.open_update_material_dialog(m))
            
            card_layout = QVBoxLayout(card)
            card_layout.addStretch()
            card_layout.addWidget(update_btn, alignment=Qt.AlignmentFlag.AlignRight)
            
            self.material_grid_layout.addWidget(card, i // 3, i % 3) # 3 columns

    def open_update_material_dialog(self, material_data):
        dialog = UpdateMaterialDialog(material_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update_material_display() # Refresh display after update

class EmballeurDashboardWidget(QWidget):
    """Main dashboard widget for emballeurs."""

    def __init__(self, data, main_window):
        super().__init__()
        self.data = data
        self.main_window = main_window
        self.connection_info = Connection.connection()
        self.db_connection = self.connection_info['db_connection']

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        hero_frame = QFrame()
        hero_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #28A745, stop:1 #007BFF);
                border-radius: 15px;
                padding: 30px;
                color: #FFFFFF;
                box-shadow: 0 8px 30px rgba(40, 167, 69, 0.3);
            }
            QLabel {
                color: #FFFFFF;
            }
        """)
        hero_layout = QVBoxLayout(hero_frame)
        
        # Fetch emballeur organization name
        emballeur_name = "Emballeur"
        
        if not self.db_connection:
            self.connection_info = Connection.connection()
            self.db_connection = self.connection_info['db_connection']
        cur = self.db_connection.cursor()
        try:
            cur.execute('SELECT "EMIR".getorganisationname(%s);',(self.data.emballeur_id,))
            result = cur.fetchone()
            if result:
                emballeur_name = result[0]
        except psycopg2.Error as e:
            print(f"Error fetching emballeur name: {e}")

        welcome_label = QLabel(f"Welcome, {emballeur_name} Team!")
        welcome_label.setStyleSheet("font-size: 32px; font-weight: bold;")

        time_label = QLabel(f"Today: {datetime.datetime.now().strftime('%A, %B %d, %Y')}")
        time_label.setStyleSheet("font-size: 16px; margin-top: 5px;")

        hero_layout.addWidget(welcome_label)
        hero_layout.addWidget(time_label)
        hero_layout.addStretch()

        dashboard_stats_layout = QHBoxLayout()
        dashboard_stats_layout.setSpacing(20)

        pending_orders = len([o for o in self.data.shipping_orders if o['Status'] in ['Pending', 'Ready for Picking']])
        in_progress_orders = len([o for o in self.data.shipping_orders if o['Status'] == 'In Progress'])
        ready_for_dispatch = len([o for o in self.data.shipping_orders if o['Status'] == 'Ready for Dispatch'])
        low_stock_materials = len([m for m in self.data.packaging_materials if m['Quantity'] < 50])

        dashboard_stats_layout.addWidget(self.create_dashboard_card("Orders to Prepare", pending_orders, "#FFC107", "New & ready for picking"))
        dashboard_stats_layout.addWidget(self.create_dashboard_card("In Progress", in_progress_orders, "#17A2B8", "Currently being picked/packed"))
        dashboard_stats_layout.addWidget(self.create_dashboard_card("Ready for Dispatch", ready_for_dispatch, "#28A745", "Packed & awaiting pickup"))
        dashboard_stats_layout.addWidget(self.create_dashboard_card("Low Stock Materials", low_stock_materials, "#DC3545", "Packaging materials needing attention"))

        hero_layout.addLayout(dashboard_stats_layout)
        layout.addWidget(hero_frame)

        quick_actions_group = QGroupBox("Quick Actions")
        quick_actions_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #343A40;
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
                color: #28A745;
            }
        """)
        quick_actions_layout = QHBoxLayout()
        quick_actions_layout.setSpacing(15)
        quick_actions_layout.setContentsMargins(20, 25, 20, 20)

        button_style = """
            QPushButton {
                background-color: #F0F2F5;
                border: none;
                border-radius: 10px;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: 600;
                color: #343A40;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #28A745;
                color: #FFFFFF;
                transform: translateY(-2px);
            }
        """

        prepare_orders_btn = QPushButton("Prepare Orders")
        prepare_orders_btn.setStyleSheet(button_style)
        prepare_orders_btn.clicked.connect(lambda: self.main_window.navigate_to_widget(self.main_window.order_preparation_widget))

        manage_materials_btn = QPushButton("Manage Packaging Materials")
        manage_materials_btn.setStyleSheet(button_style)
        manage_materials_btn.clicked.connect(lambda: self.main_window.navigate_to_widget(self.main_window.packaging_material_widget))

        quick_actions_layout.addWidget(prepare_orders_btn)
        quick_actions_layout.addWidget(manage_materials_btn)
        quick_actions_group.setLayout(quick_actions_layout)
        layout.addWidget(quick_actions_group)

        recent_activity_group = QGroupBox("Recent Activities")
        recent_activity_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #343A40;
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
                color: #007BFF;
            }
        """)
        recent_activity_layout = QVBoxLayout()
        recent_activity_layout.setContentsMargins(20, 25, 20, 20)
        recent_activity_layout.setSpacing(10)

        latest_activities = sorted(self.data.recent_activities, key=lambda x: x['Timestamp'], reverse=True)[:5]
        if latest_activities:
            for activity in latest_activities:
                activity_label = QLabel(f"<span style='font-weight:bold;'>{activity['Timestamp'].strftime('%H:%M')}</span> | {activity['Description']}")
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
        title_label.setStyleSheet("font-size: 14px; color: #6C757D; font-weight: bold;")

        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")

        description_label = QLabel(description)
        description_label.setStyleSheet("font-size: 12px; color: #999999;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(description_label)
        layout.addStretch()

        card.setLayout(layout)
        return card

class HelpWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # --- Card 1: AI Assistant Placeholder --
        ai_card = QFrame()
        ai_card.setStyleSheet("""
            QFrame {
                background-color: #F8F0FA;
                border-radius: 16px;
                border: 1px solid #E0E0E0;
                padding: 20px;
                box-shadow: 0 4px 5px rgba(40, 167, 69, 0.07);
            }
        """)
        ai_layout = QVBoxLayout(ai_card)
        ai_title = QLabel("🤖 AI Assistant ")
        ai_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #28A745;")
        ai_desc = QLabel("An intelligent assistant that will answer all your questions about the platform.")
        ai_desc.setWordWrap(True)
        ai_desc.setStyleSheet("font-size: 18px; color:#343A40;")
        ai_btn = QPushButton("Ask your questions")
        ai_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        ai_btn.clicked.connect(self.open_helpbot_dialog)  # Placeholder for AI chat functionality
        ai_layout.addWidget(ai_title)
        ai_layout.addWidget(ai_desc)
        ai_layout.addWidget(ai_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        ai_layout.addStretch()
        
        # --- Card 2: Report a Bug ---
        bug_card = QFrame()
        bug_card.setStyleSheet("""
            QFrame {
                background-color: #FFF3E0;
                border-radius: 16px;
                border: 1px solid #E0E0E0;
                padding: 20px;
                box-shadow: 0 4px 5px rgba(255, 193, 7, 0.07);
            }
        """)
        bug_layout= QVBoxLayout(bug_card)
        bug_title = QLabel("🐞 Report a Bug")
        bug_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFC107;")
        bug_desc = QLabel("If you encounter a problem or bug, please let our IT support know so we can fix it quickly.")
        bug_desc.setWordWrap(True)
        bug_desc.setStyleSheet("font-size: 18px; color: #343A40;")
        report_btn = QPushButton("Report a Bug")
        report_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                color: #343A40;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #FFB300;
            }
        """)
        report_btn.clicked.connect(self.open_bug_report_dialog)
        bug_layout.addWidget(bug_title)
        bug_layout.addWidget(bug_desc)
        bug_layout.addWidget(report_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        bug_layout.addStretch()
        
        layout.addWidget(ai_card)
        layout.addWidget(bug_card)
        layout.addStretch()
        
    def open_helpbot_dialog(self):
        self.chatbot_window = ChatBot()
        self.chatbot_window.show()
        
    def open_bug_report_dialog(self):
        dialog = BugReportDialog(self)
        dialog.exec()
        
class BugReportDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Report a Bug")
        self.setFixedSize(450,350)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30,30,30,30)
        self.setStyleSheet("""
            QDialog{
                background-color: #F8F9FA;
                border-radius: 12px;
            }
            QLabel {
                font-size: 16px;
                color: #343A40;
            }
            QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: #FFFFFF;
                padding: 8px;
            }
            QPushButton {
                background-color: #FFC107;
                color: #343A40;
                font-weight: bold;
                font-size: 15px;
                border-radius: 8px;
                padding: 10px 24px;
            }
            QPushButton:hover {
                background-color: #FFB300;
            }
        """)
        label = QLabel("Describe the bug you encounter:")
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Please provide as much details as possible")
        
        self.send_btn  = QPushButton("Send to IT Support")
        self.send_btn.clicked.connect(self.send_bug_report)
        
        layout.addWidget(label)
        layout.addWidget(self.text_edit)
        layout.addStretch()
        layout.addWidget(self.send_btn, alignment=Qt.AlignmentFlag.AlignRight)
       
    def send_bug_report(self):
        import smtplib
        from email.mime.text import MIMEText

        bug_text = self.text_edit.toPlainText().strip()
        if not bug_text:
            QMessageBox.warning(self, "Input Error", "Please describe the bug before sending.")
            return

        # --- Email sending logic (update with your IT support email) ---
        support_email = "it.support@example.com" # Placeholder email
        subject = "Bug Report from Emballeur Dashboard"
        body = bug_text

        try:
            # These details would need to be configured for a real email server
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            smtp_user = "your_email@gmail.com" # Replace with a real sender email
            smtp_password = "your_email_password" # Replace with the actual password/app password

            # This part is commented out for demo purposes to avoid actual email sending without user configuration
            # msg = MIMEText(body)
            # msg["Subject"] = subject
            # msg["From"] = smtp_user
            # msg["To"] = support_email

            # with smtplib.SMTP(smtp_server, smtp_port) as server:
            #     server.starttls()
            #     server.login(smtp_user, smtp_password)
            #     server.sendmail(smtp_user, [support_email], msg.as_string())

            QMessageBox.information(self, "Sent", "Your bug report has been simulated and would be sent to IT support. Thank you!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to simulate bug report sending.\n\nError: {e}\n\n(In a real app, configure SMTP details.)")


class EmballeurMainWindow(QMainWindow):
    """Main application window for the emballeur dashboard."""
    def __init__(self):
        super().__init__()
        self.data = EmballeurData(emballeur_org_id) # Pass emballeur_org_id
        self.setWindowTitle("Emballeur Logistics Dashboard")
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
            QLabel, QGroupBox, QTableWidget, QLineEdit, QComboBox, QPushButton, QTextEdit, QSpinBox, QListWidget, QRadioButton, QDoubleSpinBox, QCheckBox {
                font-family: 'Inter', 'Segoe UI', 'Arial', sans-serif;
                font-size: 15px;
                color: #343A40;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                font-size: 15px;
                selection-background-color: #E6F2FF; /* Light blue for selection */
                selection-color: #343A40;
                gridline-color: #F0F2F5;
                alternate-background-color: #F8F9FA;
            }
            QHeaderView::section {
                background-color: #007BFF; /* Blue header */
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
                background-color: #007BFF;
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
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 6px;
                padding: 8px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #28A745; /* Green focus border */
            }
            QMessageBox QLabel {
                color: black;
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI', 'Arial', sans-serif;
            }
        """)

    def create_navbar(self):
        self.navbar = QFrame()
        self.navbar.setFixedHeight(70)
        self.navbar.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E0E0E0;
                box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #6C757D;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                border-radius: 3px;
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #F0F2F5;
                color: #343A40;
            }
            QPushButton:checked {
                background-color: #28A745; /* Green for selected */
                color: #FFFFFF;
                font-weight: bold;
            }
        """)
        navbar_layout = QHBoxLayout(self.navbar)
        navbar_layout.setContentsMargins(20, 0, 20, 0)
        navbar_layout.setSpacing(15)

        logo_label = QLabel("Emballeur Dashboard")
        logo_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #28A745; /* Green logo */
            margin-right: 30px;
        """)
        navbar_layout.addWidget(logo_label)

        self.dashboard_btn = QPushButton("Dashboard")
        self.order_preparation_btn = QPushButton("Order Preparation")
        self.packaging_material_btn = QPushButton("Packaging Materials")
        self.help_btn = QPushButton("Help")
        self.logout_btn = QPushButton("Logout")

        self.dashboard_btn.setCheckable(True)
        self.order_preparation_btn.setCheckable(True)
        self.packaging_material_btn.setCheckable(True)
        self.help_btn.setCheckable(True)
        self.logout_btn.setCheckable(True)


        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.dashboard_btn)
        self.button_group.addButton(self.order_preparation_btn)
        self.button_group.addButton(self.packaging_material_btn)
        self.button_group.addButton(self.help_btn)
        self.button_group.addButton(self.logout_btn)


        self.dashboard_btn.clicked.connect(lambda: self.navigate_to_widget(self.dashboard_widget))
        self.order_preparation_btn.clicked.connect(lambda: self.navigate_to_widget(self.order_preparation_widget))
        self.packaging_material_btn.clicked.connect(lambda: self.navigate_to_widget(self.packaging_material_widget))
        self.help_btn.clicked.connect(lambda: self.navigate_to_widget(self.help_widget))
        self.logout_btn.clicked.connect(self.logout)
        navbar_layout.addStretch()
        navbar_layout.addWidget(self.dashboard_btn)
        navbar_layout.addWidget(self.order_preparation_btn)
        navbar_layout.addWidget(self.packaging_material_btn)
        navbar_layout.addWidget(self.help_btn) 
        navbar_layout.addWidget(self.logout_btn) 
        navbar_layout.addStretch()

        self.main_layout.addWidget(self.navbar)
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

    def create_content_area(self):
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #F0F2F5; padding: 30px;")
        
        def scrollable(widget, object_name=None):
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(widget)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            if object_name:
                widget.setObjectName(object_name) 
            return scroll

        self.dashboard_widget = scrollable(EmballeurDashboardWidget(self.data, self))
        self.order_preparation_widget = scrollable(EmballeurOrderPreparationWidget(self.data))
        self.packaging_material_widget = scrollable(EmballeurPackagingMaterialWidget(self.data))
        self.help_widget = HelpWidget()

        self.content_stack.addWidget(self.dashboard_widget)
        self.content_stack.addWidget(self.order_preparation_widget)
        self.content_stack.addWidget(self.packaging_material_widget)
        self.content_stack.addWidget(self.help_widget)

        self.main_layout.addWidget(self.content_stack)

    def navigate_to_widget(self, target_widget):
        self.content_stack.setCurrentWidget(target_widget)
        for button in self.button_group.buttons():
            button.setChecked(False)

        if target_widget == self.dashboard_widget:
            self.dashboard_btn.setChecked(True)
        elif target_widget == self.order_preparation_widget:
            self.order_preparation_btn.setChecked(True)
        elif target_widget == self.packaging_material_widget:
            self.packaging_material_btn.setChecked(True)
        elif target_widget == self.help_widget:
            self.help_btn.setChecked(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # High-contrast, accessible palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f5f5f5"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#343A40"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f0f0f0"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Text, QColor("#343A40"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#e0e0e0"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#343A40"))
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor("#007BFF"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#28A745"))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    
    app.setPalette(palette)
    app.setFont(QFont("Inter", 10)) # Using 'Inter' as requested, fallback to 'Segoe UI' or 'Arial'

    emballeur_main_window = EmballeurMainWindow()
    emballeur_main_window.showMaximized()
    sys.exit(app.exec())
