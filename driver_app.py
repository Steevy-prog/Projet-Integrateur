import sys, json
from enum import Enum
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox,
    QHeaderView, QFrame, QLineEdit, QStackedWidget, QInputDialog, QSizePolicy,
    QComboBox, QScrollArea, QGridLayout, QDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer, QPropertyAnimation, QRect, QUrl, QThread
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView
import random # For dummy location updates
import threading # For chatbot hotkey, though not used in integrated version
import google.generativeai as genai # For chatbot

# --- Fictitious Data for demonstration ---
# Ensure dates are QDate objects for easier comparison and manipulation
FICTITIOUS_PENDING_DELIVERIES = [
    {
        "id_livraison": "L001",
        "id_colis": "C001",
        "nom_destinataire": "Alice Dupont",
        "adresse": "123 Rue Principale, Douala",
        "date_expedition": QDate(2025, 7, 1),
        "date_prevue": QDate(2025, 7, 8),
        "poids": "5 kg",
        "volume": "0.1 m³",
        "type": "Colis Standard",
        "instructions": "Laisser chez le voisin si absent.",
        "lat": 4.0456,
        "lon": 9.7045,
        "status": "pending",
        "telephone_destinataire": "699123456",
        "idconducteur": "TR1234" # Assign to a dummy driver
    },
    {
        "id_livraison": "L002",
        "id_colis": "C002",
        "nom_destinataire": "Bob Martin",
        "adresse": "456 Avenue des Fleurs, Yaoundé",
        "date_expedition": QDate(2025, 7, 2),
        "date_prevue": QDate(2025, 7, 9),
        "poids": "2.5 kg",
        "volume": "0.05 m³",
        "type": "Document Urgent",
        "instructions": "Remettre en main propre.",
        "lat": 3.8480,
        "lon": 11.5021,
        "status": "pending",
        "telephone_destinataire": "677987654",
        "idconducteur": "TR1234" # Assign to the main dummy driver
    },
    {
        "id_livraison": "L003",
        "id_colis": "C003",
        "nom_destinataire": "Charlie Brown",
        "adresse": "789 Boulevard de la Liberté, Douala",
        "date_expedition": QDate(2025, 7, 3),
        "date_prevue": QDate(2025, 7, 10),
        "poids": "10 kg",
        "volume": "0.2 m³",
        "type": "Grand Colis",
        "instructions": "Appeler avant d'arriver.",
        "lat": 4.0300,
        "lon": 9.7100,
        "status": "pending",
        "telephone_destinataire": "688112233",
        "idconducteur": "TR1234" # Assign to the main dummy driver
    }
]

FICTITIOUS_COMPLETED_DELIVERIES = [
    {
        "id_livraison": "L000",
        "id_colis": "C000",
        "nom_destinataire": "Zoe White",
        "adresse": "101 Rue du Marché, Douala",
        "date_expedition": QDate(2025, 6, 28),
        "date_prevue": QDate(2025, 7, 1),
        "date_livree": QDate(2025, 7, 1),
        "poids": "1 kg",
        "volume": "0.02 m³",
        "type": "Petit Paquet",
        "instructions": "Aucune.",
        "lat": 4.0400,
        "lon": 9.7000,
        "status": "completed",
        "telephone_destinataire": "677000000",
        "delivery_time_seconds": 1800, # 30 minutes
        "distance_km": 5.2,
        "on_time": True,
        "idconducteur": "TR1234"
    },
    {
        "id_livraison": "L004",
        "id_colis": "C004",
        "nom_destinataire": "David Green",
        "adresse": "202 Rue du Port, Douala",
        "date_expedition": QDate(2025, 6, 29),
        "date_prevue": QDate(2025, 7, 2),
        "date_livree": QDate(2025, 7, 2),
        "poids": "3 kg",
        "volume": "0.1 m³",
        "type": "Colis Fragile",
        "instructions": "Manipuler avec soin.",
        "lat": 4.0350,
        "lon": 9.6950,
        "status": "completed",
        "telephone_destinataire": "677112233",
        "delivery_time_seconds": 2400, # 40 minutes
        "distance_km": 7.8,
        "on_time": True,
        "idconducteur": "TR1234"
    },
    {
        "id_livraison": "L005",
        "id_colis": "C005",
        "nom_destinataire": "Eve Black",
        "adresse": "303 Rue de la Gare, Yaoundé",
        "date_expedition": QDate(2025, 7, 1),
        "date_prevue": QDate(2025, 7, 3),
        "date_livree": QDate(2025, 7, 4), # Late delivery
        "poids": "15 kg",
        "volume": "0.3 m³",
        "type": "Équipement Lourd",
        "instructions": "Utiliser le monte-charge.",
        "lat": 3.8500,
        "lon": 11.5100,
        "status": "completed",
        "telephone_destinataire": "699445566",
        "idconducteur": "TR1235"
    },
    {
        "id_livraison": "L006",
        "id_colis": "C006",
        "nom_destinataire": "Frank White",
        "adresse": "404 Rue du Centre, Douala",
        "date_expedition": QDate(2025, 7, 4),
        "date_prevue": QDate(2025, 7, 5),
        "date_livree": QDate(2025, 7, 5),
        "poids": "0.5 kg",
        "volume": "0.01 m³",
        "type": "Lettre",
        "instructions": "Déposer dans la boîte aux lettres.",
        "lat": 4.0480,
        "lon": 9.7080,
        "status": "completed",
        "telephone_destinataire": "677778899",
        "delivery_time_seconds": 1200, # 20 minutes
        "distance_km": 3.1,
        "on_time": True,
        "idconducteur": "TR1234"
    },
    {
        "id_livraison": "L007",
        "id_colis": "C007",
        "nom_destinataire": "Grace Hall",
        "adresse": "505 Rue de la Plage, Kribi",
        "date_expedition": QDate(2025, 7, 5),
        "date_prevue": QDate(2025, 7, 7),
        "date_livree": QDate(2025, 7, 7),
        "poids": "8 kg",
        "volume": "0.15 m³",
        "type": "Produit Frais",
        "instructions": "Urgent, conserver au frais.",
        "lat": 2.9500,
        "lon": 9.9000,
        "status": "completed",
        "telephone_destinataire": "699001122",
        "delivery_time_seconds": 4800, # 80 minutes
        "distance_km": 15.0,
        "on_time": True,
        "idconducteur": "TR1236"
    },
    {
        "id_livraison": "L008",
        "id_colis": "C008",
        "nom_destinataire": "Henry King",
        "adresse": "606 Rue du Lac, Limbe",
        "date_expedition": QDate(2025, 7, 6),
        "date_prevue": QDate(2025, 7, 8),
        "date_livree": QDate(2025, 7, 8),
        "poids": "6 kg",
        "volume": "0.1 m³",
        "type": "Électronique",
        "instructions": "Signer la réception.",
        "lat": 4.0000,
        "lon": 9.2000,
        "status": "completed",
        "telephone_destinataire": "677334455",
        "delivery_time_seconds": 3000, # 50 minutes
        "distance_km": 10.5,
        "on_time": True,
        "idconducteur": "TR1234"
    },
    {
        "id_livraison": "L009",
        "id_colis": "C009",
        "nom_destinataire": "Isabelle Lee",
        "adresse": "707 Rue de la Montagne, Bafoussam",
        "date_expedition": QDate(2025, 6, 20),
        "date_prevue": QDate(2025, 6, 22),
        "date_livree": QDate(2025, 6, 22),
        "poids": "7 kg",
        "volume": "0.12 m³",
        "type": "Vêtements",
        "instructions": "Laisser à la réception.",
        "lat": 5.4760,
        "lon": 10.4180,
        "status": "completed",
        "telephone_destinataire": "699887766",
        "delivery_time_seconds": 2700, # 45 minutes
        "distance_km": 8.9,
        "on_time": True,
        "idconducteur": "TR1236"
    },
    {
        "id_livraison": "L010",
        "id_colis": "C010",
        "nom_destinataire": "Jack Wilson",
        "adresse": "808 Rue du Soleil, Garoua",
        "date_expedition": QDate(2025, 6, 25),
        "date_prevue": QDate(2025, 6, 28),
        "date_livree": QDate(2025, 6, 29), # Late delivery
        "poids": "4 kg",
        "volume": "0.08 m³",
        "type": "Livres",
        "instructions": "Déposer devant la porte.",
        "lat": 9.3000,
        "lon": 13.4000,
        "status": "completed",
        "telephone_destinataire": "677665544",
        "delivery_time_seconds": 5400, # 90 minutes
        "distance_km": 20.0,
        "on_time": False,
        "idconducteur": "TR1239"
    },
    # Add more deliveries for July to show "This Month" stats
    {
        "id_livraison": "L011",
        "id_colis": "C011",
        "nom_destinataire": "Kelly Green",
        "adresse": "909 Rue de la Paix, Douala",
        "date_expedition": QDate(2025, 7, 7),
        "date_prevue": QDate(2025, 7, 8),
        "date_livree": QDate(2025, 7, 8),
        "poids": "2 kg",
        "volume": "0.03 m³",
        "type": "Petit Paquet",
        "instructions": "Sonner deux fois.",
        "lat": 4.0550,
        "lon": 9.7150,
        "status": "completed",
        "telephone_destinataire": "699112233",
        "delivery_time_seconds": 1500, # 25 minutes
        "distance_km": 4.5,
        "on_time": True,
        "idconducteur": "TR1234"
    },
    {
        "id_livraison": "L012",
        "id_colis": "C012",
        "nom_destinataire": "Liam Brown",
        "adresse": "111 Rue du Parc, Douala",
        "date_expedition": QDate(2025, 7, 7),
        "date_prevue": QDate(2025, 7, 9),
        "date_livree": QDate(2025, 7, 9),
        "poids": "1.5 kg",
        "volume": "0.04 m³",
        "type": "Document",
        "instructions": "Laisser à la réception.",
        "lat": 4.0600,
        "lon": 9.7200,
        "status": "completed",
        "telephone_destinataire": "677223344",
        "delivery_time_seconds": 2100, # 35 minutes
        "distance_km": 6.8,
        "on_time": True,
        "idconducteur": "TR1234"
    },
    {
        "id_livraison": "L013",
        "id_colis": "C013",
        "nom_destinataire": "Mia Davis",
        "adresse": "222 Rue des Écoles, Douala",
        "date_expedition": QDate(2025, 7, 7),
        "date_prevue": QDate(2025, 7, 10),
        "date_livree": QDate(2025, 7, 11), # Late delivery
        "poids": "9 kg",
        "volume": "0.18 m³",
        "type": "Colis Volumineux",
        "instructions": "Appeler 30 min avant.",
        "lat": 4.0500,
        "lon": 9.7050,
        "status": "completed",
        "telephone_destinataire": "688556677",
        "delivery_time_seconds": 3900, # 65 minutes
        "distance_km": 10.0,
        "on_time": False,
        "idconducteur": "TR1234"
    },
]


FICTITIOUS_DRIVER_LOCATIONS = {
    "TR1234": (4.05, 9.77), # Douala, Cameroon
    "TR1235": (3.8480, 11.5021), # Yaoundé, Cameroon
    "TR1236": (5.4737, 10.4176), # Bafoussam, Cameroon
    "TR1237": (4.0200, 9.7100), # Douala, another spot
    "TR1238": (4.0000, 9.2000), # Limbe, Cameroon
    "TR1239": (9.3000, 13.4000)  # Garoua, Cameroon
}

FICTITIOUS_DRIVERS = {
    "messie.karlone@example.com": {
        "idconducteur": "TR1234", "nom": "Karlone", "prenom": "Messie",
        "telephone": "677111111", "email": "messie.karlone@example.com"
    },
    "ambiana.thibaut@example.com": {
        "idconducteur": "TR1235", "nom": "Thibaut", "prenom": "Ambiana",
        "telephone": "677222222", "email": "ambiana.thibaut@example.com"
    },
    "steevy.valery@example.com": {
        "idconducteur": "TR1236", "nom": "Valery", "prenom": "Steevy",
        "telephone": "677333333", "email": "steevy.valery@example.com"
    },
    "navou.emmanuel@example.com": {
        "idconducteur": "TR1237", "nom": "Emmanuel", "prenom": "Navou",
        "telephone": "677444444", "email": "navou.emmanuel@example.com"
    },
    "eric.viktor@example.com": {
        "idconducteur": "TR1238", "nom": "Viktor", "prenom": "Eric",
        "telephone": "677555555", "email": "eric.viktor@example.com"
    },
    "marc.landry@example.com": {
        "idconducteur": "TR1239", "nom": "Landry", "prenom": "Marc",
        "telephone": "677666666", "email": "marc.landry@example.com"
    },
}

# --- Internal Dummy Database Manager ---
# This class simulates database operations directly in memory using fictitious data.
# It is used when the application runs in a single-file, self-contained mode.
class InternalDummyDBManager:
    def __init__(self):
        # Create copies of fictitious data to allow modification during runtime
        self.pending_deliveries_dummy = [dict(d) for d in FICTITIOUS_PENDING_DELIVERIES]
        self.completed_deliveries_dummy = [dict(d) for d in FICTITIOUS_COMPLETED_DELIVERIES]
        self.driver_locations_dummy = dict(FICTITIOUS_DRIVER_LOCATIONS)
        self.drivers_info_dummy = dict(FICTITIOUS_DRIVERS) # Corrected typo here

    def connect(self):
        print("Dummy DB: Connecté (simulé).")
        return True

    def test_connection(self):
        print("Dummy DB: Test de connexion réussi (simulé).")
        return True

    def execute_query(self, query, params=None):
        print(f"Dummy DB: Exécution de la requête (simulée): {query} avec les paramètres {params}")
        # Simulate UPDATE for status change in "LivraisonConducteurColis"
        if "UPDATE" in query and "status = 'completed'" in query and "LivraisonConducteurColis" in query:
            # Assuming params are (date_livree_str, id_livraison)
            date_livree_str = params[0]
            delivery_id_to_complete = params[1] 
            
            # Find and move the delivery from pending to completed
            found_index = -1
            for i, delivery in enumerate(self.pending_deliveries_dummy):
                if delivery["id_livraison"] == delivery_id_to_complete:
                    found_index = i
                    break
            
            if found_index != -1:
                delivery = self.pending_deliveries_dummy.pop(found_index)
                delivery["status"] = "completed"
                delivery["date_livree"] = QDate.fromString(date_livree_str, 'yyyy-MM-dd')
                # Simulate "on time" status for completed deliveries moved from pending
                # For simplicity, assume it's on time if date_livree <= date_prevue
                delivery["on_time"] = (delivery["date_livree"] <= delivery["date_prevue"])
                
                # Add fictitious values for delivery_time_seconds and distance_km if absent
                if "delivery_time_seconds" not in delivery or delivery["delivery_time_seconds"] is None:
                    delivery["delivery_time_seconds"] = random.randint(1000, 5000) # Fictitious default value
                if "distance_km" not in delivery or delivery["distance_km"] is None:
                    delivery["distance_km"] = round(random.uniform(3.0, 20.0), 1) # Fictitious default value

                self.completed_deliveries_dummy.append(delivery)
                print(f"Dummy DB: Livraison {delivery_id_to_complete} marquée comme terminée et déplacée.")
            return
        # Simulate UPDATE for DriverLocations
        if "DriverLocations" in query and "UPDATE" in query:
            driver_id = params[2]
            lat = float(params[0])
            lon = float(params[1])
            self.driver_locations_dummy[driver_id] = (lat, lon)
            print(f"Dummy DB: Localisation du conducteur {driver_id} mise à jour en mémoire à ({lat}, {lon}).")
            return
        pass

    def fetch_one(self, query, params=None):
        print(f"Dummy DB: Récupération d'un élément (simulée): {query} avec les paramètres {params}")
        if "SELECT current_latitude" in query and "DriverLocations" in query:
            driver_id = params[0]
            # Returns a tuple (lat, lon) as expected by the map update function
            return self.driver_locations_dummy.get(driver_id, (4.05, 9.77)) # Default if not found
        if "SELECT idconducteur" in query and "Conducteur" in query:
            # Simulate searching for driver for login
            email = params[0]
            driver_data = self.drivers_info_dummy.get(email)
            if driver_data:
                # Return dict for consistency with how DriverApp expects data
                return driver_data
        return None # Return None if no match or other query

    def fetch_all(self, query, params=None):
        print(f"Dummy DB: Récupération de tous les éléments (simulée): {query} avec les paramètres {params}")
        driver_id = params[0] if params else None # Assume driver_id is the first param for filtering

        if "status = 'pending'" in query and "LivraisonConducteurColis" in query:
            filtered_data = [d for d in self.pending_deliveries_dummy if driver_id is None or d.get("idconducteur", "") == driver_id]
            # Return list of dictionaries
            return filtered_data
        elif "status = 'completed'" in query and "LivraisonConducteurColis" in query:
            filtered_data = [d for d in self.completed_deliveries_dummy if driver_id is None or d.get("idconducteur", "") == driver_id]
            # Return list of dictionaries
            return filtered_data
        return [] # Return an empty list for other queries

    def close(self):
        print("Dummy DB: Fermé (simulé).")

# --- Définition de la palette de couleurs "Élégance Douce" ---
COLOR_PRIMARY = "#5F7F80"  # Un vert-bleu sourd et élégant
COLOR_SECONDARY = "#8AB0B2" # Un vert-bleu plus clair et lumineux
COLOR_BACKGROUND_LIGHT = "#F5F5F5" # Un gris très clair, presque blanc
COLOR_TEXT_DARK = "#333333" # Un gris anthracite foncé
COLOR_SUCCESS = "#7CB342"  # Un vert olive doux et naturel
COLOR_WARNING = "#FFB300"  # Un orange ambre doux
COLOR_INFO = "#5F7F80"    # Le même vert-bleu sourd que COLOR_PRIMARY
COLOR_BORDER_LIGHT = "#E0E0E0" # Un gris clair et subtil
COLOR_HOVER_LIGHT = "rgba(0, 0, 0, 0.05)" # Un léger voile gris transparent
COLOR_HOVER_DARK = "#4A6465" # Un vert-bleu plus foncé pour les survols des éléments primaires
COLOR_ERROR = "#E57373" # Un rouge atténué

# Ajout des couleurs manquantes
COLOR_PRIMARY_DARK = "#4A6465" # Un vert-bleu plus foncé
COLOR_PRIMARY_LIGHT = "#C0D1D2" # Un vert-bleu très pâle
COLOR_TEXT_SECONDARY = "#757575" # Un gris moyen

# --- Informations du conducteur par défaut (utilisé pour la recherche après login) ---
placeholder_driver_info = {
    "idconducteur": "TR1234",
    "nom": "Karlone",
    "prenom": "Messie",
    "telephone": "677111111",
    "email": "messie.karlone@example.com"
}

class AnimatedButton(QPushButton):
    """Bouton animé personnalisé avec effets de survol pour la navigation latérale."""
    def __init__(self, text, icon="", parent=None):
        super().__init__(text, parent)
        self.original_text = text # Stocker le texte original
        self.icon_text = icon
        self.is_active = False
        self.setMinimumHeight(50)
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.set_expanded_state(True) # L'état initial est étendu

    def set_active(self, active):
        self.is_active = active
        self.update_style()

    def set_expanded_state(self, expanded):
        # Ajuster le texte et l'alignement en fonction de l'état étendu de la barre latérale
        if expanded:
            self.setText(self.icon_text + " " + self.original_text)
            self.setStyleSheet(self.styleSheet() + "text-align: left;")
        else:
            self.setText(self.icon_text) # Afficher uniquement l'icône
            self.setStyleSheet(self.styleSheet() + "text-align: center;")
        self.update_style() # Réappliquer le style pour que les changements prennent effet

    def update_style(self):
        if self.is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 {COLOR_PRIMARY}, stop:1 {COLOR_SECONDARY});
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-weight: 600;
                    margin: 2px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 {COLOR_PRIMARY_DARK}, stop:1 {COLOR_SECONDARY});
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {COLOR_BACKGROUND_LIGHT};
                    color: {COLOR_TEXT_DARK};
                    border: 1px solid {COLOR_BORDER_LIGHT};
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-weight: 500;
                    margin: 2px;
                }}
                QPushButton:hover {{
                    background: {COLOR_HOVER_LIGHT};
                    border: 1px solid {COLOR_PRIMARY};
                    color: {COLOR_PRIMARY};
                }}
            """)
        # Réappliquer l'alignement du texte en fonction de l'état étendu actuel
        if self.text() == self.icon_text: # État réduit
            self.setStyleSheet(self.styleSheet() + "text-align: center;")
        else: # État étendu
            self.setStyleSheet(self.styleSheet() + "text-align: left;")

class StatsCard(QFrame):
    """Widget de carte de statistiques personnalisé pour le tableau de bord et les statistiques."""
    def __init__(self, title, value, icon, color):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)
        self.setMinimumHeight(120)
        self.setMaximumHeight(120)

        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 24))
        icon_label.setStyleSheet(f"color: {color};")

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        title_label.setStyleSheet(f"color: {COLOR_TEXT_DARK};")

        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        header_layout.addWidget(title_label)

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
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: 16px;
                padding: 15px;
            }}
            QFrame:hover {{
                border: 1px solid {color};
            }}
        """)

    def update_value(self, value):
        self.value_label.setText(str(value))


class SideBar(QFrame):
    """Barre latérale personnalisée avec boutons de navigation et fonctionnalité de bascule."""
    navigation_changed = pyqtSignal(int)
    sidebar_state_changed = pyqtSignal(bool) # True for expanded, False for collapsed
    logout_requested = pyqtSignal() # Signal for logout

    def __init__(self):
        super().__init__()
        self.expanded_width = 280
        self.collapsed_width = 0 # Width when fully collapsed
        self.is_expanded = True

        self.setFrameStyle(QFrame.Shape.Box)
        self.setFixedWidth(self.expanded_width) # Initial width

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.header = QLabel("🚚 SCA Delivery Dashboard")
        self.header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.header.setStyleSheet(f"color: {COLOR_TEXT_DARK}; padding: 10px 0;")
        self.layout.addWidget(self.header)

        self.nav_buttons = []
        # Updated navigation items based on the new structure
        nav_items = [
            ("Tableau de bord", "📋"),
            ("Livraisons terminées", "✅"), # Index 1
            ("Carte interactive", "🗺️"),    # Index 2
            ("Aide", "❓"),                 # Index 3
            ("Paramètres", "⚙️")             # Index 4
        ]

        for i, (text, icon) in enumerate(nav_items):
            btn = AnimatedButton(text, icon)
            btn.clicked.connect(lambda checked, idx=i: self.set_active_nav(idx))
            self.nav_buttons.append(btn)
            self.layout.addWidget(btn)

        self.layout.addStretch()

        self.user_frame = QFrame()
        self.user_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLOR_PRIMARY};
                border-radius: 12px;
                padding: 15px;
                color: white;
            }}
        """)
        self.user_layout = QVBoxLayout(self.user_frame)
        self.user_name = QLabel("👤 Mon Profil")
        self.user_name.setObjectName("user_name_label")
        self.user_name.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.user_role = QLabel("Chauffeur-livreur")
        self.user_role.setFont(QFont("Segoe UI", 10))
        self.user_role.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        self.user_layout.addWidget(self.user_name)
        self.user_layout.addWidget(self.user_role)
        self.layout.addWidget(self.user_frame)

        self.logout_btn = AnimatedButton("Déconnexion", "➡️")
        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_ERROR};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                font-weight: 600;
                margin: 2px;
            }}
            QPushButton:hover {{
                background: #C0392B; /* Darker red */
            }}
        """)
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        self.layout.addWidget(self.logout_btn)

        self.set_active_nav(0) # Set dashboard as default active

        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 {COLOR_BACKGROUND_LIGHT}, stop:1 #edf2f7);
                border-right: 1px solid {COLOR_BORDER_LIGHT};
            }}
        """)
        self.set_expanded_state(True) # Ensure initial state is expanded

    def set_active_nav(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)
        self.current_index = index
        self.navigation_changed.emit(index)

    def toggle_sidebar(self):
        self.is_expanded = not self.is_expanded
        self.set_expanded_state(self.is_expanded)
        self.sidebar_state_changed.emit(self.is_expanded)

    def set_expanded_state(self, expanded):
        self.is_expanded = expanded
        target_width = self.expanded_width if expanded else self.collapsed_width

        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.start()

        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.start()

        if expanded:
            self.header.show()
            self.user_frame.show()
            self.logout_btn.show()
            self.layout.setContentsMargins(20, 20, 20, 20)
            for btn in self.nav_buttons:
                btn.set_expanded_state(True)
            self.logout_btn.set_expanded_state(True)
        else:
            self.header.hide()
            self.user_frame.hide()
            self.logout_btn.hide()
            self.layout.setContentsMargins(0, 0, 0, 0)
            for btn in self.nav_buttons:
                btn.set_expanded_state(False)
            self.logout_btn.set_expanded_state(False)

        self.sidebar_state_changed.emit(self.is_expanded)


class ReportIssueDialog(QDialog):
    """Dialogue personnalisé pour signaler un problème avec un champ de texte."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Signaler un problème")
        self.setMinimumSize(400, 300) # Adequate size for text input
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR_BACKGROUND_LIGHT};
                border-radius: 16px;
                border: 1px solid {COLOR_BORDER_LIGHT};
            }}
            QLabel {{
                color: {COLOR_TEXT_DARK};
                font-size: 14px;
            }}
            QTextEdit {{
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                font-size: 14px;
                color: {COLOR_TEXT_DARK};
            }}
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_SECONDARY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("Décrivez le problème rencontré :")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLOR_PRIMARY};")
        layout.addWidget(title_label)

        self.problem_text_edit = QTextEdit()
        self.problem_text_edit.setPlaceholderText("Ex: Le destinataire était absent, l'adresse est incorrecte, colis endommagé...")
        layout.addWidget(self.problem_text_edit)

        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ERROR};
            }}
            QPushButton:hover {{
                background-color: #C0392B;
            }}
        """)
        self.cancel_button.clicked.connect(self.reject) # Reject the dialog
        button_layout.addWidget(self.cancel_button)

        self.submit_button = QPushButton("Valider")
        self.submit_button.clicked.connect(self.accept) # Accept the dialog
        button_layout.addWidget(self.submit_button)

        layout.addLayout(button_layout)

    def get_problem_description(self):
        return self.problem_text_edit.toPlainText()


# --- Chatbot Integration ---
API_KEY = "AIzaSyACCuz2G5YDYs7rmVl9X7Q_Z60Qa1TOq_8"
genai.configure(api_key=API_KEY)

MODEL_NAME = "models/gemini-2.5-pro"
model = genai.GenerativeModel(MODEL_NAME)

HELP_TEXT = """
To reset your password, click 'Forgot Password' on the login screen.
You’ll receive an email with a link to create a new one.
If you don’t receive it, check your spam folder or contact support.
"""

class WorkerThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            response = model.generate_content(self.prompt)
            answer = response.text.strip()
        except Exception as e:
            answer = f"Error: {e}"
        self.finished.emit(answer)


class ChatBot(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCA AI help Chatbot")
        self.resize(400, 450)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Window) # Keep on top

        # Card frame
        card = QFrame(self)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_PRIMARY}; /* Using primary color for chatbot background */
                border-radius: 18px;
                border: 1.5px solid {COLOR_BORDER_LIGHT};
                padding: 18px;
                box-shadow: 0 6px 24px rgba(108,99,255,0.10);
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(18, 18, 18, 18)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(f"background: #fff; border-radius: 8px; padding: 8px; color: {COLOR_TEXT_DARK};")
        self.chat_display.setFont(QFont("Segoe UI", 10))
        card_layout.addWidget(self.chat_display)

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Tapez votre message ici...")
        self.input_line.setStyleSheet(f"background: #FFFFFF; border-radius: 8px; padding: 8px; color: {COLOR_TEXT_DARK};")
        self.input_line.setFont(QFont("Segoe UI", 10))
        card_layout.addWidget(self.input_line)

        self.send_button = QPushButton("Envoyer")
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SUCCESS}; /* Green for send button */
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 8px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: #3B823E; /* Darker green */
            }}
        """)
        card_layout.addWidget(self.send_button)

        # Main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(card)

        self.send_button.clicked.connect(self.on_send)
        self.input_line.returnPressed.connect(self.on_send)

        self.append_message("System", "Bienvenue ! Posez-moi des questions sur l'application.")

        self.worker_thread = None

    def append_message(self, sender, message):
        self.chat_display.append(f"<b>{sender}:</b> {message}")

    def on_send(self):
        question = self.input_line.text().strip()
        if not question:
            return

        self.append_message("Vous", question)
        self.input_line.clear()

        self.append_message("Bot", "<i>Réflexion en cours...</i>")

        prompt = f"""
You are a helpful and kind assistant. Use the following help guide to answer the user's question. If he asks about something not in the help guide, say you don't know.
If he greets you or shows any sign of politeness, respond in a friendly manner.

HELP DOCUMENT:
{HELP_TEXT}

QUESTION:
{question}

Answer only based on the HELP DOCUMENT above.
"""

        self.worker_thread = WorkerThread(prompt)
        self.worker_thread.finished.connect(self.handle_response)
        self.worker_thread.start()

    def handle_response(self, answer):
        self.chat_display.undo() # Remove "Thinking..." message
        self.append_message("SCA-Bot", answer)
        self.worker_thread = None


class DriverApp(QWidget):
    """Fenêtre principale de l'application pour le tableau de bord du conducteur."""
    def __init__(self, driver_info, db_manager):
        super().__init__()
        self.driver_info = driver_info
        self.db_manager = db_manager
        self.setWindowTitle(f"DeliveryPro - {driver_info['prenom']} {driver_info['nom']}")
        
        self.setMinimumSize(800, 600) 

        self.pending_deliveries_data = []
        self.completed_deliveries_data = []
        self.driver_current_location = None
        self.chatbot_window = None # To hold the chatbot instance

        self.init_ui()
        self.apply_modern_styles()

        self.loading_label = QLabel("Chargement des données...", self)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        self.loading_label.setStyleSheet(f"color: {COLOR_PRIMARY}; padding: 20px;")
        self.loading_label.hide()

        self.load_all_deliveries_from_db()

        self.location_timer = QTimer(self)
        self.location_timer.setInterval(60000) # Update location every 60 seconds
        self.location_timer.timeout.connect(self.update_driver_location_on_map)
        self.location_timer.start()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = SideBar()
        self.sidebar.navigation_changed.connect(self.change_view)
        self.sidebar.sidebar_state_changed.connect(self.update_top_bar_elements)
        self.sidebar.logout_requested.connect(self.logout)
        self.main_layout.addWidget(self.sidebar)

        user_name_label = self.sidebar.findChild(QLabel, "user_name_label")
        if user_name_label:
            user_name_label.setText(f"👤 {self.driver_info['prenom']} {self.driver_info['nom']}")

        self.content_area_layout = QVBoxLayout()
        self.content_area_layout.setContentsMargins(0,0,0,0)
        self.content_area_layout.setSpacing(0)

        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(60)
        self.top_bar.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-bottom: 1px solid {COLOR_BORDER_LIGHT};
            }}
        """)
        top_bar_layout = QHBoxLayout(self.top_bar)
        top_bar_layout.setContentsMargins(15, 0, 15, 0)
        top_bar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.toggle_button = QPushButton("☰") # Hamburger icon
        self.toggle_button.setFixedSize(40, 40)
        self.toggle_button.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.toggle_button.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: {COLOR_HOVER_DARK};
            }}
        """)
        self.toggle_button.clicked.connect(self.sidebar.toggle_sidebar)
        top_bar_layout.addWidget(self.toggle_button)

        top_bar_layout.addStretch()

        self.content_area_layout.addWidget(self.top_bar)

        self.content_stack = QStackedWidget()
        self.content_area_layout.addWidget(self.content_stack)

        self.create_dashboard_view()
        self.create_completed_view() # Now index 1
        self.create_map_view()       # Now index 2
        self.create_help_view()      # Now index 3
        self.create_settings_view()  # Now index 4

        self.main_layout.addLayout(self.content_area_layout, 1)

    def update_top_bar_elements(self, is_expanded):
        pass

    def create_dashboard_view(self):
        # Create a main widget for the dashboard content
        dashboard_content_widget = QWidget()
        dashboard_content_layout = QVBoxLayout(dashboard_content_widget)
        dashboard_content_layout.setSpacing(20)
        dashboard_content_layout.setContentsMargins(30, 30, 30, 30)

        # Wrap the dashboard content in a QScrollArea
        dashboard_scroll_area = QScrollArea()
        dashboard_scroll_area.setWidgetResizable(True)
        dashboard_scroll_area.setWidget(dashboard_content_widget)
        dashboard_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent; /* Make scroll area background transparent */
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent; /* Ensure content widget background is transparent */
            }
        """)

        # Add the scroll area to the content stack
        self.content_stack.addWidget(dashboard_scroll_area)


        welcome_label = QLabel(f"Bonjour {self.driver_info['prenom']} ! 👋")
        welcome_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        welcome_label.setStyleSheet(f"color: {COLOR_TEXT_DARK}; margin-bottom: 10px;")

        dashboard_content_layout.addWidget(welcome_label)

        # --- Direct display of "Livraisons en cours" ---
        pending_deliveries_title = QLabel("🕒 Livraisons en cours aujourd'hui")
        pending_deliveries_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        pending_deliveries_title.setStyleSheet(f"color: {COLOR_TEXT_DARK}; margin-top: 20px; margin-bottom: 10px;")
        dashboard_content_layout.addWidget(pending_deliveries_title)

        self.dashboard_pending_table = QTableWidget()
        self.setup_modern_table(self.dashboard_pending_table, "pending")
        # Ensure the table expands to fill available space
        self.dashboard_pending_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        dashboard_content_layout.addWidget(self.dashboard_pending_table) 

        self.no_pending_dashboard_label = QLabel("🎉 Aucune livraison en cours pour le moment. Profitez de votre pause !")
        self.no_pending_dashboard_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_pending_dashboard_label.setFont(QFont("Segoe UI", 16, QFont.Weight.DemiBold))
        self.no_pending_dashboard_label.setStyleSheet(f"color: {COLOR_SUCCESS}; padding: 50px;")
        self.no_pending_dashboard_label.hide()
        dashboard_content_layout.addWidget(self.no_pending_dashboard_label)

        # Button to navigate to the map
        view_map_btn = QPushButton("🗺️ Ouvrir la carte interactive")
        view_map_btn.setMinimumHeight(45)
        view_map_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        view_map_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {COLOR_PRIMARY}, stop:1 {COLOR_SECONDARY});
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                font-weight: 600;
                margin-top: 20px; /* Add some space above the button */
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {COLOR_PRIMARY_DARK}, stop:1 {COLOR_SECONDARY});
            }}
        """)
        view_map_btn.clicked.connect(lambda: self.sidebar.set_active_nav(2)) # Index 2 for Map
        dashboard_content_layout.addWidget(view_map_btn)

        dashboard_content_layout.addStretch() # Ensures the table and button are pushed to the top


    def populate_dashboard_pending_table(self):
        t = self.dashboard_pending_table
        t.setRowCount(len(self.pending_deliveries_data))
        if len(self.pending_deliveries_data) == 0:
            t.hide()
            self.no_pending_dashboard_label.show()
        else:
            t.show()
            self.no_pending_dashboard_label.hide()
            for row_idx, delivery in enumerate(self.pending_deliveries_data):
                t.setItem(row_idx, 0, QTableWidgetItem(str(delivery["id_livraison"])))
                t.setItem(row_idx, 1, QTableWidgetItem(delivery["id_colis"]))
                t.setItem(row_idx, 2, QTableWidgetItem(delivery["nom_destinataire"]))
                t.setItem(row_idx, 3, QTableWidgetItem(delivery["adresse"]))
                t.setItem(row_idx, 4, QTableWidgetItem(delivery["date_expedition"].toString('yyyy-MM-dd') if delivery["date_expedition"] else 'N/A'))
                t.setItem(row_idx, 5, QTableWidgetItem(delivery["date_prevue"].toString('yyyy-MM-dd') if delivery["date_prevue"] else 'N/A'))
                t.setItem(row_idx, 6, QTableWidgetItem(delivery["poids"]))
                t.setItem(row_idx, 7, QTableWidgetItem(delivery["volume"]))
                t.setItem(row_idx, 8, QTableWidgetItem(delivery["type"]))
                t.setItem(row_idx, 9, QTableWidgetItem(delivery["instructions"]))
                t.setItem(row_idx, 10, QTableWidgetItem(str(delivery["lat"]) if delivery["lat"] is not None else 'N/A'))
                t.setItem(row_idx, 11, QTableWidgetItem(str(delivery["lon"]) if delivery["lon"] is not None else 'N/A'))
                t.setItem(row_idx, 12, QTableWidgetItem(delivery["status"]))
                t.setItem(row_idx, 13, QTableWidgetItem(delivery["telephone_destinataire"]))

                details_button = QPushButton("Détails")
                details_button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_INFO};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 5px 10px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: {COLOR_PRIMARY_DARK};
                    }}
                """)
                # Connect the button to a handler, passing the entire delivery dictionary
                details_button.clicked.connect(lambda checked, d=delivery: self.show_delivery_popup(d))
                t.setCellWidget(row_idx, 14, details_button) # Column 14 for action


    def create_completed_view(self):
        completed_widget = QWidget()
        layout = QVBoxLayout(completed_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("✅ Livraisons terminées")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLOR_TEXT_DARK};")
        layout.addWidget(title)

        self.done_table = QTableWidget()
        self.setup_modern_table(self.done_table, "done")
        layout.addWidget(self.done_table)

        # Message for empty completed deliveries
        self.no_completed_label = QLabel("😔 Aucune livraison terminée n'a été enregistrée.")
        self.no_completed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_completed_label.setFont(QFont("Segoe UI", 16, QFont.Weight.DemiBold))
        self.no_completed_label.setStyleSheet(f"color: {COLOR_WARNING}; padding: 50px;")
        self.no_completed_label.hide()
        layout.addWidget(self.no_completed_label)
        layout.addStretch()
        self.content_stack.addWidget(completed_widget)

    def create_map_view(self):
        map_widget = QWidget()
        layout = QVBoxLayout(map_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("🗺️ Carte interactive")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLOR_TEXT_DARK};")
        layout.addWidget(title)

        self.map_view = QWebEngineView()
        self.map_view.setStyleSheet(f"""
            QWebEngineView {{
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: 12px;
            }}
        """)
        layout.addWidget(self.map_view)

        # Loading indicator for the map
        self.map_loading_label = QLabel("Chargement de la carte...", self)
        self.map_loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_loading_label.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        self.map_loading_label.setStyleSheet(f"color: {COLOR_PRIMARY}; padding: 20px;")
        self.map_loading_label.hide()
        layout.addWidget(self.map_loading_label)
        layout.addStretch()

        self.content_stack.addWidget(map_widget)

    def create_help_view(self):
        help_widget = QWidget()
        layout = QVBoxLayout(help_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("❓ Centre d'aide")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLOR_TEXT_DARK};")
        layout.addWidget(title)

        help_text = f"""
        <div style='font-family: Segoe UI; line-height: 1.6; color: {COLOR_TEXT_DARK};'>
            <h3 style='color: {COLOR_PRIMARY}; margin-top: 0;'>Bienvenue dans le Centre d'Aide !</h3>
            <p>Cette section vous fournit des informations essentielles sur l'utilisation de l'application de livraison.</p>
            
            <h4 style='color: {COLOR_TEXT_DARK};'>Fonctionnalités principales :</h4>
            <ul>
                <li><strong>Tableau de bord :</strong> Aperçu rapide de vos livraisons en cours et terminées du jour.</li>
                <li><strong>Livraisons terminées :</strong> Historique de toutes les livraisons que vous avez complétées.</li>
                <li><strong>Carte interactive :</strong> Visualisez votre position actuelle ainsi que les lieux de livraison en cours et terminées sur une carte.</li>
                <li><strong>Paramètres :</strong> Accédez à vos informations de profil.</li>
            </ul>
            
            <h4 style='color: {COLOR_TEXT_DARK};'>Comment marquer une livraison comme terminée ?</h4>
            <p>Dans la section "Tableau de bord", cliquez sur la carte "En cours" pour afficher la liste de vos livraisons en attente. Ensuite, cliquez sur le bouton "Détails" à côté de la livraison concernée. Une fenêtre s'ouvrira, vous y trouverez un bouton "Marquer comme livrée". Cliquez dessus pour confirmer la fin de la livraison.</p>
            
            <h4 style='color: {COLOR_TEXT_DARK};'>Que faire en cas de problème ?</h4>
            <p>Si vous rencontrez un problème avec une livraison (adresse introuvable, destinataire absent, colis endommagé, etc.), vous pouvez le signaler depuis la fenêtre des détails de la livraison en cliquant sur "Signaler un problème". Notre équipe de support vous contactera.</p>
            
            <h4 style='color: {COLOR_TEXT_DARK};'>Mise à jour de la position :</h4>
            <p>Votre position est automatiquement mise à jour sur la carte interactive toutes les 60 secondes pour permettre un suivi précis de vos livraisons.</p>
            
            <p style='margin-top: 20px; font-style: italic;'>Pour toute question supplémentaire, veuillez contacter le support technique.</p>
            <p style='margin-top: 20px; font-weight: bold;'>Pour une assistance rapide, démarrez notre chatbot intelligent !</p>
        </div>
        """
        
        self.help_content_label = QLabel()
        self.help_content_label.setTextFormat(Qt.TextFormat.RichText)
        self.help_content_label.setText(help_text)
        self.help_content_label.setWordWrap(True)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.help_content_label)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: 12px;
                background-color: white;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: white;
                padding: 20px;
            }}
        """)
        
        layout.addWidget(scroll_area)

        # Add Chatbot Button
        chatbot_button = QPushButton("🤖 Démarrer le Chatbot")
        chatbot_button.setMinimumHeight(45)
        chatbot_button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        chatbot_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_SUCCESS}, stop:1 {COLOR_PRIMARY});
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #3B823E, stop:1 {COLOR_PRIMARY_DARK});
            }}
        """)
        chatbot_button.clicked.connect(self.start_chatbot)
        layout.addWidget(chatbot_button)

        layout.addStretch()
        self.content_stack.addWidget(help_widget)

    def start_chatbot(self):
        """Launches the chatbot window."""
        if not self.chatbot_window:
            self.chatbot_window = ChatBot()
        self.chatbot_window.show()
        self.chatbot_window.activateWindow()
        self.chatbot_window.raise_()


    def create_settings_view(self):
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("⚙️ Paramètres")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLOR_TEXT_DARK};")
        layout.addWidget(title)

        # Driver Info Section
        driver_info_frame = QFrame()
        driver_info_frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        driver_info_layout = QVBoxLayout(driver_info_frame)
        driver_info_layout.setSpacing(10)

        info_title = QLabel("Informations du conducteur")
        info_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        info_title.setStyleSheet(f"color: {COLOR_PRIMARY}; margin-bottom: 10px;")
        driver_info_layout.addWidget(info_title)

        # Display driver info
        driver_info_layout.addWidget(QLabel(f"<b>ID:</b> {self.driver_info.get('idconducteur', 'N/A')}"))
        driver_info_layout.addWidget(QLabel(f"<b>Nom:</b> {self.driver_info.get('nom', 'N/A')}"))
        driver_info_layout.addWidget(QLabel(f"<b>Prénom:</b> {self.driver_info.get('prenom', 'N/A')}"))
        driver_info_layout.addWidget(QLabel(f"<b>Téléphone:</b> {self.driver_info.get('telephone', 'N/A')}"))
        driver_info_layout.addWidget(QLabel(f"<b>Email:</b> {self.driver_info.get('email', 'N/A')}"))

        layout.addWidget(driver_info_frame)
        layout.addStretch()

        self.content_stack.addWidget(settings_widget)

    def report_issue(self):
        QMessageBox.information(self, 'Signaler un problème',
                                "Votre problème a été signalé au service client. Nous vous contacterons bientôt.")


    def setup_modern_table(self, table_widget, table_type):
        """Configure le style et les propriétés des QTableWidget."""
        if table_type == "pending":
            headers = ["ID Livraison", "ID Colis", "Destinataire", "Adresse", "Date Exp.", "Date Prévue", "Poids", "Volume", "Type", "Instructions", "Lat", "Long", "Statut", "Téléphone", "Action"]
            table_widget.setColumnCount(len(headers))
        else: # table_type == "done"
            headers = ["ID Livraison", "ID Colis", "Destinataire", "Adresse", "Date Exp.", "Date Prévue", "Date Livrée", "Poids", "Volume", "Type", "Instructions", "Lat", "Long", "Statut", "Téléphone", "Temps (s)", "Distance (km)", "À l'heure"]
            table_widget.setColumnCount(len(headers))

        table_widget.setHorizontalHeaderLabels(headers)
        table_widget.horizontalHeader().setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        table_widget.horizontalHeader().setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {COLOR_PRIMARY};
                color: white;
                padding: 8px;
                border: 1px solid {COLOR_PRIMARY_DARK};
                font-weight: bold;
            }}
        """)
        table_widget.verticalHeader().setVisible(False)
        table_widget.setAlternatingRowColors(True)
        table_widget.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: 12px;
                background-color: white;
                gridline-color: {COLOR_BORDER_LIGHT};
                font-size: 14px;
                selection-background-color: {COLOR_PRIMARY_LIGHT};
                selection-color: {COLOR_TEXT_DARK};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background-color: {COLOR_PRIMARY_LIGHT};
                color: {COLOR_TEXT_DARK};
            }}
            QTableCornerButton::section {{
                background-color: {COLOR_PRIMARY};
                border: 1px solid {COLOR_PRIMARY_DARK};
            }}
        """)
        table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_widget.horizontalHeader().setStretchLastSection(True)

    def load_all_deliveries_from_db(self):
        self.loading_label.show()
        QApplication.processEvents()

        try:
            driver_id = self.driver_info["idconducteur"]
            print(f"Fetching deliveries for driver ID: {driver_id}")
            # Fetching pending deliveries (still needed for dashboard and dialog)
            self.pending_deliveries_data = self.db_manager.fetch_all(
                "SELECT * FROM LivraisonConducteurColis WHERE status = 'pending' AND idconducteur = %s;",
                (driver_id,)
            )
            # Convert QDate objects for pending deliveries
            for d in self.pending_deliveries_data:
                d["date_expedition"] = QDate.fromString(str(d["date_expedition"]), 'yyyy-MM-dd') if d.get("date_expedition") else None
                d["date_prevue"] = QDate.fromString(str(d["date_prevue"]), 'yyyy-MM-dd') if d.get("date_prevue") else None

            # Fetching completed deliveries
            self.completed_deliveries_data = self.db_manager.fetch_all(
                "SELECT * FROM LivraisonConducteurColis WHERE status = 'completed' AND idconducteur = %s;",
                (driver_id,)
            )
            # Convert QDate objects for completed deliveries
            for d in self.completed_deliveries_data:
                d["date_expedition"] = QDate.fromString(str(d["date_expedition"]), 'yyyy-MM-dd') if d.get("date_expedition") else None
                d["date_prevue"] = QDate.fromString(str(d["date_prevue"]), 'yyyy-MM-dd') if d.get("date_prevue") else None
                d["date_livree"] = QDate.fromString(str(d["date_livree"]), 'yyyy-MM-dd') if d.get("date_livree") else None


            print(f"Pending deliveries fetched: {len(self.pending_deliveries_data)}")
            print(f"Completed deliveries fetched: {len(self.completed_deliveries_data)}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur de données", f"Échec du chargement des livraisons : {e}")
            self.pending_deliveries_data = []
            self.completed_deliveries_data = []
        
        self.populate_dashboard_pending_table() # Populate the new dashboard table
        self.load_completed_table_data() # Only update completed table directly
        # self.update_dashboard_stats() # Removed as per user request
        self.update_driver_location_on_map()

        self.loading_label.hide()

    def update_tables(self):
        # This method is adjusted as pending table is no longer a main view
        # The pending table for the dialog is loaded when the dialog is shown.
        self.populate_dashboard_pending_table()
        self.load_completed_table_data()

    def load_completed_table_data(self):
        t = self.done_table
        t.setRowCount(len(self.completed_deliveries_data))
        if len(self.completed_deliveries_data) == 0:
            t.hide()
            self.no_completed_label.show()
        else:
            t.show()
            self.no_completed_label.hide()
            for row_idx, delivery in enumerate(self.completed_deliveries_data):
                t.setItem(row_idx, 0, QTableWidgetItem(str(delivery.get("id_livraison", 'N/A'))))
                t.setItem(row_idx, 1, QTableWidgetItem(delivery.get("id_colis", 'N/A')))
                t.setItem(row_idx, 2, QTableWidgetItem(delivery.get("nom_destinataire", 'N/A')))
                t.setItem(row_idx, 3, QTableWidgetItem(delivery.get("adresse", 'N/A')))
                t.setItem(row_idx, 4, QTableWidgetItem(delivery["date_expedition"].toString('yyyy-MM-dd') if delivery.get("date_expedition") else 'N/A'))
                t.setItem(row_idx, 5, QTableWidgetItem(delivery["date_prevue"].toString('yyyy-MM-dd') if delivery.get("date_prevue") else 'N/A'))
                t.setItem(row_idx, 6, QTableWidgetItem(delivery["date_livree"].toString('yyyy-MM-dd') if delivery.get("date_livree") else 'N/A'))
                t.setItem(row_idx, 7, QTableWidgetItem(delivery.get("poids", 'N/A')))
                t.setItem(row_idx, 8, QTableWidgetItem(delivery.get("volume", 'N/A')))
                t.setItem(row_idx, 9, QTableWidgetItem(delivery.get("type", 'N/A')))
                t.setItem(row_idx, 10, QTableWidgetItem(delivery.get("instructions", 'N/A')))
                t.setItem(row_idx, 11, QTableWidgetItem(str(delivery.get("lat", 'N/A'))))
                t.setItem(row_idx, 12, QTableWidgetItem(str(delivery.get("lon", 'N/A'))))
                t.setItem(row_idx, 13, QTableWidgetItem(delivery.get("status", 'N/A')))
                t.setItem(row_idx, 14, QTableWidgetItem(delivery.get("telephone_destinataire", 'N/A')))
                t.setItem(row_idx, 15, QTableWidgetItem(f"{delivery.get('delivery_time_seconds', 0) / 60:.0f} min"))
                t.setItem(row_idx, 16, QTableWidgetItem(f"{delivery.get('distance_km', 0):.1f} km"))
                t.setItem(row_idx, 17, QTableWidgetItem("Oui" if delivery.get('on_time', False) else "Non"))


    def update_dashboard_stats(self):
        # Removed "Performances du jour" stats from the dashboard as per user request.
        # The following lines are commented out:
        # today = QDate.currentDate()
        # completed_data_dicts = self.completed_deliveries_data
        # completed_today = [
        #     d for d in completed_data_dicts
        #     if d.get("date_livree") and d["date_livree"] == today
        # ]
        # completed_today_count = len(completed_today)
        # total_delivery_time_seconds_today = sum(d.get("delivery_time_seconds", 0) for d in completed_today)
        # avg_time_minutes_today = (total_delivery_time_seconds_today / completed_today_count / 60) if completed_today_count > 0 else 0
        # total_distance_km_today = sum(d.get("distance_km", 0) for d in completed_today)
        # fuel_consumption_today = (total_distance_km_today / 10) if total_distance_km_today > 0 else 0 # Dummy calc
        # on_time_deliveries_count_today = sum(1 for d in completed_today if d.get("on_time", False))
        # on_time_rate_today = (on_time_deliveries_count_today / completed_today_count * 100) if completed_today_count > 0 else 0
        # self.avg_time_value_label.setText(f"{avg_time_minutes_today:.0f} min")
        # self.total_distance_value_label.setText(f"{total_distance_km_today:.1f} km")
        # self.fuel_consumption_value_label.setText(f"{fuel_consumption_today:.1f} L")
        # self.on_time_rate_value_label.setText(f"{on_time_rate_today:.1f}%")
        pass # No longer updating these stats on the dashboard


    def show_delivery_popup(self, delivery):
        msg = QMessageBox()
        msg.setWindowTitle(f"📦 Détails - Livraison {delivery['id_livraison']}")
        msg.setStyleSheet(f"""
            QMessageBox {{
                background: white;
                border-radius: 12px;
            }}
            QMessageBox QLabel {{
                color: {COLOR_TEXT_DARK};
                font-size: 14px;
            }}
            QMessageBox QPushButton {{
                background: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
                min-width: 120px;
            }}
            QMessageBox QPushButton:hover {{
                background: {COLOR_PRIMARY_DARK};
            }}
        """)

        info = f"""
        <div style='font-family: Segoe UI; line-height: 1.6;'>
            <h3 style='color: {COLOR_TEXT_DARK}; margin-top: 0;'>📦 {delivery['id_colis']}</h3>
            <p><strong>👤 Destinataire:</strong> {delivery['nom_destinataire']}</p>
            <p><strong>📍 Adresse:</strong> {delivery['adresse']}</p>
            <p><strong>⚖️ Poids:</strong> {delivery['poids']}</p>
            <p><strong>📏 Volume:</strong> {delivery['volume']}</p>
            <p><strong>📦 Type:</strong> {delivery['type']}</p>
            <p><strong>📝 Instructions:</strong> {delivery['instructions']}</p>
            <p><strong>🗓️ Date d'expédition:</strong> {delivery['date_expedition'].toString("dd/MM/yyyy") if delivery.get('date_expedition') else 'N/A'}</p>
            <p><strong>🗓️ Date prévue:</strong> {delivery['date_prevue'].toString("dd/MM/yyyy") if delivery.get('date_prevue') else 'N/A'}</p>
        </div>
        """

        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(info)
        
        # Create custom buttons for QMessageBox
        mark_complete_btn = None
        if delivery["status"] == "pending":
            mark_complete_btn = QPushButton("✅ Marquer comme livrée")
            mark_complete_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLOR_SUCCESS}; /* Green for success */
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 500;
                    min-width: 120px;
                }}
                QPushButton:hover {{
                    background: #3B823E; /* Darker green */
                }}
            """)
            msg.addButton(mark_complete_btn, QMessageBox.ButtonRole.AcceptRole)

        report_problem_btn = QPushButton("⚠️ Signaler un problème")
        report_problem_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_WARNING}; /* Orange for warning */
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background: #CC9900; /* Darker orange */
            }}
        """)
        msg.addButton(report_problem_btn, QMessageBox.ButtonRole.DestructiveRole) # Using DestructiveRole for problem reporting

        close_btn = QPushButton("❌ Fermer")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background: {COLOR_PRIMARY_DARK};
            }}
        """)
        msg.addButton(close_btn, QMessageBox.ButtonRole.RejectRole)

        msg.exec() # Show the message box and wait for user interaction

        # Handle button clicks
        if mark_complete_btn and msg.clickedButton() == mark_complete_btn:
            self.complete_delivery(delivery)
        elif msg.clickedButton() == report_problem_btn:
            self.show_report_issue_dialog() # Call new method for reporting issue

    def show_report_issue_dialog(self):
        dialog = ReportIssueDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            problem_description = dialog.get_problem_description()
            if problem_description.strip():
                QMessageBox.information(self, "Problème signalé", f"Votre problème a été signalé avec la description : \n\n'{problem_description}'\n\nNotre équipe vous contactera bientôt.")
            else:
                QMessageBox.warning(self, "Problème non signalé", "Vous n'avez pas saisi de description pour le problème.")
        else:
            QMessageBox.information(self, "Annulé", "Le signalement du problème a été annulé.")


    def complete_delivery(self, delivery):
        reply = QMessageBox.question(self, 'Confirmer la livraison',
                                     f"Voulez-vous marquer la livraison {delivery['id_livraison']} comme terminée ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = """
                UPDATE "SCA"."LivraisonConducteurColis"
                SET status = 'completed', date_livree = %s
                WHERE id_livraison = %s;
                """
                current_date = QDate.currentDate().toString("yyyy-MM-dd")
                self.db_manager.execute_query(query, (current_date, delivery["id_livraison"]))

                success_msg = QMessageBox()
                success_msg.setIcon(QMessageBox.Icon.Information)
                success_msg.setWindowTitle("✅ Livraison terminée")
                success_msg.setText("🎉 Livraison marquée comme terminée avec succès !")
                success_msg.setStyleSheet(f"""
                    QMessageBox {{
                        background: white;
                        border-radius: 12px;
                    }}
                    QMessageBox QPushButton {{
                        background: {COLOR_SUCCESS};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 8px 16px;
                        font-weight: 500;
                    }}
                """)
                success_msg.exec()

                self.load_all_deliveries_from_db() # Reload data to reflect changes
            except Exception as e:
                QMessageBox.critical(self, "Erreur de base de données", f"Échec de la mise à jour de la livraison : {e}")

    def update_counters(self):
        pass

    def search_deliveries(self):
        # This method is no longer used for a dedicated pending view,
        # but could be adapted if a search bar is added to the dialog.
        pass

    def update_driver_location_on_map(self):
        self.map_loading_label.show()
        QApplication.processEvents()

        try:
            location_query = """
            SELECT current_latitude, current_longitude
            FROM "SCA"."DriverLocations"
            WHERE idconducteur = %s;
            """
            location_data = self.db_manager.fetch_one(location_query, (self.driver_info["idconducteur"],))
            if location_data:
                # Corrected access to tuple elements
                self.driver_current_location = (float(location_data[0]), float(location_data[1]))
            else:
                self.driver_current_location = (4.05, 9.77) # Default to Douala, Cameroon

            # Simulate location movement for the driver in dummy data
            current_lat, current_lon = self.driver_current_location
            new_lat = current_lat + (random.uniform(-0.005, 0.005))
            new_lon = current_lon + (random.uniform(-0.005, 0.005))
            self.driver_current_location = (new_lat, new_lon)
            self.db_manager.execute_query(
                "UPDATE \"SCA\".\"DriverLocations\" SET current_latitude = %s, current_longitude = %s WHERE idconducteur = %s;",
                (new_lat, new_lon, self.driver_info["idconducteur"])
            )

        except Exception as e:
            QMessageBox.warning(self, "Erreur de localisation", f"Impossible de charger la position du conducteur : {e}. Utilisation d'une position par défaut.")
            self.driver_current_location = (4.05, 9.77)

        map_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Carte des Livraisons</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <style>
                body {{ margin: 0; padding: 0; }}
                #mapid {{ width: 100%; height: 100vh; border-radius: 12px; }}
            </style>
        </head>
        <body>
            <div id="mapid"></div>
            <script>
                var map = L.map('mapid').setView([{self.driver_current_location[0]}, {self.driver_current_location[1]}], 13);

                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }}).addTo(map);

                var allMarkers = [];

                // Driver's current location marker
                var driverLat = {self.driver_current_location[0]};
                var driverLon = {self.driver_current_location[1]};
                var driverMarker = L.marker([driverLat, driverLon], {{icon: L.divIcon({{className: 'custom-div-icon', html: '<div style="background-color: {COLOR_INFO}; width: 30px; height: 30px; border-radius: 50%; border: 2px solid white; display: flex; justify-content: center; align-items: center; color: white; font-weight: bold;">🚚</div>', iconSize: [30, 30], iconAnchor: [15, 30]}})}})
                    .addTo(map)
                    .bindPopup("<b>Votre position actuelle</b><br>Chauffeur: {self.driver_info['prenom']} {self.driver_info['nom']}");
                allMarkers.push(driverMarker);

                // Add markers for pending deliveries
                var pendingDeliveries = {json.dumps([
                    {"lat": d["lat"], "lon": d["lon"], "id": d["id_livraison"], "name": d["nom_destinataire"], "address": d["adresse"]}
                    for d in self.pending_deliveries_data
                    if d.get("lat") is not None and d.get("lon") is not None
                ])};
                pendingDeliveries.forEach(function(delivery) {{
                    var marker = L.marker([delivery.lat, delivery.lon], {{icon: L.divIcon({{className: 'custom-div-icon', html: '<div style="background-color: {COLOR_WARNING}; width: 24px; height: 24px; border-radius: 50%; border: 2px solid white; display: flex; justify-content: center; align-items: center; color: white; font-weight: bold;">🕒</div>', iconSize: [24, 24], iconAnchor: [12, 24]}})}})
                        .addTo(map)
                        .bindPopup("<b>Livraison en cours: " + delivery.id + "</b><br>" + delivery.name + "<br>" + delivery.address);
                    allMarkers.push(marker);
                }});

                // Add markers for completed deliveries
                var completedDeliveries = {json.dumps([
                    {"lat": d["lat"], "lon": d["lon"], "id": d["id_livraison"], "name": d["nom_destinataire"], "address": d["adresse"]}
                    for d in self.completed_deliveries_data
                    if d.get("lat") is not None and d.get("lon") is not None
                ])};
                completedDeliveries.forEach(function(delivery) {{
                    var marker = L.marker([delivery.lat, delivery.lon], {{icon: L.divIcon({{className: 'custom-div-icon', html: '<div style="background-color: {COLOR_SUCCESS}; width: 24px; height: 24px; border-radius: 50%; border: 2px solid white; display: flex; justify-content: center; align-items: center; color: white; font-weight: bold;">✅</div>', iconSize: [24, 24], iconAnchor: [12, 24]}})}})
                        .addTo(map)
                        .bindPopup("<b>Livraison terminée: " + delivery.id + "</b><br>" + delivery.name + "<br>" + delivery.address);
                    allMarkers.push(marker);
                }});

                if (allMarkers.length > 0) {{
                    var group = L.featureGroup(allMarkers);
                    map.fitBounds(group.getBounds().pad(0.1));
                }} else {{
                    map.setView([driverLat, driverLon], 13);
                }}
            </script>
        </body>
        </html>
        """
        self.map_view.setHtml(map_html)
        self.map_loading_label.hide()

    def change_view(self, index):
        self.content_stack.setCurrentIndex(index)
        self.load_all_deliveries_from_db()
        if index == 2: # Map view (new index)
            self.update_driver_location_on_map()
        elif index == 3: # Help view (new index)
            pass # No specific update needed for the simple help view

    def apply_modern_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLOR_BACKGROUND_LIGHT};
                color: {COLOR_TEXT_DARK};
                font-family: "Segoe UI", sans-serif;
            }}
            QLabel {{
                color: {COLOR_TEXT_DARK};
            }}
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_SECONDARY};
            }}
            QTableWidget {{
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: 12px;
                background-color: white;
            }}
            QHeaderView::section {{
                background-color: {COLOR_PRIMARY};
                color: white;
                padding: 5px;
                border: 1px solid {COLOR_PRIMARY_DARK};
            }}
            QMessageBox {{
                background-color: {COLOR_BACKGROUND_LIGHT};
                color: {COLOR_TEXT_DARK};
                font-family: "Segoe UI", sans-serif;
            }}
            QMessageBox QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: normal;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {COLOR_SECONDARY};
            }}
        """)

    def logout(self):
        reply = QMessageBox.question(self, 'Déconnexion',
                                     "Êtes-vous sûr de vouloir vous déconnecter ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, 'Déconnexion', "Vous avez été déconnecté.")
            self.close()
            QApplication.quit()

class LoginScreen(QWidget):
    """Écran de connexion pour l'application."""
    login_successful = pyqtSignal(dict) # Emits driver_info on successful login

    def __init__(self, db_manager_instance):
        super().__init__()
        self.db_manager = db_manager_instance
        self.setWindowTitle("SAC DeliveryPro- Connexion")
        self.setGeometry(500, 300, 400, 350)
        self.init_ui()
        self.apply_login_styles()

        self.login_loading_label = QLabel("Connexion en cours...", self)
        self.login_loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_loading_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.login_loading_label.setStyleSheet("color: white; padding: 10px;")
        self.login_loading_label.hide()
        self.layout().addWidget(self.login_loading_label)


    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        title = QLabel("🚚 DeliveryPro")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLOR_PRIMARY};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur (e.g., email du conducteur)")
        self.username_input.setMinimumHeight(40)
        self.username_input.setFont(QFont("Segoe UI", 11))
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe (e.g., password)")
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
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 {COLOR_PRIMARY_LIGHT}, stop:1 {COLOR_PRIMARY});
                border-radius: 20px;
            }}
            QLabel {{
                color: white;
            }}
            QLineEdit {{
                background: white;
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: 10px;
                padding: 10px 15px;
                color: {COLOR_TEXT_DARK};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_PRIMARY};
            }}
            QPushButton {{
                background: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {COLOR_PRIMARY_DARK};
            }}
        """)

    def attempt_login(self):
        entered_email = self.username_input.text()
        entered_password = self.password_input.text()

        self.login_loading_label.show()
        QApplication.processEvents()

        if entered_password == "password": # Universal password for dummy login
            try:
                driver_info = None
                # Try to fetch driver info from the dummy data using the entered email
                driver_info = self.db_manager.fetch_one(
                    "SELECT idconducteur, nom, prenom, telephone, email FROM Conducteur WHERE email = %s;",
                    (entered_email,)
                )
                
                if driver_info:
                    self.login_loading_label.hide()
                    QMessageBox.information(self, "Connexion Réussie", f"Bienvenue, {driver_info['prenom']}!")
                    self.login_successful.emit(driver_info)
                else:
                    self.login_loading_label.hide()
                    QMessageBox.warning(self, "Erreur de Connexion", "Conducteur non trouvé avec cet e-mail. Veuillez vérifier.")
            except Exception as e:
                self.login_loading_label.hide()
                QMessageBox.critical(self, "Erreur de base de données", f"Échec de la récupération des informations du conducteur : {e}")
        else:
            self.login_loading_label.hide()
            QMessageBox.warning(self, "Erreur de Connexion", "Mot de passe incorrect.")


# --- Logique principale de l'application (Point d'entrée) ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Directly initialize the InternalDummyDBManager
    db_manager = InternalDummyDBManager()
    
    # No need for connection test or dialog as it's always dummy and always connected
    print("Application démarrée en mode autonome (Dummy DB).")

    main_window = QMainWindow()
    login_screen = LoginScreen(db_manager)
    main_window.setCentralWidget(login_screen)
    main_window.resize(400, 350)
    main_window.show()

    def show_main_app(driver_info):
        driver_dashboard = DriverApp(driver_info, db_manager)
        main_window.setCentralWidget(driver_dashboard)
        main_window.setWindowState(Qt.WindowState.WindowMaximized)
        main_window.setMinimumSize(800, 600)
        main_window.show()

    login_screen.login_successful.connect(show_main_app)

    sys.exit(app.exec())
