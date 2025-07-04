import sys
import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt6.QtGui import QIcon, QPixmap, QPen
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QFormLayout
from PyQt6.QtWidgets import QLineEdit, QComboBox, QDialog
from PyQt6.QtWidgets import QSpinBox, QListWidget, QSizePolicy, QSplitter
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QButtonGroup,
    QGroupBox, QScrollArea, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QDialog, QTextEdit, QSpinBox, QListWidget,QSizePolicy,
    QFormLayout, QSplitter, QMessageBox, QGridLayout, QFileDialog, QTabWidget, QDateEdit,
    QHeaderView # Import QHeaderView for table stretching
)

from PyQt6.QtCore import (
    QPropertyAnimation, 
    QEasingCurve, 
    QParallelAnimationGroup,
    QSequentialAnimationGroup
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QGraphicsBlurEffect
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtCore import QParallelAnimationGroup
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette,QIcon,QPixmap
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
    print("You have chosen the offline database.")
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="steevy",
        port=5432
    )
cur = conn.cursor()

cur.execute("SELECT (p).* FROM \"EMIR\".colis_eva() AS p;")
colis_db = cur.fetchall() # Existing packages from the database

cur.execute("SELECT (p).* FROM \"EMIR\".contenucolis_eva() AS p;")
contenu = cur.fetchall() # Existing packages from the database

class WarehouseData:
    """Data generator and manager for warehouse operations"""

    def __init__(self):
        self.generate_sample_data()

    def generate_sample_data(self):
        # Products data
        cur.execute("SELECT (p).* FROM \"EMIR\".produit_eva() AS p;")
        products = cur.fetchall()
        self.colis_df = pd.DataFrame(colis_db,columns=['id','date_cre','exp_date','receiving_org','statut'])
        self.contenu_df = pd.DataFrame(contenu,columns=['idcol','idlot','quantity','date_maj'])
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

        for i in self.colis_df.itertuples():
            print(i.id)
            cur.execute("SELECT \"EMIR\".getvaluecol(%s);",(i.id,))
            total = cur.fetchone()[0]
            items = [t for t in self.contenu_df.to_dict('records') if t['idcol'] == i.id]
            quan = len(items)
            cur.execute("SELECT \"EMIR\".getsupplier(%s);",(i.id,))
            suplier = cur.fetchone()[0]

            reception_data.append({
                'Order_ID': i.id,
                'Supplier': suplier,
                'Expected_Date': i.exp_date,
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
        destinations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']

        for i in range(25):
            expedition_data.append({
                'Order_ID': f'EO{i+1:03d}',
                'Destination': random.choice(destinations),
                'Request_Date': datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                'Items_Count': random.randint(1, 8),
                'Status': random.choice(statuses),
                'Total_Value': random.randint(500, 25000)
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
            color="#2196F3",
            icon="package"
        ), 0, 0)

        emballage_layout.addWidget(self.create_metric_card(
            title="Colis emballés",
            value="128",
            subtitle="Période: Aujourd'hui",
            info="Objectif: 150 colis/jour",
            color="#4CAF50",
            icon="check-circle"
        ), 0, 1)

        # Emballage Progress - Bottom Row
        progress_widget = self.create_progress_widget(
            title="Progression globale",
            progress=70,
            subtitle="Avancement des opérations",
            color="#FF9800"
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
            color="#2196F3",
            icon="package"
        ), 0, 0)

        desemballage_layout.addWidget(self.create_metric_card(
            title="Colis désemballés",
            value="76",
            subtitle="Période: Aujourd'hui",
            info="Efficacité: 85%",
            color="#4CAF50",
            icon="check-circle"
        ), 0, 1)

        # Désemballage Progress - Bottom Row
        progress_widget = self.create_progress_widget(
            title="Progression désemballage",
            progress=65,
            subtitle="Taux de complétion",
            color="#FF9800"
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
                border: 1px solid #e0e0e0;
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
                border: 1px solid #e0e0e0;
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
            icon_label.setPixmap(QIcon.fromTheme(icon).pixmap(24, 24))
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
                font-size: 12px;
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
                border: 1px solid #e0e0e0;
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
            self._main_layout = QGridLayout(self)

        layout = self._main_layout
        expedition_summary_table = self.create_expedition_summary_table()
        bouton = QPushButton("chatte")
        bouton.setStyleSheet("""
                    QPushButton { background-color: #2196F3; color: white; border: none;border-radius: 15px; margin-top:50px;font-weight: bold; }
                    QPushButton:hover { background-color: #1976D2; }
                """)
        layout.addWidget(expedition_summary_table,0,0,Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(bouton,1,0,Qt.AlignmentFlag.AlignBottom)

        
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
                width:90%;
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

class MenuReception(QWidget):
    def __init__(self,data):
        super().__init__()
        self.data=data
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
                    QPushButton { background-color: #2196F3; color: white; border: none; padding: 50px 16px; border-radius: 15px; font-weight: bold; }
                    QPushButton:hover { background-color: #1976D2; }
                """)
        layout.addWidget(expedition_summary_table,0,0,Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(bouton,1,0)

        
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
                width:200px;
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
            self._main_layout = QVBoxLayout(self)

        layout = self._main_layout
        layout.setContentsMargins(0, 0, 0, 0)

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
        # Example: Low Stock Exception # Make it an instance variable

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
        # Clear existing layout if init_ui is called multiple times
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QVBoxLayout(self)

        layout = self._main_layout
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Daily Operations Planning")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # Incorporate OrdersWidget as a central part of daily planning
        orders_section_label = QLabel("<h4>Order Management (Reception & Expedition)</h4>")
        layout.addWidget(orders_section_label)
        self.orders_widget = OrdersWidget(self.data)
        layout.addWidget(self.orders_widget)
        layout.setStretchFactor(self.orders_widget, 1) # Give orders widget stretch

        # Placeholder for other planning aspects
        planning_info_label = QLabel("<h3>Planning Tools:</h3>"
                                     "<ul>"
                                     "<li>Schedule Shipments & Receptions</li>"
                                     "<li>Allocate Workforce for Picking/Packing</li>"
                                     "<li>Forecast Demand (using historical data)</li>"
                                     "</ul>")
        layout.addWidget(planning_info_label)

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

        # Storage utilization
        utilization_chart = ChartWidget(title='Storage Utilization by Zone', y_label='Utilization %', x_label='Zone')
        self.create_utilization_chart(utilization_chart)
        utilization_chart.setMinimumHeight(300)
        charts_layout.addWidget(utilization_chart, 0, 1)

        # Fulfillment rate trend
        fulfillment_chart = ChartWidget(parent=self, title='Weekly Fulfillment Rate Trend', y_label='Fulfillment Rate %', x_label='Week',
                                        axisItems={'bottom': pg.DateAxisItem()})
        self.create_fulfillment_chart(fulfillment_chart)
        fulfillment_chart.setMinimumHeight(300)
        charts_layout.addWidget(fulfillment_chart, 1, 0, 1, 2)

        layout.addLayout(header_layout)
        layout.addLayout(kpi_layout)
        layout.addLayout(charts_layout)
        layout.addStretch() # Ensure content expands vertically

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