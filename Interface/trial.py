from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox,
    QLineEdit, QPushButton, QGridLayout, QVBoxLayout
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt
import sys

class InterfaceGoogleLike(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Informations générales")
        self.setStyleSheet("background-color: #121212; color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Titre
        titre = QLabel("Informations générales")
        titre.setFont(QFont("Arial", 24))
        layout.addWidget(titre)

        # Sous-titre
        sous_titre = QLabel("Saisissez votre date de naissance et votre genre.")
        sous_titre.setStyleSheet("font-size: 14px; color: #ccc;")
        layout.addWidget(sous_titre)

        # Formulaire
        form_layout = QGridLayout()
        jour_input = QLineEdit()
        jour_input.setPlaceholderText("Jour")
        jour_input.setStyleSheet("background-color: #1e1e1e; color: white; padding: 8px;")
        
        mois_input = QComboBox()
        mois_input.addItems([
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ])
        mois_input.setCurrentText("Mai")
        mois_input.setStyleSheet("background-color: #1e1e1e; color: white; padding: 8px;")
        
        an_input = QLineEdit()
        an_input.setPlaceholderText("An")
        an_input.setText("2007")
        an_input.setStyleSheet("background-color: #1e1e1e; color: white; padding: 8px;")

        genre_input = QComboBox()
        genre_input.addItems(["Homme", "Femme", "Personnalisé"])
        genre_input.setStyleSheet("background-color: #1e1e1e; color: white; padding: 8px;")
        genre_input.setPlaceholderText("Genre")

        form_layout.addWidget(jour_input, 0, 0)
        form_layout.addWidget(mois_input, 0, 1)
        form_layout.addWidget(an_input, 0, 2)
        form_layout.addWidget(genre_input, 1, 0, 1, 3)

        layout.addLayout(form_layout)

        # Lien d'information
        lien = QLabel('<a href="#">Pourquoi nous demandons la date de naissance et le genre</a>')
        lien.setOpenExternalLinks(True)
        lien.setStyleSheet("color: #8ab4f8; font-size: 13px;")
        layout.addWidget(lien)

        # Bouton Suivant
        bouton = QPushButton("Suivant")
        bouton.setStyleSheet("""
            QPushButton {
                background-color: #8ab4f8;
                border: none;
                border-radius: 18px;
                padding: 10px 20px;
                font-weight: bold;
                color: black;
                width: 100px;
            }
            QPushButton:hover {
                background-color: #a2c0ff;
            }
        """)
        bouton.setFixedWidth(100)
        bouton.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(bouton, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        self.setFixedSize(500, 250)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = InterfaceGoogleLike()
    win.show()
    sys.exit(app.exec())