# sge_transporteur/components/navigation_view.py
from kivy.uix.boxlayout import BoxLayout

class NavigationView(BoxLayout):
    """
    Custom Widget for the side navigation bar.
    Its specific visual properties are primarily defined in the KV file.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure a default orientation if not specified in KV or here
        # This can be set directly in KV if you prefer.
        # self.orientation = 'vertical' # Or explicitly in KV