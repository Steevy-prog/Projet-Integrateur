 --script de création du schéma de base
--domaines, types, tables
DROP SCHEMA IF EXISTS "EXTERNE" CASCADE;
CREATE SCHEMA "EXTERNE";
DROP SCHEMA IF EXISTS "SCA" CASCADE;
CREATE SCHEMA "SCA";
DROP SCHEMA IF EXISTS "CREDENTIALS" CASCADE;
CREATE SCHEMA "CREDENTIALS";

-- Révoquer tous les droits publics sur les schémas
REVOKE ALL ON SCHEMA "SCA" FROM PUBLIC;
REVOKE ALL ON SCHEMA "CREDENTIALS" FROM PUBLIC;
-- Créer un nouveau rôle
CREATE ROLE ITAdmin LOGIN PASSWORD 'hungry';
-- Accorder l'usage du schéma SCA au rôle
GRANT USAGE ON SCHEMA "SCA" TO ITAdmin ;
GRANT USAGE ON SCHEMA "CREDENTIALS" TO ITAdmin ;
-- Accorder les droits sur les tables existantes dans SCA
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
CREATE DOMAIN "SCA".password TEXT;

CREATE DOMAIN "SCA".dims DOUBLE PRECISION CHECK (
    VALUE>0
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
CREATE DOMAIN "EXTERNE".Idpcolis TEXT CHECK (
    VALUE~ '^PCO[A-Z0-9]{5}$'
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
CREATE DOMAIN "EXTERNE".Idplot TEXT CHECK(
    VALUE ~ '^PL[A-Z0-9]{5}$'
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
CREATE DOMAIN "EXTERNE".Idinquire TEXT CHECK(
    VALUE ~ '^INQ[A-Z0-9]{4}$'
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
CREATE TYPE "SCA".typeOrg AS ENUM('fournisseur','destinataire','SAC');
CREATE TYPE "EXTERNE".typeinquire AS ENUM('missing package','damaged item','incorrect order','billing issue','general support','other');
CREATE TYPE "SCA".etatcolis AS ENUM('Attente','Transit','Livre','Perdu','Endommagé');
CREATE TYPE "SCA".retatcolis AS ENUM('Accepte','Refuse','en attente','Arrive');
CREATE TYPE "EXTERNE".etatinq AS ENUM('closed','open','progress','resolved');
CREATE TYPE "SCA".etatexception AS ENUM('Progress','Resolu','Ouvert','Fermé');
CREATE TYPE "SCA".etat AS ENUM('bon etat','mauvais etat','deteriore','livre');
CREATE TYPE "SCA".roles AS ENUM('conducteur','magasinier','acheteur','vendeur','Admin','travailleur','manager','logistic');
CREATE TYPE "SCA".rapports AS ENUM('lors de la verification avant expedition','lors du destockage et assemblage du colis'
    ,'lors de la preparation du colis pour expedition','lors de la confirmation du stockage','lors de la reception du colis');
CREATE TYPE "SCA".etat_lot AS ENUM('neuf', 'recupere', 'standard');
CREATE TYPE "SCA".condition_materiel AS ENUM (
    'utilisable',
    'a recycler'
    );
CREATE TYPE "SCA".categorie_produit AS ENUM (
    'produit de vente',
    'materiel d''emballage'
    );
CREATE TYPE "SCA".statut_travailleur AS ENUM (
    'actif',
    'inactif',
    'en congé',
    'en formation'
    );
CREATE TYPE "SCA".type_vehicule AS ENUM (
    'camion',
    'fourgon',
    'camionnette',
    'remorque'
    );
CREATE TYPE "SCA".statut_vehicule AS ENUM (
    'disponible',
    'en maintenance',
    'en livraison',
    'hors service'
    );
CREATE TYPE "SCA".statut_conducteur AS ENUM (
    'disponible',
    'en livraison',
    'en congé',
    'en formation'
    );
CREATE TYPE "SCA".statut_utilisateur AS ENUM (
    'actif',
    'inactif',
    'suspendu',
    'en attente_validation'
    );
CREATE TYPE "SCA".niveau_acces AS ENUM (
    'admin',
    'manager',
    'employe'
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
                            receiving_org "SCA".idorg,
                            statut "SCA".etatcolis NOT NULL ,
                            CONSTRAINT Colis_CC0 PRIMARY KEY (idcolis)
);
CREATE TABLE "EXTERNE".Colis(
                            idorg "SCA".idorg NOT NULL,
                            idpcolis "EXTERNE".Idpcolis NOT NULL ,
                            date_creation date NOT NULL ,
                            expected_date date not null,
                            receiving_org "SCA".idorg,
                            statut "SCA".retatcolis NOT NULL ,
                            CONSTRAINT PColis_CC0 PRIMARY KEY (idpcolis)
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
                                 specialites TEXT,
                                 CONSTRAINT Conducteur_CC0 PRIMARY KEY (idconducteur),
                                 CONSTRAINT Conducteur_CR0 FOREIGN KEY (idutilisateur) REFERENCES "SCA".Utilisateur(idutilisateur) ON DELETE CASCADE
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
                                 idindividu "SCA".IDindividu NOT NULL ,
                                 idorganisation "SCA".idOrg NOT NULL ,
                                 role "SCA".roles NOT NULL ,
                                 CONSTRAINT Repertoire_pk PRIMARY KEY (idindividu,idorganisation,role),
                                 CONSTRAINT Repertoire_CR0 FOREIGN KEY (idindividu) REFERENCES "SCA".individu(idindividu) ON DELETE CASCADE,
                                 FOREIGN KEY (idorganisation) REFERENCES "SCA".Organisation(idorganisation) ON DELETE CASCADE
);
CREATE TABLE "SCA".Produit(
                              idproduit "SCA".Idproduit NOT NULL ,
                              idfournisseur "SCA".idorg NOT NULL ,
                              nom "SCA".Nom NOT NULL ,
                              description text NOT NULL ,
                              prix_unitaire float NOT NULL ,
                              marque "SCA".Nom NOT NULL ,
                              modele "SCA".Nom NOT NULL ,
                              categorie "SCA".categorie_produit DEFAULT 'produit de vente',
                              CONSTRAINT Produit_CC0 PRIMARY KEY (idproduit),
                              FOREIGN KEY(idfournisseur)REFERENCES "SCA".Organisation(idorganisation) ON DELETE CASCADE
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
                          date_creation date NOT NULL ,
                          statut "SCA".etat_lot DEFAULT 'standard',
                          CONSTRAINT Lot_CC0 PRIMARY KEY (idlot),
                          FOREIGN KEY (idproduit) REFERENCES "SCA".Produit(idproduit)
                              ON DELETE CASCADE
);
CREATE TABLE "EXTERNE".Lot(
                          idorg "SCA".idorg NOT NULL,
                          idplot "EXTERNE".idplot NOT NULL ,
                          idproduit "SCA".Idproduit NOT NULL ,
                          quantite "SCA".dims NOT NULL ,
                          date_creation date NOT NULL ,
                          statut "SCA".etat_lot DEFAULT 'standard',
                          CONSTRAINT PLot_CC0 PRIMARY KEY (idplot),
                          FOREIGN KEY (idproduit) REFERENCES "SCA".Produit(idproduit)
                              ON DELETE CASCADE
);

CREATE TABLE "SCA".ContenuColis(
                                   idcolis "SCA".Idcolis NOT NULL ,
                                   idlot "SCA".Idlot NOT NULL ,
                                   quantite "SCA".dims NOT NULL ,
                                   date_MAJ date NOT NULL ,
                                   CONSTRAINT contenucolis_CC0 PRIMARY KEY (idcolis,idlot),
                                   CONSTRAINT ContenuColis_CR0 FOREIGN KEY (idcolis) REFERENCES "SCA".Colis(idcolis) ON DELETE CASCADE,
                                   FOREIGN KEY (idlot) REFERENCES "SCA".Lot(idlot)
                                       ON DELETE CASCADE
);
CREATE TABLE "EXTERNE".ContenuColis(
                                   idorg "SCA".idorg not null,
                                   idpcolis "EXTERNE".Idpcolis NOT NULL ,
                                   idplot "EXTERNE".Idplot NOT NULL ,
                                   quantite "SCA".dims NOT NULL ,
                                   date_MAJ date NOT NULL ,
                                   CONSTRAINT contenucolis_CC0 PRIMARY KEY (idorg,idpcolis,idplot),
                                   CONSTRAINT contenucolis_cr1 foreign key (idorg) references  "SCA".organisation(idorganisation),
                                   CONSTRAINT ContenuColis_CR0 FOREIGN KEY (idpcolis) REFERENCES "EXTERNE".Colis(idpcolis) ON DELETE CASCADE,
                                   FOREIGN KEY (idplot) REFERENCES "EXTERNE".Lot(idplot)
                                       ON DELETE CASCADE
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
                                            idcellule "SCA".Idcellule NOT NULL ,
                                            idlot "SCA".Idlot NOT NULL ,
                                            quantite "SCA".dims NOT NULL ,
                                            datemaj date NOT NULL ,
                                            CONSTRAINT InventaireEmplacement_CC0 PRIMARY KEY (idcellule, idlot,quantite),
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
                                  competences TEXT,
                                  date_derniere_evaluation DATE,
                                  CONSTRAINT Travailleur_CC0 PRIMARY KEY (idtravailleur),
                                  CONSTRAINT Travailleur_CR0 FOREIGN KEY (idutilisateur) REFERENCES "SCA".Utilisateur(idutilisateur) ON DELETE CASCADE
);
CREATE TABLE "SCA".Tache(
                            idtache "SCA".idtache NOT NULL ,
                            idtravailleur "SCA".idtravailleur NOT NULL ,
                            idcellule "SCA".Idcellule NOT NULL ,
                            idcolis "SCA".idcolis NOT NULL ,
                            date_creation DATE NOT NULL ,
                            date_echeance DATE NOT NULL ,
                            duree_estime INT NOT NULL ,
                            description TEXT NOT NULL ,
                            priority text not null,
                            statut text NOT NULL DEFAULT 'en cours',
                            type text not null,
                            CONSTRAINT Tache_CC0 PRIMARY KEY (idtache),
                            CONSTRAINT Tache_CR0 FOREIGN KEY (idtravailleur) REFERENCES "SCA".Travailleur(idtravailleur) ON DELETE CASCADE,
                            FOREIGN KEY (idcellule) REFERENCES "SCA".Cellule(idcellule) ON DELETE CASCADE,
                            FOREIGN KEY (idcolis) REFERENCES "SCA".Colis(idcolis) ON DELETE CASCADE
);
-- CREATE TABLE "CREDENTIALS".PasswordPolicies (
--                                                 id_policy INT GENERATED ALWAYS AS IDENTITY,
--                                                 nom_policy VARCHAR(100) NOT NULL UNIQUE,
--                                                 min_length INT NOT NULL DEFAULT 8,
--                                                 max_length INT DEFAULT 255,
--                                                 require_uppercase BOOLEAN NOT NULL DEFAULT TRUE,
--                                                 require_lowercase BOOLEAN NOT NULL DEFAULT TRUE,
--                                                 require_digit BOOLEAN NOT NULL DEFAULT TRUE,
--                                                 require_special_char BOOLEAN NOT NULL DEFAULT TRUE,
--                                                 min_special_chars INT NOT NULL DEFAULT 1,
--                                                 allowed_special_chars VARCHAR(255), -- Ex: '!@#$%^&*'
--                                                 disallowed_chars VARCHAR(255), --EX: ' ='
--                                                 prevent_common_passwords BOOLEAN NOT NULL DEFAULT FALSE,
--                                                 CONSTRAINT PK_PasswordPolicies PRIMARY KEY (nom_policy)
-- );


CREATE TABLE "SCA".Vehicule(
                               idvehicule "SCA".idvehicule NOT NULL,
                               immatriculation "SCA".Nom NOT NULL UNIQUE,
                               marque "SCA".Nom NOT NULL,
                               modele "SCA".Nom NOT NULL,
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
                               consommation_moyenne DECIMAL(5,2),
                               CONSTRAINT Vehicule_CC0 PRIMARY KEY (idvehicule)
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
                                           idorganisation "SCA".idOrg NOT NULL ,
                                           mdpOrg TEXT
);

CREATE TABLE "SCA".Logs (
                            id SERIAL PRIMARY KEY,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            level VARCHAR(10),            -- e.g. 'INFO', 'ERROR', 'DEBUG'
                            message TEXT,
                            extra JSONB                   -- pour des infos supplémentaires optionnelles
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

--script pour l'interface de base
--vues, routines et triggers

-- Vue pour les utilisateurs avec informations complètes
CREATE OR REPLACE VIEW "SCA".UtilisateursComplets AS
SELECT
    u.idutilisateur,
    u.username,
    i.nom,
    i.prenom,
    i.telephone,
    u.date_inscription,
    u.date_derniere_connexion,
    u.statut,
    u.niveau_acces,
    CASE
        WHEN t.idtravailleur IS NOT NULL THEN 'Travailleur'
        WHEN c.idconducteur IS NOT NULL THEN 'Conducteur'
        ELSE 'Utilisateur simple'
    END AS type_utilisateur,
    t.poste,
    t.departement,
    t.salaire_horaire,
    t.statut as statut_travailleur,
    c.numero_permis,
    c.type_permis,
    c.statut as statut_conducteur
FROM "SCA".Utilisateur u
JOIN "SCA".individu i ON u.idindividu = i.idindividu
LEFT JOIN "CREDENTIALS".Credentials cred ON u.idutilisateur = cred.idutilisateur
LEFT JOIN "SCA".Travailleur t ON u.idutilisateur = t.idutilisateur
LEFT JOIN "SCA".Conducteur c ON u.idutilisateur = c.idutilisateur;

-- Vue pour les conducteurs avec informations complètes
CREATE OR REPLACE VIEW "SCA".ConducteursComplets AS
SELECT
    c.idconducteur,
    c.numero_permis,
    c.type_permis,
    c.date_obtention_permis,
    c.date_expiration_permis,
    c.experience_annees,
    c.statut,
    c.date_derniere_evaluation,
    c.note_evaluation,
    c.specialites,
    u.username,
    cred.email,
    u.niveau_acces,
    u.statut as statut_utilisateur,
    i.nom,
    i.prenom,
    i.telephone
FROM "SCA".Conducteur c
JOIN "SCA".Utilisateur u ON c.idutilisateur = u.idutilisateur
JOIN "SCA".individu i ON u.idindividu = i.idindividu
LEFT JOIN "CREDENTIALS".Credentials cred ON u.idutilisateur = cred.idutilisateur;

-- Vue pour les travailleurs avec informations complètes
CREATE OR REPLACE VIEW "SCA".TravailleursComplets AS
SELECT
    t.idtravailleur,
    t.date_embauche,
    t.poste,
    t.departement,
    t.salaire_horaire,
    t.statut,
    t.competences,
    t.date_derniere_evaluation,
    u.username,
    cred.email,
    u.niveau_acces,
    u.statut as statut_utilisateur,
    i.nom,
    i.prenom,
    i.telephone
FROM "SCA".Travailleur t
JOIN "SCA".Utilisateur u ON t.idutilisateur = u.idutilisateur
JOIN "SCA".individu i ON u.idindividu = i.idindividu
LEFT JOIN "CREDENTIALS".Credentials cred ON u.idutilisateur = cred.idutilisateur;

CREATE OR REPLACE VIEW "SCA".ColisEntrants AS
(SELECT
     br.idbonreception AS "Numéro bon réception",
     br.date_creation AS "Date réception",
     c.idcolis AS "Référence colis",
     c.statut AS "État colis",
     o_fournisseur.nom AS "Fournisseur",
     COUNT(cc.idlot) AS "Nombre de lots",
     SUM(l.quantite) AS "Quantité totale",
     STRING_AGG(p.nom, ', ' ORDER BY p.nom) AS "Produits",
     br.remarques AS "Remarques"
FROM
    "SCA".Bonreception br
        JOIN
    "SCA".Colis c ON br.idcolis = c.idcolis
        JOIN
    "SCA".Organisation o_fournisseur ON br.idfournisseur = o_fournisseur.idorganisation
        LEFT JOIN
    "SCA".ContenuColis cc ON c.idcolis = cc.idcolis
        LEFT JOIN
    "SCA".Lot l ON cc.idlot = l.idlot
        LEFT JOIN
    "SCA".Produit p ON l.idproduit = p.idproduit
GROUP BY
    br.idbonreception, br.date_creation, c.idcolis, c.statut,
    o_fournisseur.nom, br.remarques
ORDER BY
    br.date_creation DESC);

CREATE OR REPLACE VIEW "SCA".ColisSortants AS
(SELECT
     be.idbonexpedition AS "Numéro bon expédition",
     be.date_creation AS "Date expédition",
     c.idcolis AS "Référence colis",
     c.statut AS "État colis",
     o_destinataire.nom AS "Destinataire",
     o_transporteur.nom AS "Transporteur",
     COUNT(cc.idlot) AS "Nombre de lots",
     SUM(l.quantite) AS "Quantité totale",
     STRING_AGG(p.nom, ', ' ORDER BY p.nom) AS "Produits",
     be.remarques AS "Remarques",
     CASE
         WHEN EXISTS (SELECT 1 FROM "SCA".RapportException re
                      WHERE re.idcolis = c.idcolis
                        AND re.type = 'lors de la preparation du colis pour expedition')
             THEN 'Avec anomalies'
         ELSE 'Sans anomalies'
         END AS "Statut contrôle"
FROM
    "SCA".Bonexpedition be
        JOIN
    "SCA".Colis c ON be.idcolis = c.idcolis
        JOIN
    "SCA".Organisation o_destinataire ON be.iddestinataire = o_destinataire.idorganisation
        JOIN
    "SCA".Organisation o_transporteur ON be.idtransporteur = o_transporteur.idorganisation
        LEFT JOIN
    "SCA".ContenuColis cc ON c.idcolis = cc.idcolis
        LEFT JOIN
    "SCA".Lot l ON cc.idlot = l.idlot
        LEFT JOIN
    "SCA".Produit p ON l.idproduit = p.idproduit
GROUP BY
    be.idbonexpedition, be.date_creation, c.idcolis, c.statut,
    o_destinataire.nom, o_transporteur.nom, be.remarques
ORDER BY
    be.date_creation DESC);

CREATE OR REPLACE VIEW "SCA".inventaire AS (
                                           SELECT p.idproduit,p.nom,SUM(l.quantite) AS quantity
                                           FROM "SCA".Produit p
                                                    JOIN "SCA".Lot l ON p.idproduit = l.idproduit
                                                    JOIN "SCA".InventaireEmplacement ie ON l.idlot = ie.idlot
                                           WHERE l.idlot NOT IN (
                                               -- Exclure les lots des colis livrés
                                               SELECT DISTINCT cc.idlot
                                               FROM "SCA".ContenuColis cc
                                                        JOIN "SCA".Colis c ON cc.idcolis = c.idcolis
                                               WHERE c.statut = 'Livre'
                                           )
                                           GROUP BY p.idproduit, p.nom
                                               );

-- Vue pour les colis en cours d'expédition (non livrés)
CREATE OR REPLACE VIEW "SCA".ColisEnExpedition AS
(SELECT
     be.idbonexpedition AS "Numéro bon expédition",
     be.date_creation AS "Date expédition",
     c.idcolis AS "Référence colis",
     c.statut AS "État colis",
     o_destinataire.nom AS "Destinataire",
     o_transporteur.nom AS "Transporteur",
     COUNT(cc.idlot) AS "Nombre de lots",
     SUM(l.quantite) AS "Quantité totale",
     STRING_AGG(p.nom, ', ' ORDER BY p.nom) AS "Produits",
     be.remarques AS "Remarques",
     CASE
         WHEN c.statut = 'Livre' THEN 'Livré'
         WHEN c.statut = 'Transit' THEN 'En transit'
         WHEN c.statut = 'Endommagé' THEN 'Problème détecté'
         WHEN c.statut = 'Attente' THEN 'En attente'
         WHEN c.statut = 'Perdu' THEN 'Perdu'
         ELSE 'Statut inconnu'
         END AS "Statut livraison"
FROM
    "SCA".Bonexpedition be
        JOIN
    "SCA".Colis c ON be.idcolis = c.idcolis
        JOIN
    "SCA".Organisation o_destinataire ON be.iddestinataire = o_destinataire.idorganisation
        JOIN
    "SCA".Organisation o_transporteur ON be.idtransporteur = o_transporteur.idorganisation
        LEFT JOIN
    "SCA".ContenuColis cc ON c.idcolis = cc.idcolis
        LEFT JOIN
    "SCA".Lot l ON cc.idlot = l.idlot
        LEFT JOIN
    "SCA".Produit p ON l.idproduit = p.idproduit
GROUP BY
    be.idbonexpedition, be.date_creation, c.idcolis, c.statut,
    o_destinataire.nom, o_transporteur.nom, be.remarques
ORDER BY
    be.date_creation DESC);

-- Functions for domain idOrg

CREATE OR REPLACE FUNCTION "SCA".idOrg_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^O[A-Z]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".idOrg_VAL(v TEXT)
    RETURNS "SCA".idOrg AS $$
BEGIN
    IF NOT "SCA".idOrg_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour idOrg: %', v;
    END IF;
    RETURN v::"SCA".idOrg;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".idOrg_CONV(v TEXT)
    RETURNS "SCA".idOrg AS $$
BEGIN
    IF "SCA".idOrg_CONF(v) THEN
        RETURN v::"SCA".idOrg;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain Idrapport

CREATE OR REPLACE FUNCTION "SCA".Idrapport_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^R[A-Z]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idrapport_VAL(v TEXT)
    RETURNS "SCA".Idrapport AS $$
BEGIN
    IF NOT "SCA".Idrapport_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Idrapport: %', v;
    END IF;
    RETURN v::"SCA".Idrapport;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idrapport_CONV(v TEXT)
    RETURNS "SCA".Idrapport AS $$
BEGIN
    IF "SCA".Idrapport_CONF(v) THEN
        RETURN v::"SCA".Idrapport;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION "EXTERNE".Idinquire_CONF(v TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^INQ[A-Z0-9]{4}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EXTERNE".Idinquire_VAL(v TEXT)
RETURNS "EXTERNE".Idinquire AS $$
BEGIN
    IF NOT "EXTERNE".Idinquire_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Idinquire: %', v;
    END IF;
    RETURN v::"EXTERNE".Idinquire;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EXTERNE".Idinquire_CONV(v TEXT)
RETURNS "EXTERNE".Idinquire AS $$
BEGIN
    IF "EXTERNE".Idinquire_CONF(v) THEN
        RETURN v::"EXTERNE".Idinquire;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain email

CREATE OR REPLACE FUNCTION "SCA".email_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".email_VAL(v TEXT)
    RETURNS "SCA".email AS $$
BEGIN
    IF NOT "SCA".email_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour email: %', v;
    END IF;
    RETURN v::"SCA".email;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".email_CONV(v TEXT)
    RETURNS "SCA".email AS $$
BEGIN
    IF "SCA".email_CONF(v) THEN
        RETURN v::"SCA".email;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain password

CREATE OR REPLACE FUNCTION "SCA".password_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^[A-Za-z0-9]{7,}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".password_VAL(v TEXT)
    RETURNS "SCA"."password" AS $$
BEGIN
    IF NOT "SCA".password_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour password: %', v;
    END IF;
    RETURN v::"SCA".password;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".password_CONV(v TEXT)
    RETURNS "SCA".password AS $$
BEGIN
    IF "SCA".password_CONF(v) THEN
        RETURN v::"SCA".password;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain Idzone

CREATE OR REPLACE FUNCTION "SCA".Idzone_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^Z[A-Z0-9]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idzone_VAL(v TEXT)
    RETURNS "SCA".Idzone AS $$
BEGIN
    IF NOT "SCA".Idzone_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Idzone: %', v;
    END IF;
    RETURN v::"SCA".Idzone;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idzone_CONV(v TEXT)
    RETURNS "SCA".Idzone AS $$
BEGIN
    IF "SCA".Idzone_CONF(v) THEN
        RETURN v::"SCA".Idzone;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain Bonrecep

CREATE OR REPLACE FUNCTION "SCA".Bonrecep_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^R[A-Z0-9]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Bonrecep_VAL(v TEXT)
    RETURNS "SCA".Bonrecep AS $$
BEGIN
    IF NOT "SCA".Bonrecep_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Bonrecep: %', v;
    END IF;
    RETURN v::"SCA".Bonrecep;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Bonrecep_CONV(v TEXT)
    RETURNS "SCA".Bonrecep AS $$
BEGIN
    IF "SCA".Bonrecep_CONF(v) THEN
        RETURN v::"SCA".Bonrecep;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- Functions for domain Id

CREATE OR REPLACE FUNCTION "SCA".Idcolis_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^CO[A-Z0-9]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idcolis_VAL(v TEXT)
    RETURNS "SCA".Idcolis AS $$
BEGIN
    IF NOT "SCA".Idcolis_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Idcolis: %', v;
    END IF;
    RETURN v::"SCA".Idcolis;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idcolis_CONV(v TEXT)
    RETURNS "SCA".Idcolis AS $$
BEGIN
    IF "SCA".Idcolis_CONF(v) THEN
        RETURN v::"SCA".Idcolis;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION "EXTERNE".Idpcolis_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^PCO[A-Z0-9]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EXTERNE".Idpcolis_VAL(v TEXT)
    RETURNS "EXTERNE".Idpcolis AS $$
BEGIN
    IF NOT "EXTERNE".Idpcolis_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Idcolis: %', v;
    END IF;
    RETURN v::"EXTERNE".Idpcolis;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EXTERNE".Idpcolis_CONV(v TEXT)
    RETURNS "EXTERNE".Idpcolis AS $$
BEGIN
    IF "EXTERNE".Idpcolis_CONF(v) THEN
        RETURN v::"EXTERNE".Idpcolis;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain Idcellule

CREATE OR REPLACE FUNCTION "SCA".Idcellule_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^C[A-Z0-9]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idcellule_VAL(v TEXT)
    RETURNS "SCA".idcellule AS $$
BEGIN
    IF NOT "SCA".Idcellule_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Idcellule: %', v;
    END IF;
    RETURN v::"SCA".Idcellule;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idcellule_CONV(v TEXT)
    RETURNS "SCA".Idcellule AS $$
BEGIN
    IF "SCA".Idcellule_CONF(v) THEN
        RETURN v::"SCA".Idcellule;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain Bonexped

CREATE OR REPLACE FUNCTION "SCA".Bonexped_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^E[A-Z0-9]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Bonexped_VAL(v TEXT)
    RETURNS "SCA".Bonexped AS $$
BEGIN
    IF NOT "SCA".Bonexped_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Bonexped: %', v;
    END IF;
    RETURN v::"SCA".Bonexped;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Bonexped_CONV(v TEXT)
    RETURNS "SCA".Bonexped AS $$
BEGIN
    IF "SCA".Bonexped_CONF(v) THEN
        RETURN v::"SCA".Bonexped;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain IDindividu

CREATE OR REPLACE FUNCTION "SCA".IDindividu_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^I[A-Z0-9]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".IDindividu_VAL(v TEXT)
    RETURNS "SCA".IDindividu AS $$
BEGIN
    IF NOT "SCA".IDindividu_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour IDindividu: %', v;
    END IF;
    RETURN v::"SCA".IDindividu;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".IDindividu_CONV(v TEXT)
    RETURNS "SCA".IDindividu AS $$
BEGIN
    IF "SCA".IDindividu_CONF(v) THEN
        RETURN v::"SCA".IDindividu;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain Numero

CREATE OR REPLACE FUNCTION "SCA".Numero_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^6\d{8}$' OR v ~ '^\+2376\d{8}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Numero_VAL(v TEXT)
    RETURNS "SCA".Numero AS $$
BEGIN
    IF NOT "SCA".Numero_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Numero: %', v;
    END IF;
    RETURN v::"SCA".Numero;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Numero_CONV(v TEXT)
    RETURNS "SCA".Numero AS $$
BEGIN
    IF "SCA".Numero_CONF(v) THEN
        RETURN v::"SCA".Numero;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain Adresse

CREATE OR REPLACE FUNCTION "SCA".Adresse_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN length(length(v)) < 40;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Adresse_VAL(v TEXT)
    RETURNS "SCA".Adresse AS $$
BEGIN
    IF NOT "SCA".Adresse_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Adresse: %', v;
    END IF;
    RETURN v::"SCA".Adresse;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Adresse_CONV(v TEXT)
    RETURNS "SCA".Adresse AS $$
BEGIN
    IF "SCA".Adresse_CONF(v) THEN
        RETURN v::"SCA".Adresse;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain Nom

CREATE OR REPLACE FUNCTION "SCA".Nom_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN length(length(v)) < 60;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Nom_VAL(v TEXT)
    RETURNS "SCA".Nom AS $$
BEGIN
    IF NOT "SCA".Nom_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Nom: %', v;
    END IF;
    RETURN v::"SCA".Nom;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Nom_CONV(v TEXT)
    RETURNS "SCA".Nom AS $$
BEGIN
    IF "SCA".Nom_CONF(v) THEN
        RETURN v::"SCA".Nom;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;



-- Functions for domain Idlot

CREATE OR REPLACE FUNCTION "SCA".Idlot_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^L[A-Z0-9]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idlot_VAL(v TEXT)
    RETURNS "SCA".Idlot AS $$
BEGIN
    IF NOT "SCA".Idlot_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Idlot: %', v;
    END IF;
    RETURN v::"SCA".Idlot;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idlot_CONV(v TEXT)
    RETURNS "SCA".Idlot AS $$
BEGIN
    IF "SCA".Idlot_CONF(v) THEN
        RETURN v::"SCA".Idlot;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EXTERNE".Idplot_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^PL[A-Z0-9]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EXTERNE".Idplot_VAL(v TEXT)
    RETURNS "EXTERNE".Idplot AS $$
BEGIN
    IF NOT "EXTERNE".Idplot_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Idlot: %', v;
    END IF;
    RETURN v::"EXTERNE".Idplot;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EXTERNE".Idplot_CONV(v TEXT)
    RETURNS "EXTERNE".Idplot AS $$
BEGIN
    IF "EXTERNE".Idplot_CONF(v) THEN
        RETURN v::"EXTERNE".Idplot;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;



-- Functions for domain Idproduit

CREATE OR REPLACE FUNCTION "SCA".Idproduit_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^P[A-Z0-9]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idproduit_VAL(v TEXT)
    RETURNS "SCA".Idproduit AS $$
BEGIN
    IF NOT "SCA".Idproduit_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Idproduit: %', v;
    END IF;
    RETURN v::"SCA".Idproduit;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idproduit_CONV(v TEXT)
    RETURNS "SCA".Idproduit AS $$
BEGIN
    IF "SCA".Idproduit_CONF(v) THEN
        RETURN v::"SCA".Idproduit;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain Idproduitmateriel

CREATE OR REPLACE FUNCTION "SCA".Idproduitmateriel_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^PM[A-Z0-9]{4}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idproduitmateriel_VAL(v TEXT)
    RETURNS "SCA".Idproduitmateriel AS $$
BEGIN
    IF NOT "SCA".Idproduitmateriel_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Idproduitmateriel: %', v;
    END IF;
    RETURN v::"SCA".Idproduitmateriel;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idproduitmateriel_CONV(v TEXT)
    RETURNS "SCA".Idproduitmateriel AS $$
BEGIN
    IF "SCA".Idproduitmateriel_CONF(v) THEN
        RETURN v::"SCA".Idproduitmateriel;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain Idproduitlogiciel

CREATE OR REPLACE FUNCTION "SCA".Idproduitlogiciel_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^PL[A-Z0-9]{4}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idproduitlogiciel_VAL(v TEXT)
    RETURNS "SCA".Idproduitlogiciel AS $$
BEGIN
    IF NOT "SCA".Idproduitlogiciel_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour Idproduitlogiciel: %', v;
    END IF;
    RETURN v::"SCA".Idproduitlogiciel;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".Idproduitlogiciel_CONV(v TEXT)
    RETURNS "SCA".Idproduitlogiciel AS $$
BEGIN
    IF "SCA".Idproduitlogiciel_CONF(v) THEN
        RETURN v::"SCA".Idproduitlogiciel;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain dims

CREATE OR REPLACE FUNCTION "SCA".dims_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN CAST(v AS DOUBLE PRECISION) > 0;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".dims_VAL(v TEXT)
    RETURNS "SCA".dims AS $$
BEGIN
    IF NOT "SCA".dims_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour dims: %', v;
    END IF;
    RETURN v::"SCA".dims;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".dims_CONV(v TEXT)
    RETURNS "SCA".dims AS $$
BEGIN
    IF "SCA".dims_CONF(v) THEN
        RETURN v::"SCA".dims;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain idtravailleur

CREATE OR REPLACE FUNCTION "SCA".idtravailleur_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^TR[A-Z0-9]{4}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".idtravailleur_VAL(v TEXT)
    RETURNS "SCA".idtravailleur AS $$
BEGIN
    IF NOT "SCA".idtravailleur_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour idtravailleur: %', v;
    END IF;
    RETURN v::"SCA".idtravailleur;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".idtravailleur_CONV(v TEXT)
    RETURNS "SCA".idtravailleur AS $$
BEGIN
    IF "SCA".idtravailleur_CONF(v) THEN
        RETURN v::"SCA".idtravailleur;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain idvehicule

CREATE OR REPLACE FUNCTION "SCA".idvehicule_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^V[A-Z0-9]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".idvehicule_VAL(v TEXT)
    RETURNS "SCA".idvehicule AS $$
BEGIN
    IF NOT "SCA".idvehicule_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour idvehicule: %', v;
    END IF;
    RETURN v::"SCA".idvehicule;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".idvehicule_CONV(v TEXT)
    RETURNS "SCA".idvehicule AS $$
BEGIN
    IF "SCA".idvehicule_CONF(v) THEN
        RETURN v::"SCA".idvehicule;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain idconducteur

CREATE OR REPLACE FUNCTION "SCA".idconducteur_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^CD[A-Z0-9]{4}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".idconducteur_VAL(v TEXT)
    RETURNS "SCA".idconducteur AS $$
BEGIN
    IF NOT "SCA".idconducteur_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour idconducteur: %', v;
    END IF;
    RETURN v::"SCA".idconducteur;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".idconducteur_CONV(v TEXT)
    RETURNS "SCA".idconducteur AS $$
BEGIN
    IF "SCA".idconducteur_CONF(v) THEN
        RETURN v::"SCA".idconducteur;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain idutilisateur

CREATE OR REPLACE FUNCTION "SCA".idutilisateur_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^U[A-Z0-9]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".idutilisateur_VAL(v TEXT)
    RETURNS "SCA".idutilisateur AS $$
BEGIN
    IF NOT "SCA".idutilisateur_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour idutilisateur: %', v;
    END IF;
    RETURN v::"SCA".idutilisateur;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".idutilisateur_CONV(v TEXT)
    RETURNS "SCA".idutilisateur AS $$
BEGIN
    IF "SCA".idutilisateur_CONF(v) THEN
        RETURN v::"SCA".idutilisateur;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Functions for domain username

CREATE OR REPLACE FUNCTION "SCA".username_CONF(v TEXT)
    RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^[a-zA-Z0-9_]{3,20}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".username_VAL(v TEXT)
    RETURNS "SCA".username AS $$
BEGIN
    IF NOT "SCA".username_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour username: %', v;
    END IF;
    RETURN v::"SCA".username;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".username_CONV(v TEXT)
    RETURNS "SCA".username AS $$
BEGIN
    IF "SCA".username_CONF(v) THEN
        RETURN v::"SCA".username;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;
--EMIRSSSSSSSS
-- Fichier SQL : EMIR.sql
-- Description : Routines EMIR pour toutes les entités de la base "SCA"

-- Schéma : "EMIR"
DROP SCHEMA IF EXISTS "EMIR" CASCADE;
CREATE SCHEMA "EMIR";

-- 1. ORGANISATION (INSERTION)
create or replace procedure "EMIR".Organisation_INS(
    _idorganisation text,
    _nom text,
    _telephone text,
    _type text
)
as $$
begin
    insert into "SCA".Organisation(idorganisation, nom, telephone, type) values ("SCA".idorg_conv(_idorganisation), "SCA".nom_conv(_nom), "SCA".numero_conv(_telephone), _type::"SCA".typeOrg);
end; $$ language plpgsql;

-- 2. CELLULE
create or replace procedure "EMIR".Cellule_INS(
    _idcellule text,
    _longueur text,
    _largeur text,
    _hauteur text,
    _masse_maximale text
)
as $$
begin
    insert into "SCA".Cellule(idcellule, longueur, largeur, hauteur, masse_maximale) values ("SCA".idcellule_conv(_idcellule) ,"SCA".dims_conv(_longueur), "SCA".dims_conv(_largeur), "SCA".dims_conv(_hauteur), "SCA".dims_conv(_masse_maximale));
end; $$ language plpgsql;

-- 3. COLIS
create or replace procedure "EMIR".Colis_INS(
    _idcolis text,
    _date_creation text,
    _statut text
)
as $$
begin
    insert into "SCA".Colis(idcolis, date_creation, statut) values ("SCA".idcolis_conv(_idcolis), _date_creation::date, _statut::"SCA".etat);
end; $$ language plpgsql;

-- 4. ZONE
create or replace procedure "EMIR".Zone_INS(
    _idzone text,
    _nom text
)
as $$
begin
    insert into "SCA".Zone(idzone, nom) values ("SCA".idzone_conv(_idzone), "SCA".nom_conv(_nom));
end; $$ language plpgsql;

-- 5. BONRECEPTION
create or replace procedure "EMIR".Bonreception_INS(
    _idbonreception text,
    _idcolis text,
    _date_creation text,
    _idfournisseur text,
    _statut text,
    _remarques text
)
as $$
begin
    insert into "SCA".Bonreception(idbonreception, idcolis, date_creation, idfournisseur, statut, remarques) values ("SCA".Bonrecep_CONV(_idbonreception), "SCA".idcolis_conv(_idcolis), _date_creation::date, "SCA".idorg_conv(_idfournisseur), _statut::"SCA".etat, _remarques);
end; $$ language plpgsql;

-- 6. BONEXPEDITION
create or replace procedure "EMIR".Bonexpedition_INS(
    _idbonexpedition text,
    _idcolis text,
    _idtransporteur text,
    _date_creation text,
    _iddestinataire text,
    _statut text,
    _remarques text
)
as $$
begin
    insert into "SCA".Bonexpedition(idbonexpedition, idcolis, idtransporteur, date_creation, iddestinataire, statut, remarques) values ("SCA".Bonexped_CONV(_idbonexpedition), "SCA".idcolis_conv(_idcolis), "SCA".idconducteur_CONV(_idtransporteur), _date_creation::date, "SCA".idorg_CONV(_iddestinataire), _statut::"SCA".etat, _remarques);
end; $$ language plpgsql;

-- 7. INDIVIDU
create or replace procedure "EMIR".Individu_INS(
    _idindividu text,
    _nom text,
    _prenom text,
    _telephone text,
    _adresse text
)
as $$
begin
    insert into "SCA".Individu(idindividu, nom, prenom, telephone, adresse) values ("SCA".idindividu_conv(_idindividu), "SCA".nom_conv(_nom), "SCA".nom_conv(_prenom), "SCA".numero_conv(_telephone), "SCA".adresse_conv(_adresse));
end; $$ language plpgsql;

-- 8. REPERTOIRE
create or replace procedure "EMIR".Repertoire_INS(
    _idindividu text,
    _idorganisation text,
    _role text
)
as $$
begin
    insert into "SCA".Repertoire(idindividu, idorganisation, role) values ("SCA".idindividu_conv(_idindividu), "SCA".idorg_conv(_idorganisation), _role::"SCA".roles);
end; $$ language plpgsql;

-- 9. PRODUIT
create or replace procedure "EMIR".Produit_INS(
    _idproduit text,
    _idfournisseur text,
    _nom text,
    _description text,
    _prix text,
    _marque text,
    _modele text,
    _categorie text
)
as $$
begin
    insert into "SCA".Produit(idproduit, idfournisseur, nom, description, prix_unitaire, marque, modele,categorie) values ("SCA".idproduit_conv(_idproduit), "SCA".idorg_conv(_idfournisseur), "SCA".nom_conv(_nom), _description, _prix, "SCA".nom_conv(_marque), "SCA".nom_conv(_modele),_categorie::"SCA".categorie_produit);
end; $$ language plpgsql;

-- 10. PRODUITMATERIEL
create or replace procedure "EMIR".ProduitMateriel_INS(
    _idproduit text,
    _longueur text,
    _largeur text,
    _hauteur text,
    _masse text
)
as $$
begin
    insert into "SCA".ProduitMateriel(idproduit, longueur, largeur, hauteur, masse) values ("SCA".idproduit_conv(_idproduit), "SCA".dims_conv(_longueur), "SCA".dims_conv(_largeur), "SCA".dims_conv(_hauteur), "SCA".dims_conv(_masse));
end; $$ language plpgsql;

-- 11. PRODUITLOGICIEL
create or replace procedure "EMIR".ProduitLogiciel_INS(
    _idproduit text,
    _version text,
    _license text
)
as $$
begin
    insert into "SCA".ProduitLogiciel(idproduit, version, license) values ("SCA".idproduit_conv(_idproduit), "SCA".nom_conv(_version), "SCA".nom_conv(_license));
end; $$ language plpgsql;

-- 12. LOT
create or replace procedure "EMIR".Lot_INS(
    _idlot text,
    _idproduit text,
    _quantite text,
    _date_creation text,
    _statut text
)
as $$
begin
    insert into "SCA".Lot(idlot, idproduit, quantite, date_creation, statut) values ("SCA".idlot_conv(_idlot), "SCA".idproduit_conv(_idproduit), "SCA".dims_conv(_quantite), _date_creation::date, _statut::"SCA".etat_lot);
end; $$ language plpgsql;

-- 13. CONTENUCOLIS
create or replace procedure "EMIR".ContenuColis_INS(
    _idcolis text,
    _idlot text,
    _quantite text,
    _date_MAJ text
)
as $$
begin
    insert into "SCA".ContenuColis(idcolis, idlot, quantite, date_maj) values ("SCA".idcolis_conv(_idcolis), "SCA".idlot_conv(_idlot), "SCA".dims_conv(_quantite), _date_MAJ::date);
end; $$ language plpgsql;

-- 14. ENTREPOT
create or replace procedure "EMIR".Entrepot_INS(
    _idcellule text,
    _position text
)
as $$
begin
    insert into "SCA".Entrepot(idcellule, position) values ("SCA".idcellule_conv(_idcellule), "SCA".idzone_conv(_position));
end; $$ language plpgsql;


-- 16. RAPPORTEXCEPTION
create or replace procedure "EMIR".RapportException_INS(
    _idrapport text,
    _idcolis text,
    _type text,
    _date_creation text,
    _description text,
    _statut text
)
as $$
begin
    insert into "SCA".RapportException(idrapport, idcolis, type, date_creation, description, statut) values ("SCA".idrapport_conv(_idrapport), "SCA".idcolis_conv(_idcolis), _type::"SCA".rapports, _date_creation::date, _description, _statut::"SCA".etat);
end; $$ language plpgsql;

-- 17. INVENTAIREEMPLACEMENT
create or replace procedure "EMIR".InventaireEmplacement_INS(
    _idcellule text,
    _idlot text,
    _quantite text,
    _datemaj text
)
as $$
begin
    insert into "SCA".InventaireEmplacement(idcellule, idlot, quantite, datemaj) values ("SCA".idcellule_conv(_idcellule), "SCA".idlot_conv(_idlot), "SCA".dims_conv(_quantite), _datemaj::date);
end; $$ language plpgsql;

create or replace procedure "EMIR".Credentials_INS(
    _email text,
    _mot_de_passe_hash text,
    _idutilisateur text
)
as $$
begin
    insert into "CREDENTIALS".Credentials(
        email, mot_de_passe_hash, idutilisateur
    )
    values (
        "SCA".email_CONV(_email),
        _mot_de_passe_hash,
        "SCA".idutilisateur_CONV(_idutilisateur)
    );
end; $$ language plpgsql;

-- 18. TRAVAILLEUR
create or replace procedure "EMIR".Travailleur_INS(
    _idtravailleur text,
    _idutilisateur text,
    _date_embauche text,
    _poste text,
    _departement text,
    _salaire_horaire text,
    _statut text,
    _competences text,
    _date_derniere_evaluation text
)
as $$
begin
    insert into "SCA".Travailleur(idtravailleur, idutilisateur, date_embauche, poste, departement, salaire_horaire, statut, competences, date_derniere_evaluation)
    values ("SCA".idtravailleur_CONV(_idtravailleur), "SCA".idutilisateur_CONV(_idutilisateur), _date_embauche::date, "SCA".Nom_CONV(_poste), "SCA".Nom_CONV(_departement), _salaire_horaire::decimal, _statut::"SCA".statut_travailleur, _competences, _date_derniere_evaluation::date);
end; $$ language plpgsql;

-- 19. VEHICULE
create or replace procedure "EMIR".Vehicule_INS(
    _idvehicule text,
    _immatriculation text,
    _marque text,
    _modele text,
    _annee_fabrication text,
    _type text,
    _capacite_charge text,
    _capacite_volume text,
    _date_acquisition text,
    _statut text,
    _kilometrage_actuel text,
    _date_derniere_maintenance text,
    _prochaine_maintenance text,
    _carburant text,
    _consommation_moyenne text
)
as $$
begin
    insert into "SCA".Vehicule(idvehicule, immatriculation, marque, modele, annee_fabrication, types, capacite_charge, capacite_volume, date_acquisition, statut, kilometrage_actuel, date_derniere_maintenance, prochaine_maintenance, carburant, consommation_moyenne)
    values ("SCA".idvehicule_CONV(_idvehicule), "SCA".Nom_CONV(_immatriculation), "SCA".Nom_CONV(_marque), "SCA".Nom_CONV(_modele), _annee_fabrication::integer, _type::"SCA".type_vehicule, "SCA".dims_CONV(_capacite_charge), "SCA".dims_CONV(_capacite_volume), _date_acquisition::date, _statut::"SCA".statut_vehicule, _kilometrage_actuel::decimal, _date_derniere_maintenance::date, _prochaine_maintenance::date, _carburant, _consommation_moyenne::decimal);
end; $$ language plpgsql;

-- 20. CONDUCTEUR
create or replace procedure "EMIR".Conducteur_INS(
    _idconducteur text,
    _idutilisateur text,
    _numero_permis text,
    _type_permis text,
    _date_obtention_permis text,
    _date_expiration_permis text,
    _experience_annees text,
    _statut text,
    _date_derniere_evaluation text,
    _note_evaluation text,
    _specialites text
)
as $$
begin
    insert into "SCA".Conducteur(idconducteur, idutilisateur, numero_permis, type_permis, date_obtention_permis, date_expiration_permis, experience_annees, statut, date_derniere_evaluation, note_evaluation, specialites)
    values ("SCA".idconducteur_CONV(_idconducteur), "SCA".idutilisateur_CONV(_idutilisateur), "SCA".Nom_CONV(_numero_permis), _type_permis, _date_obtention_permis::date, _date_expiration_permis::date, _experience_annees::integer, _statut::"SCA".statut_conducteur, _date_derniere_evaluation::date, _note_evaluation::decimal, _specialites);
end; $$ language plpgsql;

-- 21. UTILISATEUR
create or replace procedure "EMIR".Utilisateur_INS(
    _idutilisateur text,
    _idindividu text,
    _username text,
    _statut text,
    _niveau_acces text
)
as $$
begin
    insert into "SCA".Utilisateur(idutilisateur, idindividu, username, statut, niveau_acces)
    values ("SCA".idutilisateur_CONV(_idutilisateur), "SCA".IDindividu_CONV(_idindividu), "SCA".username_CONV(_username), _statut::"SCA".statut_utilisateur, _niveau_acces::"SCA".niveau_acces);
end; $$ language plpgsql;

-- Fin des routines _INS
-- Fichier SQL : EMIR.sql
-- Description : Routines EMIR pour toutes les entités de la base "SCA"

-- Schéma : "EMIR"
-- 1. ORGANISATION
create or replace function "EMIR".Organisation_EVA()
    returns table (
                      idorganisation "SCA".idOrg,
                      nom "SCA".Nom,
                      telephone "SCA".Numero,
                      adresse "SCA".Adresse,
                      type "SCA".typeOrg
                  ) as $$
begin
    return query select * from "SCA".Organisation;
end; $$ language plpgsql;

-- 2. CELLULE
create or replace function "EMIR".Cellule_EVA()
    returns table (
                      idcellule "SCA".Idcellule,
                      longueur "SCA".dims,
                      largeur "SCA".dims,
                      hauteur "SCA".dims,
                      masse_maximale "SCA".dims
                  ) as $$
begin
    return query select * from "SCA".Cellule;
end; $$ language plpgsql;

-- 3. COLIS
create or replace function "EMIR".Colis_EVA()
    returns table (
                      idcolis "SCA".Idcolis,
                      date_creation date,
                      expected_date date,
                      receiving_org "SCA".idorg,
                      statut "SCA".etat
                  ) as $$
begin
    return query select * from "SCA".Colis;
end; $$ language plpgsql;

-- 4. ZONE
create or replace function "EMIR".Zone_EVA()
    returns table (
                      idzone "SCA".Idzone,
                      nom "SCA".Nom
                  ) as $$
begin
    return query select * from "SCA".Zone;
end; $$ language plpgsql;

-- 5. BONRECEPTION
create or replace function "EMIR".Bonreception_EVA()
    returns table (
                      idbonreception "SCA".Bonrecep,
                      idcolis "SCA".Idcolis,
                      date_creation date,
                      idfournisseur "SCA".idOrg,
                      statut "SCA".etat,
                      remarques text
                  ) as $$
begin
    return query select * from "SCA".Bonreception;
end; $$ language plpgsql;

-- 6. BONEXPEDITION
create or replace function "EMIR".Bonexpedition_EVA()
    returns table (
                      idbonexpedition "SCA".Bonexped,
                      idcolis "SCA".Idcolis,
                      idtransporteur "SCA".idconducteur,
                      date_creation date,
                      iddestinataire "SCA".idOrg,
                      statut "SCA".etat,
                      remarques text
                  ) as $$
begin
    return query select * from "SCA".Bonexpedition;
end; $$ language plpgsql;

-- 7. INDIVIDU
create or replace function "EMIR".Individu_EVA()
    returns table (
                      idindividu "SCA".IDindividu,
                      nom "SCA".Nom,
                      prenom "SCA".Nom,
                      adresse "SCA".Adresse,
                      telephone "SCA".Numero
                  ) as $$
begin
    return query select * from "SCA".Individu;
end; $$ language plpgsql;

-- 8. REPERTOIRE
create or replace function "EMIR".Repertoire_EVA()
    returns table (
                      idindividu "SCA".IDindividu,
                      idorganisation "SCA".idOrg,
                      role "SCA".roles
                  ) as $$
begin
    return query select * from "SCA".Repertoire;
end; $$ language plpgsql;

-- 9. PRODUIT
create or replace function "EMIR".Produit_EVA()
    returns table (
                      idproduit "SCA".Idproduit,
                      idfournisseur "SCA".idOrg,
                      nom "SCA".Nom,
                      description text,
                      prix_unitaire float,
                      marque "SCA".Nom,
                      modele "SCA".Nom,
                      categorie "SCA".categorie_produit
                  ) as $$
begin
    return query select * from "SCA".Produit;
end; $$ language plpgsql;

-- 10. PRODUITMATERIEL
create or replace function "EMIR".ProduitMateriel_EVA()
    returns table (
                      idproduit "SCA".Idproduit,
                      longueur "SCA".dims,
                      largeur "SCA".dims,
                      hauteur "SCA".dims,
                      masse "SCA".dims
                  ) as $$
begin
    return query select * from "SCA".ProduitMateriel;
end; $$ language plpgsql;

-- 11. PRODUITLOGICIEL
create or replace function "EMIR".ProduitLogiciel_EVA()
    returns table (
                      idproduit "SCA".Idproduit,
                      version "SCA".Nom,
                      license "SCA".Nom
                  ) as $$
begin
    return query select * from "SCA".ProduitLogiciel;
end; $$ language plpgsql;

-- 12. LOT
create or replace function "EMIR".Lot_EVA()
    returns table (
                      idlot "SCA".idlot,
                      idproduit "SCA".Idproduit,
                      quantite "SCA".dims,
                      date_creation date,
                      statut "SCA".etat,
                      origine "SCA".etat_lot,
                      nombre_utilisations INTEGER,
                      condition "SCA".condition_materiel
                  ) as $$
begin
    return query select * from "SCA".Lot;
end; $$ language plpgsql;

-- 13. CONTENUCOLIS
create or replace function "EMIR".ContenuColis_EVA()
    returns table (
                      idcolis "SCA".Idcolis,
                      idlot "SCA".Idlot,
                      quantite "SCA".dims,
                      date_maj date
                  ) as $$
begin
    return query select * from "SCA".ContenuColis;
end; $$ language plpgsql;

-- 14. ENTREPOT
create or replace function "EMIR".Entrepot_EVA()
    returns table (
                      idcellule "SCA".Idcellule,
                      zone "SCA".idzone
                  ) as $$
begin
    return query select * from "SCA".Entrepot;
end; $$ language plpgsql;

-- 16. RAPPORTEXCEPTION
create or replace function "EMIR".RapportException_EVA()
    returns table (
                      idrapport "SCA".Idrapport,
                      idcolis "SCA".Idcolis,
                      type "SCA".rapports,
                      date_creation date,
                      description text,
                      statut "SCA".etat
                  ) as $$
begin
    return query select * from "SCA".RapportException;
end; $$ language plpgsql;

-- 17. INVENTAIREEMPLACEMENT
create or replace function "EMIR".InventaireEmplacement_EVA()
    returns table (
                      idcellule "SCA".Idcellule,
                      idlot "SCA".Idlot,
                      quantite "SCA".dims,
                      datemaj date
                  ) as $$
begin
    return query select * from "SCA".InventaireEmplacement;
end; $$ language plpgsql;

-- 18. TRAVAILLEUR
create or replace function "EMIR".Travailleur_EVA()
    returns table (
                      idtravailleur "SCA".idtravailleur,
                      idutilisateur "SCA".idutilisateur,
                      date_embauche date,
                      poste "SCA".Nom,
                      departement "SCA".Nom,
                      salaire_horaire decimal(10,2),
                      statut "SCA".statut_travailleur,
                      competences text,
                      date_derniere_evaluation date
                  ) as $$
begin
    return query select * from "SCA".Travailleur;
end; $$ language plpgsql;

-- 19. VEHICULE
create or replace function "EMIR".Vehicule_EVA()
    returns table (
                      idvehicule "SCA".idvehicule,
                      immatriculation "SCA".Nom,
                      marque "SCA".Nom,
                      modele "SCA".Nom,
                      annee_fabrication integer,
                      type "SCA".type_vehicule,
                      capacite_charge "SCA".dims,
                      capacite_volume "SCA".dims,
                      date_acquisition date,
                      statut "SCA".statut_vehicule,
                      kilometrage_actuel decimal(10,2),
                      date_derniere_maintenance date,
                      prochaine_maintenance date,
                      carburant varchar(20),
                      consommation_moyenne decimal(5,2)
                  ) as $$
begin
    return query select * from "SCA".Vehicule;
end; $$ language plpgsql;

-- 20. CONDUCTEUR
create or replace function "EMIR".Conducteur_EVA()
    returns table (
                      idconducteur "SCA".idconducteur,
                      idutilisateur "SCA".idutilisateur,
                      numero_permis "SCA".Nom,
                      type_permis varchar(10),
                      date_obtention_permis date,
                      date_expiration_permis date,
                      experience_annees integer,
                      statut "SCA".statut_conducteur,
                      date_derniere_evaluation date,
                      note_evaluation decimal(3,2),
                      specialites text
                  ) as $$
begin
    return query select * from "SCA".Conducteur;
end; $$ language plpgsql;

-- 21. UTILISATEUR
create or replace function "EMIR".Utilisateur_EVA()
    returns table (
        idutilisateur "SCA".idutilisateur,
        idindividu "SCA".IDindividu,
        username "SCA".username,
        date_inscription timestamp,
        date_derniere_connexion timestamp,
        statut "SCA".statut_utilisateur,
        niveau_acces "SCA".niveau_acces
    ) as $$
begin
    return query select * from "SCA".Utilisateur;
end; $$ language plpgsql;

-- Fonction d'évaluation pour Credentials
create or replace function "EMIR".Credentials_EVA()
    returns table (
        email "SCA".email,
        mot_de_passe_hash text,
        idutilisateur "SCA".idutilisateur,
        date_creation timestamp
    ) as $$
begin
    return query select * from "CREDENTIALS".Credentials;
end; $$ language plpgsql;
-- Fin des fonctions d'évaluation (_EVA)
-- Routines de RETRAIT (_RET)

-- 1. ORGANISATION
create or replace procedure "EMIR".Organisation_RET(
    _idorganisation "SCA".idOrg
)
as $$
begin
    delete from "SCA".Organisation where idorganisation = _idorganisation;
end; $$ language plpgsql;

-- 2. CELLULE
create or replace procedure "EMIR".Cellule_RET(
    _idcellule "SCA".Idcellule
)
as $$
begin
    delete from "SCA".Cellule where idcellule = _idcellule;
end; $$ language plpgsql;

-- 3. COLIS
create or replace procedure "EMIR".Colis_RET(
    _idcolis "SCA".Idcolis
)
as $$
begin
    delete from "SCA".Colis where idcolis = _idcolis;
end; $$ language plpgsql;

-- 4. ZONE
create or replace procedure "EMIR".Zone_RET(
    _idzone "SCA".Idzone
)
as $$
begin
    delete from "SCA".Zone where idzone = _idzone;
end; $$ language plpgsql;

-- 5. BONRECEPTION
create or replace procedure "EMIR".Bonreception_RET(
    _idbonreception "SCA".Bonrecep
)
as $$
begin
    delete from "SCA".Bonreception where idbonreception = _idbonreception;
end; $$ language plpgsql;

-- 6. BONEXPEDITION
create or replace procedure "EMIR".Bonexpedition_RET(
    _idbonexpedition "SCA".Bonexped
)
as $$
begin
    delete from "SCA".Bonexpedition where idbonexpedition = _idbonexpedition;
end; $$ language plpgsql;

-- 7. INDIVIDU
create or replace procedure "EMIR".Individu_RET(
    _idindividu "SCA".IDindividu
)
as $$
begin
    delete from "SCA".Individu where idindividu = _idindividu;
end; $$ language plpgsql;

-- 8. REPERTOIRE
create or replace procedure "EMIR".Repertoire_RET(
    _idindividu "SCA".IDindividu,
    _idorganisation "SCA".idOrg
)
as $$
begin
    delete from "SCA".Repertoire where idindividu = _idindividu and idorganisation = _idorganisation;
end; $$ language plpgsql;

-- 9. PRODUIT
create or replace procedure "EMIR".Produit_RET(
    _idproduit "SCA".Idproduit
)
as $$
begin
    delete from "SCA".Produit where idproduit = _idproduit;
end; $$ language plpgsql;

-- 10. PRODUITMATERIEL
create or replace procedure "EMIR".ProduitMateriel_RET(
    _idproduit "SCA".Idproduit
)
as $$
begin
    delete from "SCA".ProduitMateriel where idproduit = _idproduit;
end; $$ language plpgsql;

-- 11. PRODUITLOGICIEL
create or replace procedure "EMIR".ProduitLogiciel_RET(
    _idproduit "SCA".Idproduit
)
as $$
begin
    delete from "SCA".ProduitLogiciel where idproduit = _idproduit;
end; $$ language plpgsql;

-- 12. LOT
create or replace procedure "EMIR".Lot_RET(
    _idlot "SCA".idlot
)
as $$
begin
    delete from "SCA".Lot where idlot = _idlot;
end; $$ language plpgsql;

-- 13. CONTENUCOLIS
create or replace procedure "EMIR".ContenuColis_RET(
    _idcolis "SCA".Idcolis,
    _idlot "SCA".Idlot
)
as $$
begin
    delete from "SCA".ContenuColis where idcolis = _idcolis and idlot = _idlot;
end; $$ language plpgsql;

-- 14. ENTREPOT
create or replace procedure "EMIR".Entrepot_RET(
    _idcellule "SCA".Idcellule
)
as $$
begin
    delete from "SCA".Entrepot where idcellule = _idcellule;
end; $$ language plpgsql;

-- 16. RAPPORTEXCEPTION
create or replace procedure "EMIR".RapportException_RET(
    _idrapport "SCA".Idrapport
)
as $$
begin
    delete from "SCA".RapportException where idrapport = _idrapport;
end; $$ language plpgsql;

-- 17. INVENTAIREEMPLACEMENT
create or replace procedure "EMIR".InventaireEmplacement_RET(
    _idcellule "SCA".Idcellule,
    _idlot "SCA".Idlot
)
as $$
begin
    delete from "SCA".InventaireEmplacement where idcellule = _idcellule and idlot = _idlot;
end; $$ language plpgsql;

-- 18. TRAVAILLEUR
create or replace procedure "EMIR".Travailleur_RET(
    _idtravailleur "SCA".idtravailleur
)
as $$
begin
    delete from "SCA".Travailleur where idtravailleur = _idtravailleur;
end; $$ language plpgsql;

-- 19. VEHICULE
create or replace procedure "EMIR".Vehicule_RET(
    _idvehicule "SCA".idvehicule
)
as $$
begin
    delete from "SCA".Vehicule where idvehicule = _idvehicule;
end; $$ language plpgsql;

-- 20. CONDUCTEUR
create or replace procedure "EMIR".Conducteur_RET(
    _idconducteur "SCA".idconducteur
)
as $$
begin
    delete from "SCA".Conducteur where idconducteur = _idconducteur;
end; $$ language plpgsql;

-- 21. UTILISATEUR
create or replace procedure "EMIR".Utilisateur_RET(
    _idutilisateur "SCA".idutilisateur
)
as $$
begin
    delete from "SCA".Utilisateur where idutilisateur = _idutilisateur;
end; $$ language plpgsql;

-- Fin des routines _RET

--script pour les invariants requis
-- types, vues, routines et triggers

-- Trigger function to confirm product availability for expedition
CREATE OR REPLACE FUNCTION "SCA".check_expedition_availability()
    RETURNS TRIGGER AS $$
DECLARE
    available_quantity "SCA".dims;
BEGIN
    -- Get the product ID from the Lot being referenced in ContenuColis
    -- This trigger fires BEFORE INSERT on ContenuColis when a colis is being assembled for expedition.
    -- It assumes that NEW.idcolis is for an outgoing colis.
    -- We need to check if the product in the lot is available in InventaireEmplacement.

    -- First, check if the colis is part of an expedition process
    IF EXISTS (SELECT 1 FROM "SCA".Bonexpedition WHERE idcolis = NEW.idcolis) THEN
        -- Sum up all quantities for this lot across all cells in InventaireEmplacement
        SELECT COALESCE(SUM(quantite), 0) INTO available_quantity
        FROM "SCA".InventaireEmplacement
        WHERE idlot = NEW.idlot;

        -- If the quantity being added to the outgoing colis is greater than available stock
        IF NEW.quantite > available_quantity THEN
            RAISE EXCEPTION 'Insufficient stock for lot % (Product ID: %) for expedition. Available: %, Requested: %',
                NEW.idlot,
                (SELECT idproduit FROM "SCA".Lot WHERE idlot = NEW.idlot),
                available_quantity,
                NEW.quantite;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to enforce product availability for expedition during colis content insertion
CREATE TRIGGER trg_check_expedition_availability
    BEFORE INSERT ON "SCA".ContenuColis
    FOR EACH ROW
EXECUTE FUNCTION "SCA".check_expedition_availability();


-- Trigger function to ensure expedition date is not earlier than reception date
CREATE OR REPLACE FUNCTION "SCA".check_expedition_date()
    RETURNS TRIGGER AS $$
DECLARE
    reception_date DATE;
BEGIN
    -- Get the reception date for the colis associated with the new expedition bon
    SELECT br.date_creation INTO reception_date
    FROM "SCA".Bonreception br
    WHERE br.idcolis = NEW.idcolis;

    -- If a reception record exists for this colis and its date is after the proposed expedition date
    IF reception_date IS NOT NULL AND NEW.date_creation < reception_date THEN
        RAISE EXCEPTION 'Expedition date (%) for colis % cannot be earlier than its reception date (%).',
            NEW.date_creation, NEW.idcolis, reception_date;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to enforce expedition date validity
CREATE TRIGGER trg_check_expedition_date
    BEFORE INSERT OR UPDATE ON "SCA".Bonexpedition
    FOR EACH ROW
EXECUTE FUNCTION "SCA".check_expedition_date();

CREATE OR REPLACE FUNCTION "EMIR".valeur()
    RETURNS FLOAT AS $$
BEGIN
    RETURN (select sum(quantite*prix_unitaire) from "SCA".lot  NATURAL JOIN "SCA".Produit);
END;
$$ LANGUAGE plpgsql;

--script pour les traitements proposés
-- routines équivalentes à des mises à jour

-- Routines de MODIFICATION (_MOD)

-- 1. ORGANISATION
create or replace procedure "EMIR".Organisation_MOD(
    _idorganisation "SCA".idOrg,
    _nom "SCA".Nom,
    _telephone "SCA".Numero,
    _type "SCA".typeOrg
)
as $$
begin
    update "SCA".Organisation
    set nom = "SCA".nom_conv(_nom),
        telephone = "SCA".Numero_CONV(_telephone),
        type = _type::"SCA".typeOrg
    where idorganisation = "SCA".idorg_conv(_idorganisation);
end; $$ language plpgsql;
-- 2. CELLULE
create or replace procedure "EMIR".Cellule_MOD(
    _idcellule "SCA".Idcellule,
    _longueur "SCA".dims,
    _largeur "SCA".dims,
    _hauteur "SCA".dims,
    _masse_maximale "SCA".dims
)
as $$
begin
    update "SCA".Cellule
    set longueur = "SCA".dims_conv(_longueur),
        largeur = "SCA".dims_conv(_largeur),
        hauteur = "SCA".dims_conv(_hauteur),
        masse_maximale = "SCA".dims_conv(_masse_maximale)
    where idcellule = "SCA".idcellule_conv(_idcellule);
end; $$ language plpgsql;

-- 3. COLIS
create or replace procedure "EMIR".Colis_MOD(
    _idcolis "SCA".Idcolis,
    _date_creation date,
    _statut "SCA".etat
)
as $$
begin
    update "SCA".Colis
    set date_creation = _date_creation::date,
        statut = _statut::"SCA".etat
    where idcolis = "SCA".idcolis_conv(_idcolis);
end; $$ language plpgsql;

-- 4. ZONE
create or replace procedure "EMIR".Zone_MOD(
    _idzone "SCA".Idzone,
    _nom "SCA".Nom
)
as $$
begin
    update "SCA".Zone
    set nom = "SCA".nom_conv(_nom)
    where idzone = "SCA".idzone_conv(_idzone);
end; $$ language plpgsql;

-- 5. BONRECEPTION
create or replace procedure "EMIR".Bonreception_MOD(
    _idbonreception "SCA".Bonrecep,
    _idcolis "SCA".Idcolis,
    _date_creation date,
    _idfournisseur "SCA".idOrg,
    _statut "SCA".etat,
    _remarques text
)
as $$
begin
    update "SCA".Bonreception
    SET idcolis = "SCA".Idcolis_CONV(_idcolis),
        date_creation = _date_creation::date,
        idfournisseur = "SCA".idOrg_CONV(_idfournisseur),
        statut = _statut::"SCA".etat,
        remarques = _remarques
    WHERE idbonreception = "SCA".Bonrecep_CONV(_idbonreception);
end; $$ language plpgsql;

-- 6. BONEXPEDITION
create or replace procedure "EMIR".Bonexpedition_MOD(
    _idbonexpedition "SCA".Bonexped,
    _idcolis "SCA".Idcolis,
    _idtransporteur "SCA".idOrg,
    _date_creation date,
    _iddestinataire "SCA".idOrg,
    _statut "SCA".etat,
    _remarques text
)
as $$
begin
    update "SCA".Bonexpedition
    SET idcolis = "SCA".Idcolis_CONV(_idcolis),
        idtransporteur = "SCA".idOrg_CONV(_idtransporteur),
        date_creation = _date_creation::date,
        iddestinataire = "SCA".idOrg_CONV(_iddestinataire),
        statut = _statut::"SCA".etat,
        remarques = _remarques
    WHERE idbonexpedition = "SCA".Bonexped_CONV(_idbonexpedition);
end; $$ language plpgsql;

-- 7. INDIVIDU
create or replace procedure "EMIR".Individu_MOD(
    _idindividu "SCA".IDindividu,
    _nom "SCA".Nom,
    _adresse "SCA".Adresse,
    _telephone "SCA".Numero
)
as $$
begin
    update "SCA".Individu
    SET nom = "SCA".Nom_CONV(_nom),
        adresse = "SCA".Adresse_CONV(_adresse),
        telephone = "SCA".Numero_CONV(_telephone)
    WHERE idindividu = "SCA".IDindividu_CONV(_idindividu);
end; $$ language plpgsql;

-- 8. REPERTOIRE
create or replace procedure "EMIR".Repertoire_MOD(
    _idindividu "SCA".IDindividu,
    _idorganisation "SCA".idOrg,
    _role "SCA".roles
)
as $$
begin
    update "SCA".Repertoire
    SET role = _role::"SCA".roles
    WHERE idindividu = "SCA".IDindividu_CONV(_idindividu)
      AND idorganisation = "SCA".idOrg_CONV(_idorganisation);
end; $$ language plpgsql;

-- 9. PRODUIT
create or replace procedure "EMIR".Produit_MOD(
    _idproduit "SCA".Idproduit,
    _idfournisseur "SCA".idOrg,
    _nom "SCA".Nom,
    _description text,
    _marque "SCA".Nom,
    _modele "SCA".Nom
)
as $$
begin
    update "SCA".Produit
    SET idfournisseur = "SCA".idOrg_CONV(_idfournisseur),
        nom = "SCA".Nom_CONV(_nom),
        description = _description,
        marque = "SCA".Nom_CONV(_marque),
        modele = "SCA".Nom_CONV(_modele)
    WHERE idproduit = "SCA".Idproduit_CONV(_idproduit);
end; $$ language plpgsql;

-- 10. PRODUITMATERIEL
create or replace procedure "EMIR".ProduitMateriel_MOD(
    _idproduit "SCA".Idproduit,
    _longueur "SCA".dims,
    _largeur "SCA".dims,
    _hauteur "SCA".dims,
    _masse "SCA".dims
)
as $$
begin
    update "SCA".ProduitMateriel
    SET longueur = "SCA".dims_CONV(_longueur),
        largeur = "SCA".dims_CONV(_largeur),
        hauteur = "SCA".dims_CONV(_hauteur),
        masse = "SCA".dims_CONV(_masse)
    WHERE idproduit = "SCA".Idproduit_CONV(_idproduit);
end; $$ language plpgsql;

-- 11. PRODUITLOGICIEL
create or replace procedure "EMIR".ProduitLogiciel_MOD(
    _idproduit "SCA".Idproduit,
    _version "SCA".Nom,
    _license "SCA".Nom
)
as $$
begin
    update "SCA".ProduitLogiciel
    SET version = "SCA".Nom_CONV(_version),
        license = "SCA".Nom_CONV(_license)
    WHERE idproduit = "SCA".Idproduit_CONV(_idproduit);
end; $$ language plpgsql;

-- 12. LOT
create or replace procedure "EMIR".Lot_MOD(
    _idlot "SCA".idlot,
    _idproduit "SCA".Idproduit,
    _quantite "SCA".dims,
    _date_creation date,
    _statut "SCA".etat
)
as $$
begin
    update "SCA".Lot
    SET idproduit = "SCA".Idproduit_CONV(_idproduit),
        quantite = "SCA".dims_CONV(_quantite),
        date_creation = _date_creation::date,
        statut = _statut::"SCA".etat
    WHERE idlot = "SCA".Idlot_CONV(_idlot);
end; $$ language plpgsql;

-- 13. CONTENUCOLIS
create or replace procedure "EMIR".ContenuColis_MOD(
    _idcolis "SCA".Idcolis,
    _idlot "SCA".Idlot,
    _quantite "SCA".dims,
    _date_MAJ date
)
as $$
begin
    update "SCA".ContenuColis
    SET quantite = "SCA".dims_CONV(_quantite),
        date_MAJ = _date_MAJ::date
    WHERE idcolis = "SCA".Idcolis_CONV(_idcolis)
      AND idlot = "SCA".Idlot_CONV(_idlot);
end; $$ language plpgsql;

-- 14. ENTREPOT
create or replace procedure "EMIR".Entrepot_MOD(
    _idcellule "SCA".Idcellule,
    _position "SCA".Nom
)
as $$
begin
    update "SCA".Entrepot
    SET position = "SCA".Idzone_CONV(_position)
    WHERE idcellule = "SCA".Idcellule_CONV(_idcellule);
end; $$ language plpgsql;

-- 16. RAPPORTEXCEPTION
create or replace procedure "EMIR".RapportException_MOD(
    _idrapport "SCA".Idrapport,
    _idcolis "SCA".Idcolis,
    _type "SCA".rapports,
    _date_creation date,
    _description text,
    _statut "SCA".etat
)
as $$
begin
    update "SCA".RapportException
    SET idcolis = "SCA".Idcolis_CONV(_idcolis),
        type = _type::"SCA".rapports,
        date_creation = _date_creation::date,
        description = _description,
        statut = _statut::"SCA".etat
    WHERE idrapport = "SCA".Idrapport_CONV(_idrapport);
end; $$ language plpgsql;
-- 17. INVENTAIREEMPLACEMENT
create or replace procedure "EMIR".InventaireEmplacement_MOD(
    _idcellule "SCA".Idcellule,
    _idlot "SCA".Idlot,
    _quantite "SCA".dims,
    _datemaj date
)
as $$
begin
    update "SCA".InventaireEmplacement
    SET quantite = "SCA".dims_CONV(_quantite),
        datemaj = _datemaj::date
    WHERE idcellule = "SCA".Idcellule_CONV(_idcellule)
      AND idlot = "SCA".Idlot_CONV(_idlot);
end; $$ language plpgsql;

-- 18. TRAVAILLEUR
create or replace procedure "EMIR".Travailleur_MOD(
    _idtravailleur "SCA".idtravailleur,
    _date_embauche date,
    _poste "SCA".Nom,
    _departement "SCA".Nom,
    _salaire_horaire decimal(10,2),
    _statut "SCA".statut_travailleur,
    _competences text,
    _date_derniere_evaluation date
)
as $$
begin
    update "SCA".Travailleur
    SET date_embauche = _date_embauche::date,
        poste = "SCA".Nom_CONV(_poste),
        departement = "SCA".Nom_CONV(_departement),
        salaire_horaire = _salaire_horaire::decimal,
        statut = _statut::"SCA".statut_travailleur,
        competences = _competences,
        date_derniere_evaluation = _date_derniere_evaluation::date
    WHERE idtravailleur = "SCA".idtravailleur_CONV(_idtravailleur);
end; $$ language plpgsql;

-- 19. VEHICULE
create or replace procedure "EMIR".Vehicule_MOD(
    _idvehicule "SCA".idvehicule,
    _immatriculation "SCA".Nom,
    _marque "SCA".Nom,
    _modele "SCA".Nom,
    _annee_fabrication integer,
    _type "SCA".type_vehicule,
    _capacite_charge "SCA".dims,
    _capacite_volume "SCA".dims,
    _date_acquisition date,
    _statut "SCA".statut_vehicule,
    _kilometrage_actuel decimal(10,2),
    _date_derniere_maintenance date,
    _prochaine_maintenance date,
    _carburant varchar(20),
    _consommation_moyenne decimal(5,2)
)
as $$
begin
    update "SCA".Vehicule
    SET immatriculation = "SCA".Nom_CONV(_immatriculation),
        marque = "SCA".Nom_CONV(_marque),
        modele = "SCA".Nom_CONV(_modele),
        annee_fabrication = _annee_fabrication::integer,
        types = _type::"SCA".type_vehicule,
        capacite_charge = "SCA".dims_CONV(_capacite_charge),
        capacite_volume = "SCA".dims_CONV(_capacite_volume),
        date_acquisition = _date_acquisition::date,
        statut = _statut::"SCA".statut_vehicule,
        kilometrage_actuel = _kilometrage_actuel::decimal,
        date_derniere_maintenance = _date_derniere_maintenance::date,
        prochaine_maintenance = _prochaine_maintenance::date,
        carburant = _carburant,
        consommation_moyenne = _consommation_moyenne::decimal
    WHERE idvehicule = "SCA".idvehicule_CONV(_idvehicule);
end; $$ language plpgsql;

-- 20. CONDUCTEUR
create or replace procedure "EMIR".Conducteur_MOD(
    _idconducteur "SCA".idconducteur,
    _numero_permis "SCA".Nom,
    _type_permis varchar(10),
    _date_obtention_permis date,
    _date_expiration_permis date,
    _experience_annees integer,
    _statut "SCA".statut_conducteur,
    _date_derniere_evaluation date,
    _note_evaluation decimal(3,2),
    _specialites text
)
as $$
begin
    update "SCA".Conducteur
    SET numero_permis = "SCA".Nom_CONV(_numero_permis),
        type_permis = _type_permis,
        date_obtention_permis = _date_obtention_permis::date,
        date_expiration_permis = _date_expiration_permis::date,
        experience_annees = _experience_annees::integer,
        statut = _statut::"SCA".statut_conducteur,
        date_derniere_evaluation = _date_derniere_evaluation::date,
        note_evaluation = _note_evaluation::decimal,
        specialites = _specialites
    WHERE idconducteur = "SCA".idconducteur_CONV(_idconducteur);
end; $$ language plpgsql;

-- 21. UTILISATEUR
create or replace procedure "EMIR".Utilisateur_MOD(
    _idutilisateur text,
    _username text,
    _statut text,
    _niveau_acces text
)
as $$
begin
    update "SCA".Utilisateur
    SET username = "SCA".username_CONV(_username),
        statut = _statut::"SCA".statut_utilisateur,
        niveau_acces = _niveau_acces::"SCA".niveau_acces
    WHERE idutilisateur = "SCA".idutilisateur_CONV(_idutilisateur);
end; $$ language plpgsql;

--script pour les requetes proposées
-- =============================================================================
-- FONCTIONS D'AUTHENTIFICATION ET DE GESTION DES UTILISATEURS
-- =============================================================================

-- Fonction pour l'inscription d'un nouvel utilisateur
CREATE OR REPLACE FUNCTION "EMIR".inscrire_utilisateur(
    _idindividu TEXT,
    _username TEXT,
    _nom TEXT,
    _prenom TEXT,
    _email TEXT,
    _mot_de_passe TEXT,
    _niveau_acces TEXT
)
RETURNS TEXT AS $$
DECLARE
    _idutilisateur TEXT;
    _mot_de_passe_hash TEXT;
BEGIN
    -- Générer un ID utilisateur unique
    _idutilisateur := 'U' || LPAD(FLOOR(RANDOM() * 99999)::TEXT, 5, '0');

    -- Hasher le mot de passe (en production, utilisez bcrypt ou argon2)
    _mot_de_passe_hash := encode(sha256(_mot_de_passe::bytea), 'hex');

    -- Insérer l'utilisateur (données de profil uniquement)
    INSERT INTO "SCA".Utilisateur(
        idutilisateur, idindividu, username,
        statut, niveau_acces
    ) VALUES (
        _idutilisateur, _idindividu, _username,
        'en attente_validation', _niveau_acces
    );

    -- Insérer les credentials (données d'authentification)
    INSERT INTO "CREDENTIALS".Credentials(
        email, mot_de_passe_hash, idutilisateur
    ) VALUES (
        _email, _mot_de_passe_hash, _idutilisateur
    );

    -- Log de l'inscription
    INSERT INTO "SCA".Logs (level, message, extra)
    VALUES ('INFO', 'Nouvel utilisateur inscrit',
            jsonb_build_object('username', _username, 'email', _email, 'idutilisateur', _idutilisateur, 'nom', _nom, 'prenom', _prenom));

    RETURN _idutilisateur;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour la connexion d'un utilisateur
CREATE OR REPLACE FUNCTION "EMIR".connecter_utilisateur(
    _identifiant TEXT, -- peut être username ou email
    _mot_de_passe TEXT
)
RETURNS TABLE (
    idutilisateur "SCA".idutilisateur,
    username "SCA".username,
    nom "SCA".Nom,
    prenom "SCA".Nom,
    email "SCA".email,
    niveau_acces "SCA".niveau_acces,
    statut "SCA".statut_utilisateur,
    type_utilisateur TEXT
) AS $$
DECLARE
    _utilisateur_record RECORD;
    _credentials_record RECORD;
BEGIN
    -- Rechercher les credentials par email
    SELECT * INTO _credentials_record
    FROM "CREDENTIALS".Credentials
    WHERE email = _identifiant;

    -- Si les credentials existent et le mot de passe correspond
    IF FOUND AND _credentials_record.mot_de_passe_hash = _mot_de_passe THEN
        -- Rechercher l'utilisateur
        SELECT * INTO _utilisateur_record
        FROM "SCA".Utilisateur
        WHERE idutilisateur = _credentials_record.idutilisateur
          AND statut = 'actif';

        -- Si l'utilisateur est trouvé et actif
        IF FOUND THEN
            -- Mettre à jour la date de dernière connexion dans Utilisateur
            UPDATE "SCA".Utilisateur
            SET date_derniere_connexion = CURRENT_TIMESTAMP
            WHERE idutilisateur = _utilisateur_record.idutilisateur;

            -- Log de la connexion
            INSERT INTO "SCA".Logs (level, message, extra)
            VALUES ('INFO', 'Utilisateur connecté',
                    jsonb_build_object('username', _utilisateur_record.username, 'idutilisateur', _utilisateur_record.idutilisateur));

            -- Retourner les informations de l'utilisateur via la vue
            RETURN QUERY
            SELECT
                uc.idutilisateur,
                uc.username,
                uc.nom,
                uc.prenom,
                uc.niveau_acces,
                uc.statut,
                uc.type_utilisateur
            FROM "SCA".UtilisateursComplets uc
            WHERE uc.idutilisateur = _utilisateur_record.idutilisateur;
        END IF;
    ELSE
        -- Log de tentative de connexion échouée
        INSERT INTO "SCA".Logs (level, message, extra)
        VALUES ('WARNING', 'Tentative de connexion échouée',
                jsonb_build_object('identifiant', _identifiant));

        -- Retourner une ligne vide
        RETURN;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour changer le mot de passe
CREATE OR REPLACE FUNCTION "EMIR".changer_mot_de_passe(
    _idutilisateur TEXT,
    _ancien_mot_de_passe TEXT,
    _nouveau_mot_de_passe TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    _ancien_hash TEXT;
    _nouveau_hash TEXT;
    _utilisateur_record RECORD;
    _credentials_record RECORD;
BEGIN
    -- Hasher l'ancien mot de passe
    _ancien_hash := encode(sha256(_ancien_mot_de_passe::bytea), 'hex');

    -- Vérifier que l'utilisateur existe
    SELECT * INTO _utilisateur_record
    FROM "SCA".Utilisateur
    WHERE idutilisateur = _idutilisateur;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    -- Vérifier que les credentials existent et que l'ancien mot de passe est correct
    SELECT * INTO _credentials_record
    FROM "CREDENTIALS".Credentials
    WHERE idutilisateur = _idutilisateur
      AND mot_de_passe_hash = _ancien_hash;

    IF NOT FOUND THEN
        -- Log de tentative de changement de mot de passe échouée
        INSERT INTO "SCA".Logs (level, message, extra)
        VALUES ('WARNING', 'Tentative de changement de mot de passe échouée',
                jsonb_build_object('idutilisateur', _idutilisateur));
        RETURN FALSE;
    END IF;

    -- Hasher le nouveau mot de passe
    _nouveau_hash := encode(sha256(_nouveau_mot_de_passe::bytea), 'hex');

    -- Mettre à jour le mot de passe dans Credentials uniquement
    UPDATE "CREDENTIALS".Credentials
    SET mot_de_passe_hash = _nouveau_hash
    WHERE idutilisateur = _idutilisateur;

    -- Log du changement de mot de passe
    INSERT INTO "SCA".Logs (level, message, extra)
    VALUES ('INFO', 'Mot de passe changé avec succès',
            jsonb_build_object('idutilisateur', _idutilisateur, 'username', _utilisateur_record.username));

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour activer/désactiver un utilisateur
CREATE OR REPLACE FUNCTION "EMIR".changer_statut_utilisateur(
    _idutilisateur TEXT,
    _nouveau_statut "SCA".statut_utilisateur
)
    RETURNS BOOLEAN AS $$
DECLARE
    _utilisateur_record RECORD;
BEGIN
    -- Vérifier que l'utilisateur existe
    SELECT * INTO _utilisateur_record
    FROM "SCA".Utilisateur
    WHERE idutilisateur = _idutilisateur;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    -- Mettre à jour le statut
    UPDATE "SCA".Utilisateur
    SET statut = _nouveau_statut
    WHERE idutilisateur = _idutilisateur;

    -- Log du changement de statut
    INSERT INTO "SCA".Logs (level, message, extra)
    VALUES ('INFO', 'Statut utilisateur modifié',
            jsonb_build_object('idutilisateur', _idutilisateur, 'username', _utilisateur_record.username, 'nouveau_statut', _nouveau_statut));

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour récupérer les informations d'un utilisateur
CREATE OR REPLACE FUNCTION "EMIR".obtenir_utilisateur(
    _idutilisateur TEXT
)
RETURNS TABLE (
    idutilisateur "SCA".idutilisateur,
    username "SCA".username,
    nom "SCA".Nom,
    prenom "SCA".Nom,
    email "SCA".email,
    niveau_acces "SCA".niveau_acces,
    statut "SCA".statut_utilisateur,
    date_inscription timestamp,
    date_derniere_connexion timestamp
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.idutilisateur,
        u.username,
        i.nom,
        i.prenom,
        cred.email,
        u.niveau_acces,
        u.statut,
        u.date_inscription,
        u.date_derniere_connexion
    FROM "SCA".Utilisateur u
    JOIN "SCA".individu i ON u.idindividu = i.idindividu
    LEFT JOIN "CREDENTIALS".Credentials cred ON u.idutilisateur = cred.idutilisateur
    WHERE u.idutilisateur = _idutilisateur;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour lister tous les utilisateurs
CREATE OR REPLACE FUNCTION "EMIR".lister_utilisateurs()
RETURNS TABLE (
    idutilisateur "SCA".idutilisateur,
    username "SCA".username,
    nom "SCA".Nom,
    prenom "SCA".Nom,
    niveau_acces "SCA".niveau_acces,
    statut "SCA".statut_utilisateur,
    date_inscription timestamp,
    date_derniere_connexion timestamp
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        uc.idutilisateur,
        uc.username,
        uc.nom,
        uc.prenom,
        uc.niveau_acces,
        uc.statut,
        uc.date_inscription,
        uc.date_derniere_connexion
    FROM "SCA".UtilisateursComplets uc
    ORDER BY uc.date_inscription DESC;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour vérifier si un username ou email existe déjà
CREATE OR REPLACE FUNCTION "EMIR".verifier_disponibilite(
    _username TEXT,
    _email TEXT
)
RETURNS TABLE (
    username_disponible BOOLEAN,
    email_disponible BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        NOT EXISTS(SELECT 1 FROM "SCA".Utilisateur WHERE username = _username),
        NOT EXISTS(SELECT 1 FROM "CREDENTIALS".Credentials WHERE email = _email);
END;
$$ LANGUAGE plpgsql;

--script pour les requetes proposées
--routines équivalentes à des sélections


CREATE OR REPLACE FUNCTION "EMIR".total()
    RETURNS INT AS $$
BEGIN
    RETURN  (select sum(quantite) from "SCA".lot  NATURAL JOIN "SCA".Produit);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".numcellules()
    RETURNS INT AS $$
BEGIN
    RETURN (select count(*) from "SCA".Cellule);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".numcolis( idorganisation "SCA".idOrg )
    RETURNS INT AS $$
BEGIN
    RETURN (select count(*) from "SCA".Colis where idOrganisation = idorganisation);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".produitsnum()
    RETURNS INT AS $$
BEGIN
    RETURN (
        SELECT COUNT(DISTINCT "SCA".Produit.idproduit)
        FROM "SCA".Produit
                 JOIN "SCA".Lot ON "SCA".Produit.idproduit = "SCA".Lot.idproduit
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".numzones()
    RETURNS INT AS $$
BEGIN
    RETURN (select count(*) from "SCA".Zone);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION "EMIR".available_cells()
    RETURNS INT AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)
        FROM "SCA".Cellule
        WHERE idcellule NOT IN (
            SELECT idcellule FROM "SCA".InventaireEmplacement
        )
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".colis_entrants_jour()
    RETURNS SETOF "SCA".Bonreception AS $$
BEGIN
    RETURN query SELECT * FROM "SCA".Bonreception WHERE date_creation = current_date ;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".colis_entrants_date(_date TEXT)
    RETURNS SETOF "SCA".Bonreception AS $$
BEGIN
    RETURN query SELECT *
        FROM "SCA".Bonreception
        WHERE date_creation = _date::date;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".colis_sortants_jour()
    RETURNS SETOF "SCA".Bonexpedition AS $$
BEGIN
    RETURN query
        SELECT *
        FROM "SCA".Bonexpedition
        WHERE date_creation = current_date;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".colis_sortants_date(_date TEXT)
    RETURNS SETOF "SCA".ColisSortants AS $$
BEGIN
    RETURN QUERY
        SELECT *
        FROM "SCA".ColisSortants
        WHERE "Date expédition" = _date::date;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".colis_entrants_jour_count()
    RETURNS INT AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)
        FROM "SCA".ColisEntrants
        WHERE "Date réception" = current_date
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".colis_sortants_jour_count()
    RETURNS INT AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)
        FROM "SCA".ColisSortants
        WHERE "Date expédition" = current_date
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".quantityproduct(id "SCA".idproduit)
    RETURNS INT AS $$
BEGIN
    RETURN (
        SELECT SUM(quantite)
        FROM "SCA".Lot
        WHERE idproduit = id::text
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".findzone(id "SCA".idproduit)
    RETURNS TEXT AS $$
BEGIN
    RETURN (
        SELECT "SCA".zone.nom
        FROM "SCA".Produit
                 JOIN "SCA".Lot ON "SCA".Produit.idproduit = "SCA".Lot.idproduit
                 JOIN "SCA".InventaireEmplacement ON "SCA".InventaireEmplacement.idlot = "SCA".Lot.idlot
                 JOIN "SCA".Entrepot ON "SCA".InventaireEmplacement.idcellule = "SCA".entrepot.idcellule
                 JOIN "SCA".Zone on "SCA".zone.idzone = "SCA".entrepot.position
        WHERE "SCA".Produit.idproduit = id
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".cellutilisation()
    RETURNS FLOAT AS $$
DECLARE
    a INT;
    b INT;
BEGIN
    SELECT COUNT(DISTINCT "SCA".InventaireEmplacement.idcellule) INTO a
    FROM "SCA".Cellule
             JOIN "SCA".InventaireEmplacement ON "SCA".Cellule.idcellule = "SCA".InventaireEmplacement.idcellule;

    SELECT COUNT(*) INTO b FROM "SCA".Cellule;

    RETURN (a::FLOAT / b) * 100;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".getorganisationname(id "SCA".idorg)
    RETURNS TEXT AS $$
BEGIN
    RETURN(select nom from "SCA".Organisation where idorganisation=id);
END;
$$ LANGUAGE plpgsql;

create or replace function "EMIR".valuereception()
    returns float as $$
declare
    total_value float;
begin

    select sum("SCA".Produit.prix_unitaire * "SCA".Lot.quantite) into total_value
    from "SCA".Lot
             join "SCA".Produit on "SCA".Lot.idproduit = "SCA".Produit.idproduit
             join "SCA".ContenuColis on "SCA".Lot.idlot = "SCA".ContenuColis.idlot
             join "SCA".BonReception on "SCA".ContenuColis.idcolis = "SCA".BonReception.idcolis
    where "SCA".BonReception.date_creation = current_date;

    return total_value;
end;
$$ LANGUAGE plpgsql;

create or replace function "EMIR".avgitemsreception()
    returns float as $$
declare
    avg_value float;
begin
    select avg("SCA".ContenuColis.quantite) into avg_value
    from "SCA".ContenuColis
             join "SCA".BonReception on "SCA".ContenuColis.idcolis = "SCA".BonReception.idcolis
    where "SCA".BonReception.date_creation = current_date;

    return avg_value;
end;
$$ LANGUAGE plpgsql;

create or replace function "EMIR".valueexpedition()
    returns float as $$
declare
    total_value float;
begin

    select sum("SCA".Produit.prix_unitaire * "SCA".Lot.quantite) into total_value
    from "SCA".Lot
             join "SCA".Produit on "SCA".Lot.idproduit = "SCA".Produit.idproduit
             join "SCA".ContenuColis on "SCA".Lot.idlot = "SCA".ContenuColis.idlot
             join "SCA".Bonexpedition on "SCA".ContenuColis.idcolis = "SCA".Bonexpedition.idcolis
    where "SCA".Bonexpedition.date_creation = current_date;

    return total_value;
end;
$$ LANGUAGE plpgsql;


create or replace function "EMIR".avgitemsexpedition()
    returns float as $$
declare
    avg_value float;
begin
    select avg("SCA".ContenuColis.quantite) into avg_value
    from "SCA".ContenuColis
             join "SCA".Bonexpedition on "SCA".ContenuColis.idcolis = "SCA".Bonexpedition.idcolis
    where "SCA".Bonexpedition.date_creation = current_date;

    return avg_value;
end;
$$ LANGUAGE plpgsql;


SELECT "EMIR".colis_entrants_jour_count();

-- Fonction pour confirmer la livraison d'un colis
CREATE OR REPLACE FUNCTION "EMIR".confirmer_livraison_colis(
    _idcolis "SCA".Idcolis,
    _date_livraison DATE DEFAULT CURRENT_DATE
)
    RETURNS VOID AS $$
DECLARE
    colis_exists BOOLEAN;
    colis_expedition_exists BOOLEAN;
BEGIN
    -- Vérifier que le colis existe
    SELECT EXISTS(SELECT 1 FROM "SCA".Colis WHERE idcolis = _idcolis) INTO colis_exists;
    IF NOT colis_exists THEN
        RAISE EXCEPTION 'Le colis % n''existe pas', _idcolis;
    END IF;

    -- Vérifier que le colis a un bon d'expédition
    SELECT EXISTS(SELECT 1 FROM "SCA".Bonexpedition WHERE idcolis = _idcolis) INTO colis_expedition_exists;
    IF NOT colis_expedition_exists THEN
        RAISE EXCEPTION 'Le colis % n''a pas de bon d''expédition associé', _idcolis;
    END IF;

    -- Mettre à jour le statut du colis à "livre"
    UPDATE "SCA".Colis
    SET statut = 'livre'::"SCA".etat
    WHERE idcolis = _idcolis;

    -- Mettre à jour le statut du bon d'expédition à "livre"
    UPDATE "SCA".Bonexpedition
    SET statut = 'livre'::"SCA".etat,
        remarques = remarques || ' - Livré le ' || _date_livraison::TEXT
    WHERE idcolis = _idcolis;

    -- Insérer un log de livraison
    INSERT INTO "SCA".Logs (level, message, extra)
    VALUES ('INFO', 'Colis livré avec succès',
            jsonb_build_object('idcolis', _idcolis, 'date_livraison', _date_livraison));

    RAISE NOTICE 'Livraison du colis % confirmée pour le %', _idcolis, _date_livraison;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour obtenir les colis livrés
CREATE OR REPLACE FUNCTION "EMIR".colis_livres(
    _date_debut DATE DEFAULT NULL,
    _date_fin DATE DEFAULT NULL
)
    RETURNS TABLE (
                      idcolis "SCA".Idcolis,
                      date_creation DATE,
                      date_livraison DATE,
                      destinataire TEXT,
                      transporteur TEXT,
                      statut "SCA".etat
                  ) AS $$
BEGIN
    RETURN QUERY
        SELECT
            c.idcolis,
            c.date_creation,
            be.date_creation as date_livraison,
            o_dest.nom as destinataire,
            o_trans.nom as transporteur,
            c.statut
        FROM "SCA".Colis c
                 JOIN "SCA".Bonexpedition be ON c.idcolis = be.idcolis
                 JOIN "SCA".Organisation o_dest ON be.iddestinataire = o_dest.idorganisation
                 JOIN "SCA".Organisation o_trans ON be.idtransporteur = o_trans.idorganisation
        WHERE c.statut = 'livre'::"SCA".etat
          AND (_date_debut IS NULL OR be.date_creation >= _date_debut)
          AND (_date_fin IS NULL OR be.date_creation <= _date_fin)
        ORDER BY be.date_creation DESC;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour obtenir les statistiques de livraison
CREATE OR REPLACE FUNCTION "EMIR".statistiques_livraison(
    _date_debut DATE DEFAULT NULL,
    _date_fin DATE DEFAULT NULL
)
    RETURNS TABLE (
                      total_colis_livres BIGINT,
                      total_colis_expedies BIGINT,
                      taux_livraison NUMERIC,
                      valeur_totale_livree NUMERIC
                  ) AS $$
DECLARE
    colis_livres BIGINT;
    colis_expedies BIGINT;
    valeur_livree NUMERIC;
BEGIN
    -- Compter les colis livrés
    SELECT COUNT(*) INTO colis_livres
    FROM "SCA".Colis c
             JOIN "SCA".Bonexpedition be ON c.idcolis = be.idcolis
    WHERE c.statut = 'livre'::"SCA".etat
      AND (_date_debut IS NULL OR be.date_creation >= _date_debut)
      AND (_date_fin IS NULL OR be.date_creation <= _date_fin);

    -- Compter les colis expédiés (tous statuts)
    SELECT COUNT(*) INTO colis_expedies
    FROM "SCA".Bonexpedition be
    WHERE (_date_debut IS NULL OR be.date_creation >= _date_debut)
      AND (_date_fin IS NULL OR be.date_creation <= _date_fin);

    -- Calculer la valeur totale livrée
    SELECT COALESCE(SUM(p.prix_unitaire * cc.quantite), 0) INTO valeur_livree
    FROM "SCA".Colis c
             JOIN "SCA".Bonexpedition be ON c.idcolis = be.idcolis
             JOIN "SCA".ContenuColis cc ON c.idcolis = cc.idcolis
             JOIN "SCA".Lot l ON cc.idlot = l.idlot
             JOIN "SCA".Produit p ON l.idproduit = p.idproduit
    WHERE c.statut = 'livre'::"SCA".etat
      AND (_date_debut IS NULL OR be.date_creation >= _date_debut)
      AND (_date_fin IS NULL OR be.date_creation <= _date_fin);

    RETURN QUERY
        SELECT
            colis_livres,
            colis_expedies,
            CASE
                WHEN colis_expedies > 0 THEN ROUND((colis_livres::NUMERIC / colis_expedies::NUMERIC) * 100, 2)
                ELSE 0
                END as taux_livraison,
            valeur_livree;
END;
$$ LANGUAGE plpgsql;

-- Procédure EMIR pour confirmer la livraison
create or replace procedure "EMIR".ConfirmerLivraison_INS(
    _idcolis text,
    _date_livraison text DEFAULT NULL
)
as $$
declare
    date_livraison date;
begin
    -- Si aucune date n'est fournie, utiliser la date actuelle
    if _date_livraison is null then
        date_livraison := current_date;
    else
        date_livraison := _date_livraison::date;
    end if;

    -- Appeler la fonction de confirmation de livraison
    perform "EMIR".confirmer_livraison_colis("SCA".idcolis_conv(_idcolis), date_livraison);
end; $$ language plpgsql;
create or replace function "EMIR".Logs_get(_date1 timestamp,_date2 timestamp)
    returns table(
                     id int,
                     _timestamp timestamp,
                     level varchar(10),
                     message text,
                     extra jsonb
                 )
as $$
begin
return query select id, TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp,level,message,extra from "SCA".Tache where _timestamp between _date1 and _date2;
end; $$ language plpgsql;

create or replace function "EMIR".Logs_gethigher(_date timestamp)
    returns table(
                     id int,
                     _timestamp timestamp,
                     level varchar(10),
                     message text,
                     extra jsonb
                 )
as $$
begin
return query select id, TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp,level,message,extra from "SCA".Tache where _timestamp >= _date;
end; $$ language plpgsql;

create or replace function "EMIR".Logs_getlower(_date timestamp)
    returns table(
                     id int,
                     _timestamp timestamp,
                     level varchar(10),
                     message text,
                     extra jsonb
                 )
as $$
begin
    return query select id, timestamp,level,message,extra from "SCA".Logs where _timestamp <= _date;
end; $$ language plpgsql;


create or replace function "EMIR".Tache_EVA(_idtravailleur "SCA".idtravailleur)
returns table(
    _idtache "SCA".idtache,
    _idcellule "SCA".idcellule,
    _idcolis "SCA".idcolis,
    _date_creation date,
    _date_echeance date,
    _duree_estimé int,
    _description text,
    _priority text,
    _statut text,
    _type text
)
as $$
begin
return query select idtache,idcellule,idcolis,date_creation,date_echeance,duree_estime,description,priority,statut,type from "SCA".Tache where idtravailleur = _idtravailleur;
end; $$ language plpgsql;

select * from "SCA".Produit;






CREATE OR REPLACE FUNCTION "EMIR".pendingtasks(_idtravailleur "SCA".idtravailleur)
RETURNS SETOF "SCA".Tache
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM "SCA".Tache
    WHERE idtravailleur = _idtravailleur AND statut = 'en cours';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".completedtasks(_idtravailleur "SCA".idtravailleur)
RETURNS SETOF "SCA".Tache
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM "SCA".Tache
    WHERE idtravailleur = _idtravailleur AND statut = 'termine';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION "EMIR".getproductnames(_idcolis "SCA".Idcolis)
RETURNS TABLE(nom_produit text) AS $$
BEGIN
    RETURN QUERY
    SELECT p.nom::text
    FROM "SCA".ContenuColis c
    JOIN "SCA".Lot l ON l.idlot = c.idlot
    JOIN "SCA".Produit p ON p.idproduit = l.idproduit
    WHERE c.idcolis = _idcolis;
END;
$$ LANGUAGE plpgsql;

create or replace function "EMIR".getlots(_idcolis "SCA".idcolis)
returns setof "SCA".Lot as $$
begin
return query
    select "SCA".Lot.*
    from "SCA".Lot
             join "SCA".ContenuColis on "SCA".Lot.idlot = "SCA".ContenuColis.idlot
    where "SCA".ContenuColis.idcolis = _idcolis;
end;
$$ language plpgsql;

create or replace function "EMIR".getvaluecol(_idorg "SCA".idorg,_idcolis "EXTERNE".idpcolis)
returns int as $$
begin
    return(
    select sum("SCA".Produit.prix_unitaire) from "EXTERNE".ContenuColis
    join "EXTERNE".Lot on ("EXTERNE".ContenuColis.idplot = "EXTERNE".Lot.idplot)
    join "SCA".Produit on ("EXTERNE".Lot.idproduit = "SCA".Produit.idproduit)
    where "EXTERNE".ContenuColis.idorg = _idorg and "EXTERNE".ContenuColis.idpcolis = _idcolis);
end;
$$ language plpgsql;



create or replace function "EMIR".getvaluecol(_idcolis "SCA".idcolis)
returns int as $$
begin
    return(
    select sum("SCA".Produit.prix_unitaire) from "SCA".ContenuColis
    join "SCA".Lot on ("SCA".ContenuColis.idlot = "SCA".Lot.idlot)
    join "SCA".Produit on ("SCA".Lot.idproduit = "SCA".Produit.idproduit)
    where "SCA".ContenuColis.idcolis = _idcolis);
end;
$$ language plpgsql;

create or replace procedure "EMIR".supprimer_utilisateur(_idutilisateur "SCA".idutilisateur)
as $$
begin
delete from "SCA".Utilisateur where idutilisateur = _idutilisateur;
end;
$$ language plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".Modifier_utilisateur(
    _idutilisateuranc "SCA".idutilisateur,
    _idutilisateurnouv "SCA".idutilisateur,
    nom "SCA".nom,
    prenom "SCA".nom,
    email "SCA".email,
    _niveau_acces text,
    _mot_de_passe text
)
AS $$
BEGIN
    -- Vérification du mot de passe
    IF encode(digest(_mot_de_passe, 'sha256'), 'hex') = (
        SELECT mot_de_passe_hash
        FROM "CREDENTIALS".Credentials
        WHERE idutilisateur = _idutilisateuranc
    ) THEN
        -- Appel de la procédure Utilisateur_MOD
        CALL "EMIR".Utilisateur_MOD(
            _idutilisateurnouv,
            nom, -- si nom = username
            'actif', -- ou autre valeur de statut à définir
            _niveau_acces
        );

        -- Si ID utilisateur change, mise à jour des IDs liés
        IF _idutilisateuranc <> _idutilisateurnouv THEN
            UPDATE "SCA".Utilisateur
            SET idutilisateur = _idutilisateurnouv
            WHERE idutilisateur = _idutilisateuranc;

            UPDATE "CREDENTIALS".Credentials
            SET idutilisateur = _idutilisateurnouv
            WHERE idutilisateur = _idutilisateuranc;
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql;

drop function "EMIR".Organisation_EVA();

create table "EXTERNE".inquiries(
    idorg "SCA".idorg,
    idinq "EXTERNE".Idinquire not null,
    type "EXTERNE".typeinquire not null,
    period timestamp not null,
    status "EXTERNE".etatinq not null,
    description text,
    constraint inq_pk primary key (idinq),
    foreign key(idorg) references "SCA".Organisation(idorganisation)
);

create or replace function "EMIR".Organisation_EVA()
    returns table (
                      idorganisation "SCA".idOrg,
                      nom "SCA".Nom,
                      telephone "SCA".Numero,
                      type "SCA".typeOrg
                  ) as $$
begin
    return query select * from "SCA".Organisation;
end; $$ language plpgsql;

drop function "EMIR".Colis_EVA();
create or replace function "EMIR".Colis_EVA()
    returns table (
                      idcolis "SCA".Idcolis,
                      date_creation date,
                      expected_date date,
                      receiving_org "SCA".idorg,
                      statut "SCA".etatcolis
                  ) as $$
begin
    return query select * from "SCA".Colis;
end; $$ language plpgsql;


create or replace procedure "EMIR".PLot_INS(
    _idorg text,
    _idplot text,
    _idproduit text,
    _quantite text,
    _date_creation text,
    _statut text
)
as $$
begin
    insert into "EXTERNE".Lot(idorg,idplot, idproduit, quantite, date_creation, statut) values ("SCA".idorg_conv(_idorg),"EXTERNE".idplot_conv(_idplot), "SCA".idproduit_conv(_idproduit), "SCA".dims_conv(_quantite), _date_creation::date, _statut::"SCA".etat_lot);
end; $$ language plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".PLot_EVA(_idorg "SCA".idorg)
RETURNS TABLE (
    _idplot "EXTERNE".idplot,
    _idproduit "SCA".idproduit,
    _quantite "SCA".dims,
    _date_creation date,
    _statut "SCA".etat_lot
)
AS $$
BEGIN
   RETURN QUERY
   SELECT idplot, idproduit, quantite, date_creation, statut
   FROM "EXTERNE".Lot
   WHERE idorg = _idorg;
END;
$$ LANGUAGE plpgsql;

create or replace function "EMIR".PColis_EVA(_idorg "SCA".idorg)
returns table (
    _idpcolis "EXTERNE".idpcolis,
    _date_creation date,
    _expected_date date,
    _reveiving_org "SCA".idorg,
    _statut "SCA".retatcolis
)
as $$
begin
   return query select idpcolis,date_creation,expected_date,receiving_org,statut from "EXTERNE".Colis where idorg = _idorg;
end; $$ language plpgsql;



create or replace function "EMIR".PColis_EVA1()
returns table (
    _idorg "SCA".idorg,
    _idpcolis "EXTERNE".idpcolis,
    _date_creation date,
    _expected_date date,
    _receiving_org "SCA".idorg,
    _statut "SCA".retatcolis
)
as $$
begin
   return query select idorg,idpcolis,date_creation,expected_date,receiving_org,statut from "EXTERNE".Colis;
end; $$ language plpgsql;

create or replace procedure "EMIR".PColis_INS(
    _idorg text,
    _idpcolis text,
    _date_creation text,
    expected_date text,
    _statut text
)
as $$
begin
    insert into "EXTERNE".Colis(idorg,idpcolis, date_creation, statut) values ("SCA".idorg_conv(_idorg),"EXTERNE".idpcolis_conv(_idpcolis), _date_creation::date, _statut::"SCA".retatcolis);
end; $$ language plpgsql;

create or replace function "EMIR".PContenuColis_EVA(_idorg "SCA".idorg)
returns table (
    _idpcolis "EXTERNE".idpcolis,
    _idplot "EXTERNE".idplot,
    _quantite "SCA".dims,
    _date_maj date
)
as $$
begin
  return query select idpcolis,idplot,quantite,date_maj from "EXTERNE".ContenuColis where idorg = _idorg;
end; $$ language plpgsql;

create or replace function "EMIR".PContenuColis_EVA()
returns table (
    _idorg "SCA".idorg,
    _idpcolis "EXTERNE".idpcolis,
    _idplot "EXTERNE".idplot,
    _quantite "SCA".dims,
    _date_maj date
)
as $$
begin
  return query select idorg,idpcolis,idplot,quantite,date_maj from "EXTERNE".ContenuColis;
end; $$ language plpgsql;

create or replace procedure "EMIR".PContenuColis_INS(
    _idorg text,
    _idcolis text,
    _idlot text,
    _quantite text,
    _date_MAJ text
)
as $$
begin
    insert into "EXTERNE".ContenuColis(idorg,idPcolis, idPlot, quantite, date_maj) values ("SCA".idorg_conv(_idorg),"EXTERNE".idpcolis_conv(_idcolis), "EXTERNE".idplot_conv(_idlot), "SCA".dims_conv(_quantite), _date_MAJ::date);
end; $$ language plpgsql;

select * from "EMIR".PLot_EVA('OFIRST');
select * from "EMIR".PColis_EVA('OFIRST');
select * from "EMIR".PContenuColis_EVA('OFIRST');

SELECT "EXTERNE".Idplot_CONF('PLA1BK2');  -- ✅ true
select "EXTERNE".idplot_conv('PLA1BK2');
SELECT "EXTERNE".Idplot_CONF('X-123');   -- ❌ false

CREATE OR REPLACE FUNCTION "EMIR".inquiries_eva(_idorg "SCA".idorg)
RETURNS TABLE (
    idinq       "EXTERNE".Idinquire,
    type        "EXTERNE".typeinquire,
    period      timestamp,
    status      "EXTERNE".etatinq,
    description text

) AS $$
BEGIN
    RETURN QUERY
    SELECT i.idinq, i.type, i.period, i.status,i.description
    FROM "EXTERNE".inquiries i
    WHERE i.idorg = _idorg;
END;
$$ LANGUAGE plpgsql;


create or replace function "EMIR".getvolume(_idcolis "SCA".idcolis)
returns float as $$
    declare
        volume float;
    begin
        with it as(
            select longueur as lon ,largeur as lar, hauteur as haut from "SCA".ProduitMateriel
            join "SCA".lot on "SCA".lot.idproduit = "SCA".ProduitMateriel.idproduit
            join "SCA".ContenuColis on "SCA".contenucolis.idlot = "SCA".lot.idlot
            where _idcolis = "SCA".ContenuColis.idcolis
        )
       select  sum((lon*lar*haut))  from it into volume;
        return volume;

    end;

    $$ language plpgsql;



create or replace function "EMIR".getpoids(_idcolis "SCA".idcolis)
returns float as $$
    declare
        volume float;
    begin
        with it as(
            select masse poi from "SCA".ProduitMateriel
            join "SCA".lot on "SCA".lot.idproduit = "SCA".ProduitMateriel.idproduit
            join "SCA".ContenuColis on "SCA".contenucolis.idlot = "SCA".lot.idlot
            where _idcolis = "SCA".ContenuColis.idcolis
        )
       select  sum(poi)  from it into volume;
        return volume;

    end;

    $$ language plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".entransit()
RETURNS int AS $$
DECLARE
    result int;
BEGIN
    SELECT COUNT(*) INTO result
    FROM "SCA".Bonexpedition b
    WHERE NOT EXISTS (
        SELECT 1
        FROM "SCA".Colis c
        WHERE c.idcolis = b.idcolis
    );

    RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".preparation_tasks()
RETURNS int AS $$
DECLARE
    result int;
BEGIN
    SELECT COUNT(*) INTO result
    FROM "SCA".Colis c
    WHERE NOT EXISTS (
        SELECT 1
        FROM "SCA".Bonexpedition b
        WHERE b.idcolis = c.idcolis
    );

    RETURN result;
END;
$$ LANGUAGE plpgsql;