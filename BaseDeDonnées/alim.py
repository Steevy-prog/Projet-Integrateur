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
#conn = psycopg2.connect(
#    host="dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com",
#    database="projet_integrateur",
#    user="group13",
#    password="nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3",
#    port=5432
#)

global conn
print("1. online")
print("2. offline")
it = input("Enter the number of bd you want to use : ")
if it == '0':
    conn = psycopg2.connect(
        host = "dpg-d1b612gdl3ps73eapfr0-a.oregon-postgres.render.com",
        database = "test_bpdd",
        user = "test",
        password = "w95g3tjqj0S9DLwNiaFEMb1SACWuuIjh",
        port = 5432)

if it == '1':
    print("You have chosen the online database.")
    conn = psycopg2.connect(
        host="dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com",
        database="projet_integrateur",
        user="group13",
        password="nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3",
        port=5432
    )
elif it == '2':
    print("You have chosen the Steevy's database.")
    conn = psycopg2.connect(
        host="localhost",
        database="USER",
        user="postgres",
        password="steevy",
        port=5432
    )

elif it == '3':
    print("You have chosen the Viktor's database.")
    conn = psycopg2.connect(
        host="localhost",
        database="Projet",
        user="postgres",
        password="Lune.Hatik123",
        port=5432
    )

cur = conn.cursor()

# 🔄 Fonction pour tronquer toutes les tables avant insertion
def truncate_all_tables():
    """Tronque toutes les tables dans l'ordre pour respecter les contraintes de clés étrangères"""
    print("🗑️  Troncature des tables en cours...")
    
    # Liste des tables dans l'ordre inverse des dépendances (tables enfants en premier)
    tables_to_truncate = [
        # Tables EXTERNE
        '"EXTERNE".ContenuColis',
        '"EXTERNE".Lot',
        '"EXTERNE".Colis',
        
        # Tables CREDENTIALS
        '"CREDENTIALS".organisation',
        '"CREDENTIALS".Credentials',
        '"CREDENTIALS".PasswordPolicies',
        
        # Tables SCA (tables enfants en premier)
        '"SCA".LivraisonConducteurColis',
        '"SCA".ConsommationVehicule',
        '"SCA".entrepot',
        '"SCA".RapportException',
        '"SCA".Bonexpedition',
        '"SCA".Bonreception',
        '"SCA".Tache',
        '"SCA".InventaireEmplacement',
        '"SCA".ContenuColis',
        '"SCA".LotEmballage',
        '"SCA".Lot',
        '"SCA".ProduitLogiciel',
        '"SCA".ProduitMateriel',
        '"SCA".Produit',
        '"SCA".Repertoire',
        '"SCA".ConducteurSpecialite',
        '"SCA".Conducteur',
        '"SCA".Vehicule',
        '"SCA".TravailleurCompetence',
        '"SCA".Travailleur',
        '"SCA".Utilisateur',
        '"SCA".individu',
        '"SCA".Zone',
        '"SCA".Colis',
        '"SCA".Cellule',
        '"SCA".LocalisationOrganisation',
        '"SCA".Organisation',
        '"SCA".REF_Competence',
        '"SCA".REF_Specialite',
        '"SCA".REF_Modele',
        '"SCA".REF_Marque',
    ]
    
    try:
        for table in tables_to_truncate:
            try:
                # Utiliser DELETE au lieu de TRUNCATE pour éviter les problèmes de privilèges
                cur.execute(f"DELETE FROM {table};")
                print(f"✅ Table {table} vidée")
            except Exception as e:
                print(f"⚠️  Erreur lors du vidage de {table}: {e}")
    except Exception as e:
        print(f"❌ Erreur générale lors de la troncature: {e}")
    finally:
        conn.commit()
    
    print("✅ Troncature terminée")

# Exécuter la troncature
truncate_all_tables()

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

# 📥 Fonction d'insertion en batch (pas de changement ici)
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

# Insertion des tables de référence en premier
insert('"SCA".REF_Marque',
       ["idmarque", "nom", "pays_origine", "date_creation"],
       [(m["idmarque"], m["nom"], m["pays_origine"], m["date_creation"])
        for m in sc["REF_Marque"]])

insert('"SCA".REF_Modele',
       ["idmodele", "idmarque", "nom", "type_produit", "date_creation"],
       [(m["idmodele"], m["idmarque"], m["nom"], m["type_produit"], m["date_creation"])
        for m in sc["REF_Modele"]])

insert('"SCA".REF_Specialite',
       ["idspecialite", "nom", "description", "date_creation"],
       [(s["idspecialite"], s["nom"], s["description"], s["date_creation"])
        for s in sc["REF_Specialite"]])

insert('"SCA".REF_Competence',
       ["idcompetence", "nom", "description", "niveau_requis", "date_creation"],
       [(c["idcompetence"], c["nom"], c["description"], c["niveau_requis"], c["date_creation"])
        for c in sc["REF_Competence"]])

# Utilisation de noms de table qualifiés par le schéma (ex: '"SCA"."Organisation"')
# et de noms de colonnes entre guillemets pour respecter la casse.

insert('"SCA".Organisation',
       ["idorganisation", "nom", "telephone", "type"],
       [(o["idorganisation"], o["nom"], o["telephone"], o["type"])
        for o in sc["Organisation"]])

# Insertion dans LocalisationOrganisation
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
       ["idcolis", "date_creation","expected_date","receiving_org", "statut"],
       [(c["idcolis"], c["date_creation"],c["expected_date"], c["receiving_org"],c["statut"])
        for c in sc["Colis"]])                                 

insert('"SCA".Zone',
       ["idzone", "nom"],
       [(z["idzone"], z["nom"]) for z in sc["Zone"]])

insert('"SCA".individu',
       ["idindividu", "nom", "prenom", "adresse", "telephone"],
       [(i["idindividu"], i["nom"], i["prenom"], i["adresse"], i["telephone"])
        for i in sc["individu"]])

insert('"SCA".Utilisateur',
       ["idutilisateur", "idindividu", "username", "date_inscription", "date_derniere_connexion", "statut", "niveau_acces"],
       [
           (
               u["idutilisateur"],
               u["idindividu"],
               u["username"],
               u["date_inscription"],
               u["date_derniere_connexion"],
               u["statut"],
               u["niveau_acces"]
           )
           for u in sc["Utilisateur"]
       ])

insert('"SCA".Travailleur',
       ["idtravailleur", "idutilisateur", "date_embauche", "poste", "departement", "salaire_horaire", "statut", "date_derniere_evaluation"],
       [(
           t["idtravailleur"],
           t["idutilisateur"],
           t["date_embauche"],
           t["poste"],
           t["departement"],
           t["salaire_horaire"],
           t["statut"],
           t["date_derniere_evaluation"]
        ) for t in sc["Travailleur"]])

insert('"SCA".TravailleurCompetence',
       ["idtravailleur", "idcompetence", "niveau_maitrise", "date_acquisition", "certifie", "date_derniere_evaluation"],
       [(
           tc["idtravailleur"],
           tc["idcompetence"],
           tc["niveau_maitrise"],
           tc["date_acquisition"],
           tc["certifie"],
           tc["date_derniere_evaluation"]
        ) for tc in sc["TravailleurCompetence"]])

insert('"SCA".Vehicule',
       ["idvehicule", "immatriculation", "idmodele", "annee_fabrication", "types", "capacite_charge", "capacite_volume", "date_acquisition", "statut", "kilometrage_actuel", "date_derniere_maintenance", "prochaine_maintenance", "carburant"],
       [(
           v["idvehicule"],
           v["immatriculation"],
           v["idmodele"],
           v["annee_fabrication"],
           v["types"],
           v["capacite_charge"],
           v["capacite_volume"],
           v["date_acquisition"],
           v["statut"],
           v["kilometrage_actuel"],
           v["date_derniere_maintenance"],
           v["prochaine_maintenance"],
           v["carburant"]
        ) for v in sc["Vehicule"]])

insert('"SCA".Conducteur',
       ["idconducteur", "idutilisateur", "numero_permis", "type_permis", "date_obtention_permis", "date_expiration_permis", "experience_annees", "statut", "date_derniere_evaluation", "note_evaluation"],
       [(
           c["idconducteur"],
           c["idutilisateur"],
           c["numero_permis"],
           c["type_permis"],
           c["date_obtention_permis"],
           c["date_expiration_permis"],
           c["experience_annees"],
           c["statut"],
           c["date_derniere_evaluation"],
           c["note_evaluation"]
        ) for c in sc["Conducteur"]])

insert('"SCA".ConducteurSpecialite',
       ["idconducteur", "idspecialite", "date_obtention", "niveau", "certifie", "date_expiration"],
       [(
           cs["idconducteur"],
           cs["idspecialite"],
           cs["date_obtention"],
           cs["niveau"],
           cs["certifie"],
           cs["date_expiration"]
        ) for cs in sc["ConducteurSpecialite"]])

insert('"SCA".Repertoire',
       ["idrepertoire","date_debut","date_fin","idindividu", "idorganisation", "role"],
       [(r["idrepertoire"],r["date_debut"],r["date_fin"],r["idindividu"], r["idorganisation"], r["role"])
        for r in sc["Repertoire"]])

insert('"SCA".Produit',
       ["idproduit", "idfournisseur", "nom", "description", "prix_unitaire", "idmodele", "categorie"],
       [(p["idproduit"], p["idfournisseur"], p["nom"], p["description"],
         p["prix_unitaire"], p["idmodele"], p["categorie"])
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
       ["idlot", "idproduit", "quantite", "date_creation"],
       [(l["idlot"], l["idproduit"], l["quantite"], l["date_creation"])
        for l in sc["Lot"]])

insert('"SCA".LotEmballage',
       ["idlotemballage", "idproduit", "quantite", "date_creation", "statut", "nbuses", "condition"],
       [(le["idlotemballage"], le["idproduit"], le["quantite"], le["date_creation"],
         le["statut"], le["nbuses"], le["condition"])
        for le in sc["LotEmballage"]])

insert('"SCA".ContenuColis',
       ["idcontenu","idcolis", "idlot", "date_maj"],
       [(c["idcontenu"], c["idcolis"], c["idlot"], c["date_MAJ"])
        for c in sc["ContenuColis"]])

insert('"SCA".InventaireEmplacement',
       ["idinventaire", "idcellule", "idlot", "datemaj"],
       [(i["idinventaire"], i["idcellule"], i["idlot"], i["datemaj"])
        for i in sc["InventaireEmplacement"]])

insert('"SCA".Tache',
       ["idtache", "idtravailleur", "idcellule", "idlot", "date_creation", "date_echeance", "duree_estimee", "description", "priority", "statut", "type"],
       [(
           t["idtache"],
           t["idtravailleur"],
           t["idcellule"],
           t["idlot"],
           t["date_creation"],
           t["date_echeance"],
           t["duree_estimee"],
           t["description"],
           t["priority"],
           t["statut"],
           t["type"]
        ) for t in sc["Tache"]])

insert('"SCA".Bonreception',
       ["idbonreception", "idcolis", "date_creation", "idfournisseur", "statut", "remarques"],
       [(b["idbonreception"], b["idcolis"], b["date_creation"],
         b["idfournisseur"], b["statut"], b["remarques"])
        for b in sc["Bonreception"]])

insert('"SCA".Bonexpedition',
       ["idbonexpedition", "idcolis", "idtransporteur", "date_creation", "iddestinataire", "statut", "remarques"],
       [(b["idbonexpedition"], b["idcolis"], b["idtransporteur"], b["date_creation"],
         b["iddestinataire"], b["statut"], b["remarques"])
        for b in sc["Bonexpedition"]])

insert('"SCA".RapportException',
       ["idrapport", "idcolis", "type", "date_creation", "description", "statut"],
       [(r["idrapport"], r["idcolis"], r["type"], r["date_creation"], r["description"], r["statut"])
        for r in sc["RapportException"]])

insert('"SCA".entrepot',
       ["idcellule", "position"],
       [(e["idcellule"], e["position"]) for e in sc["entrepot"]])

insert('"SCA".LivraisonConducteurColis',
       ["idconducteur","idbonexpedition","date_affectation","statut"],
       [(f["idconducteur"], f["idbonexpedition"], f["date_affectation"], f["statut"]) for f in sc["LivraisonConducteurColis"]])

insert('"SCA".ConsommationVehicule',
       ["idconsommation","idvehicule","consommation_moyenne" ,"date_mesure","conditions_mesure", "kilometrage_debut", "kilometrage_fin", "litres_consommes", "type_trajet", "date_creation"],
       [(cv["idconsommation"], cv["idvehicule"], cv["consommation_moyenne"], cv["date_mesure"],cv["conditions_mesure"], cv["kilometrage_debut"], cv["kilometrage_fin"], 
         cv["litres_consommes"], cv["type_trajet"], cv["date_creation"])
        for cv in sc["ConsommationVehicule"]])

# 🔐 Credentials et policies
cred = data["CREDENTIALS"]

insert('"CREDENTIALS".PasswordPolicies',
       ["setting_name", "setting_value", "setting_group", "description"],
       [(p["setting_name"], p["setting_value"], p["setting_group"], p["description"])
        for p in cred["PasswordPolicies"]])

insert('"CREDENTIALS".Credentials',
       ["email", "mot_de_passe_hash", "idutilisateur", "date_creation"],
       [(c["email"], c["mot_de_passe_hash"], c["idutilisateur"], c["date_creation"])
        for c in cred["Credentials"]])

insert('"CREDENTIALS".organisation',
       ["idorganisation", "mdporg"],
       [(o["idorganisation"], o["mdpOrg"])
        for o in cred["organisation"]])

insert('"CREDENTIALS".application_theme',
       ["theme_name", "interface", "theme_qss"],
       [(t["theme_name"], t["window"], t["theme_qss"])
        for t in data["application_theme"]])

ext = data["EXTERNE"]

insert('"EXTERNE".Colis',
       ["idorg","idpcolis", "date_creation", "expected_date","receiving_org", "statut"],
       [(c["idorg"],c["idpcolis"], c["date_creation"], c["expected_date"],c["receiving_org"], c["statut"])
        for c in ext["Colis"]])

insert('"EXTERNE".Lot',
       ["idorg","idplot", "idproduit", "quantite", "date_creation", "statut"],
       [(l["idorg"],l["idplot"], l["idproduit"], l["quantite"], l["date_creation"],
         l["statut"])
        for l in ext["Lot"]])

insert('"EXTERNE".ContenuColis',
       ["idpcontenu","idorg","idpcolis", "idplot", "date_maj"],
       [(c["idpcontenu"],c["idorg"],c["idpcolis"], c["idplot"], c["date_MAJ"])
        for c in ext["ContenuColis"]])

# ✅ Finalisation
conn.commit()
cur.close()
conn.close()
print("Import JSON terminé avec succès.")
