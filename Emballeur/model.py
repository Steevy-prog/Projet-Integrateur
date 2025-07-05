# model.py
import datetime
import random
import psycopg2
import pandas as pd

class Database:
    def __init__(self):
        self.conn = None
        self.cur = None
        self.client_org_id = 'OFIRST'
        self.emballeur_org_id = 'OEMB'
        
    def connect(self, it='2'):
        try:
            if it == '1':
                self.conn = psycopg2.connect(
                    host="dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com",
                    database="projet_integrateur",
                    user="group13",
                    password="nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3",
                    port=5432
                )
            elif it == '2':
                self.conn = psycopg2.connect(
                    host="localhost",
                    database="postgres",
                    user="postgres",
                    password="steevy",
                    port=5432
                )
            elif it == '3':
                self.conn = psycopg2.connect(
                    host="localhost",
                    database="Projet",
                    user="postgres",
                    password="Lune.Hatik123",
                    port=5432
                )
            self.cur = self.conn.cursor()
            return True
        except psycopg2.OperationalError as e:
            print(f"Database connection error: {e}")
            return False

    def fetch_initial_data(self):
        try:
            # Organizations
            self.cur.execute("SELECT (p).* FROM \"EMIR\".Organisation_EVA() AS p;")
            orgs = self.cur.fetchall()
            
            # Packages
            self.cur.execute("SELECT (p).* FROM \"EMIR\".PColis_EVA(%s) AS p;", (self.client_org_id,))
            colis_db = self.cur.fetchall()
            
            # Contents
            self.cur.execute("SELECT (p).* FROM \"EMIR\".PContenuColis_EVA(%s) AS p;", (self.client_org_id,))
            contenu = self.cur.fetchall()
            
            # Lots
            self.cur.execute("SELECT (p).* FROM \"EMIR\".PLot_EVA(%s) AS p;", (self.client_org_id,))
            lots_db = self.cur.fetchall()
            
            # Products
            self.cur.execute("SELECT (p).* FROM \"EMIR\".Produit_EVA() AS p;")
            produits_db = self.cur.fetchall()
            
            # Inquiries
            self.cur.execute("SELECT (p).* FROM \"EMIR\".inquiries_eva(%s) AS p;", (self.client_org_id,))
            inq_db = self.cur.fetchall()
            
            return {
                'orgs': orgs,
                'colis_db': colis_db,
                'contenu': contenu,
                'lots_db': lots_db,
                'produits_db': produits_db,
                'inq_db': inq_db
            }
        except psycopg2.Error as e:
            print(f"Database query error: {e}")
            return self.get_dummy_data()

    def get_dummy_data(self):
        return {
            'orgs': [('OFIRST', 'Client Org A'), ('OSEC', 'Supplier B'), ('OTHRD', 'Transporter C'), ('OEMB', 'Emballeur D')],
            'colis_db': [],
            'contenu': [],
            'lots_db': [],
            'produits_db': [
                ('P001', 'OSEC', 'Product A', 'Description A', 10.0, 'Brand1', 'Model1', 'Electronics'),
                ('P002', 'OSEC', 'Product B', 'Description B', 20.0, 'Brand2', 'Model2', 'Packaging'),
                ('P003', 'OSEC', 'Product C', 'Description C', 5.0, 'Brand3', 'Model3', 'Non-Electronic')
            ],
            'inq_db': []
        }

class IdGenerator:
    def generate_id(self, pattern, existing_ids):
        prefix = pattern[0:pattern.find('[')]
        while True:
            new_id = prefix + ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))
            if new_id not in existing_ids:
                return new_id

class Product:
    def __init__(self, name, fournisseur, description="", prix_unitaire=0.0, brand="", model="", category=""):
        self.name = name
        self.fournisseur = fournisseur
        self.description = description
        self.prix_unitaire = prix_unitaire
        self.brand = brand
        self.model = model
        self.category = category

class MaterialProduct(Product):
    def __init__(self, name, fournisseur, length, width, height, mass, **kwargs):
        super().__init__(name, fournisseur, **kwargs)
        self.length = length
        self.width = width
        self.height = height
        self.mass = mass

class SoftwareProduct(Product):
    def __init__(self, name, fournisseur, version, license_key, **kwargs):
        super().__init__(name, fournisseur, **kwargs)
        self.version = version
        self.license_key = license_key

class Lot:
    def __init__(self, product_id, product_name, quantity):
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

class Colis:
    def __init__(self, idcolis, statut, items, orderdate, estimated_delivery, Customer_id, totalvalue):
        self.idcolis = idcolis
        self.statut = statut
        self.items = items
        self.orderdate = orderdate
        self.estimated_delivery = estimated_delivery
        self.customerid = Customer_id
        self.totalvaule = totalvalue

class EmballeurModel:
    def __init__(self, emballeur_id, db):
        self.emballeur_id = emballeur_id
        self.db = db
        self.shipping_orders = []
        self.packaging_materials = []
        self.recent_activities = []
        
    def load_data(self):
        data = self.db.fetch_initial_data()
        
        # Products DataFrame
        self.products_df = pd.DataFrame(
            data['produits_db'], 
            columns=['ID', 'Fourniseur', 'Name', 'Description', 'Prix Unitaire', 'Brand', 'Model', 'Category']
        )
        
        # Generate shipping orders
        self._generate_shipping_orders(data['produits_db'], data['orgs'])
        
        # Generate packaging materials
        self._generate_packaging_materials()
        
        # Generate recent activities
        self._generate_recent_activities()

    def _generate_shipping_orders(self, products, orgs):
        order_statuses = ['Pending', 'Ready for Picking', 'In Progress', 'Ready for Dispatch', 'Dispatched']
        for i in range(15):
            order_id = f'ORD{i+1:04d}'
            status = random.choice(order_statuses[:4])
            items_count = random.randint(1, 5)
            order_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 7))
            
            items = []
            total_value = 0.0
            for _ in range(items_count):
                product = random.choice(products)
                qty = random.randint(1, 10)
                items.append({
                    'product_id': product[0],
                    'product_name': product[2],
                    'quantity': qty,
                    'location': random.choice(['E0-A1', 'E1-B2', 'E2-C3', 'E3-D4'])
                })
                total_value += product[4] * qty

            self.shipping_orders.append({
                'Order_ID': order_id,
                'Status': status,
                'Items_Count': items_count,
                'Order_Date': order_date,
                'Customer_Org_ID': random.choice([o[0] for o in orgs if o[0] != self.emballeur_id]),
                'Items': items,
                'Total_Value': total_value
            })

    def _generate_packaging_materials(self):
        self.packaging_materials = [
            {'Name': 'Small Box', 'ID': 'PM001', 'Quantity': 150, 'Unit': 'pcs'},
            {'Name': 'Medium Box', 'ID': 'PM002', 'Quantity': 100, 'Unit': 'pcs'},
            {'Name': 'Large Box', 'ID': 'PM003', 'Quantity': 50, 'Unit': 'pcs'},
            {'Name': 'Packing Tape', 'ID': 'PM004', 'Quantity': 200, 'Unit': 'rolls'},
            {'Name': 'Bubble Wrap', 'ID': 'PM005', 'Quantity': 75, 'Unit': 'meters'}
        ]

    def _generate_recent_activities(self):
        activity_types = ['Order Prepared', 'Material Used', 'Package Dispatched', 'Material Restocked']
        for i in range(20):
            activity_time = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(1, 120))
            activity_type = random.choice(activity_types)
            description = f"Activity {i+1} related to {activity_type}."
            
            if activity_type == 'Order Prepared':
                order_id = random.choice(self.shipping_orders)['Order_ID']
                description = f"Order {order_id} marked as '{activity_type}'."
            elif activity_type == 'Material Used':
                material = random.choice(self.packaging_materials)
                qty_used = random.randint(1, 10)
                description = f"{qty_used} {material['Unit']} of {material['Name']} used."
                
            self.recent_activities.append({
                'Timestamp': activity_time,
                'Type': activity_type,
                'Description': description
            })

    def update_order_status(self, order_id, new_status):
        for order in self.shipping_orders:
            if order['Order_ID'] == order_id:
                order['Status'] = new_status
                return True
        return False

    def update_material_quantity(self, material_id, new_quantity):
        for material in self.packaging_materials:
            if material['ID'] == material_id:
                material['Quantity'] = new_quantity
                return True
        return False

    def get_emballeur_name(self):
        try:
            self.db.cur.execute('SELECT "EMIR".getorganisationname(%s);', (self.emballeur_id,))
            result = self.db.cur.fetchone()
            return result[0] if result else "Emballeur"
        except psycopg2.Error as e:
            print(f"Error fetching emballeur name: {e}")
            return "Emballeur"