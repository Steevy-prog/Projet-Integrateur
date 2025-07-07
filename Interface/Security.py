import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QFrame, QPushButton,
                             QTableWidget, QTableWidgetItem, QTextEdit, QScrollArea,
                             QSplitter, QTabWidget, QProgressBar, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QDateTime, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QLinearGradient
import login as login
class SecurityDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SGE - Interface Agent de Sécurité")
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply modern dark theme
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
            }
            QWidget {
                background: transparent;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame {
                border-radius: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255,255,255,0.1), stop:1 rgba(255,255,255,0.05));
                border: 1px solid rgba(255,255,255,0.2);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7c8eec, stop:1 #8a5fb5);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5a6fd8, stop:1 #6a4c93);
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QTableWidget {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 10px;
                gridline-color: rgba(255,255,255,0.1);
            }
            QTableWidget::item {
                border: none;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border: none;
                padding: 12px;
                font-weight: bold;
                color: white;
            }
            QTextEdit {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', monospace;
            }
            QTabWidget::pane {
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 10px;
                background: rgba(255,255,255,0.05);
            }
            QTabBar::tab {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                padding: 12px 24px;
                margin-right: 2px;
                border-radius: 8px 8px 0 0;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            QProgressBar {
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                text-align: center;
                background: rgba(255,255,255,0.1);
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #11998e, stop:1 #38ef7d);
                border-radius: 6px;
            }
        """)
        
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area with tabs
        content_tabs = QTabWidget()
        
        # Dashboard tab
        dashboard_tab = self.create_dashboard_tab()
        content_tabs.addTab(dashboard_tab, "🏠 Tableau de Bord")
        
        # Access Control tab
        access_tab = self.create_access_control_tab()
        content_tabs.addTab(access_tab, "🔐 Contrôle d'Accès")
        
        # Surveillance tab
        surveillance_tab = self.create_surveillance_tab()
        content_tabs.addTab(surveillance_tab, "📹 Surveillance")
        
        # Incidents tab
        incidents_tab = self.create_incidents_tab()
        content_tabs.addTab(incidents_tab, "⚠️ Incidents")

        logout_btn=QPushButton("logout")
        logout_btn.clicked.connect(self.logout)
        content_tabs.addTab(logout_btn,"logout")
        main_layout.addWidget(content_tabs)
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
        
    def create_header(self):
        header_frame = QFrame()
        header_frame.setMaximumHeight(120)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 20px;
                border: 2px solid rgba(255,255,255,0.3);
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        # Left side - Title and info
        left_layout = QVBoxLayout()
        
        title_label = QLabel("🛡️ CENTRE DE SÉCURITÉ SGE")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        left_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Surveillance et Contrôle d'Accès - Entrepôt SAC")
        subtitle_label.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.8);")
        left_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(left_layout)
        
        # Right side - Status and time
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_layout.addWidget(self.time_label)
        
        self.status_label = QLabel("🟢 SYSTÈME OPÉRATIONNEL")
        self.status_label.setStyleSheet("font-size: 14px; color: #38ef7d; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_layout.addWidget(self.status_label)
        
        header_layout.addLayout(right_layout)
        
        return header_frame
    
    def create_dashboard_tab(self):
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        
        # Status cards row
        cards_layout = QHBoxLayout()
        
        # Security Status Card
        security_card = self.create_status_card("🔒 État Sécurité", "SÉCURISÉ", "#38ef7d", "Tous les accès contrôlés")
        cards_layout.addWidget(security_card)
        
        # Active Personnel Card
        personnel_card = self.create_status_card("👥 Personnel Actif", "12", "#667eea", "Agents en service")
        cards_layout.addWidget(personnel_card)
        
        # Alerts Card
        alerts_card = self.create_status_card("⚠️ Alertes", "3", "#f093fb", "Notifications actives")
        cards_layout.addWidget(alerts_card)
        
        # Cameras Card
        cameras_card = self.create_status_card("📹 Caméras", "16/16", "#4facfe", "Toutes opérationnelles")
        cards_layout.addWidget(cameras_card)

        layout.addLayout(cards_layout)

        
        # Recent activity
        activity_frame = QFrame()
        activity_layout = QVBoxLayout(activity_frame)
        
        activity_title = QLabel("📊 Activité Récente")
        activity_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        activity_layout.addWidget(activity_title)
        
        self.activity_table = QTableWidget(10, 4)
        self.activity_table.setHorizontalHeaderLabels(["Heure", "Type", "Zone", "Détails"])
        self.populate_activity_table()
        activity_layout.addWidget(self.activity_table)
        
        layout.addWidget(activity_frame)
        
        return dashboard_widget
    
    
    def create_access_control_tab(self):
        access_widget = QWidget()
        layout = QHBoxLayout(access_widget)
        
        # Left panel - Access requests
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        
        access_title = QLabel("🔐 Demandes d'Accès")
        access_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        left_layout.addWidget(access_title)
        
        self.access_table = QTableWidget(8, 5)
        self.access_table.setHorizontalHeaderLabels(["ID", "Nom", "Zone", "Statut", "Action"])
        self.populate_access_table()
        left_layout.addWidget(self.access_table)
        
        # Access control buttons
        buttons_layout = QHBoxLayout()
        
        approve_btn = QPushButton("✅ Approuver")
        approve_btn.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #11998e, stop:1 #38ef7d);")
        approve_btn.clicked.connect(self.approve_access)
        buttons_layout.addWidget(approve_btn)
        
        deny_btn = QPushButton("❌ Refuser")
        deny_btn.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff416c, stop:1 #ff4b2b);")
        deny_btn.clicked.connect(self.deny_access)
        buttons_layout.addWidget(deny_btn)
        
        left_layout.addLayout(buttons_layout)
        layout.addWidget(left_frame, 2)
        
        # Right panel - Zone access map
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        
        map_title = QLabel("🗺️ Carte d'Accès")
        map_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(map_title)
        
        # Zone access grid
        zones_grid = QGridLayout()
        zone_colors = ["#38ef7d", "#f093fb", "#4facfe", "#667eea"]
        zone_names = ["E0 - Réception", "E1 - Stockage A", "E2 - Stockage B", "E3 - Expédition"]
        
        for i, (name, color) in enumerate(zip(zone_names, zone_colors)):
            zone_btn = QPushButton(name)
            zone_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    border: 2px solid rgba(255,255,255,0.3);
                    border-radius: 15px;
                    padding: 20px;
                    font-size: 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    transform: scale(1.05);
                    border: 2px solid rgba(255,255,255,0.5);
                }}
            """)
            zones_grid.addWidget(zone_btn, i // 2, i % 2)
        
        right_layout.addLayout(zones_grid)
        layout.addWidget(right_frame, 1)
        
        return access_widget
    
    def create_surveillance_tab(self):
        surveillance_widget = QWidget()
        layout = QVBoxLayout(surveillance_widget)
        
        # Camera grid
        camera_title = QLabel("📹 Surveillance en Temps Réel")
        camera_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(camera_title)
        
        cameras_grid = QGridLayout()
        camera_locations = [
            "Entrée Principale", "Zone Réception", "Zone E0", "Zone E1",
            "Zone E2", "Zone E3", "Zone Expédition", "Parking"
        ]
        
        for i, location in enumerate(camera_locations):
            camera_frame = QFrame()
            camera_frame.setMinimumHeight(180)
            camera_frame.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(0,0,0,0.8), stop:1 rgba(50,50,50,0.8));
                    border: 2px solid rgba(255,255,255,0.2);
                    border-radius: 10px;
                }
            """)
            
            camera_layout = QVBoxLayout(camera_frame)
            
            # Camera label
            cam_label = QLabel(f"📹 {location}")
            cam_label.setStyleSheet("font-weight: bold; color: white; margin-bottom: 5px;")
            cam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            camera_layout.addWidget(cam_label)
            
            # Simulated camera feed
            feed_label = QLabel("🔴 LIVE")
            feed_label.setStyleSheet("""
                background: rgba(255,0,0,0.8);
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            """)
            feed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            camera_layout.addWidget(feed_label)
            
            # Status indicator
            status_label = QLabel("🟢 Opérationnel")
            status_label.setStyleSheet("color: #38ef7d; font-size: 12px;")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            camera_layout.addWidget(status_label)
            
            cameras_grid.addWidget(camera_frame, i // 4, i % 4)
        
        layout.addLayout(cameras_grid)
        
        return surveillance_widget
    
    def create_incidents_tab(self):
        incidents_widget = QWidget()
        layout = QVBoxLayout(incidents_widget)
        
        # Incident controls
        controls_layout = QHBoxLayout()
        
        new_incident_btn = QPushButton("➕ Nouveau Rapport")
        new_incident_btn.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f093fb, stop:1 #f5576c);")
        new_incident_btn.clicked.connect(self.create_incident)
        controls_layout.addWidget(new_incident_btn)
        
        emergency_btn = QPushButton("🚨 URGENCE")
        emergency_btn.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff416c, stop:1 #ff4b2b);")
        emergency_btn.clicked.connect(self.emergency_alert)
        controls_layout.addWidget(emergency_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Incidents table
        incidents_title = QLabel("⚠️ Historique des Incidents")
        incidents_title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px 0 10px 0;")
        layout.addWidget(incidents_title)
        
        self.incidents_table = QTableWidget(12, 6)
        self.incidents_table.setHorizontalHeaderLabels(["ID", "Date/Heure", "Type", "Zone", "Priorité", "Statut"])
        self.populate_incidents_table()
        layout.addWidget(self.incidents_table)
        
        return incidents_widget
    
    def create_status_card(self, title, value, color, description):
        card = QFrame()
        card.setMinimumHeight(120)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 rgba(255,255,255,0.1));
                border: 2px solid rgba(255,255,255,0.2);
                border-radius: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(value_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.8);")
        layout.addWidget(desc_label)
        
        return card
    
    def populate_activity_table(self):
        activities = [
            ["14:32", "Accès", "Zone E1", "Agent Martin - Badge scanné"],
            ["14:28", "Mouvement", "Zone E2", "Détection caméra #5"],
            ["14:25", "Sortie", "Parking", "Véhicule immatriculé ABC-123"],
            ["14:20", "Accès", "Réception", "Livreur DHL - Autorisation temporaire"],
            ["14:15", "Alerte", "Zone E3", "Porte laissée ouverte"],
            ["14:10", "Accès", "Entrée", "Employé Sophie - Badge valide"],
            ["14:05", "Mouvement", "Zone E0", "Activité normale détectée"],
            ["14:00", "Système", "Global", "Vérification automatique OK"],
            ["13:55", "Accès", "Zone E2", "Superviseur Jean - Inspection"],
            ["13:50", "Sortie", "Expédition", "Camion de livraison parti"]
        ]
        
        for i, activity in enumerate(activities):
            for j, item in enumerate(activity):
                table_item = QTableWidgetItem(item)
                if j == 1:  # Type column
                    if "Alerte" in item:
                        table_item.setBackground(QColor("#ff4b2b"))
                    elif "Accès" in item:
                        table_item.setBackground(QColor("#38ef7d"))
                    elif "Mouvement" in item:
                        table_item.setBackground(QColor("#4facfe"))
                self.activity_table.setItem(i, j, table_item)
    
    def populate_access_table(self):
        access_requests = [
            ["A001", "Marie Dubois", "Zone E1", "En attente", "Révision"],
            ["A002", "Paul Martin", "Zone E2", "Approuvé", "Accès autorisé"],
            ["A003", "Sophie Chen", "Réception", "En attente", "Nouvelle demande"],
            ["A004", "Jean Durand", "Zone E3", "Refusé", "Habilitation manquante"],
            ["A005", "Lisa Wang", "Expédition", "En attente", "Vérification"],
            ["A006", "Marc Lemoine", "Zone E0", "Approuvé", "Accès temporaire"],
            ["A007", "Julie Moreau", "Parking", "En attente", "Visiteur"],
            ["A008", "David Kim", "Zone E2", "Approuvé", "Personnel autorisé"]
        ]
        
        for i, request in enumerate(access_requests):
            for j, item in enumerate(request):
                table_item = QTableWidgetItem(item)
                if j == 3:  # Status column
                    if "Approuvé" in item:
                        table_item.setBackground(QColor("#38ef7d"))
                    elif "Refusé" in item:
                        table_item.setBackground(QColor("#ff4b2b"))
                    elif "En attente" in item:
                        table_item.setBackground(QColor("#f093fb"))
                self.access_table.setItem(i, j, table_item)
    
    def populate_incidents_table(self):
        incidents = [
            ["I001", "2024-07-04 14:30", "Accès non autorisé", "Zone E1", "Élevée", "Résolu"],
            ["I002", "2024-07-04 13:45", "Porte ouverte", "Zone E3", "Moyenne", "En cours"],
            ["I003", "2024-07-04 12:20", "Caméra HS", "Parking", "Faible", "Programmé"],
            ["I004", "2024-07-04 11:15", "Badge perdu", "Réception", "Moyenne", "Résolu"],
            ["I005", "2024-07-04 10:30", "Véhicule suspect", "Extérieur", "Élevée", "Résolu"],
            ["I006", "2024-07-04 09:45", "Système défaillant", "Zone E2", "Critique", "Résolu"],
            ["I007", "2024-07-04 08:20", "Intrusion détectée", "Zone E0", "Critique", "Résolu"],
            ["I008", "2024-07-03 17:30", "Maintenance", "Global", "Programmée", "Terminé"],
            ["I009", "2024-07-03 16:15", "Test système", "Toutes zones", "Info", "Terminé"],
            ["I010", "2024-07-03 15:45", "Formation personnel", "Salle sécurité", "Info", "Terminé"],
            ["I011", "2024-07-03 14:20", "Mise à jour logiciel", "Système", "Programmée", "Terminé"],
            ["I012", "2024-07-03 13:10", "Vérification caméras", "Toutes zones", "Routine", "Terminé"]
        ]
        
        for i, incident in enumerate(incidents):
            for j, item in enumerate(incident):
                table_item = QTableWidgetItem(item)
                if j == 4:  # Priority column
                    if "Critique" in item:
                        table_item.setBackground(QColor("#ff4b2b"))
                    elif "Élevée" in item:
                        table_item.setBackground(QColor("#ff6b6b"))
                    elif "Moyenne" in item:
                        table_item.setBackground(QColor("#f093fb"))
                    elif "Faible" in item:
                        table_item.setBackground(QColor("#4facfe"))
                elif j == 5:  # Status column
                    if "Résolu" in item or "Terminé" in item:
                        table_item.setBackground(QColor("#38ef7d"))
                    elif "En cours" in item:
                        table_item.setBackground(QColor("#f093fb"))
                    elif "Programmé" in item:
                        table_item.setBackground(QColor("#4facfe"))
                self.incidents_table.setItem(i, j, table_item)
    
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        self.update_time()
    
    def update_time(self):
        current_time = QDateTime.currentDateTime()
        time_str = current_time.toString("dddd dd MMMM yyyy - hh:mm:ss")
        self.time_label.setText(time_str)
    
    def approve_access(self):
        # Simulated access approval
        self.status_label.setText("🟢 ACCÈS APPROUVÉ")
        self.status_label.setStyleSheet("font-size: 14px; color: #38ef7d; font-weight: bold;")
    
    def deny_access(self):
        # Simulated access denial
        self.status_label.setText("🔴 ACCÈS REFUSÉ")
        self.status_label.setStyleSheet("font-size: 14px; color: #ff4b2b; font-weight: bold;")
    
    def create_incident(self):
        # Simulated incident creation
        self.status_label.setText("📝 NOUVEAU RAPPORT CRÉÉ")
        self.status_label.setStyleSheet("font-size: 14px; color: #f093fb; font-weight: bold;")
    
    def emergency_alert(self):
        # Simulated emergency alert
        self.status_label.setText("🚨 ALERTE URGENCE ACTIVÉE")
        self.status_label.setStyleSheet("font-size: 14px; color: #ff4b2b; font-weight: bold; animation: blink 1s infinite;")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = SecurityDashboard()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()