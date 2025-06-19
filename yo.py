from abc import ABC, abstractmethod

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