import sys
import numpy as np
import pandas as pd
import pyqtgraph as pg

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QButtonGroup,
    QGroupBox, QScrollArea, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QDialog, QTextEdit, QSpinBox, QListWidget,
    QFormLayout, QSplitter, QMessageBox, QGridLayout, QFileDialog, QTabWidget, QDateEdit,
    QHeaderView # Import QHeaderView for table stretching
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette
import datetime
import random
import psycopg2

idorg = 'OABCDE'
conn = psycopg2.connect(
    host="dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com",
    database="projet_integrateur",
    user="group13",
    password="nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3",
    port=5432
)
#conn = psycopg2.connect(
#    host="dpg-d1c2p8muk2gs73a9onng-a.oregon-postgres.render.com",
#    database="steevy1",
#    user="steevy",
#    password="T0vTIntru5D9SqS1qWnp2nxp7B9aOaWw",
#   port=5432
#)

#conn = psycopg2.connect(
#    host="localhost",
#    database="postgres",
#    user="postgres",
#    password="steevy",
#    port=5432
#)
cur = conn.cursor()

class WarehouseData:
    """Data generator and manager for warehouse operations"""

    def __init__(self):
        self.generate_sample_data()

    def generate_sample_data(self):
        # Products data
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

        for i in range(20):
            reception_data.append({
                'Order_ID': f'RO{i+1:03d}',
                'Supplier': random.choice(suppliers),
                'Expected_Date': datetime.date.today() + datetime.timedelta(days=random.randint(-5, 15)),
                'Items_Count': random.randint(1, 10),
                'Status': random.choice(statuses),
                'Total_Value': random.randint(1000, 50000)
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
        # Clear existing layout if init_ui is called multiple times (e.g., on refresh)
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QVBoxLayout(self) # Set QVBoxLayout for the widget

        layout = self._main_layout
        layout.setContentsMargins(0, 0, 0, 0) # Remove outer margins for better scroll area fit

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Real-time Inventory View")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")

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

        # Metrics cards
        metrics_layout = QHBoxLayout()
        # Handle potential psycopg2.ProgrammingError if function doesn't exist or returns no rows
        try:
            cur.execute("SELECT \"EMIR\".total();")
            total_items = cur.fetchone()[0]
            if total_items is None:
                print("fuck")
                total_items = 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching total_items: {e}. Using dummy value.")
            total_items = 0

        try:
            cur.execute("SELECT \"EMIR\".valeur();")
            total_value = cur.fetchone()[0]
            if total_value is None:
                print("fuck")
                total_value = 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching total_value: {e}. Using dummy value.")
            total_value = 0

        try:
            cur.execute("SELECT \"EMIR\".available_cells();")
            available_cells = cur.fetchone()[0]
            if available_cells is None:
                print("fuck")
                available_cells = 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching available_cells: {e}. Using dummy value.")
            available_cells = 0

        try:
            cur.execute("SELECT \"EMIR\".numzones();")
            zones_used = cur.fetchone()[0]
            if zones_used is None:
                print("fuck")
                zones_used = 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching numzones: {e}. Using dummy value.")
            zones_used = 0


        metrics_layout.addWidget(MetricCard("Total Items", f"{total_items:,}", "In Stock"))
        metrics_layout.addWidget(MetricCard("Total Value", f"${total_value:,.0f}", "Inventory Worth"))
        metrics_layout.addWidget(MetricCard("Available Cells", f"{available_cells:,}", "Cells Not In Use", "#FF9800"))
        metrics_layout.addWidget(MetricCard("Storage Zones", str(zones_used), "Active Zones"))

        # Charts section
        charts_layout = QHBoxLayout()
        charts_layout.setStretchFactor(charts_layout, 1) # Ensure charts stretch

        # Stock by category bar chart (pyqtgraph does not have native pie chart)
        category_chart = ChartWidget(title="Inventory by Category", y_label="Quantity", x_label="Category")
        self.create_category_chart(category_chart)
        category_chart.setMinimumHeight(300) # Ensure charts have a minimum height

        # Stock levels bar chart
        stock_chart = ChartWidget(title="Stock Levels - Top Products", y_label="Quantity", x_label="Products")
        self.create_stock_levels_chart(stock_chart)
        stock_chart.setMinimumHeight(300)

        charts_layout.addWidget(category_chart)
        charts_layout.addWidget(stock_chart)

        # Inventory table (can be considered a detailed view for Product Details and Location Details)
        self.inventory_table = self.create_inventory_table()
        # Wrap table in scroll area if it might exceed vertical space
        table_scroll_area = QScrollArea()
        table_scroll_area.setWidgetResizable(True)
        table_scroll_area.setWidget(self.inventory_table)
        table_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        table_scroll_area.setMinimumHeight(200) # Give table a minimum height


        # Placeholder for Stock Movements (New section)
        stock_movements_label = QLabel("Stock Movements (Not Implemented Yet)")
        stock_movements_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 15px;")
        # In a real application, this would be a table or chart showing recent movements.

        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        layout.addLayout(charts_layout)
        layout.addWidget(table_scroll_area) # Add the scrollable table
        layout.addWidget(stock_movements_label) # Add the placeholder
        layout.addStretch() # Push everything to the top

        # Set the layout of the widget only once
        if self.layout() is None:
            self.setLayout(layout)

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

        container = QWidget()
        container.setStyleSheet("background-color: #f5f5f5;")
        big_layout = QGridLayout(container)
        big_layout.setVerticalSpacing(20)
        big_layout.setHorizontalSpacing(20)
        big_layout.setContentsMargins(20, 20, 20, 20)

        # Frame pour l'emballage
        emballage_frame = QFrame()
        emballage_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        emballage_layout = QVBoxLayout(emballage_frame)
        emballage_layout.setSpacing(20)

        # Titre Emballage
        emballage_title = QLabel("Emballage")
        emballage_title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                color: #2c3e50;
                font-weight: bold;
                padding-bottom: 10px;
            }
        """)
        emballage_layout.addWidget(emballage_title)

        # Cartes de métriques pour Emballage
        metrics_emballage_layout = QGridLayout()
        metrics_emballage_layout.setVerticalSpacing(15)
        metrics_emballage_layout.setHorizontalSpacing(15)


        # Carte 1 - Colis à emballer
        card1 = self.create_metric_card(
            title="42",
            value="En attente",
            subtitle="Dernière mise à jour: 05/03/2025",
            color="#2196F3",
            title_label="Colis à emballer",
            value_label="Statut",
            subtitle_label="Information"
        )
        metrics_emballage_layout.addWidget(card1, 0, 0)

        # Carte 2 - Colis emballés
        card2 = self.create_metric_card(
            title="128",
            value="Aujourd'hui",
            subtitle="Objectif: 150 colis/jour",
            color="#4CAF50",
            title_label="Colis emballés",
            value_label="Période",
            subtitle_label="Performance"
        )
        metrics_emballage_layout.addWidget(card2, 0, 1)

        # Carte 3 - Progression
        card3 = self.create_metric_card(
            title="70%",
            value="05/03/2025",
            subtitle="Avancement global",
            color="#FF9800",
            title_label="Progression",
            value_label="Date",
            subtitle_label="Détails",
            label_color="#FFFFFF",
            label_bg="#607D8B"
        )
        
        metrics_emballage_layout.addWidget(card3, 1, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        emballage_layout.addLayout(metrics_emballage_layout)
        emballage_layout.addStretch()

        # Frame pour le désemballage
        desemballage_frame = QFrame()
        desemballage_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        desemballage_layout = QVBoxLayout(desemballage_frame)
        desemballage_layout.setSpacing(20)

        # Titre Désemballage
        desemballage_title = QLabel("Désemballage")
        desemballage_title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                color: #2c3e50;
                font-weight: bold;
                padding-bottom: 10px;
            }
        """)
        desemballage_layout.addWidget(desemballage_title)

        # Cartes de métriques pour Désemballage
        metrics_desemballage_layout = QGridLayout()
        metrics_desemballage_layout.setVerticalSpacing(15)
        metrics_desemballage_layout.setHorizontalSpacing(15)

        # Carte 4 - Colis à désemballer
        card4 = self.create_metric_card(
            title="24",
            value="En attente",
            subtitle="Priorité: Moyenne",
            color="#2196F3",
            title_label="Colis à désemballer",
            value_label="Statut",
            subtitle_label="Information"
        )
        metrics_desemballage_layout.addWidget(card4, 0, 0)

        # Carte 5 - Colis désemballés
        card5 = self.create_metric_card(
            title="76",
            value="Aujourd'hui",
            subtitle="Efficacité: 85%",
            color="#4CAF50",
            title_label="Colis désemballés",
            value_label="Période",
            subtitle_label="Performance"
        )
        metrics_desemballage_layout.addWidget(card5, 0, 1)
        # Carte 6 - Progression désemballage
        card6 = self.create_metric_card(
            title="65%",
            value="05/03/2025",
            subtitle="Taux de complétion",
            color="#FF9800",
            title_label="Progression",
            value_label="Date",
            subtitle_label="Détails",
            label_color="#FFFFFF",
            label_bg="#607D8B"
        )
        
        metrics_desemballage_layout.addWidget(card6, 1, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        desemballage_layout.addLayout(metrics_desemballage_layout)
        desemballage_layout.addStretch()

        # Ajout des frames à la disposition principale
        big_layout.addWidget(emballage_frame, 0, 0)
        big_layout.addWidget(desemballage_frame, 1, 0)

        self._main_layout.addWidget(container) # Add the container to the widget's main layout
        self._main_layout.addStretch() # Ensure it expands

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def create_metric_card(self, title, value, subtitle, color,
                           title_label=None, value_label=None, subtitle_label=None,
                           label_color="#555", label_bg="#f8f9fa"):
        """Crée une carte de métrique avec des labels optionnels pour chaque élément"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Style pour les labels descriptifs
        label_style = f"""
            QLabel {{
                font-size: 14px;
                color: {label_color};
                font-weight: 500;
                padding: 4px 8px;
                background-color: {label_bg};
                border-radius: 4px;
                border: 1px solid #e0e0e0;
                margin-bottom: 2px;
            }}
        """

        # Titre avec label optionnel
        if title_label:
            title_desc = QLabel(title_label)
            title_desc.setStyleSheet(label_style)
            layout.addWidget(title_desc)

        title_widget = QLabel(title)
        title_widget.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #666;
                font-weight: bold;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title_widget)

        # Valeur avec label optionnel
        if value_label:
            value_desc = QLabel(value_label)
            value_desc.setStyleSheet(label_style)
            layout.addWidget(value_desc)

        value_widget = QLabel(value)
        value_widget.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {color};
                margin: 5px 0;
            }}
        """)
        layout.addWidget(value_widget)

        # Sous-titre avec label optionnel
        if subtitle_label:
            subtitle_desc = QLabel(subtitle_label)
            subtitle_desc.setStyleSheet(label_style)
            layout.addWidget(subtitle_desc)

        subtitle_widget = QLabel(subtitle)
        subtitle_widget.setStyleSheet("""
            QLabel {{
                font-size: 20px;
                color: #999;
                margin-top: 5px;
            }}
        """)
        layout.addWidget(subtitle_widget)

        layout.addStretch()
        return card

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
        bouton.setFixedWidth(1000) # This fixed width might constrain layout
        bouton.setStyleSheet("""
                       QPushButton { background-color: #2196F3; color: white; border: none; padding: 50px 16px; border-radius: 15px; font-weight: bold; 
                       width:10px;}
                       QPushButton:hover { background-color: #1976D2; }
                   """)
        layout.addWidget(expedition_summary_table,0,0)
        layout.addWidget(bouton,0,1)
        layout.setColumnStretch(0, 3) # Give more stretch to the table column
        layout.setColumnStretch(1, 1) # Give less stretch to the button column
        layout.addLayout(QHBoxLayout(), 1, 0, 1, 2) # Add stretch at bottom
        
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
        reception_summary_table = self.create_reception_summary_table()
        bouton = QPushButton("informer magasinier")
        bouton.setFixedWidth(1000) # This fixed width might constrain layout
        bouton.setStyleSheet("""
               QPushButton { background-color: #2196F3; color: white; border: none; padding: 50px 16px; border-radius: 15px; font-weight: bold; 
               width:10px;}
               QPushButton:hover { background-color: #1976D2; }
           """)
        layout.addWidget(bouton,0,1)
        layout.addWidget(reception_summary_table,0,0)
        layout.setColumnStretch(0, 3) # Give more stretch to the table column
        layout.setColumnStretch(1, 1) # Give less stretch to the button column
        layout.addLayout(QHBoxLayout(), 1, 0, 1, 2) # Add stretch at bottom

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def create_reception_summary_table(self):
        table = QTableWidget()
        table.setRowCount(len(self.data.reception2_df))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(['identifiant du colis','date prevue', 'Statut'])

        for i, (_, row) in enumerate(self.data.reception2_df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['identifiant du colis']))
            table.setItem(i, 1, QTableWidgetItem(str(row['date prevue'])))
            table.setItem(i, 2, QTableWidgetItem(row['Statuts']))
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
        tabs.addTab(MenuReception(self.data), "menu reception")
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

class MainDashboardWidget(QWidget):
    """Main dashboard content area"""

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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Top section with welcome and overview
        top_layout = QHBoxLayout()
        welcome_label = QLabel("<h2>Welcome, Manager!</h2>")
        welcome_label.setStyleSheet("color: #333; margin-bottom: 10px;")
        top_layout.addWidget(welcome_label)
        top_layout.addStretch()

        # Overview cards - metrics derived from the data
        try:
            cur.execute('SELECT "EMIR".total();')
            total_items = cur.fetchone()[0]
            if total_items is None:
                print("fuck")
                total_items = 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching total_items for dashboard: {e}. Using dummy value.")
            total_items = 0

        try:
            cur.execute('SELECT "EMIR".valeur();')
            total_value = cur.fetchone()[0]
            if total_value is None:
                print("fuck")
                total_value = 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching total_value for dashboard: {e}. Using dummy value.")
            total_value = 0

        try:
            cur.execute("SELECT \"EMIR\".available_cells();")
            available_cells = cur.fetchone()[0]
            if available_cells is None:
                print("fuck")
                available_cells = 0
        except (psycopg2.Error, TypeError) as e:
            print(f"Error fetching available_cells for dashboard: {e}. Using dummy value.")
            available_cells = 0
        
        overview_layout = QHBoxLayout()
        overview_layout.addWidget(MetricCard("Total Items", f"{total_items:,}", "Current Stock"))
        overview_layout.addWidget(MetricCard("Total Inventory Value", f"${total_value:,.0f}", "Estimated Worth"))
        overview_layout.addWidget(MetricCard("Available Cells", f"{available_cells:,}", "For Storage", "#FF9800"))
        
        layout.addLayout(top_layout)
        layout.addLayout(overview_layout)

        # Main content sections as tabs or stacked widgets (for easy navigation)
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(RealtimeInventoryViewWidget(self.data), "Real-time Inventory")
        self.tab_widget.addTab(DailyOperationsPlanningWidget(self.data), "Daily Operations Planning")
        self.tab_widget.addTab(StorageSpaceManagementWidget(self.data), "Storage Space Management")
        self.tab_widget.addTab(ReportsWidget(self.data), "Generate Reports")
        self.tab_widget.addTab(WarehouseMenuInteractionWidget(self.data),"warehouse interactions")

        layout.addWidget(self.tab_widget)
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warehouse Management System - Manager Dashboard")
        self.setGeometry(100, 100, 1200, 800)

        self.data = WarehouseData()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.init_ui()

    # Helper function to make a widget scrollable
    def scrollable(self, widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        scroll.setFrameShape(QFrame.Shape.NoFrame) # No border around the scroll area
        return scroll

    def init_ui(self):
        # Create a navigation bar
        navbar = QFrame()
        navbar.setStyleSheet("background-color: #34495E; padding: 10px;")
        navbar_layout = QHBoxLayout(navbar)
        navbar_layout.setSpacing(15)

        # Logo/Title
        logo_label = QLabel("WMS Dashboard")
        logo_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        navbar_layout.addWidget(logo_label)

        # Navigation buttons (example: could be implemented as a QButtonGroup)
        self.home_btn = QPushButton("Dashboard")
        self.inventory_btn = QPushButton("Inventory")
        self.planning_btn = QPushButton("Planning")
        self.storage_btn = QPushButton("Storage")
        self.reports_btn = QPushButton("Reports")
        self.interaction_btn = QPushButton("Warehouse Interactions")

        buttons = [self.home_btn, self.inventory_btn, self.planning_btn, self.storage_btn, self.reports_btn, self.interaction_btn]
        self.button_group = QButtonGroup(self) # Create a button group
        for btn in buttons:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #34495E;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #2C3E50;
                }
                QPushButton:checked {
                    background-color: #2C3E50;
                    border: 1px solid #2196F3;
                }
            """)
            btn.setCheckable(True)
            self.button_group.addButton(btn) # Add button to group
            navbar_layout.addWidget(btn)

        navbar_layout.addStretch()

        self.main_layout.addWidget(navbar)

        # Main content area - now all wrapped in scrollable widgets
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #F0F2F5; padding: 20px;") # Content area background

        # Initialize widgets and wrap them in scroll areas
        self.dashboard_widget = self.scrollable(MainDashboardWidget(self.data))
        self.inventory_view_widget = self.scrollable(RealtimeInventoryViewWidget(self.data))
        self.daily_planning_widget = self.scrollable(DailyOperationsPlanningWidget(self.data))
        self.storage_management_widget = self.scrollable(StorageSpaceManagementWidget(self.data))
        self.reports_widget = self.scrollable(ReportsWidget(self.data))
        self.interaction_widget = self.scrollable(WarehouseMenuInteractionWidget(self.data))

        # Add scrollable widgets to the stacked widget
        self.content_stack.addWidget(self.dashboard_widget)
        self.content_stack.addWidget(self.inventory_view_widget)
        self.content_stack.addWidget(self.daily_planning_widget)
        self.content_stack.addWidget(self.storage_management_widget)
        self.content_stack.addWidget(self.reports_widget)
        self.content_stack.addWidget(self.interaction_widget)

        self.main_layout.addWidget(self.content_stack)

        # Connect buttons to navigation and ensure only one is checked
        self.home_btn.clicked.connect(lambda: self.navigate_to_widget(self.dashboard_widget))
        self.inventory_btn.clicked.connect(lambda: self.navigate_to_widget(self.inventory_view_widget))
        self.planning_btn.clicked.connect(lambda: self.navigate_to_widget(self.daily_planning_widget))
        self.storage_btn.clicked.connect(lambda: self.navigate_to_widget(self.storage_management_widget))
        self.reports_btn.clicked.connect(lambda: self.navigate_to_widget(self.reports_widget))
        self.interaction_btn.clicked.connect(lambda: self.navigate_to_widget(self.interaction_widget))

        # Set initial view and check the corresponding button
        self.home_btn.setChecked(True)
        self.content_stack.setCurrentWidget(self.dashboard_widget)

        # Timer for periodic data refresh (optional)
        self.timer = QTimer(self)
        self.timer.setInterval(60000) # 1 minute
        self.timer.timeout.connect(self.refresh_all_data)
        self.timer.start()

    def navigate_to_widget(self, target_scroll_widget):
        self.content_stack.setCurrentWidget(target_scroll_widget)
        # Get the actual widget inside the QScrollArea
        target_inner_widget = target_scroll_widget.widget()
        # Ensure UI elements of the target inner widget are refreshed if they have an init_ui method
        if hasattr(target_inner_widget, 'init_ui'):
            target_inner_widget.init_ui()
        
        # Uncheck all buttons and then check the corresponding one
        for button in self.button_group.buttons():
            if button != self.sender(): # Don't uncheck the button that was just clicked
                button.setChecked(False)

    def refresh_all_data(self):
        print("Refreshing all data...")
        self.data.generate_sample_data() # Refresh underlying data

        # Refresh individual widgets that display data
        # We need to get the inner widget from the QScrollArea
        if hasattr(self.dashboard_widget.widget(), "init_ui"):
            self.dashboard_widget.widget().init_ui()
        if hasattr(self.inventory_view_widget.widget(), "init_ui"):
            self.inventory_view_widget.widget().init_ui()
        if hasattr(self.daily_planning_widget.widget(), "init_ui"):
            self.daily_planning_widget.widget().init_ui()
        if hasattr(self.reports_widget.widget(), "init_ui"):
            self.reports_widget.widget().init_ui()
        if hasattr(self.interaction_widget.widget(), "init_ui"):
            self.interaction_widget.widget().init_ui()

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