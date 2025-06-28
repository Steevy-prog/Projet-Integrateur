# sge_transporteur/components/top_bar.py
from kivy.uix.boxlayout import BoxLayout

class TopBar(BoxLayout):
    """
    Custom Widget for the application's top bar.
    Its specific visual properties are primarily defined in the KV file.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure a default orientation if not specified in KV or here
        # self.orientation = 'horizontal' # Or explicitly in KV