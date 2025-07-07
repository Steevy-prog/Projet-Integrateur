import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QTabWidget, QTableWidget,
    QTableWidgetItem, QLineEdit, QComboBox, QTextEdit, QGroupBox,
    QFrame, QScrollArea, QProgressBar, QSplitter, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QDialog, QFormLayout, QSpinBox,
    QDateEdit, QTimeEdit, QCheckBox, QRadioButton, QButtonGroup,
    QMessageBox, QFileDialog, QStatusBar, QMenuBar, QMenu, QToolBar,
    QListWidget, QListWidgetItem, QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize, QRect
from PyQt6.QtGui import (
    QPixmap, QIcon, QFont, QColor, QPalette, QAction, QPainter,
    QBrush, QPen, QLinearGradient
)


class MetricCard(QFrame):
    """Carte de métrique stylisée pour le tableau de bord"""

    def __init__(self, title, value, color="#3498db", icon_text="📊"):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setFixedSize(200, 120)

        # Gradient background
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {color}, stop: 1 {self.darken_color(color)});
                border-radius: 10px;
                border: none;
            }}
            QLabel {{
                color: white;
                background: transparent;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        # Icon and title
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon_text)
        icon_label.setFont(QFont("Arial", 24))
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")

        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        header_layout.addWidget(title_label)

        # Value
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(header_layout)
        layout.addWidget(value_label)
        layout.addStretch()

        self.setLayout(layout)

    def darken_color(self, color):
        """Assombrit une couleur hexadécimale"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.8)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"


class TaskCard(QFrame):
    """Carte de tâche pour l'affichage des tâches récentes"""

    def __init__(self, task_id, task_type, status, priority, time):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setFixedHeight(80)

        # Couleur selon la priorité
        colors = {
            "High": "#e74c3c",
            "Medium": "#f39c12",
            "Low": "#27ae60"
        }

        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #ddd;
                border-left: 4px solid {colors.get(priority, '#3498db')};
                border-radius: 5px;
                margin: 2px;
            }}
            QFrame:hover {{
                background-color: #f8f9fa;
            }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)

        # Informations principales
        main_layout = QVBoxLayout()

        # En-tête
        header_layout = QHBoxLayout()
        id_label = QLabel(task_id)
        id_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        type_label = QLabel(task_type)
        type_label.setFont(QFont("Arial", 10))
        type_label.setStyleSheet("color: #666;")

        header_layout.addWidget(id_label)
        header_layout.addWidget(type_label)
        header_layout.addStretch()

        # Statut et heure
        footer_layout = QHBoxLayout()
        status_label = QLabel(status)
        status_label.setFont(QFont("Arial", 9))
        status_label.setStyleSheet("color: #666;")
        time_label = QLabel(time)
        time_label.setFont(QFont("Arial", 9))
        time_label.setStyleSheet("color: #999;")

        footer_layout.addWidget(status_label)
        footer_layout.addStretch()
        footer_layout.addWidget(time_label)

        main_layout.addLayout(header_layout)
        main_layout.addLayout(footer_layout)

        # Bouton de priorité
        priority_btn = QPushButton(priority)
        priority_btn.setFixedSize(60, 25)
        priority_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get(priority, '#3498db')};
                color: white;
                border: none;
                border-radius: 13px;
                font-size: 8px;
                font-weight: bold;
            }}
        """)

        layout.addLayout(main_layout)
        layout.addWidget(priority_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)


class DashboardWidget(QWidget):
    """Widget du tableau de bord principal"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Titre
        title = QLabel("Tableau de Bord")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)

        # Métriques principales
        metrics_layout = QHBoxLayout()

        metrics_data = [
            ("Réceptions", 12, "#3498db", "📦"),
            ("Expéditions", 8, "#27ae60", "🚚"),
            ("Mouvements", 156, "#9b59b6", "🔄"),
            ("Alertes", 3, "#e74c3c", "⚠️"),
            ("Occupation", "78%", "#16a085", "📊")
        ]

        for title, value, color, icon in metrics_data:
            card = MetricCard(title, value, color, icon)
            metrics_layout.addWidget(card)

        metrics_layout.addStretch()
        layout.addLayout(metrics_layout)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #bdc3c7;")
        layout.addWidget(separator)

        # Contenu principal
        content_layout = QHBoxLayout()

        # Tâches récentes
        tasks_group = QGroupBox("Tâches Récentes")
        tasks_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        tasks_layout = QVBoxLayout()

        tasks_data = [
            ("RC001", "Réception", "En cours", "High", "10:30"),
            ("EX002", "Expédition", "En attente", "Medium", "11:00"),
            ("RC003", "Réception", "Terminé", "Low", "09:15")
        ]

        for task_id, task_type, status, priority, time in tasks_data:
            task_card = TaskCard(task_id, task_type, status, priority, time)
            tasks_layout.addWidget(task_card)

        tasks_layout.addStretch()
        tasks_group.setLayout(tasks_layout)

        # Actions rapides
        actions_group = QGroupBox("Actions Rapides")
        actions_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        actions_layout = QGridLayout()

        actions = [
            ("Scanner Colis", "🔍", "#3498db"),
            ("Nouvelle Réception", "➕", "#27ae60"),
            ("Localiser Produit", "📍", "#9b59b6"),
            ("Générer Rapport", "📄", "#e67e22")
        ]

        for i, (text, icon, color) in enumerate(actions):
            btn = QPushButton(f"{icon} {text}")
            btn.setFixedHeight(50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            actions_layout.addWidget(btn, i // 2, i % 2)

        actions_group.setLayout(actions_layout)

        content_layout.addWidget(tasks_group, 2)
        content_layout.addWidget(actions_group, 1)

        layout.addLayout(content_layout)
        layout.addStretch()

        self.setLayout(layout)

    def darken_color(self, color):
        """Assombrit une couleur hexadécimale"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.8)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"


class ReceptionWidget(QWidget):
    """Widget de gestion des réceptions"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # En-tête
        header_layout = QHBoxLayout()
        title = QLabel("Gestion des Réceptions")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")

        new_btn = QPushButton("➕ Nouvelle Réception")
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(new_btn)

        layout.addLayout(header_layout)

        # Contenu principal
        content_layout = QHBoxLayout()

        # Bons de réception en attente
        pending_group = QGroupBox("Bons de Réception en Attente")
        pending_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        pending_layout = QVBoxLayout()

        # Table des bons de réception
        self.reception_table = QTableWidget()
        self.reception_table.setColumnCount(5)
        self.reception_table.setHorizontalHeaderLabels([
            "Bon N°", "Fournisseur", "Articles", "Statut", "Action"
        ])

        # Données d'exemple
        reception_data = [
            ("BR-2024-001", "TechCorp SA", "15", "En attente"),
            ("BR-2024-002", "LogiPro SARL", "23", "En attente"),
            ("BR-2024-003", "SupplyChain Inc", "8", "En attente")
        ]

        self.reception_table.setRowCount(len(reception_data))

        for i, (bon, fournisseur, articles, statut) in enumerate(reception_data):
            self.reception_table.setItem(i, 0, QTableWidgetItem(bon))
            self.reception_table.setItem(i, 1, QTableWidgetItem(fournisseur))
            self.reception_table.setItem(i, 2, QTableWidgetItem(articles))
            self.reception_table.setItem(i, 3, QTableWidgetItem(statut))

            # Bouton d'action
            action_btn = QPushButton("Traiter")
            action_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            self.reception_table.setCellWidget(i, 4, action_btn)

        self.reception_table.horizontalHeader().setStretchLastSection(True)
        self.reception_table.setAlternatingRowColors(True)

        pending_layout.addWidget(self.reception_table)
        pending_group.setLayout(pending_layout)

        # Processus de réception
        process_group = QGroupBox("Processus de Réception")
        process_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        process_layout = QVBoxLayout()

        process_steps = [
            ("1", "Arrivée du Chargement", "Scanner le colis et vérifier les documents", True),
            ("2", "Vérification", "Contrôler les quantités et l'état", False),
            ("3", "Stockage", "Attribution des emplacements optimaux", False)
        ]

        for step, title, description, active in process_steps:
            step_frame = QFrame()
            step_frame.setFrameStyle(QFrame.Shape.Box)
            step_frame.setLineWidth(1)

            if active:
                step_frame.setStyleSheet("""
                    QFrame {
                        background-color: #e3f2fd;
                        border: 2px solid #006775;
                        border-radius: 8px;
                        padding: 10px;
                    }
                """)
            else:
                step_frame.setStyleSheet("""
                    QFrame {
                        background-color: #f5f5f5;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 10px;
                    }
                """)

            step_layout = QHBoxLayout()

            # Numéro d'étape
            step_label = QLabel(step)
            step_label.setFixedSize(30, 30)
            step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            step_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {'#006775' if active else '#bbb'};
                    color: white;
                    border-radius: 15px;
                    font-weight: bold;
                }}
            """)

            # Texte
            text_layout = QVBoxLayout()
            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            desc_label = QLabel(description)
            desc_label.setFont(QFont("Arial", 9))
            desc_label.setStyleSheet("color: #666;")

            text_layout.addWidget(title_label)
            text_layout.addWidget(desc_label)

            step_layout.addWidget(step_label)
            step_layout.addLayout(text_layout)

            step_frame.setLayout(step_layout)
            process_layout.addWidget(step_frame)

        process_layout.addStretch()
        process_group.setLayout(process_layout)

        content_layout.addWidget(pending_group, 2)
        content_layout.addWidget(process_group, 1)

        layout.addLayout(content_layout)

        self.setLayout(layout)


class InventoryWidget(QWidget):
    """Widget de gestion des stocks"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # En-tête
        header_layout = QHBoxLayout()
        title = QLabel("Gestion des Stocks")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")

        # Barre de recherche
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Rechercher un produit ou emplacement...")
        search_input.setFixedHeight(35)
        search_btn = QPushButton("🔍")
        search_btn.setFixedSize(35, 35)

        search_layout.addWidget(search_input)
        search_layout.addWidget(search_btn)

        # Boutons d'action
        filter_btn = QPushButton("📊 Filtrer")
        export_btn = QPushButton("📤 Exporter")

        for btn in [filter_btn, export_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addLayout(search_layout)
        header_layout.addWidget(filter_btn)
        header_layout.addWidget(export_btn)

        layout.addLayout(header_layout)

        # Emplacements de stockage
        storage_group = QGroupBox("Emplacements de Stockage")
        storage_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        storage_layout = QGridLayout()

        # Données d'exemple des emplacements
        locations_data = [
            ("E0-A1", "E0", 85, 12, "#e74c3c"),
            ("E0-A2", "E0", 62, 8, "#f39c12"),
            ("E0-A3", "E0", 45, 6, "#27ae60"),
            ("E1-B1", "E1", 78, 15, "#f39c12"),
            ("E1-B2", "E1", 92, 18, "#e74c3c"),
            ("E1-B3", "E1", 33, 4, "#27ae60"),
            ("E2-C1", "E2", 67, 11, "#f39c12"),
            ("E2-C2", "E2", 89, 16, "#e74c3c"),
            ("E2-C3", "E2", 54, 9, "#27ae60")
        ]

        for i, (location_id, zone, capacity, products, color) in enumerate(locations_data):
            location_frame = QFrame()
            location_frame.setFrameStyle(QFrame.Shape.Box)
            location_frame.setLineWidth(1)
            location_frame.setFixedSize(200, 150)
            location_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                }
                QFrame:hover {
                    background-color: #f8f9fa;
                }
            """)

            location_layout = QVBoxLayout()

            # En-tête
            header_loc_layout = QHBoxLayout()
            id_label = QLabel(location_id)
            id_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            zone_label = QLabel(f"Zone {zone}")
            zone_label.setFont(QFont("Arial", 9))
            zone_label.setStyleSheet("color: #666;")

            # Badge de capacité
            capacity_badge = QLabel(f"{capacity}%")
            capacity_badge.setFixedSize(50, 20)
            capacity_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            capacity_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: white;
                    border-radius: 10px;
                    font-size: 8px;
                    font-weight: bold;
                }}
            """)

            header_loc_layout.addWidget(id_label)
            header_loc_layout.addWidget(zone_label)
            header_loc_layout.addStretch()
            header_loc_layout.addWidget(capacity_badge)

            # Barre de progression
            progress_layout = QVBoxLayout()
            progress_label = QLabel("Occupation")
            progress_label.setFont(QFont("Arial", 8))
            progress_label.setStyleSheet("color: #666;")

            progress_bar = QProgressBar()
            progress_bar.setValue(capacity)
            progress_bar.setFixedHeight(10)
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 5px;
                }}
            """)

            progress_layout.addWidget(progress_label)
            progress_layout.addWidget(progress_bar)

            # Pied de page
            footer_layout = QHBoxLayout()
            products_label = QLabel(f"{products} produits")
            products_label.setFont(QFont("Arial", 9))
            products_label.setStyleSheet("color: #666;")

            view_btn = QPushButton("👁️")
            view_btn.setFixedSize(25, 25)
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 13px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)

            footer_layout.addWidget(products_label)
            footer_layout.addStretch()
            footer_layout.addWidget(view_btn)

            location_layout.addLayout(header_loc_layout)
            location_layout.addLayout(progress_layout)
            location_layout.addStretch()
            location_layout.addLayout(footer_layout)

            location_frame.setLayout(location_layout)
            storage_layout.addWidget(location_frame, i // 3, i % 3)

        storage_group.setLayout(storage_layout)

        # Scroll area pour les emplacements
        scroll_area = QScrollArea()
        scroll_area.setWidget(storage_group)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)

        self.setLayout(layout)


class SGEMainWindow(QMainWindow):
    """Fenêtre principale de l'application SGE"""

    def __init__(self):
        super().__init__()
        self.current_user = {
            "name": "Marie Dubois",
            "role": "Magasinier",
            "id": "MAG001"
        }
        self.notifications = 3
        self.init_ui()
        self.init_timer()

    def init_ui(self):
        self.setWindowTitle("SGE - Système de Gestion d'Entrepôts")
        self.setGeometry(100, 100, 1400, 900)

        # Style global
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #5dade2;
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout()

        # En-tête
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)

        # Onglets principaux
        self.tab_widget = QTabWidget()

        # Onglet Tableau de bord
        dashboard_tab = DashboardWidget()
        self.tab_widget.addTab(dashboard_tab, "🏠 Tableau de Bord")

        # Onglet Réceptions
        reception_tab = ReceptionWidget()
        self.tab_widget.addTab(reception_tab, "🚚 Réceptions")

        # Onglet Expéditions
        expedition_tab = QWidget()
        expedition_layout = QVBoxLayout()
        expedition_layout.addWidget(QLabel("Module Expéditions - En développement"))
        expedition_tab.setLayout(expedition_layout)
        self.tab_widget.addTab(expedition_tab, "📦 Expéditions")

        # Onglet Stocks
        inventory_tab = InventoryWidget()
        self.tab_widget.addTab(inventory_tab, "📊 Stocks")

        # Onglet Rapports
        reports_tab = QWidget()
        reports_layout = QVBoxLayout()
        reports_layout.addWidget(QLabel("Module Rapports - En développement"))
        reports_tab.setLayout(reports_layout)
        self.tab_widget.addTab(reports_tab, "📈 Rapports")

        main_layout.addWidget(self.tab_widget)

        central_widget.setLayout(main_layout)

        # Barre de statut
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Système prêt")

        # Menu
        self.create_menu_bar()

    def create_header(self):
        """Créer l'en-tête de l'application"""
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 2px solid #e9ecef;
            }
        """)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 10, 20, 10)

        # Logo et titre
        logo_layout = QHBoxLayout()
        logo_label = QLabel("📦")
        logo_label.setFont(QFont("Arial", 24))

        title_label = QLabel("SGE - Système de Gestion d'Entrepôts")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50;")

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(title_label)
        logo_layout.addStretch()

        # Informations utilisateur
        user_layout = QHBoxLayout()

        # Heure
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 10))
        self.time_label.setStyleSheet("color: #666;")

        # Notifications
        notif_btn = QPushButton(f"🔔 {self.notifications}")
        notif_btn.setFixedSize(50, 30)
        notif_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        notif_btn.clicked.connect(self.show_notifications)

        user_name_label = QLabel(self.current_user["name"])
        user_name_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        user_name_label.setStyleSheet("color: #333;")

        user_role_label = QLabel(self.current_user["role"])
        user_role_label.setFont(QFont("Arial", 9))
        user_role_label.setStyleSheet("color: #777;")

        user_info_layout = QVBoxLayout()
        user_info_layout.addWidget(user_name_label)
        user_info_layout.addWidget(user_role_label)

        user_layout.addWidget(self.time_label)
        user_layout.addSpacing(15)
        user_layout.addWidget(notif_btn)
        user_layout.addSpacing(10)
        user_layout.addLayout(user_info_layout)

        header_layout.addLayout(logo_layout)
        header_layout.addLayout(user_layout)

        header_widget.setLayout(header_layout)
        return header_widget

    def create_menu_bar(self):
        """Créer la barre de menu de l'application"""
        menu_bar = self.menuBar()

        # Menu Fichier
        file_menu = menu_bar.addMenu("Fichier")
        exit_action = QAction("Quitter", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Outils
        tools_menu = menu_bar.addMenu("Outils")
        settings_action = QAction("Paramètres", self)
        tools_menu.addAction(settings_action)

        # Menu Aide
        help_menu = menu_bar.addMenu("Aide")
        about_action = QAction("À propos", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def init_timer(self):
        """Initialise le minuteur pour l'affichage de l'heure"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Met à jour chaque seconde
        self.update_time() # Met à jour immédiatement au démarrage

    def update_time(self):
        """Met à jour l'affichage de l'heure actuelle"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)

    def show_notifications(self):
        """Affiche un message de notification"""
        QMessageBox.information(self, "Notifications",
                                f"Vous avez {self.notifications} nouvelles notifications.")

    def show_about_dialog(self):
        """Affiche la boîte de dialogue 'À propos'"""
        QMessageBox.about(self, "À propos de SGE",
                          "SGE - Système de Gestion d'Entrepôts\n"
                          "Version 1.0\n"
                          "Développé par [Votre Nom/Organisation]\n"
                          "© 2024 Tous droits réservés.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SGEMainWindow()
    window.showMaximized() # Ou window.show() pour une taille par défaut
    sys.exit(app.exec())