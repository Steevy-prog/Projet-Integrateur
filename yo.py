from abc import ABC, abstractmethod
import sys
from Worker_Dashboard import MainWindow as window1
from Client_Dashboard import QMainWindow as window2
from IT_Technician import MainWindow as window3
from Manager_Dashboard import MainWindow as window4
# ----------------------------
# Abstract Definitions
# ----------------------------
class dashboard(ABC):
    @abstractmethod
    def exec(self, entier):
        pass

class state(ABC):
    @abstractmethod
    def doit(self):
        pass

# ----------------------------
# Concrete States (Menus)
# ----------------------------
class MainMenu(state):
    def doit(self):
        print("Main Menu: showing dashboard overview...")

class ReceptionMenu(state):
    def receive_package(self):
        pass
    def verify_package(self):
        pass
    def store_package(self):
        pass
    def reception_status(self):
        pass
    def doit(self):
        print("Reception Menu: handling package reception...")

class ExpeditionMenu(state):
    def prepare_order(self):
        pass
    def pick_items(self):
        pass
    def pack_order(self):
        pass
    def ship_order(self):
        pass
    def doit(self):
        print("Expedition Menu: managing shipping...")

class InventoryMenu(state):
    def list_products(self):
        pass
    def search_product(self):
        pass
    def move_product(self):
        pass
    def count_inventory(self):
        pass
    def doit(self):
        print("Inventory Menu: listing and searching products...")

class ReportMenu(state):
    def stock_report(self):
        pass
    def performance_report(self):
        pass
    def exception_report(self):
        pass
    def export_data(self):
        pass
    def doit(self):
        print("Report Menu: generating reports...")

class ConfigurationMenu(state):
    def user_managment(self):
        pass
    def system_settings(self):
        pass
    def backup_database(self):
        pass
    def restore_database(self):
        pass
    def doit(self):
        print("Configuration Menu: updating settings...")

class Help_Topics(state):
    def command_help(self):
        pass
    def syntax_help(self):
        pass
    def examples(self):
        pass
    def doit(self):
        print("Help Menu: providing help topics...")

# ----------------------------
# State Manager
# ----------------------------
class StateManager:
    def __init__(self):
        self.state = None

    def set_state(self, state: state):
        self.state = state

    def execute(self):
        if self.state:
            self.state.doit()
        else:
            print("No state selected.")

# ----------------------------
# Concrete Dashboards
# ----------------------------
class dashboard_stockmanager(dashboard):
    def exec(self, entier):
        manager = StateManager()
        options = {
            1: MainMenu(),
            2: InventoryMenu(),
            3: ReportMenu()
        }
        state = options.get(entier, MainMenu())
        manager.set_state(state)
        manager.execute()

class dashboard_warehouse_worker(dashboard):
    def exec(self, entier):
        manager = StateManager()
        options = {
            1: MainMenu(),
            2: ReceptionMenu(),
            3: ExpeditionMenu()
        }
        state = options.get(entier, MainMenu())
        manager.set_state(state)
        manager.execute()

class dashboard_logistic_agent(dashboard):
    def exec(self, entier):
        manager = StateManager()
        options = {
            1: MainMenu(),
            2: ExpeditionMenu(),
            3: InventoryMenu()
        }
        state = options.get(entier, MainMenu())
        manager.set_state(state)
        manager.execute()

class dashboard_IT_admin(dashboard):
    def exec(self, entier):
        manager = StateManager()
        options = {
            1: MainMenu(),
            2: ConfigurationMenu(),
            3: ReportMenu(),
            4: Help_Topics()
        }
        state = options.get(entier, MainMenu())
        manager.set_state(state)
        manager.execute()

# ----------------------------
# Dashboard Manager (optional)
# ----------------------------
class DashboardManager:
    def __init__(self, dashboard: dashboard):
        self.dashboard = dashboard

    def run(self, menu_choice: int):
        self.dashboard.exec(menu_choice)

# ----------------------------
# Example Usage
# ----------------------------
if __name__ == "__main__":
    # Simulate a user (e.g., stock manager) choosing a menu
    manager = DashboardManager(dashboard_stockmanager())
    manager.run(2)  # Should print: Inventory Menu...

class Product:
    def __init__(self, name):
        self.name = name 

class MaterialProduct(Product):
    def __init__(self, name, length, width, height, mass):
        super().__init__(name)
        self.length = length
        self.width = width
        self.height = height
        self.mass = mass
class SoftwareProduct(Product):
    def __init__(self, name, version, license_key):
        super().__init__(name)  
        self.version = version
        self.license_key = license_key

class Lot:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class Package:
    def __init__(self, lots, creation_date,status):
        self.lots = lots
        self.creation_date = creation_date
        self.status = status

    def __str__(self):
        return "Package contains: " + ", ".join(str(p) for p in self.lots) + f" | Created on: {self.creation_date} | Status: {self.status}"

class bon_reception:
    def __init__(self,colis,transporteur,fournisseur,date_creation,statut,remarques):
        self.colis = colis
        self.transporteur = transporteur
        self.fournisseur = fournisseur
        self.date_creation = date_creation
        self.statut = statut
        self.remarques = remarques
    
    def _str_(self):
        return f"Bon de réception: {self.colis} | Transporteur: {self.transporteur} | Fournisseur: {self.fournisseur} | Date: {self.date_creation} | Statut: {self.statut} | Remarques: {self.remarques}"

class bon_expedition:
    def _init_(self,colis,transporteur,destinataire,date_creation,statut,remarques):
        self.colis = colis
        self.transporteur = transporteur
        self.destinataire = destinataire
        self.date_creation = date_creation
        self.statut = statut
        self.remarques = remarques

    def __str__(self):
        return f"Bon d'expédition: {self.colis} | Transporteur: {self.transporteur} | Destinataire: {self.destinataire} | Date: {self.date_creation} | Statut: {self.statut} | Remarques: {self.remarques}"
    
class Rapport:
    def __init__(self,colis, type,date_creation,statut,description):
        self.colis = colis
        self.type = type
        self.date_creation = date_creation
        self.statut = statut
        self.description = description

    def __str__(self):
        return f"Rapport: {self.type} | Contenu: {self.description} | Date: {self.date_creation} | Statut: {self.statut} | Colis: {self.colis}"

class interface:
    @staticmethod
    def create_interface(number):
        if number == 1:
            return window1()
        elif number == 2:
            return window2()
        elif number == 3:
            return window3()
        elif number == 4:
            return window4()
        else:
            raise ValueError("Unknown interface number. Use 1 for Worker, 2 for Client, 3 for IT Technician.")
