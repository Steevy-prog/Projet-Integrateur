import sys
import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt6.QtGui import QIcon, QPixmap, QPen, QPainter, QColor, QPalette, QFont
from PyQt6.QtCore import QRectF, Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup, QDate, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QTableWidget, QTableWidgetItem, QFormLayout, QLineEdit, QComboBox, QDialog,
    QSpinBox, QListWidget, QSizePolicy, QSplitter, QStackedWidget, QButtonGroup, QGroupBox,
    QHeaderView, QMessageBox, QGridLayout, QFileDialog, QTabWidget, QDateEdit, QProgressBar,
    QGraphicsOpacityEffect, QGraphicsBlurEffect
)
from PyQt6.QtCore import Qt
import datetime
import random
import psycopg2
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QBrush
#import login as login
import internalmail
from db_connection import ConnectionDB


# Configuration de la base de données
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
#         database="postgres",
#         user="postgres",
#         password="steevy",
#         port=5432
#     )


Connection = ConnectionDB()
Connection_info = Connection.connection()

db_connection = Connection_info['db_connection']

cur = conn.cursor()


cur.execute("SELECT (p).* FROM \"EMIR\".Conducteur_EVA() AS p;")
conducteurs = cur.fetchall()
if conducteurs is None:
  print("noiyo1")

cur.execute("SELECT (p).* FROM \"EMIR\".Colis_eva() AS p;")
colis = cur.fetchall()
if colis is None:
  print("noiyo2")

cur.execute("SELECT (p).* FROM \"EMIR\".Bonexpedition_eva() AS p;")
bonexp = cur.fetchall()
if bonexp is None:
  print("noiyo3")


cur.execute("SELECT (p).* FROM \"EMIR\".ContenuColis_eva() AS p;")
contenucolis = cur.fetchall()
if contenucolis is None:
  print("noiyo4")



class LogisticsData:
    """Data generator and manager for logistics operations"""
    
    def __init__(self):
        self.connection_info = Connection.connection()
        self.db_connection = self.connection_info['db_connection']
        self.generate_sample_data()
    def generate_sample_data(self):
        self.transporteurs_df = pd.DataFrame(conducteurs,columns=['id','idutil','nopermis','typepermis','date_obt','date_exp','annee_xp','statut','derniere_eva','noto_eva'])
        self.colis_df = pd.DataFrame(colis,columns=['id','date_cre','exp_date','receiving_org','statut'])
        self.bonexp_df = pd.DataFrame(bonexp,columns=['id','idcol','idtrans','date_cre','iddest','statut','remarque'])
        self.contenu_df = pd.DataFrame(contenucolis,columns=['idcol','idlot','quantity','date_maj'])

        #daily metrics

        dates = pd.date_range(start='2024-01-01', end='2024-06-19', freq='D')
        self.daily_metrics = pd.DataFrame({
            'Date': dates,
            'Items_Received': np.random.poisson(50, len(dates)),
            'Items_Shipped': np.random.poisson(45, len(dates)),
            'Storage_Utilization': np.random.uniform(60, 95, len(dates)),
            'Order_Fulfillment_Rate': np.random.uniform(85, 99, len(dates))
        })

        if not self.db_connection:
                self.connection_info = Connection.connection()
                self.db_connection = self.connection_info['db_connection']
        cur = self.db_connection.cursor()

        #reports
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
            self.products_df = pd.DataFrame(products, columns=['ID', 'Fourniseur', 'Name', 'Description', 'Prix Unitaire', 'idModel', 'Category'])
        
        for product in self.products_df.itertuples():
            print(f"Product ID: {product.ID}, Name: {product.Name}")

        inventory_data = []
        storage_zones = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2']
        if not self.products_df.empty: # Only proceed if products exist
            for _, product in self.products_df.iterrows():
                try:
                    cur.execute('SELECT "EMIR".quantityproduct(%s);', (product['ID'],))
                    quantity = cur.fetchone()[0]
                    if quantity is None:
                        print("cul")

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
        
        # Commandes en attente d'expédition
        expeditions = []
        statuts = ['En préparation', 'Prête à expédier', 'En transit', 'Livrée']
        destinations = ['Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Lille', 'Toulouse', 'Nantes']
        
        for i in self.colis_df.itertuples():
            transporteur = random.choice(self.transporteurs_df['id'].values)
            cur.execute("SELECT \"EMIR\".getvolume(%s)",(i.id,))
            volume = cur.fetchall()
            cur.execute("SELECT \"EMIR\".getvaluecol(%s)",(i.id,))
            value = cur.fetchall()
            cur.execute("SELECT \"EMIR\".getpoids(%s)",(i.id,))
            poids = cur.fetchall()
            expeditions.append({
                'id_commande': i.id,
                'destination': i.receiving_org,
                'date_creation': i.date_cre,
                'date_expedition': i.exp_date,
                'statut': i.statut,
                'poids': poids,
                'volume': volume,
                'cout_estime': value,
                #'urgence': random.choice(['Standard', 'Express', 'Prioritaire'])
            })
        self.expeditions_df = pd.DataFrame(expeditions)
        
        # Données de performance logistique
        dates = pd.date_range(start='2024-01-01', end='2024-06-19', freq='D')
        self.performance_df = pd.DataFrame({
            'date': dates,
            'commandes_expediees': np.random.poisson(25, len(dates)),
            'delais_moyens': np.random.uniform(1.5, 3.5, len(dates)),
            'taux_livraison': np.random.uniform(85, 99, len(dates)),
            'cout_transport': np.random.uniform(2000, 5000, len(dates))
        })
        
        # Données de traçabilité
        self.traces_df = pd.DataFrame([
            {'id_colis': 'COL001', 'etape': 'Réception', 'date': '2024-06-01 09:15', 'localisation': 'Entrepôt principal', 'statut': 'Terminé'},
            {'id_colis': 'COL001', 'etape': 'Vérification', 'date': '2024-06-01 10:30', 'localisation': 'Zone de contrôle', 'statut': 'Terminé'},
            {'id_colis': 'COL001', 'etape': 'Stockage', 'date': '2024-06-01 11:45', 'localisation': 'Zone B2', 'statut': 'Terminé'},
            {'id_colis': 'COL001', 'etape': 'Préparation', 'date': '2024-06-03 14:20', 'localisation': 'Zone d\'expédition', 'statut': 'Terminé'},
            {'id_colis': 'COL001', 'etape': 'Expédition', 'date': '2024-06-03 16:00', 'localisation': 'Transporteur DHL', 'statut': 'En cours'},
            {'id_colis': 'COL002', 'etape': 'Réception', 'date': '2024-06-02 08:30', 'localisation': 'Entrepôt principal', 'statut': 'Terminé'},
            {'id_colis': 'COL002', 'etape': 'Vérification', 'date': '2024-06-02 09:45', 'localisation': 'Zone de contrôle', 'statut': 'Terminé'},
            {'id_colis': 'COL002', 'etape': 'Stockage', 'date': '2024-06-02 11:00', 'localisation': 'Zone A1', 'statut': 'Terminé'},
            {'id_colis': 'COL003', 'etape': 'Réception', 'date': '2024-06-05 10:15', 'localisation': 'Entrepôt principal', 'statut': 'Terminé'},
            {'id_colis': 'COL003', 'etape': 'Vérification', 'date': '2024-06-05 11:30', 'localisation': 'Zone de contrôle', 'statut': 'En cours'}
        ])
        #vehicules
        self.vehicules_df = pd.DataFrame([
        {
        'immatriculation': 'AB-123-CD',
        'marque': 'Toyota',
        'modele': 'Hilux',
        'capacite': 1000,
        'disponibilite': True
        },
        {
        'immatriculation': 'EF-456-GH',
        'marque': 'Renault',
        'modele': 'Kangoo',
        'capacite': 750,
        'disponibilite': False
        },
        {
        'immatriculation': 'IJ-789-KL',
        'marque': 'Mercedes',
        'modele': 'Sprinter',
        'capacite': 1200,
        'disponibilite': True
        }
        ])

    

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
        try:
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
        except Exception as e:
            print(e)

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

class ChartWidget(pg.PlotWidget):
    """Custom PlotWidget for consistent styling"""
    
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

class LogisticsOverviewWidget(QWidget):
    """Vue d'ensemble des opérations logistiques"""
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.connection_info = Connection.connection()
        self.db_connection = self.connection_info['db_connection']

        self.init_ui()
    
    def init_ui(self):
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QVBoxLayout(self)
        
        # Créer un widget conteneur et un layout pour le contenu
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Vue d'ensemble logistique")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        
        refresh_btn = QPushButton("Actualiser")
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
        if not self.db_connection:
                self.connection_info = Connection.connection()
                self.db_connection = self.connection_info['db_connection']

        cur = self.db_connection.cursor()
        metrics_layout = QHBoxLayout()
        cur.execute("SELECT \"EMIR\".entransit()")
        cmd_en_transit = cur.fetchone()[0]
        
        # Calcul des métriques
        cur.execute("SELECT \"EMIR\".preparation_tasks()")
        cmd_en_prep = cur.fetchone()[0]
        delai_moyen = self.data.performance_df['delais_moyens'].mean()
        
        metrics_layout.addWidget(MetricCard("Commandes en prép.", cmd_en_prep, "À traiter", "#FF9800"))
        metrics_layout.addWidget(MetricCard("Prêtes à expédier", len(bonexp) , "En attente", "#2196F3"))
        metrics_layout.addWidget(MetricCard("En transit", cmd_en_transit, "En cours", "#4CAF50"))
        metrics_layout.addWidget(MetricCard("Délai moyen", f"{delai_moyen:.1f} jours", "Livraison", "#9C27B0"))
        
        # Charts section
        charts_layout = QHBoxLayout()
        
        # Commandes par statut
        status_chart = ChartWidget(title="Commandes par statut", y_label="Nombre", x_label="Statut")
        self.create_status_chart(status_chart)
        
        # Performance livraison
        perf_chart = ChartWidget(title="Performance de livraison", y_label="Taux (%)", x_label="Semaine")
        self.create_perf_chart(perf_chart)
        
        charts_layout.addWidget(status_chart)
        charts_layout.addWidget(perf_chart)
        
        # Commandes urgentes table
        #urgent_table = self.create_urgent_table()
        #urgent_table.setFixedHeight(500)  # 400 pixels de hauteur
        #urgent_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Ajouter tous les éléments au layout de contenu
        content_layout.addLayout(header_layout)
        content_layout.addLayout(metrics_layout)
        content_layout.addLayout(charts_layout)
        #content_layout.addWidget(urgent_table)
        
        # Créer la zone de défilement et y placer le widget de contenu
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Configurer le layout principal avec la zone de défilement
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.addWidget(scroll_area)
    
    def refresh_data(self):
        self.data.generate_sample_data()
        self.init_ui()
    
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())
    
    def create_status_chart(self, chart_widget):
        status_counts = self.data.expeditions_df['statut'].value_counts()
        x_vals = np.arange(len(status_counts))
        y_vals = status_counts.values
        
        colors = [QColor('#FF9800'), QColor('#2196F3'), QColor('#4CAF50'), QColor('#9C27B0')]
        brushes = [colors[i % len(colors)] for i in range(len(x_vals))]
        
        bargraph = pg.BarGraphItem(x=x_vals, height=y_vals, width=0.6, brushes=brushes)
        chart_widget.addItem(bargraph)
        
        ticks = [(i, label) for i, label in enumerate(status_counts.index)]
        chart_widget.getAxis('bottom').setTicks([ticks])
        
        for i, value in enumerate(y_vals):
            text_item = pg.TextItem(text=f'{int(value)}', anchor=(0.5, 0), color='k')
            text_item.setPos(x_vals[i], value + 0.1)
            chart_widget.addItem(text_item)
    
    def create_perf_chart(self, chart_widget):
        weekly_data = self.data.performance_df.copy()
        weekly_data['week'] = weekly_data['date'].dt.to_period('W').dt.start_time
        weekly_summary = weekly_data.groupby('week')['taux_livraison'].mean().reset_index()
        
        x_vals = weekly_summary['week'].apply(lambda x: x.timestamp()).values
        y_vals = weekly_summary['taux_livraison'].values
        
        chart_widget.plot(x_vals, y_vals, pen=pg.mkPen(color='#2196F3', width=2), symbol='o', symbolSize=8)
        chart_widget.plotItem.setYRange(min(y_vals)*0.9, 100)
        
        target_line = pg.InfiniteLine(95, angle=0, pen=pg.mkPen('r', width=2, style=Qt.PenStyle.DashLine))
        chart_widget.addItem(target_line)
        target_label = pg.TextItem("Objectif (95%)", color='r', anchor=(0.5, 0))
        target_label.setPos(x_vals[-1], 95)
        chart_widget.addItem(target_label)
    
    def create_urgent_table(self):
        #urgent_df = self.data.expeditions_df[self.data.expeditions_df['urgence'] != 'Standard'].sort_values('date_expedition')
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['ID Commande', 'Destination', 'Date expédition', 'Transporteur', 'Statut'])
        
        for i, in self.data.expeditions_df.itertuples():
            table.setItem(i, 0, QTableWidgetItem(i['id_commande']))
            table.setItem(i, 1, QTableWidgetItem(i['destination']))
            table.setItem(i, 2, QTableWidgetItem(str(i['date_expedition'])))
            
            match = self.data.transporteurs_df[self.data.transporteurs_df['id'] == i['id_transporteur']]
            if not match.empty:
                transporteur = match['idutil'].values[0]
            else:
                transporteur = "Inconnu"
            table.setItem(i, 3, QTableWidgetItem(transporteur))
            
            status_item = QTableWidgetItem(i['statut'])
            if i['statut'] == 'En préparation':
                status_item.setBackground(QColor('#BBDEFB'))  # Bleu clair
            elif i['statut'] == 'Prête à expédier':
                status_item.setBackground(QColor('#C8E6C9'))  # Vert clair
            else:
                status_item.setBackground(QColor('#E1BEE7'))  # Violet clair
            table.setItem(i, 4, status_item)
        
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #dcdcdc;
                border: 1px solid #e0e0e0;
                font-size: 12px;
                height:600px;
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
class ConducteurSelectionDialog(QDialog):
    """Fenêtre de sélection des conducteurs"""
    
    def __init__(self, conducteurs_df, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sélectionner un conducteur")
        self.setFixedSize(400, 300)
        self.selected_conducteur = None
        self.init_ui(conducteurs_df)
    
    def init_ui(self, conducteurs_df):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("Liste des conducteurs disponibles")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Tableau des conducteurs
        self.table = QTableWidget()
        self.table.setRowCount(len(conducteurs_df))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['ID', 'ID Util', 'Années d\'exp'])
        self.table.verticalHeader().setVisible(False)
        
        for i, (_, row) in enumerate(conducteurs_df.iterrows()):
            self.table.setItem(i, 0, QTableWidgetItem(row['id']))
            self.table.setItem(i, 1, QTableWidgetItem(row['idutil']))
            self.table.setItem(i, 2, QTableWidgetItem(str(row['annee_xp'])))
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.table.setStyleSheet("""
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
                padding: 8px;
                border: 1px solid #dcdcdc;
                font-weight: bold;
                font-size: 12px;
                color: #555;
            }
        """)
        
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)
        
        # Bouton de confirmation
        btn_confirm = QPushButton("Confirmer la sélection")
        btn_confirm.setStyleSheet("""
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
        btn_confirm.clicked.connect(self.on_confirm)
        layout.addWidget(btn_confirm, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Connecter le double-clic sur une ligne
        self.table.doubleClicked.connect(self.on_double_click)
    
    def on_confirm(self):
        selected = self.table.selectedItems()
        if selected:
            self.selected_conducteur = {
                'id': selected[0].text(),
                'idutil': selected[1].text(),
                'annee_xp': selected[2].text()
            }
            self.accept()
    
    def on_double_click(self, index):
        self.on_confirm()
class TransportManagementWidget(QWidget):
    """Gestion des transporteurs et des expéditions"""
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()
        self.assignments = []
    
    def init_ui(self):
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QVBoxLayout(self)
        
        layout = self._main_layout
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        title = QLabel("Gestion des transporteurs")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # 
        
        tabs = QTabWidget()
        
        # Onglet Transporteurs
        transporteurs_tab = self.create_transporteurs_tab()
        tabs.addTab(transporteurs_tab, "Colis a expedier")
        
        # Onglet Planification
        vehicules_tab = self.create_vehicules_table()
        tabs.addTab(vehicules_tab, "vehicules")
        
        layout.addWidget(tabs)
    def create_vehicules_table(self):
        """Crée le tableau des véhicules"""
        table = QTableWidget()

        # Supposons que self.data.vehicules_df contient les données des véhicules
        vehicules_data = self.data.vehicules_df 

        table.setRowCount(len(vehicules_data))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['Immatriculation', 'Marque', 'Modèle', 'Capacité (kg)', 'Disponibilité'])

        for i, (_, row) in enumerate(vehicules_data.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['immatriculation']))
            table.setItem(i, 1, QTableWidgetItem(row['marque']))
            table.setItem(i, 2, QTableWidgetItem(row['modele']))
            table.setItem(i, 3, QTableWidgetItem(str(row['capacite'])))

            dispo_item = QTableWidgetItem("Disponible" if row['disponibilite'] else "Indisponible")
            dispo_item.setForeground(QColor('green') if row['disponibilite'] else QColor('red'))
            table.setItem(i, 4, dispo_item)

        # Style du tableau
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
        """)

        table.setAlternatingRowColors(True)
        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)

        return table
    
    def create_transporteurs_tab(self):
        class data:
            def __init__(self,date,receiving_org,id):
                self.id = id
                self.receiving_org = receiving_org
                self.date = date
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Titre section
        title = QLabel("Colis à expédier")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        # Scroll area pour les frames
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)

        # Création des frames pour chaque colis
        for idx, (_, colis) in enumerate(self.data.expeditions_df.iterrows()):
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 5px;
                    border: 1px solid #e0e0e0;
                    padding: 10px;
                }
            """)

            frame_layout = QHBoxLayout(frame)

            # Infos colis
            info_layout = QVBoxLayout()
            info_layout.setSpacing(5)

            id_label = QLabel(f"ID Colis: {colis['id_commande']}")
            dest_label = QLabel(f"Destination: {colis['destination']}")
            date_label = QLabel(f"Date expédition: {str(colis['date_expedition'])}")

            for label in [id_label, dest_label, date_label]:
                label.setStyleSheet("font-size: 12px; color: #555;")
                info_layout.addWidget(label)

            frame_layout.addLayout(info_layout)
            frame_layout.addStretch()

            # Bouton assigner
            assign_btn = QPushButton("Assigner conducteur")
            assign_btn.setFixedWidth(150)
            assign_btn.setProperty("colis_index", idx)  # Stocker l'index du colis
            assign_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #43A047;
                }
            """)

            # Connecter le bouton à l'ouverture de la fenêtre de sélection
            assign_btn.clicked.connect(
                lambda _, b=assign_btn, colis_data=colis: 
                self.open_conducteur_dialog(b, data(colis_data['date_expedition'], colis_data['destination'], colis_data['id_commande']))
            )

            frame_layout.addWidget(assign_btn)
            scroll_layout.addWidget(frame)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        return widget

    def open_conducteur_dialog(self, button,datas):
        """Ouvre la fenêtre de sélection des conducteurs"""
        colis_index = button.property("colis_index")
        dialog = ConducteurSelectionDialog(self.data.transporteurs_df, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = dialog.selected_conducteur
            if selected:
                # Mettre à jour l'assignation du conducteur pour ce colis
                self.data.expeditions_df.at[colis_index, 'id_transporteur'] = selected['id']
                self.data.expeditions_df.at[colis_index, 'idutil_transporteur'] = selected['idutil']

                # Afficher un message de confirmation
                QMessageBox.information(
                    self, 
                    "Assignation réussie",
                    f"Le conducteur {selected['id']} a été assigné au colis {self.data.expeditions_df.at[colis_index, 'id_commande']}",
                    QMessageBox.StandardButton.Ok
                )
                self.assignments.append({
                                         'package_id': datas.id,
                                         'driver_id': selected['id'],
                                         'driver_user_id': selected['idutil'],
                                         'destination': datas.receiving_org,
                                         'date_expedition': datas.date
                                        })
                
                print(datas.date)
                internalmail.send_conducteur("SCA ASSIGNATION COLIS","thibaud.ambiana@2029.ucac-icam.com",datas.date,datas.id,datas.receiving_org)
                internalmail.send_conducteur("SCA ASSIGNATION COLIS","steevy.tongoue@2029.ucac-icam.com",datas.date,datas.id,datas.receiving_org)

    def create_planif_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Graphique de capacité
        cap_chart = ChartWidget(title="Capacité des transporteurs", y_label="Capacité (kg)", x_label="Transporteur")
        self.create_capacity_chart(cap_chart)
        
        # Tableau des expéditions
        expeditions_table = self.create_expeditions_table()
        
        # Bouton d'assignation
        assign_btn = QPushButton("Assigner transporteur")
        assign_btn.setStyleSheet("""
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
        
        layout.addWidget(cap_chart)
        layout.addWidget(expeditions_table)
        layout.addWidget(assign_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        return widget
    
    def create_transporteurs_table(self):
        table = QTableWidget()
        table.setRowCount(len(self.data.transporteurs_df))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['ID', 'IDUtil', 'Num permis', 'Type permis', 'annee d\'xp)'])
        
        for i, (_, row) in enumerate(self.data.transporteurs_df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['id']))
            table.setItem(i, 1, QTableWidgetItem(row['idutil']))
            table.setItem(i, 2, QTableWidgetItem(row['nopermis']))
            table.setItem(i, 3, QTableWidgetItem(row['typepermis']))
            table.setItem(i, 4, QTableWidgetItem(str(row['annee_xp'])))
        
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
    
    def create_capacity_chart(self, chart_widget):
        x_vals = np.arange(len(self.data.transporteurs_df))
        y_vals = self.data.transporteurs_df['capacite'].values
        
        colors = [QColor('#2196F3'), QColor('#4CAF50'), QColor('#FF9800'), QColor('#9C27B0')]
        brushes = [colors[i % len(colors)] for i in range(len(x_vals))]
        
        bargraph = pg.BarGraphItem(x=x_vals, height=y_vals, width=0.6, brushes=brushes)
        chart_widget.addItem(bargraph)
        
        ticks = [(i, label) for i, label in enumerate(self.data.transporteurs_df['idutil'])]
        chart_widget.getAxis('bottom').setTicks([ticks])
        
        for i, value in enumerate(y_vals):
            text_item = pg.TextItem(text=f'{int(value)}kg', anchor=(0.5, 0), color='k')
            text_item.setPos(x_vals[i], value + 50)
            chart_widget.addItem(text_item)
    
    def create_expeditions_table(self):
        table = QTableWidget()
        table.setRowCount(len(self.data.expeditions_df))
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(['ID Commande', 'Destination', 'Date expédition', 'Poids (kg)', 'Volume (m³)', 'Transporteur'])
        
        for i, (_, row) in enumerate(self.data.expeditions_df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['id_commande']))
            table.setItem(i, 1, QTableWidgetItem(row['destination']))
            table.setItem(i, 2, QTableWidgetItem(str(row['date_expedition'])))
            table.setItem(i, 3, QTableWidgetItem(str(row['poids'])))
            table.setItem(i, 4, QTableWidgetItem(str(row['volume'])))
            
            transporteur = self.data.transporteurs_df[self.data.transporteurs_df['id'] == row['id_transporteur']]['idutil'].values[0]
            transporteur_item = QTableWidgetItem(transporteur)
            
            # Vérifier si la capacité est suffisante
            cap_transp = self.data.transporteurs_df[self.data.transporteurs_df['id'] == row['id_transporteur']]['annee_exp'].values[0]
            if row['poids'] > cap_transp * 0.9:
                transporteur_item.setBackground(QColor('#FFCDD2'))  # Rouge si >90% capacité
            elif row['poids'] > cap_transp * 0.7:
                transporteur_item.setBackground(QColor('#FFF9C4'))  # Jaune si >70% capacité
            
            table.setItem(i, 5, transporteur_item)
        
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
    
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

class TraceabilityWidget(QWidget):
    """Widget de traçabilité des colis"""
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()
    
    def init_ui(self):
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QVBoxLayout(self)
        
        layout = self._main_layout
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        title = QLabel("Traçabilité des colis")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Sélection du colis
        search_layout = QHBoxLayout()
        search_label = QLabel("Rechercher un colis:")
        self.search_input = QLineEdit()
        search_btn = QPushButton("Rechercher")
        
        search_btn.setStyleSheet("""
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
        search_btn.clicked.connect(self.search_package)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # Résultats
        self.result_tabs = QTabWidget()
        layout.addWidget(self.result_tabs)
        
        # Initialiser avec un exemple
        self.display_trace('COL001')
    
    def search_package(self):
        package_id = self.search_input.text().strip()
        print(f"Recherche du colis: {package_id}")  # Debug
        if package_id:
            try:
                self.display_trace(package_id)
            except Exception as e:
                print(f"Erreur dans display_trace: {e}")  # Debug
    
    def display_trace(self, package_id):
        # Clear previous tabs
        while self.result_tabs.count() > 0:
            widget = self.result_tabs.widget(0)
            self.result_tabs.removeTab(0)
            widget.deleteLater()
    
        # Get traces for this package
        try:
            traces = self.data.traces_df[self.data.traces_df['id_colis'] == package_id]
        
            if traces.empty:
                no_data_widget = QWidget()
                no_data_layout = QVBoxLayout(no_data_widget)
                no_data_layout.addWidget(QLabel(f"Aucune donnée de traçabilité trouvée pour le colis {package_id}"))
                self.result_tabs.addTab(no_data_widget, "Résultats")
                return
        
            # Timeline tab
            timeline_tab = self.create_timeline_tab(traces)
            self.result_tabs.addTab(timeline_tab, "Chronologie")
        
            # Details tab
            details_tab = self.create_details_tab(traces)
            self.result_tabs.addTab(details_tab, "Détails")
        
        except Exception as e:
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_layout.addWidget(QLabel(f"Erreur lors du chargement des données: {str(e)}"))
            self.result_tabs.addTab(error_widget, "Erreur")
    def create_timeline_tab(self, traces):
        widget = QWidget()
        layout = QVBoxLayout(widget)
    
        # Timeline visualization
        timeline = QGraphicsView()
        scene = QGraphicsScene()
        timeline.setScene(scene)
        timeline.setRenderHint(QPainter.RenderHint.Antialiasing)
    
        # Draw timeline
        y_pos = 20
        for i, (_, trace) in enumerate(traces.iterrows()):
            # Timeline node
            color = QColor('#4CAF50') if trace['statut'] == 'Terminé' else QColor('#FF9800')
            scene.addEllipse(50, y_pos, 20, 20, QPen(color), QBrush(color))
        
            # Timeline text
            text = f"{trace['etape']} - {trace['date']}\nLocalisation: {trace['localisation']}"
            text_item = scene.addText(text, QFont("Arial", 10))
            text_item.setPos(80, y_pos)
        
        # Timeline connector (except last)
            if i < len(traces) - 1:
                scene.addLine(60, y_pos + 20, 60, y_pos + 40, QPen(QColor('#BDBDBD'), 2))
        
            y_pos += 60
    
        # Set minimum size for the view
        timeline.setMinimumSize(600, y_pos + 40)
    
        # Add scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(timeline)
    
        layout.addWidget(scroll_area)
        return widget
    
    def create_details_tab(self, traces):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        table = QTableWidget()
        table.setRowCount(len(traces))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Étape', 'Date', 'Localisation', 'Statut'])
        
        for i, (_, row) in enumerate(traces.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['etape']))
            table.setItem(i, 1, QTableWidgetItem(row['date']))
            table.setItem(i, 2, QTableWidgetItem(row['localisation']))
            
            status_item = QTableWidgetItem(row['statut'])
            if row['statut'] == 'Terminé':
                status_item.setBackground(QColor('#C8E6C9'))  # Vert clair
            else:
                status_item.setBackground(QColor('#FFECB3'))  # Orange clair
            table.setItem(i, 3, status_item)
        
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
        
        layout.addWidget(table)
        return widget
    
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

class LogisticsReportsWidget(QWidget):
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
                border: 1px solid #e0e0e0;
                font-size: 12px;
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

class LogisticsDashboardWidget(QWidget):
    """Dashboard principal pour le responsable logistique"""
    
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
        title_label = QLabel("Tableau de bord logistique")
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
            ("Vue d'ensemble", "home"),
            ("Gestion transporteurs", "truck"),
            ("Traçabilité", "package"),
            ("Rapports", "file-text"),
            ("Déconnexion", "system-log-out")
        ]
        
        for text, icon in menu_items:
            btn = QPushButton(text)
            btn.setIcon(QIcon.fromTheme(icon))
            
            # Style différent pour le bouton Déconnexion
            if text == "Déconnexion":
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
        
        # Add metrics data
        metrics_layout.addWidget(self.create_metric_label("Statistiques rapides"))
        
        # Calculate metrics.
        cmd_en_prep = len(self.data.expeditions_df[self.data.expeditions_df['statut'] == 'En préparation'])
        delai_moyen = self.data.performance_df['delais_moyens'].mean()
        
        metrics_layout.addWidget(self.create_metric_item("En préparation", f"{cmd_en_prep}"))
        metrics_layout.addWidget(self.create_metric_item("Prêtes à expédier", f"{len(bonexp)}"))
        metrics_layout.addWidget(self.create_metric_item("Délai moyen", f"{delai_moyen:.1f} jours"))
        
        # Insert metrics before Logout button
        sidebar_layout.insertWidget(len(menu_items) - 1, metrics_widget)
        sidebar_layout.addStretch(1)  # Push Logout to bottom
        
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
        self.switch_content("Vue d'ensemble")
    
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
        try:
            if self.current_widget:
                self.current_widget.deleteLater()
                self.current_widget = None
        
            if menu_item == "Vue d'ensemble":
                widget = LogisticsOverviewWidget(self.data)
            elif menu_item == "Gestion transporteurs":
                widget = TransportManagementWidget(self.data)
            elif menu_item == "Traçabilité":
                widget = TraceabilityWidget(self.data)
            elif menu_item == "Rapports":
                widget = LogisticsReportsWidget(self.data)
            else:
                return
            
            self.current_widget = widget
            self.content_layout.addWidget(widget)
        
        except Exception as e:
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_layout.addWidget(QLabel(f"Erreur lors du chargement de {menu_item}: {str(e)}"))
        
            if self.current_widget:
                self.current_widget.deleteLater()
            self.current_widget = error_widget
            self.content_layout.addWidget(error_widget)

class LogisticsMainWindow(QMainWindow):
    """Fenêtre principale pour le dashboard logistique"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Système de Gestion d'Entrepôt - Tableau de bord Logistique")
        self.setGeometry(100, 100, 1200, 800)
        
        self.data = LogisticsData()
        
        # Widget central
        self.central_widget = LogisticsDashboardWidget(self.data)
        self.setCentralWidget(self.central_widget)
        
        # Timer pour le rafraîchissement des données
    
    def refresh_data(self):
        print("Actualisation des données...")
        self.data.generate_sample_data()
        if hasattr(self.central_widget, 'init_ui'):
            self.central_widget.init_ui()
        print("Mise à jour de l'interface terminée.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Apply a modern style
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
    
    main_window = LogisticsMainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())