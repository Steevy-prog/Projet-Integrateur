
import sys,os
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
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
from id import idgenerator # Assuming 'id.py' exists and contains idgenerator
from helpbot import ChatBot

# Global organization ID for the client currently logged in
# In a real application, this would come from a login system
client_org_id = 'OABCDE' # Example client organization ID

# --- START OF BACKEND/DATABASE INITIALIZATION (DO NOT TOUCH) ---
# This section establishes the database connection and fetches initial data.
# It is intended to remain as provided in its initial configuration.
global conn
print("1. online")
print("2. offline")
it = input("Enter the number of bd you want to use : ")

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
        database="postgres",
        user="postgres",
        password="steevy",
        port=5432
    )

cur = conn.cursor()

# Fetch initial data for product, lot, and package IDs to ensure uniqueness
# These queries fetch existing data from the database at startup.
cur.execute("SELECT (p).* FROM \"EMIR\".Organisation_EVA() AS p;")
orgs = cur.fetchall() # All organizations from the database

cur.execute("SELECT (p).* FROM \"EMIR\".Colis_EVA() AS p;")
colis_db = cur.fetchall() # Existing packages from the database

cur.execute("SELECT (p).* FROM \"EMIR\".PLot_EVA() AS p;")
lots_db = cur.fetchall() # Existing products from the database

cur.execute("SELECT (p).* FROM \"EMIR\".Produit_EVA() AS p;")
produits_db = cur.fetchall() # Existing products from the database

# Global lists to keep track of generated IDs for uniqueness checks
# Populated with existing IDs from the database to prevent collisions.
productids = []
lotids = [l[0] for l in colis_db] # Assuming colis_db contains lot IDs, this might need adjustment
packageids = [c[0] for c in colis_db] # Assuming package IDs are in colis_db

print(idgenerator.generate_id('^P[A-Z0-9]{5}$',productids))
os.system("pause")

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

class ClientData:
    """Manages data relevant to the client dashboard."""

    def __init__(self, client_id):
        self.client_id = client_id
        self.generate_sample_data()

    def generate_sample_data(self):
        """Generates or fetches sample data for client's view."""
        # Fetch products relevant to the client's organization
        # For simplicity, assuming all products are relevant or fetching client-specific products
        cur.execute("SELECT (p).* FROM \"EMIR\".Produit_EVA() AS p;")
        products = cur.fetchall()
        if not products:
            print("No products loaded from the database. Generating dummy product data.")
            # Dummy data if no products found (should ideally be handled by DB setup)
            products = [
                ('P001', 'SupplierA', 'Dummy Product 1', 'Desc 1', 10.0, 'BrandX', 'ModelA', 'Electronics'),
                ('P002', 'SupplierB', 'Dummy Product 2', 'Desc 2', 20.0, 'BrandY', 'ModelB', 'Furniture')
            ]
        self.products_df = pd.DataFrame(products, columns=['ID', 'Fourniseur', 'Name', 'Description', 'Prix Unitaire', 'Brand', 'Model', 'Category'])

        # Client Orders (adapted from expedition tasks)
        self.client_orders = []
        order_statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
        for i in range(15):
            order_items_raw = random.sample(products, random.randint(1, min(4, len(products))))
            order_items_count = sum([random.randint(1, 5) for _ in order_items_raw])
            
            # Simulate a few orders belonging to this client_id
            customer_org = self.client_id if random.random() > 0.3 else 'OtherOrg'

            self.client_orders.append({
                'Order_ID': f'CO{i+1:03d}',
                'Status': random.choice(order_statuses),
                'Items_Count': order_items_count,
                'Order_Date': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30)),
                'Estimated_Delivery': datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 10)),
                'Customer_Org_ID': customer_org,
                'Items': order_items_raw, # Store raw product data
                'Total_Value': round(sum(p[4] * random.randint(1,5) for p in order_items_raw), 2)
            })
        
        # Filter orders for the current client
        self.client_orders = [order for order in self.client_orders if order['Customer_Org_ID'] == self.client_id]

        # Product Movement History (tracking shipments for client's packages)
        self.movement_history = []
        movement_types = ['Outbound', 'In Transit', 'Received', 'Return']
        for i in range(50):
            product = random.choice(products)
            # Simulate movements for this client's packages
            package_id_sim = f'PKG{random.randint(100, 999):03d}'
            if random.random() < 0.6: # More likely to be client's package
                self.movement_history.append({
                    'Movement_ID': f"MOV{i:05d}",
                    'Timestamp': datetime.datetime.now() - datetime.timedelta(hours=random.randint(0, 72)),
                    'Package_ID': package_id_sim,
                    'Product_Name': product[2], # Product name from tuple
                    'Movement_Type': random.choice(movement_types),
                    'Location': random.choice(['Warehouse A', 'Transit Hub B', 'Client Dock', 'Supplier C']),
                    'Description': f"Package {package_id_sim} {random.choice(['departed', 'arrived at', 'in transit to'])} {random.choice(['destination', 'next hub'])}."
                })
        
        # Exceptions/Inquiries
        self.inquiries = []
        inquiry_types = ['Missing Package', 'Damaged Item', 'Incorrect Order', 'Billing Issue', 'General Support']
        inquiry_statuses = ['Open', 'In Progress', 'Resolved', 'Closed']
        for i in range(8):
            product = random.choice(products)
            # Simulate inquiries from this client
            inquirer_org = self.client_id if random.random() > 0.3 else 'OtherOrg'
            self.inquiries.append({
                'ID': f'INQ{i+1:03d}',
                'Type': random.choice(inquiry_types),
                'Related_Product': product[2],
                'Reported_By_Org': inquirer_org,
                'Reported_Time': datetime.datetime.now() - datetime.timedelta(hours=random.randint(0, 12)),
                'Status': random.choice(inquiry_statuses),
                'Description': f'Inquiry about {product[2]} due to {random.choice(["damage", "missing items", "delivery delay"])}.'
            })
        
        # Filter inquiries for the current client
        self.inquiries = [inq for inq in self.inquiries if inq['Reported_By_Org'] == self.client_id]

class ClientTaskCard(QFrame):
    """Card widget for displaying individual client orders."""

    order_selected = pyqtSignal(dict) # Renamed signal

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
                border: 1px solid #FFFFFF;
                margin: 5px 0;
                padding: 0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
                transition: all 0.2s ease-in-out;
            }}
            QFrame:hover {{
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
                transform: translateY(-2px);
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
        order_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #333333;")
        header_row.addWidget(order_label)
        header_row.addStretch()

        status_label = QLabel(self.order_data['Status'])
        status_label.setStyleSheet(f"background-color: {color}; color: #FFFFFF; border-radius: 8px; font-size: 12px; font-weight: bold; padding: 1px 1px;")
        header_row.addWidget(status_label)
        info_layout.addLayout(header_row)

        details_text = f"Items: <b>{self.order_data['Items_Count']}</b> &nbsp; | &nbsp; Value: <b>${self.order_data['Total_Value']:.2f}</b>"
        due_text = f"Expected: <b>{self.order_data['Estimated_Delivery'].strftime('%Y-%m-%d')}</b>"

        details_label = QLabel(details_text)
        details_label.setStyleSheet("font-size: 13px; color: #666666;")
        details_label.setTextFormat(Qt.TextFormat.RichText)
        due_label = QLabel(due_text)
        due_label.setStyleSheet("font-size: 13px; color: #888888;")
        due_label.setTextFormat(Qt.TextFormat.RichText)

        info_layout.addWidget(details_label)
        info_layout.addWidget(due_label)
        info_layout.addStretch()

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

    def get_status_color(self, status):
        colors = {
            'Pending':"#6C63FF",
            'Processing': "#6C63FF",    # Blue
            'Shipped': "#6C63FF",
            'Delivered': "#6C63FF",
            'Cancelled': "#6C63FF",   # Red
        }
        return colors.get(status, '#666666') # Default color

    def on_action_clicked(self):
        self.order_selected.emit(self.order_data)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.order_selected.emit(self.order_data)

class OrderDetailsDialog(QDialog):
    """Dialog to display details of a selected client order."""
    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.setWindowTitle(f"Order Details: {self.order_data['Order_ID']}")
        self.setFixedSize(500, 550)
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
                margin-bottom: 7px;
            }
            QLabel.title {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
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
                transition: all 0.2s ease-in-out;
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
            }
            QListWidget::item {
                padding: 5px;
            }
            QFormLayout QLabel {
                font-weight: bold;
                color: #555555;
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
        form_layout.addRow("Estimated Delivery:", QLabel(self.order_data['Estimated_Delivery'].strftime('%Y-%m-%d')))
        form_layout.addRow("Customer Org ID:", QLabel(self.order_data['Customer_Org_ID']))
        layout.addLayout(form_layout)

        items_list_label = QLabel("Items in Order:")
        layout.addWidget(items_list_label)
        items_list = QListWidget()
        for item_data in self.order_data['Items']:
            items_list.addItem(f"- {item_data[2]} (ID: {item_data[0]}), Price: ${item_data[4]:.2f}")
        layout.addWidget(items_list)

        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #999999;")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

class ProductCreationPopup(QDialog):
    """Dialog to create a new product (physical or software)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Product")
        self.setFixedSize(900, 600)
        self.layout = QVBoxLayout(self)
        self.step = 1
        self.product_type = None

        self.setStyleSheet("""
            QLabel {
                color: black;
                font-weight: bold;
                font-size: 13px;
            }
            QLineEdit, QDoubleSpinBox, QComboBox, QTextEdit {
                color: black;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)

        self.build_step_1()

    def build_step_1(self):
        self.clear_layout()
        label = QLabel("Choose product type:")
        self.physical_radio = QRadioButton("Physical Product")
        self.software_radio = QRadioButton("Software Product")

        next_btn = QPushButton("Next")
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        next_btn.clicked.connect(self.goto_step_2)

        self.scroll_layout.addWidget(label)
        self.scroll_layout.addWidget(self.physical_radio)
        self.scroll_layout.addWidget(self.software_radio)
        self.scroll_layout.addStretch()
        self.scroll_layout.addWidget(next_btn)

    def goto_step_2(self):
        if self.physical_radio.isChecked():
            self.product_type = "physical"
        elif self.software_radio.isChecked():
            self.product_type = "software"
        else:
            QMessageBox.warning(self, "Error", "Please select a product type.")
            return

        self.clear_layout()
        form_layout = QFormLayout()

        # ...existing code...

        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("color: #232946; background: #FFFFFF;height: 30px;")
        self.prix_unitaire = QDoubleSpinBox()
        self.prix_unitaire.setSuffix(" $")
        self.prix_unitaire.setStyleSheet("color: #232946; background: #FFFFFF;")
        self.prix_unitaire.setRange(0.0, 100000.0)

        self.marque = QLineEdit()
        self.description = QTextEdit()
        self.marque.setStyleSheet("color: #232946; background: #FFFFFF;")
        self.description = QTextEdit()
        self.description.setStyleSheet("color: #232946; background: #FFFFFF;")
        self.modele = QLineEdit()
        self.modele.setStyleSheet("color: #232946; background: #FFFFFF;")

# For radio buttons and combo box, you can also set styles if needed:
        
        self.categorie_group = QButtonGroup(self)
        self.categorie1 = QRadioButton("Packaging")
        self.categorie2 = QRadioButton("Electronic")
        self.categorie3 = QRadioButton("Non-Electronic")
        self.categorie_group.addButton(self.categorie1)
        self.categorie_group.addButton(self.categorie2)
        self.categorie_group.addButton(self.categorie3)
        self.categorie1.setChecked(True)
        self.categorie1.setChecked(True) # Default selection
        self.categorie1.setStyleSheet("color: #232946;")
        self.categorie2.setStyleSheet("color: #232946;")
        self.categorie3.setStyleSheet("color: #232946;")
        

        

        self.fournisseur = QComboBox()
        for org in orgs:
            self.fournisseur.addItem(org[1], org[0]) # Display name, store ID
        self.fournisseur.setStyleSheet("color: #232946; background: #FFFFFF;")
        
        if self.product_type == "physical":
            self.category_text = "Packaging"
            self.categorie_group.buttonClicked.connect(lambda btn: setattr(self, 'category_text', btn.text()))

            self.length_input = QDoubleSpinBox()
            self.length_input.setSuffix(" cm")
            self.length_input.setRange(0.0, 1000.0)
            self.length_input.setValue(10.0)

            self.width_input = QDoubleSpinBox()
            self.width_input.setSuffix(" cm")
            self.width_input.setRange(0.0, 1000.0)
            self.width_input.setValue(10.0)

            self.height_input = QDoubleSpinBox()
            self.height_input.setSuffix(" cm")
            self.height_input.setRange(0.0, 1000.0)
            self.height_input.setValue(10.0)

            self.mass_input = QDoubleSpinBox()
            self.mass_input.setSuffix(" kg")
            self.mass_input.setRange(0.0, 1000.0)
            self.mass_input.setValue(10.0)

            ho = QHBoxLayout()
            ho.addWidget(self.categorie1)
            ho.addWidget(self.categorie2)
            ho.addWidget(self.categorie3)

            form_layout.addRow("Name:", self.name_input)
            form_layout.addRow("Supplier:", self.fournisseur)
            form_layout.addRow("Description:", self.description)
            form_layout.addRow("Unit Price:", self.prix_unitaire)
            form_layout.addRow("Brand:", self.marque)
            form_layout.addRow("Model:", self.modele)
            form_layout.addRow("Category:", ho)
            form_layout.addRow("Length:", self.length_input)
            form_layout.addRow("Width:", self.width_input)
            form_layout.addRow("Height:", self.height_input)
            form_layout.addRow("Mass:", self.mass_input)
        else:
            self.version_input = QLineEdit()
            self.license_input = QLineEdit()

            form_layout.addRow("Name:", self.name_input)
            form_layout.addRow("Supplier:", self.fournisseur)
            form_layout.addRow("Description:", self.description)
            form_layout.addRow("Unit Price:", self.prix_unitaire)
            form_layout.addRow("Brand:", self.marque)
            form_layout.addRow("Model:", self.modele)
            form_layout.addRow("Version:", self.version_input)
            form_layout.addRow("License Key:", self.license_input)
            self.category_text = "Software"

        self.produitid = idgenerator.generate_id("^P[A-Z0-9]{5}$", productids)
        productids.append(self.produitid)

        submit_btn = QPushButton("Create Product")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        submit_btn.clicked.connect(self.submit_product)

        self.scroll_layout.addLayout(form_layout)
        self.scroll_layout.addStretch()
        self.scroll_layout.addWidget(submit_btn)

    def submit_product(self):
        name = self.name_input.text().strip()
        fournisseur_id = self.fournisseur.currentData()
        description = self.description.toPlainText().strip()
        prix_unitaire = self.prix_unitaire.value()
        marque = self.marque.text().strip()
        modele = self.modele.text().strip()
        category = self.category_text

        if not name or not fournisseur_id:
            QMessageBox.warning(self, "Validation Error", "Product name and supplier are required.")
            return

        try:
            cur.execute('CALL "EMIR".Produit_INS(%s,%s,%s,%s,%s,%s,%s,%s)',
                        (self.produitid, fournisseur_id, name, description, prix_unitaire, marque, modele, category))
            if self.product_type == "physical":
                cur.execute('CALL "EMIR".ProduitMateriel_INS(%s,%s,%s,%s,%s)',
                            (self.produitid,
                             self.length_input.value(),
                             self.width_input.value(),
                             self.height_input.value(),
                             self.mass_input.value()))
            else:
                cur.execute('CALL "EMIR".ProduitLogiciel_INS(%s,%s,%s)',
                            (self.produitid,
                             self.version_input.text().strip(),
                             self.license_input.text().strip()))
            conn.commit()
            QMessageBox.information(self, "Success", f"Product '{name}' created successfully.")
            self.accept()
        except psycopg2.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to create product: {e}")

    def clear_layout(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

class ProductCreationPopup1(QDialog):
    """Dialog to create a new product (physical or software)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Product")
        self.setFixedSize(1200, 500)
        self.layout = QVBoxLayout(self)
        self.step = 1
        self.product_type = None
        self.build_step_1()

    def build_step_1(self):
        self.clear_layout()
        label = QLabel("Choose product type:")
        label.setStyleSheet("color: black;")
        self.physical_radio = QRadioButton("Physical Product")
        self.software_radio = QRadioButton("Software Product")

        next_btn = QPushButton("Next")
        next_btn.setStyleSheet("""
            QPushButton {
                background-color:#333333;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5247D6;;
            }
        """)
        self.setStyleSheet("""
            QLabel {
                color: black;
                font-weight: bold;
                font-size: 13px;
            }
            QLineEdit, QDoubleSpinBox, QComboBox, QTextEdit {
                color: black;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                width: 7px;
                height: 20px

            }
        """)
        next_btn.clicked.connect(self.goto_step_2)

        self.layout.addWidget(label)
        self.layout.addWidget(self.physical_radio)
        self.layout.addWidget(self.software_radio)
        self.layout.addStretch()
        self.layout.addWidget(next_btn)

    def goto_step_2(self):
        if self.physical_radio.isChecked():
            self.product_type = "physical"
        elif self.software_radio.isChecked():
            self.product_type = "software"
        else:
            QMessageBox.warning(self, "Error", "Please select a product type.")
            return

        self.clear_layout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_container = QWidget()
        form_layout = QFormLayout(form_container)

        scroll.setWidget(form_container)
        self.layout.addWidget(scroll)

        self.name_input = QLineEdit()
        self.prix_unitaire = QDoubleSpinBox()
        self.prix_unitaire.setSuffix(" $")
        self.prix_unitaire.setRange(0.0, 100000.0)

        self.marque = QLineEdit()
        self.description = QTextEdit()
        self.modele = QLineEdit()

        self.fournisseur = QComboBox()
        for org in orgs:
            self.fournisseur.addItem(org[1], org[0])  # Display name, store ID

        form_layout.addRow(QLabel("Name:"), self.name_input)
        form_layout.addRow(QLabel("Supplier:"), self.fournisseur)
        form_layout.addRow(QLabel("Description:"), self.description)
        form_layout.addRow(QLabel("Unit Price:"), self.prix_unitaire)
        form_layout.addRow(QLabel("Brand:"), self.marque)
        form_layout.addRow(QLabel("Model:"), self.modele)

        if self.product_type == "physical":
            self.categorie_group = QButtonGroup(self)
            self.categorie1 = QRadioButton("Packaging")
            self.categorie2 = QRadioButton("Electronic")
            self.categorie3 = QRadioButton("Non-Electronic")
            self.categorie_group.addButton(self.categorie1)
            self.categorie_group.addButton(self.categorie2)
            self.categorie_group.addButton(self.categorie3)
            self.categorie1.setChecked(True)
            self.category_text = "Packaging"
            self.categorie_group.buttonClicked.connect(lambda btn: setattr(self, 'category_text', btn.text()))

            ho = QHBoxLayout()
            ho.addWidget(self.categorie1)
            ho.addWidget(self.categorie2)
            ho.addWidget(self.categorie3)

            self.length_input = QDoubleSpinBox()
            self.length_input.setSuffix(" cm")
            self.length_input.setRange(0.0, 1000.0)
            self.length_input.setValue(10.0)

            self.width_input = QDoubleSpinBox()
            self.width_input.setSuffix(" cm")
            self.width_input.setRange(0.0, 1000.0)
            self.width_input.setValue(10.0)

            self.height_input = QDoubleSpinBox()
            self.height_input.setSuffix(" cm")
            self.height_input.setRange(0.0, 1000.0)
            self.height_input.setValue(10.0)

            self.mass_input = QDoubleSpinBox()
            self.mass_input.setSuffix(" kg")
            self.mass_input.setRange(0.0, 1000.0)
            self.mass_input.setValue(10.0)

            form_layout.addRow(QLabel("Category:"), ho)
            form_layout.addRow(QLabel("Length:"), self.length_input)
            form_layout.addRow(QLabel("Width:"), self.width_input)
            form_layout.addRow(QLabel("Height:"), self.height_input)
            form_layout.addRow(QLabel("Mass:"), self.mass_input)
        else:
            self.version_input = QLineEdit()
            self.license_input = QLineEdit()
            form_layout.addRow(QLabel("Version:"), self.version_input)
            form_layout.addRow(QLabel("License Key:"), self.license_input)
            self.category_text = "Software"

        # Generate Product ID
        self.produitid = idgenerator.generate_id("^P[A-Z0-9]{5}$", productids)
        productids.append(self.produitid)

        submit_btn = QPushButton("Create Product")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-color: black;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        submit_btn.clicked.connect(self.submit_product)

        self.layout.addWidget(submit_btn)

    def submit_product(self):
        name = self.name_input.text().strip()
        fournisseur_id = self.fournisseur.currentData()
        description = self.description.toPlainText().strip()
        prix_unitaire = self.prix_unitaire.value()
        marque = self.marque.text().strip()
        modele = self.modele.text().strip()
        category = self.category_text

        if not name or not fournisseur_id:
            QMessageBox.warning(self, "Validation Error", "Product name and supplier are required.")
            return

        try:
            cur.execute('CALL "EMIR".Produit_INS(%s,%s,%s,%s,%s,%s,%s,%s)',
                        (self.produitid, fournisseur_id, name, description, prix_unitaire, marque, modele, category))
            if self.product_type == "physical":
                length = self.length_input.value()
                width = self.width_input.value()
                height = self.height_input.value()
                mass = self.mass_input.value()
                cur.execute('CALL "EMIR".ProduitMateriel_INS(%s,%s,%s,%s,%s)',
                            (self.produitid, length, width, height, mass))
            else:
                version = self.version_input.text().strip()
                license_key = self.license_input.text().strip()
                cur.execute('CALL "EMIR".ProduitLogiciel_INS(%s,%s,%s)',
                            (self.produitid, version, license_key))
            conn.commit()
            QMessageBox.information(self, "Success", f"Product '{name}' (ID: {self.produitid}) created successfully.")
            self.accept()
        except psycopg2.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to create product: {e}")

    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


def show_product_creation_popup(parent=None):
    dialog = ProductCreationPopup1(parent)
    dialog.exec()

class ProductInputRow(QHBoxLayout):
    """A row for product selection and quantity in package creation."""
    def __init__(self, products_data, remove_callback):
        super().__init__()
        self.products_data = products_data
        self.remove_callback = remove_callback

        self.product_combo = QComboBox()
        self.product_combo.addItem("— Select a product —", None)
        self.product_combo.setStyleSheet("background-color: 5472AE")
        for p in self.products_data:
            self.product_combo.addItem(p[2], p[0]) # Display name, store ID

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 1000)
        self.qty_spin.setValue(1)

        self.remove_btn = QPushButton("X")
        self.remove_btn.setFixedSize(34, 34)
        self.remove_btn.setStyleSheet("color: red; font-weight: bold; border-radius: 12px; background-color: #FFEBEE;")
        self.remove_btn.clicked.connect(self._on_remove_clicked)

        self.addWidget(self.product_combo)
        self.addWidget(self.qty_spin)
        self.addWidget(self.remove_btn)

    def _on_remove_clicked(self):
        # Remove widgets from layout first
        for i in reversed(range(self.count())):
            widget = self.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        # Then call the callback to remove this row from the parent's list
        self.remove_callback(self)

    def get_selected_product(self):
        product_id = self.product_combo.currentData()
        quantity = self.qty_spin.value()
        if product_id:
            product_name = self.product_combo.currentText()
            return Lot(product_id, product_name, quantity)
        return None

class NameInputDialog(QDialog):
    """Generic dialog for entering a name/string."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Name")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()
        self.label = QLabel("Please enter a name for the package:")
        self.name_input = QLineEdit()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.submit_name)

        layout.addWidget(self.label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)
        self.result_name = ""

    def submit_name(self):
        name = self.name_input.text().strip()
        if name:
            self.result_name = name
            self.accept()
        else:
            QMessageBox.warning(self, "Input Error", "Name cannot be empty.")

    def get_name(self):
        if self.exec() == QDialog.DialogCode.Accepted:
            return self.result_name
        return None

class ClientLogisticsWidget(QWidget):
    """Widget for client-side product and package management (creation, sending)."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.package_input_rows = [] # To keep track of ProductInputRow instances
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Product & Package Management")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color:#6C63FF;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Main splitter for horizontal sections
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setHandleWidth(10)
        main_splitter.setStyleSheet("QSplitter::handle { background-color: #E0E0E0; border-radius: 5px; }")

        # Section 1: Create Product
        main_splitter.addWidget(self.create_product_section("Create New Product"))

        # Section 2: Create Package
        main_splitter.addWidget(self.create_package_section("Create New Package"))

        # Section 3: Send Package
        main_splitter.addWidget(self.create_send_section("Send a Package"))

        main_splitter.setSizes([self.width() // 2, self.width() // 1, self.width() // 2])
        main_layout.addWidget(main_splitter)
        main_layout.addStretch()

    def create_product_section(self, name):
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                font-color: black;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #E0E0E0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
            QLabel {
                font-size: 16px;
                color: #333;
            }
        """)
        layout = QVBoxLayout(section)
        layout.setSpacing(15)

        title = QLabel(name)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #333333;font-color:black")
        layout.addWidget(title)
        layout.addStretch()

        add_product_btn = QPushButton("Launch Product Creation")
        add_product_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 25px;
                font-weight: bold;
                font-size: 16px;
                box-shadow: 0 4px 10px rgba(76, 175, 80, 0.2);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #5247D6;
                transform: translateY(-2px);
            }
        """)
        add_product_btn.clicked.connect(lambda: show_product_creation_popup(self))

        layout.addWidget(add_product_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        return section
    def clear_package_rows(self):
        while self.package_items_layout.count():
            item = self.package_items_layout.takeAt(0)
            if item.layout():
                child_layout = item.layout()
                while child_layout.count():
                    sub_item = child_layout.takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
                child_layout.deleteLater()
            elif item.widget():
                item.widget().deleteLater()
        self.package_input_rows.clear()

    def create_package_section(self, name):
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #E0E0E0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
            QLabel {
                font-size: 16px;
                color: #333;
            }
        """)
        layout = QVBoxLayout(section)
        layout.setSpacing(15)

        title = QLabel(name)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #333333;")
        layout.addWidget(title)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        package_items_widget = QWidget()
        self.package_items_layout = QVBoxLayout(package_items_widget)
        self.package_items_layout.setContentsMargins(0,0,0,0) # Remove margin for compact list
        self.package_items_layout.setSpacing(8) # Spacing between product rows
        scroll_area.setWidget(package_items_widget)
        layout.addWidget(scroll_area)
        package_items_widget.setStyleSheet("""
            QWidget {
                background-color: #F9F9F9;
                border-radius: 8px;
                padding: 10px;
            }
            QScrollArea {
                border: none;
            }
        """)

        add_product_row_btn = QPushButton("Add Product to Package")
        add_product_row_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-weight: bold;
                font-size: 14px;
                box-shadow: 0 2px 8px rgba(255, 152, 0, 0.2);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #5247D6;
                transform: translateY(-1px);
            }
        """)
        add_product_row_btn.clicked.connect(self.add_product_to_package_row)
        layout.addWidget(add_product_row_btn)

        create_package_btn = QPushButton("Create Package")
        create_package_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 25px;
                font-weight: bold;
                font-size: 16px;
                box-shadow: 0 4px 10px rgba(33, 150, 243, 0.2);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #5247D6;;
                transform: translateY(-2px);
            }
        """)
        create_package_btn.clicked.connect(self.create_package)
        layout.addWidget(create_package_btn)

        layout.addStretch()
        return section

    def add_product_to_package_row(self):
        row = ProductInputRow(produits_db, self.remove_product_row)
        self.package_items_layout.addLayout(row)
        self.package_input_rows.append(row)

    def remove_product_row(self, row_layout):
        self.package_input_rows = [r for r in self.package_input_rows if r != row_layout]
        # The row_layout's widgets are already removed by ProductInputRow's _on_remove_clicked

    def create_package(self):
        if not self.package_input_rows:
            QMessageBox.warning(self, "No Products", "Please add at least one product to the package.")
            return

        package_contents = []
        for row_layout in self.package_input_rows:
            lot = row_layout.get_selected_product()
            if lot:
                package_contents.append(lot)
            else:
                QMessageBox.warning(self, "Invalid Product", "Please select a product for all rows.")
                return

        if not package_contents:
            QMessageBox.warning(self, "No Products", "No valid products selected for the package.")
            return

        dialog = NameInputDialog()
        package_name = dialog.get_name()
        if not package_name:
            return
        while package_name in names:
            QMessageBox.information(
            self,
            "ERROR",
            f"The package name {package_name} is already existent" 
            )
            dialog = NameInputDialog()
            package_name = dialog.get_name()
        names.append(package_name)
        added_packages[package_name] = package_contents


            # Update the package combo box in the 'Send a Package' section
        send_widget = self.parent().findChild(ClientLogisticsWidget, "clientLogisticsWidget")
        if send_widget and hasattr(send_widget, 'package_to_send_combo'): # Corrected attribute name
            send_widget.package_to_send_combo.addItem(package_name)

        QMessageBox.information(
            self,
            "Package Created",
            f"Package '{package_name}' created successfully with:\n" + "\n".join([str(lot) for lot in package_contents])
        )

            # Clear the package creation rows after successful creation
        self.clear_package_rows()


    def create_send_section(self, name):
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 5px;
                padding: 15px;
                border: 1px solid #E0E0E0;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            }
            QLabel {
                font-size: 16px;
                color: #333;
            }
            QLineEdit, QComboBox {
                padding: 15px;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                font-size: 15px;
                background-color: white;
            }
        """)
        layout = QVBoxLayout(section)
        layout.setSpacing(15)

        title = QLabel(name)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color:#333333;")
        layout.addWidget(title)

        form = QGridLayout()
        self.transporting_org_combo = QComboBox()
        self.receiving_org_combo = QComboBox()
        for org in orgs:
            self.transporting_org_combo.addItem(org[1], org[0])
            self.receiving_org_combo.addItem(org[1], org[0])

        self.package_to_send_combo = QComboBox()
        self.package_to_send_combo.addItem("— Select a package —", None)
        # Populate with existing packages from DB
        for i, pkg in added_packages.items():
            self.package_to_send_combo.addItem(i)  # pkg = nom visible, i = ID

        form.addWidget(QLabel("Receiving Org:"), 0, 0)
        form.addWidget(self.receiving_org_combo, 0, 1)
        form.addWidget(QLabel("Choose a Package:"), 1, 0)
        form.addWidget(self.package_to_send_combo, 1, 1)
        layout.addLayout(form)

        # Apply styling to combos
        combo_style = """
            QComboBox {
                background-color: #F0F2F5;
                color: #333;
                border: 1px solid #D0D0D0;
                border-radius: 6px;
                padding: 10px 10px;
                font-weight: normal;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down.png);
                width: 12px;
                height: 12px;
            }
        """
        self.transporting_org_combo.setStyleSheet(combo_style)
        self.receiving_org_combo.setStyleSheet(combo_style)
        self.package_to_send_combo.setStyleSheet(combo_style)

        send_btn = QPushButton("Send Package")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 25px;
                font-weight: bold;
                font-size: 16px;
                box-shadow: 0 4px 10px rgba(108, 99, 255, 0.2);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #5247D6;
                transform: translateY(-2px);
            }
        """)
        send_btn.clicked.connect(self.send_package)

        layout.addWidget(send_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        return section


    def send_package(self):
        receive_org_id = self.receiving_org_combo.currentData()
        package_id = self.package_to_send_combo.currentText()  # key from added_packages is the name, not the ID
        lots = added_packages.get(package_id)
    
        if not lots:
            QMessageBox.warning(self, "Missing", "No lots found for selected package.")
            return
    
        for lot in lots:
            try:
                cur.execute(
                    'CALL "EMIR".PLot_INS(%s, %s, %s, %s, %s)',
                    (
                        idgenerator.generate_id('^PL[A-Z0-9]{5}$', lotids),
                        lot.id,                         # _idproduit
                        str(lot.quantity),              # _quantite
                        datetime.date.today().isoformat(),  # _date_creation
                        "envoyé"                        # _statut
                    )
                )
            except psycopg2.Error as e:
                conn.rollback()
                QMessageBox.critical(self, "Database Error", f"Failed to send lot: {e}")
                return
    
        try:
            cur.execute('CALL "EMIR".PC_INS(%s, %s, %s, %s)',
                (
                    idgenerator.generate_id("^BE[0-9]{4}$", []),  # Dummy ID for BonExpedition
                    datetime.date.today().isoformat(),
                    receive_org_id,
                    package_id
                )
            )
            conn.commit()
            QMessageBox.information(
                self,
                "Success",
                f"Package '{package_id}' sent successfully from {self.transporting_org_combo.currentText()} to {self.receiving_org_combo.currentText()}."
            )
        except psycopg2.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to insert BonExpedition: {e}")

class ClientOrderManagementWidget(QWidget):
    """Widget for managing client orders."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        header_layout = QHBoxLayout()
        title = QLabel("My Orders")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #6C63FF;")

        refresh_btn = QPushButton("Refresh Orders")
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
        # refresh_btn.clicked.connect(self.refresh_orders) # Implement refresh logic if needed

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        pending_orders = len([o for o in self.data.client_orders if o['Status'] == 'Pending'])
        in_transit_orders = len([o for o in self.data.client_orders if o['Status'] == 'Shipped' or o['Status'] == 'Processing'])
        delivered_orders = len([o for o in self.data.client_orders if o['Status'] == 'Delivered'])

        stats_layout.addWidget(self.create_stat_card("Pending Orders", pending_orders, "#FFC107"))
        stats_layout.addWidget(self.create_stat_card("In Transit", in_transit_orders, "#2196F3"))
        stats_layout.addWidget(self.create_stat_card("Delivered", delivered_orders, "#4CAF50"))
        layout.addLayout(stats_layout)

        sections_splitter = QSplitter(Qt.Orientation.Horizontal)
        sections_splitter.setHandleWidth(10)
        sections_splitter.setStyleSheet("QSplitter::handle { background-color: #E0E0E0; border-radius: 10px; }")

        recent_orders_section = self.create_order_section("Recent Orders",
            sorted(self.data.client_orders, key=lambda x: x['Order_Date'], reverse=True)[:10]) # Show most recent orders
        sections_splitter.addWidget(recent_orders_section)

        pending_orders_section = self.create_order_section("Orders to Action",
            [o for o in self.data.client_orders if o['Status'] == 'Pending' or o['Status'] == 'Processing'])
        sections_splitter.addWidget(pending_orders_section)

        sections_splitter.setSizes([self.width() // 2, self.width() // 2])
        layout.addWidget(sections_splitter)

        self.setLayout(layout)

    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setFrameShadow(QFrame.Shadow.Raised)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: "#FFFFFF";
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

    def create_order_section(self, title, orders):
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

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333; margin-bottom: 5px;")
        layout.addWidget(title_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMaximumHeight(600)

        order_widget = QWidget()
        order_layout = QVBoxLayout(order_widget)
        order_layout.setSpacing(10)

        if orders:
            for order in orders:
                order_card = ClientTaskCard(order)
                order_card.order_selected.connect(self.on_order_selected)
                order_layout.addWidget(order_card)
        else:
            no_orders_label = QLabel("No orders available in this section.")
            no_orders_label.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
            order_layout.addWidget(no_orders_label)

        order_layout.addStretch()
        scroll_area.setWidget(order_widget)
        layout.addWidget(scroll_area)
        section.setLayout(layout)
        return section

    def on_order_selected(self, order_data):
        dialog = OrderDetailsDialog(order_data, self)
        dialog.exec()

class ShipmentTrackingWidget(QWidget):
    """Widget for tracking client's shipments."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        header_layout = QHBoxLayout()
        title = QLabel("Shipment Tracking")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color:#6C63FF;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        filter_search_layout = QHBoxLayout()
        filter_search_layout.setSpacing(15)

        search_label = QLabel("Search Package:")
        search_label.setStyleSheet("font-size: 15px; color: #FFFFFF;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter package ID or product name...")
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
        self.type_combo.addItems(['All', 'Outbound', 'In Transit', 'Received', 'Return'])
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
        """)
        self.type_combo.currentTextChanged.connect(self.filter_movements)

        filter_search_layout.addWidget(search_label)
        filter_search_layout.addWidget(self.search_input, 3)
        filter_search_layout.addWidget(type_label)
        filter_search_layout.addWidget(self.type_combo, 1)
        filter_search_layout.addStretch()

        layout.addLayout(filter_search_layout)

        self.movements_table = self.create_movements_table()
        layout.addWidget(self.movements_table)

        self.setLayout(layout)
        self.update_movements_table(self.data.movement_history) # Initial population

    def create_movements_table(self):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['Timestamp', 'Package ID', 'Type', 'Location', 'Description'])

        table.verticalHeader().setDefaultSectionSize(40)

        table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                font-size: 14px;
                selection-background-color: #E6E6FF;
                selection-color: #333333;
                gridline-color: #F0F2F5;
            }
            QHeaderView::section {
                background-color: #6C63FF;
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
                color: #FFFFFF;
            }
        """)

        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.resizeColumnsToContents()

        return table

    def filter_movements(self):
        search_text = self.search_input.text().lower()
        movement_type = self.type_combo.currentText()

        filtered_movements = []
        for movement in self.data.movement_history:
            if search_text and search_text not in movement['Package_ID'].lower() and search_text not in movement['Product_Name'].lower():
                continue
            if movement_type != 'All' and movement['Movement_Type'] != movement_type:
                continue
            filtered_movements.append(movement)

        self.update_movements_table(filtered_movements)

    def update_movements_table(self, movements):
        sorted_movements = sorted(movements, key=lambda x: x['Timestamp'], reverse=True)
        self.movements_table.setRowCount(len(sorted_movements))

        accent_color = "#6C63FF"

        for i, movement in enumerate(sorted_movements):
            self.movements_table.setItem(i, 0, QTableWidgetItem(movement['Timestamp'].strftime('%H:%M %b %d')))
            self.movements_table.setItem(i, 1, QTableWidgetItem(movement['Package_ID']))

            type_item = QTableWidgetItem(movement['Movement_Type'])
            type_item.setBackground(QColor(accent_color))
            type_item.setForeground(QColor('#FFFFFF'))
            self.movements_table.setItem(i, 2, type_item)

            self.movements_table.setItem(i, 3, QTableWidgetItem(movement['Location']))
            self.movements_table.setItem(i, 4, QTableWidgetItem(movement['Description']))

        self.movements_table.resizeColumnsToContents()


class InquiryDetailDialog(QDialog):
    """Dialog to display details of an inquiry and allow status update."""
    def __init__(self, inquiry_data, parent=None):
        super().__init__(parent)
        self.inquiry_data = inquiry_data
        self.setWindowTitle(f"Inquiry Details: {self.inquiry_data['ID']}")
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
                padding: 20px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }
            QTextEdit:focus, QComboBox:focus {
                border: 1px solid #F44336;
            }
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #5247D6;
            }
        """)

        title_label = QLabel(f"Inquiry: {self.inquiry_data['ID']}")
        title_label.setProperty("class", "title")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.addRow("Type:", QLabel(self.inquiry_data['Type']))
        form_layout.addRow("Related Product:", QLabel(self.inquiry_data['Related_Product']))
        form_layout.addRow("Reported By:", QLabel(self.inquiry_data['Reported_By_Org']))
        form_layout.addRow("Reported Time:", QLabel(self.inquiry_data['Reported_Time'].strftime('%Y-%m-%d %H:%M')))

        description_label = QLabel("Description:")
        layout.addWidget(description_label)
        description_text = QTextEdit()
        description_text.setText(self.inquiry_data['Description'])
        description_text.setReadOnly(True)
        layout.addWidget(description_text)

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Update Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(['Open', 'In Progress', 'Resolved', 'Closed'])
        self.status_combo.setCurrentText(self.inquiry_data['Status'])
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save Status")
        save_button.clicked.connect(self.save_status)
        button_layout.addWidget(save_button)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #6C63FF;")
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def save_status(self):
        new_status = self.status_combo.currentText()
        if new_status != self.inquiry_data['Status']:
            # In a real app, this would update the database
            self.inquiry_data['Status'] = new_status # Update in-memory data
            QMessageBox.information(self, "Status Updated", f"Inquiry {self.inquiry_data['ID']} status updated to {new_status}.")
            self.accept()
        else:
            self.accept()

class NewInquiryDialog(QDialog):
    """Dialog to report a new inquiry."""
    def __init__(self, data, client_id, parent=None):
        super().__init__(parent)
        self.data = data
        self.client_id = client_id
        self.setWindowTitle("Report New Inquiry")
        self.setFixedSize(450, 500)
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
                border: 1px solid #F44336;
            }
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #5247D6;
            }
        """)

        self.inquiry_type_combo = QComboBox()
        self.inquiry_type_combo.addItems(['Missing Package', 'Damaged Item', 'Incorrect Order', 'Billing Issue', 'General Support', 'Other'])
        layout.addRow("Inquiry Type:", self.inquiry_type_combo)

        self.related_product_combo = QComboBox()
        self.related_product_combo.addItem("— None (General Inquiry) —", None)
        for product in self.data.products_df.itertuples():
            self.related_product_combo.addItem(product.Name, product.ID)
        layout.addRow("Related Product:", self.related_product_combo)

        description_label = QLabel("Description:")
        layout.addWidget(description_label)
        self.description_text = QTextEdit()
        self.description_text.setPlaceholderText("Provide detailed information about your inquiry...")
        layout.addWidget(self.description_text)

        button_layout = QHBoxLayout()
        report_button = QPushButton("Submit Inquiry")
        report_button.clicked.connect(self.report_inquiry)
        button_layout.addWidget(report_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("background-color: #CCCCCC;")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addChildLayout(button_layout)
        self.setLayout(layout)

    def report_inquiry(self):
        inquiry_type = self.inquiry_type_combo.currentText()
        related_product_id = self.related_product_combo.currentData()
        related_product_name = self.related_product_combo.currentText() if related_product_id else "N/A"
        description = self.description_text.toPlainText()

        if not description:
            QMessageBox.warning(self, "Input Error", "Please provide a detailed description for your inquiry.")
            return

        new_inquiry = {
            'ID': f'INQ{len(self.data.inquiries) + 1:03d}',
            'Type': inquiry_type,
            'Related_Product': related_product_name,
            'Reported_By_Org': self.client_id,
            'Reported_Time': datetime.datetime.now(),
            'Status': 'Open',
            'Description': description
        }
        self.data.inquiries.append(new_inquiry) # Add to in-memory list
        QMessageBox.information(self, "Success", "Inquiry reported successfully!")
        self.accept()

class ClientInquiriesWidget(QWidget):
    """Widget for viewing and managing client inquiries."""

    def __init__(self, data, client_id):
        super().__init__()
        self.data = data
        self.client_id = client_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        header_layout = QHBoxLayout()
        title = QLabel("My Inquiries")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #6C63FF;")

        report_inquiry_btn = QPushButton("Submit New Inquiry")
        report_inquiry_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C63FF;
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
                background-color: #5247D6;
                transform: translateY(-2px);
            }
        """)
        report_inquiry_btn.clicked.connect(self.report_new_inquiry)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(report_inquiry_btn)
        layout.addLayout(header_layout)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        open_inquiries = len([i for i in self.data.inquiries if i['Status'] == 'Open'])
        in_progress_inquiries = len([i for i in self.data.inquiries if i['Status'] == 'In Progress'])
        resolved_inquiries = len([i for i in self.data.inquiries if i['Status'] == 'Resolved' or i['Status'] == 'Closed'])

        stats_layout.addWidget(self.create_inquiry_stat_card("Open Inquiries", open_inquiries, "#F44336"))
        stats_layout.addWidget(self.create_inquiry_stat_card("In Progress", in_progress_inquiries, "#FFC107"))
        stats_layout.addWidget(self.create_inquiry_stat_card("Resolved/Closed", resolved_inquiries, "#4CAF50"))
        layout.addLayout(stats_layout)

        self.inquiries_table = self.create_inquiries_table()
        layout.addWidget(self.inquiries_table)

        self.setLayout(layout)
        self.update_inquiries_table(self.data.inquiries) # Initial population

    def create_inquiry_stat_card(self, title, value, color):
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

    def create_inquiries_table(self):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['ID', 'Type', 'Related Product', 'Time', 'Status'])
    
    # Set header visibility BEFORE styling
        table.horizontalHeader().setVisible(True)
        table.horizontalHeader().setMinimumHeight(45)  # Ensure header has proper height
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(40)

        table.setStyleSheet("""
        QTableWidget {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 10px;
            font-size: 14px;
            selection-background-color: #FFEBEE;
            selection-color: #333333;
            gridline-color: #F0F2F5;
        }
        QHeaderView::section {
            background-color: #6C63FF;
            color: #FFFFFF;
            padding: 12px;
            border: none;
            font-weight: bold;
            font-size: 15px;
            text-align: left;
            height: 90px;
            min-height: 45px;
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
            background-color: #FFEBEE;
            color: #333333;
        }
    """)

        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.cellDoubleClicked.connect(self.view_inquiry_details)
    
    # Remove the test row - it's not needed and might interfere
    # The table will be populated by update_inquiries_table()
    
        return table

    def update_inquiries_table(self, inquiries):
        sorted_inquiries = sorted(inquiries, key=lambda x: x['Reported_Time'], reverse=True)
        self.inquiries_table.setRowCount(len(sorted_inquiries))

        for i, inquiry in enumerate(sorted_inquiries):
            self.inquiries_table.setItem(i, 0, QTableWidgetItem(inquiry['ID']))
            self.inquiries_table.setItem(i, 1, QTableWidgetItem(inquiry['Type']))
            self.inquiries_table.setItem(i, 2, QTableWidgetItem(inquiry['Related_Product']))
            self.inquiries_table.setItem(i, 3, QTableWidgetItem(inquiry['Reported_Time'].strftime('%m/%d %H:%M')))

            status_item = QTableWidgetItem(inquiry['Status'])
            status_colors = {
                'Open': '#F44336',
                'In Progress': '#FFC107',
                'Resolved': '#4CAF50',
                'Closed': '#9E9E9E' # Grey for closed
            }
            status_item.setBackground(QColor(status_colors.get(inquiry['Status'], '#E0E0E0')))
            status_item.setForeground(QColor('#FFFFFF'))
            if inquiry['Status'] == 'In Progress':
                status_item.setForeground(QColor('#333333'))
            self.inquiries_table.setItem(i, 4, status_item)
        self.inquiries_table.resizeColumnsToContents()


    def view_inquiry_details(self, row, column):
        inquiry_id = self.inquiries_table.item(row, 0).text()
        inquiry_data = next((i for i in self.data.inquiries if i['ID'] == inquiry_id), None)

        if inquiry_data:
            dialog = InquiryDetailDialog(inquiry_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.update_inquiries_table(self.data.inquiries) # Refresh table if status changed

    def report_new_inquiry(self):
        dialog = NewInquiryDialog(self.data, self.client_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update_inquiries_table(self.data.inquiries)
            
class HelpWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        from helpbot import ChatBot
        
        # --- Card 1: AI Assistant Placeholder --
        ai_card = QFrame()
        ai_card.setStyleSheet("""
            QFrame {
                background-color: #F8F0FA;
                border-radius: 16px;
                border: 1px solid #E0E0E0
                padding: 20px;
                box-shadow: 0 4px 5px rgba(108,99,255,0.07)
            }
        """)
        ai_layout = QVBoxLayout(ai_card)
        ai_title = QLabel("🤖 AI Assistant ")
        ai_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #6C63FF;")
        ai_desc = QLabel("An Intelligent assistant that will answer all your questions about the platform.")
        ai_desc.setWordWrap(True)
        ai_desc.setStyleSheet("font-size: 18px; color:#333")
        ai_btn = QPushButton("Ask your questions")
        ai_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C63FF;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #5247D6;;
            }
        """)
        ai_btn.clicked.connect(self.open_helpbot_dialog)  # Placeholder for AI chat functionality
        ai_layout.addWidget(ai_title)
        ai_layout.addWidget(ai_desc)
        ai_layout.addWidget(ai_btn)
        ai_layout.addWidget(ai_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        ai_layout.addStretch()
        
        # --- Card 2: Report a Bug ---
        bug_card = QFrame()
        ai_card.setStyleSheet("""
            QFrame {
                background-color: #F8F0FA;
                border-radius: 16px;
                border: 1px solid #E0E0E0
                padding: 20px;
                box-shadow: 0 4px 5px rgba(108,99,255,0.07)
            }
        """)
        bug_layout= QVBoxLayout(bug_card)
        bug_title = QLabel("🐞 Report a Bug")
        bug_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF9800;")
        bug_desc = QLabel("If you encounter a problem or bug, please let our IT support know so we can fix it quickly.")
        bug_desc.setWordWrap(True)
        bug_desc.setStyleSheet("font-size: 18px; color: #333;")
        report_btn = QPushButton("Report a Bug")
        report_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 12x 20px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        report_btn.clicked.connect(self.open_bug_report_dialog)
        bug_layout.addWidget(bug_title)
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
        self.setStyleSheet(""""
            QDialog{
                background-color: #FFFDE7;
                border-radius: 12px;
            }
            QLabel {
                font-size: 16px;
                color: #333px;
            }
            QTextEdit {
                border: 1px solid #FFD180;
                border-radius: 8px;
                font-size: 15px;
                background-color: #FFFFFF;
            }
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 8px;
                padding: 10 24px;
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
        support_email = "steevy.tongoue@2029.ucac-icam.com"
        subject = "Bug Report from Client Dashboard"
        body = bug_text

        try:
            
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            smtp_user = "scarobotinterne@gmail.com"
            smtp_password = "vzeokmezwltpoqbt"

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = smtp_user
            msg["To"] = support_email

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, [support_email], msg.as_string())

            QMessageBox.information(self, "Sent", "Your bug report has been sent to IT support. Thank you!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send bug report.\n\n{e}")


        

class ClientMainDashboard(QWidget):
    """Main dashboard widget for clients."""

    def __init__(self, data, main_window):
        super().__init__()
        self.data = data
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        hero_frame = QFrame()
        hero_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6C63FF, stop:1 #00BFA5);
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

        welcome_label = QLabel(f"Welcome, Client Organization {self.data.client_id}!")
        welcome_label.setStyleSheet("font-size: 32px; font-weight: bold;")

        time_label = QLabel(f"Today: {datetime.datetime.now().strftime('%A, %B %d, %Y')}")
        time_label.setStyleSheet("font-size: 16px; margin-top: 5px;")

        hero_layout.addWidget(welcome_label)
        hero_layout.addWidget(time_label)
        hero_layout.addStretch()

        dashboard_stats_layout = QHBoxLayout()
        dashboard_stats_layout.setSpacing(20)

        total_orders = len(self.data.client_orders)
        in_transit = len([o for o in self.data.client_orders if o['Status'] == 'Shipped' or o['Status'] == 'Processing'])
        delivered_today = len([o for o in self.data.client_orders if o['Status'] == 'Delivered' and (datetime.datetime.now() - o['Order_Date']).total_seconds() < 86400]) # Last 24 hours
        open_inquiries = len([i for i in self.data.inquiries if i['Status'] == 'Open'])

        dashboard_stats_layout.addWidget(self.create_dashboard_card("Total Orders", total_orders, "#FFC107", "All orders placed"))
        dashboard_stats_layout.addWidget(self.create_dashboard_card("In Transit", in_transit, "#2196F3", "Orders currently in shipment"))
        dashboard_stats_layout.addWidget(self.create_dashboard_card("Delivered Today", delivered_today, "#4CAF50", "Orders delivered in last 24h"))
        dashboard_stats_layout.addWidget(self.create_dashboard_card("Open Inquiries", open_inquiries, "#F44336", "Issues requiring attention"))

        hero_layout.addLayout(dashboard_stats_layout)
        layout.addWidget(hero_frame)

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
                color: #6C63FF;
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
                color: #333333;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #6C63FF;
                color: #FFFFFF;
                transform: translateY(-2px);
            }
        """

        view_orders_btn = QPushButton("View My Orders")
        view_orders_btn.setStyleSheet(button_style)
        view_orders_btn.clicked.connect(lambda: self.main_window.navigate_to_widget(self.main_window.order_management_widget))

        manage_logistics_btn = QPushButton("Manage Products/Packages")
        manage_logistics_btn.setStyleSheet(button_style)
        manage_logistics_btn.clicked.connect(lambda: self.main_window.navigate_to_widget(self.main_window.client_logistics_widget))

        submit_inquiry_btn = QPushButton("Submit an Inquiry")
        submit_inquiry_btn.setStyleSheet(button_style)
        submit_inquiry_btn.clicked.connect(lambda: self.main_window.navigate_to_widget(self.main_window.client_inquiries_widget))

        quick_actions_layout.addWidget(view_orders_btn)
        quick_actions_layout.addWidget(manage_logistics_btn)
        quick_actions_layout.addWidget(submit_inquiry_btn)
        quick_actions_group.setLayout(quick_actions_layout)
        layout.addWidget(quick_actions_group)

        recent_activity_group = QGroupBox("Recent Shipment Activities")
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
                color: #00BFA5;
            }
        """)
        recent_activity_layout = QVBoxLayout()
        recent_activity_layout.setContentsMargins(20, 25, 20, 20)
        recent_activity_layout.setSpacing(10)

        latest_movements = sorted(self.data.movement_history, key=lambda x: x['Timestamp'], reverse=True)[:5]
        if latest_movements:
            for movement in latest_movements:
                activity_label = QLabel(f"<span style='font-weight:bold;'>{movement['Timestamp'].strftime('%H:%M')}</span> | Package <span style='font-weight:bold;'>{movement['Package_ID']}</span>: {movement['Movement_Type']} at {movement['Location']}")
                activity_label.setStyleSheet("font-size: 14px; color: #444; padding: 2px 0;")
                activity_label.setTextFormat(Qt.TextFormat.RichText)
                recent_activity_layout.addWidget(activity_label)
        else:
            no_activity_label = QLabel("No recent shipment activities to display.")
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
        layout.addStretch()

        card.setLayout(layout)
        return card

class ClientMainWindow(QMainWindow):
    """Main application window for the client dashboard."""
    def __init__(self):
        super().__init__()
        self.data = ClientData(client_org_id) # Pass client_org_id
        self.setWindowTitle("Client Logistics Dashboard")
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
            QLabel, QGroupBox, QTableWidget, QLineEdit, QComboBox, QPushButton, QTextEdit, QSpinBox, QListWidget, QRadioButton, QDoubleSpinBox {
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
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 6px;
                padding: 8px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #6C63FF;
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
                color: #666666;
                padding: 10px 20px;
                font-size: 14x;
                font-weight: 500;
                border-radius: 3px;
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

        logo_label = QLabel("Client Dashboard")
        logo_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #6C63FF;
            margin-right: 30px;
        """)
        navbar_layout.addWidget(logo_label)

        self.dashboard_btn = QPushButton("Dashboard")
        self.order_management_btn = QPushButton("My Orders")
        self.shipment_tracking_btn = QPushButton("Shipment Tracking")
        self.client_logistics_btn = QPushButton("Logistics") # For product/package management
        self.client_inquiries_btn = QPushButton("My Inquiries")
        self.help_btn = QPushButton("Help")

        self.dashboard_btn.setCheckable(True)
        self.order_management_btn.setCheckable(True)
        self.shipment_tracking_btn.setCheckable(True)
        self.client_logistics_btn.setCheckable(True)
        self.client_inquiries_btn.setCheckable(True)
        self.help_btn.setCheckable(True)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.dashboard_btn)
        self.button_group.addButton(self.order_management_btn)
        self.button_group.addButton(self.shipment_tracking_btn)
        self.button_group.addButton(self.client_logistics_btn)
        self.button_group.addButton(self.client_inquiries_btn)
        self.button_group.addButton(self.help_btn)

        self.dashboard_btn.clicked.connect(lambda: self.navigate_to_widget(self.dashboard_widget))
        self.order_management_btn.clicked.connect(lambda: self.navigate_to_widget(self.order_management_widget))
        self.shipment_tracking_btn.clicked.connect(lambda: self.navigate_to_widget(self.shipment_tracking_widget))
        self.client_logistics_btn.clicked.connect(lambda: self.navigate_to_widget(self.client_logistics_widget))
        self.client_inquiries_btn.clicked.connect(lambda: self.navigate_to_widget(self.client_inquiries_widget))
        self.help_btn.clicked.connect(lambda: self.navigate_to_widget(self.help_widget))

        navbar_layout.addStretch()
        navbar_layout.addWidget(self.dashboard_btn)
        navbar_layout.addWidget(self.order_management_btn)
        navbar_layout.addWidget(self.shipment_tracking_btn)
        navbar_layout.addWidget(self.client_logistics_btn)
        navbar_layout.addWidget(self.client_inquiries_btn)
        navbar_layout.addWidget(self.help_btn)  
        navbar_layout.addStretch()

        self.main_layout.addWidget(self.navbar)

    def create_content_area(self):
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #F0F2F5; padding: 30px;")
        

        def scrollable(widget, object_name=None):
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(widget)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            if object_name:
                widget.setObjectName(object_name) # Set object name on the widget inside scroll
            return scroll

        self.dashboard_widget = scrollable(ClientMainDashboard(self.data, self))
        self.order_management_widget = scrollable(ClientOrderManagementWidget(self.data))
        self.shipment_tracking_widget = scrollable(ShipmentTrackingWidget(self.data))
        self.client_logistics_widget = scrollable(ClientLogisticsWidget(self.data), object_name="clientLogisticsWidget") # Add object_name
        self.client_inquiries_widget = scrollable(ClientInquiriesWidget(self.data, client_org_id))
        self.help_widget = HelpWidget()

        self.content_stack.addWidget(self.dashboard_widget)
        self.content_stack.addWidget(self.order_management_widget)
        self.content_stack.addWidget(self.shipment_tracking_widget)
        self.content_stack.addWidget(self.client_logistics_widget)
        self.content_stack.addWidget(self.client_inquiries_widget)
        self.content_stack.addWidget(self.help_widget)

        self.main_layout.addWidget(self.content_stack)

    def navigate_to_widget(self, target_widget):
        self.content_stack.setCurrentWidget(target_widget)
        for button in self.button_group.buttons():
            button.setChecked(False)

        if target_widget == self.dashboard_widget:
            self.dashboard_btn.setChecked(True)
        elif target_widget == self.order_management_widget:
            self.order_management_btn.setChecked(True)
        elif target_widget == self.shipment_tracking_widget:
            self.shipment_tracking_btn.setChecked(True)
        elif target_widget == self.client_logistics_widget:
            self.client_logistics_btn.setChecked(True)
        elif target_widget == self.client_inquiries_widget:
            self.client_inquiries_btn.setChecked(True)
        elif target_widget == self.help_widget:
            self.help_btn.setChecked(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # ...existing code...
    

# Set QMessageBox text color to black
    
# ...existing code...

    # High-contrast, accessible palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f5f5f5"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#333333"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f0f0f0"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Text, QColor("#333333"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#e0e0e0"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#333333"))
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor("#2196F3"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2196F3"))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    
    app.setPalette(palette)
    app.setStyleSheet("""
    QMessageBox QLabel {
    color: black;
    font-size: 14px;
    font-family: 'Segoe UI', 'Arial', sans-serif;
        }
    """)


    app.setFont(QFont("Segoe UI", 10))

    client_main_window = ClientMainWindow()
    client_main_window.showMaximized()
    sys.exit(app.exec())
