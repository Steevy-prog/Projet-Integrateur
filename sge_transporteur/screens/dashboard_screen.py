# sge_transporteur/screens/dashboard_screen.py

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

# Importez le dialogue de déconnexion que nous allons créer
# Assurez-vous que logout_dialog.py existe dans le dossier screens
from screens.logout_dialog import LogoutConfirmPopup

# Définition du widget personnalisé DashboardStatCard
# C'est une classe Python qui correspond à la règle KV <DashboardStatCard@BoxLayout>
class DashboardStatCard(BoxLayout):
    card_color = ListProperty([1, 1, 1, 1])
    card_border_color = ListProperty([0.0, 0.25, 0.7, 1])
    title = StringProperty('')
    value = StringProperty('')
    icon_source = StringProperty('')

class DashboardScreen(Screen):
    # Propriétés Kivy pour afficher les données du tableau de bord
    active_deliveries_count = StringProperty("0")
    pending_deliveries_count = StringProperty("0")
    vehicles_available_count = StringProperty("0")
    drivers_on_duty_count = StringProperty("0")

    dashboard_status_message = StringProperty("Chargement des données...")
    dashboard_status_color = ObjectProperty([0.2, 0.5, 0.8, 1]) # Couleur par défaut (info)

    def __init__(self, **kw):
        super().__init__(**kw)
        # Initialisation des propriétés avec des valeurs par défaut
        self.active_deliveries_count = "0"
        self.pending_deliveries_count = "0"
        self.vehicles_available_count = "0"
        self.drivers_on_duty_count = "0"
        self.dashboard_status_message = "Bienvenue sur votre Tableau de Bord !"
        
        # Tenter d'obtenir la configuration pour la couleur initiale du statut
        app = App.get_running_app()
        if app and app.app_config: # Vérifiez que app et app_config sont initialisés
            self.dashboard_status_color = app.app_config.COLOR_INFO
        else:
            # Fallback si app_config n'est pas encore prêt (devrait être rare)
            self.dashboard_status_color = [0.2, 0.5, 0.8, 1]

    def on_enter(self, *args):
        """Appelée lorsque l'écran du tableau de bord devient actif."""
        print("DashboardScreen: Entrée sur l'écran du tableau de bord.")
        # Lancer le chargement des données
        self.load_dashboard_data()

    def load_dashboard_data(self):
        """Déclenche l'appel à l'API pour charger les données du tableau de bord."""
        app = App.get_running_app()
        if not app.token:
            # Si pas de token, afficher un message d'erreur et retourner à l'écran de connexion
            self.update_dashboard_status("Non connecté. Retour au login.", "error")
            Clock.schedule_once(lambda dt: app.change_screen("login"), 2) # Retour au login après 2s
            return

        self.update_dashboard_status("Chargement des données du dashboard...", "info")
        # Planifier l'appel API sur le thread principal pour éviter les problèmes de threading Kivy
        Clock.schedule_once(lambda dt: self._perform_dashboard_api_call(app.token), 0.1)

    def _perform_dashboard_api_call(self, token):
        """Exécute l'appel réel au service API."""
        app = App.get_running_app()
        response = app.api_service.get_dashboard_data(token)

        if response.get("success"):
            data = response.get("data", {})
            self.update_dashboard_ui(data) # Mettre à jour l'UI avec les données
            self.update_dashboard_status("Données du dashboard mises à jour.", "success")
            print("DashboardScreen: Données du dashboard chargées avec succès.")
        else:
            message = response.get("message", "Échec du chargement des données du dashboard.")
            self.update_dashboard_status(message, "error")
            print(f"DashboardScreen: Erreur de chargement des données: {message}")
            # Si l'erreur est liée au token, rediriger vers l'écran de connexion
            if "token" in message.lower() or "authentification" in message.lower():
                Clock.schedule_once(lambda dt: app.change_screen("login"), 2)

    @mainthread
    def update_dashboard_ui(self, data):
        """
        Met à jour l'interface utilisateur avec les données reçues de l'API.
        Cette méthode doit être appelée depuis le thread principal de Kivy (via @mainthread ou Clock.schedule_once).
        """
        self.active_deliveries_count = str(data.get("active_deliveries", 0))
        self.pending_deliveries_count = str(data.get("pending_deliveries", 0))
        self.vehicles_available_count = str(data.get("available_vehicles", 0))
        self.drivers_on_duty_count = str(data.get("drivers_on_duty", 0))

        # Mettre à jour la liste des activités récentes
        if self.ids.get('recent_activities_container'): # Utilisez .get() pour éviter KeyError si l'ID n'est pas encore prêt
            self.ids.recent_activities_container.clear_widgets()
            app_config = App.get_running_app().app_config
            recent_activities = data.get("recent_activities", [])

            if not recent_activities:
                self.ids.recent_activities_container.add_widget(
                    Label(text="Aucune activité récente.",
                          color=app_config.COLOR_TEXT_MUTED,
                          font_size=app_config.FONT_SIZE_SM,
                          size_hint_y=None, height=dp(30),
                          halign='left', valign='middle',
                          text_size=(self.ids.recent_activities_container.width * 0.9, None))
                )
            else:
                for activity in recent_activities:
                    time_str = activity.get("time", "N/A")
                    status = activity.get("status", "Inconnu")
                    delivery_id = activity.get("delivery_id", "N/A")
                    destination = activity.get("destination", "N/A")

                    activity_color_rgba = app_config.COLOR_TEXT_DARK
                    if "livré" in status.lower() or "terminé" in status.lower():
                        activity_color_rgba = app_config.COLOR_SUCCESS
                    elif "en transit" in status.lower() or "actif" in status.lower():
                        activity_color_rgba = app_config.COLOR_INFO
                    elif "attente" in status.lower() or "pending" in status.lower():
                        activity_color_rgba = app_config.COLOR_WARNING
                    elif "annulé" in status.lower():
                        activity_color_rgba = app_config.COLOR_ERROR

                    activity_color_hex = app_config.rgba_to_hex(activity_color_rgba)

                    # CONVERTIR FONT_SIZE_SM EN ENTIER POUR LE MARKUP [size=...]
                    # dp() renvoie un float, mais [size=...] a besoin d'un entier
                    font_size_for_markup = int(app_config.FONT_SIZE_SM)

                    self.ids.recent_activities_container.add_widget(
                        Label(
                            text=f"[b]{time_str}[/b] - {status} [color={activity_color_hex}][size={font_size_for_markup}]{delivery_id}[/size][/color] : {destination}",
                            color=app_config.COLOR_TEXT_DARK, 
                            font_size=app_config.FONT_SIZE_MD, # Ceci est le font_size normal du Label, peut rester float
                            size_hint_y=None,
                            height=dp(40),
                            text_size=(self.ids.recent_activities_container.width * 0.9, None), # S'adapte à la largeur du conteneur
                            halign='left',
                            valign='middle',
                            markup=True # Active le support du Kivy Text Markup
                        )
                    )
                
            print(f"Dashboard data updated: "
                  f"Active: {self.active_deliveries_count}, "
                  f"Pending: {self.pending_deliveries_count}, "
                  f"Vehicles: {self.vehicles_available_count}, "
                  f"Drivers: {self.drivers_on_duty_count}")
            print("DashboardScreen: UI mise à jour avec les dernières données.")
        else:
            print("DashboardScreen: 'recent_activities_container' ID non disponible. Attendez le chargement du KV ou vérifiez l'ID.")

    @mainthread
    def update_dashboard_status(self, message, msg_type="info"):
        """
        Met à jour le message de statut du tableau de bord et sa couleur.
        """
        app_config = App.get_running_app().app_config
        self.dashboard_status_message = message
        if msg_type == "error":
            self.dashboard_status_color = app_config.COLOR_ERROR
        elif msg_type == "success":
            self.dashboard_status_color = app_config.COLOR_SUCCESS
        elif msg_type == "info":
            self.dashboard_status_color = app_config.COLOR_INFO
        else:
            self.dashboard_status_color = app_config.COLOR_TEXT_MUTED

    def show_logout_dialog(self):
        """Affiche le popup de confirmation de déconnexion."""
        app = App.get_running_app()
        popup = LogoutConfirmPopup() # S'assure que LogoutConfirmPopup est importé
        popup.bind(on_dismiss=self.on_logout_dialog_dismiss)
        popup.open()

    def on_logout_dialog_dismiss(self, instance):
        """Gère la réponse du popup de déconnexion."""
        if instance.result == 'yes':
            self.do_logout()

    def do_logout(self):
        """Exécute la logique de déconnexion."""
        app = App.get_running_app()
        app.token = None # Efface le token
        app.change_screen("login") # Retourne à l'écran de connexion
        print("Déconnexion réussie.")

    def navigate_to_screen(self, screen_name):
        """Navigue vers un écran spécifié."""
        app = App.get_running_app()
        app.change_screen(screen_name)
