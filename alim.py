import json
import psycopg2
from psycopg2.extras import execute_batch
import os

script_path = os.path.abspath(__file__)
# 📦 Charger le fichier JSON
# Assurez-vous que le chemin vers votre fichier 'jdd.JSON' est correct
with open(os.path.join(os.path.dirname(script_path), 'jdd.JSON'), 'r', encoding='utf-8') as f:
    data = json.load(f)

# 🗄️ Connexion à PostgreSQL (adapte les infos)
conn = psycopg2.connect(
    host="dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com",
    database="projet_integrateur",
    user="group13",
    password="nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3",
    port=5432
)

cur = conn.cursor()
# Schéma cible
schema = 'SCA'

def lister_tables(schema):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_type = 'BASE TABLE'
        """, (schema,))
        tables = cur.fetchall()
        print(f"Tables dans le schéma '{schema}' :")
        for table in tables:
            print(f" - {table[0]}")

lister_tables(schema)

# 📥 Fonction d’insertion en batch (pas de changement ici)
def insert(table, cols, rows):
    # Utilise ON CONFLICT DO NOTHING pour éviter les erreurs si les données existent déjà
    placeholders = ", ".join(["%s"] * len(cols))
    cols_sql = ", ".join([f'"{c}"' for c in cols])  # Ajout de guillemets pour la casse
    sql = f"INSERT INTO {table} ({cols_sql}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

    # Vérifier que la liste de lignes n'est pas vide avant d'exécuter
    if rows:
        execute_batch(cur, sql, rows)


# ➕ Préparation des données à insérer
sc = data["SCA"]

# Utilisation de noms de table qualifiés par le schéma (ex: '"SCA"."Organisation"')
# et de noms de colonnes entre guillemets pour respecter la casse.

insert('"SCA".Organisation',
       ["idorganisation", "nom", "telephone", "type"],
       [(o["idorganisation"], o["nom"], o["telephone"], o["type"])
        for o in sc["Organisation"]])

# Insertion dans LocalisationOrganisation (nouvelle table)
if "LocalisationOrganisation" in sc:
    insert('"SCA".LocalisationOrganisation',
        ["idorganisation", "adresse", "ville", "region", "pays", "latitude", "longitude", "date_ajout"],
        [
            (
                l["idorganisation"],
                l["adresse"],
                l["ville"],
                l["region"],
                l["pays"],
                l["latitude"],
                l["longitude"],
                l["date_ajout"]
            )
            for l in sc["LocalisationOrganisation"]
        ])

insert('"SCA".Cellule',
       ["idcellule", "longueur", "largeur", "hauteur", "masse_maximale"],
       [(c["idcellule"], c["longueur"], c["largeur"], c["hauteur"], c["masse_maximale"])
        for c in sc["Cellule"]])

insert('"SCA".Colis',
       ["idcolis", "date_creation", "statut"],
       [(c["idcolis"], c["date_creation"], c["statut"])
        for c in sc["Colis"]])

insert('"SCA".Zone',
       ["idzone", "nom"],
       [(z["idzone"], z["nom"]) for z in sc["Zone"]])

insert('"SCA".individu',
       ["idindividu", "nom", "adresse", "telephone"],
       [(i["idindividu"], i["nom"], i["adresse"], i["telephone"])
        for i in sc["individu"]])

insert('"SCA".Repertoire',
       ["idindividu", "idorganisation", "role"],
       [(r["idindividu"], r["idorganisation"], r["role"])
        for r in sc["Repertoire"]])

insert('"SCA".Produit',
       ["idproduit", "idfournisseur", "nom", "description", "prix_unitaire", "marque", "modele", "categorie"],
       [(p["idproduit"], p["idfournisseur"], p["nom"], p["description"],
         p["prix_unitaire"], p["marque"], p["modele"], p["categorie"])
        for p in sc["Produit"]])

insert('"SCA".ProduitMateriel',
       ["idproduit", "longueur", "largeur", "hauteur", "masse"],
       [(m["idproduit"], m["longueur"], m["largeur"], m["hauteur"], m["masse"])
        for m in sc["ProduitMateriel"]])

insert('"SCA".ProduitLogiciel',
       ["idproduit", "version", "license"],
       [(l["idproduit"], l["version"], l["license"])
        for l in sc["ProduitLogiciel"]])

insert('"SCA".Lot',
       ["idlot", "idproduit", "quantite", "date_creation", "statut", "origine", "nombre_utilisations", "condition"],
       [(l["idlot"], l["idproduit"], l["quantite"], l["date_creation"],
         l["statut"], l["origine"], l["nombre_utilisations"], l["condition"])
        for l in sc["Lot"]])

insert('"SCA".ContenuColis',
       ["idcolis", "idlot", "quantite", "date_maj"],
       [(c["idcolis"], c["idlot"], c["quantite"], c["date_MAJ"])
        for c in sc["ContenuColis"]])

insert('"SCA".InventaireEmplacement',
       ["idcellule", "idlot", "quantite", "datemaj"],
       [(i["idcellule"], i["idlot"], i["quantite"], i["datemaj"])
        for i in sc["InventaireEmplacement"]])

insert('"SCA".Bonreception',
       ["idbonreception", "idcolis", "idtransporteur", "date_creation", "idfournisseur", "statut", "remarques"],
       [(b["idbonreception"], b["idcolis"], b["idtransporteur"], b["date_creation"],
         b["idfournisseur"], b["statut"], b["remarques"])
        for b in sc["Bonreception"]])

insert('"SCA".Bonexpedition',
       ["idbonexpedition", "idcolis", "idtransporteur", "date_creation", "iddestinataire", "statut", "remarques"],
       [(b["idbonexpedition"], b["idcolis"], b["idtransporteur"], b["date_creation"],
         b["iddestinataire"], b["statut"], b["remarques"])
        for b in sc["Bonexpedition"]])

# CORRECTION: La colonne s'appelle 'type' dans le JSON, et doit correspondre à la colonne 'type' de la table.
insert('"SCA".RapportException',
       ["idrapport", "idcolis", "type", "date_creation", "description", "statut"],
       [(r["idrapport"], r["idcolis"], r["type"], r["date_creation"], r["description"], r["statut"])
        for r in sc["RapportException"]])

insert('"SCA".entrepot',
       ["idcellule", "position"],
       [(e["idcellule"], e["position"]) for e in sc["entrepot"]])

# 🔐 Credentials et policies
cred = data["CREDENTIALS"]

insert('"CREDENTIALS".PasswordPolicies',
       ["nom_policy", "min_length", "max_length", "require_uppercase", "require_lowercase",
        "require_digit", "require_special_char", "min_special_chars", "allowed_special_chars", "disallowed_chars",
        "prevent_common_passwords"],
       [(p["nom_policy"], p["min_length"], p["max_length"],
         p["require_uppercase"], p["require_lowercase"], p["require_digit"],
         p["require_special_char"], p["min_special_chars"], p["allowed_special_chars"],
         p.get("disallowed_chars"), p["prevent_common_passwords"])
        for p in cred["PasswordPolicies"]])

insert('"CREDENTIALS".Credentials',
       ["email", "password", "nom_policy", "idindividu"],
       [(c["email"], c["password"], c["nom_policy"], c["idindividu"])
        for c in cred["Credentials"]])

# CORRECTION: La table s'appelle 'organisation' et non 'OrganisationCred'.
insert('"CREDENTIALS".organisation',
       ["idorganisation", "mdporg"],
       [(o["idorganisation"], o["mdpOrg"])
        for o in cred["organisation"]])

# Cette table n'a pas de schéma spécifié, donc elle est probablement dans le schéma 'public'.
# Pas besoin de préfixe de schéma si 'public' est dans le search_path.
insert('"CREDENTIALS".application_theme',
       ["theme_name", "interface", "theme_qss"],
       [(t["theme_name"], t["window"], t["theme_qss"])
        for t in data["application_theme"]])

# ✅ Finalisation
conn.commit()
cur.close()
conn.close()
print("Import JSON terminé avec succès.")
