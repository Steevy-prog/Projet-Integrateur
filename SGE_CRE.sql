DROP SCHEMA IF EXISTS "EXTERNE" CASCADE;
CREATE SCHEMA "EXTERNE";
DROP SCHEMA IF EXISTS "SCA" CASCADE;
CREATE SCHEMA "SCA";
DROP SCHEMA IF EXISTS "CREDENTIALS" CASCADE;
CREATE SCHEMA "CREDENTIALS";
REVOKE ALL ON SCHEMA "SCA" FROM PUBLIC;
REVOKE ALL ON SCHEMA "CREDENTIALS" FROM PUBLIC;
CREATE ROLE ITAdmin LOGIN PASSWORD 'hungry';
GRANT USAGE ON SCHEMA "SCA" TO ITAdmin ;
GRANT USAGE ON SCHEMA "CREDENTIALS" TO ITAdmin ;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA "SCA" TO ITAdmin;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA "CREDENTIALS" TO ITAdmin;

CREATE DOMAIN "SCA".Nom TEXT CHECK(
    length(value)<60
    );

CREATE DOMAIN "SCA".idOrg TEXT CHECK (
    VALUE~ '^O[A-Z]{5}$'
    );

CREATE DOMAIN "SCA".Idrapport TEXT CHECK (
    VALUE~ '^R[A-Z]{5}$'
    );

CREATE DOMAIN "SCA".email TEXT CHECK(
    VALUE~ '^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    );

CREATE DOMAIN "SCA".idcontenu TEXT CHECK(
    VALUE~ '^CON[0-9]{3}$'
    );

CREATE DOMAIN "SCA".idpcontenu TEXT CHECK(
    VALUE~ '^PCON[0-9]{3}$'
    );

CREATE DOMAIN "SCA".idinventaire TEXT CHECK(
    VALUE~ '^INV[0-9]{3}$'
    );

CREATE DOMAIN "SCA".idmodele TEXT CHECK(
    VALUE~ '^MOD[0-9]{3}$'
    );

CREATE DOMAIN "SCA".idrepertoire TEXT CHECK(
    VALUE~ '^REP[0-9]{3}$'
    );

CREATE DOMAIN "SCA".password TEXT;

CREATE DOMAIN "SCA".dims DOUBLE PRECISION CHECK (
    VALUE > 0
    );

CREATE DOMAIN "SCA".Idzone TEXT CHECK (
    VALUE~ '^Z[A-Z0-9]{5}$'
    );

CREATE DOMAIN "SCA".Bonrecep TEXT CHECK (
    VALUE~ '^R[A-Z0-9]{5}$'
    );

CREATE DOMAIN "SCA".Idcolis TEXT CHECK (
    VALUE~ '^CO[A-Z0-9]{5}$'
    );

CREATE DOMAIN "SCA".Idcellule TEXT CHECK (
    VALUE~ '^C[A-Z0-9]{5}$'
    );

CREATE DOMAIN "SCA".Bonexped TEXT CHECK (
    VALUE~ '^E[A-Z0-9]{5}$'
    );

CREATE DOMAIN "SCA".IDindividu TEXT CHECK (
    VALUE~ '^I[A-Z0-9]{5}$'
    );

CREATE DOMAIN "SCA".Numero TEXT CHECK(
    VALUE ~ '^6\d{8}$' OR
    VALUE ~ '^\+2376\d{8}$'
    );

CREATE DOMAIN "SCA".Adresse TEXT CHECK (
    length(value)<40
    );

CREATE DOMAIN "SCA".Idlot TEXT CHECK(
    VALUE ~ '^L[A-Z0-9]{5}$'
    );

CREATE DOMAIN "SCA".Idproduit TEXT CHECK(
    VALUE ~ '^P[A-Z0-9]{5}$'
    );

CREATE DOMAIN "SCA".Idproduitmateriel TEXT CHECK(
    VALUE ~ '^PM[A-Z0-9]{4}$'
    );

CREATE DOMAIN "SCA".Idproduitlogiciel TEXT CHECK(
    VALUE ~ '^PL[A-Z0-9]{4}$'
    );

CREATE DOMAIN "SCA".idtache TEXT CHECK (
    VALUE~ '^T[A-Z0-9]{5}$'
    );

CREATE DOMAIN "SCA".idtravailleur TEXT CHECK (
    VALUE~ '^TR[A-Z0-9]{4}$'
    );

CREATE DOMAIN "SCA".idvehicule TEXT CHECK (
    VALUE~ '^V[A-Z0-9]{5}$'
    );

CREATE DOMAIN "SCA".idconducteur TEXT CHECK (
    VALUE~ '^CD[A-Z0-9]{4}$'
    );

CREATE DOMAIN "SCA".idutilisateur TEXT CHECK (
    VALUE~ '^U[A-Z0-9]{5}$'
    );

CREATE DOMAIN "SCA".username TEXT CHECK (
    VALUE~ '^[a-zA-Z0-9_]{3,20}$'
    );

CREATE DOMAIN "EXTERNE".Idpcolis TEXT CHECK (
    VALUE~ '^PCO[A-Z0-9]{5}$'
    );

CREATE DOMAIN "EXTERNE".Idplot TEXT CHECK(
    VALUE ~ '^PL[A-Z0-9]{5}$'
    );

CREATE DOMAIN "EXTERNE".Idinquire TEXT CHECK(
    VALUE ~ '^INQ[A-Z0-9]{4}$'
    );

CREATE TYPE "EXTERNE".etatinq AS ENUM('closed','open','progress','resolved');
CREATE TYPE "EXTERNE".typeinquire AS ENUM('missing package','damaged item','incorrect order','billing issue','general support','other');
CREATE TYPE "SCA".typeOrg AS ENUM('fournisseur','destinataire','SAC');
CREATE TYPE "SCA".etatcolis AS ENUM('Attente','Transit','Livre','Perdu','Endommagé');
CREATE TYPE "SCA".retatcolis AS ENUM('Accepte','Refuse','en attente','Arrive');
CREATE TYPE "SCA".etatexception AS ENUM('Progress','Resolu','Ouvert','Fermé');
CREATE TYPE "SCA".etat AS ENUM('bon etat','mauvais etat','deteriore','livre');
CREATE TYPE "SCA".roles AS ENUM('conducteur','magasinier','acheteur','vendeur','Admin','travailleur','manager','logistic');
CREATE TYPE "SCA".rapports AS ENUM('lors de la verification avant expedition','lors du destockage et assemblage du colis','lors de la preparation du colis pour expedition','lors de la confirmation du stockage','lors de la reception du colis');
CREATE TYPE "SCA".etat_lot AS ENUM('neuf', 'recupere', 'standard');
CREATE TYPE "SCA".condition_materiel AS ENUM ( 'utilisable','a recycler');
CREATE TYPE "SCA".categorie_produit AS ENUM ('produit de vente','materiel d''emballage');
CREATE TYPE "SCA".statut_travailleur AS ENUM ('actif','inactif','en congé','en formation');
CREATE TYPE "SCA".type_vehicule AS ENUM ('camion','fourgon','camionnette','remorque');
CREATE TYPE "SCA".statut_vehicule AS ENUM ('disponible','en maintenance','en livraison','hors service');
CREATE TYPE "SCA".statut_conducteur AS ENUM ('disponible','en livraison','en congé','en formation');
CREATE TYPE "SCA".statut_utilisateur AS ENUM ('actif','inactif','suspendu','en attente_validation');
CREATE TYPE "SCA".niveau_acces AS ENUM ('admin','manager','employe');


CREATE TABLE "SCA".REF_Marque (
    idmarque VARCHAR(50) PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    pays_origine VARCHAR(100),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table REF_Modele
CREATE TABLE "SCA".REF_Modele (
    idmodele "SCA".idmodele PRIMARY KEY,
    idmarque VARCHAR(50) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    type_produit VARCHAR(50),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idmarque) REFERENCES REF_Marque(idmarque) ON DELETE CASCADE
);

-- Table REF_Specialite
CREATE TABLE "SCA".REF_Specialite (
    idspecialite VARCHAR(50) PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table REF_Competence
CREATE TABLE "SCA".REF_Competence (
    idcompetence VARCHAR(50) PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    niveau_requis VARCHAR(50),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE "SCA".Organisation(
  idorganisation "SCA".idOrg NOT NULL ,
  nom "SCA".Nom NOT NULL ,
  telephone "SCA".Numero NOT NULL ,
  type "SCA".typeOrg NOT NULL ,
  CONSTRAINT ORG_CC0 PRIMARY KEY (idorganisation)
);

CREATE TABLE "SCA".Cellule(
  idcellule "SCA".Idcellule NOT NULL ,
  longueur "SCA".dims NOT NULL ,
  largeur "SCA".dims NOT NULL ,
  hauteur "SCA".dims NOT NULL ,
  masse_maximale "SCA".dims NOT NULL ,
  CONSTRAINT Cellule_CC0 PRIMARY KEY (idcellule)
);
CREATE TABLE "SCA".Colis(
  idcolis "SCA".Idcolis NOT NULL ,
  date_creation date NOT NULL ,
  expected_date date NOT NULL,
  receiving_org "SCA".idOrg NOT NULL,
  statut "SCA".etatcolis NOT NULL ,
  CONSTRAINT Colis_CC0 PRIMARY KEY (idcolis)
);
CREATE TABLE "SCA".Zone(
  idzone "SCA".Idzone NOT NULL ,
  nom "SCA".Nom NOT NULL ,
  CONSTRAINT Zone_CC0 PRIMARY KEY (idzone)
);
CREATE TABLE "SCA".individu(
  idindividu "SCA".IDindividu NOT NULL ,
  nom "SCA".Nom NOT NULL ,
  prenom "SCA".Nom NOT NULL ,
  adresse "SCA".Adresse NOT NULL ,
  telephone "SCA".Numero NOT NULL ,
  CONSTRAINT individu_CC0 PRIMARY KEY (idindividu)
);
CREATE TABLE "SCA".Utilisateur(
  idutilisateur "SCA".idutilisateur NOT NULL,
  idindividu "SCA".IDindividu NOT NULL,
  username "SCA".username NOT NULL UNIQUE,
  date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  date_derniere_connexion TIMESTAMP,
  statut "SCA".statut_utilisateur DEFAULT 'en attente_validation',
  niveau_acces "SCA".niveau_acces DEFAULT 'employe',
  CONSTRAINT Utilisateur_CC0 PRIMARY KEY (idutilisateur),
  CONSTRAINT Utilisateur_CR0 FOREIGN KEY (idindividu) REFERENCES "SCA".individu(idindividu) ON DELETE CASCADE
);

CREATE TABLE "SCA".Conducteur(
  idconducteur "SCA".idconducteur NOT NULL,
  idutilisateur "SCA".idutilisateur NOT NULL,
  numero_permis "SCA".Nom NOT NULL UNIQUE,
  type_permis VARCHAR(10) NOT NULL,
  date_obtention_permis DATE NOT NULL,
  date_expiration_permis DATE NOT NULL,
  experience_annees INTEGER DEFAULT 0,
  statut "SCA".statut_conducteur DEFAULT 'disponible',
  date_derniere_evaluation DATE,
  note_evaluation DECIMAL(3,2) CHECK (note_evaluation >= 0 AND note_evaluation <= 5),
  CONSTRAINT Conducteur_CC0 PRIMARY KEY (idconducteur),
  CONSTRAINT Conducteur_CR0 FOREIGN KEY (idutilisateur) REFERENCES "SCA".Utilisateur(idutilisateur) ON DELETE CASCADE
);

CREATE TABLE "SCA".ConducteurSpecialite (
    idconducteur VARCHAR(50) NOT NULL,
    idspecialite VARCHAR(50) NOT NULL,
    date_obtention DATE,
    niveau VARCHAR(50) DEFAULT 'Débutant',
    certifie BOOLEAN DEFAULT FALSE,
    date_expiration DATE,
    PRIMARY KEY (idconducteur, idspecialite),
    FOREIGN KEY (idconducteur) REFERENCES SCA_Conducteur(idconducteur) ON DELETE CASCADE,
    FOREIGN KEY (idspecialite) REFERENCES REF_Specialite(idspecialite) ON DELETE CASCADE
);


CREATE TABLE "SCA".Bonreception(
  idbonreception "SCA".Bonrecep NOT NULL ,
  idcolis "SCA".Idcolis NOT NULL ,
  date_creation DATE NOT NULL ,
  idfournisseur "SCA".idorg NOT NULL ,
  statut "SCA".etat NOT NULL ,
  remarques TEXT NOT NULL ,
  CONSTRAINT Bonreception_CC0 PRIMARY KEY(idbonreception),
  FOREIGN KEY (idcolis)REFERENCES "SCA".Colis(idcolis),
  FOREIGN KEY (idfournisseur)REFERENCES "SCA".Organisation(idorganisation)ON DELETE CASCADE
);
CREATE TABLE "SCA".Bonexpedition(
  idbonexpedition "SCA".Bonexped NOT NULL ,
  idcolis "SCA".Idcolis NOT NULL ,
  idtransporteur "SCA".idconducteur NOT NULL ,
  date_creation DATE NOT NULL ,
  iddestinataire "SCA".idorg NOT NULL ,
  statut "SCA".etat NOT NULL ,
  remarques TEXT NOT NULL ,
  CONSTRAINT Bonexpedition_CC0 PRIMARY KEY(idbonexpedition),
  FOREIGN KEY (idcolis)REFERENCES "SCA".Colis(idcolis),
  FOREIGN KEY (idtransporteur)REFERENCES "SCA".conducteur(idconducteur) ON DELETE CASCADE,
  FOREIGN KEY (iddestinataire)REFERENCES "SCA".Organisation(idorganisation)ON DELETE CASCADE
);
CREATE TABLE "SCA".Repertoire(
  idrepertoire "SCA".idrepertoire, 
  date_debut date, 
  date_fin date,
  idindividu "SCA".IDindividu NOT NULL ,
  idorganisation "SCA".idOrg NOT NULL ,
  role "SCA".roles NOT NULL ,
  CONSTRAINT Repertoire_pk PRIMARY KEY (idrepertoire),
  CONSTRAINT Repertoire_CR0 FOREIGN KEY (idindividu) REFERENCES "SCA".individu(idindividu) ON DELETE CASCADE,
  FOREIGN KEY (idorganisation) REFERENCES "SCA".Organisation(idorganisation) ON DELETE CASCADE
);
CREATE TABLE "SCA".Produit(
  idproduit "SCA".Idproduit NOT NULL ,
  idfournisseur "SCA".idorg NOT NULL ,
  nom "SCA".Nom NOT NULL ,
  description text NOT NULL ,
  prix_unitaire float NOT NULL ,
  idmodele "SCA".idmodele,
  categorie "SCA".categorie_produit DEFAULT 'produit de vente',
  CONSTRAINT Produit_CC0 PRIMARY KEY (idproduit),
  FOREIGN KEY(idfournisseur)REFERENCES "SCA".Organisation(idorganisation) ON DELETE CASCADE,
  FOREIGN KEY(idmodele) REFERENCES "SCA".REF_Modele(idmodele)
);
CREATE TABLE "SCA".ProduitMateriel(
  idproduit "SCA".Idproduit NOT NULL ,
  longueur "SCA".dims NOT NULL ,
  largeur "SCA".dims NOT NULL ,
  hauteur "SCA".dims NOT NULL ,
  masse "SCA".dims NOT NULL ,
  CONSTRAINT ProduitMateriel_CC0 PRIMARY KEY (idproduit),
  CONSTRAINT ProduitMateriel_cr0 FOREIGN KEY (idproduit)REFERENCES "SCA".produit(idproduit) ON DELETE CASCADE
);
CREATE TABLE "SCA".ProduitLogiciel(
  idproduit "SCA".Idproduit NOT NULL ,
  version "SCA".Nom NOT NULL ,
  license "SCA".Nom NOT NULL ,
  CONSTRAINT ProduitLogiciel_CC0 PRIMARY KEY(idproduit),
  FOREIGN KEY (idproduit)REFERENCES "SCA".Produit(idproduit) ON DELETE CASCADE
);
CREATE TABLE "SCA".Lot(
  idlot "SCA".idlot NOT NULL ,
  idproduit "SCA".Idproduit NOT NULL ,
  quantite "SCA".dims NOT NULL ,
  date_creation date NOT NULL ,,
  CONSTRAINT Lot_CC0 PRIMARY KEY (idlot),
  FOREIGN KEY (idproduit) REFERENCES "SCA".Produit(idproduit) ON DELETE CASCADE
);

CREATE TABLE "SCA".LotEmballage(
  idlotemballage SERIAL PRIMARY KEY,
  idproduit "SCA".Idproduit NOT NULL,
  quantite "SCA".dims NOT NULL,
  date_creation DATE NOT NULL,
  statut "SCA".etat_lot DEFAULT 'neuf',
  nbuses INT DEFAULT 0,
  condition "SCA".condition_materiel DEFAULT 'utilisable',
  CONSTRAINT LotEmballage_CR0 FOREIGN KEY (idproduit) REFERENCES "SCA".Produit(idproduit) ON DELETE CASCADE
);

CREATE TABLE "SCA".ContenuColis(
  idcontenu "SCA".idcontenu,
  idcolis "SCA".Idcolis NOT NULL ,
  idlot "SCA".Idlot NOT NULL ,
  date_MAJ date NOT NULL ,
  CONSTRAINT contenucolis_CC0 PRIMARY KEY (idcontenu),
  CONSTRAINT ContenuColis_CR0 FOREIGN KEY (idcolis) REFERENCES "SCA".Colis(idcolis) ON DELETE CASCADE,
  FOREIGN KEY (idlot) REFERENCES "SCA".Lot(idlot) ON DELETE CASCADE
);

CREATE TABLE "SCA".entrepot(
  idcellule "SCA".Idcellule NOT NULL ,
  position "SCA".idzone NOT NULL ,
  CONSTRAINT entrepot_CC0 PRIMARY KEY (idcellule,position),
  CONSTRAINT entrepot_CR0 FOREIGN KEY (idcellule)REFERENCES "SCA".Cellule(idcellule) ON DELETE CASCADE ,
  FOREIGN KEY (position) REFERENCES "SCA".Zone(idzone)  ON DELETE CASCADE
);

CREATE TABLE "SCA".RapportException(
  idrapport "SCA".Idrapport NOT NULL ,
  idcolis "SCA".Idcolis NOT NULL ,
  type "SCA".rapports NOT NULL ,
  date_creation date NOT NULL ,
  description text NOT NULL ,
  statut "SCA".etatexception NOT NULL ,
  CONSTRAINT RapportException_CC0 PRIMARY KEY (idrapport),
  FOREIGN KEY (idcolis) REFERENCES "SCA".Colis(idcolis) ON DELETE CASCADE
);

CREATE TABLE "CREDENTIALS".application_theme(
  theme_name TEXT,
  interface TEXT,
  theme_qss TEXT,
  CONSTRAINT application_theme_CC0 PRIMARY KEY (theme_name, interface)
);

CREATE TABLE "SCA".InventaireEmplacement(
  idinventaire "SCA".idinventaire,
  idcellule "SCA".Idcellule NOT NULL ,
  idlot "SCA".Idlot NOT NULL ,
  datemaj date NOT NULL ,
  CONSTRAINT InventaireEmplacement_CC0 PRIMARY KEY (idinventaire),
  CONSTRAINT InventaireEmplacement_CR0 FOREIGN KEY (idcellule)REFERENCES "SCA".cellule(idcellule) ON DELETE CASCADE,
  FOREIGN KEY (idlot)REFERENCES "SCA".Lot(idlot) ON DELETE CASCADE
);
CREATE TABLE "SCA".Travailleur(
  idtravailleur "SCA".idtravailleur NOT NULL,
  idutilisateur "SCA".idutilisateur NOT NULL,
  date_embauche DATE NOT NULL,
  poste "SCA".Nom NOT NULL,
  departement "SCA".Nom NOT NULL,
  salaire_horaire DECIMAL(10,2) NOT NULL,
  statut "SCA".statut_travailleur DEFAULT 'actif',
  date_derniere_evaluation DATE NOT NULL,
  CONSTRAINT Travailleur_CC0 PRIMARY KEY (idtravailleur),
  CONSTRAINT Travailleur_CR0 FOREIGN KEY (idutilisateur) REFERENCES "SCA".Utilisateur(idutilisateur) ON DELETE CASCADE
);

CREATE TABLE "SCA".TravailleurCompetence (
    idtravailleur VARCHAR(50) NOT NULL,
    idcompetence VARCHAR(50) NOT NULL,
    niveau_maitrise VARCHAR(50) DEFAULT 'Débutant',
    date_acquisition DATE,
    certifie BOOLEAN DEFAULT FALSE,
    date_derniere_evaluation DATE,
    PRIMARY KEY (idtravailleur, idcompetence),
    FOREIGN KEY (idtravailleur) REFERENCES SCA_Travailleur(idtravailleur) ON DELETE CASCADE,
    FOREIGN KEY (idcompetence) REFERENCES REF_Competence(idcompetence) ON DELETE CASCADE
);

CREATE TABLE "SCA".Tache(
  idtache "SCA".idtache NOT NULL ,
  idtravailleur "SCA".idtravailleur NOT NULL ,
  idcellule "SCA".Idcellule NOT NULL ,
  idcolis "SCA".Idcolis NOT NULL ,
  date_creation DATE NOT NULL ,
  date_echeance DATE NOT NULL ,
  duree_estimee INT NOT NULL ,
  description TEXT NOT NULL ,
  priority text not null,
  statut text NOT NULL DEFAULT 'en cours',
  type text not null,
  CONSTRAINT Tache_CC0 PRIMARY KEY (idtache),
  CONSTRAINT Tache_CR0 FOREIGN KEY (idtravailleur) REFERENCES "SCA".Travailleur(idtravailleur) ON DELETE CASCADE,
  CONSTRAINT Tache_CR1 FOREIGN KEY (idcellule) REFERENCES "SCA".Cellule(idcellule) ON DELETE CASCADE,
  CONSTRAINT Tache_CR2 FOREIGN KEY (idcolis) REFERENCES "SCA".Colis(idcolis) ON DELETE CASCADE
);


CREATE TABLE "SCA".Vehicule(
  idvehicule "SCA".idvehicule NOT NULL,
  immatriculation "SCA".Nom NOT NULL UNIQUE,
  idmodele "SCA".idmodele,
  annee_fabrication INTEGER NOT NULL,
  types "SCA".type_vehicule NOT NULL,
  capacite_charge "SCA".dims NOT NULL,
  capacite_volume "SCA".dims NOT NULL,
  date_acquisition DATE NOT NULL,
  statut "SCA".statut_vehicule DEFAULT 'disponible',
  kilometrage_actuel DECIMAL(10,2) DEFAULT 0,
  date_derniere_maintenance DATE,
  prochaine_maintenance DATE,
  carburant VARCHAR(20) DEFAULT 'Diesel',
  CONSTRAINT Vehicule_CC0 PRIMARY KEY (idvehicule),
  FOREIGN KEY (idmodele) REFERENCES "SCA".REF_Modele(idmodele)
);

CREATE TABLE "SCA".ConsommationVehicule (
    idconsommation VARCHAR(50) PRIMARY KEY,
    idvehicule VARCHAR(50) NOT NULL,
    consommation_moyenne DECIMAL(5,2) NOT NULL,
    date_mesure DATE NOT NULL,
    conditions_mesure TEXT,
    kilometrage_debut DECIMAL(10,2),
    kilometrage_fin DECIMAL(10,2),
    litres_consommes DECIMAL(8,2),
    type_trajet VARCHAR(50), -- urbain, autoroute, mixte
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idvehicule) REFERENCES SCA_Vehicule(idvehicule) ON DELETE CASCADE
);

CREATE TABLE "CREDENTIALS".PasswordPolicies (
  setting_name VARCHAR(100) NOT NULL UNIQUE,
  setting_value VARCHAR(100) NOT NULL,
  setting_group VARCHAR(100) NOT NULL,
  description VARCHAR(100) NOT NULL,
  CONSTRAINT PK_PasswordPolicies PRIMARY KEY (setting_name)
);

CREATE TABLE "CREDENTIALS".Credentials(
  email "SCA".email NOT NULL,
  mot_de_passe_hash TEXT NOT NULL,
  idutilisateur "SCA".idutilisateur UNIQUE NOT NULL,
  date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT Credentials_CC0 PRIMARY KEY (email),
  CONSTRAINT Credentials_CR0 FOREIGN KEY (idutilisateur) REFERENCES "SCA".Utilisateur(idutilisateur) ON DELETE CASCADE
);

CREATE TABLE "CREDENTIALS".organisation(
  idorganisation "SCA".idOrg NOT NULL,
  mdpOrg TEXT,
  CONSTRAINT org_pk PRIMARY KEY (idorganisation),
  CONSTRAINT org_fk FOREIGN KEY (idorganisation) REFERENCES "SCA".Organisation(idorganisation)
);

CREATE TABLE "SCA".Logs (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  level VARCHAR(10),            -- e.g. 'INFO', 'ERROR', 'DEBUG'
  message TEXT,
);

-- Table SCA_LogsExtra
CREATE TABLE "SCA".LogsExtra (
    id SERIAL PRIMARY KEY,
    log_id INTEGER NOT NULL,
    cle VARCHAR(100) NOT NULL,
    valeur TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (log_id) REFERENCES SCA_Logs(id) ON DELETE CASCADE
);


CREATE TABLE "SCA".LocalisationOrganisation (
  idlocalisation SERIAL PRIMARY KEY,
  idorganisation "SCA".idOrg NOT NULL,
  adresse "SCA".Adresse NOT NULL ,
  ville VARCHAR(60),
  region VARCHAR(60),
  pays VARCHAR(60) DEFAULT 'Cameroun',
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  date_ajout DATE DEFAULT CURRENT_DATE,
  CONSTRAINT LocalisationOrganisation_CR0 FOREIGN KEY (idorganisation) REFERENCES "SCA".Organisation(idorganisation) ON DELETE CASCADE
);

CREATE TABLE "SCA".LivraisonConducteurColis (
  idlivraison SERIAL PRIMARY KEY,
  idconducteur "SCA".idconducteur NOT NULL,
  idbonexpedition "SCA".Bonexped NOT NULL,
  date_affectation DATE DEFAULT CURRENT_DATE,
  statut "SCA".etatcolis DEFAULT 'Attente',
  CONSTRAINT fk_conducteur FOREIGN KEY (idconducteur) REFERENCES "SCA".Conducteur(idconducteur) ON DELETE CASCADE,
  CONSTRAINT fk_colis FOREIGN KEY (idbonexpedition) REFERENCES "SCA".Bonexpedition(idbonexpedition) ON DELETE CASCADE
);

CREATE TABLE "EXTERNE".Colis(
  idorg "SCA".idorg not null,
  idpcolis "EXTERNE".Idpcolis NOT NULL ,
  date_creation date NOT NULL ,
  expected_date date NOT NULL,
  receiving_org "SCA".idorg NOT NULL,
  statut "SCA".retatcolis NOT NULL ,
  CONSTRAINT PColis_CC0 PRIMARY KEY (idpcolis) on delete CASCADE
  CONSTRAINT PColis_CR0 FOREIGN KEY (idorg) REFERENCES "SCA".Organisation(idorganisation)
);
CREATE TABLE "EXTERNE".Lot(
  idorg "SCA".idorg not null,
  idplot "EXTERNE".idplot NOT NULL ,
  idproduit "SCA".Idproduit NOT NULL ,
  quantite "SCA".dims NOT NULL ,
  date_creation date NOT NULL ,
  statut "SCA".etat_lot DEFAULT 'standard',
  CONSTRAINT PLot_CC0 PRIMARY KEY (idplot),
  FOREIGN KEY (idproduit) REFERENCES "SCA".Produit(idproduit) ON DELETE CASCADE
);
CREATE TABLE "EXTERNE".ContenuColis(
  idpcontenu "SCA".idpcontenu,
  idorg "SCA".idorg NOT NULL,
  idpcolis "EXTERNE".Idpcolis NOT NULL ,
  idplot "EXTERNE".Idplot NOT NULL ,
  date_MAJ date NOT NULL ,
  CONSTRAINT pcontenucolis_CC0 PRIMARY KEY (idpcontenu),
  CONSTRAINT pContenuColis_CR0 FOREIGN KEY (idpcolis) REFERENCES "EXTERNE".Colis(idpcolis) ON DELETE CASCADE,
  CONSTRAINT pContenuColis_CR1 FOREIGN KEY (idplot) REFERENCES "EXTERNE".Lot(idplot) ON DELETE CASCADE,
  CONSTRAINT pContenuColis_CR2 FOREIGN KEY (idorg) REFERENCES "SCA".Organisation(idorganisation) ON DELETE CASCADE
);

CREATE TABLE "EXTERNE".inquiries (
    idutilisateur "SCA".idutilisateur NOT NULL,
    idinq         "EXTERNE".Idinquire NOT NULL,
    type          "EXTERNE".typeinquire NOT NULL,
    period        timestamp NOT NULL,
    status        "EXTERNE".etatinq NOT NULL,
    description   text,
    CONSTRAINT inq_pk PRIMARY KEY (idinq),
    FOREIGN KEY (idutilisateur) REFERENCES "SCA".Utilisateur(idutilisateur)
);

CREATE TABLE "SCA".Bugreport (
  id SERIAL PRIMARY KEY,
  idutilisateur "SCA".idutilisateur NOT NULL,

  description TEXT NOT NULL,
  date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  statut "EXTERNE".etatinq DEFAULT 'closed',
  CONSTRAINT fk_utilisateur FOREIGN KEY (idutilisateur) REFERENCES "SCA".Utilisateur(idutilisateur) ON DELETE CASCADE
);