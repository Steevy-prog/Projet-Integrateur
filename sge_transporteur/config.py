# sge_transporteur/config.py

from kivy.metrics import dp
from kivy.utils import get_color_from_hex # AJOUTÉ: Nécessaire pour convertir les couleurs hexadécimales

class AppConfig:
    def __init__(self): # <--- Tous les attributs sont maintenant dans __init__
        # --- API ---
        self.API_BASE_URL = "http://localhost:5000" # URL de base de votre API Flask

        # --- Couleurs (RGBA) ---
        # Utilisé get_color_from_hex pour des couleurs plus professionnelles et cohérentes
        self.COLOR_PRIMARY = get_color_from_hex("#1976D2")  # Bleu primaire (Material Design)
        self.COLOR_SECONDARY = get_color_from_hex("#424242") # Gris foncé (pour les fonds de sidebar, etc.)
        self.COLOR_ACCENT = get_color_from_hex("#FFAB00")   # Orange Ambre (pour accents, warnings)

        # Couleurs de fond
        self.COLOR_BACKGROUND_DARK = get_color_from_hex("#212121")  # Très foncé
        self.COLOR_BACKGROUND_LIGHT = get_color_from_hex("#F5F5F5") # Très clair
        self.COLOR_BACKGROUND_CARD = get_color_from_hex("#FFFFFF")  # Blanc pur pour les cartes

        # Couleurs de texte
        self.COLOR_TEXT_PRIMARY = get_color_from_hex("#212121") # Noir/gris très foncé pour texte principal sur clair
        self.COLOR_TEXT_SECONDARY = get_color_from_hex("#757575") # Gris moyen pour texte secondaire
        self.COLOR_TEXT_LIGHT = get_color_from_hex("#FFFFFF")   # Blanc pour texte sur fond sombre
        self.COLOR_TEXT_DARK = get_color_from_hex("#1E1E1E")    # Très foncé pour texte sur très clair
        self.COLOR_TEXT_MUTED = get_color_from_hex("#BDBDBD")   # Gris très clair pour indications discrètes

        # Couleurs de statut/feedback
        self.COLOR_SUCCESS = get_color_from_hex("#38A169")  # Vert
        self.COLOR_WARNING = get_color_from_hex("#E77E23")  # Orange
        self.COLOR_ERROR = get_color_from_hex("#F44366")    # Rouge (légèrement modifié pour une meilleure visibilité)
        self.COLOR_INFO = get_color_from_hex("#03A9F4")     # Bleu ciel

        # Couleurs des boutons (CORRIGÉES ET AJOUTÉES)
        self.COLOR_BUTTON_NORMAL = get_color_from_hex("#607D8B") # Gris bleuâtre pour les boutons non actifs
        self.COLOR_BUTTON_PRESSED = get_color_from_hex("#455A64") # Gris bleuâtre foncé pour les boutons pressés

        # Autres couleurs utiles
        self.COLOR_CARD_BORDER_DARK = get_color_from_hex("#8A8A8A") # Bordure de carte discrète
        self.WHITE = get_color_from_hex("#FFFFFF") # Définition explicite du blanc

        # --- Tailles de Police (utilisez dp pour la densité de pixels) ---
        self.FONT_SIZE_XS = dp(10)
        self.FONT_SIZE_SM = dp(14)
        self.FONT_SIZE_MD = dp(16)
        self.FONT_SIZE_LG = dp(20)
        self.FONT_SIZE_XL = dp(24)
        self.FONT_SIZE_XXL = dp(32)

        # --- Espacement (entre les widgets) ---
        self.SPACING_XS = dp(5)
        self.SPACING_SMALL = dp(10)
        self.SPACING_MEDIUM = dp(15) # CORRIGÉ: Était SPACING_MD dans le code, maintenant SPACING_MEDIUM existe
        self.SPACING_LARGE = dp(20)
        self.SPACING_XL = dp(40)

        # --- Padding (rembourrage interne des layouts) ---
        self.PADDING_XS = dp(5)
        self.PADDING_SMALL = dp(10)
        self.PADDING_MEDIUM = dp(20)
        self.PADDING_LARGE = dp(30)

        # --- Rayons des Coins (pour les éléments arrondis) ---
        self.CORNER_RADIUS_SM = dp(4)
        self.CORNER_RADIUS_MD = dp(8)
        self.CORNER_RADIUS_LG = dp(12)
        self.CORNER_RADIUS_XL = dp(20)

    # Fonction utilitaire pour convertir RGBA en hexadécimal
    # Reste une méthode de classe normale car elle n'a pas besoin d'être dans __init__
    def rgba_to_hex(self, rgba_list):
        """Convertit une liste RGBA [r, g, b, a] en une chaîne hexadécimale #RRGGBBAA."""
        if not isinstance(rgba_list, (list, tuple)) or len(rgba_list) not in [3, 4]:
            raise ValueError("RGBA list must have 3 or 4 components.")

        # Ajoutez l'alpha s'il n'est pas présent (par défaut opaque)
        if len(rgba_list) == 3:
            r, g, b = rgba_list
            a = 1.0
        else:
            r, g, b, a = rgba_list

        # S'assurer que les valeurs sont clampées entre 0 et 1
        r, g, b, a = [max(0, min(1, c)) for c in [r, g, b, a]]

        # Convertir en entiers 0-255
        r_int, g_int, b_int, a_int = int(r * 255), int(g * 255), int(b * 255), int(a * 255)

        # Retourner la chaîne hexadécimale
        return f"#{r_int:02X}{g_int:02X}{b_int:02X}{a_int:02X}"
