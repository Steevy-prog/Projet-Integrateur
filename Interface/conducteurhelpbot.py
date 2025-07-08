import sys
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QThread, pyqtSignal
from pynput import keyboard
import google.generativeai as genai

API_KEY = "AIzaSyACCuz2G5YDYs7rmVl9X7Q_Z60Qa1TOq_8"
genai.configure(api_key=API_KEY)

MODEL_NAME = "models/gemini-2.5-pro"
model = genai.GenerativeModel(MODEL_NAME)

HELP_TEXT = """
Guide d'utilisation de l'application conducteur SCA Delivery
Cette application est conçue pour aider les conducteurs à gérer efficacement leurs livraisons. Elle offre une interface intuitive pour suivre les colis, consulter les détails des livraisons et signaler les problèmes.

Fonctionnalités principales :
Tableau de bord : Fournit un aperçu rapide des livraisons en cours et terminées pour la journée.

Mots-clés : tableau de bord, aperçu, livraisons du jour

Livraisons en cours : Affiche une liste détaillée de toutes les livraisons qui vous sont assignées et qui n'ont pas encore été complétées.

Mots-clés : livraisons en cours, colis en attente, mes livraisons

Livraisons terminées : Présente l'historique de toutes les livraisons que vous avez complétées.

Mots-clés : livraisons terminées, historique colis, colis livrés

Carte interactive : Permet de visualiser votre position actuelle ainsi que les lieux de livraison en cours et terminées sur une carte.

Mots-clés : carte, localisation, itinéraire, position

Aide : Cette section fournit des informations essentielles sur l'utilisation de l'application.

Mots-clés : aide, support, questions, informations

Paramètres : Accédez à vos informations de profil.

Mots-clés : paramètres, profil, mon compte, informations conducteur

Comment ça marche ?
Connexion : Connectez-vous avec votre nom d'utilisateur (email du conducteur) et votre mot de passe fourni.

Tableau de bord : Après la connexion, vous accédez à votre tableau de bord qui résume votre activité du jour.

Gestion des livraisons en cours :

Dans la section "Livraisons en cours", vous verrez la liste des colis à livrer.

Cliquez sur le bouton "Détails" à côté de chaque livraison pour afficher des informations complètes sur le colis (destinataire, adresse, poids, volume, instructions, etc.).

Marquer une livraison comme terminée : Une fois la livraison effectuée, cliquez sur le bouton "Marquer comme livrée" dans la fenêtre des détails. Confirmez l'action pour mettre à jour le statut du colis.

Visualisation sur la carte : La section "Carte interactive" vous permet de voir votre position en temps réel (mise à jour toutes les 60 secondes) ainsi que les emplacements de vos livraisons en cours et terminées. Cela vous aide à planifier vos itinéraires.

Signaler un problème : Si vous rencontrez un problème lors d'une livraison (par exemple, adresse introuvable, destinataire absent, colis endommagé), vous pouvez le signaler directement depuis la fenêtre des détails de la livraison en cliquant sur "Signaler un problème". L'équipe de support sera informée.

Déconnexion : Pour quitter l'application, utilisez le bouton "Déconnexion" situé en bas de la barre latérale.
"""

class WorkerThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            response = model.generate_content(self.prompt)
            answer = response.text.strip()
        except Exception as e:
            answer = f"Error: {e}"
        self.finished.emit(answer)


class ChatBot(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCA AI help Chatbot")
        self.resize(400, 450)

        # Card frame
        card = QFrame(self)
        card.setStyleSheet("""
            QFrame {
                background-color: #4683B7;
                border-radius: 18px;
                border: 1.5px solid #E0E0E0;
                padding: 18px;
                box-shadow: 0 6px 24px rgba(108,99,255,0.10);
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(18, 18, 18, 18)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background: #fff; border-radius: 8px; padding: 8px;")
        card_layout.addWidget(self.chat_display)

        self.input_line = QLineEdit()
        self.input_line.setStyleSheet("background: #FFFFFF; border-radius: 8px; padding: 8px;")
        card_layout.addWidget(self.input_line)

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #6C63FF;
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #5247D6;
            }
        """)
        card_layout.addWidget(self.send_button)

        # Main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(card)

        self.send_button.clicked.connect(self.on_send)
        self.input_line.returnPressed.connect(self.on_send)

        self.append_message("System", "Welcome! Ask me anything about your app.")

        self.worker_thread = None


    def append_message(self, sender, message):
        self.chat_display.append(f"<b>{sender}:</b> {message}")

    def on_send(self):
        question = self.input_line.text().strip()
        if not question:
            return

        self.append_message("You", question)
        self.input_line.clear()

        self.append_message("Bot", "<i>Thinking...</i>")

        prompt = f"""
You are a helpful and kind assistant. Use the following help guide to answer the user's question. If he asks about something not in the help guide, say you don't know.
If he greets you or shows any sign of politeness, respond in a friendly manner.

HELP DOCUMENT:
{HELP_TEXT}

QUESTION:
{question}

Answer only based on the HELP DOCUMENT above.
"""

        self.worker_thread = WorkerThread(prompt)
        self.worker_thread.finished.connect(self.handle_response)
        self.worker_thread.start()

    def handle_response(self, answer):
        self.chat_display.undo()
        self.append_message("SAC-Bot", answer)
        self.worker_thread = None


def listen_for_hotkey(app, chatbot):
    def on_press(key):
        try:
            if key == keyboard.Key.space and current_keys.get('ctrl'):
                if chatbot.isVisible():
                    chatbot.hide()
                else:
                    chatbot.show()
                    chatbot.activateWindow()
                    chatbot.raise_()
        except Exception as e:
            print("Hotkey error:", e)

    def on_release(key):
        if key == keyboard.Key.alt_l:
            current_keys['ctrl'] = False

    def on_key_down(key):
        if key == keyboard.Key.alt_l:
            current_keys['ctrl'] = True

    current_keys = {'ctrl': False}
    with keyboard.Listener(on_press=on_key_down, on_release=on_release) as listener:
        listener2 = keyboard.Listener(on_press=on_press)
        listener2.start()
        listener.join()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chatbot = ChatBot()
    chatbot.showMaximized()

    sys.exit(app.exec())