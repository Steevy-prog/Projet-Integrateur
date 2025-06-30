from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QMessageBox
)
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRect
import sys

# 🔄 États et couleurs
COULEURS = {
    "vide": "#2ECC71",     # vert
    "occupe": "#E74C3C",   # rouge
    "reserve": "#F39C12"   # orange
}

# 🧪 Données fictives des cellules
cellules = [
    {"id": "A1", "etat": "vide", "contenu": ""},
    {"id": "A2", "etat": "occupe", "contenu": "Boîtes alimentaires"},
    {"id": "A3", "etat": "reserve", "contenu": "Réservé pour livraison"},
    {"id": "B1", "etat": "vide", "contenu": ""},
    {"id": "B2", "etat": "occupe", "contenu": "Vêtements"},
    {"id": "B3", "etat": "reserve", "contenu": "Réservation client B12"},
    {"id": "C1", "etat": "vide", "contenu": ""},
    {"id": "C2", "etat": "occupe", "contenu": "Meubles"},
    {"id": "C3", "etat": "reserve", "contenu": "Stock urgent"},
]

class CelluleWidget(QWidget):
    def __init__(self, cellule_data, parent=None):
        super().__init__(parent)
        self.cellule_data = cellule_data
        self.setFixedSize(100, 100)

    def mousePressEvent(self, event):
        self.afficher_info()

    def afficher_info(self):
        etat = self.cellule_data["etat"]
        contenu = self.cellule_data["contenu"] or "Aucun contenu"
        msg = QMessageBox()
        msg.setWindowTitle(f"Cellule {self.cellule_data['id']}")
        msg.setText(
            f"État : {etat.capitalize()}\n"
            f"Contenu : {contenu}"
        )
        msg.exec()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        couleur = QColor(COULEURS[self.cellule_data["etat"]])
        painter.setBrush(couleur)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawRect(10, 10, 80, 80)

        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(QRect(10, 10, 80, 80), Qt.AlignmentFlag.AlignCenter,
                         self.cellule_data["id"])

class FenetrePrincipale(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualisation des Cellules")
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        lignes = 3
        colonnes = 3

        index = 0
        for row in range(lignes):
            for col in range(colonnes):
                if index < len(cellules):
                    widget = CelluleWidget(cellules[index])
                    layout.addWidget(widget, row, col)
                    index += 1

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetrePrincipale()
    fenetre.show()
    sys.exit(app.exec())