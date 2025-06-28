# sge_transporteur/screens/login_screen.py (PLACEHOLDER)
# ATTENTION: Vous avez fourni le code de dashboard_screen.py pour login_screen.py.
# Remplacez ce contenu par votre VRAI code d'écran de connexion.
# Ce code est un minimum pour éviter une erreur ModuleNotFoundError.

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty
from kivy.app import App
from kivy.clock import Clock
from threading import Thread # Pour les opérations non bloquantes

class LoginScreen(Screen):
    login_status_message = StringProperty("Veuillez vous connecter")
    login_status_color = ObjectProperty([0, 0.5, 1, 1]) # Bleu pour info

    def __init__(self, **kw):
        super().__init__(**kw)
        app = App.get_running_app()
        if app and app.app_config:
            self.login_status_color = app.app_config.COLOR_INFO

    def on_enter(self, *args):
        # Réinitialise le message de statut lors de l'entrée sur l'écran
        app = App.get_running_app()
        if app and app.app_config:
            self.login_status_message = "Veuillez vous connecter"
            self.login_status_color = app.app_config.COLOR_INFO
        else:
            self.login_status_message = "Prêt à se connecter"
            self.login_status_color = [0, 0.5, 1, 1] # Fallback
        # Assurez-vous que les champs de saisie sont clairs à l'entrée
        if self.ids.get('username_input'):
            self.ids.username_input.text = ''
        if self.ids.get('password_input'):
            self.ids.password_input.text = ''

    def attempt_login(self, username, password):
        """Lance l'authentification dans un thread séparé pour ne pas bloquer l'UI."""
        self.login_status_message = "Connexion en cours..."
        app_config = App.get_running_app().app_config
        self.login_status_color = app_config.COLOR_INFO # Bleu pour le statut "en cours"

        # Lancer la logique de connexion dans un thread séparé
        Thread(target=self._perform_login_api_call, args=(username, password, app_config)).start()

    def _perform_login_api_call(self, username, password, app_config):
        """Effectue l'appel à l'API de connexion."""
        app = App.get_running_app()
        response = app.api_service.login(username, password)

        if response.get("success"):
            app.token = response.get("token")
            # Utilise Clock.schedule_once pour changer l'UI depuis le thread principal
            Clock.schedule_once(lambda dt: self._on_login_success(response.get("message"), app_config), 0)
        else:
            message = response.get("message", "Erreur de connexion inconnue.")
            Clock.schedule_once(lambda dt: self._on_login_failure(message, app_config), 0)

    def _on_login_success(self, message, app_config):
        """Mise à jour de l'UI en cas de succès de connexion."""
        self.login_status_message = message
        self.login_status_color = app_config.COLOR_SUCCESS
        App.get_running_app().change_screen("dashboard")
        print("LoginScreen: Connexion réussie, redirection vers le dashboard.")

    def _on_login_failure(self, message, app_config):
        """Mise à jour de l'UI en cas d'échec de connexion."""
        self.login_status_message = message
        self.login_status_color = app_config.COLOR_ERROR
        print(f"LoginScreen: Échec de connexion: {message}")

