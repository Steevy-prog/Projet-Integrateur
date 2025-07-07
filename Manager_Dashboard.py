import sys
import numpy as np
import pandas as pd
import pyqtgraph as pg
import datetime
import random
import psycopg2

from PyQt6.QtCore import (
    Qt, QDate, QTimer,
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QPen, QFont, QColor, QPalette, QPainter
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QDialog,
    QSpinBox, QListWidget, QSizePolicy, QSplitter, QStackedWidget,
    QButtonGroup, QGroupBox, QMessageBox, QFileDialog, QTabWidget, QDateEdit,
    QTextEdit, QGraphicsOpacityEffect, QGraphicsBlurEffect, # Confirm QGraphicsBlurEffect is here, often QtGui
    QLayout # Crucial for your fix
)

# If QGraphicsBlurEffect truly belongs to QtGui, then it should be in the QtGui import block.
# If your current setup works, keep it where it is, but it's less common.

idorg = 'OABCDE'

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
        database="projet",
        user="postgres",
        password="postgres",
        port=5432
    )
cur=conn.cursor()
cur.execute("SELECT (p).* FROM \"EMIR\".colis_eva() AS p;")
colis_db = cur.fetchall() # Existing packages from the database

cur.execute("SELECT (p).* FROM \"EMIR\".Pcolis_eva1() AS p;")
pcolis_db = cur.fetchall() # Existing packages from the database

cur.execute("SELECT (p).* FROM \"EMIR\".contenucolis_eva() AS p;")
contenu = cur.fetchall() # Existing packages from the database

cur.execute("SELECT (p).* FROM \"EMIR\".Pcontenucolis_eva() AS p;")
pcontenu = cur.fetchall() # Existing packages from the database

class WarehouseData:
    """Data generator and manager for warehouse operations"""

    def __init__(self):
        self.generate_sample_data()

    def generate_sample_data(self):
        # Products data
        cur.execute("SELECT (p).* FROM \"EMIR\".produit_eva() AS p;")
        products = cur.fetchall()
        self.colis_df = pd.DataFrame(colis_db,columns=['id','date_cre','exp_date','receiving_org','statut'])
        self.pcolis_df = pd.DataFrame(pcolis_db,columns=['idorg','id','date_cre','expected_date','receiving_org','statut'])
        self.contenu_df = pd.DataFrame(contenu,columns=['idcol','idlot','quantity','date_maj'])
        self.pcontenu_df = pd.DataFrame(pcontenu,columns=['idorg','idcol','idlot','quantity','date_maj'])
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
            self.products_df = pd.DataFrame(products, columns=['ID', 'Fourniseur', 'Name', 'Description', 'Prix Unitaire', 'Brand', 'Model', 'Category'])
        
        for product in self.products_df.itertuples():
            print(f"Product ID: {product.ID}, Name: {product.Name}")

        # Inventory data
        inventory_data = []
        storage_zones = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2']
        if not self.products_df.empty: # Only proceed if products exist
            for _, product in self.products_df.iterrows():
                try:
                    cur.execute('SELECT "EMIR".quantityproduct(%s);', (product['ID'],))
                    quantity = cur.fetchone()[0]
                    print(f"Fetched quantity for product {product['ID']}: {quantity}")
                    cur.execute('SELECT "EMIR".findzone(%s);', (product['ID'],))
                    zone = cur.fetchone()[0]
                except Exception as e:
                    print(f"Error fetching inventory for product {product['ID']}: {e}. Using dummy values.")
                    quantity = random.randint(10, 200)
                    zone = random.choice(storage_zones)

                inventory_data.append({
                    'Product_ID': product['ID'],
                    'Product_Name': product['Name'],
                    'Quantity': quantity,
                    'Zone': zone,
                    'Last_Updated': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30)),
                    'Value': product['Prix Unitaire']
                })
        else: # Fallback if no products at all
            inventory_data.append({
                'Product_ID': 'DUMMY_P001', 'Product_Name': 'Dummy Item', 'Quantity': 100,
                'Zone': 'A1', 'Last_Updated': datetime.datetime.now(), 'Value': 50.0
            })

        self.inventory_df = pd.DataFrame(inventory_data)

        # Reception orders
        reception_data = []
        suppliers = ['Dell Corp', 'Apple Inc', 'IKEA', 'Samsung', 'Logitech']
        statuses = ['Pending', 'In Transit', 'Received', 'Processing']

        for i in self.pcolis_df.itertuples():
            cur.execute("SELECT \"EMIR\".getvaluecol(%s,%s);",(i.idorg,i.id))
            total = cur.fetchone()[0]
            items = [t for t in self.pcontenu_df.to_dict('records') if t['idcol'] == i.id]
            quan = len(items)
            reception_data.append({
                'Order_ID': i.id,
                'Supplier': i.idorg,
                'Expected_Date': i.expected_date,
                'Items_Count': quan,
                'Status': i.statut,
                'Total_Value': total
            })
        self.reception_df = pd.DataFrame(reception_data)

        #reception data 2
        reception2_datas=[]
        for i in range(20):
            reception2_datas.append({
                'identifiant du colis':f'C{i+1:04d}',
                'date prevue':datetime.date.today() + datetime.timedelta(days=random.randint(-5, 15)),
                'Statuts': random.choice(statuses)
            })
        self.reception2_df = pd.DataFrame(reception2_datas)

        # Expedition orders
        expedition_data = []

        for i in self.colis_df.itertuples():
            cur.execute("SELECT \"EMIR\".getvaluecol(%s);",(i.id,))
            total = cur.fetchone()[0]
            items = [t for t in self.contenu_df.to_dict('records') if t['idcol'] == i.id]
            expedition_data.append({
                'Order_ID': i.id,
                'Destination': i.receiving_org,
                'Request_Date': i.exp_date,
                'Items_Count': len(items),
                'Status': i.statut,
                'Total_Value': total
            })
        self.expedition_df = pd.DataFrame(expedition_data)

        #expedition 2 data
        expedition2_datas=[]
        for i in range(25):
            expedition2_datas.append({
                'identifiant du colis':f'C{i+1:04d}',
                'identifiant du lot':f'L{i+1:04d}',
                'idbonexpedition':f'BE{i+1:03d}',
                'dateexpedition': datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
            })
        self.expedition2_df = pd.DataFrame(expedition2_datas)

        # Generate time series data for performance metrics
        dates = pd.date_range(start='2024-01-01', end='2024-06-19', freq='D')
        self.daily_metrics = pd.DataFrame({
            'Date': dates,
            'Items_Received': np.random.poisson(50, len(dates)),
            'Items_Shipped': np.random.poisson(45, len(dates)),
            'Storage_Utilization': np.random.uniform(60, 95, len(dates)),
            'Order_Fulfillment_Rate': np.random.uniform(85, 99, len(dates))
        })

class ChartWidget(pg.PlotWidget):
    def __init__(self, parent=None, title="", y_label="", x_label="", axisItems=None):
        super().__init__(parent=parent, axisItems=axisItems) # Pass axisItems to super
        self.plotItem.setTitle(title)
        self.plotItem.setLabel('left', y_label)
        self.plotItem.setLabel('bottom', x_label)
        self.plotItem.showGrid(x=True, y=True, alpha=0.3)
        self.setBackground('w')
        self.setAntialiasing(True) # Improve plot smoothness

    def plot_data(self, *args, **kwargs):
        self.clear()
        self.plot(*args, **kwargs)

    def add_item(self, item):
        self.addItem(item)

class MetricCard(QFrame):
    """Card widget for displaying key metrics"""

    def __init__(self, title, value, subtitle="", color="#38A169"):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #D3DCE0;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }}
        """)

        layout = QVBoxLayout()

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; color: #666; font-weight: bold;")

        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")

        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("font-size: 10px; color: #999;")
            layout.addWidget(subtitle_label)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.setSpacing(5)

        self.setLayout(layout)

class RealtimeInventoryViewWidget(QWidget):
    """Widget for real-time inventory view, product details, location details, and stock movements"""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        # Clear existing layout if init_ui is called multiple times
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QVBoxLayout(self)
            self._main_layout.setContentsMargins(0, 0, 0, 0)

        # Create main content widget that will be scrollable
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)

        # Header section
        header_layout = QHBoxLayout()
        title = QLabel("Real-time Inventory View")
        title.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #333;
            margin-bottom: 10px;
        """)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #006775;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        content_layout.addLayout(header_layout)

        # Metrics cards section
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)

        try:
            cur.execute("SELECT \"EMIR\".total();")
            total_items = cur.fetchone()[0] or 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching total_items: {e}")
            total_items = 0

        try:
            cur.execute("SELECT \"EMIR\".valeur();")
            total_value = cur.fetchone()[0] or 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching total_value: {e}")
            total_value = 0

        try:
            cur.execute("SELECT \"EMIR\".available_cells();")
            available_cells = cur.fetchone()[0] or 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching available_cells: {e}")
            available_cells = 0

        try:
            cur.execute("SELECT \"EMIR\".numzones();")
            zones_used = cur.fetchone()[0] or 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching numzones: {e}")
            zones_used = 0
        

        metrics_layout.addWidget(MetricCard("Total Items", f"{total_items:,}", "In Stock"))
        metrics_layout.addWidget(MetricCard("Total Value", f"${total_value:,.0f}", "Inventory Worth"))
        metrics_layout.addWidget(MetricCard("Available Cells", f"{available_cells:,}", "Cells Not In Use", "#E77E23"))
        metrics_layout.addWidget(MetricCard("Storage Zones", str(zones_used), "Active Zones"))
        content_layout.addLayout(metrics_layout)

        # Charts section
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)

        category_chart = ChartWidget(title="Inventory by Category", y_label="Quantity", x_label="Category")
        self.create_category_chart(category_chart)
        category_chart.setMinimumHeight(300)

        stock_chart = ChartWidget(title="Stock Levels - Top Products", y_label="Quantity", x_label="Products")
        self.create_stock_levels_chart(stock_chart)
        stock_chart.setMinimumHeight(300)

        charts_layout.addWidget(category_chart)
        charts_layout.addWidget(stock_chart)
        content_layout.addLayout(charts_layout)

        # Inventory table
        self.inventory_table = self.create_inventory_table()
        self.inventory_table.setMinimumHeight(300)
        content_layout.addWidget(self.inventory_table)

        # Stock Movements placeholder
        stock_movements_label = QLabel("Stock Movements (Not Implemented Yet)")
        stock_movements_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            margin-top: 10px;
            color: #555;
        """)
        content_layout.addWidget(stock_movements_label)
        content_layout.addStretch()

        # Create and configure main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Hide scroll bars but keep scrolling functionality
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Ensure scrolling still works with mouse wheel
        scroll_area.verticalScrollBar().setEnabled(True)
        scroll_area.horizontalScrollBar().setEnabled(True)

        # Set minimum sizes
        content_widget.setMinimumWidth(800)
        self.setMinimumSize(850, 600)

        # Add scroll area to main layout
        self._main_layout.addWidget(scroll_area)

    def refresh_data(self):
        # This method can be called to re-render the UI with fresh data
        self.data.generate_sample_data() # Refresh underlying data
        self.init_ui() # Re-initialize UI with new data

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def create_category_chart(self, chart_widget):
        # pyqtgraph does not have a direct pie chart. Representing as a bar chart.
        merged_df = pd.merge(
            self.data.inventory_df,
            self.data.products_df[['ID', 'Category']],
            left_on='Product_ID',
            right_on='ID',
            how='left'
        )
    
        # Replace missing quantities with 0 before groupby
        merged_df['Quantity'] = merged_df['Quantity'].fillna(0)
    
        category_summary = merged_df.groupby('Category')['Quantity'].sum()
    
        x_vals = np.arange(len(category_summary.index))
        y_vals = category_summary.values
    
        # Replace NaN or non-numeric values with 0
        y_vals = np.nan_to_num(y_vals, nan=0.0)
    
        colors = [
            QColor('#E77E23'), QColor('#38A169'), QColor('#006775'),
            QColor('#9C27B0'), QColor('#F6AD55'), QColor('#00BCD4')
        ]
        brushes = [colors[i % len(colors)] for i in range(len(x_vals))]
    
        bargraph = pg.BarGraphItem(x=x_vals, height=y_vals, width=0.6, brushes=brushes)
        chart_widget.addItem(bargraph)
    
        # Set custom x-axis ticks
        ticks = [(i, label) for i, label in enumerate(category_summary.index)]
        chart_widget.getAxis('bottom').setTicks([ticks])
        chart_widget.plotItem.setTitle("Inventory by Category")
        chart_widget.plotItem.setLabel('left', 'Quantity')

    def create_stock_levels_chart(self, chart_widget):
        # Ensure Quantity column is numeric
        self.data.inventory_df['Quantity'] = pd.to_numeric(
            self.data.inventory_df['Quantity'], errors='coerce'
        ).fillna(0)
    
        top_products = self.data.inventory_df.nlargest(8, 'Quantity')
    
        x_vals = np.arange(len(top_products))
        y_vals = top_products['Quantity'].values
    
        y_vals = np.nan_to_num(y_vals, nan=0.0)
    
        bargraph = pg.BarGraphItem(x=x_vals, height=y_vals, width=0.6)
        chart_widget.addItem(bargraph)
    
        product_names = [
            name[:15] + '...' if len(name) > 15 else name 
            for name in top_products['Product_Name']
        ]
        ticks = [(i, label) for i, label in enumerate(product_names)]
        chart_widget.getAxis('bottom').setTicks([ticks])
        chart_widget.getAxis('bottom').setHeight(60)
        
        chart_widget.plotItem.setTitle('Stock Levels - Top Products')
        chart_widget.plotItem.setLabel('left', 'Quantity')

    def create_inventory_table(self):
        table = QTableWidget()
        table.setRowCount(len(self.data.inventory_df))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['Product', 'Quantity', 'Zone', 'Status', 'Value'])

        for i, (_, row) in enumerate(self.data.inventory_df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['Product_Name']))
            table.setItem(i, 1, QTableWidgetItem(str(row['Quantity'])))
            table.setItem(i, 2, QTableWidgetItem(row['Zone']))

            # Status based on stock level
            status = "In Stock"
            status_item = QTableWidgetItem(status)
            status_item.setBackground(QColor('#E8F5E8'))
            table.setItem(i, 3, status_item)
            table.setItem(i, 4, QTableWidgetItem(f"${row['Value']:,.2f}"))

        # Aesthetic improvements for tables
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #dcdcdc; /* Lighter grid lines */
                border: 1px solid #D3DCE0;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #f0f0f0; /* Lighter header background */
                padding: 10px 8px; /* More padding */
                border: 1px solid #dcdcdc;
                font-weight: bold;
                font-size: 13px;
                color: #555;
            }
            QTableWidget::item {
                padding: 8px; /* More padding for items */
            }
            QTableWidget::item:selected {
                background-color: #cce7ff; /* Lighter selection */
                color: #333;
            }
        """)

        table.setAlternatingRowColors(True)
        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # Stretch columns to fill space
        table.verticalHeader().setVisible(False) # Hide vertical header (row numbers)

        return table

class InputDialog(QDialog):
    """A generic input dialog for single text input."""
    def __init__(self, title: str, label_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(350, 150)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        self.label = QLabel(label_text)
        self.label.setStyleSheet("font-size: 14px; color: #333;")
        self.layout.addWidget(self.label)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Entrez l'identifiant ici...")
        self.line_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #006775;
            }
        """)
        self.layout.addWidget(self.line_edit)

        self.buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("Confirmer")
        self.ok_button.setStyleSheet(_get_button_style("#38A169"))
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setStyleSheet(_get_button_style("#E77E23"))
        self.cancel_button.clicked.connect(self.reject)

        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.ok_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.buttons_layout)

    def get_text(self) -> str:
        return self.line_edit.text()

class ProblemReportDialog(QDialog):
    """Custom dialog for reporting a problem."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Signaler un Problème")
        self.setMinimumSize(450, 350)
        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID Colis/Lot (optionnel)")
        self.id_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 5px; font-size: 14px;")

        self.problem_type_combo = QComboBox()
        self.problem_type_combo.addItems(["Colis endommagé", "Article manquant", "Erreur d'étiquetage", "Problème d'équipement", "Autre"])
        self.problem_type_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: 0px; /* No border for the arrow */
            }
            QComboBox::down-arrow {
                /* No specific icon, rely on system default or provide a dummy image */
            }
        """)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Décrivez le problème en détail...")
        self.description_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.description_input.setMinimumHeight(100)

        self.layout.addRow("ID Colis/Lot:", self.id_input)
        self.layout.addRow("Type de Problème:", self.problem_type_combo)
        self.layout.addRow("Description:", self.description_input)

        self.buttons_layout = QHBoxLayout()
        self.send_button = QPushButton("Envoyer")
        self.send_button.setStyleSheet(_get_button_style("#38A169"))
        self.send_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setStyleSheet(_get_button_style("#E77E23"))
        self.cancel_button.clicked.connect(self.reject)

        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.send_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.layout.addRow(self.buttons_layout)

    def get_problem_data(self) -> dict:
        return {
            "item_id": self.id_input.text(),
            "problem_type": self.problem_type_combo.currentText(),
            "description": self.description_input.toPlainText()
        }

class AssistanceRequestDialog(QDialog):
    """Custom dialog for requesting assistance."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Demander de l'Assistance")
        self.setMinimumSize(400, 250)
        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        self.request_type_combo = QComboBox()
        self.request_type_combo.addItems(["Support Technique", "Assistance Superviseur", "Problème Logistique", "Question Générale"])
        self.request_type_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
        """)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Décrivez votre besoin d'assistance...")
        self.message_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.message_input.setMinimumHeight(80)

        self.layout.addRow("Type de demande:", self.request_type_combo)
        self.layout.addRow("Message:", self.message_input)

        self.buttons_layout = QHBoxLayout()
        self.send_button = QPushButton("Envoyer")
        self.send_button.setStyleSheet(_get_button_style("#38A169"))
        self.send_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setStyleSheet(_get_button_style("#E77E23"))
        self.cancel_button.clicked.connect(self.reject)

        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.send_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.layout.addRow(self.buttons_layout)

    def get_assistance_data(self) -> dict:
        return {
            "request_type": self.request_type_combo.currentText(),
            "message": self.message_input.toPlainText()
        }

import datetime
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QProgressBar, QMessageBox, QLayout,
    QTableWidget, QTableWidgetItem, QHeaderView # Added for potential future use or consistency
)


class ZoneEmballage(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self._main_layout = None  # Initialize to None for the first call to init_ui
        self.init_ui()

    def init_ui(self):
        # Clear existing layout if init_ui is called multiple times
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QVBoxLayout(self)
            self._main_layout.setContentsMargins(15, 15, 15, 15)
            self._main_layout.setSpacing(20)

        # Main container with scroll area (just in case, but designed to avoid scrolling)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        scroll.setWidget(container)
        self._main_layout.addWidget(scroll)

        # Main grid layout for the container
        container_layout = QGridLayout(container)
        container_layout.setContentsMargins(5, 5, 5, 5)
        container_layout.setVerticalSpacing(20)
        container_layout.setHorizontalSpacing(20)

        # Emballage Section
        emballage_frame = self.create_section_frame("Emballage")
        emballage_layout = QGridLayout(emballage_frame)
        emballage_layout.setContentsMargins(15, 15, 15, 15)
        emballage_layout.setVerticalSpacing(15)
        emballage_layout.setHorizontalSpacing(15)

        # Emballage Cards - Top Row
        emballage_layout.addWidget(self.create_metric_card(
            title="Colis à emballer",
            value="42",
            subtitle="Statut: En attente",
            info="Dernière mise à jour: 05/03/2025",
            color="#006775",
            icon="package"
        ), 0, 0)

        emballage_layout.addWidget(self.create_metric_card(
            title="Colis emballés",
            value="128",
            subtitle="Période: Aujourd'hui",
            info="Objectif: 150 colis/jour",
            color="#38A169",
            icon="check-circle"
        ), 0, 1)

        # Emballage Progress - Bottom Row
        progress_widget = self.create_progress_widget(
            title="Progression globale",
            progress=70,
            subtitle="Avancement des opérations",
            color="#E77E23"
        )
        emballage_layout.addWidget(progress_widget, 1, 0, 1, 2)

        # Désemballage Section
        desemballage_frame = self.create_section_frame("Désemballage")
        desemballage_layout = QGridLayout(desemballage_frame)
        desemballage_layout.setContentsMargins(15, 15, 15, 15)
        desemballage_layout.setVerticalSpacing(15)
        desemballage_layout.setHorizontalSpacing(15)

        # Désemballage Cards - Top Row
        desemballage_layout.addWidget(self.create_metric_card(
            title="Colis à désemballer",
            value="24",
            subtitle="Statut: En attente",
            info="Priorité: Moyenne",
            color="#006775",
            icon="package"
        ), 0, 0)

        desemballage_layout.addWidget(self.create_metric_card(
            title="Colis désemballés",
            value="76",
            subtitle="Période: Aujourd'hui",
            info="Efficacité: 85%",
            color="#38A169",
            icon="check-circle"
        ), 0, 1)

        # Désemballage Progress - Bottom Row
        progress_widget = self.create_progress_widget(
            title="Progression désemballage",
            progress=65,
            subtitle="Taux de complétion",
            color="#E77E23"
        )
        desemballage_layout.addWidget(progress_widget, 1, 0, 1, 2)

        # Add sections to main layout
        container_layout.addWidget(emballage_frame, 0, 0)
        container_layout.addWidget(desemballage_frame, 1, 0)
        container_layout.setRowStretch(0, 1)
        container_layout.setRowStretch(1, 1)
        container_layout.setRowStretch(2, 1)

        # Add quick actions toolbar at the bottom
        actions_frame = self.create_quick_actions()
        container_layout.addWidget(actions_frame, 2, 0, 1, 1)

    def create_section_frame(self, title):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #D3DCE0;
            }
        """)

        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.addWidget(title_label)
        return frame

    def create_metric_card(self, title, value, subtitle, info, color, icon=None):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border: 1px solid #D3DCE0;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header with optional icon
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #555;
            }
        """)
        header_layout.addWidget(title_label)

        if icon:
            icon_label = QLabel()
            # QIcon.fromTheme might require a theme to be set or present on the system.
            # For robustness, you might want to provide fallback images or ensure themes are available.
            try:
                icon_label.setPixmap(QIcon.fromTheme(icon).pixmap(24, 24))
            except Exception as e:
                print(f"Warning: Could not load icon '{icon}'. Error: {e}")
                # Fallback or just skip the icon
                pass
            header_layout.addWidget(icon_label)
            header_layout.setAlignment(icon_label, Qt.AlignmentFlag.AlignRight)

        layout.addLayout(header_layout)

        # Main value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {color};
            }}
        """)
        layout.addWidget(value_label)

        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #777;
            }
        """)
        layout.addWidget(subtitle_label)

        # Info (separator + additional info)
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            QFrame {
                border: 1px solid #eee;
            }
        """)
        layout.addWidget(separator)

        info_label = QLabel(info)
        info_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #999;
                font-style: italic;
            }
        """)
        layout.addWidget(info_label)

        layout.addStretch()
        return card

    def create_progress_widget(self, title, progress, subtitle, color):
        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border-radius: 8px;
                border: 1px solid #D3DCE0;
            }}
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #555;
            }
        """)
        layout.addWidget(title_label)

        # Progress bar with percentage
        progress_layout = QHBoxLayout()

        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(progress)
        progress_bar.setTextVisible(False)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #ddd;
                border-radius: 4px;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        progress_layout.addWidget(progress_bar, 4)

        percent_label = QLabel(f"{progress}%")
        percent_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {color};
                margin-left: 10px;
            }}
        """)
        progress_layout.addWidget(percent_label, 1)

        layout.addLayout(progress_layout)

        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #777;
            }
        """)
        layout.addWidget(subtitle_label)

        return widget

    def create_quick_actions(self):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #D3DCE0;
            }
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Action buttons
        actions = [
            ("Marquer comme terminé", "dialog-ok", "#38A169"),
            ("Signaler problème", "dialog-warning", "#E77E23"),
            ("Demande d'assistance", "help", "#006775")
        ]

        for text, icon, color in actions:
            btn = QPushButton(text)
            # QIcon.fromTheme might require a theme to be set or present on the system.
            try:
                btn.setIcon(QIcon.fromTheme(icon))
            except Exception as e:
                print(f"Warning: Could not load icon '{icon}' for button '{text}'. Error: {e}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 5px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            layout.addWidget(btn)

        return frame

    def darken_color(self, hex_color, factor=0.8):
        """Darken a hex color by a given factor"""
        color = QColor(hex_color)
        return color.darker(int(100 * factor)).name()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

# --- MenuExpedition Class ---
class MenuExpedition(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self._main_layout = None # Initialize to None
        self.init_ui()

    def init_ui(self):
        # Clear existing layout if init_ui is called multiple times
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QGridLayout(self)

        layout = self._main_layout
        expedition_summary_table = self.create_expedition_summary_table()
        bouton = QPushButton("chatte")
        bouton.setStyleSheet("""
            QPushButton { background-color: #006775; color: white; border: none;border-radius: 15px; margin-top:50px;font-weight: bold; }
            QPushButton:hover { background-color: #1976D2; }
        """)
        layout.addWidget(expedition_summary_table, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(bouton, 1, 0, Qt.AlignmentFlag.AlignBottom)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def create_expedition_summary_table(self):
        table = QTableWidget()

        # Ensure expedition2_df exists and is not empty before accessing
        if hasattr(self.data, 'expedition2_df') and not self.data.expedition2_df.empty:
            table.setRowCount(len(self.data.expedition2_df))
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(['identifiant du colis', 'identifiant du lot', 'id du bon de reception', "date d'expedition"])

            for i, (_, row) in enumerate(self.data.expedition2_df.iterrows()):
                table.setItem(i, 0, QTableWidgetItem(str(row.get('identifiant du colis', ''))))
                table.setItem(i, 1, QTableWidgetItem(str(row.get('identifiant du lot', ''))))
                table.setItem(i, 2, QTableWidgetItem(str(row.get('idbonexpedition', ''))))
                table.setItem(i, 3, QTableWidgetItem(str(row.get('dateexpedition', ''))))
        else:
            table.setRowCount(0)
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(['identifiant du colis', 'identifiant du lot', 'id du bon de reception', "date d'expedition"])
            print("Warning: self.data.expedition2_df is not available or empty in MenuExpedition.")


        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #dcdcdc;
                border: 1px solid #D3DCE0;
                font-size: 13px;
                width:90%; /* This width might not behave as expected in a layout */
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 10px 8px;
                border: 1px solid #dcdcdc;
                font-weight: bold;
                font-size: 13px;
                color: #555;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #cce7ff;
                color: #333;
            }
        """)
        table.setAlternatingRowColors(True)
        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        return table

# --- MenuReception Class ---
class MenuReception(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self._main_layout = None # Initialize to None
        self.init_ui()

    def init_ui(self):
        # Clear existing layout if init_ui is called multiple times
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QGridLayout(self)

        layout = self._main_layout
        expedition_summary_table = self.create_expedition_summary_table()
        bouton = QPushButton("chatte")
        bouton.setFixedWidth(500) # This fixed width might constrain layout
        bouton.setStyleSheet("""
            QPushButton { background-color: #006775; color: white; border: none; padding: 50px 16px; border-radius: 15px; font-weight: bold; }
            QPushButton:hover { background-color: #1976D2; }
        """)
        layout.addWidget(expedition_summary_table, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(bouton, 1, 0)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def create_expedition_summary_table(self):
        table = QTableWidget()

        # Ensure expedition2_df exists and is not empty before accessing
        if hasattr(self.data, 'expedition2_df') and not self.data.expedition2_df.empty:
            table.setRowCount(len(self.data.expedition2_df))
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(['identifiant du colis', 'identifiant du lot', 'id du bon de reception', "date d'expedition"])

            for i, (_, row) in enumerate(self.data.expedition2_df.iterrows()):
                table.setItem(i, 0, QTableWidgetItem(str(row.get('identifiant du colis', ''))))
                table.setItem(i, 1, QTableWidgetItem(str(row.get('identifiant du lot', ''))))
                table.setItem(i, 2, QTableWidgetItem(str(row.get('idbonexpedition', ''))))
                table.setItem(i, 3, QTableWidgetItem(str(row.get('dateexpedition', ''))))
        else:
            table.setRowCount(0)
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(['identifiant du colis', 'identifiant du lot', 'id du bon de reception', "date d'expedition"])
            print("Warning: self.data.expedition2_df is not available or empty in MenuReception.")

        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #dcdcdc;
                border: 1px solid #D3DCE0;
                font-size: 13px;
                width:200px; /* This fixed width might constrain layout */
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 10px 8px;
                border: 1px solid #dcdcdc;
                font-weight: bold;
                font-size: 13px;
                color: #555;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #cce7ff;
                color: #333;
            }
        """)

        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        return table

# --- Main application setup (for testing) ---
class DummyData:
    """A dummy class to simulate the 'data' object passed to the widgets."""
    def __init__(self):
        # Create a sample DataFrame for demonstration
        self.expedition2_df = pd.DataFrame({
            'identifiant du colis': ['PCK001', 'PCK002', 'PCK003'],
            'identifiant du lot': ['LOT001', 'LOT001', 'LOT002'],
            'idbonexpedition': ['BONEX001', 'BONEX001', 'BONEX002'],
            'dateexpedition': ['2025-07-01', '2025-07-01', '2025-07-02']
        })

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create dummy data instance
    dummy_data = DummyData()

    # Demonstrate ZoneEmballage
    print("Displaying ZoneEmballage...")
    emballage_window = ZoneEmballage(dummy_data)
    emballage_window.setWindowTitle("Zone Emballage Dashboard")
    emballage_window.setGeometry(100, 100, 800, 600)
    emballage_window.show()

    # Demonstrate MenuExpedition
    print("Displaying MenuExpedition...")
    expedition_window = MenuExpedition(dummy_data)
    expedition_window.setWindowTitle("Menu Expedition")
    expedition_window.setGeometry(950, 100, 700, 500)
    expedition_window.show()

    # Demonstrate MenuReception
    print("Displaying MenuReception...")
    reception_window = MenuReception(dummy_data)
    reception_window.setWindowTitle("Menu Reception")
    reception_window.setGeometry(100, 700, 700, 500)
    reception_window.show()


 
class MenuReception(QWidget):
    """
    A QWidget class for displaying reception-related information,
    specifically a summary table of reception data.
    """

    def __init__(self, data: object):
        """
        Initializes the MenuReception widget.

        Args:
            data: An object expected to have a 'expedition2_df' attribute (DataFrame-like).
                  Note: The original code uses 'expedition2_df' for reception,
                  which might be a logical inconsistency depending on the data source.
        """
        super().__init__()
        self.data = data
        self._main_layout: QGridLayout | None = None
        self.init_ui()

    def init_ui(self) -> None:
        """
        Initializes or re-initializes the user interface for the reception menu.
        It clears any existing layout before setting up new components.
        """
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self._clear_layout(self._main_layout)
        else:
            self._main_layout = QGridLayout(self)

        layout = self._main_layout
        reception_summary_table = self._create_summary_table()
        
        # Example button - consider making text and functionality dynamic
        action_button = QPushButton("Effectuer une action de réception")
        action_button.setStyleSheet("""
            QPushButton {
                background-color: #006775;
                color: white;
                border: none;
                padding: 15px 30px; /* Adjusted padding for better fit with fixed width */
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        # Consider removing fixed width unless absolutely necessary, as it can hinder responsiveness
        action_button.setFixedWidth(500) 
        
        layout.addWidget(reception_summary_table, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(action_button, 1, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter) # Centered the button

    def _clear_layout(self, layout: QLayout) -> None:
        """
        Recursively clears all widgets and layouts from a given layout.

        Args:
            layout (QLayout): The layout to clear.
        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self._clear_layout(item.layout())

    def _create_summary_table(self) -> QTableWidget:
        """
        Creates a QTableWidget to display reception summary data.

        Returns:
            QTableWidget: A styled table widget populated with reception data.
        """
        table = QTableWidget()

        # Ensure data.expedition2_df exists and is iterable
        # NOTE: The original code uses 'expedition2_df' for reception.
        # If reception data comes from a different source, update 'self.data.expedition2_df'
        if hasattr(self.data, 'expedition2_df') and not self.data.expedition2_df.empty:
            table.setRowCount(len(self.data.expedition2_df))
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(['identifiant du colis', 'identifiant du lot', 'id du bon de reception', "date d'expedition"])

            for i, (_, row) in enumerate(self.data.expedition2_df.iterrows()):
                table.setItem(i, 0, QTableWidgetItem(str(row.get('identifiant du colis', ''))))
                table.setItem(i, 1, QTableWidgetItem(str(row.get('identifiant du lot', ''))))
                table.setItem(i, 2, QTableWidgetItem(str(row.get('idbonexpedition', ''))))
                table.setItem(i, 3, QTableWidgetItem(str(row.get('dateexpedition', ''))))
        else:
            table.setRowCount(1)
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(['identifiant du colis', 'identifiant du lot', 'id du bon de reception', "date d'expedition"])
            table.setItem(0, 0, QTableWidgetItem("No Data"))
            table.setSpan(0, 0, 1, 4) # Span across all columns for "No Data" message

        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #dcdcdc;
                border: 1px solid #D3DCE0;
                font-size: 13px;
                width: 90%; /* This is a stylistic preference, actual size depends on layout */
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 10px 8px;
                border: 1px solid #dcdcdc;
                font-weight: bold;
                font-size: 13px;
                color: #555;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #cce7ff;
                color: #333;
            }
        """)

        table.setAlternatingRowColors(True)
        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        return table
class WarehouseMenuInteractionWidget(QWidget):
    """Widget principal de 'Menu interaction' qui regroupe les vues du module warehouse."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        # Clear existing layout if init_ui is called multiple times
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QVBoxLayout(self)

        layout = self._main_layout
        # Titre
        title = QLabel("Warehouse Operations Menu")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        # Onglets
        tabs = QTabWidget()
        #tabs.addTab(MenuReception(self.data), "menu reception")
        tabs.addTab(MenuExpedition(self.data), "menu expedition")
        tabs.addTab(ZoneEmballage(self.data),"zone d'emballage")
        layout.addWidget(tabs)
        layout.addStretch() # Ensure tabs expand
        
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

class StorageSpaceManagementWidget(QWidget):
    """Widget for Storage Space Management"""
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        # Clear existing layout if init_ui is called multiple times
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QVBoxLayout(self)

        layout = self._main_layout
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Storage Space Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # Metric Card for Utilization
        try:
            cur.execute('SELECT "EMIR".cellutilisation();')
            utilization = cur.fetchone()[0]
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching cell utilization: {e}. Using dummy value.")
            utilization = 0.0

        layout.addWidget(MetricCard("Overall Utilization", f"{utilization:.1f}%", "Average Warehouse Utilization"))

        # Placeholder for sub-features
        sub_features_layout = QGridLayout()
        sub_features_layout.addWidget(QLabel("<h3>Cell Optimization</h3><p>Simulate optimal cell assignment.</p>"), 0, 0)
        sub_features_layout.addWidget(QLabel("<h3>Space Allocation</h3><p>Manage space assignments for product categories.</p>"), 0, 1)
        sub_features_layout.addWidget(QLabel("<h3>Layout Management</h3><p>Visualize and modify warehouse layout.</p>"), 1, 0, 1, 2)
        layout.addLayout(sub_features_layout)

        layout.addStretch()
        
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

class ReportsWidget(QWidget):
    """Widget for generating various reports"""
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        # Clear existing layout if init_ui is called multiple times
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            # Créer un QScrollArea comme widget principal
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
            # Créer le widget conteneur et son layout
            self.container_widget = QWidget()
            self._main_layout = QVBoxLayout(self.container_widget)
            
            # Configurer le scroll area
            self.scroll_area.setWidget(self.container_widget)
            super().setLayout(QVBoxLayout())
            super().layout().addWidget(self.scroll_area)
            super().layout().setContentsMargins(0, 0, 0, 0)
    
        layout = self._main_layout
        layout.setContentsMargins(10, 10, 10, 10)  # Ajouter des marges pour le contenu
    
        title = QLabel("Generate Reports")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)
    
        tabs = QTabWidget()
    
        # Stock Reports
        stock_reports_widget = QWidget()
        stock_reports_layout = QVBoxLayout()
        stock_reports_layout.addWidget(QLabel("<h4>Stock Reports</h4>"))
        stock_reports_layout.addWidget(QLabel("Generate reports on current stock levels, low stock items, and inventory value."))
    
        self.stock_summary_table = self.create_stock_summary_table()
        stock_reports_layout.addWidget(self.stock_summary_table)
    
        # Add Save button for Stock Reports
        save_stock_btn = QPushButton("Save Stock Report to CSV")
        save_stock_btn.setStyleSheet("""
            QPushButton {
                background-color: #38A169;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
        """)
        save_stock_btn.clicked.connect(self.save_stock_report_to_csv)
        stock_reports_layout.addWidget(save_stock_btn)
    
        stock_reports_widget.setLayout(stock_reports_layout)
        tabs.addTab(stock_reports_widget, "Stock Reports")
    
        # Performance Reports
        self.performance_reports_widget = PerformanceWidget(self.data)
        tabs.addTab(self.performance_reports_widget, "Performance Reports")
    
        # Exception Reports
        exception_reports_widget = QWidget()
        exception_reports_layout = QVBoxLayout()
        exception_reports_layout.addWidget(QLabel("<h4>Exception Reports</h4>"))
        exception_reports_layout.addWidget(QLabel("View reports on overdue orders, critical low stock, and discrepancies."))
        exception_reports_layout.addWidget(QLabel("<p>No critical low stock items.</p>"))
    
        exception_reports_widget.setLayout(exception_reports_layout)
        tabs.addTab(exception_reports_widget, "Exception Reports")
    
        layout.addWidget(tabs)
        layout.addStretch()
        
        
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def create_stock_summary_table(self):
        table = QTableWidget()
        row_count = len(self.data.inventory_df)
        table.setRowCount(row_count)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Product', 'Category', 'Quantity', 'Current Value'])
    
        # Désactiver complètement les scrollbars
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    
        # Remplir le tableau
        self.stock_summary_data = []
        for i, (_, row) in enumerate(self.data.inventory_df.iterrows()):
            product_info = self.data.products_df[self.data.products_df['ID'] == row['Product_ID']].iloc[0] if not self.data.products_df.empty else {'Category': 'N/A'}
            current_value = row['Quantity'] * row['Value']
            table.setItem(i, 0, QTableWidgetItem(row['Product_Name']))
            table.setItem(i, 1, QTableWidgetItem(product_info['Category']))
            table.setItem(i, 2, QTableWidgetItem(str(row['Quantity'])))
            table.setItem(i, 3, QTableWidgetItem(f"${current_value:,.2f}"))
            self.stock_summary_data.append({
                'Product': row['Product_Name'],
                'Category': product_info['Category'],
                'Quantity': row['Quantity'],
                'Current Value': current_value
            })
    
        # Style et configuration
        table.setStyleSheet("""
            QTableWidget {
<<<<<<< Updated upstream
                border: 1px solid #e0e0e0;
                font-size: 12px;
=======
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #dcdcdc;
                border: 1px solid #D3DCE0;
                font-size: 13px;
>>>>>>> Stashed changes
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 6px;
                font-weight: bold;
            }
        """)
        table.setAlternatingRowColors(True)
        
        # Calculer la hauteur exacte nécessaire
        header_height = table.horizontalHeader().height()
        row_height = 30  # Hauteur moyenne par ligne
        total_height = header_height + (row_count * row_height) + 2  # +2 pour la bordure
        
        # Appliquer la hauteur fixe
        table.setFixedHeight(total_height)
        
        # Configuration des colonnes
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        
        return table
    def save_stock_report_to_csv(self):
        if not self.stock_summary_df.empty:
            options = QFileDialog.Option.DontUseNativeDialog  # option facultative
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save Stock Report",
                "stock_report.csv",
                "CSV Files (*.csv);;All Files (*)",
                options=options
            )
            if file_name:
                try:
                    self.stock_summary_df.to_csv(file_name, index=False)
                    QMessageBox.information(self, "Success", f"Stock report saved to:\n{file_name}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save stock report: {e}")
        else:
            QMessageBox.warning(self, "No Data", "No stock data to save.")

    def save_low_stock_report_to_csv(self):
        if not hasattr(self, 'low_stock_exceptions') or self.low_stock_exceptions.empty:
            QMessageBox.warning(self, "No Data", "No low stock exceptions to save.")
            return

        options = QFileDialog.options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Low Stock Report", "low_stock_report.csv", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            try:
                report_df = self.low_stock_exceptions[['Product_Name', 'Quantity']]
                report_df.to_csv(file_name, index=False)
                QMessageBox.information(self, "Success", f"Low stock report saved to:\n{file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save low stock report: {e}")


class DailyOperationsPlanningWidget(QWidget):
    """Widget for Daily Operations Planning"""
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        # Initialisation du layout principal du widget
        if not hasattr(self, '_main_layout') or self._main_layout is None:
            self._main_layout = QVBoxLayout(self)
        else:
            self.clear_layout(self._main_layout)

        # 1. Créer le QScrollArea
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True) # Permet au contenu de se redimensionner
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame) # Supprime la bordure par défaut du QScrollArea

        # 2. Créer un QWidget "conteneur" pour tout le contenu défilable
        self.scroll_content_widget = QWidget()
        # 3. Créer un layout pour ce conteneur
        self.scroll_content_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_content_layout.setContentsMargins(20, 20, 20, 20) # Marge intérieure pour le contenu défilant
        self.scroll_content_layout.setSpacing(25) # Espacement entre les sections principales

        # 4. Assigner le widget conteneur au QScrollArea
        self.scroll_area.setWidget(self.scroll_content_widget)

        # 5. Ajouter le QScrollArea au layout principal de DailyOperationsPlanningWidget
        self._main_layout.addWidget(self.scroll_area)

        # --- Déplacer tout le contenu existant vers self.scroll_content_layout ---
        title = QLabel("Daily Operations Planning")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2C3E50; margin-bottom: 15px;")
        self.scroll_content_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Incorporate OrdersWidget as a central part of daily planning
        orders_section_label = QLabel("<h4>Order Management (Reception & Expedition)</h4>")
        orders_section_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        self.scroll_content_layout.addWidget(orders_section_label)
        
        self.orders_widget = OrdersWidget(self.data)
        self.scroll_content_layout.addWidget(self.orders_widget)
        self.scroll_content_layout.setStretchFactor(self.orders_widget, 1) # Give orders widget stretch

        # Placeholder for other planning aspects (j'ai ajouté plus de texte ici pour rendre le défilement visible)
        planning_info_label = QLabel("<h3>Planning Tools:</h3>"
                                     "<ul>"
                                     "<li>Schedule Shipments & Receptions</li>"
                                     "<li>Allocate Workforce for Picking/Packing</li>"
                                     "<li>Forecast Demand (using historical data)</li>"
                                     "<li>Optimize Routes for Deliveries</li>"
                                     "<li>Manage Warehouse Inventory Levels</li>"
                                     "<li>Track Employee Performance</li>"
                                     "<li>Generate Daily Operation Reports</li>"
                                     "<li>Integrate with External Systems (ERP, CRM)</li>"
                                     "<li>Handle Exceptions and Delays</li>"
                                     "<li>Automate Repetitive Tasks</li>"
                                     "<li>Visualize Supply Chain Flow</li>"
                                     "<li>Manage Returns and Reverse Logistics</li>"
                                     "<li>Ensure Compliance with Regulations</li>"
                                     "<li>Implement Quality Control Checks</li>"
                                     "<li>Conduct Risk Assessments</li>"
                                     "</ul>")
        planning_info_label.setWordWrap(True) # Pour que le texte long s'enroule
        planning_info_label.setStyleSheet("font-size: 16px; color: #444; line-height: 1.5;")
        self.scroll_content_layout.addWidget(planning_info_label)

        self.scroll_content_layout.addStretch() # Pousse le contenu vers le haut

        # Styles pour le QScrollArea et son contenu interne
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent; /* Rendre l'arrière-plan du QScrollArea transparent */
            }
            QScrollBar:vertical {
                border: none;
                background: #E8EBF0;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
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
            /* Style pour le widget de contenu interne pour lui donner un aspect de carte */
            QWidget#daily_ops_scroll_content_widget { /* Utiliser un nom d'objet spécifique pour le styliser */
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #D3DCE0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05); /* Ombre douce */
            }
        """)
        # Assigner un nom d'objet au widget de contenu pour le styliser spécifiquement
        self.scroll_content_widget.setObjectName("daily_ops_scroll_content_widget")


    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

class OrdersWidget(QWidget):
    """Widget for order management (reception and expedition)"""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        if not hasattr(self, '_main_layout') or self._main_layout is None:
            self._main_layout = QVBoxLayout(self)
        else:
            self.clear_layout(self._main_layout)

        layout = self._main_layout
        layout.setContentsMargins(0, 0, 0, 0) # Adjust margins for nested widget

        # Tab widget for different order types
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { /* The tab widget frame */
                border: 1px solid #D3DCE0;
                border-radius: 8px;
                background-color: #FFFFFF;
            }
            QTabBar::tab {
                background: #EBF2F7;
                border: 1px solid #D3DCE0;
                border-bottom-color: #D3DCE0; /* same as pane color */
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 100px;
                padding: 10px;
                font-weight: bold;
                color: #555;
            }
            QTabBar::tab:selected {
                background: #FFFFFF;
                border-bottom-color: #FFFFFF; /* selected tab has no border on the bottom */
                color: #006775;
            }
            QTabBar::tab:hover {
                background: #E0E5EB;
            }
        """)

        # Reception orders tab
        reception_widget = self.create_reception_tab()
        tabs.addTab(reception_widget, "Reception Orders")

        # Expedition orders tab
        expedition_widget = self.create_expedition_tab()
        tabs.addTab(expedition_widget, "Expedition Orders")

        layout.addWidget(tabs)
        layout.addStretch() # Ensure tabs expand
        
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def create_reception_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15,15,15,15) # Add padding inside tab content

        # Header with metrics
        header_layout = QHBoxLayout()
        title = QLabel("Reception Orders")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Metrics
        metrics_layout = QHBoxLayout()
        try:
            cur.execute("SELECT \"EMIR\".colis_entrants_jour_count();")
            today_rec = cur.fetchone()[0]
            if today_rec is None: today_rec = 0
            cur.execute("SELECT \"EMIR\".valuereception();")
            total_value = cur.fetchone()[0]
            if total_value is None: total_value = 0.0
            cur.execute("SELECT \"EMIR\".avgitemsreception();")
            avg_items = cur.fetchone()[0]
            if avg_items is None: avg_items = 0.0
        except Exception as e:
            print(f"Error fetching reception metrics: {e}")
            today_rec = 0
            total_value = 0.0
            avg_items = 0.0


        metrics_layout.addWidget(MetricCard("Today Receptions", f"{today_rec:,}", "Awaiting Receipt"))
        metrics_layout.addWidget(MetricCard("Total Value", f"${total_value:,.0f}", "All Orders"))
        metrics_layout.addWidget(MetricCard("Avg Items", f"{avg_items:.1f}", "Per Order"))

        # Chart and table
        content_layout = QHBoxLayout()

        # Status chart
        status_chart = ChartWidget(title="Reception Orders by Status", y_label="Number of Orders", x_label="Status")
        if hasattr(self.data, 'reception_df') and not self.data.reception_df.empty:
            self.create_status_chart(status_chart, self.data.reception_df)
        status_chart.setMinimumHeight(250)
        status_chart.setMinimumWidth(300)

        # Orders table
        table = self.create_orders_table(self.data.reception_df)
        table_scroll_area = QScrollArea() # Wrap table in scroll area
        table_scroll_area.setWidgetResizable(True)
        table_scroll_area.setWidget(table)
        table_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        table_scroll_area.setMinimumHeight(200)

        content_layout.addWidget(status_chart, 1)
        content_layout.addWidget(table_scroll_area, 2) # Add scrollable table

        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        layout.addLayout(content_layout)
        layout.addStretch() # Ensure the tab content expands
        return widget

    def create_expedition_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15,15,15,15) # Add padding inside tab content

        # Header with metrics
        header_layout = QHBoxLayout()
        title = QLabel("Expedition Orders")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Metrics
        metrics_layout = QHBoxLayout()

        try:
            cur.execute("SELECT \"EMIR\".colis_sortants_jour_count();")
            today_exp = cur.fetchone()[0]
            if today_exp is None: today_exp = 0
            cur.execute("SELECT \"EMIR\".valueexpedition();")
            total_value = cur.fetchone()[0]
            if total_value is None: total_value = 0.0
            cur.execute("SELECT \"EMIR\".avgitemsexpedition();")
            avg_items = cur.fetchone()[0]
            if avg_items is None: avg_items = 0.0
        except Exception as e:
            print(f"Error fetching expedition metrics: {e}")
            today_exp = 0
            total_value = 0.0
            avg_items = 0.0

        metrics_layout.addWidget(MetricCard("Today Expeditions", f"{today_exp:,}", "Ready to Ship"))
        metrics_layout.addWidget(MetricCard("Total Value", f"${total_value:,.0f}", "All Orders"))
        metrics_layout.addWidget(MetricCard("Avg Items", f"{avg_items:.1f}", "Per Order"))

        # Chart and table
        content_layout = QHBoxLayout()

        # Status chart
        status_chart = ChartWidget(title="Expedition Orders by Status", y_label="Number of Orders", x_label="Status")
        if hasattr(self.data, 'expedition_df') and not self.data.expedition_df.empty:
            self.create_status_chart(status_chart, self.data.expedition_df)
        status_chart.setMinimumHeight(250)
        status_chart.setMinimumWidth(300)

        # Orders table
        table = self.create_orders_table(self.data.expedition_df, is_expedition=True)
        table_scroll_area = QScrollArea() # Wrap table in scroll area
        table_scroll_area.setWidgetResizable(True)
        table_scroll_area.setWidget(table)
        table_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        table_scroll_area.setMinimumHeight(200)

        content_layout.addWidget(status_chart, 1)
        content_layout.addWidget(table_scroll_area, 2) # Add scrollable table

        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        layout.addLayout(content_layout)
        layout.addStretch() # Ensure tab content expands
        return widget

    def create_status_chart(self, chart_widget, df):
        # Cette méthode dépend de `numpy` et `pyqtgraph`.
        # Assurez-vous qu'ils sont installés et importés en haut de votre fichier.
        # Si vous n'avez pas pyqtgraph/numpy, ce code peut nécessiter une adaptation.
        if isinstance(np, type) and np.__name__ == 'MockNp': # Check if it's our mock
            chart_widget.layout().addWidget(QLabel("Charting library (pyqtgraph/numpy) not found.", alignment=Qt.AlignmentFlag.AlignCenter))
            return

        try:
            status_counts = df['Status'].value_counts()
            x_vals = np.arange(len(status_counts))
            y_vals = status_counts.values
            
            colors = [QColor('#38A169'), QColor('#E77E23'), QColor('#006775'), QColor('#9C27B0')]
            brushes = [colors[i % len(colors)] for i in range(len(x_vals))]

            bargraph = pg.BarGraphItem(x=x_vals, height=y_vals, width=0.6, brushes=brushes)
            chart_widget.addItem(bargraph)

            ticks = [(i, label) for i, label in enumerate(status_counts.index)]
            chart_widget.getAxis('bottom').setTicks([ticks])
            
            for i, value in enumerate(y_vals):
                text_item = pg.TextItem(text=f'{int(value)}', anchor=(0.5, 0), color='k')
                text_item.setPos(x_vals[i], value + 0.1)
                chart_widget.addItem(text_item)
            
            # Assurez-vous que chart_widget.plotItem et ses sous-attributs existent et sont configurés correctement dans votre ChartWidget
            chart_widget.plotItem.setTitle(chart_widget.plotItem.titleLabel.text)
            chart_widget.plotItem.setLabel('left', 'Number of Orders')
        except Exception as e:
            print(f"Error creating chart: {e}")
            chart_widget.layout().addWidget(QLabel(f"Error rendering chart: {e}", alignment=Qt.AlignmentFlag.AlignCenter))


    def create_orders_table(self, df, is_expedition=False):
        table = QTableWidget()
        table.setRowCount(len(df))

        if is_expedition:
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(['Order ID', 'Destination', 'Request Date', 'Items', 'Status', 'Value'])
            date_col = 'Request_Date'
            location_col = 'Destination'
        else:
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(['Order ID', 'Supplier', 'Expected Date', 'Items', 'Status', 'Value'])
            date_col = 'Expected_Date'
            location_col = 'Supplier'

        for i, (_, row) in enumerate(df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(str(row['Order_ID'])))
            table.setItem(i, 1, QTableWidgetItem(str(row[location_col])))
            table.setItem(i, 2, QTableWidgetItem(str(row[date_col])))
            table.setItem(i, 3, QTableWidgetItem(str(row['Items_Count'])))

            status_item = QTableWidgetItem(str(row['Status']))
            if row['Status'] == 'Pending':
                status_item.setBackground(QColor('#FFF3E0'))
            elif row['Status'] == 'Processing':
                status_item.setBackground(QColor('#E3F2FD'))
            elif row['Status'] == 'Received' or row['Status'] == 'In Transit' or row['Status'] == 'Completed':
                status_item.setBackground(QColor('#E8F5E8'))

            table.setItem(i, 4, status_item)
            table.setItem(i, 5, QTableWidgetItem(f"${row['Total_Value']:,.0f}"))

        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #dcdcdc;
                border: 1px solid #D3DCE0;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 10px 8px;
                border: 1px solid #dcdcdc;
                font-weight: bold;
                font-size: 13px;
                color: #555;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #cce7ff;
                color: #333;
            }
        """)

        table.setAlternatingRowColors(True)
        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)

        return table

class OrdersWidget(QWidget):
    """Widget for order management (reception and expedition)"""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        # Clear existing layout if init_ui is called multiple times
        if not hasattr(self, '_main_layout') or self._main_layout is None:
            self._main_layout = QVBoxLayout(self)
        else:
            self.clear_layout(self._main_layout)

        # Create a QScrollArea for the OrdersWidget content
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame) # No border for the scroll area

        # Create a container widget for all the content that needs to be scrollable
        self.scroll_content_widget = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_content_layout.setContentsMargins(10, 10, 10, 10) # Add some padding inside
        self.scroll_content_layout.setSpacing(20) # Spacing between sections

        self.scroll_area.setWidget(self.scroll_content_widget)

        # Add the scroll area to the main layout of OrdersWidget
        self._main_layout.addWidget(self.scroll_area)


        # Tab widget for different order types (moved inside scroll_content_layout)
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { /* The tab widget frame */
                border: 1px solid #D3DCE0;
                border-radius: 8px;
                background-color: #FFFFFF;
                margin-top: -1px; /* Overlap with tab bar border */
            }
            QTabBar::tab {
                background: #EBF2F7;
                border: 1px solid #D3DCE0;
                border-bottom-color: #D3DCE0;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 120px; /* Slightly wider tabs */
                padding: 10px 15px; /* More padding */
                font-weight: bold;
                color: #555;
            }
            QTabBar::tab:selected {
                background: #FFFFFF;
                border-bottom-color: #FFFFFF;
                color: #006775;
                margin-bottom: -1px; /* Visually connect selected tab to content */
            }
            QTabBar::tab:hover {
                background: #E0E5EB;
            }
        """)

        reception_widget = self.create_reception_tab()
        tabs.addTab(reception_widget, "Reception Orders")

        expedition_widget = self.create_expedition_tab()
        tabs.addTab(expedition_widget, "Expedition Orders")

        self.scroll_content_layout.addWidget(tabs)
        self.scroll_content_layout.addStretch() # Ensure tabs expand

        # Styling for the scroll area within OrdersWidget
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 8px; /* Thinner scrollbar */
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #C0C0C0; /* Lighter handle */
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QWidget#orders_scroll_content_widget { /* Specific style for this content widget */
                background-color: #F8F9FA; /* Slightly off-white background */
                border-radius: 10px;
                border: 1px solid #E0E0E0;
                padding: 5px; /* Less padding, as tabs have their own */
            }
        """)
        self.scroll_content_widget.setObjectName("orders_scroll_content_widget") # Set object name for styling

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def create_reception_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15,15,15,15) # Add padding inside tab content
        layout.setSpacing(15) # Spacing within tab

        header_layout = QHBoxLayout()
        title = QLabel("Reception Orders")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15) # Spacing between metric cards
        try:
            cur.execute("SELECT \"EMIR\".colis_entrants_jour_count();")
            today_rec = cur.fetchone()[0]
            if today_rec is None: today_rec = 0
            cur.execute("SELECT \"EMIR\".valuereception();")
            total_value = cur.fetchone()[0]
            if total_value is None: total_value = 0.0
            cur.execute("SELECT \"EMIR\".avgitemsreception();")
            avg_items = cur.fetchone()[0]
            if avg_items is None: avg_items = 0.0
        except Exception as e:
            print(f"Error fetching reception metrics: {e}")
            today_rec = 0
            total_value = 0.0
            avg_items = 0.0

        metrics_layout.addWidget(MetricCard("Today Receptions", f"{today_rec:,}", "Awaiting Receipt"))
        metrics_layout.addWidget(MetricCard("Total Value", f"${total_value:,.0f}", "All Orders"))
        metrics_layout.addWidget(MetricCard("Avg Items", f"{avg_items:.1f}", "Per Order"))

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20) # Spacing between chart and table

        status_chart = ChartWidget(title="Reception Orders by Status", y_label="Number of Orders", x_label="Status")
        if hasattr(self.data, 'reception_df') and not self.data.reception_df.empty:
            self.create_status_chart(status_chart, self.data.reception_df)
        status_chart.setMinimumHeight(280) # Slightly taller chart
        status_chart.setMinimumWidth(350) # Wider chart
        status_chart.setStyleSheet("border: 1px solid #E0E0E0; border-radius: 8px;") # Border for chart

        table = self.create_orders_table(self.data.reception_df)
        # Table is already wrapped in a scroll area, no need for an outer one here
        # The table's own scroll area handles its content.
        table_scroll_area = QScrollArea()
        table_scroll_area.setWidgetResizable(True)
        table_scroll_area.setWidget(table)
        table_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        table_scroll_area.setMinimumHeight(250) # Slightly taller table area
        table_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E0E0E0; /* Border for the table scroll area */
                border-radius: 8px;
                background-color: #FFFFFF;
            }
            QScrollBar:vertical {
                border: none;
                background: #F0F0F0;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #C8C8C8;
                border-radius: 4px;
            }
        """)


        content_layout.addWidget(status_chart, 1)
        content_layout.addWidget(table_scroll_area, 2)

        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        layout.addLayout(content_layout)
        layout.addStretch()
        return widget

    def create_expedition_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15,15,15,15)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        title = QLabel("Expedition Orders")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)

        try:
            cur.execute("SELECT \"EMIR\".colis_sortants_jour_count();")
            today_exp = cur.fetchone()[0]
            if today_exp is None: today_exp = 0
            cur.execute("SELECT \"EMIR\".valueexpedition();")
            total_value = cur.fetchone()[0]
            if total_value is None: total_value = 0.0
            cur.execute("SELECT \"EMIR\".avgitemsexpedition();")
            avg_items = cur.fetchone()[0]
            if avg_items is None: avg_items = 0.0
        except Exception as e:
            print(f"Error fetching expedition metrics: {e}")
            today_exp = 0
            total_value = 0.0
            avg_items = 0.0

        metrics_layout.addWidget(MetricCard("Today Expeditions", f"{today_exp:,}", "Ready to Ship"))
        metrics_layout.addWidget(MetricCard("Total Value", f"${total_value:,.0f}", "All Orders"))
        metrics_layout.addWidget(MetricCard("Avg Items", f"{avg_items:.1f}", "Per Order"))

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        status_chart = ChartWidget(title="Expedition Orders by Status", y_label="Number of Orders", x_label="Status")
        if hasattr(self.data, 'expedition_df') and not self.data.expedition_df.empty:
            self.create_status_chart(status_chart, self.data.expedition_df)
        status_chart.setMinimumHeight(280)
        status_chart.setMinimumWidth(350)
        status_chart.setStyleSheet("border: 1px solid #E0E0E0; border-radius: 8px;")

        table = self.create_orders_table(self.data.expedition_df, is_expedition=True)
        table_scroll_area = QScrollArea()
        table_scroll_area.setWidgetResizable(True)
        table_scroll_area.setWidget(table)
        table_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        table_scroll_area.setMinimumHeight(250)
        table_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: #FFFFFF;
            }
            QScrollBar:vertical {
                border: none;
                background: #F0F0F0;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #C8C8C8;
                border-radius: 4px;
            }
        """)

        content_layout.addWidget(status_chart, 1)
        content_layout.addWidget(table_scroll_area, 2)

        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        layout.addLayout(content_layout)
        layout.addStretch()
        return widget

    def create_status_chart(self, chart_widget, df):
        if isinstance(np, type) and np.__name__ == 'MockNp':
            chart_widget.layout().addWidget(QLabel("Charting library (pyqtgraph/numpy) not found.", alignment=Qt.AlignmentFlag.AlignCenter))
            return

        try:
            status_counts = df['Status'].value_counts()
            if status_counts.empty: # Handle empty DataFrame case
                chart_widget.layout().addWidget(QLabel("No data to display.", alignment=Qt.AlignmentFlag.AlignCenter))
                return

            x_vals = np.arange(len(status_counts))
            y_vals = status_counts.values
            
            colors = [QColor('#38A169'), QColor('#E77E23'), QColor('#006775'), QColor('#9C27B0'), QColor('#DC3545')] # Added a color for 'Cancelled'/'Failed'
            brushes = [colors[i % len(colors)] for i in range(len(x_vals))]

            bargraph = pg.BarGraphItem(x=x_vals, height=y_vals, width=0.6, brushes=brushes)
            chart_widget.addItem(bargraph)

            ticks = [(i, label) for i, label in enumerate(status_counts.index)]
            chart_widget.getAxis('bottom').setTicks([ticks])
            chart_widget.plotItem.setYRange(0, max(y_vals) * 1.2 if y_vals.size > 0 else 1) # Adjust Y range safely
            
            for i, value in enumerate(y_vals):
                text_item = pg.TextItem(text=f'{int(value)}', anchor=(0.5, 0), color='k')
                text_item.setPos(x_vals[i], value + 0.1)
                chart_widget.addItem(text_item)
            
            chart_widget.plotItem.setTitle(chart_widget.plotItem.titleLabel.text)
            chart_widget.plotItem.setLabel('left', 'Number of Orders')
        except Exception as e:
            print(f"Error creating chart: {e}")
            chart_widget.layout().addWidget(QLabel(f"Error rendering chart: {e}", alignment=Qt.AlignmentFlag.AlignCenter))

    def create_orders_table(self, df, is_expedition=False):
        table = QTableWidget()
        table.setRowCount(len(df))

        if is_expedition:
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(['Order ID', 'Destination', 'Request Date', 'Items', 'Status', 'Value'])
            date_col = 'Request_Date'
            location_col = 'Destination'
        else:
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(['Order ID', 'Supplier', 'Expected Date', 'Items', 'Status', 'Value'])
            date_col = 'Expected_Date'
            location_col = 'Supplier'

        for i, (_, row) in enumerate(df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(str(row['Order_ID'])))
            table.setItem(i, 1, QTableWidgetItem(str(row[location_col])))
            table.setItem(i, 2, QTableWidgetItem(str(row[date_col])))
            table.setItem(i, 3, QTableWidgetItem(str(row['Items_Count'])))

            status_item = QTableWidgetItem(str(row['Status']))
            # Enhanced color coding for various statuses
            if row['Status'] == 'Pending':
                status_item.setBackground(QColor('#FFECB3')) # Light Orange
            elif row['Status'] == 'Processing':
                status_item.setBackground(QColor('#BBDEFB')) # Light Blue
            elif row['Status'] == 'Received' or row['Status'] == 'Completed':
                status_item.setBackground(QColor('#C8E6C9')) # Light Green
            elif row['Status'] == 'In Transit':
                status_item.setBackground(QColor('#DCEDC8')) # Light Green-Yellow
            elif row['Status'] == 'Cancelled' or row['Status'] == 'Failed': # New status colors
                status_item.setBackground(QColor('#FFCDD2')) # Light Red

            table.setItem(i, 4, status_item)
            table.setItem(i, 5, QTableWidgetItem(f"${row['Total_Value']:,.0f}"))

        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f8f8; /* Slightly different alternate row */
                selection-background-color: #e3f2fd;
                gridline-color: #e0e0e0; /* Lighter grid lines */
                border: none; /* No border directly on the table, it's on the scroll area */
                font-size: 13px;
                border-radius: 8px; /* Match scroll area border-radius */
            }
            QHeaderView::section {
                background-color: #EFEFF3; /* Lighter header background */
                padding: 10px 8px;
                border: 1px solid #dcdcdc;
                border-left: none; /* Remove left border for clean look */
                border-right: none; /* Remove right border */
                font-weight: bold;
                font-size: 13px;
                color: #555;
            }
            QHeaderView::section:first { border-left: 1px solid #dcdcdc; border-top-left-radius: 8px; }
            QHeaderView::section:last { border-right: 1px solid #dcdcdc; border-top-right-radius: 8px; }

            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #cce7ff;
                color: #333;
            }
        """)

        table.setAlternatingRowColors(True)
        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)

        return table
class PerformanceWidget(QWidget):
    """Widget for Performance Metrics and Analytics"""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        if not hasattr(self, '_main_layout') or self._main_layout is None:
            self._main_layout = QVBoxLayout(self)
        else:
            self.clear_layout(self._main_layout)

        # Create a QScrollArea for the PerformanceWidget content
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Create a container widget for all scrollable content
        self.scroll_content_widget = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_content_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll_content_layout.setSpacing(25) # More spacing between sections

        self.scroll_area.setWidget(self.scroll_content_widget)
        self._main_layout.addWidget(self.scroll_area)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Performance Analytics")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2C3E50;")

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("<b>From:</b>")) # Bold label
        from_date = QDateEdit(QDate.currentDate().addDays(-30))
        from_date.setCalendarPopup(True)
        from_date.setStyleSheet("""
            QDateEdit {
                border: 1px solid #D3DCE0;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #D3DCE0;
                image: url(path/to/calendar_icon.png); /* Replace with your icon */
            }
            QDateEdit::down-arrow {
                image: url(path/to/arrow_down_icon.png); /* Replace with your icon */
            }
        """)
        date_layout.addWidget(from_date)

        date_layout.addWidget(QLabel("<b>To:</b>")) # Bold label
        to_date = QDateEdit(QDate.currentDate())
        to_date.setCalendarPopup(True)
        to_date.setStyleSheet(from_date.styleSheet()) # Apply same style
        date_layout.addWidget(to_date)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addLayout(date_layout)
        self.scroll_content_layout.addLayout(header_layout) # Add header to scroll content

        # KPI Cards
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20) # Spacing between KPI cards
        kpi_layout.setContentsMargins(0, 10, 0, 10) # Vertical margins around KPI section

        # Calculate KPIs from recent data
        if hasattr(self.data, 'daily_metrics') and not self.data.daily_metrics.empty:
            recent_data = self.data.daily_metrics.tail(30)
            avg_received = recent_data['Items_Received'].mean() if not recent_data.empty else 0
            avg_shipped = recent_data['Items_Shipped'].mean() if not recent_data.empty else 0
            avg_utilization = recent_data['Storage_Utilization'].mean() if not recent_data.empty else 0
            avg_fulfillment = recent_data['Order_Fulfillment_Rate'].mean() if not recent_data.empty else 0
        else:
            avg_received = avg_shipped = avg_utilization = avg_fulfillment = 0 # Default if no data

        kpi_layout.addWidget(MetricCard("Daily Received", f"{avg_received:.0f}", "Avg Last 30 days"))
        kpi_layout.addWidget(MetricCard("Daily Shipped", f"{avg_shipped:.0f}", "Avg Last 30 days"))
        kpi_layout.addWidget(MetricCard("Storage Utilization", f"{avg_utilization:.1f}%", "Current Average"))
        kpi_layout.addWidget(MetricCard("Fulfillment Rate", f"{avg_fulfillment:.1f}%", "Order Success"))
        self.scroll_content_layout.addLayout(kpi_layout) # Add KPI cards to scroll content

        # Charts
        charts_layout = QGridLayout()
        charts_layout.setContentsMargins(0, 15, 0, 0) # Top margin for charts section
        charts_layout.setSpacing(20) # Spacing between charts

        trend_chart = ChartWidget(parent=self.scroll_content_widget, title='Daily Operations Trend (Last 30 Days)', y_label='Items Count', x_label='Date',
                                  axisItems={'bottom': pg.DateAxisItem()})
        if hasattr(self.data, 'daily_metrics') and not self.data.daily_metrics.empty:
            self.create_trend_chart(trend_chart)
        trend_chart.setMinimumHeight(350) # Taller charts
        trend_chart.setStyleSheet("border: 1px solid #E0E0E0; border-radius: 8px;")
        charts_layout.addWidget(trend_chart, 0, 0)

        utilization_chart = ChartWidget(parent=self.scroll_content_widget, title='Storage Utilization by Zone', y_label='Utilization %', x_label='Zone')
        if hasattr(self.data, 'daily_metrics') and not self.data.daily_metrics.empty:
            self.create_utilization_chart(utilization_chart)
        utilization_chart.setMinimumHeight(350)
        utilization_chart.setStyleSheet("border: 1px solid #E0E0E0; border-radius: 8px;")
        charts_layout.addWidget(utilization_chart, 0, 1)

        fulfillment_chart = ChartWidget(parent=self.scroll_content_widget, title='Weekly Fulfillment Rate Trend', y_label='Fulfillment Rate %', x_label='Week',
                                        axisItems={'bottom': pg.DateAxisItem()})
        if hasattr(self.data, 'daily_metrics') and not self.data.daily_metrics.empty:
            self.create_fulfillment_chart(fulfillment_chart)
        fulfillment_chart.setMinimumHeight(350)
        fulfillment_chart.setStyleSheet("border: 1px solid #E0E0E0; border-radius: 8px;")
        charts_layout.addWidget(fulfillment_chart, 1, 0, 1, 2) # Span across two columns

        self.scroll_content_layout.addLayout(charts_layout) # Add charts to scroll content
        self.scroll_content_layout.addStretch() # Ensure content expands vertically

        # Styling for the scroll area within PerformanceWidget
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #C0C0C0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QWidget#performance_scroll_content_widget {
                background-color: #F8F9FA;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03); /* Lighter shadow */
            }
        """)
        self.scroll_content_widget.setObjectName("performance_scroll_content_widget") # Set object name for styling


    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def create_trend_chart(self, chart_widget):
        if isinstance(np, type) and np.__name__ == 'MockNp': return

        recent_data = self.data.daily_metrics.tail(30)
        if recent_data.empty: return

        x_vals = recent_data['Date'].apply(lambda x: x.timestamp()).values
        chart_widget.plot(x_vals, recent_data['Items_Received'].to_numpy(), pen=pg.mkPen(color='#38A169', width=2), name='Received')
        chart_widget.plot(x_vals, recent_data['Items_Shipped'].to_numpy(), pen=pg.mkPen(color='#006775', width=2), name='Shipped')
        
        chart_widget.plotItem.addLegend()
        # The axisItems {'bottom': pg.DateAxisItem()} already handles setting the DateAxisItem
        # chart_widget.plotItem.setLabel('bottom', 'Date', axisClass=pg.DateAxisItem) # Redundant due to axisItems init
        
        # Ensure correct y-range handling for empty data
        y_max = recent_data[['Items_Received', 'Items_Shipped']].max().max()
        chart_widget.plotItem.setYRange(0, y_max * 1.1 if y_max > 0 else 1)


    def create_utilization_chart(self, chart_widget):
        if isinstance(np, type) and np.__name__ == 'MockNp': return
        # Storage utilization by zone (simulated or from data if available)
        if hasattr(self.data, 'storage_utilization_data'): # Assuming you might have this in self.data
            zones = self.data.storage_utilization_data['Zone'].tolist()
            utilization = self.data.storage_utilization_data['Utilization'].tolist()
        else: # Fallback to simulated if not in data
            zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E', 'Zone F'] # More zones
            utilization = [85, 72, 91, 68, 78, 88]
        
        if not zones: return # No data to plot

        x_vals = np.arange(len(zones))
        y_vals = np.array(utilization)

        colors = [QColor('#FF5722') if u > 85 else QColor('#E77E23') if u > 75 else QColor('#38A169') for u in utilization]
        brushes = [color for color in colors]

        bargraph = pg.BarGraphItem(x=x_vals, height=y_vals, width=0.6, brushes=brushes)
        chart_widget.addItem(bargraph)

        ticks = [(i, label) for i, label in enumerate(zones)]
        chart_widget.getAxis('bottom').setTicks([ticks])
        chart_widget.plotItem.setYRange(0, 100)
        
        target_line = pg.InfiniteLine(80, angle=0, pen=pg.mkPen('r', width=2, style=Qt.PenStyle.DashLine), movable=False)
        chart_widget.addItem(target_line)
        target_label = pg.TextItem("Target (80%)", color='r', anchor=(0.5, 0))
        target_label.setPos(x_vals[-1], 80)
        chart_widget.addItem(target_label)

        for i, value in enumerate(y_vals):
            text_item = pg.TextItem(text=f'{int(value)}%', anchor=(0.5, 0), color='k')
            text_item.setPos(x_vals[i], value + 1)
            chart_widget.addItem(text_item)
            
    def create_fulfillment_chart(self, chart_widget):
        if isinstance(np, type) and np.__name__ == 'MockNp': return

        if hasattr(self.data, 'daily_metrics') and not self.data.daily_metrics.empty:
            weekly_data = self.data.daily_metrics.copy()
            weekly_data['Week'] = weekly_data['Date'].dt.to_period('W').dt.start_time
            
            weekly_summary = weekly_data.groupby('Week').agg({
                'Order_Fulfillment_Rate': 'mean'
            }).reset_index()
            
            if weekly_summary.empty: return

            x_vals = weekly_summary['Week'].apply(lambda x: x.timestamp()).values
            y_vals = weekly_summary['Order_Fulfillment_Rate'].values

            chart_widget.plot(x_vals, y_vals, pen=pg.mkPen(color='#9C27B0', width=2), symbol='o', symbolSize=8, symbolBrush='#9C27B0')
            chart_widget.plotItem.setTitle('Weekly Fulfillment Rate Trend')
            chart_widget.plotItem.setLabel('left', 'Fulfillment Rate %')
            # chart_widget.plotItem.setLabel('bottom', 'Week', axisClass=pg.DateAxisItem) # Redundant
            
            y_min = min(y_vals) if y_vals.size > 0 else 0
            y_max = max(y_vals) if y_vals.size > 0 else 1
            chart_widget.plotItem.setYRange(y_min * 0.9, y_max * 1.1)
        else:
            print("No daily_metrics data for fulfillment chart.")


# Your ChartWidget class (unmodified, but included for completeness)
class ChartWidget(pg.PlotWidget):
    def __init__(self, parent=None, title="", y_label="", x_label="", axisItems=None):
        super().__init__(parent=parent, axisItems=axisItems)
        self.plotItem.setTitle(title)
        self.plotItem.setLabel('left', y_label)
        self.plotItem.setLabel('bottom', x_label)
        self.plotItem.showGrid(x=True, y=True, alpha=0.3)
        self.setBackground('w')
        self.setAntialiasing(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(200, 200)

    def plot_data(self, *args, **kwargs):
        self.clear()
        self.plot(*args, **kwargs)

    def add_item(self, item):
        self.addItem(item)
        
class ChartWidget(pg.PlotWidget):
    def __init__(self, parent=None, title="", y_label="", x_label="", axisItems=None):
        super().__init__(parent=parent, axisItems=axisItems)
        self.plotItem.setTitle(title)
        self.plotItem.setLabel('left', y_label)
        self.plotItem.setLabel('bottom', x_label)
        self.plotItem.showGrid(x=True, y=True, alpha=0.3)
        self.setBackground('w')
        self.setAntialiasing(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(200, 200)

    def plot_data(self, *args, **kwargs):
        self.clear()
        self.plot(*args, **kwargs)

    def add_item(self, item):
        self.addItem(item)

class MainDashboardWidget(QWidget):
    """Dashboard with sidebar menu and top bar"""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.current_widget = None
        self.is_menu_expanded = True
        self.init_ui()

    def init_ui(self):
        # Main vertical layout (top bar + content)
        main_vertical_layout = QVBoxLayout(self)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        main_vertical_layout.setSpacing(0)

        # Top bar
        top_bar = QWidget()
        top_bar.setFixedHeight(50)
        top_bar.setStyleSheet("""
            background-color: #2c3e50;
            border-bottom: 1px solid #1a2a3a;
        """)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 0, 20, 0)

        # Menu toggle button
        self.toggle_btn = QPushButton("≡")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: #2c3e50;
                color: white;
                font-size: 40px;
                margin-left: 2px;
                margin-right: 5px;
                margin-bottom: 2px;
                padding: 10px;
                border: none;
            }
            QPushButton:hover {
                background: #3d566e;
            }
        """)

        # Title
        title_label = QLabel("Warehouse Manager Dashboard")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)

        top_bar_layout.addWidget(self.toggle_btn)
        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch()
        main_vertical_layout.addWidget(top_bar)

        # Content area (sidebar + main content)
        content_horizontal_layout = QHBoxLayout()
        content_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        content_horizontal_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
            border-right: 1px solid #1a2a3a;
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.toggle_btn.clicked.connect(self.toggle_menu)

        # Menu items
        self.menu_buttons = []
        menu_items = [
            ("Real-time Inventory", "list"),
            ("Daily Operations Planning", "calendar"),
            ("Storage Space Management", "box"), 
            ("Generate Reports", "file-text"),
            ("Warehouse Interactions", "activity"),
            ("Logout", "system-log-out")  # Ajouté ici
        ]

        for text, icon in menu_items:
            btn = QPushButton(text)
            btn.setIcon(QIcon.fromTheme(icon))

            # Style différent pour le bouton Logout
            if text == "Logout":
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 13px 15px;
                        color: white;
                        border: none;
                        border-left: 4px solid transparent;
                    }
                    QPushButton:hover {
                        background: #34495e;
                        border-left: 4px solid #ff0000;
                    }
                """)
                btn.clicked.connect(self.logout)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 13px 15px;
                        color: white;
                        border: none;
                        border-left: 4px solid transparent;
                    }
                    QPushButton:hover {
                        background: #34495e;
                        border-left: 4px solid #3498db;
                    }
                """)
                btn.clicked.connect(lambda _, t=text: self.switch_content(t))

            self.menu_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        # Metrics widget
        metrics_widget = QWidget()
        metrics_widget.setStyleSheet("""
            background: #34495e; 
            margin: 10px; 
            border-radius: 5px;
        """)
        metrics_layout = QVBoxLayout(metrics_widget)
        metrics_layout.setContentsMargins(10, 10, 10, 10)
        try:
            cur.execute("SELECT \"EMIR\".total();")
            total_items = cur.fetchone()[0] or 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching total_items: {e}")
            total_items = 0
        try:
            cur.execute("SELECT \"EMIR\".valeur();")
            total_value = cur.fetchone()[0] or 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching total_value: {e}")
            total_value = 0

        try:
            cur.execute("SELECT \"EMIR\".available_cells();")
            available_cells = cur.fetchone()[0] or 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching available_cells: {e}")
            available_cells = 0


        # Add metrics data
        metrics_layout.addWidget(self.create_metric_label("Quick Stats"))
        metrics_layout.addWidget(self.create_metric_item("Total Items", f"{total_items:,}"))
        metrics_layout.addWidget(self.create_metric_item("Total Value", f"${total_value}"))
        metrics_layout.addWidget(self.create_metric_item("Available Cells", f"{available_cells}"))

        # Insérer les métriques avant le bouton Logout
        sidebar_layout.insertWidget(len(menu_items) - 1, metrics_widget)
        sidebar_layout.addStretch(1)  # Ajoute un stretch pour pousser Logout en bas

        # Main content area
        self.content_area = QWidget()
        self.content_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        self.content_area.setStyleSheet("background: #ecf0f1;")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        # Add widgets to layouts
        content_horizontal_layout.addWidget(self.sidebar)
        content_horizontal_layout.addWidget(self.content_area, 1)
        main_vertical_layout.addLayout(content_horizontal_layout, 1)

        # Show default widget
        self.switch_content("Real-time Inventory")

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
            parent_window = self.window()
            if parent_window is not self:
                parent_window.close()
            import login as login
            self.loginpage = login.FlipCard()
            self.loginpage.show()

    def create_metric_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold; color: #bdc3c7;")
        return label

    def create_metric_item(self, name, value):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 5, 0, 5)

        name_label = QLabel(name)
        name_label.setStyleSheet("color: #bdc3c7;")

        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-weight: bold;")

        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(value_label)

        return widget

    def toggle_menu(self):
        self.is_menu_expanded = not self.is_menu_expanded
        if self.is_menu_expanded:
            self.sidebar.setFixedWidth(220)
            self.sidebar.show()
        else:
            self.sidebar.setFixedWidth(0)

    def switch_content(self, menu_item):
        if self.current_widget:
            self.current_widget.deleteLater()

        if menu_item == "Real-time Inventory":
            widget = RealtimeInventoryViewWidget(self.data)
        elif menu_item == "Daily Operations Planning":
            widget = DailyOperationsPlanningWidget(self.data)
        elif menu_item == "Storage Space Management":
            widget = StorageSpaceManagementWidget(self.data)
        elif menu_item == "Generate Reports":
            widget = ReportsWidget(self.data)
        elif menu_item == "Warehouse Interactions":
            widget = WarehouseMenuInteractionWidget(self.data)

        self.current_widget = widget
        self.content_layout.addWidget(widget)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warehouse Management System - Manager Dashboard")
        self.setGeometry(100, 100, 1200, 800)

        self.data = WarehouseData()
        
        # Widget central avec seulement le dashboard
        self.central_widget = MainDashboardWidget(self.data)
        self.setCentralWidget(self.central_widget)

        # Timer pour le rafraîchissement des données
        #self.timer = QTimer(self)
        #self.timer.setInterval(60000) # 1 minute
        #self.timer.timeout.connect(self.refresh_data)
        #self.timer.start()

    def refresh_data(self):
        print("Refreshing data...")
        self.data.generate_sample_data()
        if hasattr(self.central_widget, 'init_ui'):
            self.central_widget.init_ui()
        print("UI update complete.")
        
        

if __name__ == '__main__':
    # It is recommended to install PySide6 as the primary Qt binding for pyqtgraph
    # if you encounter issues with PyQt6 and matplotlib extras.
    # pip install PySide6
    # pip install pyqtgraph

    app = QApplication(sys.argv)

    # Apply a modern style (optional)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f5f5f5"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#2D3748"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f0f0f0"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, QColor("#2D3748"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#D3DCE0"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#2D3748"))
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor("#006775"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#006775"))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

    app.setPalette(palette)

    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())