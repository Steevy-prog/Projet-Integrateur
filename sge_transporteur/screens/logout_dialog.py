# sge_transporteur/screens/logout_dialog.py

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.app import App
from kivy.metrics import dp

class LogoutConfirmPopup(Popup):
    """
    Un popup simple pour demander une confirmation de déconnexion.
    Définit une propriété `result` ('yes' ou 'no') à la fermeture.
    """
    result = StringProperty('') # Pour stocker le résultat de la confirmation

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Confirmer la déconnexion"
        self.size_hint = (0.7, 0.4) # Taille du popup
        self.auto_dismiss = False # Empêche la fermeture au clic en dehors du popup

        app_config = App.get_running_app().app_config if App.get_running_app() else None
        
        # Le contenu du popup
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Message
        message_label = Label(
            text="Êtes-vous sûr de vouloir vous déconnecter ?",
            halign='center',
            valign='middle',
            font_size=app_config.FONT_SIZE_MD if app_config else '18sp',
            color=app_config.COLOR_INFO if app_config else [0,0,0,1]
        )
        content.add_widget(message_label)

        # Boutons d'action
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        btn_yes = Button(
            text="Oui",
            background_normal='',
            background_color=app_config.COLOR_ERROR if app_config else [0.8, 0.2, 0.2, 1], # Rouge pour "Oui"
            color=app_config.COLOR_TEXT_LIGHT if app_config else [1,1,1,1],
            font_size=app_config.FONT_SIZE_MD if app_config else '16sp'
        )
        btn_yes.bind(on_release=self.confirm_yes)
        
        btn_no = Button(
            text="Non",
            background_normal='',
            background_color=app_config.COLOR_BUTTON_NORMAL if app_config else [0.3, 0.3, 0.3, 1], # Gris pour "Non"
            color=app_config.COLOR_TEXT_LIGHT if app_config else [1,1,1,1],
            font_size=app_config.FONT_SIZE_MD if app_config else '16sp'
        )
        btn_no.bind(on_release=self.confirm_no)

        button_layout.add_widget(btn_no)
        button_layout.add_widget(btn_yes)
        
        content.add_widget(button_layout)
        
        self.content = content

    def confirm_yes(self, instance):
        self.result = 'yes'
        self.dismiss()

    def confirm_no(self, instance):
        self.result = 'no'
        self.dismiss()
