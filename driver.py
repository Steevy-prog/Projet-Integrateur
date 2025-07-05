import sys, json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QLabel, QMessageBox, QHeaderView, QFrame, QLineEdit,
    QScrollArea, QSplitter, QStackedWidget, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QPen
from PyQt6.QtWebEngineWidgets import QWebEngineView

class AnimatedButton(QPushButton):
    """Custom animated button with hover effects"""
    def __init__(self, text, icon="", parent=None):
        super().__init__(text, parent)
        self.icon_text = icon
        self.is_active = False
        self.setMinimumHeight(50)
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
    def set_active(self, active):
        self.is_active = active
        self.update_style()
        
    def update_style(self):
        if self.is_active:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                 stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-weight: 600;
                    text-align: left;
                    margin: 2px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                 stop:0 #5a67d8, stop:1 #6b46c1);
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.1);
                    color: #4a5568;
                    border: 1px solid rgba(0, 0, 0, 0.1);
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-weight: 500;
                    text-align: left;
                    margin: 2px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(0, 0, 0, 0.2);
                    color: #2d3748;
                }
            """)

class StatsCard(QFrame):
    """Custom stats card widget"""
    def __init__(self, title, value, icon, color):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)
        self.setMinimumHeight(120)
        self.setMaximumHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Icon and title
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 24))
        icon_label.setStyleSheet(f"color: {color};")
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        title_label.setStyleSheet("color: #718096;")
        
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {color};")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addStretch()
        
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 15px;
            }}
            QFrame:hover {{
                border: 1px solid {color};
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}
        """)
    
    def update_value(self, value):
        self.value_label.setText(str(value))

class SideBar(QFrame):
    """Custom sidebar with navigation"""
    navigation_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setFixedWidth(280)
        self.setFrameStyle(QFrame.Shape.Box)
        self.current_index = 0
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Logo/Header
        header = QLabel("🚚 DeliveryPro")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #2d3748; padding: 10px 0;")
        layout.addWidget(header)
        
        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("📋 Tableau de bord", "📋"),
            ("🕒 Livraisons en cours", "🕒"),
            ("✅ Livraisons terminées", "✅"),
            ("🗺️ Carte interactive", "🗺️"),
            ("📊 Statistiques", "📊"),
            ("⚙️ Paramètres", "⚙️")
        ]
        
        for i, (text, icon) in enumerate(nav_items):
            btn = AnimatedButton(text, icon)
            btn.clicked.connect(lambda checked, idx=i: self.set_active_nav(idx))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # User info
        user_frame = QFrame()
        user_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        user_layout = QVBoxLayout(user_frame)
        user_name = QLabel("👤 My Self")
        user_name.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        user_role = QLabel("Chauffeur-livreur")
        user_role.setFont(QFont("Segoe UI", 10))
        user_role.setStyleSheet("color: #718096;")
        user_layout.addWidget(user_name)
        user_layout.addWidget(user_role)
        
        layout.addWidget(user_frame)
        
        # Set initial active button
        self.set_active_nav(0)
        
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                 stop:0 #f7fafc, stop:1 #edf2f7);
                border-right: 1px solid #e2e8f0;
            }
        """)
    
    def set_active_nav(self, index):
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)
        
        self.current_index = index
        self.navigation_changed.emit(index)

class DriverApp(QWidget):
    def __init__(self, driver_info):
        super().__init__()
        self.driver_info = driver_info
        self.setWindowTitle(f"DeliveryPro - {driver_info['prenom']} {driver_info['nom']}")
        self.setGeometry(100, 100, 1400, 900)

        self.pending_deliveries_data = []
        self.completed_deliveries_data = []
        self.load_simulated_data()
        self.init_ui()
        self.apply_modern_styles()
        self.load_all_deliveries()

    def load_simulated_data(self):
        self.pending_deliveries_data = [
            {
                "id_livraison": 101, "id_colis": "PKG001",
                "nom_destinataire": "Alice Dubois",
                "adresse": "10 Rue Principale, Yaoundé",
                "date_expedition": QDate(2025, 7, 1),
                "date_prevue": QDate(2025, 7, 5),
                "poids": "2 kg", "volume": "0.01 m³", "type": "Document",
                "instructions": "Fragile, éviter l'humidité",
                "lat": 3.8619, "lon": 11.5217
            },
            {
                "id_livraison": 102, "id_colis": "PKG002",
                "nom_destinataire": "Bob Martin",
                "adresse": "25 Avenue de la Liberté, Douala",
                "date_expedition": QDate(2025, 7, 2),
                "date_prevue": QDate(2025, 7, 6),
                "poids": "10 kg", "volume": "0.05 m³", "type": "Électronique",
                "instructions": "Ne pas exposer au soleil",
                "lat": 4.0415, "lon": 9.7028
            },
            {
                "id_livraison": 103, "id_colis": "PKG003",
                "nom_destinataire": "Claire Nguyen",
                "adresse": "15 Boulevard du 20 Mai, Bafoussam",
                "date_expedition": QDate(2025, 7, 3),
                "date_prevue": QDate(2025, 7, 7),
                "poids": "5 kg", "volume": "0.02 m³", "type": "Vêtements",
                "instructions": "Livrer entre 9h et 17h",
                "lat": 5.4737, "lon": 10.4176
            }
        ]
        self.completed_deliveries_data = [
            {
                "id_livraison": 100, "id_colis": "PKG000",
                "nom_destinataire": "David Kamga",
                "adresse": "8 Rue de la Paix, Douala",
                "date_expedition": QDate(2025, 6, 30),
                "date_prevue": QDate(2025, 7, 4),
                "date_livree": QDate(2025, 7, 4),
                "poids": "3 kg", "volume": "0.015 m³", "type": "Livre",
                "instructions": "Appeler avant livraison",
                "lat": 4.0463, "lon": 9.7075
            }
        ]

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        self.sidebar = SideBar()
        self.sidebar.navigation_changed.connect(self.change_view)
        
        # Main content area
        self.content_stack = QStackedWidget()
        
        # Create different views
        self.create_dashboard_view()
        self.create_pending_view()
        self.create_completed_view()
        self.create_map_view()
        self.create_stats_view()
        self.create_settings_view()
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack, 1)

    def create_dashboard_view(self):
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Welcome header
        welcome_label = QLabel(f"Bonjour {self.driver_info['prenom']} ! 👋")
        welcome_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: #2d3748; margin-bottom: 10px;")
        
        subtitle = QLabel("Voici un aperçu de vos livraisons aujourd'hui")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: #718096; margin-bottom: 20px;")
        
        layout.addWidget(welcome_label)
        layout.addWidget(subtitle)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_card = StatsCard("Total", 0, "📦", "#3182ce")
        self.pending_card = StatsCard("En cours", 0, "🕒", "#e53e3e")
        self.completed_card = StatsCard("Terminées", 0, "✅", "#38a169")
        
        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.pending_card)
        stats_layout.addWidget(self.completed_card)
        
        layout.addLayout(stats_layout)
        
        # Quick actions
        actions_frame = QFrame()
        actions_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        actions_layout = QVBoxLayout(actions_frame)
        
        actions_title = QLabel("🚀 Actions rapides")
        actions_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        actions_title.setStyleSheet("color: #2d3748; margin-bottom: 15px;")
        
        actions_buttons_layout = QHBoxLayout()
        
        view_pending_btn = QPushButton("📋 Voir les livraisons en cours")
        view_map_btn = QPushButton("🗺️ Ouvrir la carte")
        add_delivery_btn = QPushButton("➕ Ajouter une livraison")
        
        for btn in [view_pending_btn, view_map_btn, add_delivery_btn]:
            btn.setMinimumHeight(45)
            btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                 stop:0 #4f46e5, stop:1 #7c3aed);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                 stop:0 #4338ca, stop:1 #6d28d9);
                }
            """)
            actions_buttons_layout.addWidget(btn)
        
        view_pending_btn.clicked.connect(lambda: self.sidebar.set_active_nav(1))
        view_map_btn.clicked.connect(lambda: self.sidebar.set_active_nav(3))
        
        actions_layout.addWidget(actions_title)
        actions_layout.addLayout(actions_buttons_layout)
        
        layout.addWidget(actions_frame)
        layout.addStretch()
        
        self.content_stack.addWidget(dashboard)

    def create_pending_view(self):
        pending_widget = QWidget()
        layout = QVBoxLayout(pending_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("🕒 Livraisons en cours")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2d3748;")
        
        # Search bar
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 25px;
                padding: 5px;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(15, 5, 15, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher une livraison...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 14px;
                padding: 5px;
            }
        """)
        
        search_btn = QPushButton("Rechercher")
        search_btn.setStyleSheet("""
            QPushButton {
                background: #4f46e5;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #4338ca;
            }
        """)
        search_btn.clicked.connect(self.search_deliveries)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(search_frame)
        
        layout.addLayout(header_layout)
        
        # Table
        self.pending_table = QTableWidget()
        self.setup_modern_table(self.pending_table, "pending")
        layout.addWidget(self.pending_table)
        
        self.content_stack.addWidget(pending_widget)

    def create_completed_view(self):
        completed_widget = QWidget()
        layout = QVBoxLayout(completed_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("✅ Livraisons terminées")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2d3748;")
        layout.addWidget(title)
        
        self.done_table = QTableWidget()
        self.setup_modern_table(self.done_table, "done")
        layout.addWidget(self.done_table)
        
        self.content_stack.addWidget(completed_widget)

    def create_map_view(self):
        map_widget = QWidget()
        layout = QVBoxLayout(map_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("🗺️ Carte interactive")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2d3748;")
        layout.addWidget(title)
        
        self.map_view = QWebEngineView()
        self.map_view.setStyleSheet("""
            QWebEngineView {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        layout.addWidget(self.map_view)
        
        self.content_stack.addWidget(map_widget)

    def create_stats_view(self):
        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("📊 Statistiques détaillées")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2d3748;")
        layout.addWidget(title)
        
        # Placeholder for detailed stats
        placeholder = QLabel("📈 Statistiques détaillées à venir...")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setFont(QFont("Segoe UI", 16))
        placeholder.setStyleSheet("color: #718096; padding: 50px;")
        layout.addWidget(placeholder)
        
        self.content_stack.addWidget(stats_widget)

    def create_settings_view(self):
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("⚙️ Paramètres")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2d3748;")
        layout.addWidget(title)
        
        # Placeholder for settings
        placeholder = QLabel("🔧 Paramètres à venir...")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setFont(QFont("Segoe UI", 16))
        placeholder.setStyleSheet("color: #718096; padding: 50px;")
        layout.addWidget(placeholder)
        
        self.content_stack.addWidget(settings_widget)

    def setup_modern_table(self, table, table_type):
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setShowGrid(False)
        table.setMinimumHeight(400)
        
        if table_type == "pending":
            headers = ["ID", "Colis", "Destinataire", "Adresse", "Date prévue", "Action"]
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
        else:
            headers = ["ID", "Colis", "Destinataire", "Adresse", "Date livrée"]
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                gridline-color: #f7fafc;
            }
            QTableWidget::item {
                padding: 12px;
                border: none;
            }
            QTableWidget::item:selected {
                background: #ebf8ff;
                color: #2b6cb0;
            }
            QTableWidget::item:alternate {
                background: #f7fafc;
            }
            QHeaderView::section {
                background: #4f46e5;
                color: white;
                padding: 12px;
                border: none;
                font-weight: 600;
            }
            QHeaderView::section:first {
                border-top-left-radius: 12px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 12px;
            }
        """)

    def change_view(self, index):
        self.content_stack.setCurrentIndex(index)
        if index == 3:  # Map view
            self.update_map()

    def load_all_deliveries(self):
        self.load_pending()
        self.load_done()
        self.update_counters()

    def load_pending(self):
        t = self.pending_table
        t.setRowCount(0)
        for i, d in enumerate(self.pending_deliveries_data):
            t.insertRow(i)
            t.setItem(i, 0, QTableWidgetItem(str(d["id_livraison"])))
            t.setItem(i, 1, QTableWidgetItem(d["id_colis"]))
            t.setItem(i, 2, QTableWidgetItem(d["nom_destinataire"]))
            t.setItem(i, 3, QTableWidgetItem(d["adresse"]))
            t.setItem(i, 4, QTableWidgetItem(d["date_prevue"].toString()))
            
            btn = QPushButton("📋 Détails")
            btn.setStyleSheet("""
                QPushButton {
                    background: #4f46e5;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #4338ca;
                }
            """)
            btn.clicked.connect(lambda _, di=d: self.show_delivery_popup(di))
            t.setCellWidget(i, 5, btn)

    def load_done(self):
        t = self.done_table
        t.setRowCount(0)
        for i, d in enumerate(self.completed_deliveries_data):
            t.insertRow(i)
            t.setItem(i, 0, QTableWidgetItem(str(d["id_livraison"])))
            t.setItem(i, 1, QTableWidgetItem(d["id_colis"]))
            t.setItem(i, 2, QTableWidgetItem(d["nom_destinataire"]))
            t.setItem(i, 3, QTableWidgetItem(d["adresse"]))
            t.setItem(i, 4, QTableWidgetItem(d["date_livree"].toString()))

    def show_delivery_popup(self, delivery):
        msg = QMessageBox()
        msg.setWindowTitle(f"📦 Détails - Livraison {delivery['id_livraison']}")
        msg.setStyleSheet("""
            QMessageBox {
                background: white;
                border-radius: 12px;
            }
            QMessageBox QLabel {
                color: #2d3748;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background: #4f46e5;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
                min-width: 120px;
            }
            QMessageBox QPushButton:hover {
                background: #4338ca;
            }
        """)
        
        info = f"""
        <div style='font-family: Segoe UI; line-height: 1.6;'>
            <h3 style='color: #2d3748; margin-top: 0;'>📦 {delivery['id_colis']}</h3>
            <p><strong>👤 Destinataire:</strong> {delivery['nom_destinataire']}</p>
            <p><strong>📍 Adresse:</strong> {delivery['adresse']}</p>
            <p><strong>⚖️ Poids:</strong> {delivery['poids']}</p>
            <p><strong>📏 Volume:</strong> {delivery['volume']}</p>
            <p><strong>📦 Type:</strong> {delivery['type']}</p>
            <p><strong>📝 Instructions:</strong> {delivery['instructions']}</p>
        </div>
        """
        
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(info)
        msg.addButton("✅ Marquer comme livrée", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("⚠️ Signaler un problème", QMessageBox.ButtonRole.DestructiveRole)
        msg.addButton("❌ Fermer", QMessageBox.ButtonRole.RejectRole)
        
        ret = msg.exec()
        if ret == 0:
            self.complete_delivery(delivery)
        elif ret == 1:
            QMessageBox.information(self, "⚠️ Problème signalé", "Le problème a été signalé au service client.")

    def complete_delivery(self, delivery):
        delivery["date_livree"] = QDate.currentDate()
        self.pending_deliveries_data.remove(delivery)
        self.completed_deliveries_data.append(delivery)
        
        success_msg = QMessageBox()
        success_msg.setIcon(QMessageBox.Icon.Information)
        success_msg.setWindowTitle("✅ Livraison terminée")
        success_msg.setText("🎉 Livraison marquée comme terminée avec succès !")
        success_msg.setStyleSheet("""
            QMessageBox {
                background: white;
                border-radius: 12px;
            }
            QMessageBox QPushButton {
                background: #38a169;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }
        """)
        success_msg.exec()
        
        self.load_all_deliveries()

    def update_counters(self):
        total = len(self.pending_deliveries_data) + len(self.completed_deliveries_data)
        pending = len(self.pending_deliveries_data)
        completed = len(self.completed_deliveries_data)
        
        # Update dashboard cards
        self.total_card.update_value(total)
        self.pending_card.update_value(pending)
        self.completed_card.update_value(completed)

    def search_deliveries(self):
        text = self.search_input.text().lower()
        for row in range(self.pending_table.rowCount()):
            match = any(text in (self.pending_table.item(row, col).text().lower() if self.pending_table.item(row, col) else "") for col in range(self.pending_table.columnCount() - 1)) # Exclude the button column
            self.pending_table.setRowHidden(row, not match)

    def update_map(self):
        # Generate a simple HTML map with OpenStreetMap and markers
        # For a production app, consider using a more robust mapping library or API
        
        # Center the map roughly in the middle of Cameroon (Yaounde)
        map_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OpenStreetMap</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <style>
                body {{ margin: 0; padding: 0; }}
                #mapid {{ height: 100%; width: 100%; }}
            </style>
        </head>
        <body>
            <div id="mapid"></div>
            <script>
                var mymap = L.map('mapid').setView([4.05, 9.77], 7); // Centered near Douala, Cameroon
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                    attribution: '© OpenStreetMap contributors'
                }}).addTo(mymap);
                
                var pendingDeliveries = {json.dumps([
                    {"lat": d["lat"], "lon": d["lon"], "id": d["id_livraison"], "recipient": d["nom_destinataire"]}
                    for d in self.pending_deliveries_data
                ])};
                
                var completedDeliveries = {json.dumps([
                    {"lat": d["lat"], "lon": d["lon"], "id": d["id_livraison"], "recipient": d["nom_destinataire"]}
                    for d in self.completed_deliveries_data
                ])};

                // Add markers for pending deliveries (red)
                pendingDeliveries.forEach(function(delivery) {{
                    L.marker([delivery.lat, delivery.lon], {{icon: L.divIcon({{className: 'custom-div-icon', html: "<div style='background-color:#e53e3e; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;'>🕒</div>", iconSize: [30,30]}})}}).addTo(mymap)
                        .bindPopup('<b>Livraison #' + delivery.id + '</b><br>Destinataire: ' + delivery.recipient + '<br>Statut: En cours');
                }});

                // Add markers for completed deliveries (green)
                completedDeliveries.forEach(function(delivery) {{
                    L.marker([delivery.lat, delivery.lon], {{icon: L.divIcon({{className: 'custom-div-icon', html: "<div style='background-color:#38a169; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;'>✅</div>", iconSize: [30,30]}})}}).addTo(mymap)
                        .bindPopup('<b>Livraison #' + delivery.id + '</b><br>Destinataire: ' + delivery.recipient + '<br>Statut: Terminée');
                }});
                
            </script>
        </body>
        </html>
        """
        self.map_view.setHtml(map_html)

    def apply_modern_styles(self):
        # Global styles for the main window/widget
        self.setStyleSheet("""
            QWidget {
                background: #f7fafc; /* Light gray background */
                font-family: 'Segoe UI', sans-serif;
                color: #2d3748;
            }
        """)

class LoginScreen(QWidget):
    login_successful = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DeliveryPro - Connexion")
        self.setGeometry(500, 300, 400, 350)
        self.init_ui()
        self.apply_login_styles()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        title = QLabel("🚚 DeliveryPro")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #4f46e5;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        self.username_input.setMinimumHeight(40)
        self.username_input.setFont(QFont("Segoe UI", 11))
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setFont(QFont("Segoe UI", 11))
        layout.addWidget(self.password_input)

        login_button = QPushButton("Se connecter")
        login_button.setMinimumHeight(45)
        login_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        login_button.clicked.connect(self.attempt_login)
        layout.addWidget(login_button)

        layout.addStretch()

    def apply_login_styles(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                 stop:0 #a7bfe8, stop:1 #6190e8);
                border-radius: 20px;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 10px 15px;
                color: #2d3748;
            }
            QLineEdit:focus {
                border: 2px solid #4f46e5;
            }
            QPushButton {
                background: #4f46e5;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                font-weight: 600;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: #4338ca;
            }
        """)

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Simulate a successful login with dummy data
        if username == "driver" and password == "password":
            driver_info = {
                "id_chauffeur": 1,
                "nom": "Doe",
                "prenom": "John",
                "email": "john.doe@example.com",
                "telephone": "+237677123456",
                "vehicule": "Toyota Hilux"
            }
            self.login_successful.emit(driver_info)
        else:
            QMessageBox.warning(self, "Erreur de connexion", "Nom d'utilisateur ou mot de passe incorrect.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_app = None
        self.show_login_screen()

    def show_login_screen(self):
        self.login_screen = LoginScreen()
        self.setCentralWidget(self.login_screen)
        self.login_screen.login_successful.connect(self.start_driver_app)
        self.resize(self.login_screen.size()) # Adjust main window size to login screen

    def start_driver_app(self, driver_info):
        self.current_app = DriverApp(driver_info)
        self.setCentralWidget(self.current_app)
        self.current_app.showMaximized() # Maximize the window for the main app

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # High-DPI scaling is often enabled by default in recent PyQt6 versions,
    # so these lines are usually not needed and can cause an AttributeError.
    # app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    # app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    # Set default font for better consistency
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())