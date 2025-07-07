
import sys, os

import numpy as np
import pandas as pd
from matplotlib.figure import Figure

# Consolidated PyQt6.QtWidgets imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QCheckBox, QFrame, QScrollArea,
    QSizePolicy, QSpacerItem, QGridLayout, QMessageBox, QComboBox, QStackedWidget,
    QTableWidgetItem, QTableWidget, QHeaderView, QTextEdit, QSplitter, QSpinBox,
    QAbstractItemView, QGroupBox, QListWidget, QListWidgetItem, QRadioButton,
    QDoubleSpinBox, QButtonGroup, QDialog, QGraphicsDropShadowEffect, # Ensure QGraphicsDropShadowEffect is here
    QStyle
)

# Consolidated PyQt6.QtCore imports
from PyQt6.QtCore import (
    Qt, QDate, QTimer, pyqtSignal, QSize,
    QPropertyAnimation, QEasingCurve
)

# Consolidated PyQt6.QtGui imports
from PyQt6.QtGui import (
    QColor, QFont, QPalette, QPixmap, QPainter # Ensure QColor is here
)

import datetime
import random
import psycopg2
from id import idgenerator
from helpbot import ChatBot
import send_sca_mail
import internalmail



class DatabaseSelectionDialog(QDialog):
    """
    Dialogue permettant à l'utilisateur de choisir entre la base de données en ligne ou hors ligne.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Selection")
        self.setFixedSize(350, 180)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.selected_db = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Choose your database connection:")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2D3748;
            }
        """)
        main_layout.addWidget(title_label)

        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(20)
        radio_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.online_radio = QRadioButton("Online Database")
        self.offline_radio = QRadioButton("Offline Database")

        radio_style = """
            QRadioButton {
                font-size: 15px;
                color: #555555;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
            }
            QRadioButton::indicator:checked {
                background-color: #006775;
                border: 2px solid #006775;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #BBBBBB;
                background-color: #F8F9FA;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #4A5568;
            }
        """
        self.online_radio.setStyleSheet(radio_style)
        self.offline_radio.setStyleSheet(radio_style)

        self.online_radio.setChecked(True)

        radio_layout.addWidget(self.online_radio)
        radio_layout.addWidget(self.offline_radio)
        main_layout.addLayout(radio_layout)

        confirm_button = QPushButton("Connect")
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #006775;
                color: white;
                border: none;
                padding: 10px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                margin-top: 10px;
                box-shadow: 0 4px 13px rgba(108, 99, 255, 0.25);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #004F5C;
                box-shadow: 0 6px 16px rgba(108, 99, 255, 0.35);
            }
            QPushButton:pressed {
                background-color: #00454F;
                box-shadow: none;
            }
        """)
        confirm_button.clicked.connect(self.accept_selection)
        main_layout.addWidget(confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

        self.setStyleSheet("""
                           
            QDialog {
                background-color: #FFFFFF;
                border-radius: 13px;
                border: 1px solid #D3DCE0;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            }
        """)

    def accept_selection(self):
        if self.online_radio.isChecked():
            self.selected_db = '1'
        elif self.offline_radio.isChecked():
            self.selected_db = '2'
        self.accept()
# Global organization ID for the client currently logged in
# In a real application, this would come from a login system
client_org_id = 'OFIRST' # Example client organization ID

# --- START OF BACKEND/DATABASE INITIALIZATION (DO NOT TOUCH) ---

app_for_dialog = QApplication(sys.argv) # Créez une instance de QApplication pour le dialogue
db_dialog = DatabaseSelectionDialog()
if db_dialog.exec() == QDialog.DialogCode.Accepted:
    selected_db_choice = db_dialog.selected_db
else:

    sys.exit("Database selection cancelled. Exiting application.")
app_for_dialog = None 

global conn
if selected_db_choice == '1':
    print("You have chosen the online database.")
    conn = psycopg2.connect(
        host="dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com",
        database="projet_integrateur",
        user="group13",
        password="nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3",
        port=5432
    )
elif selected_db_choice == '2':
    print("You have chosen the offline database.")
    conn = psycopg2.connect(
        host="localhost",
        database="projet",
        user="postgres",
        password="postgres",
        port=5432
    )
else:
    # Cela ne devrait pas arriver si le dialogue fonctionne comme prévu
    sys.exit("Invalid database selection. Exiting.")

cur = conn.cursor()


# --- FIN DE LA LOGIQUE DE SÉLECTION DE LA DB AMÉLIORÉE ---

# Fetch initial data for product, lot, and package IDs to ensure uniqueness
# These queries fetch existing data from the database at startup.
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

cur.execute("SELECT (p).* FROM \"EMIR\".inquiries_eva(%s) AS p;",(client_org_id,))
inq_db = cur.fetchall() # Existing products from the database

# Global lists to keep track of generated IDs for uniqueness checks
# Populated with existing IDs from the database to prevent collisions.
productids = [l[0] for l in produits_db]
lotids = [l[0] for l in lots_db] # Assuming colis_db contains lot IDs, this might need adjustment
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
        self.colis_df = pd.DataFrame(colis_db,columns=['id','date_cre','expected_date','receiving_org','statut'])
        self.contenu_df = pd.DataFrame(contenu,columns=['idcol','idlot','quantity','date_maj'])
        self.inq_df = pd.DataFrame(inq_db,columns=['id','type','period','status','description'])

        #my_pending_tasks = len([t for t in self.data.expedition_tasks.to_dict('records') if  t['status'] == 'en cours'])
        # Client Orders (adapted from expedition tasks)
        self.client_orders = []

        order_statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
        for i in self.colis_df.itertuples():
            cur.execute("SELECT \"EMIR\".getvaluecol(%s,%s);",(client_org_id,i.id))
            total = cur.fetchone()[0]
            items = [t for t in self.contenu_df.to_dict('records') if t['idcol'] == i.id]
            it = Colis(i.id,i.statut,items,i.date_cre, datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 10)),client_org_id,total)
            

            self.client_orders.append({
                'Order_ID': it.idcolis,
                'Status': it.statut,
                'Items_Count': len(it.items),
                'Order_Date': it.orderdate,
                'Estimated_Delivery': it.estimated_delivery,
                'Customer_Org_ID': it.customerid,
                'Items': it.items, # Store raw product data
                'Total_Value': it.totalvaule
            })
        

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
        for i in self.inq_df.itertuples():
            self.inquiries.append({
                'ID': i.id,
                'Type': i.type,
                'Reported_By_Org': client_org_id,
                'Reported_Time': i.period,
                'Status': i.status,
                'Description':i.description
            })
        
        # Filter inquiries for the current client
        self.inquiries = [inq for inq in self.inquiries if inq['Reported_By_Org'] == self.client_id]

# REMPLACER l'intégralité de la classe OrderCard() par celle-ci
# REMPLACER l'intégralité de la classe OrderCard par celle-ci
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect # Assurez-vous d'avoir QGraphicsDropShadowEffect ici
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor # Assurez-vous d'avoir QColor ici

class OrderCard(QFrame):
    """Card widget for displaying individual client orders with enhanced styling."""

    order_selected = pyqtSignal(dict)

    def __init__(self, order_data):
        super().__init__()
        self.order_data = order_data
        self.init_ui()

    def init_ui(self):
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFixedHeight(120)
        self.setContentsMargins(0, 0, 0, 0)

        # Applique le style de base de la carte (sans box-shadow ici)
        self.setStyleSheet("""
            OrderCard {
                background-color: #FFFFFF;
                border-radius: 13px;
                border: none;
                margin: 8px 0;
                padding: 0;
            }
        """)

        # Crée et applique l'effet d'ombre portée
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(25) # Intensité du flou de l'ombre
        self.shadow_effect.setColor(QColor(0, 0, 0, 60)) # Couleur de l'ombre (RGBA: 60 = 23% d'opacité)
        self.shadow_effect.setXOffset(0) # Décalage horizontal
        self.shadow_effect.setYOffset(8) # Décalage vertical
        self.setGraphicsEffect(self.shadow_effect)

        # Pour les animations de survol, vous pouvez utiliser QPropertyAnimation
        self.hover_animation = QPropertyAnimation(self.shadow_effect, b"blurRadius")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.shadow_color_animation = QPropertyAnimation(self.shadow_effect, b"color")
        self.shadow_color_animation.setDuration(200)
        self.shadow_color_animation.setEasingCurve(QEasingCurve.Type.OutQuad)


        status_color = self.get_status_color(self.order_data.get('Status', 'Pending'))

        accent_bar = QFrame(self)
        accent_bar.setFixedWidth(6)
        accent_bar.setStyleSheet(f"background-color: {status_color}; border-top-left-radius: 13px; border-bottom-left-radius: 13px;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(accent_bar)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(25)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        header_row = QHBoxLayout()
        order_label = QLabel(self.order_data['Order_ID'])
        order_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #2C3E50;")
        header_row.addWidget(order_label)
        header_row.addStretch()

        status_label = QLabel(self.order_data['Status'])
        status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {status_color};
                color: #FFFFFF;
                border-radius: 13px;
                font-size: 13px;
                font-weight: bold;
                padding: 4px 13px;
                min-width: 80px;
                text-align: center;
            }}
        """)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_row.addWidget(status_label)
        info_layout.addLayout(header_row)

        details_text = f"Items: <b>{self.order_data['Items_Count']}</b> &nbsp; | &nbsp; Value: <b>${self.order_data['Total_Value']:.2f}</b>"
        due_text = f"Expected Delivery: <b>{self.order_data['Estimated_Delivery'].strftime('%Y-%m-%d')}</b>"

        details_label = QLabel(details_text)
        details_label.setStyleSheet("font-size: 14px; color: #555555;")
        details_label.setTextFormat(Qt.TextFormat.RichText)
        due_label = QLabel(due_text)
        due_label.setStyleSheet("font-size: 13px; color: #7F8C8D;")
        due_label.setTextFormat(Qt.TextFormat.RichText)

        info_layout.addWidget(details_label)
        info_layout.addWidget(due_label)
        info_layout.addStretch()

        action_btn = QPushButton("View Details")
        action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        action_btn.setStyleSheet("""
            QPushButton {
                background-color: #006775;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                color: #FFFFFF;
                box-shadow: 0 2px 8px rgba(108, 99, 255, 0.2); /* Garde un petit shadow ici si vous voulez */
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #004F5C;
                box-shadow: 0 4px 13px rgba(108, 99, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: #00454F;
                box-shadow: none;
            }
        """)
        action_btn.clicked.connect(self.on_action_clicked)

        content_layout.addLayout(info_layout, stretch=3)
        content_layout.addWidget(action_btn, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def get_status_color(self, status):
        colors = {
            'Pending': "#F6AD55",
            'Processing': "#17A2B8",
            'Shipped': "#007BFF",
            'Delivered': "#28A745",
            'Cancelled': "#DC3545",
        }
        return colors.get(status, '#4A5568')

    def enterEvent(self, event):
        # Animation au survol
        self.hover_animation.setStartValue(self.shadow_effect.blurRadius())
        self.hover_animation.setEndValue(35) # Ombre plus floue
        self.hover_animation.start()

        start_color = self.shadow_effect.color()
        end_color = QColor(0, 0, 0, 90) # Ombre plus foncée
        self.shadow_color_animation.setStartValue(start_color)
        self.shadow_color_animation.setEndValue(end_color)
        self.shadow_color_animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        # Animation au départ du survol
        self.hover_animation.setStartValue(self.shadow_effect.blurRadius())
        self.hover_animation.setEndValue(25) # Revenir à l'ombre de base
        self.hover_animation.start()

        start_color = self.shadow_effect.color()
        end_color = QColor(0, 0, 0, 60) # Revenir à la couleur de base
        self.shadow_color_animation.setStartValue(start_color)
        self.shadow_color_animation.setEndValue(end_color)
        self.shadow_color_animation.start()

        super().leaveEvent(event)

    def on_action_clicked(self):
        self.order_selected.emit(self.order_data)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.order_selected.emit(self.order_data)
# REMPLACER l'intégralité de la classe OrderDetailsDialog par celle-ci
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget,
    QFormLayout, QFrame, QGridLayout, QGraphicsDropShadowEffect # Assurez-vous d'avoir QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize # Assurez-vous d'avoir QSize
from PyQt6.QtGui import QColor # Assurez-vous d'avoir QColor

# REMPLACER l'intégralité de la classe OrderDetailsDialog par celle-ci
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget,
    QFormLayout, QFrame, QGridLayout, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor

class OrderDetailsDialog(QDialog):
    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.setWindowTitle(f"Order Details: {order_data['Order_ID']}")
        
        # REMOVED: self.setFixedSize(700, 750)
        # ADDED: Set a minimum size and allow resizing
        self.setMinimumSize(600, 700) # Minimum size (adjust as needed)
        self.resize(750, 800) # Initial size, but now resizable

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border-radius: 15px;
                border: 1px solid #D3DCE0;
            }
            QLabel {
                color: #2D3748;
                font-size: 14px;
            }
            QLabel.title {
                font-size: 20px;
                font-weight: bold;
                color: #2C3E50;
                margin-bottom: 10px;
            }
            QLabel.value {
                font-weight: 600;
                color: #555555;
            }
            /* ScrollBar styling (already present, ensuring consistency) */
            QScrollBar:vertical {
                border: none;
                background: #EDF2F7;
                width: 10px;
                margin: 0px;
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

        header_frame = QFrame(self)
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #006775;
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                padding: 15px 25px;
            }
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 0, 25, 0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        header_title = QLabel(f"Order Details: {self.order_data['Order_ID']}")
        header_title.setObjectName("title")
        header_layout.addWidget(header_title)
        main_layout.addWidget(header_frame)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; }") # Override potential default borders

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 25, 30, 25)
        content_layout.setSpacing(25)

        # --- Section Order Information ---
        order_info_group = self.create_section_card("Order Information")
        # Ensure layout for this group stretches
        order_info_layout = QFormLayout(order_info_group)
        order_info_layout.setContentsMargins(20, 20, 20, 20)
        order_info_layout.setSpacing(10)
        order_info_layout.addRow(self.create_label_pair("Client Name:", self.order_data.get('Client_Name', 'N/A')))
        order_info_layout.addRow(self.create_label_pair("Order Date:", self.order_data.get('Order_Date', 'N/A').strftime('%Y-%m-%d')))
        order_info_layout.addRow(self.create_label_pair("Expected Delivery:", self.order_data.get('Estimated_Delivery', 'N/A').strftime('%Y-%m-%d')))
        order_info_layout.addRow(self.create_label_pair("Status:", self.order_data.get('Status', 'N/A')))
        order_info_layout.addRow(self.create_label_pair("Total Value:", f"${self.order_data.get('Total_Value', 0.0):.2f}"))
        content_layout.addWidget(order_info_group)
        content_layout.setStretchFactor(order_info_group, 0) # Don't stretch this group vertically, let its content define size

        # --- Section Package Details ---
        package_details_group = self.create_section_card("Package Details")
        package_details_layout = QVBoxLayout(package_details_group)
        package_details_layout.setContentsMargins(20, 20, 20, 20)
        package_details_layout.setSpacing(10)
        # Added a QWidget to hold package frames, allowing it to stretch
        packages_container = QWidget()
        packages_layout = QVBoxLayout(packages_container)
        packages_layout.setContentsMargins(0,0,0,0) # No extra margins for internal container
        packages_layout.setSpacing(10)

        for package in self.order_data.get('Packages', []):
            package_frame = QFrame()
            package_frame.setStyleSheet("""
                QFrame {
                    background-color: #EDF2F7;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 0px; /* Managed by layout spacing */
                }
            """)
            package_layout = QFormLayout(package_frame)
            package_layout.setSpacing(5)
            package_layout.addRow(self.create_label_pair("Package ID:", package.get('Package_ID', 'N/A')))
            package_layout.addRow(self.create_label_pair("Weight:", f"{package.get('Weight_kg', 0.0):.2f} kg"))
            package_layout.addRow(self.create_label_pair("Dimensions:", f"{package.get('Dimensions_cm', 'N/A')} cm"))
            packages_layout.addWidget(package_frame)
        if not self.order_data.get('Packages'):
            packages_layout.addWidget(QLabel("No packages associated with this order."))
        
        packages_layout.addStretch(1) # Stretch in package container if content is less
        package_details_layout.addWidget(packages_container) # Add container to group layout
        content_layout.addWidget(package_details_group)
        content_layout.setStretchFactor(package_details_group, 1) # This group can stretch if needed

        # --- Section Product Details ---
        product_details_group = self.create_section_card("Product Details")
        product_details_layout = QVBoxLayout(product_details_group)
        product_details_layout.setContentsMargins(20, 20, 20, 20)
        product_details_layout.setSpacing(10)
        # Added a QWidget to hold product frames, allowing it to stretch
        products_container = QWidget()
        products_layout = QVBoxLayout(products_container)
        products_layout.setContentsMargins(0,0,0,0) # No extra margins for internal container
        products_layout.setSpacing(10)

        for product in self.order_data.get('Products', []):
            product_frame = QFrame()
            product_frame.setStyleSheet("""
                QFrame {
                    background-color: #EDF2F7;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 0px; /* Managed by layout spacing */
                }
            """)
            product_layout = QFormLayout(product_frame)
            product_layout.setSpacing(5)
            product_layout.addRow(self.create_label_pair("Product Name:", product.get('Product_Name', 'N/A')))
            product_layout.addRow(self.create_label_pair("Quantity:", str(product.get('Quantity', 'N/A'))))
            product_layout.addRow(self.create_label_pair("Unit Price:", f"${product.get('Unit_Price', 0.0):.2f}"))
            products_layout.addWidget(product_frame)
        if not self.order_data.get('Products'):
            products_layout.addWidget(QLabel("No products associated with this order."))
        
        products_layout.addStretch(1) # Stretch in product container if content is less
        product_details_layout.addWidget(products_container) # Add container to group layout
        content_layout.addWidget(product_details_group)
        content_layout.setStretchFactor(product_details_group, 1) # This group can stretch if needed

        content_layout.addStretch(1) # Ensure overall content fills space if all groups are small

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #006775;
                color: white;
                border: none;
                padding: 13px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                margin: 15px 25px;
                box-shadow: 0 4px 13px rgba(108, 99, 255, 0.25);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #004F5C;
                box-shadow: 0 6px 16px rgba(108, 99, 255, 0.35);
            }
            QPushButton:pressed {
                background-color: #00454F;
                box-shadow: none;
            }
        """)
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def create_label_pair(self, label_text, value_text):
        h_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: 500; color: #555555;")
        value = QLabel(str(value_text))
        value.setStyleSheet("font-weight: 600; color: #2D3748;")
        h_layout.addWidget(label)
        h_layout.addStretch()
        h_layout.addWidget(value)
        return h_layout

    def create_section_card(self, title_text):
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #EEEEEE;
            }
            QLabel.section_title {
                font-size: 18px;
                font-weight: bold;
                color: #2C3E50;
                margin-bottom: 10px;
            }
        """)
        shadow_effect = QGraphicsDropShadowEffect(card_frame)
        shadow_effect.setBlurRadius(15)
        shadow_effect.setColor(QColor(0, 0, 0, 30))
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(5)
        card_frame.setGraphicsEffect(shadow_effect)

        layout = QVBoxLayout(card_frame)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel(title_text)
        title_label.setObjectName("section_title")
        layout.addWidget(title_label)
        layout.addSpacing(10)

        return card_frame


# REMPLACER l'intégralité de la classe ProductCreationPopup1 par celle-ci
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton,
    QLineEdit, QDoubleSpinBox, QComboBox, QTextEdit, QScrollArea, QWidget,
    QRadioButton, QButtonGroup, QMessageBox, QGraphicsDropShadowEffect # Assurez-vous d'avoir QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize # Assurez-vous d'avoir QSize
from PyQt6.QtGui import QColor # Assurez-vous d'avoir QColor

class ProductCreationPopup1(QDialog): # C'est la classe que nous allons modifier
    """Dialog to create a new product (physical or software) with enhanced UI."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Product")
        
        # Rendre le dialogue redimensionnable avec une taille minimale
        self.setMinimumSize(800, 600) # Taille minimale raisonnable
        self.resize(1000, 700) # Taille initiale plus grande, mais redimensionnable
        
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint) # Retire le bouton d'aide

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0) # Marges gérées par les sous-layouts
        self.main_layout.setSpacing(0)

        # Appliquer un style global au dialogue
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA; /* Arrière-plan doux */
                border-radius: 15px;
                border: 1px solid #D3DCE0;
            }
            QLabel {
                color: #2D3748;
                font-weight: 500; /* Moins gras pour les labels normaux */
                font-size: 14px;
            }
            QLabel.dialog_title { /* Titre du dialogue */
                font-size: 24px;
                font-weight: bold;
                color: #2D3748;
                margin-bottom: 15px;
            }
            QLineEdit, QDoubleSpinBox, QComboBox, QTextEdit {
                color: #232946;
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 8px; /* Plus arrondis */
                padding: 10px 13px; /* Padding généreux pour la hauteur et l'espace */
                min-height: 38px; /* Hauteur minimale pour les champs */
            }
            QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #006775; /* Bordure d'accentuation au focus */
                box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.2); /* Ombre au focus */
            }
            QTextEdit {
                min-height: 80px; /* Hauteur minimale pour les zones de texte */
            }
            QRadioButton {
                font-size: 15px;
                color: #555555;
                padding: 5px 0; /* Padding pour les radios */
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
            }
            QRadioButton::indicator:checked {
                background-color: #006775;
                border: 2px solid #006775;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #BBBBBB;
                background-color: #F8F9FA;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #4A5568;
            }
            QPushButton {
                background-color: #006775; /* Couleur principale pour les boutons d'action */
                color: white;
                border: none;
                padding: 13px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                box-shadow: 0 4px 13px rgba(108, 99, 255, 0.25);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #004F5C;
                box-shadow: 0 6px 16px rgba(108, 99, 255, 0.35);
            }
            QPushButton:pressed {
                background-color: #00454F;
                box-shadow: none;
            }
            QPushButton#cancelButton { /* Style spécifique pour un bouton Annuler */
                background-color: #D3DCE0;
                color: #2D3748;
                box-shadow: none;
            }
            QPushButton#cancelButton:hover {
                background-color: #D0D0D0;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #E8EBF0;
                width: 10px;
                margin: 0px;
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

        # En-tête du dialogue
        header_frame = QFrame(self)
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #006775; /* Couleur d'accentuation */
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                padding: 15px 25px;
            }
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 0, 25, 0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        header_title = QLabel("Create New Product")
        header_layout.addWidget(header_title)
        self.main_layout.addWidget(header_frame)

        # Zone de contenu défilable
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.scroll_content_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_layout.setContentsMargins(30, 25, 30, 25) # Marges internes pour le contenu
        self.scroll_layout.setSpacing(20) # Espacement entre les éléments du formulaire

        self.scroll_area.setWidget(self.scroll_content_widget)
        self.main_layout.addWidget(self.scroll_area, stretch=1) # Permet au contenu de s'étirer

        self.step = 1
        self.product_type = None
        self.build_step_1()

        # Boutons de navigation en bas du dialogue
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(30, 15, 30, 15) # Marges pour les boutons
        self.button_layout.setSpacing(15)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_btn)
        
        self.button_layout.addStretch() # Pousse les boutons à droite

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.goto_step_2)
        self.button_layout.addWidget(self.next_btn)

        self.submit_btn = QPushButton("Create Product")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745; /* Vert pour l'action de création */
                color: white;
                border: none;
                padding: 13px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                box-shadow: 0 4px 13px rgba(40, 167, 69, 0.25);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #218838;
                box-shadow: 0 6px 16px rgba(40, 167, 69, 0.35);
            }
            QPushButton:pressed {
                background-color: #1E7E34;
                box-shadow: none;
            }
        """)
        self.submit_btn.clicked.connect(self.submit_product)
        self.submit_btn.hide() # Caché par défaut, affiché à l'étape 2

        self.main_layout.addLayout(self.button_layout)


    def build_step_1(self):
        self.clear_scroll_layout() # Nettoie le layout de la zone de défilement

        title_label = QLabel("Select Product Type")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50; margin-bottom: 15px;")
        self.scroll_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        radio_group_layout = QVBoxLayout()
        radio_group_layout.setSpacing(15)
        radio_group_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.physical_radio = QRadioButton("Physical Product (Material)")
        self.software_radio = QRadioButton("Software Product (Digital License)")
        
        # Assurez-vous que les styles des radios sont appliqués ici aussi
        radio_style = """
            QRadioButton {
                font-size: 16px;
                color: #2D3748;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 20px; /* Taille de l'indicateur */
                height: 20px;
                border-radius: 10px; /* Rend l'indicateur rond */
            }
            QRadioButton::indicator:checked {
                background-color: #006775;
                border: 3px solid #006775;
            }
            QRadioButton::indicator:unchecked {
                border: 3px solid #BBBBBB;
                background-color: #F8F9FA;
            }
            QRadioButton::indicator:hover {
                border: 3px solid #4A5568;
            }
        """
        self.physical_radio.setStyleSheet(radio_style)
        self.software_radio.setStyleSheet(radio_style)


        self.physical_radio.setChecked(True) # Option par défaut

        radio_group_layout.addWidget(self.physical_radio)
        radio_group_layout.addWidget(self.software_radio)
        
        # Centrer le groupe de radios
        center_widget = QWidget()
        center_layout = QHBoxLayout(center_widget)
        center_layout.addStretch()
        center_layout.addLayout(radio_group_layout)
        center_layout.addStretch()
        self.scroll_layout.addWidget(center_widget)


        self.scroll_layout.addStretch() # Pousse les éléments vers le haut

        self.next_btn.show()
        self.submit_btn.hide()
        self.button_layout.removeWidget(self.submit_btn) # S'assurer qu'il n'est pas là
        self.button_layout.addWidget(self.next_btn) # S'assurer qu'il est là


    def goto_step_2(self):
        if self.physical_radio.isChecked():
            self.product_type = "physical"
        elif self.software_radio.isChecked():
            self.product_type = "software"
        else:
            QMessageBox.warning(self, "Error", "Please select a product type.")
            return

        self.clear_scroll_layout() # Nettoie le layout de la zone de défilement

        title_label = QLabel(f"Enter {self.product_type.capitalize()} Product Details")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50; margin-bottom: 15px;")
        self.scroll_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setVerticalSpacing(15) # Espacement vertical entre les lignes du formulaire
        form_layout.setHorizontalSpacing(20) # Espacement horizontal entre label et champ

        # Initialisation des champs de saisie
        self.name_input = QLineEdit()
        self.prix_unitaire = QDoubleSpinBox()
        self.prix_unitaire.setSuffix(" $")
        self.prix_unitaire.setRange(0.0, 1000000.0) # Augmenter la plage max
        self.prix_unitaire.setDecimals(2) # 2 décimales pour les prix

        self.marque = QLineEdit()
        self.description = QTextEdit()
        self.modele = QLineEdit()

        self.fournisseur = QComboBox()
        # Assurez-vous que 'orgs' est accessible ici (variable globale ou passée en paramètre)
        # Si 'orgs' n'est pas global, vous devrez le passer au constructeur du popup
        try:
            if 'orgs' in globals(): # Vérifier si 'orgs' est une variable globale
                for org in orgs:
                    self.fournisseur.addItem(org[1], org[0]) # Display name, store ID
            else:
                self.fournisseur.addItem("Default Supplier", "DEFAULT_ORG_ID") # Fallback
                QMessageBox.warning(self, "Data Warning", "Supplier data 'orgs' not found. Using dummy data.")
        except NameError:
             self.fournisseur.addItem("Default Supplier", "DEFAULT_ORG_ID") # Fallback
             QMessageBox.warning(self, "Data Warning", "Supplier data 'orgs' not found. Using dummy data.")


        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Supplier:", self.fournisseur)
        form_layout.addRow("Description:", self.description)
        form_layout.addRow("Unit Price:", self.prix_unitaire)
        form_layout.addRow("Brand:", self.marque)
        form_layout.addRow("Model:", self.modele)

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
            ho.setSpacing(15) # Espacement entre les radios
            ho.addWidget(self.categorie1)
            ho.addWidget(self.categorie2)
            ho.addWidget(self.categorie3)
            ho.addStretch() # Pousse les radios à gauche

            self.length_input = QDoubleSpinBox()
            self.length_input.setSuffix(" cm")
            self.length_input.setRange(0.0, 1000.0)
            self.length_input.setValue(10.0)
            self.length_input.setDecimals(2)

            self.width_input = QDoubleSpinBox()
            self.width_input.setSuffix(" cm")
            self.width_input.setRange(0.0, 1000.0)
            self.width_input.setValue(10.0)
            self.width_input.setDecimals(2)

            self.height_input = QDoubleSpinBox()
            self.height_input.setSuffix(" cm")
            self.height_input.setRange(0.0, 1000.0)
            self.height_input.setValue(10.0)
            self.height_input.setDecimals(2)

            self.mass_input = QDoubleSpinBox()
            self.mass_input.setSuffix(" kg")
            self.mass_input.setRange(0.0, 1000.0)
            self.mass_input.setValue(10.0)
            self.mass_input.setDecimals(2)

            form_layout.addRow("Category:", ho)
            form_layout.addRow("Length:", self.length_input)
            form_layout.addRow("Width:", self.width_input)
            form_layout.addRow("Height:", self.height_input)
            form_layout.addRow("Mass:", self.mass_input)
        else: # Software product
            self.version_input = QLineEdit()
            self.license_input = QLineEdit()

            form_layout.addRow("Version:", self.version_input)
            form_layout.addRow("License Key:", self.license_input)
            self.category_text = "Software"

        # Centrer le formulaire dans le scroll_layout
        form_container_widget = QWidget()
        form_container_widget.setLayout(form_layout)
        
        center_form_layout = QHBoxLayout()
        center_form_layout.addStretch()
        center_form_layout.addWidget(form_container_widget)
        center_form_layout.addStretch()
        
        self.scroll_layout.addLayout(center_form_layout)
        self.scroll_layout.addStretch() # Pousse le formulaire vers le haut

        # Gestion des boutons de navigation
        self.next_btn.hide()
        self.button_layout.removeWidget(self.next_btn) # S'assurer qu'il est retiré
        self.button_layout.addWidget(self.submit_btn) # Ajouter le bouton de soumission
        self.submit_btn.show()

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

        # Assurez-vous que 'cur' et 'conn' sont accessibles ici (variables globales ou passées en paramètre)
        # Si 'cur' et 'conn' ne sont pas globaux, vous devrez les passer au constructeur du popup
        try:
            if 'cur' in globals() and 'conn' in globals():
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
            else:
                QMessageBox.critical(self, "Database Error", "Database connection (cur, conn) not found. Cannot save product.")
                # Pour le test visuel, on peut accepter même sans DB si vous voulez
                # self.accept() 
        except psycopg2.Error as e:
            if 'conn' in globals():
                conn.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to create product: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")


    def clear_scroll_layout(self):
        """Efface tous les widgets et layouts du layout de défilement."""
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Pour les layouts imbriqués, il faut aussi les nettoyer récursivement
                self.clear_nested_layout(item.layout())
                item.layout().deleteLater()

    def clear_nested_layout(self, layout):
        """Fonction utilitaire pour nettoyer un layout imbriqué."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_nested_layout(item.layout())
                item.layout().deleteLater()


def show_product_creation_popup(parent=None):
    dialog = ProductCreationPopup1(parent) # Assurez-vous que c'est bien ProductCreationPopup1
    dialog.exec()

class ProductInputRow(QHBoxLayout):
    """A row for product selection and quantity in package creation."""
    def __init__(self, products_data, remove_callback):
        super().__init__()
        self.products_data = products_data
        self.remove_callback = remove_callback

        self.product_combo = QComboBox()
        self.product_combo.setFixedWidth(150)
        self.product_combo.addItem("— Select a product —", None)
        self.product_combo.setStyleSheet("background-color: 5472AE")
        for p in self.products_data:
            self.product_combo.addItem(p[2], p[0]) # Display name, store ID

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 1000)
        self.qty_spin.setValue(1)

        self.remove_btn = QPushButton("X")
        self.remove_btn.setFixedSize(34, 34)
        self.remove_btn.setStyleSheet("color: red; font-weight: bold; border-radius: 13px; background-color: #FFEBEE;")
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
class ProductCreationPopup(QDialog):
    """Dialog to create a new product (physical or software) with enhanced UI."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Product")
        
        # Rendre le dialogue redimensionnable avec une taille minimale
        self.setMinimumSize(800, 600) # Taille minimale raisonnable
        self.resize(1000, 700) # Taille initiale plus grande, mais redimensionnable
        
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint) # Retire le bouton d'aide

        self.main_layout = QVBoxLayout(self) # Renamed from self.layout for clarity
        self.main_layout.setContentsMargins(0, 0, 0, 0) # Marges gérées par les sous-layouts
        self.main_layout.setSpacing(0)

        # Appliquer un style global au dialogue
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA; /* Arrière-plan doux */
                border-radius: 15px;
                border: 1px solid #D3DCE0;
            }
            QLabel {
                color: #2D3748;
                font-weight: 500; /* Moins gras pour les labels normaux */
                font-size: 14px;
            }
            QLabel.dialog_title { /* Titre du dialogue */
                font-size: 24px;
                font-weight: bold;
                color: #2D3748;
                margin-bottom: 15px;
            }
            QLineEdit, QDoubleSpinBox, QComboBox, QTextEdit, QSpinBox { /* Added QSpinBox */
                color: #232946;
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 8px; /* Plus arrondis */
                padding: 10px 13px; /* Padding généreux pour la hauteur et l'espace */
                min-height: 38px; /* Hauteur minimale pour les champs */
            }
            QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus, QTextEdit:focus, QSpinBox:focus { /* Added QSpinBox */
                border: 1px solid #006775; /* Bordure d'accentuation au focus */
                box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.2); /* Ombre au focus */
            }
            QTextEdit {
                min-height: 80px; /* Hauteur minimale pour les zones de texte */
            }
            QRadioButton {
                font-size: 15px;
                color: #555555;
                padding: 5px 0; /* Padding pour les radios */
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
            }
            QRadioButton::indicator:checked {
                background-color: #006775;
                border: 2px solid #006775;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #BBBBBB;
                background-color: #F8F9FA;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #4A5568;
            }
            QPushButton {
                background-color: #006775; /* Couleur principale pour les boutons d'action */
                color: white;
                border: none;
                padding: 13px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                box-shadow: 0 4px 13px rgba(108, 99, 255, 0.25);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #004F5C;
                box-shadow: 0 6px 16px rgba(108, 99, 255, 0.35);
            }
            QPushButton:pressed {
                background-color: #00454F;
                box-shadow: none;
            }
            QPushButton#cancelButton { /* Style spécifique pour un bouton Annuler */
                background-color: #D3DCE0;
                color: #2D3748;
                box-shadow: none;
            }
            QPushButton#cancelButton:hover {
                background-color: #D0D0D0;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #E8EBF0;
                width: 10px;
                margin: 0px;
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

        # En-tête du dialogue
        header_frame = QFrame(self)
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #006775; /* Couleur d'accentuation */
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                padding: 15px 25px;
            }
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 0, 25, 0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        header_title = QLabel("Create New Product")
        header_layout.addWidget(header_title)
        self.main_layout.addWidget(header_frame)

        # Zone de contenu défilable
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.scroll_content_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_layout.setContentsMargins(30, 25, 30, 25) # Marges internes pour le contenu
        self.scroll_layout.setSpacing(20) # Espacement entre les éléments du formulaire

        self.scroll_area.setWidget(self.scroll_content_widget)
        self.main_layout.addWidget(self.scroll_area, stretch=1) # Permet au contenu de s'étirer

        self.step = 1
        self.product_type = None
        self.produitid = None # Initialize produitid here, will be generated in goto_step_2
        self.product_data_saved_successfully = None # To store data on successful creation
        self.build_step_1()

        # Boutons de navigation en bas du dialogue
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(30, 15, 30, 15) # Marges pour les boutons
        self.button_layout.setSpacing(15)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_btn)
        
        self.button_layout.addStretch() # Pousse les boutons à droite

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.goto_step_2)
        self.button_layout.addWidget(self.next_btn)

        self.submit_btn = QPushButton("Create Product")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745; /* Vert pour l'action de création */
                color: white;
                border: none;
                padding: 13px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                box-shadow: 0 4px 13px rgba(40, 167, 69, 0.25);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #218838;
                box-shadow: 0 6px 16px rgba(40, 167, 69, 0.35);
            }
            QPushButton:pressed {
                background-color: #1E7E34;
                box-shadow: none;
            }
        """)
        self.submit_btn.clicked.connect(self.submit_product)
        self.submit_btn.hide() # Caché par défaut, affiché à l'étape 2

        self.main_layout.addLayout(self.button_layout)


    def build_step_1(self):
        self.clear_scroll_layout() # Nettoie le layout de la zone de défilement

        title_label = QLabel("Select Product Type")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50; margin-bottom: 15px;")
        self.scroll_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        radio_group_layout = QVBoxLayout()
        radio_group_layout.setSpacing(15)
        radio_group_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.physical_radio = QRadioButton("Physical Product (Material)")
        self.software_radio = QRadioButton("Software Product (Digital License)")
        
        # Assurez-vous que les styles des radios sont appliqués ici aussi
        radio_style = """
            QRadioButton {
                font-size: 16px;
                color: #2D3748;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 20px; /* Taille de l'indicateur */
                height: 20px;
                border-radius: 10px; /* Rend l'indicateur rond */
            }
            QRadioButton::indicator:checked {
                background-color: #006775;
                border: 3px solid #006775;
            }
            QRadioButton::indicator:unchecked {
                border: 3px solid #BBBBBB;
                background-color: #F8F9FA;
            }
            QRadioButton::indicator:hover {
                border: 3px solid #4A5568;
            }
        """
        self.physical_radio.setStyleSheet(radio_style)
        self.software_radio.setStyleSheet(radio_style)

        # Use a QButtonGroup to manage radio button selection
        self.product_type_group = QButtonGroup(self)
        self.product_type_group.addButton(self.physical_radio)
        self.product_type_group.addButton(self.software_radio)

        self.physical_radio.setChecked(True) # Option par défaut

        radio_group_layout.addWidget(self.physical_radio)
        radio_group_layout.addWidget(self.software_radio)
        
        # Centrer le groupe de radios
        center_widget = QWidget()
        center_layout = QHBoxLayout(center_widget)
        center_layout.addStretch()
        center_layout.addLayout(radio_group_layout)
        center_layout.addStretch()
        self.scroll_layout.addWidget(center_widget)


        self.scroll_layout.addStretch() # Pousse les éléments vers le haut

        self.next_btn.show()
        self.submit_btn.hide()
        # Ensure only one of next/submit is in the layout at a time
        if self.button_layout.indexOf(self.submit_btn) != -1:
            self.button_layout.removeWidget(self.submit_btn)
        if self.button_layout.indexOf(self.next_btn) == -1:
            self.button_layout.addWidget(self.next_btn)


    def goto_step_2(self):
        if self.physical_radio.isChecked():
            self.product_type = "physical"
        elif self.software_radio.isChecked():
            self.product_type = "software"
        else:
            QMessageBox.warning(self, "Error", "Please select a product type.")
            return

        self.clear_scroll_layout() # Nettoie le layout de la zone de défilement

        title_label = QLabel(f"Enter {self.product_type.capitalize()} Product Details")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50; margin-bottom: 15px;")
        self.scroll_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setVerticalSpacing(15) # Espacement vertical entre les lignes du formulaire
        form_layout.setHorizontalSpacing(20) # Espacement horizontal entre label et champ

        # Initialisation des champs de saisie
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Gaming Laptop, Office Chair")

        self.prix_unitaire = QDoubleSpinBox()
        self.prix_unitaire.setSuffix(" $")
        self.prix_unitaire.setRange(0.0, 1000000.0) # Augmenter la plage max
        self.prix_unitaire.setDecimals(2) # 2 décimales pour les prix

        self.marque = QLineEdit()
        self.marque.setPlaceholderText("e.g., Dell, IKEA")

        self.description = QTextEdit()
        self.description.setPlaceholderText("A detailed description of the product...")

        self.modele = QLineEdit()
        self.modele.setPlaceholderText("e.g., XPS 15, Markus")

        self.fournisseur = QComboBox()
        self.fournisseur.addItem("Select Supplier", None) # Add a default "Select" item
        # Ensure 'orgs' is accessible here (global variable)
        try:
            if 'orgs' in globals() and isinstance(orgs, list): # Check if 'orgs' is a global variable
                for org_id, org_name in orgs:
                    self.fournisseur.addItem(org_name, org_id) # Display name, store ID
            else:
                QMessageBox.warning(self, "Data Warning", "Supplier data 'orgs' not found or is not a list. Using dummy data.")
        except NameError:
            QMessageBox.warning(self, "Data Warning", "Supplier data 'orgs' not found. Using dummy data.")
        
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Supplier:", self.fournisseur)
        form_layout.addRow("Description:", self.description)
        form_layout.addRow("Unit Price:", self.prix_unitaire)
        form_layout.addRow("Brand:", self.marque)
        form_layout.addRow("Model:", self.modele)

        if self.product_type == "physical":
            self.categorie_group = QButtonGroup(self)
            self.categorie1 = QRadioButton("Packaging")
            self.categorie2 = QRadioButton("Electronic")
            self.categorie3 = QRadioButton("Non-Electronic")
            self.categorie_group.addButton(self.categorie1)
            self.categorie_group.addButton(self.categorie2)
            self.categorie_group.addButton(self.categorie3)
            self.categorie1.setChecked(True)
            self.category_text = "Packaging" # Default category
            # Connect to update category_text, remove spaces for consistency (e.g., in DB)
            self.categorie_group.buttonClicked.connect(lambda btn: setattr(self, 'category_text', btn.text().replace(" ", ""))) 
            
            self.length_input = QDoubleSpinBox()
            self.length_input.setSuffix(" cm")
            self.length_input.setRange(0.0, 1000.0)
            self.length_input.setValue(10.0)
            self.length_input.setDecimals(2)

            self.width_input = QDoubleSpinBox()
            self.width_input.setSuffix(" cm")
            self.width_input.setRange(0.0, 1000.0)
            self.width_input.setValue(10.0)
            self.width_input.setDecimals(2)

            self.height_input = QDoubleSpinBox()
            self.height_input.setSuffix(" cm")
            self.height_input.setRange(0.0, 1000.0)
            self.height_input.setValue(10.0)
            self.height_input.setDecimals(2)

            self.mass_input = QDoubleSpinBox()
            self.mass_input.setSuffix(" kg")
            self.mass_input.setRange(0.0, 1000.0)
            self.mass_input.setValue(10.0)
            self.mass_input.setDecimals(2)

            ho = QHBoxLayout()
            ho.addWidget(self.categorie1)
            ho.addWidget(self.categorie2)
            ho.addWidget(self.categorie3)
            ho.addStretch()

            form_layout.addRow("Category:", ho)
            form_layout.addRow("Length:", self.length_input)
            form_layout.addRow("Width:", self.width_input)
            form_layout.addRow("Height:", self.height_input)
            form_layout.addRow("Mass:", self.mass_input)
        else: # Software product
            self.version_input = QLineEdit()
            self.version_input.setPlaceholderText("e.g., 1.0.0, 2024.1")
            self.license_input = QLineEdit()
            self.license_input.setPlaceholderText("e.g., Perpetual, Subscription")

            form_layout.addRow("Version:", self.version_input)
            form_layout.addRow("License Type:", self.license_input)
            self.category_text = "Software" # Hardcoded category for software

        # Generate product ID here, as per your original structure
        # Ensure 'idgenerator' and 'productids' (as a set) are global
        if 'idgenerator' not in globals() or 'productids' not in globals():
            QMessageBox.critical(self, "Error", "IDGenerator or productids not found in global scope. Cannot generate product ID.")
            self.reject() # Close dialog if critical dependency is missing
            return
        
        try:
            # Assumes idgenerator.generate_id takes pattern and a set of existing IDs
            self.produitid = idgenerator.generate_id("^PROD[A-Z0-9]{5}$", productids)
            productids.add(self.produitid) # Add to the global set of existing product IDs to prevent duplicates
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate unique product ID: {e}")
            self.reject()
            return

        # Centrer le formulaire dans le scroll_layout
        form_container_widget = QWidget()
        form_container_widget.setLayout(form_layout)
        
        center_form_layout = QHBoxLayout()
        center_form_layout.addStretch()
        center_form_layout.addWidget(form_container_widget)
        center_form_layout.addStretch()
        
        self.scroll_layout.addLayout(center_form_layout)
        self.scroll_layout.addStretch() # Pousse le formulaire vers le haut

        # Gestion des boutons de navigation
        self.next_btn.hide()
        if self.button_layout.indexOf(self.next_btn) != -1:
            self.button_layout.removeWidget(self.next_btn) # S'assurer qu'il est retiré
        if self.button_layout.indexOf(self.submit_btn) == -1:
            self.button_layout.addWidget(self.submit_btn) # Ajouter le bouton de soumission
        self.submit_btn.show()

    def submit_product(self):
        # Ensure global access to cur, conn for database operations
        # These are expected to be available in the global scope where this class is defined
        global cur, conn, productids

        name = self.name_input.text().strip()
        fournisseur_id = self.fournisseur.currentData()
        description = self.description.toPlainText().strip()
        prix_unitaire = self.prix_unitaire.value()
        marque = self.marque.text().strip()
        modele = self.modele.text().strip()
        category = self.category_text

        # --- Validation ---
        if not name:
            QMessageBox.warning(self, "Validation Error", "Product name is required.")
            return
        if fournisseur_id is None: # Check for the 'None' data from "Select Supplier"
            QMessageBox.warning(self, "Validation Error", "Please select a supplier.")
            return
        if prix_unitaire <= 0:
            QMessageBox.warning(self, "Validation Error", "Unit Price must be greater than 0.")
            return
        if not marque:
            QMessageBox.warning(self, "Validation Error", "Brand is required.")
            return
        if not modele:
            QMessageBox.warning(self, "Validation Error", "Model is required.")
            return
        if not description:
            QMessageBox.warning(self, "Validation Error", "Description is required.")
            return

        if self.product_type == "physical":
            if not self.categorie_group.checkedButton():
                QMessageBox.warning(self, "Validation Error", "Please select a category for physical product.")
                return
            if self.length_input.value() <= 0 or self.width_input.value() <= 0 or \
               self.height_input.value() <= 0 or self.mass_input.value() <= 0:
                QMessageBox.warning(self, "Validation Error", "Length, Width, Height, and Mass must be greater than 0.")
                return
        elif self.product_type == "software":
            if not self.version_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Version is required for software product.")
                return
            if not self.license_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "License Type is required for software product.")
                return
        # --- End Validation ---

        try:
            # Main product insertion (Product_INS is common for both types)
            # The exact number and order of parameters depend on your 'Produit_INS' stored procedure.
            # Assuming (_idproduit, _idsfournisseur, _nom, _description, _prixunitaire, _marque, _modele, _categorie)
            cur.execute('CALL "EMIR".Produit_INS(%s,%s,%s,%s,%s,%s,%s,%s)',
                        (self.produitid, fournisseur_id, name, description, prix_unitaire, marque, modele, category))
            
            # Type-specific product insertion
            if self.product_type == "physical":
                # Assuming ProduitMateriel_INS takes (_idproduit, _categorie, _longueur, _largeur, _hauteur, _masse)
                cur.execute('CALL "EMIR".ProduitMateriel_INS(%s,%s,%s,%s,%s,%s)',
                            (self.produitid,
                             category, # Use the cleaned category text
                             self.length_input.value(),
                             self.width_input.value(),
                             self.height_input.value(),
                             self.mass_input.value()))
            else: # Software product
                # Assuming ProduitLogiciel_INS takes (_idproduit, _version, _clelicence)
                cur.execute('CALL "EMIR".ProduitLogiciel_INS(%s,%s,%s)',
                            (self.produitid,
                             self.version_input.text().strip(),
                             self.license_input.text().strip()))
            
            conn.commit() # Commit the transaction if all operations succeed
            
            # Store data to pass back to the calling widget (e.g., ClientLogisticsWidget)
            self.product_data_saved_successfully = {
                'produitid': self.produitid,
                'name': name,
                'price': prix_unitaire,
                'type': self.product_type,
                'category': category
            }

            QMessageBox.information(self, "Success", f"Product '{name}' (ID: {self.produitid}) created successfully.")
            self.accept() # Close the dialog and signal success

        # Use generic Exception for mock DB, or psycopg2.Error for a real PostgreSQL DB
        except Exception as e: 
            if 'conn' in globals(): # Check if conn exists before trying to rollback
                conn.rollback() # Rollback the transaction on error
            QMessageBox.critical(self, "Database Error", f"Failed to create product: {e}\nTransaction rolled back.")
            print(f"Detailed DB error: {e}") # For debugging in console

    def clear_scroll_layout(self): 
        """Efface tous les widgets et layouts du layout de défilement."""
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Pour les layouts imbriqués, il faut aussi les nettoyer récursivement
                self.clear_nested_layout(item.layout())
                item.layout().deleteLater()

    def clear_nested_layout(self, layout):
        """Fonction utilitaire pour nettoyer un layout imbriqué."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_nested_layout(item.layout())
                item.layout().deleteLater()

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


class ClientLogisticsWidget(QWidget):
    """Widget for client-side product and package management (creation, sending)."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.package_input_rows = [] # To keep track of ProductInputRow instances
        self.init_ui()
        self.setObjectName("clientLogisticsWidget")

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Product & Package Management")
        title.setObjectName("headerTitle") 
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Main splitter for horizontal sections
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setHandleWidth(10)
        main_splitter.setStyleSheet("QSplitter::handle { background-color: #D3DCE0; border-radius: 5px; }")

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
                border: 1px solid #D3DCE0;
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
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        layout.addStretch()

        add_product_btn = QPushButton("Launch Product Creation")
        add_product_btn.setStyleSheet("""
            QPushButton {
                background-color: #006775;
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
                background-color: #004F5C;
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
                border: 1px solid #D3DCE0;
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
        title.setObjectName("sectionTitle")
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
                background-color: #006775;
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
                background-color: #004F5C;
                transform: translateY(-1px);
            }
        """)
        add_product_row_btn.clicked.connect(self.add_product_to_package_row)
        layout.addWidget(add_product_row_btn)

        create_package_btn = QPushButton("Create Package")
        create_package_btn.setStyleSheet("""
            QPushButton {
                background-color: #006775;
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
                background-color: #004F5C;;
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
                border: 1px solid #D3DCE0;
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
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        form = QGridLayout()
        self.transporting_org_combo = QComboBox()
        self.receiving_org_combo = QComboBox()
        for org in orgs:
            if org[0] != client_org_id:
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
                background-color: #EDF2F7;
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
                width: 13px;
                height: 13px;
            }
        """
        self.transporting_org_combo.setStyleSheet(combo_style)
        self.receiving_org_combo.setStyleSheet(combo_style)
        self.package_to_send_combo.setStyleSheet(combo_style)

        send_btn = QPushButton("Send Package")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #006775;
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
                background-color: #004F5C;
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
        idcolis = idgenerator.generate_id("^PCO[0-9]{5}$", packageids)
    
        if not lots:
            QMessageBox.warning(self, "Missing", "No lots found for selected package.")
            return
        
        try:
            cur.execute('CALL "EMIR".PColis_INS(%s, %s, %s, %s)',
                (   client_org_id,
                    idcolis,  # Dummy ID for BonExpedition
                    str(datetime.date.today().isoformat()),
                    'en attente'
                )
            )
            print("sucess")
        except psycopg2.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to insert BonExpedition: {e}")
    
        for lot in lots:
            nlotid = idgenerator.generate_id('^PL[A-Z0-9]{5}$', lotids)
            try:
                cur.execute(
                    'CALL "EMIR".PLot_INS(%s,%s, %s, %s, %s, %s)',
                    (   client_org_id,
                        nlotid,
                        lot.product_id,                         # _idproduit
                        str(lot.quantity),              # _quantite
                        str(datetime.date.today().isoformat()),  # _date_creation
                        "neuf"                        # _statut
                    )
                )
                print("sucess")
                cur.execute(
                    'CALL "EMIR".PContenuColis_INS(%s, %s, %s, %s, %s)',
                    (   client_org_id,
                        idcolis,
                        nlotid,                         # _idproduit
                        str(len(lots)),              # _quantite
                        str(datetime.date.today().isoformat()),  #                     # _statut
                    )
                )
                print("sucess")
            except psycopg2.Error as e:
                conn.rollback()
                QMessageBox.critical(self, "Database Error", f"Failed to send lot: {e}")
                return
    
            QMessageBox.information(
                self,
                "Success",
                f"Package '{package_id}' sent successfully from {self.transporting_org_combo.currentText()} to {self.receiving_org_combo.currentText()}."
            )
            cur.execute('SELECT "EMIR".getorganisationname(%s);',(client_org_id,))
            name = cur.fetchone()[0]
            internalmail.send_email("Order Automaticnotification - SCA","steevyvalery7@gmail.com",client_org_id,name,idcolis,self.receiving_org_combo.currentText())
class OrderCard(QFrame):
    order_selected = pyqtSignal(dict) # Signal to emit order data

    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.init_ui()

    def init_ui(self):
        self.setCursor(Qt.CursorShape.PointingHandCursor) # Correct for PyQt6
        self.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #EAEAEA;
                border-radius: 8px;
                padding: 12px;
            }
            QFrame:hover {
                background-color: #F0F2F5; /* Lighten on hover */
                border: 1px solid #D0D0D0;
            }
            QLabel {
                font-size: 14px;
                color: #4A5568;
            }
            QLabel.order_id {
                font-weight: bold;
                color: #006775;
                font-size: 15px;
            }
            QLabel.status {
                font-weight: bold;
                font-size: 13px;
                padding: 3px 8px;
                border-radius: 5px;
                color: white;
            }
        """)

        # APPLY QGraphicsDropShadowEffect PROGRAMMATICALLY FOR SHADOWS
        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(8)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(2)
        shadow_effect.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow_effect)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Order ID and Status
        top_row_layout = QHBoxLayout()
        order_id_label = QLabel(f"Order #{self.order_data.get('Order_ID', 'N/A')}")
        order_id_label.setObjectName("order_id")
        top_row_layout.addWidget(order_id_label)
        top_row_layout.addStretch()

        status_text = self.order_data.get('Status', 'Unknown')
        status_color = self._get_status_color(status_text)
        status_label = QLabel(status_text.capitalize())
        status_label.setObjectName("status")
        status_label.setStyleSheet(f"QLabel.status {{ background-color: {status_color}; }}")
        top_row_layout.addWidget(status_label)
        layout.addLayout(top_row_layout)

        # Other details
        order_date_raw = self.order_data.get('Order_Date')
        formatted_date = 'N/A'
        if isinstance(order_date_raw, datetime.datetime): # Use datetime.datetime
            formatted_date = order_date_raw.strftime('%b %d, %Y')
        elif isinstance(order_date_raw, str):
            try:
                # Assuming a common format like "YYYY-MM-DD HH:MM:SS"
                parsed_date = datetime.datetime.strptime(order_date_raw, '%Y-%m-%d %H:%M:%S')
                formatted_date = parsed_date.strftime('%b %d, %Y')
            except ValueError:
                formatted_date = str(order_date_raw) # Fallback to raw string if parsing fails

        layout.addWidget(QLabel(f"Customer: {self.order_data.get('Customer_Name', 'N/A')}"))
        layout.addWidget(QLabel(f"Date: {formatted_date}"))

        self.setLayout(layout)

    def mousePressEvent(self, event):
        # Emit the signal when the card is clicked
        self.order_selected.emit(self.order_data)
        super().mousePressEvent(event)

    def _get_status_color(self, status):
        # This maps your backend statuses to display colors
        if status == 'en attente':
            return '#F6AD55' # Orange
        elif status == 'Accepte':
            return '#006775' # Blue (Assuming "Accepted" means In Transit)
        elif status == 'Livré':
            return '#38A169' # Green (Delivered)
        elif status == 'Refuse':
            return '#E53E3E' # Red (Refused)
        else:
            return '#A0AEC0' # Grey (Default/Unknown)

class ClientOrderManagementWidget(QWidget):
    """Widget for managing client orders."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.order_cards_layout = None # Will be set in init_ui
        self.init_ui()
        self._update_order_display() # Initial display of orders

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        header_layout = QHBoxLayout()
        title = QLabel("My Orders")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #006775;")

        refresh_btn = QPushButton("🔄 Refresh Orders")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #006775;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #004F5C;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_orders_view)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)

        # Stat cards (these typically don't need to be recreated, just their values updated)
        self.pending_label = QLabel() # Store references to labels to update them
        self.in_transit_label = QLabel()
        self.delivered_label = QLabel()
        self.refused_label = QLabel()

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        stats_layout.addWidget(self._create_stat_card("Pending", self.pending_label, "#F6AD55"))
        stats_layout.addWidget(self._create_stat_card("In Transit", self.in_transit_label, "#006775"))
        stats_layout.addWidget(self._create_stat_card("Delivered", self.delivered_label, "#38A169"))
        stats_layout.addWidget(self._create_stat_card("Refused", self.refused_label, "#E53E3E"))
        layout.addLayout(stats_layout)

        sections_splitter = QSplitter(Qt.Orientation.Horizontal)
        sections_splitter.setHandleWidth(10)
        sections_splitter.setStyleSheet("QSplitter::handle { background-color: #D3DCE0; border-radius: 5px; }")

        # Recent Orders Section
        self.recent_orders_widget = QWidget()
        recent_orders_layout = QVBoxLayout(self.recent_orders_widget)
        recent_orders_layout.setSpacing(15)
        recent_orders_layout.setContentsMargins(0, 0, 0, 0) # Adjust margins if needed

        recent_orders_title = QLabel("Recent Orders")
        recent_orders_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2D3748; margin-bottom: 5px;")
        recent_orders_layout.addWidget(recent_orders_title)

        self.recent_orders_scroll_area = QScrollArea()
        self.recent_orders_scroll_area.setWidgetResizable(True)
        self.recent_orders_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.recent_orders_scroll_area.setMaximumHeight(600)
        self.recent_orders_cards_container = QWidget()
        self.recent_orders_cards_layout = QVBoxLayout(self.recent_orders_cards_container)
        self.recent_orders_cards_layout.setSpacing(12)
        self.recent_orders_cards_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_orders_cards_layout.addStretch() # Add stretch at the end
        self.recent_orders_scroll_area.setWidget(self.recent_orders_cards_container)
        recent_orders_layout.addWidget(self.recent_orders_scroll_area)
        self._apply_section_style_and_shadow(self.recent_orders_widget) # Apply style

        # Pending Action Section
        self.pending_orders_widget = QWidget()
        pending_orders_layout = QVBoxLayout(self.pending_orders_widget)
        pending_orders_layout.setSpacing(15)
        pending_orders_layout.setContentsMargins(0, 0, 0, 0)

        pending_orders_title = QLabel("Pending Action")
        pending_orders_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2D3748; margin-bottom: 5px;")
        pending_orders_layout.addWidget(pending_orders_title)

        self.pending_orders_scroll_area = QScrollArea()
        self.pending_orders_scroll_area.setWidgetResizable(True)
        self.pending_orders_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.pending_orders_scroll_area.setMaximumHeight(600)
        self.pending_orders_cards_container = QWidget()
        self.pending_orders_cards_layout = QVBoxLayout(self.pending_orders_cards_container)
        self.pending_orders_cards_layout.setSpacing(12)
        self.pending_orders_cards_layout.setContentsMargins(0, 0, 0, 0)
        self.pending_orders_cards_layout.addStretch() # Add stretch at the end
        self.pending_orders_scroll_area.setWidget(self.pending_orders_cards_container)
        pending_orders_layout.addWidget(self.pending_orders_scroll_area)
        self._apply_section_style_and_shadow(self.pending_orders_widget) # Apply style

        sections_splitter.addWidget(self.recent_orders_widget)
        sections_splitter.addWidget(self.pending_orders_widget)

        layout.addWidget(sections_splitter)
        self.setLayout(layout)

    def _apply_section_style_and_shadow(self, widget):
        widget.setStyleSheet("""
            QWidget { /* Use QWidget instead of QFrame if it's not actually a QFrame */
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #D3DCE0;
            }
        """)
        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(15)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(4)
        shadow_effect.setColor(QColor(0, 0, 0, 40))
        widget.setGraphicsEffect(shadow_effect)


    def _create_stat_card(self, title, value_label_ref, color):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.NoFrame)
        card.setFrameShadow(QFrame.Shadow.Plain)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: "#FFFFFF";
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 20px 25px;
            }}
        """)
        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(20)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(6)
        shadow_effect.setColor(QColor(0, 0, 0, 20))
        card.setGraphicsEffect(shadow_effect)

        layout = QVBoxLayout()
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 15px; color: #718096; font-weight: 600;")

        # Use the passed label reference directly
        value_label_ref.setStyleSheet(f"font-size: 42px; font-weight: bold; color: {color};")
        value_label_ref.setText("0") # Initial value

        layout.addWidget(title_label)
        layout.addWidget(value_label_ref)
        card.setLayout(layout)
        return card

    def _update_order_display(self):
        """
        Updates the order statistics and repopulates the order card sections.
        This is called on initial load and on refresh.
        """
        all_client_orders = self.data.client_orders # Assume this is always the source of truth

        # 1. Update Stat Cards
        pending_count = len([o for o in all_client_orders if o.get('Status') == 'en attente'])
        in_transit_count = len([o for o in all_client_orders if o.get('Status') == 'Accepte'])
        refused_count = len([o for o in all_client_orders if o.get('Status') == 'Refuse'])
        completed_count = len([o for o in all_client_orders if o.get('Status') == 'Livré'])

        self.pending_label.setText(str(pending_count))
        self.in_transit_label.setText(str(in_transit_count))
        self.delivered_label.setText(str(completed_count))
        self.refused_label.setText(str(refused_count))

        # 2. Repopulate Recent Orders Section
        self._clear_layout(self.recent_orders_cards_layout) # Clear existing cards
        try:
            sorted_recent_orders = sorted(all_client_orders, key=lambda x: x.get('Order_Date', datetime.datetime.min), reverse=True)[:10]
        except TypeError:
            sorted_recent_orders = all_client_orders[:10]
            print("Warning: Could not sort recent orders by date during update. Check 'Order_Date' format consistency.")

        if sorted_recent_orders:
            for order in sorted_recent_orders:
                order_card = OrderCard(order)
                order_card.order_selected.connect(self.on_order_selected)
                self.recent_orders_cards_layout.insertWidget(self.recent_orders_cards_layout.count() - 1, order_card) # Insert before stretch
        else:
            no_orders_label = QLabel("No recent orders to display.")
            no_orders_label.setStyleSheet("color: #999; font-style: italic; padding: 20px; text-align: center;")
            self.recent_orders_cards_layout.insertWidget(self.recent_orders_cards_layout.count() - 1, no_orders_label)


        # 3. Repopulate Pending Action Section
        self._clear_layout(self.pending_orders_cards_layout) # Clear existing cards
        pending_action_orders = [o for o in all_client_orders if o.get('Status') == 'en attente']

        if pending_action_orders:
            for order in pending_action_orders:
                order_card = OrderCard(order)
                order_card.order_selected.connect(self.on_order_selected)
                self.pending_orders_cards_layout.insertWidget(self.pending_orders_cards_layout.count() - 1, order_card) # Insert before stretch
        else:
            no_pending_label = QLabel("No pending orders to action.")
            no_pending_label.setStyleSheet("color: #999; font-style: italic; padding: 20px; text-align: center;")
            self.pending_orders_cards_layout.insertWidget(self.pending_orders_cards_layout.count() - 1, no_pending_label)


    def on_order_selected(self, order_data):
        QMessageBox.information(self, "Order Details",
                                f"Order ID: {order_data.get('Order_ID', 'N/A')}\n"
                                f"Customer: {order_data.get('Customer_Name', 'N/A')}\n"
                                f"Status: {order_data.get('Status', 'N/A')}\n"
                                f"Date: {order_data.get('Order_Date', 'N/A')}\n"
                                f"Total: {order_data.get('Total_Amount', 'N/A')}")

    def refresh_orders_view(self):
        # In a real app, you would fetch new data here:
        # self.data.fetch_latest_client_orders() # <-- Call your data fetching method
        # For now, we assume self.data.client_orders is updated externally or through a simulated call.

        self._update_order_display() # Just re-render with current data
        QMessageBox.information(self, "Refreshed", "Order data refreshed.")

    def _clear_layout(self, layout):
        if layout is not None:
            # Iterate backwards to remove widgets correctly
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                if item.widget():
                    item.widget().deleteLater()
                    layout.removeItem(item) # Remove the item from the layout
                elif item.layout():
                    self._clear_layout(item.layout())
                    layout.removeItem(item) # Remove the nested layout item

class ShipmentTrackingWidget(QWidget):
    """Widget for tracking client's shipments."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()
        # Initial population handled by update_movements_table in init_ui

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        header_layout = QHBoxLayout()
        title = QLabel("Shipment Tracking")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color:#006775;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Add a refresh button for consistency
        refresh_btn = QPushButton("🔄 Refresh Shipments")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #006775;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #004F5C;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_shipments_view) # Connect to new refresh method
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        filter_search_layout = QHBoxLayout()
        filter_search_layout.setSpacing(15)

        search_label = QLabel("Search Package:")
        search_label.setStyleSheet("font-size: 15px; color: #4A5568; font-weight: 500;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Package ID or Product Name...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #D0D0D0;
                border-radius: 8px;
                font-size: 15px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #006775;
            }
        """)
        self.search_input.textChanged.connect(self.filter_movements)

        type_label = QLabel("Filter by Type:")
        type_label.setStyleSheet("font-size: 15px; color: #4A5568; font-weight: 500;")
        self.type_combo = QComboBox()
        self.type_combo.addItems(['All', 'Outbound', 'In Transit', 'Received', 'Return'])
        self.type_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #D0D0D0;
                border-radius: 8px;
                font-size: 15px;
                background-color: #FFFFFF;
                selection-background-color: #E6E6FF;
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
        table.setHorizontalHeaderLabels(['Timestamp', 'Package ID', 'Status', 'Location', 'Description'])

        table.verticalHeader().setDefaultSectionSize(40)

        table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                font-size: 14px;
                selection-background-color: #E0F2F7;
                selection-color: #2D3748;
                gridline-color: #EDF2F7;
            }
            QHeaderView::section {
                background-color: #006775;
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
                padding: 10px 8px;
            }
            QTableWidget::item:selected {
                background-color: #006775;
                color: #FFFFFF;
            }
            QTableWidget::item:hover {
                background-color: #F0F8FF;
            }
        """)

        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.resizeColumnsToContents()

        return table

    def filter_movements(self):
        search_text = self.search_input.text().lower().strip()
        movement_type = self.type_combo.currentText()

        filtered_movements = []
        for movement in self.data.movement_history:
            package_id_match = search_text in movement.get('Package_ID', '').lower()
            product_name_match = search_text in movement.get('Product_Name', '').lower()

            if search_text and not (package_id_match or product_name_match):
                continue

            if movement_type != 'All':
                if movement_type == 'Outbound' and movement.get('Movement_Type') != 'Outbound':
                    continue
                elif movement_type == 'In Transit' and movement.get('Movement_Type') != 'In Transit':
                    continue
                elif movement_type == 'Received' and movement.get('Movement_Type') != 'Received':
                    continue
                elif movement_type == 'Return' and movement.get('Movement_Type') != 'Return':
                    continue
            filtered_movements.append(movement)

        self.update_movements_table(filtered_movements)

    def update_movements_table(self, movements):
        def get_timestamp_for_sort(movement):
            ts = movement.get('Timestamp')
            if isinstance(ts, datetime.datetime):
                return ts
            if isinstance(ts, str):
                try:
                    return datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    pass
            return datetime.datetime.min

        sorted_movements = sorted(movements, key=get_timestamp_for_sort, reverse=True)
        self.movements_table.setRowCount(len(sorted_movements)) # Clear and set row count

        type_colors = {
            'Outbound': '#006775',
            'In Transit': '#F6AD55',
            'Received': '#38A169',
            'Return': '#E53E3E',
            'Unknown': '#A0AEC0'
        }

        for i, movement in enumerate(sorted_movements):
            display_timestamp = movement.get('Timestamp')
            if isinstance(display_timestamp, datetime.datetime):
                display_timestamp_str = display_timestamp.strftime('%H:%M %b %d, %Y')
            elif isinstance(display_timestamp, str):
                try:
                    parsed_ts = datetime.datetime.strptime(display_timestamp, '%Y-%m-%d %H:%M:%S')
                    display_timestamp_str = parsed_ts.strftime('%H:%M %b %d, %Y')
                except ValueError:
                    display_timestamp_str = display_timestamp
            else:
                display_timestamp_str = 'N/A'

            self.movements_table.setItem(i, 0, QTableWidgetItem(display_timestamp_str))
            self.movements_table.setItem(i, 1, QTableWidgetItem(movement.get('Package_ID', 'N/A')))

            m_type = movement.get('Movement_Type', 'Unknown')
            type_item = QTableWidgetItem(m_type)
            type_item.setBackground(QColor(type_colors.get(m_type, type_colors['Unknown'])))
            type_item.setForeground(QColor('#FFFFFF'))
            font = type_item.font()
            font.setBold(True)
            type_item.setFont(font)
            self.movements_table.setItem(i, 2, type_item)

            self.movements_table.setItem(i, 3, QTableWidgetItem(movement.get('Location', 'N/A')))
            self.movements_table.setItem(i, 4, QTableWidgetItem(movement.get('Description', 'N/A')))

        self.movements_table.resizeColumnsToContents()

    def refresh_shipments_view(self):
        # In a real app, you would fetch new data here:
        # self.data.fetch_latest_movement_history() # <-- Call your data fetching method
        # For now, assume self.data.movement_history is updated externally or through simulation.

        self.filter_movements() # Re-apply filters and update table with current data
        QMessageBox.information(self, "Refreshed", "Shipment data refreshed.")


class InquiryDetailDialog(QDialog):
    """Dialog to display details of an inquiry and allow status update."""
    def __init__(self, inquiry_data, parent=None):
        super().__init__(parent)
        self.inquiry_data = inquiry_data
        self.setWindowTitle(f"Inquiry Details: {self.inquiry_data['ID']}")
        self.setFixedSize(550, 620) # Slightly larger for better spacing

        # Apply shadow effect to the dialog
        shadow_dialog = QGraphicsDropShadowEffect(self)
        shadow_dialog.setBlurRadius(25)
        shadow_dialog.setXOffset(0)
        shadow_dialog.setYOffset(10)
        shadow_dialog.setColor(QColor(0, 0, 0, 40)) # More subtle shadow
        self.setGraphicsEffect(shadow_dialog)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self) # Set layout directly on the dialog
        layout.setContentsMargins(30, 30, 30, 30) # Adjusted margins
        layout.setSpacing(20) # Spacing between major sections

        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA; /* Consistent light background */
                border-radius: 15px;
                /* box-shadow handled by QGraphicsDropShadowEffect */
            }
            QLabel {
                font-size: 15px;
                color: #2D3748; /* Darker text for better readability */
            }
            QLabel[property="title"] { /* Targeting the title label with a custom property */
                font-size: 26px; /* Slightly adjusted title size */
                font-weight: bold;
                color: #006775; /* Primary teal color for title */
                margin-bottom: 10px; /* Adjusted margin */
                padding-bottom: 8px; /* Adjusted padding */
                border-bottom: 1px solid #D3DCE0; /* Subtle border */
            }
            QTextEdit, QComboBox {
                padding: 10px 12px; /* Consistent padding */
                border: 1px solid #D3DCE0; /* Consistent border */
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
                color: #2D3748;
            }
            QTextEdit:focus, QComboBox:focus {
                border: 1px solid #006775; /* Focus border in primary color */
                outline: none;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(path/to/your/down_arrow_icon.png); /* Optional: custom arrow icon */
                width: 16px;
                height: 16px;
            }
            QPushButton {
                background-color: #006775; /* Primary button color */
                color: white;
                border: none;
                padding: 12px 25px; /* Consistent padding */
                border-radius: 10px; /* Consistent border-radius */
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #004F5C; /* Darker teal on hover */
            }
            /* Style for secondary buttons */
            QPushButton#secondaryButton { /* Using objectName to target specific buttons */
                background-color: #A0AEC0; /* Grey for secondary action */
                color: #2D3748;
            }
            QPushButton#secondaryButton:hover {
                background-color: #718096; /* Darker grey on hover */
            }
        """)

        title_label = QLabel(f"Inquiry: {self.inquiry_data['ID']}")
        title_label.setProperty("property", "title") # Use property for CSS targeting
        layout.addWidget(title_label)
        
        # Spacer for better separation
        layout.addSpacing(10)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10) # Spacing between form rows
        
        # Displaying inquiry details
        form_layout.addRow("Type:", QLabel(self.inquiry_data['Type']))
        form_layout.addRow("Related Product:", QLabel(self.inquiry_data['Related_Product']))
        form_layout.addRow("Reported By:", QLabel(self.inquiry_data['Reported_By_Org']))
        form_layout.addRow("Reported Time:", QLabel(self.inquiry_data['Reported_Time'].strftime('%Y-%m-%d %H:%M')))

        layout.addLayout(form_layout)
        
        layout.addSpacing(15) # Spacer before description

        description_label = QLabel("Description:")
        layout.addWidget(description_label)
        self.description_text = QTextEdit()
        self.description_text.setText(self.inquiry_data['Description'])
        self.description_text.setReadOnly(True)
        self.description_text.setMinimumHeight(120) # Make description field taller
        layout.addWidget(self.description_text)

        layout.addSpacing(20) # Spacer before status update

        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)
        status_label = QLabel("Update Status:")
        status_label.setStyleSheet("font-weight: bold; color: #2D3748;") # Emphasize status update label
        status_layout.addWidget(status_label)
        self.status_combo = QComboBox()
        self.status_combo.addItems(['Open', 'In Progress', 'Resolved', 'Closed'])
        self.status_combo.setCurrentText(self.inquiry_data['Status'])
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch() # Pushes combo box to the left

        layout.addLayout(status_layout)

        layout.addSpacing(25) # Spacer before buttons

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15) # Spacing between buttons

        close_button = QPushButton("Close")
        close_button.setObjectName("secondaryButton") # Use objectName for secondary style
        close_button.clicked.connect(self.reject) # Use reject for close
        button_layout.addWidget(close_button)

        save_button = QPushButton("Save Status")
        save_button.clicked.connect(self.save_status)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)
        # self.setLayout(layout) # Already set in constructor if QVBoxLayout(self)

    def save_status(self):
        new_status = self.status_combo.currentText()
        if new_status != self.inquiry_data['Status']:
            # In a real app, this would update the database
            self.inquiry_data['Status'] = new_status # Update in-memory data
            QMessageBox.information(self, "Status Updated! ✨", f"Inquiry **{self.inquiry_data['ID']}** status successfully updated to **{new_status}**! 🎉")
            self.accept() # Close dialog and signal acceptance
        else:
            QMessageBox.information(self, "No Change", "The status is already the same. No update needed. 😉")
            self.accept() # Close dialog even if no change, as user clicked save.
        

class NewInquiryDialog(QDialog):
    """Dialog to report a new inquiry."""
    def __init__(self, data, client_id, parent=None):
        super().__init__(parent)
        self.data = data
        self.client_id = client_id
        self.setWindowTitle("Report New Inquiry")
        self.setFixedSize(480, 520) # Taille ajustée pour un meilleur équilibre

        # Appliquer l'ombre portée au dialogue
        shadow_dialog = QGraphicsDropShadowEffect(self)
        shadow_dialog.setBlurRadius(25)
        shadow_dialog.setXOffset(0)
        shadow_dialog.setYOffset(10)
        shadow_dialog.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow_dialog)

        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        layout.setContentsMargins(30, 30, 30, 30) # Marges internes ajustées
        layout.setVerticalSpacing(15) # Espacement vertical entre les champs

        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA; /* Fond clair et moderne */
                border-radius: 15px;
                /* box-shadow est remplacé par QGraphicsDropShadowEffect */
            }
            QLabel {
                font-size: 15px;
                color: #4A5568; /* Gris moyen pour les labels */
                font-weight: 500; /* Légèrement plus épais */
            }
            QLineEdit, QComboBox, QTextEdit {
                padding: 10px 12px; /* Padding interne ajusté */
                border: 1px solid #D3DCE0; /* Bordure subtile et cohérente */
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
                color: #2D3748; /* Couleur de texte sombre */
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #006775; /* Bordure de focus bleue-verte (couleur principale) */
                outline: none; /* Supprime l'outline par défaut sur certains OS */
            }
            QComboBox::drop-down {
                border: 0px; /* Supprime la bordure par défaut du bouton déroulant */
            }
            QComboBox::down-arrow {
                image: url(path/to/your/down_arrow_icon.png); /* Optionnel: icône de flèche personnalisée */
                width: 16px;
                height: 16px;
            }
            QPushButton {
                background-color: #006775; /* Couleur principale pour le bouton d'action */
                color: white;
                border: none;
                padding: 12px 25px; /* Padding ajusté */
                border-radius: 10px; /* Rayon cohérent */
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #004F5C;
            }
            /* Style pour le bouton Annuler */
            QPushButton#cancelButton { /* Utilisation d'un objectName pour le cibler */
                background-color: #A0AEC0; /* Gris plus clair */
                color: #2D3748; /* Texte sombre pour un bouton secondaire */
                border: none;
                padding: 12px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton#cancelButton:hover {
                background-color: #718096; /* Gris plus foncé au survol */
            }
        """)

        self.inquiry_type_combo = QComboBox()
        self.inquiry_type_combo.addItems(['Missing Package', 'Damaged Item', 'Incorrect Order', 'Billing Issue', 'General Support', 'Other'])
        layout.addRow("Inquiry Type:", self.inquiry_type_combo)

        self.related_product_combo = QComboBox()
        self.related_product_combo.addItem("— None (General Inquiry) —", None)
        # Assurez-vous que self.data.products_df existe et est un DataFrame pandas ou a une méthode itertuples()
        if hasattr(self.data, 'products_df') and not self.data.products_df.empty:
            for product in self.data.products_df.itertuples():
                self.related_product_combo.addItem(product.Name, product.ID)
        else:
            self.related_product_combo.addItem("No products available", None) # Gérer le cas où il n'y a pas de produits
        layout.addRow("Related Product:", self.related_product_combo)

        # QLabel pour la description sur sa propre ligne
        description_label = QLabel("Description:")
        layout.addWidget(description_label)
        self.description_text = QTextEdit()
        self.description_text.setPlaceholderText("Provide detailed information about your inquiry (e.g., date of incident, order number, specific items involved)...")
        self.description_text.setMinimumHeight(100) # Hauteur minimale pour le champ de texte
        layout.addWidget(self.description_text)

        # Boutons d'action
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10) # Espacement entre les boutons

        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton") # Définir un objectName pour le style spécifique
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        report_button = QPushButton("Submit Inquiry")
        report_button.clicked.connect(self.report_inquiry)
        button_layout.addWidget(report_button)
        
        layout.addRow(button_layout) # Ajoute le layout de boutons comme une ligne dans le QFormLayout
        self.setLayout(layout)

    def report_inquiry(self):
        inquiry_type = self.inquiry_type_combo.currentText()
        related_product_id = self.related_product_combo.currentData()
        related_product_name = self.related_product_combo.currentText() if related_product_id else "N/A"
        description = self.description_text.toPlainText().strip() # .strip() pour enlever les espaces inutiles

        if not description:
            QMessageBox.warning(self, "Input Error", "Please provide a detailed description for your inquiry.")
            return

        # Assurez-vous que self.data.inquiries est une liste et que 'ID' est généré de manière unique
        try:
            next_id_num = len(self.data.inquiries) + 1
            # Boucle pour s'assurer que l'ID est unique s'il existe déjà (peu probable mais bonne pratique)
            while any(i['ID'] == f'INQ{next_id_num:03d}' for i in self.data.inquiries):
                next_id_num += 1
            new_inquiry_id = f'INQ{next_id_num:03d}'
        except AttributeError:
            QMessageBox.critical(self, "Data Error", "Cannot access inquiries data. Please check self.data.inquiries.")
            return
        except Exception as e:
            QMessageBox.critical(self, "ID Generation Error", f"Failed to generate inquiry ID: {e}")
            return

        new_inquiry = {
            'ID': new_inquiry_id,
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
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #006775;")

        report_inquiry_btn = QPushButton("Submit New Inquiry")
        report_inquiry_btn.setStyleSheet("""
            QPushButton {
                background-color: #006775;
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
                background-color: #004F5C;
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

        stats_layout.addWidget(self.create_inquiry_stat_card("Open Inquiries", open_inquiries, "#E53E3E"))
        stats_layout.addWidget(self.create_inquiry_stat_card("In Progress", in_progress_inquiries, "#F6AD55"))
        stats_layout.addWidget(self.create_inquiry_stat_card("Resolved/Closed", resolved_inquiries, "#38A169"))
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
                border: 1px solid #D3DCE0;
                border-radius: 10px;
                padding: 18px 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #4A5568; font-weight: bold;")

        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")

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
            border: 1px solid #D3DCE0;
            border-radius: 10px;
            font-size: 14px;
            selection-background-color: #FFEBEE;
            selection-color: #2D3748;
            gridline-color: #EDF2F7;
        }
        QHeaderView::section {
            background-color: #006775;
            color: #FFFFFF;
            padding: 13px;
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
            color: #2D3748;
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
                'Open': '#E53E3E',
                'In Progress': '#F6AD55',
                'Resolved': '#38A169',
                'Closed': '#9E9E9E' # Grey for closed
            }
            status_item.setBackground(QColor(status_colors.get(inquiry['Status'], '#D3DCE0')))
            status_item.setForeground(QColor('#FFFFFF'))
            if inquiry['Status'] == 'In Progress':
                status_item.setForeground(QColor('#2D3748'))
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
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)

        # --- Card 1: AI Assistant Placeholder ---
        ai_card = QFrame()
        ai_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #D3DCE0;
                padding: 25px;
            }
        """)
        shadow_ai = QGraphicsDropShadowEffect(ai_card)
        shadow_ai.setBlurRadius(20)
        shadow_ai.setXOffset(0)
        shadow_ai.setYOffset(8)
        shadow_ai.setColor(QColor(0, 0, 0, 35))
        ai_card.setGraphicsEffect(shadow_ai)

        ai_layout = QVBoxLayout(ai_card)
        ai_layout.setSpacing(10)
        ai_title = QLabel("🤖 AI Assistant ")
        ai_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #006775;")
        ai_desc = QLabel("An intelligent assistant that will answer all your questions about the platform.")
        ai_desc.setWordWrap(True)
        ai_desc.setStyleSheet("font-size: 16px; color:#2D3748;")
        
        ai_btn = QPushButton("Ask your questions")
        ai_btn.setStyleSheet("""
            QPushButton {
                background-color: #006775;
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 10px;
                padding: 10px 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #004F5C;
            }
        """)
        ai_btn.clicked.connect(self.open_helpbot_dialog)
        
        ai_layout.addWidget(ai_title)
        ai_layout.addWidget(ai_desc)
        ai_layout.addSpacing(20)
        ai_layout.addWidget(ai_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        ai_layout.addStretch()

        # --- Card 2: Report a Bug ---
        bug_card = QFrame()
        bug_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #D3DCE0;
                padding: 25px;
            }
        """)
        shadow_bug = QGraphicsDropShadowEffect(bug_card)
        shadow_bug.setBlurRadius(20)
        shadow_bug.setXOffset(0)
        shadow_bug.setYOffset(8)
        shadow_bug.setColor(QColor(0, 0, 0, 35))
        bug_card.setGraphicsEffect(shadow_bug)
        
        bug_layout= QVBoxLayout(bug_card)
        bug_layout.setSpacing(10)
        bug_title = QLabel("🐞 Report a Bug")
        bug_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #E77E23;")
        bug_desc = QLabel("If you encounter a problem or bug, please let our IT support know so we can fix it quickly.")
        bug_desc.setWordWrap(True)
        bug_desc.setStyleSheet("font-size: 16px; color: #2D3748;")
        
        report_btn = QPushButton("Report a Bug")
        report_btn.setStyleSheet("""
            QPushButton {
                background-color: #E77E23;
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 10px;
                padding: 10px 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #C27C37;
            }
        """)
        report_btn.clicked.connect(self.open_bug_report_dialog)
        
        bug_layout.addWidget(bug_title)
        bug_layout.addWidget(bug_desc)
        bug_layout.addSpacing(20)
        bug_layout.addWidget(report_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        bug_layout.addStretch()
        
        layout.addWidget(ai_card)
        layout.addWidget(bug_card)
        layout.addStretch()

    def open_helpbot_dialog(self):
        try:
            # Assurez-vous que la classe ChatBot est bien importée de helpbot.py
            from helpbot import ChatBot # If you have a separate file for ChatBot
            self.chatbot_window = ChatBot()
            self.chatbot_window.show()
        except ImportError:
            QMessageBox.critical(self, "Erreur", "La classe ChatBot n'a pas pu être importée. Assurez-vous que 'helpbot.py' existe et est accessible.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur ChatBot", f"Une erreur est survenue lors de l'ouverture du ChatBot: {e}")
        
    def open_bug_report_dialog(self):
        try:
            # NO IMPORT STATEMENT NEEDED IF BugReportDialog IS IN THE SAME FILE
            dialog = BugReportDialog(self) # Directly access the class
            dialog.exec()
        except Exception as e: # This will now catch any other errors, if any.
            QMessageBox.critical(self, "Erreur Bug Report", f"Une erreur est survenue lors de l'ouverture du rapport de bug: {e}")

        
class BugReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Report a Bug")
        self.setFixedSize(450, 380)

        shadow_dialog = QGraphicsDropShadowEffect(self)
        shadow_dialog.setBlurRadius(25)
        shadow_dialog.setXOffset(0)
        shadow_dialog.setYOffset(10)
        shadow_dialog.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow_dialog)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border-radius: 15px;
            }
            QLabel {
                font-size: 16px;
                color: #2D3748;
                margin-bottom: 5px;
            }
            QTextEdit {
                border: 1px solid #D3DCE0;
                border-radius: 8px;
                font-size: 15px;
                background-color: #FFFFFF;
                padding: 10px;
            }
            QTextEdit:focus {
                border: 1px solid #E77E23;
            }
            QPushButton {
                background-color: #E77E23;
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 10px;
                padding: 12px 24px;
                border: none;
            }
            QPushButton:hover {
                background-color: #C27C37;
            }
        """)
        
        label = QLabel("Describe the bug you encountered:")
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Please provide as much detail as possible (steps to reproduce, expected behavior, actual behavior, screenshots if possible)...")
        
        self.send_btn = QPushButton("Send to IT Support")
        self.send_btn.clicked.connect(self.send_bug_report)
        
        layout.addWidget(label)
        layout.addWidget(self.text_edit)
        layout.addSpacing(20)
        layout.addWidget(self.send_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
    def send_bug_report(self):
        # Make sure smtplib and email.mime.text are imported at the top of your main file
        import smtplib
        from email.mime.text import MIMEText

        bug_text = self.text_edit.toPlainText().strip()
        if not bug_text:
            QMessageBox.warning(self, "Input Error", "Please describe the bug before sending.")
            return

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
            QMessageBox.critical(self, "Error", f"Failed to send bug report.\n\nDetails: {e}")

        
class BugReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Report a Bug")
        self.setFixedSize(450, 380) # Légèrement plus grand pour un meilleur padding

        # Appliquer l'ombre portée au dialogue
        shadow_dialog = QGraphicsDropShadowEffect(self)
        shadow_dialog.setBlurRadius(25)
        shadow_dialog.setXOffset(0)
        shadow_dialog.setYOffset(10)
        shadow_dialog.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow_dialog)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30) # Marges internes ajustées
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA; /* Fond clair et moderne */
                border-radius: 15px; /* Rayon légèrement plus grand pour un look doux */
                /* box-shadow est remplacé par QGraphicsDropShadowEffect */
            }
            QLabel {
                font-size: 16px;
                color: #2D3748; /* Couleur de texte plus foncée pour le contraste */
                margin-bottom: 5px; /* Petit espace sous le label */
            }
            QTextEdit {
                border: 1px solid #D3DCE0; /* Bordure subtile et cohérente */
                border-radius: 8px;
                font-size: 15px;
                background-color: #FFFFFF; /* Fond blanc */
                padding: 10px; /* Padding interne */
            }
            QTextEdit:focus {
                border: 1px solid #E77E23; /* Bordure orange au focus */
            }
            QPushButton {
                background-color: #E77E23; /* Couleur orange pour l'action */
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 10px; /* Rayon de bordure cohérent */
                padding: 12px 24px; /* Padding ajusté */
                border: none;
            }
            QPushButton:hover {
                background-color: #C27C37; /* Orange plus foncé au survol */
            }
        """)
        
        label = QLabel("Describe the bug you encountered:")
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Please provide as much detail as possible (steps to reproduce, expected behavior, actual behavior, screenshots if possible)...")
        
        self.send_btn = QPushButton("Send to IT Support")
        self.send_btn.clicked.connect(self.send_bug_report)
        
        layout.addWidget(label)
        layout.addWidget(self.text_edit)
        layout.addSpacing(20) # Espacement avant le bouton
        layout.addWidget(self.send_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
    def send_bug_report(self):
        # Assurez-vous d'avoir les imports smtplib et email.mime.text en haut de votre fichier
        import smtplib
        from email.mime.text import MIMEText

        bug_text = self.text_edit.toPlainText().strip()
        if not bug_text:
            QMessageBox.warning(self, "Input Error", "Please describe the bug before sending.")
            return

        # --- Email sending logic (update with your IT support email) ---
        support_email = "steevy.tongoue@2029.ucac-icam.com" # Assurez-vous que cet e-mail est correct
        subject = "Bug Report from Client Dashboard"
        body = bug_text

        try:
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            smtp_user = "scarobotinterne@gmail.com" # Votre adresse e-mail d'envoi
            smtp_password = "vzeokmezwltpoqbt" # Votre mot de passe d'application ou mot de passe réel

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
            QMessageBox.critical(self, "Error", f"Failed to send bug report.\n\nDetails: {e}")


        

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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #006775, stop:1 #006775);
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
        cur.execute('SELECT "EMIR".getorganisationname(%s);',(self.data.client_id,))
        name = cur.fetchone()[0]
        welcome_label = QLabel(f"Welcome, Client Organization {name}!")
        welcome_label.setStyleSheet("font-size: 36px; font-weight: bold;")

        time_label = QLabel(f"Today: {datetime.datetime.now().strftime('%A, %B %d, %Y')}")
        time_label.setStyleSheet("font-size: 16px; margin-top: 5px;")

        hero_layout.addWidget(welcome_label)
        hero_layout.addWidget(time_label)
        hero_layout.addStretch()

        dashboard_stats_layout = QHBoxLayout()
        dashboard_stats_layout.setSpacing(20)

        total_orders = len(self.data.client_orders)
        in_transit = len([o for o in self.data.client_orders if o['Status'] == 'Accepte'])
        pending = len([o for o in self.data.client_orders if o['Status'] == 'en attente' ]) # Last 24 hours
        open_inquiries = len([i for i in self.data.inquiries if i['Status'] == 'Open'])

        dashboard_stats_layout.addWidget(self.create_dashboard_card("Total Orders", total_orders, "#F6AD55", "All orders placed"))
        dashboard_stats_layout.addWidget(self.create_dashboard_card("In Transit", in_transit, "#006775", "Orders currently in shipment"))
        dashboard_stats_layout.addWidget(self.create_dashboard_card("Pending", pending, "#38A169", "Not yet proccessed"))
        dashboard_stats_layout.addWidget(self.create_dashboard_card("Open Inquiries", open_inquiries, "#E53E3E", "Issues requiring attention"))

        hero_layout.addLayout(dashboard_stats_layout)
        layout.addWidget(hero_frame)

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
                color: #006775;
            }
        """)
        quick_actions_layout = QHBoxLayout()
        quick_actions_layout.setSpacing(15)
        quick_actions_layout.setContentsMargins(20, 25, 20, 20)

        button_style = """
            QPushButton {
                background-color: #EDF2F7;
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
                background-color: #006775;
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
                color: #006775;
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
                border: 1px solid #D3DCE0;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #4A5568; font-weight: bold;")

        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")

        description_label = QLabel(description)
        description_label.setStyleSheet("font-size: 13px; color: #4A5568;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(description_label)
        layout.addStretch()

        card.setLayout(layout)
        return card

# REPLACE the entire ClientMainWindow class with this code
class ClientMainWindow(QMainWindow):
    """Main application window for the client dashboard."""
    def __init__(self):
        super().__init__()
        self.data = ClientData(client_org_id)
        self.setWindowTitle("Client Logistics Dashboard")
        
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600) # Minimum size for usability

        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.create_navbar()
        self.create_content_area()

        self.main_layout.addWidget(self.navbar)
        self.main_layout.addWidget(self.content_stack, stretch=1) # Ensure content_stack stretches

        self.apply_global_styles()

        self.navigate_to_widget(self.dashboard_widget)
        self.dashboard_btn.setChecked(True)

    def apply_global_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #EDF2F7;
            }
            QLabel, QGroupBox, QTableWidget, QLineEdit, QComboBox, QPushButton, QTextEdit, QSpinBox, QListWidget, QRadioButton, QDoubleSpinBox {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 15px;
                color: #232946;
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
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 6px;
                padding: 8px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #006775;
            }
            QStackedWidget {
                background-color: #EDF2F7;
                padding: 25px;
            }
        """)

    def create_navbar(self):
        self.navbar = QFrame()
        self.navbar.setFixedHeight(70)
        self.navbar.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-bottom: 1px solid #D3DCE0;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #4A5568;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                border-radius: 3px;
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #EDF2F7;
                color: #2D3748;
            }
            QPushButton:checked {
                background-color: #006775;
                color: #FFFFFF;
                font-weight: bold;
            }
        """)
        
        # --- Add QGraphicsDropShadowEffect for the navbar ---
        nav_shadow_effect = QGraphicsDropShadowEffect(self.navbar)
        nav_shadow_effect.setBlurRadius(15) # Less blur than card, subtle elevation
        nav_shadow_effect.setColor(QColor(0, 0, 0, 40)) # Light black shadow
        nav_shadow_effect.setXOffset(0)
        nav_shadow_effect.setYOffset(4) # Slight vertical offset
        self.navbar.setGraphicsEffect(nav_shadow_effect)
        # --- End QGraphicsDropShadowEffect ---

        navbar_layout = QHBoxLayout(self.navbar)
        navbar_layout.setContentsMargins(20, 0, 20, 0)
        navbar_layout.setSpacing(15)

        logo_label = QLabel("Client Dashboard")
        logo_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #006775;
            margin-right: 25px;
        """)
        navbar_layout.addWidget(logo_label)

        self.dashboard_btn = QPushButton("Dashboard")
        self.order_management_btn = QPushButton("My Orders")
        self.shipment_tracking_btn = QPushButton("Shipment Tracking")
        self.client_logistics_btn = QPushButton("Logistics")
        self.client_inquiries_btn = QPushButton("My Inquiries")
        self.logout_btn = QPushButton("Logout")
        self.help_btn = QPushButton("Help")

        self.dashboard_btn.setCheckable(True)
        self.order_management_btn.setCheckable(True)
        self.shipment_tracking_btn.setCheckable(True)
        self.client_logistics_btn.setCheckable(True)
        self.client_inquiries_btn.setCheckable(True)
        self.logout_btn.setCheckable(True)
        self.help_btn.setCheckable(True)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.dashboard_btn)
        self.button_group.addButton(self.order_management_btn)
        self.button_group.addButton(self.shipment_tracking_btn)
        self.button_group.addButton(self.client_logistics_btn)
        self.button_group.addButton(self.client_inquiries_btn)
        self.button_group.addButton(self.help_btn)
        self.button_group.addButton(self.logout_btn)
        self.dashboard_btn.clicked.connect(lambda: self.navigate_to_widget(self.dashboard_widget))
        self.order_management_btn.clicked.connect(lambda: self.navigate_to_widget(self.order_management_widget))
        self.shipment_tracking_btn.clicked.connect(lambda: self.navigate_to_widget(self.shipment_tracking_widget))
        self.client_logistics_btn.clicked.connect(lambda: self.navigate_to_widget(self.client_logistics_widget))
        self.client_inquiries_btn.clicked.connect(lambda: self.navigate_to_widget(self.client_inquiries_widget))
        self.logout_btn.clicked.connect(self.logout)
        self.help_btn.clicked.connect(lambda: self.navigate_to_widget(self.help_widget))

        navbar_layout.addStretch()
        navbar_layout.addWidget(self.dashboard_btn)
        navbar_layout.addWidget(self.order_management_btn)
        navbar_layout.addWidget(self.shipment_tracking_btn)
        navbar_layout.addWidget(self.client_logistics_btn)
        navbar_layout.addWidget(self.client_inquiries_btn)
        navbar_layout.addWidget(self.help_btn)  
        navbar_layout.addWidget(self.logout_btn)
        navbar_layout.addStretch()

    def create_content_area(self):
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #EDF2F7; padding: 25px;") 
        
        def scrollable(widget, object_name=None):
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(widget)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            if object_name:
                widget.setObjectName(object_name)
            return scroll

        self.dashboard_widget = scrollable(ClientMainDashboard(self.data, self))
        self.order_management_widget = scrollable(ClientOrderManagementWidget(self.data))
        self.shipment_tracking_widget = scrollable(ShipmentTrackingWidget(self.data))
        self.client_logistics_widget = scrollable(ClientLogisticsWidget(self.data), object_name="clientLogisticsWidget")
        self.client_inquiries_widget = scrollable(ClientInquiriesWidget(self.data, client_org_id))
        self.help_widget = HelpWidget()

        self.content_stack.addWidget(self.dashboard_widget)
        self.content_stack.addWidget(self.order_management_widget)
        self.content_stack.addWidget(self.shipment_tracking_widget)
        self.content_stack.addWidget(self.client_logistics_widget)
        self.content_stack.addWidget(self.client_inquiries_widget)
        self.content_stack.addWidget(self.help_widget)

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

# Set QMessageBox text color to black
# ... (your other code, classes, functions, etc.) ...

if __name__ == '__main__': 
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")

    # High-contrast, accessible palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f5f5f5"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#2D3748"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f0f0f0"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Text, QColor("#2D3748"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#D3DCE0"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#2D3748"))
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor("#006775"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#006775"))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    
    app.setPalette(palette)
    app.setStyleSheet("""
  
    /* Styles généraux pour tous les QWidget */
    QWidget {
        font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; /* Priorise Segoe UI pour Windows, Helvetica Neue pour Mac, sinon Arial */
        color: #343A40; /* Texte principal */
        background-color: #F8F9FA; /* Arrière-plan principal très clair */
    }
    
    /* Styles pour les QDialog (popups) */
    QDialog {
        background-color: #FFFFFF; /* Fond blanc pour les dialogues pour les faire ressortir */
        border-radius: 13px; /* Rayon de bordure légèrement plus grand */
        border: 1px solid #E9ECEF; /* Bordure légère */
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.1); /* Ombre plus prononcée pour les dialogues */
    }

    /* Styles pour les QPushButton */
    QPushButton {
        background-color: #006775; /* Nouvelle couleur d'accent primaire (Teal) */
        color: white;
        border: none;
        border-radius: 8px;
        padding: 13px 20px;
        font-weight: 600; /* Semi-bold */
        font-size: 15px;
        transition: all 0.2s ease-in-out; /* Animation douce */
    }
    QPushButton:hover {
        background-color: #004F5C; /* Couleur d'accent secondaire au survol */
        transform: translateY(-1px); /* Léger soulèvement visuel */
    }
    QPushButton:pressed {
        background-color: #00454F; /* Couleur plus foncée au clic */
        transform: translateY(0);
    }
    QPushButton:disabled {
        background-color: #CED4DA; /* Gris clair pour les boutons désactivés */
        color: #6C757D;
    }

    /* Styles pour les QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox */
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        padding: 10px 13px;
        border: 1px solid #DEE2E6; /* Bordure plus douce */
        border-radius: 8px; /* Bords légèrement plus arrondis pour les inputs */
        font-size: 14px;
        background-color: #FFFFFF; /* Fond blanc pour les champs de saisie */
        color: #343A40; /* Texte principal */
    }
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
        border: 1px solid #006775; /* Bordure accentuée au focus (Teal) */
        background-color: #F8F9FA; /* Léger changement de fond au focus */
    }

    /* Styles spécifiques pour QComboBox */
    QComboBox::drop-down {
        border: 0px;
        width: 25px;
        subcontrol-origin: padding;
        subcontrol-position: center right;
    }
    QComboBox::down-arrow {
        image: url(icons/arrow_down.png); /* Vérifiez le chemin et l'existence de l'icône */
        width: 15px;
        height: 15px;
        padding-right: 5px;
    }
    QComboBox QAbstractItemView { /* Style pour la liste déroulante du QComboBox */
        border: 1px solid #DEE2E6;
        border-radius: 8px;
        selection-background-color: #E0F2F4; /* Léger accent Teal pour la sélection */
        selection-color: #343A40;
        background-color: #FFFFFF;
        padding: 5px 0;
    }
    QComboBox QAbstractItemView::item {
        padding: 8px 13px;
    }

    /* Styles pour les QFrame (utilisés pour les sections et les cartes) */
    QFrame {
        background-color: #FFFFFF; /* Fond blanc pour les cadres/sections */
        border-radius: 10px;
        border: 1px solid #E9ECEF; /* Bordure légère */
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.06); /* Ombre douce, légèrement plus présente */
    }
    
    /* Styles pour les QLabel (texte) */
    QLabel {
        color: #343A40; /* Couleur de texte principale par défaut */
    }
    QLabel#headerTitle { /* Pour les titres principaux de section */
        font-size: 28px;
        font-weight: bold;
        color: #006775; /* Utilisation de la nouvelle couleur d'accent (Teal) */
    }
    QLabel#sectionTitle { /* Pour les titres de sous-section */
        font-size: 20px;
        font-weight: 600; /* Semi-bold */
        color: #343A40;
    }
    QLabel#statCardTitle { /* Titre dans les cartes de statistiques */
        font-size: 14px;
        color: #6C757D; /* Texte secondaire */
        font-weight: 600;
    }
    QLabel#statCardValue { /* Valeur dans les cartes de statistiques */
        font-size: 36px;
        font-weight: bold;
    }


    /* Styles pour les QScrollBar */
    QScrollBar:vertical {
        border: none;
        background: #E9ECEF;
        width: 10px;
        margin: 0px 0px 0px 0px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #ADB5BD;
        border-radius: 5px;
        min-height: 25px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }

    /* Styles pour QSplitter */
    QSplitter::handle { 
        background-color: #DEE2E6; 
        border-radius: 5px; 
        width: 8px;
    }
    QSplitter::handle:hover {
        background-color: #ADB5BD;
    }

    /* Styles pour QTableWidget */
    QTableWidget {
        background-color: #FFFFFF;
        border: 1px solid #E9ECEF;
        border-radius: 10px;
        font-size: 14px;
        selection-background-color: #E0F2F4; /* Accent doux pour la sélection (Teal light) */
        selection-color: #343A40;
        gridline-color: #F1F3F5; /* Lignes de grille très claires */
    }
    QHeaderView::section {
        background-color: #006775; /* En-têtes de tableau accentués (Teal) */
        color: #FFFFFF;
        padding: 13px;
        border: none;
        font-weight: 600;
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
        padding: 10px 8px;
        border-bottom: 1px solid #E9ECEF;
    }
    QTableWidget::item:selected {
        background-color: #006775; /* Couleur d'accent pour la sélection */
        color: #FFFFFF;
    }
    QTableWidget::item:selected:!active {
        background-color: #6C757D; /* Un gris plus neutre pour la sélection inactive */
        color: #FFFFFF;
    }
    QTableWidget::indicator { /* Pour les QCheckBox dans les cellules par exemple */
        width: 18px;
        height: 18px;
        border: 1px solid #ADB5BD;
        border-radius: 4px;
        background-color: #FFFFFF;
    }
    QTableWidget::indicator:checked {
        background-color: #006775;
        border: 1px solid #006775;
    }
""")

    app.setFont(QFont("Segoe UI", 10))

    client_main_window = ClientMainWindow()
    client_main_window.show() # Using show() as discussed
    sys.exit(app.exec())


    