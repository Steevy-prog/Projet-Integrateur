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
import datetime
import random
import psycopg2
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QBrush
import login as login

# Configuration de la base de données
conn = psycopg2.connect(
    host="dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com",
    database="projet_integrateur",
    user="group13",
    password="nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3",
    port=5432
)
cur = conn.cursor()

class LogisticsData:
    """Data generator and manager for logistics operations"""
    
    def __init__(self):
        self.generate_sample_data()
    
    def generate_sample_data(self):
        # Données des transporteurs
        transporteurs = [
            {'id': 'TR001', 'nom': 'DHL Express', 'contact': 'Jean Dupont', 'tel': '+123456789', 'capacite': 5000, 'cout_km': 0.85},
            {'id': 'TR002', 'nom': 'FedEx', 'contact': 'Marie Martin', 'tel': '+987654321', 'capacite': 4500, 'cout_km': 0.78},
            {'id': 'TR003', 'nom': 'UPS', 'contact': 'Pierre Lambert', 'tel': '+456123789', 'capacite': 6000, 'cout_km': 0.92},
            {'id': 'TR004', 'nom': 'Chronopost', 'contact': 'Sophie Leroy', 'tel': '+789456123', 'capacite': 4000, 'cout_km': 0.75}
        ]
        self.transporteurs_df = pd.DataFrame(transporteurs)
        
        # Commandes en attente d'expédition
        expeditions = []
        statuts = ['En préparation', 'Prête à expédier', 'En transit', 'Livrée']
        destinations = ['Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Lille', 'Toulouse', 'Nantes']
        
        for i in range(15):
            transporteur = random.choice(self.transporteurs_df['id'].values)
            expeditions.append({
                'id_commande': f'CMD{i+1:03d}',
                'destination': random.choice(destinations),
                'date_creation': datetime.date.today() - datetime.timedelta(days=random.randint(0, 5)),
                'date_expedition': datetime.date.today() + datetime.timedelta(days=random.randint(0, 3)),
                'statut': random.choice(statuts),
                'poids': random.randint(5, 50),
                'volume': random.randint(1, 10),
                'id_transporteur': transporteur,
                'cout_estime': round(random.uniform(50, 500), 2),
                'urgence': random.choice(['Standard', 'Express', 'Prioritaire'])
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
        self.init_ui()
    
    def init_ui(self):
        if hasattr(self, '_main_layout') and self._main_layout is not None:
            self.clear_layout(self._main_layout)
        else:
            self._main_layout = QVBoxLayout(self)
        
        layout = self._main_layout
        layout.setContentsMargins(0, 0, 0, 0)
        
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
        metrics_layout = QHBoxLayout()
        
        # Calcul des métriques
        cmd_en_prep = len(self.data.expeditions_df[self.data.expeditions_df['statut'] == 'En préparation'])
        cmd_pretes = len(self.data.expeditions_df[self.data.expeditions_df['statut'] == 'Prête à expédier'])
        cmd_en_transit = len(self.data.expeditions_df[self.data.expeditions_df['statut'] == 'En transit'])
        delai_moyen = self.data.performance_df['delais_moyens'].mean()
        
        metrics_layout.addWidget(MetricCard("Commandes en prép.", cmd_en_prep, "À traiter", "#FF9800"))
        metrics_layout.addWidget(MetricCard("Prêtes à expédier", cmd_pretes, "En attente", "#2196F3"))
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
        urgent_table = self.create_urgent_table()
        table_scroll = QScrollArea()
        table_scroll.setWidgetResizable(True)
        table_scroll.setWidget(urgent_table)
        table_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        layout.addLayout(charts_layout)
        layout.addWidget(table_scroll)
    
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
        urgent_df = self.data.expeditions_df[self.data.expeditions_df['urgence'] != 'Standard'].sort_values('date_expedition')
        
        table = QTableWidget()
        table.setRowCount(len(urgent_df))
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(['ID Commande', 'Destination', 'Date expédition', 'Urgence', 'Transporteur', 'Statut'])
        
        for i, (_, row) in enumerate(urgent_df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['id_commande']))
            table.setItem(i, 1, QTableWidgetItem(row['destination']))
            table.setItem(i, 2, QTableWidgetItem(str(row['date_expedition'])))
            
            urgency_item = QTableWidgetItem(row['urgence'])
            if row['urgence'] == 'Prioritaire':
                urgency_item.setBackground(QColor('#FFCDD2'))  # Rouge clair
            else:
                urgency_item.setBackground(QColor('#FFF9C4'))  # Jaune clair
            table.setItem(i, 3, urgency_item)
            
            transporteur = self.data.transporteurs_df[self.data.transporteurs_df['id'] == row['id_transporteur']]['nom'].values[0]
            table.setItem(i, 4, QTableWidgetItem(transporteur))
            
            status_item = QTableWidgetItem(row['statut'])
            if row['statut'] == 'En préparation':
                status_item.setBackground(QColor('#BBDEFB'))  # Bleu clair
            elif row['statut'] == 'Prête à expédier':
                status_item.setBackground(QColor('#C8E6C9'))  # Vert clair
            else:
                status_item.setBackground(QColor('#E1BEE7'))  # Violet clair
            table.setItem(i, 5, status_item)
        
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

class TransportManagementWidget(QWidget):
    """Gestion des transporteurs et des expéditions"""
    
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
        title = QLabel("Gestion des transporteurs")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet Transporteurs
        transporteurs_tab = self.create_transporteurs_tab()
        tabs.addTab(transporteurs_tab, "Transporteurs")
        
        # Onglet Planification
        planif_tab = self.create_planif_tab()
        tabs.addTab(planif_tab, "Planification")
        
        layout.addWidget(tabs)
    
    def create_transporteurs_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tableau des transporteurs
        transporteurs_table = self.create_transporteurs_table()
        
        # Boutons d'action
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Ajouter")
        edit_btn = QPushButton("Modifier")
        remove_btn = QPushButton("Supprimer")
        
        for btn in [add_btn, edit_btn, remove_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    margin-right: 5px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        
        layout.addWidget(transporteurs_table)
        layout.addLayout(btn_layout)
        
        return widget
    
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
        table.setHorizontalHeaderLabels(['ID', 'Nom', 'Contact', 'Téléphone', 'Capacité (kg)'])
        
        for i, (_, row) in enumerate(self.data.transporteurs_df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['id']))
            table.setItem(i, 1, QTableWidgetItem(row['nom']))
            table.setItem(i, 2, QTableWidgetItem(row['contact']))
            table.setItem(i, 3, QTableWidgetItem(row['tel']))
            table.setItem(i, 4, QTableWidgetItem(str(row['capacite'])))
        
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
        
        ticks = [(i, label) for i, label in enumerate(self.data.transporteurs_df['nom'])]
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
            
            transporteur = self.data.transporteurs_df[self.data.transporteurs_df['id'] == row['id_transporteur']]['nom'].values[0]
            transporteur_item = QTableWidgetItem(transporteur)
            
            # Vérifier si la capacité est suffisante
            cap_transp = self.data.transporteurs_df[self.data.transporteurs_df['id'] == row['id_transporteur']]['capacite'].values[0]
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
    """Widget pour les rapports logistiques"""
    
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
        title = QLabel("Rapports logistiques")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Date range selection
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Période:"))
        
        self.from_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.from_date.setCalendarPopup(True)
        date_layout.addWidget(self.from_date)
        
        date_layout.addWidget(QLabel("à"))
        
        self.to_date = QDateEdit(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        date_layout.addWidget(self.to_date)
        
        generate_btn = QPushButton("Générer rapport")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
        """)
        generate_btn.clicked.connect(self.generate_report)
        
        date_layout.addWidget(generate_btn)
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Report tabs
        self.report_tabs = QTabWidget()
        layout.addWidget(self.report_tabs)
        
        # Generate initial report
        self.generate_report()
    
    def generate_report(self):
        # Clear previous tabs
        while self.report_tabs.count() > 0:
            self.report_tabs.removeTab(0)
        
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        
        # Performance tab
        perf_tab = self.create_performance_tab(from_date, to_date)
        self.report_tabs.addTab(perf_tab, "Performance")
        
        # Costs tab
        costs_tab = self.create_costs_tab(from_date, to_date)
        self.report_tabs.addTab(costs_tab, "Coûts")
        
        # Transport tab
        transport_tab = self.create_transport_tab(from_date, to_date)
        self.report_tabs.addTab(transport_tab, "Transporteurs")
    
    def create_performance_tab(self, from_date, to_date):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filter data
        mask = (self.data.performance_df['date'] >= from_date) & (self.data.performance_df['date'] <= to_date)
        filtered_df = self.data.performance_df[mask]
        
        if filtered_df.empty:
            layout.addWidget(QLabel("Aucune donnée disponible pour cette période"))
            return widget
        
        # Metrics
        metrics_layout = QHBoxLayout()
        
        avg_delivery = filtered_df['delais_moyens'].mean()
        success_rate = filtered_df['taux_livraison'].mean()
        total_shipments = filtered_df['commandes_expediees'].sum()
        
        metrics_layout.addWidget(MetricCard("Délai moyen", f"{avg_delivery:.1f} jours", "Livraison"))
        metrics_layout.addWidget(MetricCard("Taux réussite", f"{success_rate:.1f}%", "Livraisons"))
        metrics_layout.addWidget(MetricCard("Commandes", f"{total_shipments:,}", "Expédiées"))
        
        layout.addLayout(metrics_layout)
        
        # Charts
        charts_layout = QHBoxLayout()
        
        # Delivery time trend
        deliv_chart = ChartWidget(parent=self, title='Délais de livraison', y_label='Jours', x_label='Date',
                                 axisItems={'bottom': pg.DateAxisItem()})
        x_vals = filtered_df['date'].apply(lambda x: x.timestamp()).values
        deliv_chart.plot(x_vals, filtered_df['delais_moyens'].values, pen=pg.mkPen(color='#2196F3', width=2))
        deliv_chart.setMinimumHeight(300)
        
        # Success rate trend
        success_chart = ChartWidget(parent=self, title='Taux de livraison', y_label='%', x_label='Date',
                                   axisItems={'bottom': pg.DateAxisItem()})
        success_chart.plot(x_vals, filtered_df['taux_livraison'].values, pen=pg.mkPen(color='#4CAF50', width=2))
        success_chart.setMinimumHeight(300)
        
        charts_layout.addWidget(deliv_chart)
        charts_layout.addWidget(success_chart)
        layout.addLayout(charts_layout)
        
        return widget
    
    def create_costs_tab(self, from_date, to_date):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filter expeditions data
        mask = (self.data.expeditions_df['date_expedition'] >= from_date) & (self.data.expeditions_df['date_expedition'] <= to_date)
        filtered_df = self.data.expeditions_df[mask]
        
        if filtered_df.empty:
            layout.addWidget(QLabel("Aucune donnée disponible pour cette période"))
            return widget
        
        # Calculate costs by carrier
        costs_by_carrier = filtered_df.groupby('id_transporteur')['cout_estime'].sum().reset_index()
        costs_by_carrier['nom'] = costs_by_carrier['id_transporteur'].apply(
            lambda x: self.data.transporteurs_df[self.data.transporteurs_df['id'] == x]['nom'].values[0])
        
        # Metrics
        metrics_layout = QHBoxLayout()
        
        total_cost = filtered_df['cout_estime'].sum()
        avg_cost = filtered_df['cout_estime'].mean()
        shipments = len(filtered_df)
        
        metrics_layout.addWidget(MetricCard("Coût total", f"${total_cost:,.0f}", "Transport"))
        metrics_layout.addWidget(MetricCard("Coût moyen", f"${avg_cost:,.0f}", "Par commande"))
        metrics_layout.addWidget(MetricCard("Commandes", f"{shipments:,}", "Expédiées"))
        
        layout.addLayout(metrics_layout)
        
        # Cost by carrier chart
        cost_chart = ChartWidget(title='Coûts par transporteur', y_label='Coût ($)', x_label='Transporteur')
        
        x_vals = np.arange(len(costs_by_carrier))
        y_vals = costs_by_carrier['cout_estime'].values
        
        colors = [QColor('#2196F3'), QColor('#4CAF50'), QColor('#FF9800'), QColor('#9C27B0')]
        brushes = [colors[i % len(colors)] for i in range(len(x_vals))]
        
        bargraph = pg.BarGraphItem(x=x_vals, height=y_vals, width=0.6, brushes=brushes)
        cost_chart.addItem(bargraph)
        
        ticks = [(i, label) for i, label in enumerate(costs_by_carrier['nom'])]
        cost_chart.getAxis('bottom').setTicks([ticks])
        
        for i, value in enumerate(y_vals):
            text_item = pg.TextItem(text=f"${value:,.0f}", anchor=(0.5, 0), color='k')
            text_item.setPos(x_vals[i], value + max(y_vals)*0.05)
            cost_chart.addItem(text_item)
        
        cost_chart.setMinimumHeight(300)
        layout.addWidget(cost_chart)
        
        return widget
    
    def create_transport_tab(self, from_date, to_date):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filter expeditions data
        mask = ((self.data.expeditions_df['date_expedition'] >= from_date) & 
        (self.data.expeditions_df['date_expedition'] <= to_date))
        filtered_df = self.data.expeditions_df[mask]
        
        if filtered_df.empty:
            layout.addWidget(QLabel("Aucune donnée disponible pour cette période"))
            return widget
        
        # Calculate shipments by carrier
        shipments_by_carrier = filtered_df.groupby('id_transporteur').size().reset_index(name='count')
        shipments_by_carrier['nom'] = shipments_by_carrier['id_transporteur'].apply(
            lambda x: self.data.transporteurs_df[self.data.transporteurs_df['id'] == x]['nom'].values[0])
        
        # Metrics
        metrics_layout = QHBoxLayout()
        
        total_shipments = len(filtered_df)
        carriers_used = len(shipments_by_carrier)
        avg_per_carrier = total_shipments / carriers_used if carriers_used > 0 else 0
        
        metrics_layout.addWidget(MetricCard("Commandes", f"{total_shipments:,}", "Expédiées"))
        metrics_layout.addWidget(MetricCard("Transporteurs", f"{carriers_used}", "Utilisés"))
        metrics_layout.addWidget(MetricCard("Moyenne", f"{avg_per_carrier:.1f}", "Par transporteur"))
        
        layout.addLayout(metrics_layout)
        
        # Shipments by carrier chart
        ship_chart = ChartWidget(title='Commandes par transporteur', y_label='Nombre', x_label='Transporteur')
        
        x_vals = np.arange(len(shipments_by_carrier))
        y_vals = shipments_by_carrier['count'].values
        
        colors = [QColor('#2196F3'), QColor('#4CAF50'), QColor('#FF9800'), QColor('#9C27B0')]
        brushes = [colors[i % len(colors)] for i in range(len(x_vals))]
        
        bargraph = pg.BarGraphItem(x=x_vals, height=y_vals, width=0.6, brushes=brushes)
        ship_chart.addItem(bargraph)
        
        ticks = [(i, label) for i, label in enumerate(shipments_by_carrier['nom'])]
        ship_chart.getAxis('bottom').setTicks([ticks])
        
        for i, value in enumerate(y_vals):
            text_item = pg.TextItem(text=f"{int(value)}", anchor=(0.5, 0), color='k')
            text_item.setPos(x_vals[i], value + max(y_vals)*0.05)
            ship_chart.addItem(text_item)
        
        ship_chart.setMinimumHeight(300)
        layout.addWidget(ship_chart)
        
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
        
        # Calculate metrics
        cmd_en_prep = len(self.data.expeditions_df[self.data.expeditions_df['statut'] == 'En préparation'])
        cmd_pretes = len(self.data.expeditions_df[self.data.expeditions_df['statut'] == 'Prête à expédier'])
        delai_moyen = self.data.performance_df['delais_moyens'].mean()
        
        metrics_layout.addWidget(self.create_metric_item("En préparation", f"{cmd_en_prep}"))
        metrics_layout.addWidget(self.create_metric_item("Prêtes à expédier", f"{cmd_pretes}"))
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
        self.timer = QTimer(self)
        self.timer.setInterval(60000)  # 1 minute
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start()
    
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