# sge_transporteur/screens/vehicle_screen.py

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.uix.recycleview import RecycleView

# Nouvelle classe Python pour chaque élément de la liste des véhicules
class VehicleListItem(BoxLayout):
    # Propriétés de Kivy qui seront mises à jour par les données de la RecycleView
    id_text = StringProperty('')
    plate_text = StringProperty('')
    type_text = StringProperty('')
    capacity_text = StringProperty('')
    status_text = StringProperty('')
    driver_text = StringProperty('')
    item_status_color = ListProperty([0,0,0,1]) # Couleur du texte de statut, calculée dans Python
    item_border_color = ListProperty([0,0,0,1]) # Nouvelle propriété pour la couleur de la bordure, calculée dans Python
    
    # Propriétés pour les couleurs et tailles de la configuration, passées pour éviter les appels App.get_running_app()
    font_size_md = dp(16)
    font_size_sm = dp(14)
    text_dark_color = ListProperty([0.2,0.2,0.2,1])
    text_muted_color = ListProperty([0.5,0.5,0.5,1])
    padding_small = dp(10)
    spacing_small = dp(10)
    corner_radius_sm = dp(5)
    background_card_color = ListProperty([1,1,1,1])
    card_border_dark_color = ListProperty([0.8,0.8,0.8,1])
    accent_color = ListProperty([0.98,0.75,0.04,1])


class VehicleScreen(Screen):
    # Propriété pour le statut de chargement de la page Véhicules
    vehicle_status_message = StringProperty("Chargement des véhicules...")
    vehicle_status_color = ObjectProperty([0.2, 0.5, 0.8, 1]) # Couleur bleue (info)

    # Propriété pour les données de la RecycleView
    vehicles_data = ListProperty([])

    def __init__(self, **kw):
        super().__init__(**kw)
        app = App.get_running_app()
        if app and app.app_config:
            self.vehicle_status_color = app.app_config.COLOR_INFO
        else:
            self.vehicle_status_color = [0.2, 0.5, 0.8, 1]

    def on_enter(self, *args):
        """Appelée lorsque l'écran des véhicules devient actif."""
        print("VehicleScreen: Entrée sur l'écran des Véhicules.")
        self.load_vehicles_data()

    def load_vehicles_data(self):
        """Déclenche l'appel à l'API pour charger les données des véhicules."""
        app = App.get_running_app()
        if not app.token:
            self.update_vehicle_status("Non connecté. Retour au login.", "error")
            Clock.schedule_once(lambda dt: app.change_screen("login"), 2)
            return

        self.update_vehicle_status("Chargement des données des véhicules...", "info")
        # Lancer l'appel API dans un thread séparé ou via Clock.schedule_once pour ne pas bloquer l'UI
        Clock.schedule_once(lambda dt: self._perform_vehicles_api_call(app.token), 0.1)

    def _perform_vehicles_api_call(self, token):
        """Exécute l'appel réel au service API pour les véhicules."""
        app = App.get_running_app()
        response = app.api_service.get_vehicles(token)

        if response.get("success"):
            data = response.get("data", [])
            self.update_vehicles_ui(data)
            self.update_vehicle_status("Données des véhicules mises à jour.", "success")
            print("VehicleScreen: Données des véhicules chargées avec succès.")
        else:
            message = response.get("message", "Échec du chargement des données des véhicules.")
            self.update_vehicle_status(message, "error")
            print(f"VehicleScreen: Erreur de chargement des données: {message}")
            if "token" in message.lower() or "authentification" in message.lower():
                Clock.schedule_once(lambda dt: app.change_screen("login"), 2)

    @mainthread
    def update_vehicles_ui(self, data):
        """
        Met à jour l'interface utilisateur avec les données des véhicules reçues de l'API.
        Formate les données pour la RecycleView.
        """
        app_config = App.get_running_app().app_config
        formatted_data = []

        if not data:
            formatted_data.append({
                'text': "Aucun véhicule trouvé.",
                'color': app_config.COLOR_TEXT_MUTED,
                'font_size': app_config.FONT_SIZE_MD,
                'halign': 'center',
                'valign': 'middle',
                'size_hint_y': None,
                'height': dp(50),
                # Add default values for VehicleListItem properties
                'id_text': '', 'plate_text': '', 'type_text': '', 'capacity_text': '', 'status_text': '', 'driver_text': '',
                'item_status_color': app_config.COLOR_TEXT_MUTED,
                'item_border_color': app_config.COLOR_BACKGROUND_CARD, # Neutral border
                'background_card_color': app_config.COLOR_BACKGROUND_CARD,
                'card_border_dark_color': app_config.COLOR_CARD_BORDER_DARK,
                'accent_color': app_config.COLOR_ACCENT,
                'font_size_md': app_config.FONT_SIZE_MD,
                'font_size_sm': app_config.FONT_SIZE_SM,
                'text_dark_color': app_config.COLOR_TEXT_DARK,
                'text_muted_color': app_config.COLOR_TEXT_MUTED,
                'padding_small': app_config.PADDING_SMALL,
                'spacing_small': app_config.SPACING_SMALL,
                'corner_radius_sm': app_config.CORNER_RADIUS_SM,
            })
        else:
            for item in data:
                status_text = item.get('status', 'Inconnu')
                status_color = app_config.COLOR_TEXT_DARK # Default color for status text
                border_color = app_config.COLOR_BACKGROUND_CARD # Default border color

                if "disponible" in status_text.lower():
                    status_color = app_config.COLOR_SUCCESS
                    border_color = app_config.COLOR_SUCCESS
                elif "en mission" in status_text.lower():
                    status_color = app_config.COLOR_INFO
                    border_color = app_config.COLOR_INFO
                elif "en maintenance" in status_text.lower():
                    status_color = app_config.COLOR_WARNING
                    border_color = app_config.COLOR_WARNING
                elif "hors service" in status_text.lower():
                    status_color = app_config.COLOR_ERROR
                    border_color = app_config.COLOR_ERROR

                formatted_data.append({
                    'id_text': f"ID: {item.get('id', 'N/A')}",
                    'plate_text': f"Immat.: {item.get('plate', 'N/A')}",
                    'type_text': f"Type: {item.get('type', 'N/A')}",
                    'capacity_text': f"Capacité: {item.get('capacity', 'N/A')}",
                    'status_text': f"Statut: {status_text}",
                    'driver_text': f"Chauffeur: {item.get('driver', 'N/A')}",
                    'item_status_color': status_color, # Property for status text color
                    'item_border_color': border_color, # Property for item border color
                    
                    # Transfer AppConfig properties to RecycleView items
                    'font_size_md': app_config.FONT_SIZE_MD,
                    'font_size_sm': app_config.FONT_SIZE_SM,
                    'text_dark_color': app_config.COLOR_TEXT_DARK,
                    'text_muted_color': app_config.COLOR_TEXT_MUTED,
                    'padding_small': app_config.PADDING_SMALL,
                    'spacing_small': app_config.SPACING_SMALL,
                    'corner_radius_sm': app_config.CORNER_RADIUS_SM,
                    'background_card_color': app_config.COLOR_BACKGROUND_CARD,
                    'card_border_dark_color': app_config.COLOR_CARD_BORDER_DARK,
                    'accent_color': app_config.COLOR_ACCENT,
                })
        self.vehicles_data = formatted_data
        print(f"VehicleScreen: UI updated with {len(data)} vehicles.")

    @mainthread
    def update_vehicle_status(self, message, msg_type="info"):
        """
        Updates the vehicle page status message and its color.
        """
        app_config = App.get_running_app().app_config
        self.vehicle_status_message = message
        if msg_type == "error":
            self.vehicle_status_color = app_config.COLOR_ERROR
        elif msg_type == "success":
            self.vehicle_status_color = app_config.COLOR_SUCCESS
        elif msg_type == "info":
            self.vehicle_status_color = app_config.COLOR_INFO
        else:
            self.vehicle_status_color = app_config.COLOR_TEXT_MUTED
