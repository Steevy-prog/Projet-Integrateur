# sge_transporteur/api_service.py

import requests
import json
import time # Importez time pour simuler un délai réseau

class ApiService:
    def __init__(self, base_url):
        self.base_url = base_url
        print(f"ApiService: Initialisé avec l'URL de base: {self.base_url}")
        # Si base_url est 'SIMULATION_MODE', on active la simulation.
        self.simulation_mode = (base_url == "SIMULATION_MODE")
        if self.simulation_mode:
            print("ApiService: Mode de simulation activé.")

    def _make_request(self, method, endpoint, data=None, token=None):
        """
        Méthode utilitaire interne pour faire des requêtes HTTP à l'API.
        Elle ne sera appelée que si nous NE SOMMES PAS en mode simulation.
        """
        if self.simulation_mode and endpoint in ["auth/login", "dashboard", "deliveries", "drivers", "vehicles", "delivery/update_status"]:
            # Cette branche ne devrait pas être atteinte pour ces endpoints en simulation
            # car nous allons simuler directement dans les méthodes appelantes.
            print(f"ApiService: Attention: Appel _make_request en mode simulation pour {endpoint}. "
                  "Ceci ne devrait pas arriver pour les endpoints simulés.")
            return {"success": False, "message": "Erreur interne: Tentative de requête HTTP en mode simulation."}

        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        print(f"ApiService: Requête {method} vers {url} avec data={data} et token={'présent' if token else 'absent'}")

        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == "GET":
                response = requests.get(url, headers=headers, params=data, timeout=10)
            else:
                return {"success": False, "message": "Méthode HTTP non supportée."}

            response.raise_for_status()

            try:
                return response.json()
            except json.JSONDecodeError:
                print(f"ApiService: Avertissement: Réponse non JSON reçue de {url}: {response.text}")
                return {"success": False, "message": "Réponse invalide du serveur (non-JSON)."}

        except requests.exceptions.Timeout:
            print(f"ApiService: Erreur de timeout pour la requête vers {url}")
            return {"success": False, "message": "La requête a expiré. Veuillez vérifier votre connexion ou l'état du serveur."}
        except requests.exceptions.ConnectionError:
            print(f"ApiService: Erreur de connexion pour la requête vers {url}")
            return {"success": False, "message": "Impossible de se connecter au serveur API. Le serveur est-il en ligne et accessible ?"}
        except requests.exceptions.RequestException as e:
            print(f"ApiService: Erreur lors de la requête vers {url}: {e}")
            status_code = response.status_code if 'response' in locals() else None
            error_message = f"Erreur API: {status_code} - {e}"

            if 'response' in locals() and response.text:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", error_message)
                except json.JSONDecodeError:
                    pass

            return {"success": False, "message": error_message}
        except Exception as e:
            print(f"ApiService: Erreur inattendue: {e}")
            return {"success": False, "message": f"Une erreur inattendue est survenue: {e}"}

    def login(self, username, password):
        """
        Gère la logique de connexion.
        Simule la réponse si en mode SIMULATION_MODE, sinon fait une vraie requête HTTP.
        """
        if self.simulation_mode:
            print(f"ApiService (SIMULATION): Tentative de connexion pour l'utilisateur: {username}")
            time.sleep(0.5) # Simule un petit délai réseau pour l'expérience utilisateur

            if username == "admin" and password == "admin":
                print("ApiService (SIMULATION): Connexion réussie.")
                return {"success": True, "message": "Connexion réussie", "token": "simulated_jwt_token_123"}
            elif not username or not password:
                print("ApiService (SIMULATION): Nom d'utilisateur ou mot de passe vide.")
                return {"success": False, "message": "Veuillez entrer votre nom d'utilisateur et votre mot de passe."}
            else:
                print("ApiService (SIMULATION): Identifiants invalides.")
                return {"success": False, "message": "Nom d'utilisateur ou mot de passe incorrect. Essayez 'admin'/'admin'."}
        else:
            # Si pas en mode simulation, faire la vraie requête API
            endpoint = "auth/login"
            data = {"username": username, "password": password}
            return self._make_request("POST", endpoint, data=data)

    def get_dashboard_data(self, token):
        """
        Récupère les données du tableau de bord.
        Simule la réponse si en mode SIMULATION_MODE, sinon fait une vraie requête HTTP.
        """
        if self.simulation_mode:
            print(f"ApiService (SIMULATION): Récupération des données du dashboard avec token: {token}")
            time.sleep(0.3) # Simule un petit délai

            if not token or token == "invalid_token" or token == "expired_token":
                print("ApiService (SIMULATION): Token invalide pour le dashboard.")
                return {"success": False, "message": "Authentification requise ou token invalide. Veuillez vous reconnecter."}
            
            # Données de tableau de bord simulées
            data = {
                "active_deliveries": 18,
                "pending_deliveries": 9,
                "available_vehicles": 4,
                "drivers_on_duty": 11,
                "recent_activities": [
                    {"time": "11:00", "status": "Livré", "delivery_id": "SIM001", "destination": "Yaoundé"},
                    {"time": "10:15", "status": "En Transit", "delivery_id": "SIM002", "destination": "Douala"},
                    {"time": "09:30", "status": "En Attente", "delivery_id": "SIM003", "destination": "Bafoussam"},
                    {"time": "08:45", "status": "Annulé", "delivery_id": "SIM004", "destination": "Kribi"},
                    {"time": "07:00", "status": "Livré", "delivery_id": "SIM005", "destination": "Bafang"},
                ]
            }
            print("ApiService (SIMULATION): Données du dashboard récupérées avec succès.")
            return {"success": True, "message": "Données du dashboard chargées (Simulées)", "data": data}
        else:
            # Si pas en mode simulation, faire la vraie requête API
            endpoint = "dashboard"
            return self._make_request("GET", endpoint, token=token)

    def get_deliveries(self, token):
        """
        Récupère les données des livraisons.
        Simule la réponse si en mode SIMULATION_MODE, sinon fait une vraie requête HTTP.
        """
        if self.simulation_mode:
            print(f"ApiService (SIMULATION): Récupération des données de livraisons avec token: {token}")
            time.sleep(0.4) # Simule un petit délai

            if not token or token == "invalid_token" or token == "expired_token":
                print("ApiService (SIMULATION): Token invalide pour les livraisons.")
                return {"success": False, "message": "Authentification requise ou token invalide. Veuillez vous reconnecter."}
            
            # Données de livraisons simulées
            deliveries_raw_data = [
                {"id": "DEL001", "client": "Dupont S.A.", "address": "123 Rue Principale, Douala", "status": "En Attente", "driver": "Jean Mvondo", "vehicle": "Camion A", "contact": "jean.dupont@example.com", "items": "10 cartons de marchandises diverses", "history": [{"status": "Créé", "time": "2025-06-25 09:00"}]},
                {"id": "DEL002", "client": "SARL Etoile", "address": "456 Av. Liberté, Yaoundé", "status": "Chargé", "driver": "Pierre Okala", "vehicle": "Fourgon B", "contact": "pierre.etoile@example.com", "items": "2 palettes de produits frais", "history": [{"status": "Créé", "time": "2025-06-25 08:30"}, {"status": "Chargé", "time": "2025-06-25 09:30"}]},
                {"id": "DEL003", "client": "Transco C.I.", "address": "789 Boul. Central, Bafoussam", "status": "En Transit", "driver": "Marie Nkom", "vehicle": "Camion C", "contact": "marie.transco@example.com", "items": "5 conteneurs de matériaux de construction", "history": [{"status": "Créé", "time": "2025-06-24 14:00"}, {"status": "Chargé", "time": "2025-06-25 07:00"}, {"status": "En Transit", "time": "2025-06-25 08:00"}]},
                {"id": "DEL004", "client": "Global Logistics", "address": "10 Place du Marché, Garoua", "status": "Arrivé", "driver": "Paul Ndongo", "vehicle": "Fourgon D", "contact": "paul.global@example.com", "items": "1 palette d'électronique", "history": [{"status": "Créé", "time": "2025-06-24 10:00"}, {"status": "Chargé", "time": "2025-06-24 11:00"}, {"status": "En Transit", "time": "2025-06-24 12:00"}, {"status": "Arrivé", "time": "2025-06-25 15:00"}]},
                {"id": "DEL005", "client": "Africa Express", "address": "22 Rue de la Plage, Kribi", "status": "Livré", "driver": "Alice Manga", "vehicle": "Camion E", "contact": "alice.africa@example.com", "items": "Matériel de pêche", "history": [{"status": "Créé", "time": "2025-06-23 18:00"}, {"status": "Chargé", "time": "2025-06-24 07:00"}, {"status": "En Transit", "time": "2025-06-24 08:00"}, {"status": "Arrivé", "time": "2025-06-24 16:00"}, {"status": "Livré", "time": "2025-06-24 17:00"}]},
                {"id": "DEL006", "client": "NextGen Ltd", "address": "33 Quartier Commercial, Limbe", "status": "Annulé", "driver": "Bertrand Kwe", "vehicle": "Fourgon F", "contact": "bertrand.nextgen@example.com", "items": "Logiciels et licences", "history": [{"status": "Créé", "time": "2025-06-22 11:00"}, {"status": "Annulé", "time": "2025-06-22 14:00"}]},
                # Ajoutez plus de données de livraison avec des statuts variés
                {"id": "DEL007", "client": "Innov Solutions", "address": "1 Av. du Progrès, Bamenda", "status": "En Attente", "driver": "Caroline Ngo", "vehicle": "Camion G", "contact": "caroline.innov@example.com", "items": "Équipement de bureau", "history": [{"status": "Créé", "time": "2025-06-25 10:30"}]},
                {"id": "DEL008", "client": "Fast Deliveries", "address": "5 Rue Rapide, Ngaoundéré", "status": "Chargé", "driver": "David Abessolo", "vehicle": "Fourgon H", "contact": "david.fast@example.com", "items": "Petits colis", "history": [{"status": "Créé", "time": "2025-06-25 07:00"}, {"status": "Chargé", "time": "2025-06-25 08:00"}]},
            ]

            # Ajouter les drapeaux can_X à chaque livraison simulée
            deliveries_data_with_flags = []
            for delivery in deliveries_raw_data:
                current_status = delivery.get('status', 'N/A').lower()
                delivery['can_load'] = False
                delivery['can_depart'] = False
                delivery['can_arrive'] = False
                delivery['can_deliver'] = False

                if current_status == "en attente":
                    delivery['can_load'] = True
                elif current_status == "chargé":
                    delivery['can_depart'] = True
                elif current_status == "en transit":
                    delivery['can_arrive'] = True
                elif current_status == "arrivé":
                    delivery['can_deliver'] = True
                # Les statuts "Livré" ou "Annulé" n'activent aucun bouton

                deliveries_data_with_flags.append(delivery)


            print("ApiService (SIMULATION): Données de livraisons récupérées avec succès et drapeaux ajoutés.")
            return {"success": True, "message": "Données de livraisons chargées (Simulées)", "data": deliveries_data_with_flags}
        else:
            # Si pas en mode simulation, faire la vraie requête API
            endpoint = "deliveries"
            return self._make_request("GET", endpoint, token=token)

    def get_drivers(self, token):
        """
        Récupère les données des conducteurs.
        Simule la réponse si en mode SIMULATION_MODE, sinon fait une vraie requête HTTP.
        """
        if self.simulation_mode:
            print(f"ApiService (SIMULATION): Récupération des données de conducteurs avec token: {token}")
            time.sleep(0.3) # Simule un petit délai

            if not token or token == "invalid_token" or token == "expired_token":
                print("ApiService (SIMULATION): Token invalide pour les conducteurs.")
                return {"success": False, "message": "Authentification requise ou token invalide. Veuillez vous reconnecter."}
            
            # Données de conducteurs simulées
            drivers_data = [
                {"id": "DRV001", "name": "Jean Mvondo", "status": "En service", "phone": "+237 677 123 456", "license": "B2345"},
                {"id": "DRV002", "name": "Pierre Okala", "status": "En pause", "phone": "+237 699 789 012", "license": "A1234"},
                {"id": "DRV003", "name": "Marie Nkom", "status": "En service", "phone": "+237 655 432 109", "license": "C5678"},
                {"id": "DRV004", "name": "Alice Manga", "status": "En congé", "phone": "+237 680 112 233", "license": "B9876"},
                {"id": "DRV005", "name": "David Abessolo", "status": "En service", "phone": "+237 670 567 890", "license": "C3456"},
                {"id": "DRV006", "name": "Caroline Ngo", "status": "En service", "phone": "+237 660 210 987", "license": "B5432"},
            ]
            print("ApiService (SIMULATION): Données de conducteurs récupérées avec succès.")
            return {"success": True, "message": "Données de conducteurs chargées (Simulées)", "data": drivers_data}
        else:
            # Si pas en mode simulation, faire la vraie requête API
            endpoint = "drivers"
            return self._make_request("GET", endpoint, token=token)

    def get_vehicles(self, token):
        """
        Récupère les données des véhicules.
        Simule la réponse si en mode SIMULATION_MODE, sinon fait une vraie requête HTTP.
        """
        if self.simulation_mode:
            print(f"ApiService (SIMULATION): Récupération des données des véhicules avec token: {token}")
            time.sleep(0.3) # Simule un petit délai

            if not token or token == "invalid_token" or token == "expired_token":
                print("ApiService (SIMULATION): Token invalide pour les véhicules.")
                return {"success": False, "message": "Authentification requise ou token invalide. Veuillez vous reconnecter."}
            
            # Données de véhicules simulées
            vehicles_data = [
                {"id": "VHC001", "plate": "CM-123-AB", "type": "Camion", "capacity": "15T", "status": "Disponible", "driver": "N/A"},
                {"id": "VHC002", "plate": "CM-456-CD", "type": "Fourgon", "capacity": "5T", "status": "En mission", "driver": "Jean Mvondo"},
                {"id": "VHC003", "plate": "CM-789-EF", "type": "Camion", "capacity": "20T", "status": "En maintenance", "driver": "N/A"},
                {"id": "VHC004", "plate": "CM-012-GH", "type": "Fourgon", "capacity": "3T", "status": "Disponible", "driver": "N/A"},
                {"id": "VHC005", "plate": "CM-345-IJ", "type": "Camion", "capacity": "10T", "status": "En mission", "driver": "Marie Nkom"},
                {"id": "VHC006", "plate": "CM-678-KL", "type": "Fourgon", "capacity": "7T", "status": "Disponible", "driver": "N/A"},
            ]
            print("ApiService (SIMULATION): Données des véhicules récupérées avec succès.")
            return {"success": True, "message": "Données des véhicules chargées (Simulées)", "data": vehicles_data}
        else:
            # Si pas en mode simulation, faire la vraie requête API
            endpoint = "vehicles"
            return self._make_request("GET", endpoint, token=token)

    def update_delivery_status(self, token, delivery_id, new_status, current_time):
        """
        Simule la mise à jour du statut d'une livraison.
        En mode simulation, elle détermine les nouveaux drapeaux can_X.
        """
        if self.simulation_mode:
            print(f"ApiService (SIMULATION): Tentative de mise à jour du statut pour {delivery_id} à {new_status}")
            time.sleep(0.5) # Simule un délai
            
            simulated_can_load = False
            simulated_can_depart = False
            simulated_can_arrive = False
            simulated_can_deliver = False

            # Déterminer les nouveaux drapeaux basés sur le nouveau statut
            if new_status == "En Attente":
                simulated_can_load = True
            elif new_status == "Chargé":
                simulated_can_depart = True
            elif new_status == "En Transit":
                simulated_can_arrive = True
            elif new_status == "Arrivé":
                simulated_can_deliver = True
            
            # IMPORTANT: La simulation de update_delivery_status ne renvoie PAS toutes les données originales de la livraison.
            # Elle renvoie juste les flags pertinents pour l'état des boutons.
            # L'écran de détails doit fusionner ces flags avec ses données existantes.
            response_data = {
                "id": delivery_id, # Assurez-vous d'inclure l'ID
                "status": new_status,
                "can_load": simulated_can_load,
                "can_depart": simulated_can_depart,
                "can_arrive": simulated_can_arrive,
                "can_deliver": simulated_can_deliver,
            }
            print(f"ApiService (SIMULATION): Statut mis à jour et capacités des boutons définies pour {delivery_id}.")
            return {"success": True, "message": f"Statut de la livraison {delivery_id} mis à jour à {new_status}.", "data": response_data}
        else:
            # Cette partie ferait un vrai appel API si le mode simulation était désactivé
            endpoint = f"delivery/{delivery_id}/update_status"
            data = {"new_status": new_status, "time": current_time}
            return self._make_request("POST", endpoint, data=data, token=token)

