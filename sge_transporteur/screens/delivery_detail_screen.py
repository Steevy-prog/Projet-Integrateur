# sge_transporteur/screens/delivery_detail_screen.py

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import mainthread, Clock
from datetime import datetime # Pour horodatage
from kivy.uix.label import Label # <-- AJOUT DE CETTE LIGNE

class DeliveryDetailScreen(Screen):
    # Propriété pour les données complètes de la livraison
    delivery_data = ObjectProperty(None)

    # Propriétés individuelles pour l'affichage dans le KV
    delivery_id = StringProperty("N/A")
    client_name = StringProperty("N/A")
    destination_address = StringProperty("N/A")
    current_status = StringProperty("N/A")
    driver_assigned = StringProperty("N/A")
    vehicle_assigned = StringProperty("N/A")
    contact_info = StringProperty("N/A")
    items_description = StringProperty("N/A")
    
    # Propriétés pour gérer l'état des boutons d'action
    can_load = ObjectProperty(False)
    can_depart = ObjectProperty(False)
    can_arrive = ObjectProperty(False)
    can_deliver = ObjectProperty(False)

    # Propriété pour le message de statut de l'écran de détails
    detail_status_message = StringProperty("")
    detail_status_color = ListProperty([0.2, 0.5, 0.8, 1]) # Bleu (info)

    def __init__(self, **kw):
        super().__init__(**kw)
        app = App.get_running_app()
        if app and app.app_config:
            self.detail_status_color = app.app_config.COLOR_INFO

    def on_enter(self, *args):
        """Initialise l'écran lorsque l'on y entre."""
        print(f"DeliveryDetailScreen: Entrée avec données: {self.delivery_data}")
        self.update_ui_with_delivery_data()
        self.update_detail_status("Détails de la livraison chargés.")

    def update_ui_with_delivery_data(self):
        """Met à jour les propriétés de l'écran avec les données de la livraison."""
        if self.delivery_data:
            self.delivery_id = self.delivery_data.get('id', 'N/A')
            self.client_name = self.delivery_data.get('client', 'N/A')
            self.destination_address = self.delivery_data.get('address', 'N/A')
            self.current_status = self.delivery_data.get('status', 'N/A')
            self.driver_assigned = self.delivery_data.get('driver', 'N/A')
            self.vehicle_assigned = self.delivery_data.get('vehicle', 'N/A')
            self.contact_info = self.delivery_data.get('contact', 'N/A')
            self.items_description = self.delivery_data.get('items', 'N/A')

            # Mettre à jour l'état des boutons basé sur les données de l'API
            self.can_load = self.delivery_data.get('can_load', False)
            self.can_depart = self.delivery_data.get('can_depart', False)
            self.can_arrive = self.delivery_data.get('can_arrive', False)
            self.can_deliver = self.delivery_data.get('can_deliver', False)

            # Mettre à jour l'historique des statuts
            self.update_status_history_ui(self.delivery_data.get('history', []))
        else:
            self.update_detail_status("Aucune donnée de livraison à afficher.", "error")
            self.clear_ui()

    def clear_ui(self):
        """Réinitialise toutes les propriétés de l'UI."""
        self.delivery_id = "N/A"
        self.client_name = "N/A"
        self.destination_address = "N/A"
        self.current_status = "N/A"
        self.driver_assigned = "N/A"
        self.vehicle_assigned = "N/A"
        self.contact_info = "N/A"
        self.items_description = "N/A"
        self.can_load = False
        self.can_depart = False
        self.can_arrive = False
        self.can_deliver = False
        if self.ids.get('status_history_container'):
            self.ids.status_history_container.clear_widgets()

    @mainthread
    def update_status_history_ui(self, history_data):
        """Met à jour le BoxLayout affichant l'historique des statuts."""
        if self.ids.get('status_history_container'):
            self.ids.status_history_container.clear_widgets()
            app_config = App.get_running_app().app_config

            if not history_data:
                self.ids.status_history_container.add_widget(
                    Label(text="Aucun historique de statut.",
                          color=app_config.COLOR_TEXT_MUTED,
                          font_size=app_config.FONT_SIZE_SM,
                          size_hint_y=None, height=dp(30),
                          halign='left', valign='middle',
                          text_size=(self.ids.status_history_container.width, None))
                )
            else:
                for entry in history_data:
                    status = entry.get('status', 'Inconnu')
                    time_str = entry.get('time', 'N/A')

                    entry_color = app_config.COLOR_TEXT_DARK
                    if "créé" in status.lower():
                        entry_color = app_config.COLOR_TEXT_PRIMARY
                    elif "chargé" in status.lower():
                        entry_color = app_config.COLOR_INFO
                    elif "en transit" in status.lower():
                        entry_color = app_config.COLOR_WARNING
                    elif "arrivé" in status.lower():
                        entry_color = app_config.COLOR_PRIMARY
                    elif "livré" in status.lower():
                        entry_color = app_config.COLOR_SUCCESS
                    elif "annulé" in status.lower():
                        entry_color = app_config.COLOR_ERROR

                    self.ids.status_history_container.add_widget(
                        Label(text=f"[b]{status}[/b] à {time_str}",
                              markup=True,
                              color=entry_color,
                              font_size=app_config.FONT_SIZE_SM,
                              size_hint_y=None, height=dp(25),
                              halign='left', valign='middle',
                              text_size=(self.ids.status_history_container.width, None))
                    )

    def update_delivery_status_action(self, new_status):
        """
        Appelle l'API pour mettre à jour le statut de la livraison.
        """
        app = App.get_running_app()
        if not app.token or not self.delivery_data:
            self.update_detail_status("Erreur: Non connecté ou pas de livraison sélectionnée.", "error")
            return

        delivery_id = self.delivery_data.get('id')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M") # Horodatage actuel

        self.update_detail_status(f"Mise à jour du statut vers '{new_status}'...", "info")
        # Exécuter l'appel API dans un thread pour ne pas bloquer l'UI
        Clock.schedule_once(lambda dt: self._perform_status_update_api_call(app.token, delivery_id, new_status, current_time), 0.1)

    def _perform_status_update_api_call(self, token, delivery_id, new_status, current_time):
        """Exécute l'appel réel à l'API pour la mise à jour du statut."""
        app = App.get_running_app()
        # Supposons une méthode dans ApiService pour mettre à jour le statut
        response = app.api_service.update_delivery_status(token, delivery_id, new_status, current_time)

        if response.get("success"):
            self.update_detail_status(f"Statut mis à jour à '{new_status}'.", "success")
            # Mettre à jour les données locales pour refléter le changement
            self.delivery_data['status'] = new_status
            
            # Ajoutez la nouvelle entrée à l'historique de manière simulée
            if 'history' not in self.delivery_data:
                self.delivery_data['history'] = []
            self.delivery_data['history'].append({"status": new_status, "time": current_time})
            
            # Re-évaluer les boutons d'action (peut-être basé sur le nouveau statut)
            self.update_action_buttons_state(new_status)
            self.update_ui_with_delivery_data() # Rafraîchir l'UI complète
            print(f"DeliveryDetailScreen: Statut de {delivery_id} mis à jour à {new_status}.")
        else:
            message = response.get("message", f"Échec de la mise à jour du statut pour {delivery_id}.")
            self.update_detail_status(message, "error")
            print(f"DeliveryDetailScreen: Erreur de mise à jour du statut: {message}")

    @mainthread
    def update_detail_status(self, message, msg_type="info"):
        """Met à jour le message de statut et sa couleur sur l'écran de détails."""
        app_config = App.get_running_app().app_config
        self.detail_status_message = message
        if msg_type == "error":
            self.detail_status_color = app_config.COLOR_ERROR
        elif msg_type == "success":
            self.detail_status_color = app_config.COLOR_SUCCESS
        elif msg_type == "info":
            self.detail_status_color = app_config.COLOR_INFO
        else:
            self.detail_status_color = app_config.COLOR_TEXT_MUTED

    def update_action_buttons_state(self, current_status):
        """
        Met à jour l'état (actif/inactif) des boutons d'action
        basé sur le statut actuel de la livraison.
        """
        # Réinitialiser tous les boutons à False, puis activer si nécessaire
        self.can_load = False
        self.can_depart = False
        self.can_arrive = False
        self.can_deliver = False

        if current_status == "En Attente":
            self.can_load = True
        elif current_status == "Chargé":
            self.can_depart = True
        elif current_status == "En Transit":
            self.can_arrive = True
        elif current_status == "Arrivé":
            self.can_deliver = True
        # Si "Livré" ou "Annulé", aucun bouton n'est actif

    def go_back(self):
        """Retourne à l'écran précédent (liste des livraisons)."""
        App.get_running_app().change_screen('delivery')
