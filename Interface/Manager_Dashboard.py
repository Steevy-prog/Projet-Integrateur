import sys
import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt6.QtGui import QIcon, QPixmap, QPen, QPainter, QColor, QPalette, QFont
from PyQt6.QtCore import QRectF, Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup, QDate, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QWidget, QTableWidget, QTableWidgetItem, QFormLayout,
    QLineEdit, QComboBox, QDialog, QSpinBox, QListWidget, QSizePolicy, QSplitter,
    QMessageBox, QGridLayout, QFileDialog, QTabWidget, QDateEdit, QProgressBar,
    QHeaderView, QGroupBox
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QGraphicsBlurEffect

import datetime
import random
import psycopg2

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
    print("You have chosen the Steevy's database.")
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

cur.execute("SELECT (p).* FROM \"EMIR\".colis_eva() AS p;")
colis_db = cur.fetchall() # Existing packages from the database

cur.execute("SELECT (p).* FROM \"EMIR\".Pcolis_eva1() AS p;")
pcolis_db = cur.fetchall() # Existing packages from the database

cur.execute("SELECT (p).* FROM \"EMIR\".contenucolis_eva() AS p;")
contenu = cur.fetchall() # Existing packages from the database

cur.execute("SELECT (p).* FROM \"EMIR\".Pcontenucolis_eva() AS p;")
pcontenu = cur.fetchall() # Existing packages from the database

cur.execute("SELECT (p).* FROM \"EMIR\".Produit_EVA() AS p;")
produits_db = cur.fetchall() # Existing products from the database

# Fetch workers for assignment
cur.execute("SELECT (w).* FROM \"EMIR\".Travailleur_EVA() AS w;")
workers_db = cur.fetchall()
workers_list = [{'id': w[0], 'name': w[1]} for w in workers_db] # Assuming worker ID and Name

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
                    ('P001', 'SupplierA', 'Dummy Product 1', 'Desc 1', 10.0,  'ModelA', 'Electronics'),
                    ('P002', 'SupplierB', 'Dummy Product 2', 'Desc 2', 20.0,  'ModelB', 'Furniture')
                ],
                columns=['ID', 'Fourniseur', 'Name', 'Description', 'Prix Unitaire',  'Model', 'Category']
            )
        else:
            self.products_df = pd.DataFrame(products, columns=['ID', 'Fourniseur', 'Name', 'Description', 'Prix Unitaire',  'Model', 'Category'])
        
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
            
            # Add a status to each product item in the list for assignment tracking
            for item in items:
                # Ensure 'assignment_status' is set for existing items, default to 'pending_assignment'
                if 'assignment_status' not in item:
                    item['assignment_status'] = 'pending_assignment' 
                if 'assigned_worker_id' not in item:
                    item['assigned_worker_id'] = None
                if 'assignment_date' not in item:
                    item['assignment_date'] = None

            quan = len(items)
            reception_data.append({
                'Order_ID': i.id,
                'Supplier': i.idorg,
                'Expected_Date': i.expected_date,
                'Items_Count': quan,
                'Status': i.statut,
                'Total_Value': total,
                'Products': items, # Store raw product data for detail dialog
                'packer_assignment_status': 'unassigned', # New field for colis assignment
                'assigned_packer_id': None,
                'colis_assignment_date': None
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
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(200, 200)

    def plot_data(self, *args, **kwargs):
        self.clear()
        self.plot(*args, **kwargs)

    def add_item(self, item):
        self.addItem(item)

class MetricCard(QFrame):
    """Card widget for displaying key metrics"""

    def __init__(self, title, value, subtitle="", color="#4CAF50"):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }}
        """)

        layout = QVBoxLayout()

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #666; font-weight: bold;")

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
                background-color: #2196F3;
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
        metrics_layout.addWidget(MetricCard("Available Cells", f"{available_cells:,}", "Cells Not In Use", "#FF9800"))
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
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded) # Allow vertical scrolling

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
            QColor('#FF9800'), QColor('#4CAF50'), QColor('#2196F3'),
            QColor('#9C27B0'), QColor('#FFC107'), QColor('#00BCD4')
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
    
        # Modified to take only 3 products for top stocks level
        top_products = self.data.inventory_df.nlargest(3, 'Quantity')
    
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
                border: 1px solid #e0e0e0;
                font-size: 12px;
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

class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0  # en pourcentage
        self.setMinimumSize(200, 200)

    def setProgress(self, value: float):
        self.progress = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(10, 10, self.width() - 20, self.height() - 20)

        # Fond gris clair
        pen_bg = QPen(QColor("#dfe3e6"), 20)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)

        # Cercle de progression bleu
        pen_fg = QPen(QColor("#3498db"), 20)
        pen_fg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_fg)
        painter.drawArc(rect, -90 * 16, -self.progress * 3.6 * 16)

        # Texte
        painter.setPen(QColor("#ffffff"))
        font = QFont("Arial", 30, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{int(self.progress)}%")

        # Cercle intérieur
        painter.setBrush(QColor("#205081"))
        painter.setPen(Qt.PenStyle.NoPen)
        inner_rect = QRectF(30, 30, self.width() - 60, self.height() - 60)
        painter.drawEllipse(inner_rect)

class ColisEmballageCard(QFrame):
    """Aesthetic card for a colis to be wrapped."""
    def __init__(self, colis_data, parent=None):
        super().__init__(parent)
        self.colis_data = colis_data
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
                padding: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QLabel.title {
                font-size: 18px;
                font-weight: bold;
                color: #6C63FF;
                margin-bottom: 5px;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title_label = QLabel(f"Colis ID: {self.colis_data['Order_ID']}")
        title_label.setProperty("class", "title")
        layout.addWidget(title_label)
        
        layout.addWidget(QLabel(f"Supplier: <b>{self.colis_data['Supplier']}</b>"))
        layout.addWidget(QLabel(f"Items Count: <b>{self.colis_data['Items_Count']}</b>"))
        layout.addWidget(QLabel(f"Expected Date: <b>{self.colis_data['Expected_Date']}</b>"))
        layout.addWidget(QLabel(f"Status: <b>{self.colis_data['Status']}</b>"))

        # REMOVED: The "Mark as Wrapped" button is no longer included
        layout.addStretch()

class LotDesemballageCard(QFrame):
    """Aesthetic card for a lot to be unwrapped."""
    def __init__(self, lot_data, parent=None):
        super().__init__(parent)
        self.lot_data = lot_data
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
                padding: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QLabel.title {
                font-size: 18px;
                font-weight: bold;
                color: #6C63FF;
                margin-bottom: 5px;
            }
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title_label = QLabel(f"Lot ID: {self.lot_data['idlot']}")
        title_label.setProperty("class", "title")
        layout.addWidget(title_label)
        
        layout.addWidget(QLabel(f"Product: <b>{self.lot_data.get('product_name', 'N/A')}</b>"))
        layout.addWidget(QLabel(f"Quantity: <b>{self.lot_data['quantity']}</b>"))
        layout.addWidget(QLabel(f"Assigned Worker: <b>{self.lot_data.get('assigned_worker_name', 'N/A')}</b>"))
        layout.addWidget(QLabel(f"Assignment Date: <b>{self.lot_data.get('assignment_date', 'N/A')}</b>"))

        unwrap_button = QPushButton("Mark as Unwrapped")
        unwrap_button.clicked.connect(self.mark_as_unwrapped)
        layout.addWidget(unwrap_button)
        layout.addStretch()

    def mark_as_unwrapped(self):
        # Simulate updating database
        order_id = self.lot_data['Order_ID']
        idlot = self.lot_data['idlot']

        zone_emballage_widget = self.parent().parent().parent()
        if isinstance(zone_emballage_widget, ZoneEmballage):
            order_index = zone_emballage_widget.data.reception_df.index[
                zone_emballage_widget.data.reception_df['Order_ID'] == order_id
            ].tolist()

            if order_index:
                order_idx = order_index[0]
                products_list = zone_emballage_widget.data.reception_df.at[order_idx, 'Products']
                for p_item in products_list:
                    if p_item.get('idlot') == idlot:
                        p_item['assignment_status'] = 'unwrapped' # Update status
                        QMessageBox.information(self, "Success", f"Lot {idlot} marked as unwrapped.")
                        zone_emballage_widget.refresh_desemballage_lots() # Refresh the list
                        return
            QMessageBox.warning(self, "Error", f"Lot {idlot} not found for update.")
        else:
            QMessageBox.warning(self, "Error", "Could not find parent ZoneEmballage widget.")


class ZoneEmballage(QWidget):
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
            self._main_layout.setContentsMargins(15, 15, 15, 15)
            self._main_layout.setSpacing(20)

        # Main container with scroll area
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

        # Emballage Section (Colis à emballer) - FIXED: Only show items not yet wrapped
        emballage_group_box = self.create_section_group_box("Colis à Emballer (Packaging)")
        self.emballage_colis_layout = QVBoxLayout(emballage_group_box)
        self.emballage_colis_layout.setContentsMargins(15, 15, 15, 15)
        self.emballage_colis_layout.setSpacing(10)
        
        # Add a scroll area for the colis cards
        self.emballage_scroll_area = QScrollArea()
        self.emballage_scroll_area.setWidgetResizable(True)
        self.emballage_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.emballage_colis_container = QWidget()
        self.emballage_colis_container_layout = QVBoxLayout(self.emballage_colis_container)
        self.emballage_colis_container_layout.setContentsMargins(0,0,0,0)
        self.emballage_colis_container_layout.setSpacing(10)
        self.emballage_scroll_area.setWidget(self.emballage_colis_container)
        self.emballage_colis_layout.addWidget(self.emballage_scroll_area)

        self.refresh_emballage_colis() # Populate with cards

        # Désemballage Section (Lots à désemballer)
        desemballage_group_box = self.create_section_group_box("Lots à Désemballer (Unpackaging)")
        self.desemballage_lots_layout = QVBoxLayout(desemballage_group_box)
        self.desemballage_lots_layout.setContentsMargins(15, 15, 15, 15)
        self.desemballage_lots_layout.setSpacing(10)

        # Add a scroll area for the lots cards
        self.desemballage_scroll_area = QScrollArea()
        self.desemballage_scroll_area.setWidgetResizable(True)
        self.desemballage_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.desemballage_lots_container = QWidget()
        self.desemballage_lots_container_layout = QVBoxLayout(self.desemballage_lots_container)
        self.desemballage_lots_container_layout.setContentsMargins(0,0,0,0)
        self.desemballage_lots_container_layout.setSpacing(10)
        self.desemballage_scroll_area.setWidget(self.desemballage_lots_container)
        self.desemballage_lots_layout.addWidget(self.desemballage_scroll_area)

        self.refresh_desemballage_lots() # Populate with cards

        # Add sections to main layout
        container_layout.addWidget(emballage_group_box, 0, 0)
        container_layout.addWidget(desemballage_group_box, 1, 0)
        container_layout.setRowStretch(0, 1)
        container_layout.setRowStretch(1, 1)
        container_layout.setRowStretch(2, 1)

        # Add quick actions toolbar at the bottom
        actions_frame = self.create_quick_actions()
        container_layout.addWidget(actions_frame, 2, 0, 1, 1)

    def refresh_emballage_colis(self):
        # Clear existing cards
        while self.emballage_colis_container_layout.count():
            item = self.emballage_colis_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # FIXED: Filter for orders that are 'Accepte' and 'unassigned' for packer (meaning not yet wrapped)
        # This ensures only items not yet wrapped are shown
        colis_to_wrap = [
            order for order in self.data.reception_df.to_dict('records')
            if order['Status'] == 'Accepte' and order['packer_assignment_status'] == 'unassigned'
        ]

        if not colis_to_wrap:
            no_colis_label = QLabel("No accepted colis awaiting wrapping.")
            no_colis_label.setStyleSheet("font-style: italic; color: #777; padding: 20px;")
            self.emballage_colis_container_layout.addWidget(no_colis_label, alignment=Qt.AlignmentFlag.AlignCenter)
            return

        for colis_data in colis_to_wrap:
            colis_card = ColisEmballageCard(colis_data, self)
            self.emballage_colis_container_layout.addWidget(colis_card)
        self.emballage_colis_container_layout.addStretch() # Push cards to top

    def refresh_desemballage_lots(self):
        # Clear existing cards
        while self.desemballage_lots_container_layout.count():
            item = self.desemballage_lots_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        lots_to_unwrap = []
        today = datetime.date.today()

        for order_data in self.data.reception_df.to_dict('records'):
            if 'Products' in order_data and isinstance(order_data['Products'], list):
                for product_item in order_data['Products']:
                    # Check if assigned, not unwrapped, and assigned today
                    if product_item.get('assignment_status') == 'assigned':
                        assignment_date_str = product_item.get('assignment_date')
                        if assignment_date_str:
                            assignment_date = datetime.datetime.strptime(assignment_date_str, '%Y-%m-%d %H:%M:%S').date()
                            if assignment_date == today:
                                # Get product name and assigned worker name for display
                                product_id_or_lot = product_item.get('idlot')
                                product_name = next((p[2] for p in produits_db if p[0] == product_id_or_lot), "Unknown Product")
                                assigned_worker_id = product_item.get('assigned_worker_id')
                                assigned_worker_name = next((w['name'] for w in workers_list if w['id'] == assigned_worker_id), "N/A")

                                lot_info = product_item.copy()
                                lot_info['Order_ID'] = order_data['Order_ID'] # Add Order_ID for context
                                lot_info['product_name'] = product_name
                                lot_info['assigned_worker_name'] = assigned_worker_name
                                lots_to_unwrap.append(lot_info)

        if not lots_to_unwrap:
            no_lots_label = QLabel("No lots received today awaiting unwrap.")
            no_lots_label.setStyleSheet("font-style: italic; color: #777; padding: 20px;")
            self.desemballage_lots_container_layout.addWidget(no_lots_label, alignment=Qt.AlignmentFlag.AlignCenter)
            return

        for lot_data in lots_to_unwrap:
            lot_card = LotDesemballageCard(lot_data, self)
            self.desemballage_lots_container_layout.addWidget(lot_card)
        self.desemballage_lots_container_layout.addStretch() # Push cards to top


    def create_section_group_box(self, title):
        group_box = QGroupBox(title)
        group_box.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                margin-top: 10px; /* Space for title */
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left; /* Position at top left */
                padding: 0 10px;
                background-color: transparent;
            }
        """)
        return group_box

    def create_quick_actions(self):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Action buttons
        actions = [
            ("Marquer comme terminé", "dialog-ok", "#4CAF50"),
            ("Signaler problème", "dialog-warning", "#FF9800"),
            ("Demande d'assistance", "help", "#2196F3")
        ]

        for text, icon, color in actions:
            btn = QPushButton(text)
            btn.setIcon(QIcon.fromTheme(icon))
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

class MenuExpedition(QWidget):
    def __init__(self,data):
        super().__init__()
        self.data=data
        self.init_ui()
    def init_ui(self):
        # Clear existing layout if init_ui is called multiple times
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QVBoxLayout(self) # Changed to QVBoxLayout for scrollability

        layout = self._main_layout
        
        title = QLabel("Expedition Orders Overview")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        expedition_summary_table = self.create_expedition_summary_table()
        
        # Wrap the table in a scroll area
        table_scroll_area = QScrollArea()
        table_scroll_area.setWidgetResizable(True)
        table_scroll_area.setWidget(expedition_summary_table)
        table_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(table_scroll_area)

        bouton = QPushButton("Generate Expedition Report")
        bouton.setStyleSheet("""
                    QPushButton { background-color: #2196F3; color: white; border: none;border-radius: 15px; margin-top:20px;font-weight: bold; padding: 10px 20px;}
                    QPushButton:hover { background-color: #1976D2; }
                """)
        bouton.clicked.connect(self.generate_expedition_report_csv) # Connect to new function
        layout.addWidget(bouton, alignment=Qt.AlignmentFlag.AlignCenter) # Center the button
        layout.addStretch() # Push content to top

    def clear_layout(self: 'MenuExpedition', layout):
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
        
        table.setRowCount(len(self.data.expedition2_df))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['identifiant du colis', 'identifiant du lot', 'id du bon de reception',"date d'expedition"])

        for i, (_, row) in enumerate(self.data.expedition2_df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['identifiant du colis']))
            table.setItem(i, 1, QTableWidgetItem(row['identifiant du lot']))
            table.setItem(i, 2, QTableWidgetItem(row['idbonexpedition']))
            table.setItem(i, 3, QTableWidgetItem(str(row['dateexpedition'])))
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #dcdcdc;
                border: 1px solid #e0e0e0;
                font-size: 12px;
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

    def generate_expedition_report_csv(self):
        if not self.data.expedition_df.empty:
            options = QFileDialog.Option.DontUseNativeDialog
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save Expedition Report",
                "expedition_report.csv",
                "CSV Files (*.csv);;All Files (*)",
                options=options
            )
            if file_name:
                try:
                    self.data.expedition_df.to_csv(file_name, index=False)
                    QMessageBox.information(self, "Success", f"Expedition report saved to:\n{file_name}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save expedition report: {e}")
        else:
            QMessageBox.warning(self, "No Data", "No expedition data to save.")

# New ProductDetailDialog
class ProductDetailDialog(QDialog):
    product_validated = pyqtSignal(str) # Emits order_id when validated
    product_refused = pyqtSignal(str) # Emits order_id when refused

    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.setWindowTitle(f"Product Details for Order: {order_data['Order_ID']}")
        self.setFixedSize(600, 700)
        self.init_ui()

    def checkeligibility(self):
        for i in self.order_data['Products']:
            if self.Eligible(i['idlot']) == False:
                return "Not Eligible"
        return "Eligible"

    
    def Eligible(self,idlot):
        cur.execute("SELECT \"EMIR\".Attribuer_Cellule_Optimale(%s)",(idlot,))
        eli = cur.fetchone()[0]
        if eli is not None:
            print(eli)
            return True
        
        return False

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
        print(self.order_data['Order_ID']) 
        eligible_status = self.checkeligibility()
        
        
        status_color = "#28A745" if eligible_status == "Eligible" else "#DC3545"
        # Construct the HTML string for the title label
        # The <span> tag with inline style will color only the eligibility part
        title_html = (
            f"<h1 style='font-size: 24px; font-weight: bold; color: #333333; "
            f"margin-bottom: 20px; padding-bottom: 10px; "
            f"border-bottom: 1px solid #E0E0E0;'>"
            f"Order: {self.order_data['Order_ID']}"
            f"&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp; "
            f"<span style='color: {status_color}; margin-left: 60px; '>  {eligible_status}</span>"
            f"</h1>"
        )

        title_label = QLabel()
        title_label.setText(title_html)
        # Crucially, set the text format to RichText to interpret HTML
        title_label.setTextFormat(Qt.TextFormat.RichText)
        # Remove the setProperty("class", "title") as styling is now inline HTML
        # title_label.setProperty("class", "title") # No longer needed for color/bold

        layout.addWidget(title_label)
        
        

        form_layout = QFormLayout()
        form_layout.addRow("Supplier:", QLabel(self.order_data['Supplier']))
        form_layout.addRow("Expected Date:", QLabel(str(self.order_data['Expected_Date'])))
        form_layout.addRow("Items Count:", QLabel(str(self.order_data['Items_Count'])))
        form_layout.addRow("Total Value:", QLabel(f"${self.order_data['Total_Value']:.2f}"))
        layout.addLayout(form_layout)

        products_label = QLabel("Products in this Order:")
        layout.addWidget(products_label)
        products_list_widget = QListWidget()
        for item in self.order_data['Products']:
            # Fetch product details from the global produits_db
            product_id_or_lot = item.get('idlot') # Changed from idproduit to idlot
            product_name = "Unknown Product"
            quantity = item.get('quantity', 'N/A')

            # Find product name from produits_db using product_id_or_lot
            for prod_data in produits_db:
                if prod_data[0] == product_id_or_lot: # Assuming prod_data[0] is the ID to match idlot
                    product_name = prod_data[2] # Assuming name is at index 2
                    break
            products_list_widget.addItem(f"- {product_name} (ID: {product_id_or_lot}), Quantity: {quantity}")
        layout.addWidget(products_list_widget)

        button_layout = QHBoxLayout()
        validate_button = QPushButton("Validate Order")
        validate_button.setStyleSheet("background-color: #4CAF50;")
        validate_button.clicked.connect(self.validate_product)
        button_layout.addWidget(validate_button)

        refuse_button = QPushButton("Refuse Order")
        refuse_button.setStyleSheet("background-color: #F44336;")
        refuse_button.clicked.connect(self.refuse_product)
        button_layout.addWidget(refuse_button)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #999999;")
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def validate_product(self):
        # Update status in DB (example, replace with actual DB call)
        try:
            cur.execute('UPDATE "EMIR".PColis SET statut = %s WHERE id = %s AND idorg = %s;', ('Accepte', self.order_data['Order_ID'], self.order_data['Supplier']))
            conn.commit()
            QMessageBox.information(self, "Success", f"Order {self.order_data['Order_ID']} validated successfully!")
            self.product_validated.emit(self.order_data['Order_ID'])
            self.accept()
        except psycopg2.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to validate order: {e}")

    def refuse_product(self):
        # Update status in DB (example, replace with actual DB call)
        try:
            cur.execute('UPDATE "EMIR".PColis SET statut = %s WHERE id = %s AND idorg = %s;', ('Refuse', self.order_data['Order_ID'], self.order_data['Supplier']))
            conn.commit()
            QMessageBox.information(self, "Success", f"Order {self.order_data['Order_ID']} refused.")
            self.product_refused.emit(self.order_data['Order_ID'])
            self.accept()
        except psycopg2.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to refuse order: {e}")

class ReceptionOrderCard(QFrame):
    """Aesthetic card for displaying a reception order."""
    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
                padding: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QLabel.title {
                font-size: 18px;
                font-weight: bold;
                color: #6C63FF;
                margin-bottom: 5px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton.validate {
                background-color: #4CAF50;
            }
            QPushButton.validate:hover {
                background-color: #388E3C;
            }
            QPushButton.refuse {
                background-color: #F44336;
            }
            QPushButton.refuse:hover {
                background-color: #D32F2F;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title_label = QLabel(f"Order ID: {self.order_data['Order_ID']}")
        title_label.setProperty("class", "title")
        layout.addWidget(title_label)
        
        layout.addWidget(QLabel(f"Supplier: <b>{self.order_data['Supplier']}</b>"))
        layout.addWidget(QLabel(f"Expected Date: <b>{self.order_data['Expected_Date']}</b>"))
        layout.addWidget(QLabel(f"Items Count: <b>{self.order_data['Items_Count']}</b>"))
        
        status_label = QLabel(f"Status: <b>{self.order_data['Status']}</b>")
        status_label.setStyleSheet(f"color: {'#FF9800' if self.order_data['Status'] == 'en attente' else '#2196F3'}; font-weight: bold;")
        layout.addWidget(status_label)

        button_layout = QHBoxLayout()

        details_btn = QPushButton("View Details")
        details_btn.clicked.connect(self.show_details)
        button_layout.addWidget(details_btn)

        validate_btn = QPushButton("Validate")
        validate_btn.setProperty("class", "validate")
        validate_btn.clicked.connect(self.validate_order)
        button_layout.addWidget(validate_btn)

        refuse_btn = QPushButton("Refuse")
        refuse_btn.setProperty("class", "refuse")
        refuse_btn.clicked.connect(self.refuse_order)
        button_layout.addWidget(refuse_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()

    def get_menu_reception_parent(self):
        """Helper to find the MenuReception parent widget."""
        parent_widget = self.parentWidget()
        while parent_widget is not None:
            if isinstance(parent_widget, MenuReception):
                return parent_widget
            parent_widget = parent_widget.parentWidget()
        return None

    def show_details(self):
        dialog = ProductDetailDialog(self.order_data, self)
        menu_reception_widget = self.get_menu_reception_parent()
        if menu_reception_widget:
            dialog.product_validated.connect(menu_reception_widget.handle_order_validated)
            dialog.product_refused.connect(menu_reception_widget.handle_order_refused)
        else:
            QMessageBox.warning(self, "Error", "Could not find parent MenuReception widget to connect signals.")
        dialog.exec()


    def validate_order(self):
        menu_reception_widget = self.get_menu_reception_parent()
        if isinstance(menu_reception_widget, MenuReception):
            menu_reception_widget.validate_order(self.order_data['Order_ID'])
            self.deleteLater() # Remove card after action
        else:
            QMessageBox.warning(self, "Error", "Could not find parent MenuReception widget.")

    def refuse_order(self):
        menu_reception_widget = self.get_menu_reception_parent()
        if isinstance(menu_reception_widget, MenuReception):
            menu_reception_widget.refuse_order(self.order_data['Order_ID'])
            self.deleteLater() # Remove card after action
        else:
            QMessageBox.warning(self, "Error", "Could not find parent MenuReception widget.")

# Modified MenuReception
class MenuReception(QWidget):
    def __init__(self,data):
        super().__init__()
        self.data=data
        self.accepted_products = [] # List to store accepted products for assignment
        self.init_ui()

    def init_ui(self):
        # Clear existing layout if init_ui is called multiple times
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QVBoxLayout(self)
            self._main_layout.setContentsMargins(15, 15, 15, 15)
            self._main_layout.setSpacing(20)

        layout = self._main_layout
        
        title = QLabel("Reception Orders Validation")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        # Container for cards
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10) # Spacing between cards

        # Scroll area for cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)
        layout.addStretch()

        self.refresh_reception_cards() # Populate cards

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def refresh_reception_cards(self):
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Filter reception_df to only show 'Pending' or 'Processing' orders
        pending_orders_df = self.data.reception_df[
            (self.data.reception_df['Status'] == 'en attente') | 
            (self.data.reception_df['Status'] == 'Processing')
        ].copy()

        if pending_orders_df.empty:
            no_orders_label = QLabel("No reception orders awaiting validation.")
            no_orders_label.setStyleSheet("font-style: italic; color: #777; padding: 20px;")
            self.cards_layout.addWidget(no_orders_label, alignment=Qt.AlignmentFlag.AlignCenter)
            return

        for _, row in pending_orders_df.iterrows():
            order_card = ReceptionOrderCard(row.to_dict(), self)
            self.cards_layout.addWidget(order_card)
        self.cards_layout.addStretch() # Push cards to top

    def validate_order(self, order_id):
        # Update status in the underlying DataFrame
        order_index = self.data.reception_df.index[self.data.reception_df['Order_ID'] == order_id].tolist()
        if order_index:
            order_idx = order_index[0]
            self.data.reception_df.at[order_idx, 'Status'] = 'Accepte'
            
            # Add the accepted order's products to the list for worker assignment
            accepted_order_data = self.data.reception_df[self.data.reception_df['Order_ID'] == order_id].iloc[0].to_dict()
            if 'Products' not in accepted_order_data or not isinstance(accepted_order_data['Products'], list):
                accepted_order_data['Products'] = []
            self.accepted_products.append(accepted_order_data)
            
            QMessageBox.information(self, "Order Validated", f"Order {order_id} has been validated and moved for assignment.")
            self.refresh_reception_cards() # Refresh cards to remove the validated one
            
            # Notify other widgets to refresh their data
            main_window = self.window()
            if isinstance(main_window, MainWindow):
                if hasattr(main_window.central_widget, 'current_widget') and isinstance(main_window.central_widget.current_widget, WarehouseMenuInteractionWidget):
                    assign_lot_widget = main_window.central_widget.current_widget.findChild(AssignLotToMagasinierWidget)
                    if assign_lot_widget:
                        assign_lot_widget.refresh_accepted_products()
                    assigned_tasks_widget = main_window.central_widget.current_widget.findChild(AssignedTasksViewWidget)
                    if assigned_tasks_widget:
                        assigned_tasks_widget.refresh_assigned_tasks()
                    assign_colis_widget = main_window.central_widget.current_widget.findChild(AssignColisToEmballeurWidget)
                    if assign_colis_widget:
                        assign_colis_widget.refresh_pending_colis()
                    packaging_zone_widget = main_window.central_widget.current_widget.findChild(ZoneEmballage)
                    if packaging_zone_widget:
                        packaging_zone_widget.refresh_emballage_colis()
        else:
            QMessageBox.warning(self, "Error", f"Order {order_id} not found in data.")

    def refuse_order(self, order_id):
        # Update status in the underlying DataFrame
        order_index = self.data.reception_df.index[self.data.reception_df['Order_ID'] == order_id].tolist()
        if order_index:
            order_idx = order_index[0]
            self.data.reception_df.at[order_idx, 'Status'] = 'Refuse'
            
            QMessageBox.information(self, "Order Refused", f"Order {order_id} has been refused.")
            self.refresh_reception_cards() # Refresh cards to remove the refused one
        else:
            QMessageBox.warning(self, "Error", f"Order {order_id} not found in data.")

    def handle_order_validated(self, order_id):
        # This signal is emitted from ProductDetailDialog
        # We already handle the removal in validate_order, so this might be redundant
        # unless there's specific UI update needed here.
        self.refresh_reception_cards() # Ensure UI is updated if dialog was used

    def handle_order_refused(self, order_id):
        # This signal is emitted from ProductDetailDialog
        # We already handle the removal in refuse_order, so this might be redundant
        # unless there's specific UI update needed here.
        self.refresh_reception_cards() # Ensure UI is updated if dialog was used

# New AssignColisToEmballeurWidget
class AssignColisToEmballeurWidget(QWidget):
    def __init__(self, data, workers_list):
        super().__init__()
        self.data = data
        self.workers_list = workers_list
        self.init_ui()
        self.refresh_pending_colis() # Initial refresh

    def init_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(15, 15, 15, 15)
        self._main_layout.setSpacing(20)

        title = QLabel("Assign Colis (Packages) to Emballeurs (Packers)")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px;")
        self._main_layout.addWidget(title)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.colis_container = QWidget()
        self.colis_layout = QVBoxLayout(self.colis_container)
        self.colis_layout.setContentsMargins(0, 0, 0, 0)
        self.colis_layout.setSpacing(15)
        self.scroll_area.setWidget(self.colis_container)
        self._main_layout.addWidget(self.scroll_area)

        self._main_layout.addStretch()

    def refresh_pending_colis(self):
        # Clear existing cards
        while self.colis_layout.count():
            item = self.colis_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Filter for orders that are 'Accepte' and 'unassigned' for packer
        pending_colis_for_assignment = [
            order for order in self.data.reception_df.to_dict('records')
            if order['Status'] == 'Accepte' and order['packer_assignment_status'] == 'unassigned'
        ]

        if not pending_colis_for_assignment:
            no_colis_label = QLabel("No accepted colis awaiting emballeur assignment.")
            no_colis_label.setStyleSheet("font-style: italic; color: #777; padding: 20px;")
            self.colis_layout.addWidget(no_colis_label, alignment=Qt.AlignmentFlag.AlignCenter)
            return

        for colis_data in pending_colis_for_assignment:
            colis_card = self.create_colis_assignment_card(
                colis_data['Order_ID'],
                colis_data['Supplier'],
                colis_data['Items_Count'],
                self.workers_list # Assuming all workers can be emballeurs for now
            )
            self.colis_layout.addWidget(colis_card)
        self.colis_layout.addStretch() # Push cards to top

    def create_colis_assignment_card(self, order_id, supplier, items_count, workers):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
                padding: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QLabel.title {
                font-size: 18px;
                font-weight: bold;
                color: #6C63FF;
                margin-bottom: 5px;
            }
            QComboBox {
                border: 1px solid #CCC;
                border-radius: 5px;
                padding: 5px;
                min-width: 100px;
            }
            QPushButton {
                background-color: #00BFA5;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00897B;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(f"Colis ID: {order_id} (Supplier: {supplier})")
        title_label.setProperty("class", "title")
        layout.addWidget(title_label)
        
        layout.addWidget(QLabel(f"Items in Colis: <b>{items_count}</b>"))
        
        assignment_layout = QHBoxLayout()
        assignment_layout.addWidget(QLabel("Assign to Emballeur:"))
        
        worker_combo = QComboBox()
        worker_combo.addItem("— Select Emballeur —", None)
        for worker in workers:
            worker_combo.addItem(worker['name'], worker['id'])
        assignment_layout.addWidget(worker_combo)
        
        assign_btn = QPushButton("Assign Colis")
        assign_btn.clicked.connect(lambda: self.assign_colis(order_id, worker_combo.currentData(), card))
        assignment_layout.addWidget(assign_btn)
        
        layout.addLayout(assignment_layout)
        layout.addStretch()
        
        return card

    def assign_colis(self, order_id, worker_id, card_widget):
        if not worker_id:
            QMessageBox.warning(self, "Assignment Error", "Please select an emballeur.")
            return

        worker_name = next((w['name'] for w in self.workers_list if w['id'] == worker_id), "Unknown Emballeur")
        
        # Update the status of the specific colis in the reception_df
        order_index = self.data.reception_df.index[self.data.reception_df['Order_ID'] == order_id].tolist()
        if order_index:
            order_idx = order_index[0]
            self.data.reception_df.at[order_idx, 'packer_assignment_status'] = 'assigned'
            self.data.reception_df.at[order_idx, 'assigned_packer_id'] = worker_id
            self.data.reception_df.at[order_idx, 'colis_assignment_date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        card_widget.deleteLater() # Remove the card from the UI
        
        QMessageBox.information(self, "Colis Assigned", 
                                f"Colis '{order_id}' assigned to Emballeur: {worker_name}.")
        
        # Re-render the cards to ensure assigned items are gone
        self.refresh_pending_colis()
        # Notify the AssignedTasksViewWidget to refresh
        main_window = self.window()
        if isinstance(main_window, MainWindow):
            if hasattr(main_window.central_widget, 'current_widget') and isinstance(main_window.central_widget.current_widget, WarehouseMenuInteractionWidget):
                assigned_tasks_widget = main_window.central_widget.current_widget.findChild(AssignedTasksViewWidget)
                if assigned_tasks_widget:
                    assigned_tasks_widget.refresh_assigned_tasks()
                packaging_zone_widget = main_window.central_widget.current_widget.findChild(ZoneEmballage)
                if packaging_zone_widget:
                    packaging_zone_widget.refresh_emballage_colis() # Refresh packaging zone for new colis

# Renamed AssignToWorkerWidget to AssignLotToMagasinierWidget
class AssignLotToMagasinierWidget(QWidget):
    def __init__(self, data, workers_list):
        super().__init__()
        self.data = data
        self.workers_list = workers_list
        self.accepted_products_for_assignment = [] # Will hold products from validated orders
        self.init_ui()
        self.refresh_accepted_products() # Initial refresh

    def init_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(15, 15, 15, 15)
        self._main_layout.setSpacing(20)

        title = QLabel("Assign Lots (Product Items) to Magasiniers (Warehouse Workers)")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px;")
        self._main_layout.addWidget(title)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.products_container = QWidget()
        self.products_layout = QVBoxLayout(self.products_container)
        self.products_layout.setContentsMargins(0, 0, 0, 0)
        self.products_layout.setSpacing(15)
        self.scroll_area.setWidget(self.products_container)
        self._main_layout.addWidget(self.scroll_area)

        self._main_layout.addStretch()

    def refresh_accepted_products(self):
        # Clear existing cards
        while self.products_layout.count():
            item = self.products_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Get accepted orders from MenuReception (assuming it's the source)
        main_window = self.window()
        if isinstance(main_window, MainWindow):
            if hasattr(main_window.central_widget, 'current_widget') and isinstance(main_window.central_widget.current_widget, WarehouseMenuInteractionWidget):
                reception_widget = main_window.central_widget.current_widget.findChild(MenuReception)
                if reception_widget:
                    # Filter for orders that are 'Accepte'
                    accepted_orders = [
                        order for order in reception_widget.data.reception_df.to_dict('records')
                        if order['Status'] == 'Accepte'
                    ]
                    self.accepted_products_for_assignment = []
                    for order_data in accepted_orders:
                        for product_item in order_data['Products']:
                            # Only add products that are pending assignment
                            if product_item.get('assignment_status') == 'pending_assignment':
                                self.accepted_products_for_assignment.append({
                                    'Order_ID': order_data['Order_ID'],
                                    'product_item': product_item # Keep the full product item dictionary
                                })

        # Sample data for assign lots if no actual accepted products
        if not self.accepted_products_for_assignment:
            # Add some dummy data for demonstration if no real data is available
            # Ensure these dummy products have a corresponding entry in produits_db or handle "Unknown Product"
            dummy_product_id = 'P001' # Assuming P001 exists in produits_db
            dummy_product_name = next((p[2] for p in produits_db if p[0] == dummy_product_id), "Sample Product A")
            dummy_product_category = next((p[7] for p in produits_db if p[0] == dummy_product_id), "Electronics")

            self.accepted_products_for_assignment.extend([
                {
                    'Order_ID': 'DUMMY001',
                    'product_item': {
                        'idcol': 'DUMMYCOL001', 'idlot': dummy_product_id, 'quantity': 5, 'date_maj': '2024-07-07',
                        'assignment_status': 'pending_assignment', 'assigned_worker_id': None, 'assignment_date': None
                    }
                },
                {
                    'Order_ID': 'DUMMY002',
                    'product_item': {
                        'idcol': 'DUMMYCOL002', 'idlot': 'P002', 'quantity': 12, 'date_maj': '2024-07-07',
                        'assignment_status': 'pending_assignment', 'assigned_worker_id': None, 'assignment_date': None
                    }
                }
            ])
            QMessageBox.information(self, "Sample Data", "Loaded sample data for 'Assign Lots' for demonstration.")


        if not self.accepted_products_for_assignment:
            no_products_label = QLabel("No accepted products awaiting assignment.")
            no_products_label.setStyleSheet("font-style: italic; color: #777; padding: 20px;")
            self.products_layout.addWidget(no_products_label, alignment=Qt.AlignmentFlag.AlignCenter)
            return

        for assignment_data in self.accepted_products_for_assignment:
            order_id = assignment_data['Order_ID']
            product_item = assignment_data['product_item']

            # Find full product details from produits_db using idlot
            product_id_or_lot = product_item.get('idlot')
            product_name = "Unknown Product"
            product_category = "N/A"
            product_details_from_db = next((p for p in produits_db if p[0] == product_id_or_lot), None)
            if product_details_from_db:
                product_name = product_details_from_db[2]
                product_category = product_details_from_db[7]

            product_card = self.create_product_assignment_card(
                order_id,
                product_name,
                product_item['quantity'],
                product_category,
                self.workers_list,
                product_id_or_lot # Pass product_id_or_lot to identify the specific product
            )
            self.products_layout.addWidget(product_card)
        self.products_layout.addStretch() # Push cards to top

    def create_product_assignment_card(self, order_id, product_name, quantity, category, workers, product_id_or_lot):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
                padding: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QLabel.title {
                font-size: 18px;
                font-weight: bold;
                color: #6C63FF;
                margin-bottom: 5px;
            }
            QComboBox {
                border: 1px solid #CCC;
                border-radius: 5px;
                padding: 5px;
                min-width: 100px;
            }
            QPushButton {
                background-color: #00BFA5;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00897B;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(f"Order: {order_id} - Product: {product_name}")
        title_label.setProperty("class", "title")
        layout.addWidget(title_label)
        
        layout.addWidget(QLabel(f"Quantity: <b>{quantity}</b>"))
        layout.addWidget(QLabel(f"Category: <b>{category}</b>"))
        
        assignment_layout = QHBoxLayout()
        assignment_layout.addWidget(QLabel("Assign to Magasinier:"))
        
        worker_combo = QComboBox()
        worker_combo.addItem("— Select Magasinier —", None)
        for worker in workers:
            worker_combo.addItem(worker['name'], worker['id'])
        assignment_layout.addWidget(worker_combo)
        
        assign_btn = QPushButton("Assign Lot")
        assign_btn.clicked.connect(lambda: self.assign_task(order_id, product_id_or_lot, worker_combo.currentData(), card))
        assignment_layout.addWidget(assign_btn)
        
        layout.addLayout(assignment_layout)
        layout.addStretch()
        
        return card

    def assign_task(self, order_id, product_id_or_lot, worker_id, card_widget):
        if not worker_id:
            QMessageBox.warning(self, "Assignment Error", "Please select a worker.")
            return

        worker_name = next((w['name'] for w in self.workers_list if w['id'] == worker_id), "Unknown Worker")
        
        # Update the status of the specific product in the reception_df
        # Find the order
        order_index = self.data.reception_df.index[self.data.reception_df['Order_ID'] == order_id].tolist()
        if order_index:
            order_idx = order_index[0]
            # Find the product within the order's Products list
            products_list = self.data.reception_df.at[order_idx, 'Products']
            for p_item in products_list:
                if p_item.get('idlot') == product_id_or_lot: # Match by idlot
                    p_item['assignment_status'] = 'assigned'
                    # Optionally, store worker_id and assignment_date here
                    p_item['assigned_worker_id'] = worker_id
                    p_item['assignment_date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    break
        
        card_widget.deleteLater() # Remove the card from the UI
        
        QMessageBox.information(self, "Task Assigned", 
                                f"Product ID '{product_id_or_lot}' from Order '{order_id}' assigned to {worker_name}.")
        
        # Re-render the cards to ensure assigned items are gone
        self.refresh_accepted_products()
        # Notify the AssignedTasksViewWidget to refresh
        main_window = self.window()
        if isinstance(main_window, MainWindow):
            if hasattr(main_window.central_widget, 'current_widget') and isinstance(main_window.central_widget.current_widget, WarehouseMenuInteractionWidget):
                assigned_tasks_widget = main_window.central_widget.current_widget.findChild(AssignedTasksViewWidget)
                if assigned_tasks_widget:
                    assigned_tasks_widget.refresh_assigned_tasks()
                packaging_zone_widget = main_window.central_widget.current_widget.findChild(ZoneEmballage)
                if packaging_zone_widget:
                    packaging_zone_widget.refresh_desemballage_lots() # Refresh desemballage zone for new lots

class TaskCard(QFrame):
    """Aesthetic card for displaying an assigned task."""
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.setStyleSheet("""
            QFrame {
                background-color: #F0F8FF; /* Light blue background */
                border-radius: 12px;
                border: 1px solid #ADD8E6; /* Lighter blue border */
                padding: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            }
            QLabel {
                color: #2F4F4F; /* Dark slate gray */
                font-size: 14px;
            }
            QLabel.title {
                font-size: 18px;
                font-weight: bold;
                color: #1E90FF; /* Dodger Blue */
                margin-bottom: 5px;
            }
            QLabel.detail {
                font-size: 13px;
                color: #555;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title_label = QLabel(f"Task Type: {self.task_data['Task_Type']}")
        title_label.setProperty("class", "title")
        layout.addWidget(title_label)
        
        layout.addWidget(QLabel(f"Order ID: <b>{self.task_data['Order_ID']}</b>"))
        layout.addWidget(QLabel(f"Item/Product: <b>{self.task_data['Item_Product_Name']}</b>"))
        layout.addWidget(QLabel(f"Quantity: <b>{self.task_data['Quantity']}</b>"))
        layout.addWidget(QLabel(f"Category: <b>{self.task_data['Category']}</b>"))
        layout.addWidget(QLabel(f"Assigned To: <b>{self.task_data['Assigned_Worker']}</b>"))
        layout.addWidget(QLabel(f"Assignment Date: <b>{self.task_data['Assignment_Date']}</b>"))
        layout.addStretch()

# FIXED: AssignedTasksViewWidget - Now properly shows assigned tasks
class AssignedTasksViewWidget(QWidget):
    def __init__(self, data, workers_list):
        super().__init__()
        self.data = data
        self.workers_list = workers_list
        self.init_ui()
        self.refresh_assigned_tasks() # Initial refresh

    def init_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(15, 15, 15, 15)
        self._main_layout.setSpacing(20)

        title = QLabel("View All Assigned Tasks")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px;")
        self._main_layout.addWidget(title)

        # Use a scroll area to contain the task cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_layout.setSpacing(10) # Spacing between cards
        
        self.scroll_area.setWidget(self.tasks_container)
        self._main_layout.addWidget(self.scroll_area)
        self._main_layout.addStretch()

    def refresh_assigned_tasks(self):
        # Clear existing cards
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        assigned_tasks_data = []

        # FIXED: Collect Colis assignments - now properly shows assigned colis
        for order_data in self.data.reception_df.to_dict('records'):
            if order_data.get('packer_assignment_status') == 'assigned':
                assigned_packer_id = order_data.get('assigned_packer_id')
                assigned_packer_name = next((w['name'] for w in self.workers_list if w['id'] == assigned_packer_id), "N/A")
                assignment_date = order_data.get('colis_assignment_date', 'N/A')
                
                assigned_tasks_data.append({
                    'Task_Type': 'Colis (Package) Assignment',
                    'Order_ID': order_data['Order_ID'],
                    'Item_Product_Name': f"Package with {order_data['Items_Count']} items", # Display item count for colis
                    'Quantity': order_data['Items_Count'],
                    'Category': 'Package', # Category for colis
                    'Assigned_Worker': assigned_packer_name + " (Emballeur)",
                    'Assignment_Date': assignment_date
                })

            # FIXED: Collect Lot assignments within this order - now properly shows assigned lots
            if 'Products' in order_data and isinstance(order_data['Products'], list):
                for product_item in order_data['Products']:
                    if product_item.get('assignment_status') == 'assigned':
                        product_id_or_lot = product_item.get('idlot')
                        product_name = "Unknown Product"
                        product_category = "N/A"
                        product_details_from_db = next((p for p in produits_db if p[0] == product_id_or_lot), None)
                        if product_details_from_db:
                            product_name = product_details_from_db[2]
                            product_category = product_details_from_db[6] if len(product_details_from_db) > 6 else "N/A"
                        
                        assigned_worker_id = product_item.get('assigned_worker_id')
                        assigned_worker_name = next((w['name'] for w in self.workers_list if w['id'] == assigned_worker_id), "N/A")
                        assignment_date = product_item.get('assignment_date', 'N/A')

                        assigned_tasks_data.append({
                            'Task_Type': 'Lot (Product Item) Assignment',
                            'Order_ID': order_data['Order_ID'],
                            'Item_Product_Name': product_name,
                            'Quantity': product_item.get('quantity', 'N/A'),
                            'Category': product_category,
                            'Assigned_Worker': assigned_worker_name + " (Magasinier)",
                            'Assignment_Date': assignment_date
                        })
        
        if not assigned_tasks_data:
            no_tasks_label = QLabel("No tasks currently assigned.")
            no_tasks_label.setStyleSheet("font-style: italic; color: #777; padding: 20px;")
            self.tasks_layout.addWidget(no_tasks_label, alignment=Qt.AlignmentFlag.AlignCenter)
            return

        for task_data in assigned_tasks_data:
            task_card = TaskCard(task_data)
            self.tasks_layout.addWidget(task_card)
        self.tasks_layout.addStretch() # Push cards to top


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
        tabs.addTab(MenuReception(self.data), "Reception Validation") # Updated tab name
        tabs.addTab(MenuExpedition(self.data), "Expedition")
        tabs.addTab(ZoneEmballage(self.data),"Packaging Zone")
        tabs.addTab(AssignColisToEmballeurWidget(self.data, workers_list), "Assign Colis") # New tab for colis assignment
        tabs.addTab(AssignLotToMagasinierWidget(self.data, workers_list), "Assign Lots") # Renamed tab for lot assignment
        tabs.addTab(AssignedTasksViewWidget(self.data, workers_list), "View Assigned Tasks") # New tab for assigned tasks
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

        # Wrap content in a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)

        title = QLabel("Storage Space Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        content_layout.addWidget(title)

        # Metric Card for Utilization
        try:
            cur.execute('SELECT "EMIR".cellutilisation();')
            utilization = cur.fetchone()[0]
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching cell utilization: {e}. Using dummy value.")
            utilization = 0.0

        content_layout.addWidget(MetricCard("Overall Utilization", f"{utilization:.1f}%", "Average Warehouse Utilization"))

        # Placeholder for sub-features
        sub_features_layout = QGridLayout()
        sub_features_layout.addWidget(QLabel("<h3>Cell Optimization</h3><p>Simulate optimal cell assignment.</p>"), 0, 0)
        sub_features_layout.addWidget(QLabel("<h3>Space Allocation</h3><p>Manage space assignments for product categories.</p>"), 0, 1)
        sub_features_layout.addWidget(QLabel("<h3>Layout Management</h3><p>Visualize and modify warehouse layout.</p>"), 1, 0, 1, 2)
        content_layout.addLayout(sub_features_layout)

        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
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
            self._main_layout = QVBoxLayout(self)

        layout = self._main_layout
        layout.setContentsMargins(0, 0, 0, 0)

        # Wrap content in a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)

        title = QLabel("Generate Reports")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        content_layout.addWidget(title)

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
                background-color: #4CAF50;
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

        # Performance Reports (reusing PerformanceWidget logic)
        self.performance_reports_widget = PerformanceWidget(self.data)
        tabs.addTab(self.performance_reports_widget, "Performance Reports")

        # Exception Reports
        exception_reports_widget = QWidget()
        exception_reports_layout = QVBoxLayout()
        exception_reports_layout.addWidget(QLabel("<h4>Exception Reports</h4>"))
        exception_reports_layout.addWidget(QLabel("View reports on overdue orders, critical low stock, and discrepancies."))
        
        # Add a button to generate exceptions
        generate_exceptions_btn = QPushButton("Generate Exception Report")
        generate_exceptions_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #E64A19;
            }
        """)
        generate_exceptions_btn.clicked.connect(self.generate_exception_report)
        exception_reports_layout.addWidget(generate_exceptions_btn)

        self.exception_output_label = QLabel("Click 'Generate Exception Report' to see exceptions.")
        self.exception_output_label.setStyleSheet("font-style: italic; color: #777; padding: 10px;")
        exception_reports_layout.addWidget(self.exception_output_label)

        exception_reports_widget.setLayout(exception_reports_layout)
        tabs.addTab(exception_reports_widget, "Exception Reports")

        content_layout.addWidget(tabs)
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
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
        table.setRowCount(len(self.data.inventory_df))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Product', 'Category', 'Quantity', 'Current Value'])

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
        self.stock_summary_df = pd.DataFrame(self.stock_summary_data)
        
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #dcdcdc;
                border: 1px solid #e0e0e0;
                font-size: 12px;
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

    def generate_exception_report(self):
        exceptions = []

        # Exception 1: Overdue Reception Orders (Status 'en attente' and Expected_Date in past)
        overdue_receptions = self.data.reception_df[
            (self.data.reception_df['Status'] == 'en attente') & 
            (self.data.reception_df['Expected_Date'] < datetime.date.today())
        ]
        if not overdue_receptions.empty:
            for _, row in overdue_receptions.iterrows():
                exceptions.append(f"Overdue Reception Order: ID {row['Order_ID']} from {row['Supplier']} (Expected: {row['Expected_Date']})")

        # Exception 2: Low Stock Items (Quantity below a threshold, e.g., 20)
        low_stock_threshold = 20
        low_stock_items = self.data.inventory_df[self.data.inventory_df['Quantity'] < low_stock_threshold]
        if not low_stock_items.empty:
            for _, row in low_stock_items.iterrows():
                exceptions.append(f"Low Stock Alert: Product '{row['Product_Name']}' (ID: {row['Product_ID']}) has only {row['Quantity']} units left.")

        # Exception 3: Unassigned Colis (Accepted but not assigned to packer)
        unassigned_colis = self.data.reception_df[
            (self.data.reception_df['Status'] == 'Accepte') &
            (self.data.reception_df['packer_assignment_status'] == 'unassigned')
        ]
        if not unassigned_colis.empty:
            for _, row in unassigned_colis.iterrows():
                exceptions.append(f"Unassigned Colis: Order ID {row['Order_ID']} is accepted but not assigned for packaging.")

        # Display exceptions
        if exceptions:
            report_text = "<h3>Generated Exception Report:</h3>" + "<br>".join(exceptions)
            self.exception_output_label.setText(report_text)
            self.exception_output_label.setStyleSheet("color: #D32F2F; font-weight: bold; padding: 10px;")
        else:
            self.exception_output_label.setText("No exceptions found at this time. All operations are running smoothly!")
            self.exception_output_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 10px;")


class DailyOperationsPlanningWidget(QWidget):
    """Widget for Daily Operations Planning"""
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

        # Wrap content in a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)

        title = QLabel("Daily Operations Planning")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        content_layout.addWidget(title)

        # Incorporate OrdersWidget as a central part of daily planning
        orders_section_label = QLabel("<h4>Order Management (Reception & Expedition)</h4>")
        content_layout.addWidget(orders_section_label)
        self.orders_widget = OrdersWidget(self.data)
        content_layout.addWidget(self.orders_widget)
        content_layout.setStretchFactor(self.orders_widget, 1) # Give orders widget stretch

        # Placeholder for other planning aspects
        planning_info_label = QLabel("<h3>Planning Tools:</h3>"
                                     "<ul>"
                                     "<li>Schedule Shipments & Receptions</li>"
                                     "<li>Allocate Workforce for Picking/Packing</li>"
                                     "<li>Forecast Demand (using historical data)</li>"
                                     "</ul>")
        content_layout.addWidget(planning_info_label)

        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

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
        # Clear existing layout if init_ui is called multiple times
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QVBoxLayout(self)

        layout = self._main_layout
        layout.setContentsMargins(0, 0, 0, 0) # Adjust margins for nested widget

        # Tab widget for different order types
        tabs = QTabWidget()

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
        layout.setContentsMargins(0,0,0,0)

        # Header with metrics
        header_layout = QHBoxLayout()
        title = QLabel("Reception Orders")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Metrics
        metrics_layout = QHBoxLayout()
        cur.execute("SELECT \"EMIR\".colis_entrants_jour_count();")
        today_rec = cur.fetchone()[0]
        if today_rec is None:
            today_rec = 0
        cur.execute("SELECT \"EMIR\".valuereception();")
        total_value = cur.fetchone()[0]
        if total_value is None:
            total_value = 0.0
        cur.execute("SELECT \"EMIR\".avgitemsreception();")
        avg_items = cur.fetchone()[0]
        if avg_items is None:
            avg_items = 0.0

        metrics_layout.addWidget(MetricCard("Today Receptions", f"{today_rec:,}", "Awaiting Receipt"))
        metrics_layout.addWidget(MetricCard("Total Value", f"${total_value:,.0f}", "All Orders"))
        metrics_layout.addWidget(MetricCard("Avg Items", f"{avg_items:.1f}", "Per Order"))

        # Chart and table
        content_layout = QHBoxLayout()

        # Status chart
        status_chart = ChartWidget(title="Reception Orders by Status", y_label="Number of Orders", x_label="Status")
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
        layout.setContentsMargins(0,0,0,0)

        # Header with metrics
        header_layout = QHBoxLayout()
        title = QLabel("Expedition Orders")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Metrics
        metrics_layout = QHBoxLayout()

        cur.execute("SELECT \"EMIR\".colis_sortants_jour_count();")
        today_exp = cur.fetchone()[0]
        if today_exp is None:
            today_exp = 0
        cur.execute("SELECT \"EMIR\".valueexpedition();")
        total_value = cur.fetchone()[0]
        if total_value is None:
            total_value = 0.0
        cur.execute("SELECT \"EMIR\".avgitemsexpedition();")
        avg_items = cur.fetchone()[0]
        if avg_items is None:
            avg_items = 0.0

        metrics_layout.addWidget(MetricCard("Today Expeditions", f"{today_exp:,}", "Ready to Ship"))
        metrics_layout.addWidget(MetricCard("Total Value", f"${total_value:,.0f}", "All Orders"))
        metrics_layout.addWidget(MetricCard("Avg Items", f"{avg_items:.1f}", "Per Order"))

        # Chart and table
        content_layout = QHBoxLayout()

        # Status chart
        status_chart = ChartWidget(title="Expedition Orders by Status", y_label="Number of Orders", x_label="Status")
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
        status_counts = df['Status'].value_counts()
        x_vals = np.arange(len(status_counts))
        y_vals = status_counts.values
        
        colors = [QColor('#4CAF50'), QColor('#FF9800'), QColor('#2196F3'), QColor('#9C27B0')]
        brushes = [colors[i % len(colors)] for i in range(len(x_vals))]

        bargraph = pg.BarGraphItem(x=x_vals, height=y_vals, width=0.6, brushes=brushes)
        chart_widget.addItem(bargraph)

        # Set custom x-axis ticks
        ticks = [(i, label) for i, label in enumerate(status_counts.index)]
        chart_widget.getAxis('bottom').setTicks([ticks])
        
        # Add value labels on bars (more involved in pyqtgraph, simplified here)
        for i, value in enumerate(y_vals):
            text_item = pg.TextItem(text=f'{int(value)}', anchor=(0.5, 0), color='k')
            text_item.setPos(x_vals[i], value + 0.1) # Position above the bar
            chart_widget.addItem(text_item)
        
        chart_widget.plotItem.setTitle(chart_widget.plotItem.titleLabel.text)
        chart_widget.plotItem.setLabel('left', 'Number of Orders')

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
            table.setItem(i, 0, QTableWidgetItem(row['Order_ID']))
            table.setItem(i, 1, QTableWidgetItem(row[location_col]))
            table.setItem(i, 2, QTableWidgetItem(str(row[date_col])))
            table.setItem(i, 3, QTableWidgetItem(str(row['Items_Count'])))

            # Status with color coding
            status_item = QTableWidgetItem(row['Status'])
            if row['Status'] == 'Pending':
                status_item.setBackground(QColor('#FFF3E0'))
            elif row['Status'] == 'Processing':
                status_item.setBackground(QColor('#E3F2FD'))
            elif row['Status'] == 'Received' or row['Status'] == 'In Transit':
                status_item.setBackground(QColor('#E8F5E8'))

            table.setItem(i, 4, status_item)
            table.setItem(i, 5, QTableWidgetItem(f"${row['Total_Value']:,.0f}"))

        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #dcdcdc;
                border: 1px solid #e0e0e0;
                font-size: 12px;
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

class PerformanceWidget(QWidget):
    """Widget for performance metrics and analytics"""

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

        # Wrap content in a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Performance Analytics")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")

        # Date range selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        from_date = QDateEdit(QDate.currentDate().addDays(-30))
        from_date.setCalendarPopup(True)
        date_layout.addWidget(from_date)

        date_layout.addWidget(QLabel("To:"))
        to_date = QDateEdit(QDate.currentDate())
        to_date.setCalendarPopup(True)
        date_layout.addWidget(to_date)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addLayout(date_layout)

        # KPI Cards

        # KPI Cards
        kpi_layout = QHBoxLayout()

        # Calculate KPIs from recent data
        recent_data = self.data.daily_metrics.tail(30)
        avg_received = recent_data['Items_Received'].mean()
        avg_shipped = recent_data['Items_Shipped'].mean()
        avg_utilization = recent_data['Storage_Utilization'].mean()
        avg_fulfillment = recent_data['Order_Fulfillment_Rate'].mean()

        kpi_layout.addWidget(MetricCard("Daily Received", f"{avg_received:.0f}", "Avg Last 30 days"))
        kpi_layout.addWidget(MetricCard("Daily Shipped", f"{avg_shipped:.0f}", "Avg Last 30 days"))
        kpi_layout.addWidget(MetricCard("Storage Utilization", f"{avg_utilization:.1f}%", "Current Average"))
        kpi_layout.addWidget(MetricCard("Fulfillment Rate", f"{avg_fulfillment:.1f}%", "Order Success"))

        # Charts
        charts_layout = QGridLayout()
        charts_layout.setContentsMargins(0, 0, 0, 0) # Ensure charts don't have excessive margins

        # Daily operations trend
        trend_chart = ChartWidget(parent=self, title='Daily Operations Trend (Last 30 Days)', y_label='Items Count', x_label='Date',
                                  axisItems={'bottom': pg.DateAxisItem()})
        self.create_trend_chart(trend_chart)
        trend_chart.setMinimumHeight(300)
        charts_layout.addWidget(trend_chart, 0, 0)
        charts_layout.setColumnStretch(0, 1) # Ensure this chart stretches

        # Storage utilization
        utilization_chart = ChartWidget(title='Storage Utilization by Zone', y_label='Utilization %', x_label='Zone')
        self.create_utilization_chart(utilization_chart)
        utilization_chart.setMinimumHeight(300)
        charts_layout.addWidget(utilization_chart, 0, 1)
        charts_layout.setColumnStretch(1, 1) # Ensure this chart stretches

        # Fulfillment rate trend
        fulfillment_chart = ChartWidget(parent=self, title='Weekly Fulfillment Rate Trend', y_label='Fulfillment Rate %', x_label='Week',
                                        axisItems={'bottom': pg.DateAxisItem()})
        self.create_fulfillment_chart(fulfillment_chart)
        fulfillment_chart.setMinimumHeight(300)
        charts_layout.addWidget(fulfillment_chart, 1, 0, 1, 2)
        charts_layout.setRowStretch(0, 1) # Stretch the row containing charts
        charts_layout.setRowStretch(1, 1) # Stretch the row containing charts

        content_layout.addLayout(header_layout)
        content_layout.addLayout(kpi_layout)
        content_layout.addLayout(charts_layout)
        content_layout.addStretch() # Ensure content expands vertically
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

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
        recent_data = self.data.daily_metrics.tail(30)
        
        # Convert pandas Timestamps to Unix timestamps for pyqtgraph DateAxisItem
        x_vals = recent_data['Date'].apply(lambda x: x.timestamp()).values
        chart_widget.plot(x_vals, recent_data['Items_Received'].to_numpy(), pen=pg.mkPen(color='#4CAF50', width=2), name='Received')
        chart_widget.plot(x_vals, recent_data['Items_Shipped'].to_numpy(), pen=pg.mkPen(color='#2196F3', width=2), name='Shipped')
        
        chart_widget.plotItem.addLegend()
        chart_widget.plotItem.setLabel('bottom', 'Date', axisClass=pg.DateAxisItem)
        chart_widget.plotItem.setYRange(0, recent_data[['Items_Received', 'Items_Shipped']].max().max() * 1.1)


    def create_utilization_chart(self, chart_widget):
        # Storage utilization by zone (simulated)
        zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D']
        utilization = [85, 72, 91, 68]
        
        x_vals = np.arange(len(zones))
        y_vals = np.array(utilization)

        colors = [QColor('#FF5722') if u > 85 else QColor('#FF9800') if u > 75 else QColor('#4CAF50') for u in utilization]
        brushes = [color for color in colors]

        bargraph = pg.BarGraphItem(x=x_vals, height=y_vals, width=0.6, brushes=brushes)
        chart_widget.addItem(bargraph)

        # Set custom x-axis ticks
        ticks = [(i, label) for i, label in enumerate(zones)]
        chart_widget.getAxis('bottom').setTicks([ticks])
        chart_widget.plotItem.setYRange(0, 100)
        
        # Add a horizontal line for target utilization
        target_line = pg.InfiniteLine(80, angle=0, pen=pg.mkPen('r', width=2, style=Qt.PenStyle.DashLine), movable=False)
        chart_widget.addItem(target_line)
        # Add text label for the target line
        target_label = pg.TextItem("Target (80%)", color='r', anchor=(0.5, 0))
        target_label.setPos(x_vals[-1], 80)
        chart_widget.addItem(target_label)

        # Add percentage labels on bars (pyqtgraph TextItem)
        for i, value in enumerate(y_vals):
            text_item = pg.TextItem(text=f'{int(value)}%', anchor=(0.5, 0), color='k')
            text_item.setPos(x_vals[i], value + 1)
            chart_widget.addItem(text_item)
            
    def create_fulfillment_chart(self, chart_widget):
        # Weekly fulfillment rate
        weekly_data = self.data.daily_metrics.tail(42).copy()
        weekly_data['Week'] = weekly_data['Date'].dt.to_period('W').dt.start_time
        
        weekly_summary = weekly_data.groupby('Week').agg({
            'Order_Fulfillment_Rate': 'mean'
        }).reset_index()
        
        x_vals = weekly_summary['Week'].apply(lambda x: x.timestamp()).values
        y_vals = weekly_summary['Order_Fulfillment_Rate'].values

        chart_widget.plot(x_vals, y_vals, pen=pg.mkPen(color='#9C27B0', width=2), symbol='o', symbolSize=8, symbolBrush='#9C27B0')
        chart_widget.plotItem.setTitle('Weekly Fulfillment Rate Trend')
        chart_widget.plotItem.setLabel('left', 'Fulfillment Rate %')
        chart_widget.plotItem.setLabel('bottom', 'Week', axisClass=pg.DateAxisItem)
        chart_widget.plotItem.setYRange(min(y_vals) * 0.9, max(y_vals) * 1.1)

        
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
                        padding: 12px 15px;
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
                        padding: 12px 15px;
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
            import logintravailleur as login
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
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#333333"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f0f0f0"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, QColor("#333333"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#e0e0e0"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#333333"))
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor("#2196F3"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2196F3"))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

    app.setPalette(palette)

    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())

