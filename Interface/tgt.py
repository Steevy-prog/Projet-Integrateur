import sys
import json
from datetime import datetime, date

# Import Kivy components
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp # For density-independent pixels

# Set window size for desktop testing (optional, for mobile it will be full screen)
# Window.size = (1400, 900)
# Window.minimum_width = 800
# Window.minimum_height = 600

# Kivy Language String for UI definitions
# This makes the UI structure cleaner and separates it from Python logic
KV = """
#:import hex kivy.utils.get_color_from_hex
#:import NoTransition kivy.uix.screenmanager.NoTransition

<RoundedBoxLayout@BoxLayout>:
    # A reusable BoxLayout with rounded corners and shadow (simulated)
    canvas.before:
        Color:
            rgba: hex('#ffffff') # White background
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16),]
        # Simple shadow effect (can be more complex with shaders)
        Color:
            rgba: 0, 0, 0, 0.05 # Light shadow
        RoundedRectangle:
            pos: self.x + dp(2), self.y - dp(2) # Offset for shadow
            size: self.width - dp(4), self.height - dp(4)
            radius: [dp(16),]

<AnimatedButton@Button>:
    # Custom animated button with hover effects (Kivy style)
    background_normal: ''
    background_down: ''
    background_color: 0,0,0,0 # Transparent background for custom drawing
    font_name: 'Roboto' # Default Kivy font, can be loaded
    font_size: dp(16)
    bold: True if self.is_active else False
    color: hex('#ffffff') if self.is_active else hex('#4a5568')
    padding: dp(12), dp(20)
    size_hint_y: None
    height: dp(50)
    text_size: self.width - dp(40), None # Adjust text size for padding
    halign: 'left'
    valign: 'middle'
    is_active: False # Custom property to track active state

    canvas.before:
        Color:
            # Active state gradient
            rgba: (hex('#667eea') if self.is_active else hex('#edf2f7')) if self.state == 'normal' else (hex('#5a67d8') if self.is_active else hex('#e2e8f0'))
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12),]
        # Border for inactive state
        Color:
            rgba: hex('#e2e8f0') if not self.is_active else (0,0,0,0)
        Line:
            width: dp(1)
            rounded_rectangle: self.x, self.y, self.width, self.height, dp(12)

<StatsCard@RoundedBoxLayout>:
    # Custom stats card widget
    orientation: 'vertical'
    size_hint_y: None
    height: dp(120)
    padding: dp(15)
    spacing: dp(5)
    title: ''
    value: 0
    icon: ''
    card_color: hex('#3182ce') # Default color

    canvas.before:
        Color:
            rgba: hex('#ffffff') # White background
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16),]
        Color:
            rgba: hex('#e2e8f0') # Border color
        Line:
            width: dp(1)
            rounded_rectangle: self.x, self.y, self.width, self.height, dp(16)
    
    # Hover effect (simplified, Kivy doesn't have direct CSS-like hover)
    # This would require custom event handling or a behavior
    # For now, the border color will be static unless custom logic is added

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(30)
        Label:
            text: root.icon
            font_size: dp(24)
            color: root.card_color
            size_hint_x: None
            width: self.texture_size[0] + dp(10)
            halign: 'left'
            valign: 'middle'
            text_size: self.size
        Widget: # Spacer
        Label:
            text: root.title
            font_size: dp(12)
            color: hex('#718096')
            size_hint_x: None
            width: self.texture_size[0] + dp(10)
            halign: 'right'
            valign: 'middle'
            text_size: self.size
    Label:
        text: str(root.value)
        font_size: dp(28)
        bold: True
        color: root.card_color
        halign: 'center'
        valign: 'middle'
        text_size: self.size
    Widget: # Spacer

<DeliveryListItem@RecycleDataViewBehavior+BoxLayout>:
    # Custom item for RecycleView (table rows)
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(60)
    padding: dp(12)
    spacing: dp(5)
    canvas.before:
        Color:
            rgba: hex('#f7fafc') if self.index % 2 == 1 else hex('#ffffff') # Alternating row colors
        Rectangle:
            pos: self.pos
            size: self.size
    
    # Data properties for the RecycleView item
    delivery_id: ''
    package_id: ''
    recipient_name: ''
    address: ''
    date_info: ''
    is_pending: False # To show/hide action button

    Label:
        text: root.delivery_id
        color: hex('#2d3748')
        font_size: dp(14)
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        size_hint_x: 0.15
    Label:
        text: root.package_id
        color: hex('#2d3748')
        font_size: dp(14)
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        size_hint_x: 0.15
    Label:
        text: root.recipient_name
        color: hex('#2d3748')
        font_size: dp(14)
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        size_hint_x: 0.2
    Label:
        text: root.address
        color: hex('#2d3748')
        font_size: dp(14)
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        size_hint_x: 0.3
    Label:
        text: root.date_info
        color: hex('#2d3748')
        font_size: dp(14)
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        size_hint_x: 0.15
    Button:
        text: '📋 Détails'
        size_hint_x: 0.15
        background_normal: ''
        background_down: ''
        background_color: 0,0,0,0
        color: hex('#ffffff')
        font_size: dp(14)
        bold: True
        on_release: app.root.get_screen('driver_app_screen').show_delivery_popup(self.delivery_data)
        opacity: 1 if root.is_pending else 0 # Show/hide based on type
        disabled: not root.is_pending # Disable if not pending

        canvas.before:
            Color:
                rgba: hex('#4f46e5') if self.state == 'normal' else hex('#4338ca')
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(8),]

<LoginScreen>:
    name: 'login_screen'
    canvas.before:
        Color:
            # Background gradient
            rgba: hex('#a7bfe8')
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: hex('#6190e8')
        Rectangle:
            pos: self.pos[0], self.pos[1] + self.height / 2
            size: self.width, self.height / 2
            
    BoxLayout:
        orientation: 'vertical'
        size_hint: 0.7, 0.7 # Make the login box smaller
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        padding: dp(50)
        spacing: dp(20)
        canvas.before:
            Color:
                rgba: hex('#ffffff')
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(20),]
            Color:
                rgba: 0, 0, 0, 0.1 # Shadow
            RoundedRectangle:
                pos: self.x + dp(5), self.y - dp(5)
                size: self.width - dp(10), self.height - dp(10)
                radius: [dp(20),]

        Label:
            text: '🚚 DeliveryPro'
            font_size: dp(30)
            bold: True
            color: hex('#4f46e5')
            size_hint_y: None
            height: self.texture_size[1]
            halign: 'center'
            valign: 'middle'
            text_size: self.size

        TextInput:
            id: username_input
            hint_text: "Nom d'utilisateur"
            font_size: dp(16)
            size_hint_y: None
            height: dp(40)
            padding: dp(10), dp(10)
            background_normal: ''
            background_active: ''
            background_color: hex('#ffffff')
            foreground_color: hex('#2d3748')
            cursor_color: hex('#4f46e5')
            multiline: False
            canvas.before:
                Color:
                    rgba: hex('#e2e8f0') if not self.focus else hex('#4f46e5')
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(10),]
                Color:
                    rgba: hex('#ffffff')
                RoundedRectangle:
                    pos: self.x + dp(1), self.y + dp(1)
                    size: self.width - dp(2), self.height - dp(2)
                    radius: [dp(9),]

        TextInput:
            id: password_input
            hint_text: "Mot de passe"
            password: True
            font_size: dp(16)
            size_hint_y: None
            height: dp(40)
            padding: dp(10), dp(10)
            background_normal: ''
            background_active: ''
            background_color: hex('#ffffff')
            foreground_color: hex('#2d3748')
            cursor_color: hex('#4f46e5')
            multiline: False
            canvas.before:
                Color:
                    rgba: hex('#e2e8f0') if not self.focus else hex('#4f46e5')
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(10),]
                Color:
                    rgba: hex('#ffffff')
                RoundedRectangle:
                    pos: self.x + dp(1), self.y + dp(1)
                    size: self.width - dp(2), self.height - dp(2)
                    radius: [dp(9),]

        Button:
            text: 'Se connecter'
            font_size: dp(18)
            bold: True
            size_hint_y: None
            height: dp(45)
            background_normal: ''
            background_down: ''
            background_color: 0,0,0,0
            color: hex('#ffffff')
            on_release: root.attempt_login(username_input.text, password_input.text)
            canvas.before:
                Color:
                    rgba: hex('#4f46e5') if self.state == 'normal' else hex('#4338ca')
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(12),]

<DriverAppScreen>:
    name: 'driver_app_screen'
    driver_name: '' # Property to hold driver's name

    BoxLayout:
        orientation: 'horizontal'
        padding: 0
        spacing: 0

        # Sidebar
        BoxLayout:
            id: sidebar
            orientation: 'vertical'
            size_hint_x: None
            width: dp(280)
            padding: dp(20)
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: hex('#f7fafc') # Light gray background
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: hex('#e2e8f0') # Right border
                Line:
                    points: self.right, self.y, self.right, self.top
                    width: dp(1)

            Label:
                text: '🚚 SCA Delivery Dashboard'
                font_size: dp(18)
                bold: True
                color: hex('#2d3748')
                size_hint_y: None
                height: self.texture_size[1] + dp(20) # Add padding
                halign: 'left'
                valign: 'middle'
                text_size: self.size

            AnimatedButton:
                text: '📋 Tableau de bord'
                is_active: True if root.ids.screen_manager.current == 'dashboard_screen' else False
                on_release: root.ids.screen_manager.current = 'dashboard_screen'
            AnimatedButton:
                text: '🕒 Livraisons en cours'
                is_active: True if root.ids.screen_manager.current == 'pending_screen' else False
                on_release: root.ids.screen_manager.current = 'pending_screen'
            AnimatedButton:
                text: '✅ Livraisons terminées'
                is_active: True if root.ids.screen_manager.current == 'completed_screen' else False
                on_release: root.ids.screen_manager.current = 'completed_screen'
            AnimatedButton:
                text: '🗺️ Carte interactive'
                is_active: True if root.ids.screen_manager.current == 'map_screen' else False
                on_release: root.ids.screen_manager.current = 'map_screen'
            AnimatedButton:
                text: '📊 Statistiques'
                is_active: True if root.ids.screen_manager.current == 'stats_screen' else False
                on_release: root.ids.screen_manager.current = 'stats_screen'
            AnimatedButton:
                text: '⚙️ Paramètres'
                is_active: True if root.ids.screen_manager.current == 'settings_screen' else False
                on_release: root.ids.screen_manager.current = 'settings_screen'

            Widget: # Spacer
                size_hint_y: None
                height: dp(20)

            RoundedBoxLayout: # User Info Frame
                orientation: 'vertical'
                size_hint_y: None
                height: dp(100)
                padding: dp(15)
                spacing: dp(5)
                canvas.before:
                    Color:
                        rgba: hex('#ffffff') # White background
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(12),]
                Label:
                    text: '👤 My Self' # Placeholder, should be root.driver_name
                    font_size: dp(14)
                    bold: True
                    color: hex('#2d3748')
                    halign: 'left'
                    valign: 'middle'
                    text_size: self.size
                Label:
                    text: 'Chauffeur-livreur'
                    font_size: dp(12)
                    color: hex('#718096')
                    halign: 'left'
                    valign: 'middle'
                    text_size: self.size

        # Main Content Area
        ScreenManager:
            id: screen_manager
            transition: NoTransition() # Disable transition for instant switching

            Screen:
                name: 'dashboard_screen'
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(30)
                    spacing: dp(20)
                    canvas.before:
                        Color:
                            rgba: hex('#f7fafc') # Background
                        Rectangle:
                            pos: self.pos
                            size: self.size

                    Label:
                        text: f"Bonjour {root.driver_name} ! 👋"
                        font_size: dp(24)
                        bold: True
                        color: hex('#2d3748')
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size
                    Label:
                        text: "Voici un aperçu de vos livraisons aujourd'hui"
                        font_size: dp(14)
                        color: hex('#718096')
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size

                    GridLayout:
                        cols: 3
                        spacing: dp(20)
                        size_hint_y: None
                        height: dp(120) # Height of the cards

                        StatsCard:
                            id: total_card
                            title: 'Total'
                            value: 0
                            icon: '📦'
                            card_color: hex('#3182ce')
                        StatsCard:
                            id: pending_card
                            title: 'En cours'
                            value: 0
                            icon: '🕒'
                            card_color: hex('#e53e3e')
                        StatsCard:
                            id: completed_card
                            title: 'Terminées'
                            value: 0
                            icon: '✅'
                            card_color: hex('#38a169')

                    RoundedBoxLayout: # Quick Actions Frame
                        orientation: 'vertical'
                        padding: dp(20)
                        spacing: dp(15)
                        size_hint_y: None
                        height: dp(200) # Adjust as needed

                        Label:
                            text: '🚀 Actions rapides'
                            font_size: dp(18)
                            bold: True
                            color: hex('#2d3748')
                            size_hint_y: None
                            height: self.texture_size[1]
                            halign: 'left'
                            valign: 'middle'
                            text_size: self.size

                        BoxLayout:
                            orientation: 'horizontal'
                            spacing: dp(10)
                            size_hint_y: None
                            height: dp(45)

                            Button:
                                text: '📋 Voir les livraisons en cours'
                                font_size: dp(14)
                                bold: True
                                background_normal: ''
                                background_down: ''
                                background_color: 0,0,0,0
                                color: hex('#ffffff')
                                on_release: root.ids.screen_manager.current = 'pending_screen'
                                canvas.before:
                                    Color:
                                        rgba: hex('#4f46e5') if self.state == 'normal' else hex('#4338ca')
                                    RoundedRectangle:
                                        pos: self.pos
                                        size: self.size
                                        radius: [dp(12),]
                            Button:
                                text: '🗺️ Ouvrir la carte'
                                font_size: dp(14)
                                bold: True
                                background_normal: ''
                                background_down: ''
                                background_color: 0,0,0,0
                                color: hex('#ffffff')
                                on_release: root.ids.screen_manager.current = 'map_screen'
                                canvas.before:
                                    Color:
                                        rgba: hex('#4f46e5') if self.state == 'normal' else hex('#4338ca')
                                    RoundedRectangle:
                                        pos: self.pos
                                        size: self.size
                                        radius: [dp(12),]
                            Button:
                                text: '➕ Ajouter une livraison'
                                font_size: dp(14)
                                bold: True
                                background_normal: ''
                                background_down: ''
                                background_color: 0,0,0,0
                                color: hex('#ffffff')
                                on_release: root.show_message_popup("Fonctionnalité à venir", "L'ajout de livraison n'est pas encore implémenté.")
                                canvas.before:
                                    Color:
                                        rgba: hex('#4f46e5') if self.state == 'normal' else hex('#4338ca')
                                    RoundedRectangle:
                                        pos: self.pos
                                        size: self.size
                                        radius: [dp(12),]
                    Widget: # Spacer

            Screen:
                name: 'pending_screen'
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(30)
                    spacing: dp(20)
                    canvas.before:
                        Color:
                            rgba: hex('#f7fafc')
                        Rectangle:
                            pos: self.pos
                            size: self.size

                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(50)
                        Label:
                            text: '🕒 Livraisons en cours'
                            font_size: dp(20)
                            bold: True
                            color: hex('#2d3748')
                            size_hint_x: 0.7
                            halign: 'left'
                            valign: 'middle'
                            text_size: self.size
                        RoundedBoxLayout: # Search Frame
                            size_hint_x: 0.3
                            orientation: 'horizontal'
                            padding: dp(5)
                            spacing: dp(5)
                            TextInput:
                                id: search_input_pending
                                hint_text: '🔍 Rechercher une livraison...'
                                font_size: dp(14)
                                multiline: False
                                background_normal: ''
                                background_active: ''
                                background_color: hex('#ffffff')
                                foreground_color: hex('#2d3748')
                                cursor_color: hex('#4f46e5')
                                on_text_validate: root.search_deliveries(self.text, 'pending')
                                size_hint_x: 0.7
                                canvas.before:
                                    Color:
                                        rgba: hex('#ffffff')
                                    RoundedRectangle:
                                        pos: self.pos
                                        size: self.size
                                        radius: [dp(10),]
                            Button:
                                text: 'Rechercher'
                                font_size: dp(14)
                                bold: True
                                background_normal: ''
                                background_down: ''
                                background_color: 0,0,0,0
                                color: hex('#ffffff')
                                on_release: root.search_deliveries(search_input_pending.text, 'pending')
                                size_hint_x: 0.3
                                canvas.before:
                                    Color:
                                        rgba: hex('#4f46e5') if self.state == 'normal' else hex('#4338ca')
                                    RoundedRectangle:
                                        pos: self.pos
                                        size: self.size
                                        radius: [dp(15),]

                    RoundedBoxLayout: # Table Container
                        orientation: 'vertical'
                        padding: 0
                        spacing: 0
                        size_hint_y: 1

                        # Table Header
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint_y: None
                            height: dp(50)
                            canvas.before:
                                Color:
                                    rgba: hex('#4f46e5') # Header background
                                Rectangle:
                                    pos: self.pos
                                    size: self.size
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(12), dp(12), 0, 0] # Top rounded corners
                            Label:
                                text: 'ID'
                                color: hex('#ffffff')
                                font_size: dp(14)
                                bold: True
                                size_hint_x: 0.15
                            Label:
                                text: 'Colis'
                                color: hex('#ffffff')
                                font_size: dp(14)
                                bold: True
                                size_hint_x: 0.15
                            Label:
                                text: 'Destinataire'
                                color: hex('#ffffff')
                                font_size: dp(14)
                                bold: True
                                size_hint_x: 0.2
                            Label:
                                text: 'Adresse'
                                color: hex('#ffffff')
                                font_size: dp(14)
                                bold: True
                                size_hint_x: 0.3
                            Label:
                                text: 'Date prévue'
                                color: hex('#ffffff')
                                font_size: dp(14)
                                bold: True
                                size_hint_x: 0.15
                            Label: # For the Action button column
                                text: 'Action'
                                color: hex('#ffffff')
                                font_size: dp(14)
                                bold: True
                                size_hint_x: 0.15

                        RecycleView:
                            id: pending_rv
                            viewclass: 'DeliveryListItem'
                            bar_width: dp(10)
                            scroll_type: ['bars', 'content']
                            scroll_wheel_distance: dp(10)
                            effect_cls: 'ScrollEffect'
                            do_scroll_x: False
                            data: [] # This will be populated by Python

                            RecycleBoxLayout:
                                default_size: None, dp(60)
                                default_size_hint: 1, None
                                size_hint_y: None
                                orientation: 'vertical'
                                height: self.minimum_height
                                padding: 0
                                spacing: 0
                                key_selection: 'selectable'

            Screen:
                name: 'completed_screen'
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(30)
                    spacing: dp(20)
                    canvas.before:
                        Color:
                            rgba: hex('#f7fafc')
                        Rectangle:
                            pos: self.pos
                            size: self.size

                    Label:
                        text: '✅ Livraisons terminées'
                        font_size: dp(20)
                        bold: True
                        color: hex('#2d3748')
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size

                    RoundedBoxLayout: # Table Container
                        orientation: 'vertical'
                        padding: 0
                        spacing: 0
                        size_hint_y: 1

                        # Table Header
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint_y: None
                            height: dp(50)
                            canvas.before:
                                Color:
                                    rgba: hex('#4f46e5') # Header background
                                Rectangle:
                                    pos: self.pos
                                    size: self.size
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(12), dp(12), 0, 0] # Top rounded corners
                            Label:
                                text: 'ID'
                                color: hex('#ffffff')
                                font_size: dp(14)
                                bold: True
                                size_hint_x: 0.15
                            Label:
                                text: 'Colis'
                                color: hex('#ffffff')
                                font_size: dp(14)
                                bold: True
                                size_hint_x: 0.15
                            Label:
                                text: 'Destinataire'
                                color: hex('#ffffff')
                                font_size: dp(14)
                                bold: True
                                size_hint_x: 0.2
                            Label:
                                text: 'Adresse'
                                color: hex('#ffffff')
                                font_size: dp(14)
                                bold: True
                                size_hint_x: 0.3
                            Label:
                                text: 'Date livrée'
                                color: hex('#ffffff')
                                font_size: dp(14)
                                bold: True
                                size_hint_x: 0.2

                        RecycleView:
                            id: completed_rv
                            viewclass: 'DeliveryListItem'
                            bar_width: dp(10)
                            scroll_type: ['bars', 'content']
                            scroll_wheel_distance: dp(10)
                            effect_cls: 'ScrollEffect'
                            do_scroll_x: False
                            data: [] # This will be populated by Python

                            RecycleBoxLayout:
                                default_size: None, dp(60)
                                default_size_hint: 1, None
                                size_hint_y: None
                                orientation: 'vertical'
                                height: self.minimum_height
                                padding: 0
                                spacing: 0
                                key_selection: 'selectable'

            Screen:
                name: 'map_screen'
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(30)
                    spacing: dp(20)
                    canvas.before:
                        Color:
                            rgba: hex('#f7fafc')
                        Rectangle:
                            pos: self.pos
                            size: self.size

                    Label:
                        text: '🗺️ Carte interactive'
                        font_size: dp(20)
                        bold: True
                        color: hex('#2d3748')
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size

                    RoundedBoxLayout:
                        Label:
                            text: 'Map functionality requires external Kivy extensions (e.g., kivymd_extensions.web_view) or a custom map integration. \\n\\nDisplaying static map placeholder.'
                            font_size: dp(16)
                            color: hex('#718096')
                            halign: 'center'
                            valign: 'middle'
                            text_size: self.size
                            padding: dp(50)

            Screen:
                name: 'stats_screen'
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(30)
                    spacing: dp(20)
                    canvas.before:
                        Color:
                            rgba: hex('#f7fafc')
                        Rectangle:
                            pos: self.pos
                            size: self.size

                    Label:
                        text: '📊 Statistiques détaillées'
                        font_size: dp(20)
                        bold: True
                        color: hex('#2d3748')
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size

                    RoundedBoxLayout:
                        Label:
                            text: '📈 Statistiques détaillées à venir...'
                            font_size: dp(16)
                            color: hex('#718096')
                            halign: 'center'
                            valign: 'middle'
                            text_size: self.size
                            padding: dp(50)

            Screen:
                name: 'settings_screen'
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(30)
                    spacing: dp(20)
                    canvas.before:
                        Color:
                            rgba: hex('#f7fafc')
                        Rectangle:
                            pos: self.pos
                            size: self.size

                    Label:
                        text: '⚙️ Paramètres'
                        font_size: dp(20)
                        bold: True
                        color: hex('#2d3748')
                        size_hint_y: None
                        height: self.texture_size[1]
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size

                    RoundedBoxLayout:
                        Label:
                            text: '🔧 Paramètres à venir...'
                            font_size: dp(16)
                            color: hex('#718096')
                            halign: 'center'
                            valign: 'middle'
                            text_size: self.size
                            padding: dp(50)
"""

# Load the Kivy Language string
Builder.load_string(KV)

class LoginScreen(Screen):
    """
    Login screen for the application.
    Handles user authentication.
    """
    def attempt_login(self, username, password):
        """
        Simulates a login attempt.
        In a real app, this would involve backend authentication.
        """
        if username == "driver" and password == "password":
            driver_info = {
                "id_chauffeur": 1,
                "nom": "Doe",
                "prenom": "John",
                "email": "john.doe@example.com",
                "telephone": "+237677123456",
                "vehicule": "Toyota Hilux"
            }
            app = App.get_running_app()
            driver_app_screen = app.root.get_screen('driver_app_screen')
            driver_app_screen.set_driver_info(driver_info)
            app.root.current = 'driver_app_screen'
        else:
            self.show_message_popup("Erreur de connexion", "Nom d'utilisateur ou mot de passe incorrect.")

    def show_message_popup(self, title, message):
        """
        Displays a simple message popup.
        """
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message, halign='center', valign='middle', text_size=(Window.width * 0.7 - dp(40), None)))
        
        # Add a spacer to push the button to the bottom
        content.add_widget(BoxLayout(size_hint_y=None, height=dp(10))) 

        close_button = Button(text="Fermer", size_hint=(None, None), size=(dp(120), dp(40)), pos_hint={'center_x': 0.5})
        close_button.background_normal = ''
        close_button.background_down = ''
        close_button.background_color = 0,0,0,0
        close_button.color = [1,1,1,1]
        close_button.canvas.before:
            Color:
                rgba: App.get_running_app().hex_to_rgba('#4f46e5') if close_button.state == 'normal' else App.get_running_app().hex_to_rgba('#4338ca')
            RoundedRectangle:
                pos: close_button.pos
                size: close_button.size
                radius: [dp(8),]

        content.add_widget(close_button)

        popup = Popup(title=title, content=content, size_hint=(0.7, 0.4), auto_dismiss=False)
        close_button.bind(on_release=popup.dismiss)
        popup.open()


class DriverAppScreen(Screen):
    """
    Main dashboard screen for the driver application.
    Contains sidebar navigation and content areas.
    """
    driver_name = StringProperty('') # Kivy property to update driver's name in UI

    def __init__(self, **kw):
        super().__init__(**kw)
        self.driver_info = {}
        self.pending_deliveries_data = []
        self.completed_deliveries_data = []
        self.load_simulated_data()
        # Bind to the screen manager's current screen property to update active nav
        self.bind(on_enter=self.on_screen_enter) # Load data when screen is entered

    def on_screen_enter(self, *args):
        """
        Called when this screen becomes the current screen in the ScreenManager.
        Useful for initial data loading or UI updates.
        """
        self.load_all_deliveries()
        self.update_counters()
        # Set initial active button in sidebar (Kivy KV handles this via current screen)

    def set_driver_info(self, info):
        """Sets the driver information and updates the UI."""
        self.driver_info = info
        self.driver_name = info.get('prenom', 'Chauffeur') # Update Kivy property

    def load_simulated_data(self):
        """Loads dummy data for deliveries."""
        self.pending_deliveries_data = [
            {
                "id_livraison": 101, "id_colis": "PKG001",
                "nom_destinataire": "Alice Dubois",
                "adresse": "10 Rue Principale, Yaoundé",
                "date_expedition": "2025-07-01",
                "date_prevue": "2025-07-05",
                "poids": "2 kg", "volume": "0.01 m³", "type": "Document",
                "instructions": "Fragile, éviter l'humidité",
                "lat": 3.8619, "lon": 11.5217
            },
            {
                "id_livraison": 102, "id_colis": "PKG002",
                "nom_destinataire": "Bob Martin",
                "adresse": "25 Avenue de la Liberté, Douala",
                "date_expedition": "2025-07-02",
                "date_prevue": "2025-07-06",
                "poids": "10 kg", "volume": "0.05 m³", "type": "Électronique",
                "instructions": "Ne pas exposer au soleil",
                "lat": 4.0415, "lon": 9.7028
            },
            {
                "id_livraison": 103, "id_colis": "PKG003",
                "nom_destinataire": "Claire Nguyen",
                "adresse": "15 Boulevard du 20 Mai, Bafoussam",
                "date_expedition": "2025-07-03",
                "date_prevue": "2025-07-07",
                "poids": "5 kg", "volume": "0.02 m³", "type": "Vêtements",
                "instructions": "Livrer entre 9h et 17h",
                "lat": 5.4737, "lon": 10.4176
            }
        ]
        self.completed_deliveries_data = [
            {
                "id_livraison": 100, "id_colis": "PKG000",
                "nom_destinataire": "David Kamga",
                "adresse": "8 Rue de la Paix, Douala",
                "date_expedition": "2025-06-30",
                "date_prevue": "2025-07-04",
                "date_livree": "2025-07-04",
                "poids": "3 kg", "volume": "0.015 m³", "type": "Livre",
                "instructions": "Appeler avant livraison",
                "lat": 4.0463, "lon": 9.7075
            }
        ]

    def load_all_deliveries(self):
        """Loads all delivery data into the RecycleViews."""
        self.load_pending_deliveries()
        self.load_completed_deliveries()
        self.update_counters()

    def load_pending_deliveries(self, search_text=""):
        """Populates the pending deliveries RecycleView."""
        rv_data = []
        filtered_data = [d for d in self.pending_deliveries_data if search_text.lower() in str(d).lower()]

        for d in filtered_data:
            rv_data.append({
                'delivery_id': str(d["id_livraison"]),
                'package_id': d["id_colis"],
                'recipient_name': d["nom_destinataire"],
                'address': d["adresse"],
                'date_info': d["date_prevue"],
                'is_pending': True,
                'delivery_data': d # Pass the full data for the popup
            })
        self.ids.pending_rv.data = rv_data

    def load_completed_deliveries(self):
        """Populates the completed deliveries RecycleView."""
        rv_data = []
        for d in self.completed_deliveries_data:
            rv_data.append({
                'delivery_id': str(d["id_livraison"]),
                'package_id': d["id_colis"],
                'recipient_name': d["nom_destinataire"],
                'address': d["adresse"],
                'date_info': d["date_livree"],
                'is_pending': False,
                'delivery_data': d # Pass the full data for the popup
            })
        self.ids.completed_rv.data = rv_data

    def update_counters(self):
        """Updates the dashboard stats cards."""
        total = len(self.pending_deliveries_data) + len(self.completed_deliveries_data)
        pending = len(self.pending_deliveries_data)
        completed = len(self.completed_deliveries_data)

        self.ids.total_card.value = total
        self.ids.pending_card.value = pending
        self.ids.completed_card.value = completed

    def search_deliveries(self, text, table_type):
        """Filters deliveries based on search text."""
        if table_type == 'pending':
            self.load_pending_deliveries(search_text=text)
        # Add search for completed if needed

    def show_delivery_popup(self, delivery):
        """
        Displays a detailed popup for a delivery.
        """
        content_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        info_text = f"""
        [size=20][b]📦 {delivery['id_colis']}[/b][/size]
        [size=16]👤 Destinataire: [b]{delivery['nom_destinataire']}[/b][/size]
        [size=16]📍 Adresse: [b]{delivery['adresse']}[/b][/size]
        [size=16]⚖️ Poids: [b]{delivery['poids']}[/b][/size]
        [size=16]📏 Volume: [b]{delivery['volume']}[/b][/size]
        [size=16]📦 Type: [b]{delivery['type']}[/b][/size]
        [size=16]📝 Instructions: [b]{delivery['instructions']}[/b][/size]
        [size=16]📅 Date Prévue: [b]{delivery['date_prevue']}[/b][/size]
        """
        
        details_label = Label(text=info_text, markup=True, halign='left', valign='top',
                              text_size=(Window.width * 0.7 - dp(40), None))
        content_layout.add_widget(details_label)
        
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(45))

        mark_complete_btn = Button(text="✅ Marquer comme livrée")
        report_problem_btn = Button(text="⚠️ Signaler un problème")
        close_btn = Button(text="❌ Fermer")

        # Apply button styles
        for btn in [mark_complete_btn, report_problem_btn, close_btn]:
            btn.background_normal = ''
            btn.background_down = ''
            btn.background_color = 0,0,0,0
            btn.color = [1,1,1,1]
            btn.font_size = dp(14)
            btn.bold = True
            btn.canvas.before:
                Color:
                    rgba: App.get_running_app().hex_to_rgba('#4f46e5') if btn.state == 'normal' else App.get_running_app().hex_to_rgba('#4338ca')
                RoundedRectangle:
                    pos: btn.pos
                    size: btn.size
                    radius: [dp(8),]
        
        # Override specific button colors
        report_problem_btn.canvas.before:
            Color:
                rgba: App.get_running_app().hex_to_rgba('#e53e3e') if report_problem_btn.state == 'normal' else App.get_running_app().hex_to_rgba('#c53030')
            RoundedRectangle:
                pos: report_problem_btn.pos
                size: report_problem_btn.size
                radius: [dp(8),]
        
        mark_complete_btn.canvas.before:
            Color:
                rgba: App.get_running_app().hex_to_rgba('#38a169') if mark_complete_btn.state == 'normal' else App.get_running_app().hex_to_rgba('#2f855a')
            RoundedRectangle:
                pos: mark_complete_btn.pos
                size: mark_complete_btn.size
                radius: [dp(8),]

        button_layout.add_widget(mark_complete_btn)
        button_layout.add_widget(report_problem_btn)
        button_layout.add_widget(close_btn)
        content_layout.add_widget(button_layout)

        popup = Popup(title=f"📦 Détails - Livraison {delivery['id_livraison']}",
                      content=content_layout,
                      size_hint=(0.8, 0.8),
                      auto_dismiss=False)
        
        mark_complete_btn.bind(on_release=lambda x: self.complete_delivery(delivery, popup))
        report_problem_btn.bind(on_release=lambda x: self.report_problem(popup))
        close_btn.bind(on_release=popup.dismiss)
        
        popup.open()

    def complete_delivery(self, delivery, popup):
        """Marks a delivery as complete."""
        # Find and remove the delivery from pending
        for i, d in enumerate(self.pending_deliveries_data):
            if d["id_livraison"] == delivery["id_livraison"]:
                completed_delivery = self.pending_deliveries_data.pop(i)
                completed_delivery["date_livree"] = datetime.now().strftime("%Y-%m-%d")
                self.completed_deliveries_data.append(completed_delivery)
                break
        
        popup.dismiss() # Dismiss the details popup
        self.show_message_popup("✅ Livraison terminée", "🎉 Livraison marquée comme terminée avec succès !")
        self.load_all_deliveries() # Reload data to update tables and counters

    def report_problem(self, popup):
        """Handles reporting a problem with a delivery."""
        popup.dismiss()
        self.show_message_popup("⚠️ Problème signalé", "Le problème a été signalé au service client.")

    def show_message_popup(self, title, message):
        """
        Displays a simple message popup.
        """
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message, halign='center', valign='middle', text_size=(Window.width * 0.7 - dp(40), None)))
        
        content.add_widget(BoxLayout(size_hint_y=None, height=dp(10))) 

        close_button = Button(text="OK", size_hint=(None, None), size=(dp(120), dp(40)), pos_hint={'center_x': 0.5})
        close_button.background_normal = ''
        close_button.background_down = ''
        close_button.background_color = 0,0,0,0
        close_button.color = [1,1,1,1]
        close_button.canvas.before:
            Color:
                rgba: App.get_running_app().hex_to_rgba('#4f46e5') if close_button.state == 'normal' else App.get_running_app().hex_to_rgba('#4338ca')
            RoundedRectangle:
                pos: close_button.pos
                size: close_button.size
                radius: [dp(8),]

        content.add_widget(close_button)

        popup = Popup(title=title, content=content, size_hint=(0.7, 0.4), auto_dismiss=False)
        close_button.bind(on_release=popup.dismiss)
        popup.open()


class DeliveryApp(App):
    """
    Main Kivy application class.
    Manages the screen transitions.
    """
    def build(self):
        """Builds the main application UI."""
        self.title = "DeliveryPro"
        # Set default font for the app (Kivy uses 'Roboto' by default)
        # You can load custom fonts if needed:
        # LabelBase.register(name='Segoe UI', fn_regular='path/to/SegoeUI.ttf')
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login_screen'))
        sm.add_widget(DriverAppScreen(name='driver_app_screen'))
        return sm

    def hex_to_rgba(self, hex_color):
        """Helper to convert hex color string to Kivy RGBA list."""
        from kivy.utils import get_color_from_hex
        return get_color_from_hex(hex_color)

if __name__ == '__main__':
    DeliveryApp().run()
