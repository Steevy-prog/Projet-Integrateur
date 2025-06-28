# sge_transporteur/main.py

import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty

# Import des écrans
# Assurez-vous que ces fichiers Python existent dans le dossier 'screens'
from screens.login_screen import LoginScreen
from screens.dashboard_screen import DashboardScreen
from screens.delivery_screen import DeliveryScreen
from screens.driver_screen import DriverScreen
from screens.vehicle_screen import VehicleScreen
from screens.delivery_detail_screen import DeliveryDetailScreen # NOUVEL IMPORT

# Import du service API et de la configuration
from api_service import ApiService
from config import AppConfig

class SGETransporteurApp(App):
    token = StringProperty(None) # Pour stocker le JWT token
    sm = ObjectProperty(None) # Référence au ScreenManager
    api_service = ObjectProperty(None) # Instance du service API
    app_config = ObjectProperty(None) # Instance de la configuration de l'application

    def build(self):
        # Initialiser la configuration et le service API au démarrage de l'application
        self.app_config = AppConfig()
        self.api_service = ApiService(base_url="SIMULATION_MODE") # Utilisez SIMULATION_MODE pour le développement

        self.sm = ScreenManager()

        # Chargez tous les fichiers KV trouvés dans le dossier 'kv_files'
        kv_path = os.path.join(os.path.dirname(__file__), "kv_files")
        for kv_file in os.listdir(kv_path):
            if kv_file.endswith(".kv"):
                Builder.load_file(os.path.join(kv_path, kv_file))
                print(f"Chargement du fichier KV: {kv_file}")


        # Ajoutez tous les écrans au ScreenManager
        # Assurez-vous que les classes d'écran sont définies dans leurs fichiers respectifs
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(DeliveryScreen(name="delivery"))
        self.sm.add_widget(DriverScreen(name="driver"))
        self.sm.add_widget(VehicleScreen(name="vehicle"))
        self.sm.add_widget(DeliveryDetailScreen(name="delivery_details")) # AJOUT DE L'ÉCRAN DE DÉTAILS

        # Définir l'écran initial
        self.sm.current = "login"
        return self.sm

    def change_screen(self, screen_name):
        """Change l'écran affiché par le ScreenManager."""
        self.sm.current = screen_name

    def on_stop(self):
        """Appelée lorsque l'application est sur le point d'être arrêtée."""
        print("SGETransporteurApp: L'application est en cours de fermeture...")

if __name__ == "__main__":
    SGETransporteurApp().run()
