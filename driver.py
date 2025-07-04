import sys, json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QLabel, QMessageBox, QHeaderView, QFrame, QLineEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView

class DriverApp(QWidget):
    def __init__(self, driver_info):
        super().__init__()
        self.driver_info = driver_info
        self.setWindowTitle(f"Livraisons - {driver_info['prenom']} {driver_info['nom']}")
        self.setGeometry(100, 100, 1200, 800)

        self.pending_deliveries_data = []
        self.completed_deliveries_data = []
        self.load_simulated_data()
        self.init_ui()
        self.apply_styles()
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
            }
        ]
        self.completed_deliveries_data = []

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        header = QLabel(f"🚚 Bienvenue, {self.driver_info['prenom']} {self.driver_info['nom']}")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        stats_layout = QHBoxLayout()
        self.total_label = QLabel("Total: 0")
        self.pending_label = QLabel("En attente: 0")
        self.done_label = QLabel("Terminées: 0")
        for lbl in [self.total_label, self.pending_label, self.done_label]:
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-weight:bold; padding:5px; border:1px solid #1e3a8a; border-radius:8px;")
            stats_layout.addWidget(lbl)

        # Recherche
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        search_btn = QPushButton("Rechercher")
        search_btn.clicked.connect(self.search_deliveries)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)

        # Onglets
        self.tabs = QTabWidget()
        self.pending_tab = QWidget()
        self.done_tab = QWidget()
        self.tabs.addTab(self.pending_tab, "🕒 En cours")
        self.tabs.addTab(self.done_tab, "✅ Terminées")

        self.setup_table(self.pending_tab, "pending")
        self.setup_table(self.done_tab, "done")

        # Carte
        self.map_view = QWebEngineView()
        self.update_map()

        main_layout.addWidget(header)
        main_layout.addLayout(stats_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.tabs, 3)
        main_layout.addWidget(self.map_view, 2)

    def setup_table(self, tab, tab_type):
        layout = QVBoxLayout(tab)
        table = QTableWidget()
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        if tab_type == "pending":
            headers = ["ID", "Colis", "Destinataire", "Adresse", "Prévue", "Action"]
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            self.pending_table = table
        else:
            headers = ["ID", "Colis", "Destinataire", "Adresse", "Livrée le"]
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            self.done_table = table
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)

    def load_all_deliveries(self):
        self.load_pending()
        self.load_done()
        self.update_counters()
        self.update_map()

    def load_pending(self):
        t = self.pending_table
        t.setRowCount(0)
        for i, d in enumerate(self.pending_deliveries_data):
            t.insertRow(i)
            t.setItem(i,0,QTableWidgetItem(str(d["id_livraison"])))
            t.setItem(i,1,QTableWidgetItem(d["id_colis"]))
            t.setItem(i,2,QTableWidgetItem(d["nom_destinataire"]))
            t.setItem(i,3,QTableWidgetItem(d["adresse"]))
            t.setItem(i,4,QTableWidgetItem(d["date_prevue"].toString()))
            btn = QPushButton("Détails / Livrer")
            btn.clicked.connect(lambda _, di=d: self.show_delivery_popup(di))
            t.setCellWidget(i,5,btn)

    def load_done(self):
        t = self.done_table
        t.setRowCount(0)
        for i, d in enumerate(self.completed_deliveries_data):
            t.insertRow(i)
            t.setItem(i,0,QTableWidgetItem(str(d["id_livraison"])))
            t.setItem(i,1,QTableWidgetItem(d["id_colis"]))
            t.setItem(i,2,QTableWidgetItem(d["nom_destinataire"]))
            t.setItem(i,3,QTableWidgetItem(d["adresse"]))
            t.setItem(i,4,QTableWidgetItem(d["date_livree"].toString()))

    def show_delivery_popup(self, delivery):
        info = (f"<b>Colis:</b> {delivery['id_colis']}<br>"
                f"<b>Poids:</b> {delivery['poids']}<br>"
                f"<b>Volume:</b> {delivery['volume']}<br>"
                f"<b>Type:</b> {delivery['type']}<br>"
                f"<b>Instructions:</b> {delivery['instructions']}")
        msg = QMessageBox()
        msg.setWindowTitle(f"Détails livraison {delivery['id_livraison']}")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(info)
        msg.addButton("Marquer comme livrée", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("Signaler un problème", QMessageBox.ButtonRole.DestructiveRole)
        msg.addButton("Fermer", QMessageBox.ButtonRole.RejectRole)
        ret = msg.exec()
        if ret == 0:
            self.complete_delivery(delivery)
        elif ret == 1:
            QMessageBox.warning(self, "Problème signalé", "Le problème a été signalé.")

    def complete_delivery(self, delivery):
        delivery["date_livree"] = QDate.currentDate()
        self.pending_deliveries_data.remove(delivery)
        self.completed_deliveries_data.append(delivery)
        QMessageBox.information(self, "Livré", "Livraison marquée comme livrée.")
        self.load_all_deliveries()

    def update_counters(self):
        total = len(self.pending_deliveries_data) + len(self.completed_deliveries_data)
        self.total_label.setText(f"Total: {total}")
        self.pending_label.setText(f"En attente: {len(self.pending_deliveries_data)}")
        self.done_label.setText(f"Terminées: {len(self.completed_deliveries_data)}")

    def search_deliveries(self):
        text = self.search_input.text().lower()
        for row in range(self.pending_table.rowCount()):
            match = any(text in (self.pending_table.item(row,col).text().lower() if self.pending_table.item(row,col) else '') 
                        for col in range(0,5))
            self.pending_table.setRowHidden(row, not match)

    def update_map(self):
        markers = [{"lat": d["lat"], "lon": d["lon"], "popup": d["nom_destinataire"]}
                   for d in self.pending_deliveries_data]
        center = (3.8,11.5)
        if markers:
            center = (markers[0]["lat"], markers[0]["lon"])
        html = f"""
        <html><head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
        </head><body style='margin:0'>
        <div id='map' style='width:100%; height:100%'></div>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
        var map = L.map('map').setView([{center[0]}, {center[1]}], 6);
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}.png').addTo(map);
        var m={json.dumps(markers)};
        m.forEach(d=>L.marker([d.lat,d.lon]).addTo(map).bindPopup(d.popup));
        </script></body></html>"""
        self.map_view.setHtml(html)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background:#f9fafb; color:#1e3a8a; font-family:'Segoe UI'; }
            QTabWidget::pane { border:1px solid #1e3a8a; border-radius:8px; }
            QTabBar::tab { background:#e0e7ff; padding:8px; border-radius:8px; }
            QTabBar::tab:selected { background:#1e3a8a; color:white; }
            QTableWidget { background:white; border:1px solid #1e3a8a; }
            QHeaderView::section { background:#1e3a8a; color:white; }
            QPushButton { background:#1e3a8a; color:white; border-radius:5px; padding:5px; }
            QPushButton:hover { background:#3b5bdb; }
            QLineEdit { background:white; color:black; border-radius:5px; padding:5px; }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.driver_info = {"prenom":"My_","nom":"Self"}
        self.setCentralWidget(DriverApp(self.driver_info))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
