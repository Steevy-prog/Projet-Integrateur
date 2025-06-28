# sge_transporteur/screens/delivery_screen.py

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.uix.recycleview import RecycleView
from kivy.uix.behaviors import ButtonBehavior # Import nécessaire pour rendre les éléments cliquables

# Nouvelle classe Python pour chaque élément de la liste des livraisons
class DeliveryListItem(ButtonBehavior, BoxLayout):
    # Full delivery data object (dict from API), set by RecycleView's data
    delivery_data = ObjectProperty(None)

    # Propriétés individuelles dérivées de delivery_data pour l'affichage dans le KV
    # Ces StringProperty sont mises à jour dans on_delivery_data
    id_text = StringProperty('')
    client_text = StringProperty('')
    destination_text = StringProperty('')
    status_text = StringProperty('')
    driver_text = StringProperty('')
    vehicle_text = StringProperty('')

    # Propriétés calculées pour le style (couleurs des bordures/statuts), mises à jour dans on_delivery_data
    item_status_color = ListProperty([0,0,0,1])
    item_border_color = ListProperty([0,0,0,1])
    
    # Propriétés passées depuis AppConfig pour éviter des appels répétitifs à App.get_running_app()
    # Ces valeurs seront injectées par le `data` du RecycleView
    font_size_md = ObjectProperty(dp(16))
    font_size_sm = ObjectProperty(dp(14))
    text_dark_color = ListProperty([0.2,0.2,0.2,1])
    text_muted_color = ListProperty([0.5,0.5,0.5,1])
    padding_small = ObjectProperty(dp(10))
    spacing_small = ObjectProperty(dp(10))
    corner_radius_sm = ObjectProperty(dp(5))
    background_card_color = ListProperty([1,1,1,1])
    card_border_dark_color = ListProperty([0.8,0.8,0.8,1])
    accent_color = ListProperty([0.98,0.75,0.04,1])


    def on_delivery_data(self, instance, value):
        """
        Met à jour les propriétés du widget lorsque de nouvelles données de livraison sont définies.
        Cette méthode est cruciale car `delivery_data` est le seul élément directement mappé par la RecycleView.
        """
        if value:
            app = App.get_running_app()
            app_config = app.app_config if app else None

            # Assurez-vous que app_config est disponible avant d'essayer d'accéder à ses propriétés
            if app_config:
                self.id_text = f"ID: {value.get('id', 'N/A')}"
                self.client_text = f"Client: {value.get('client', 'N/A')}"
                self.destination_text = f"Dest.: {value.get('address', 'N/A')}" # Utilise 'address' pour la destination
                self.status_text = f"Statut: {value.get('status', 'Inconnu')}"
                self.driver_text = f"Chauffeur: {value.get('driver', 'N/A')}"
                self.vehicle_text = f"Véhicule: {value.get('vehicle', 'N/A')}"

                # Calculer les couleurs en fonction du statut
                current_status = value.get('status', 'Inconnu').lower()
                if "livré" in current_status:
                    self.item_status_color = app_config.COLOR_SUCCESS
                    self.item_border_color = app_config.COLOR_SUCCESS
                elif "en transit" in current_status:
                    self.item_status_color = app_config.COLOR_INFO
                    self.item_border_color = app_config.COLOR_INFO
                elif "attente" in current_status:
                    self.item_status_color = app_config.COLOR_WARNING
                    self.item_border_color = app_config.COLOR_WARNING
                elif "annulé" in current_status:
                    self.item_status_color = app_config.COLOR_ERROR
                    self.item_border_color = app_config.COLOR_ERROR
                elif "chargé" in current_status: # Nouveau statut pour la bordure
                    self.item_status_color = app_config.COLOR_PRIMARY
                    self.item_border_color = app_config.COLOR_PRIMARY
                elif "arrivé" in current_status: # Nouveau statut pour la bordure
                    self.item_status_color = app_config.COLOR_ACCENT
                    self.item_border_color = app_config.COLOR_ACCENT
                else:
                    self.item_status_color = app_config.COLOR_TEXT_DARK
                    self.item_border_color = app_config.COLOR_CARD_BORDER_DARK # Couleur de bordure par défaut
                
                # Assurez-vous que les propriétés de style sont bien définies même si on_delivery_data est appelé tard
                self.font_size_md = app_config.FONT_SIZE_MD
                self.font_size_sm = app_config.FONT_SIZE_SM
                self.text_dark_color = app_config.COLOR_TEXT_DARK
                self.text_muted_color = app_config.COLOR_TEXT_MUTED
                self.padding_small = app_config.PADDING_SMALL
                self.spacing_small = app_config.SPACING_SMALL
                self.corner_radius_sm = app_config.CORNER_RADIUS_SM
                self.background_card_color = app_config.COLOR_BACKGROUND_CARD
                self.card_border_dark_color = app_config.COLOR_CARD_BORDER_DARK
                self.accent_color = app_config.COLOR_ACCENT
            else:
                # Fallback pour les couleurs et tailles si app_config n'est pas prêt
                self.item_status_color = [0,0,0,1]
                self.item_border_color = [0.8,0.8,0.8,1]
                self.font_size_md = dp(16)
                self.font_size_sm = dp(14)
                self.text_dark_color = [0.2,0.2,0.2,1]
                self.text_muted_color = [0.5,0.5,0.5,1]
                self.padding_small = dp(10)
                self.spacing_small = dp(10)
                self.corner_radius_sm = dp(5)
                self.background_card_color = [1,1,1,1]
                self.card_border_dark_color = [0.8,0.8,0.8,1]
                self.accent_color = [0.98,0.75,0.04,1]
        else:
            # Réinitialiser si delivery_data est None
            self.id_text = "Aucune livraison trouvée."
            self.client_text = self.destination_text = self.status_text = self.driver_text = self.vehicle_text = ''
            self.item_status_color = self.text_muted_color
            self.item_border_color = self.background_card_color


class DeliveryScreen(Screen):
    # Propriété pour le statut de chargement de la page Livraisons
    delivery_status_message = StringProperty("Chargement des livraisons...")
    delivery_status_color = ObjectProperty([0.2, 0.5, 0.8, 1]) # Couleur bleue (info)

    # Propriété pour les données de la RecycleView
    deliveries_data = ListProperty([])

    def __init__(self, **kw):
        super().__init__(**kw)
        app = App.get_running_app()
        if app and app.app_config:
            self.delivery_status_color = app.app_config.COLOR_INFO
        else:
            self.delivery_status_color = [0.2, 0.5, 0.8, 1]

    def on_enter(self, *args):
        """Appelée lorsque l'écran des livraisons devient actif."""
        print("DeliveryScreen: Entrée sur l'écran des Livraisons.")
        self.load_deliveries_data()

    def load_deliveries_data(self):
        """Déclenche l'appel à l'API pour charger les données de livraisons."""
        app = App.get_running_app()
        if not app.token:
            self.update_delivery_status("Non connecté. Retour au login.", "error")
            Clock.schedule_once(lambda dt: app.change_screen("login"), 2)
            return

        self.update_delivery_status("Chargement des données de livraisons...", "info")
        # Lancer l'appel API dans un thread séparé ou via Clock.schedule_once pour ne pas bloquer l'UI
        Clock.schedule_once(lambda dt: self._perform_deliveries_api_call(app.token), 0.1)

    def _perform_deliveries_api_call(self, token):
        """Exécute l'appel réel au service API pour les livraisons."""
        app = App.get_running_app()
        response = app.api_service.get_deliveries(token)

        if response.get("success"):
            data = response.get("data", [])
            self.update_deliveries_ui(data)
            self.update_delivery_status("Données des livraisons mises à jour.", "success")
            print("DeliveryScreen: Données des livraisons chargées avec succès.")
        else:
            message = response.get("message", "Échec du chargement des données des livraisons.")
            self.update_delivery_status(message, "error")
            print(f"DeliveryScreen: Erreur de chargement des données: {message}")
            if "token" in message.lower() or "authentification" in message.lower():
                Clock.schedule_once(lambda dt: app.change_screen("login"), 2)

    @mainthread
    def update_deliveries_ui(self, data):
        """
        Met à jour l'interface utilisateur avec les données de livraisons reçues de l'API.
        Formate les données pour la RecycleView en passant l'objet de données complet.
        """
        app = App.get_running_app()
        app_config = app.app_config if app else None

        formatted_data = []
        if not data:
            # Si aucune donnée, ajoutez un élément factice pour afficher un message
            formatted_data.append({
                'delivery_data': None, # Aucune donnée réelle de livraison
                # Les propriétés de style doivent être passées directement si delivery_data est None
                # pour que DeliveryListItem puisse afficher le message "Aucune livraison trouvée."
                'font_size_md': app_config.FONT_SIZE_MD if app_config else dp(16),
                'text_muted_color': app_config.COLOR_TEXT_MUTED if app_config else [0.5,0.5,0.5,1],
                'background_card_color': app_config.COLOR_BACKGROUND_CARD if app_config else [1,1,1,1],
                'card_border_dark_color': app_config.COLOR_CARD_BORDER_DARK if app_config else [0.8,0.8,0.8,1],
                'padding_small': app_config.PADDING_SMALL if app_config else dp(10),
                'spacing_small': app_config.SPACING_SMALL if app_config else dp(10),
                'corner_radius_sm': app_config.CORNER_RADIUS_SM if app_config else dp(5),
            })
        else:
            for item in data:
                # Chaque élément de `data` du RecycleView est un dictionnaire
                # contenant la propriété `delivery_data` et toutes les propriétés de style nécessaires.
                formatted_data.append({
                    'delivery_data': item, # Passe l'objet de données complet de la livraison
                    # Passez ici toutes les propriétés de AppConfig que DeliveryListItem utilise
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
        self.deliveries_data = formatted_data
        print(f"DeliveryScreen: UI mise à jour avec {len(data)} livraisons.")

    @mainthread
    def update_delivery_status(self, message, msg_type="info"):
        """
        Met à jour le message de statut de la page livraisons et sa couleur.
        """
        app_config = App.get_running_app().app_config
        self.delivery_status_message = message
        if msg_type == "error":
            self.delivery_status_color = app_config.COLOR_ERROR
        elif msg_type == "success":
            self.delivery_status_color = app_config.COLOR_SUCCESS
        elif msg_type == "info":
            self.delivery_status_color = app_config.COLOR_INFO
        else:
            self.delivery_status_color = app_config.COLOR_TEXT_MUTED

    def show_delivery_details(self, delivery_data):
        """
        Navigue vers l'écran de détails de livraison en passant les données de la livraison.
        Appelée par l'événement on_release de DeliveryListItem.
        """
        app = App.get_running_app()
        # Vérifiez que l'écran existe dans le ScreenManager avant de tenter d'y accéder
        if app.sm.has_screen('delivery_details'): # <-- CORRECTION DU NOM DE L'ÉCRAN ICI
            detail_screen = app.sm.get_screen('delivery_details') # <-- CORRECTION DU NOM DE L'ÉCRAN ICI
            detail_screen.delivery_data = delivery_data # Passe les données complètes de la livraison
            app.change_screen('delivery_details') # <-- CORRECTION DU NOM DE L'ÉCRAN ICI
        else:
            print("Erreur: L'écran 'delivery_details' n'est pas trouvé dans le ScreenManager.")
            self.update_delivery_status("Erreur: Écran de détails introuvable.", "error")
