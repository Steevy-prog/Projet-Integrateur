--script de création du schéma de base
--domaines, types, tables

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
CREATE TYPE "SCA".typeOrg AS ENUM('fournisseur','destinataire','SAC');
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
                            statut "SCA".etat NOT NULL ,
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
                               adresse "SCA".Adresse NOT NULL ,
                               telephone "SCA".Numero NOT NULL ,
                               CONSTRAINT individu_CC0 PRIMARY KEY (idindividu)
);
CREATE TABLE "SCA".Bonreception(
                                   idbonreception "SCA".Bonrecep NOT NULL ,
                                   idcolis "SCA".Idcolis NOT NULL ,
                                   idtransporteur "SCA".idindividu NOT NULL ,
                                   date_creation DATE NOT NULL ,
                                   idfournisseur "SCA".idorg NOT NULL ,
                                   statut "SCA".etat NOT NULL ,
                                   remarques TEXT NOT NULL ,
                                   CONSTRAINT Bonreception_CC0 PRIMARY KEY(idbonreception),
                                   FOREIGN KEY (idcolis)REFERENCES "SCA".Colis(idcolis),
                                   FOREIGN KEY (idtransporteur)REFERENCES "SCA".individu(idindividu)ON DELETE CASCADE,
                                   FOREIGN KEY (idfournisseur)REFERENCES "SCA".Organisation(idorganisation)ON DELETE CASCADE
);
CREATE TABLE "SCA".Bonexpedition(
                                    idbonexpedition "SCA".Bonexped NOT NULL ,
                                    idcolis "SCA".Idcolis NOT NULL ,
                                    idtransporteur "SCA".idindividu NOT NULL ,
                                    date_creation DATE NOT NULL ,
                                    iddestinataire "SCA".idorg NOT NULL ,
                                    statut "SCA".etat NOT NULL ,
                                    remarques TEXT NOT NULL ,
                                    CONSTRAINT Bonexpedition_CC0 PRIMARY KEY(idbonexpedition),
                                    FOREIGN KEY (idcolis)REFERENCES "SCA".Colis(idcolis),
                                    FOREIGN KEY (idtransporteur)REFERENCES "SCA".individu(idindividu) ON DELETE CASCADE,
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
                          statut "SCA".etat NOT NULL ,
                          origine "SCA".etat_lot DEFAULT 'standard',
                          nombre_utilisations INTEGER DEFAULT 0,
                          condition "SCA".condition_materiel DEFAULT 'utilisable',
                          CONSTRAINT Lot_CC0 PRIMARY KEY (idlot),
                          FOREIGN KEY (idproduit) REFERENCES "SCA".Produit(idproduit)
                              ON DELETE CASCADE
);

CREATE TABLE "SCA".ContenuColis(
                                   idcolis "SCA".Idcolis NOT NULL ,
                                   idlot "SCA".Idlot NOT NULL ,
                                   quantite "SCA".dims NOT NULL ,
                                   date_MAJ date NOT NULL ,
                                   CONSTRAINT contenucolis_CC0 PRIMARY KEY (idcolis,idlot,quantite),
                                   CONSTRAINT ContenuColis_CR0 FOREIGN KEY (idcolis) REFERENCES "SCA".Colis(idcolis) ON DELETE CASCADE,
                                   FOREIGN KEY (idlot) REFERENCES "SCA".Lot(idlot)
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
                                       statut "SCA".etat NOT NULL ,
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

CREATE TABLE "SCA".Tache(
    idtache "SCA".idtache NOT NULL ,
    idtravailleur "SCA".idtravailleur NOT NULL ,
    idcellule "SCA".Idcellule NOT NULL ,
    idlot "SCA".Idlot NOT NULL ,
    date_creation DATE NOT NULL ,
    description TEXT NOT NULL ,
    priority text not null,
    statut text NOT NULL DEFAULT 'en cours',
    type text not null,
    CONSTRAINT Tache_CC0 PRIMARY KEY (idtache),
    CONSTRAINT Tache_CR0 FOREIGN KEY (idtravailleur) REFERENCES "SCA".Travailleur(idtravailleur) ON DELETE CASCADE,
    FOREIGN KEY (idcellule) REFERENCES "SCA".Cellule(idcellule) ON DELETE CASCADE,
    FOREIGN KEY (idlot) REFERENCES "SCA".Lot(idlot) ON DELETE CASCADE
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

CREATE TABLE "SCA".Travailleur(
    idtravailleur "SCA".idtravailleur NOT NULL,
    idindividu "SCA".IDindividu NOT NULL,
    date_embauche DATE NOT NULL,
    poste "SCA".Nom NOT NULL,
    departement "SCA".Nom NOT NULL,
    salaire_horaire DECIMAL(10,2) NOT NULL,
    statut "SCA".statut_travailleur DEFAULT 'actif',
    competences TEXT,
    date_derniere_evaluation DATE,
    CONSTRAINT Travailleur_CC0 PRIMARY KEY (idtravailleur),
    CONSTRAINT Travailleur_CR0 FOREIGN KEY (idindividu) REFERENCES "SCA".individu(idindividu) ON DELETE CASCADE
);

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

CREATE TABLE "SCA".Conducteur(
    idconducteur "SCA".idconducteur NOT NULL,
    idindividu "SCA".IDindividu NOT NULL,
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
    CONSTRAINT Conducteur_CR0 FOREIGN KEY (idindividu) REFERENCES "SCA".individu(idindividu) ON DELETE CASCADE
);

CREATE TABLE "CREDENTIALS".PasswordPolicies (
                                                setting_name VARCHAR(100) NOT NULL UNIQUE,
                                                setting_value VARCHAR(100) NOT NULL,
                                                setting_group VARCHAR(100) NOT NULL,
                                                description VARCHAR(100) NOT NULL,
                                                CONSTRAINT PK_PasswordPolicies PRIMARY KEY (setting_name)
);

CREATE TABLE "CREDENTIALS".Credentials(
                                          email "SCA".email NOT NULL ,
    -- password "SCA".password NOT NULL ,
                                          nom_policy VARCHAR(100),
                                          idindividu "SCA".IDindividu UNIQUE NOT NULL,
                                          CONSTRAINT Credentials_CC0 PRIMARY KEY (email),
                                          CONSTRAINT Credentials_CR0 FOREIGN KEY (idindividu) REFERENCES "SCA".individu
    -- CONSTRAINT Credentials_CR1 FOREIGN KEY (nom_policy) REFERENCES "CREDENTIALS".PasswordPolicies
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


--script pour l'interface de base
--vues, routines et triggers

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
                                               WHERE c.statut = 'livre'
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
         WHEN c.statut = 'livre' THEN 'Livré'
         WHEN c.statut = 'bon etat' THEN 'En transit'
         WHEN c.statut = 'mauvais etat' THEN 'Problème détecté'
         WHEN c.statut = 'deteriore' THEN 'Endommagé'
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
    _adresse text,
    _type text
)
as $$
begin
    insert into "SCA".Organisation(idorganisation, nom, telephone, adresse, type) values ("SCA".idorg_conv(_idorganisation), "SCA".nom_conv(_nom), "SCA".numero_conv(_telephone), "SCA".Adresse_conv(_adresse), _type::"SCA".typeOrg);
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
    _idtransporteur text,
    _date_creation text,
    _idfournisseur text,
    _statut text,
    _remarques text
)
as $$
begin
    insert into "SCA".Bonreception(idbonreception, idcolis, idtransporteur, date_creation, idfournisseur, statut, remarques) values ("SCA".Bonrecep_CONV(_idbonreception), "SCA".idcolis_conv(_idcolis), "SCA".idorg_conv(_idtransporteur), _date_creation::date, "SCA".idorg_conv(_idfournisseur), _statut::"SCA".etat, _remarques);
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
    insert into "SCA".Bonexpedition(idbonexpedition, idcolis, idtransporteur, date_creation, iddestinataire, statut, remarques) values ("SCA".Bonexped_CONV(_idbonexpedition), "SCA".idcolis_conv(_idcolis), "SCA".idorg_conv(_idtransporteur), _date_creation::date, "SCA".idorg_CONV(_iddestinataire), _statut::"SCA".etat, _remarques);
end; $$ language plpgsql;

-- 7. INDIVIDU
create or replace procedure "EMIR".Individu_INS(
    _idindividu text,
    _nom text,
    _adresse text,
    _telephone text
)
as $$
begin
    insert into "SCA".Individu(idindividu, nom, adresse, telephone) values ("SCA".idindividu_conv(_idindividu), "SCA".nom_conv(_nom), "SCA".adresse_conv(_adresse), "SCA".numero_conv(_telephone));
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
    _statut text,
    _origine text,
    _nbUses INT,
    _cond text
)
as $$
begin
    insert into "SCA".Lot(idlot, idproduit, quantite, date_creation, statut,origine,nombre_utilisations,condition) values ("SCA".idlot_conv(_idlot), "SCA".idproduit_conv(_idproduit), "SCA".dims_conv(_quantite), _date_creation::date, _statut::"SCA".etat,_origine::"SCA".etat_lot,_nbUses::int,_cond::"SCA".condition_materiel);
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
    _password text,
    _idindiv text
)
as $$
begin
    insert into "CREDENTIALS".Credentials(email, password,idindividu) values ("SCA".email_CONV(_email),"SCA".password_CONV(_password),"SCA".IDindividu_CONV(_idindiv));
end; $$ language plpgsql;

-- 18. TRAVAILLEUR
create or replace procedure "EMIR".Travailleur_INS(
    _idtravailleur text,
    _idindividu text,
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
    insert into "SCA".Travailleur(idtravailleur, idindividu, date_embauche, poste, departement, salaire_horaire, statut, competences, date_derniere_evaluation) 
    values ("SCA".idtravailleur_CONV(_idtravailleur), "SCA".IDindividu_CONV(_idindividu), _date_embauche::date, "SCA".Nom_CONV(_poste), "SCA".Nom_CONV(_departement), _salaire_horaire::decimal, _statut::"SCA".statut_travailleur, _competences, _date_derniere_evaluation::date);
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
    insert into "SCA".Vehicule(idvehicule, immatriculation, marque, modele, annee_fabrication, type, capacite_charge, capacite_volume, date_acquisition, statut, kilometrage_actuel, date_derniere_maintenance, prochaine_maintenance, carburant, consommation_moyenne) 
    values ("SCA".idvehicule_CONV(_idvehicule), "SCA".Nom_CONV(_immatriculation), "SCA".Nom_CONV(_marque), "SCA".Nom_CONV(_modele), _annee_fabrication::integer, _type::"SCA".type_vehicule, "SCA".dims_CONV(_capacite_charge), "SCA".dims_CONV(_capacite_volume), _date_acquisition::date, _statut::"SCA".statut_vehicule, _kilometrage_actuel::decimal, _date_derniere_maintenance::date, _prochaine_maintenance::date, _carburant, _consommation_moyenne::decimal);
end; $$ language plpgsql;

-- 20. CONDUCTEUR
create or replace procedure "EMIR".Conducteur_INS(
    _idconducteur text,
    _idindividu text,
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
    insert into "SCA".Conducteur(idconducteur, idindividu, numero_permis, type_permis, date_obtention_permis, date_expiration_permis, experience_annees, statut, date_derniere_evaluation, note_evaluation, specialites) 
    values ("SCA".idconducteur_CONV(_idconducteur), "SCA".IDindividu_CONV(_idindividu), "SCA".Nom_CONV(_numero_permis), _type_permis, _date_obtention_permis::date, _date_expiration_permis::date, _experience_annees::integer, _statut::"SCA".statut_conducteur, _date_derniere_evaluation::date, _note_evaluation::decimal, _specialites);
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
                      idtransporteur "SCA".idOrg,
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
                      idtransporteur "SCA".idOrg,
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
                      idindividu "SCA".IDindividu,
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
                      idindividu "SCA".IDindividu,
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

-- Fin des fonctions d'évaluation (_EVA)
-- Les routines MOD, INS, RET peuvent être ajoutées de la même manière si tu veux

-- Fichier SQL : EMIR.sql
-- Description : Routines EMIR pour toutes les entités de la base "SCA"

-- Schéma : "EMIR"

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

--script pour les traitements proposés
-- routines équivalentes à des mises à jour

-- Routines de MODIFICATION (_MOD)

-- 1. ORGANISATION
create or replace procedure "EMIR".Organisation_MOD(
    _idorganisation "SCA".idOrg,
    _nom "SCA".Nom,
    _telephone "SCA".Numero,
    _adresse "SCA".Adresse,
    _type "SCA".typeOrg
)
as $$
begin
    update "SCA".Organisation
    set nom = "SCA".nom_conv(_nom),
        telephone = "SCA".Numero_CONV(_telephone),
        adresse = "SCA".adresse_conv(_adresse),
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
    _idtransporteur "SCA".idOrg,
    _date_creation date,
    _idfournisseur "SCA".idOrg,
    _statut "SCA".etat,
    _remarques text
)
as $$
begin
    update "SCA".Bonreception
    SET idcolis = "SCA".Idcolis_CONV(_idcolis),
        idtransporteur = "SCA".idOrg_CONV(_idtransporteur),
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


--script pour les requetes proposées
--routines équivalentes à des sélections

CREATE OR REPLACE FUNCTION "EMIR".valeur()
    RETURNS FLOAT AS $$
BEGIN
    RETURN (select sum(quantite*prix_unitaire) from "SCA".lot  NATURAL JOIN "SCA".Produit);
END;
$$ LANGUAGE plpgsql;


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
    RETURNS INT AS $$
BEGIN
    RETURN (
        SELECT *
        FROM "SCA".Bonreception
        WHERE date_creation = current_date);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".colis_entrants_date(_date TEXT)
    RETURNS INT AS $$
BEGIN
    RETURN (
        SELECT *
        FROM "SCA".Bonreception
        WHERE date_creation = _date::date);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".colis_sortants_jour()
    RETURNS INT AS $$
BEGIN
    RETURN (
        SELECT *
        FROM "SCA".Bonexpedition
        WHERE date_creation = current_date);
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
                 JOIN "SCA".Entrepot ON "SCA".InventaireEmplacement.idcellule = entrepot.idcellule
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



-- SGE_test-pos.sql
-- Script SQL pour les tests unitaires positifs

-- Désactiver les messages pour des sorties plus propres (optionnel, dépend du client SQL)
-- \set QUIET on

-- Démarrer une transaction pour chaque bloc de test afin de pouvoir faire un ROLLBACK
-- et maintenir l'état de la base de données propre entre les tests.

-- =============================================================================
-- Test 1: Insertion réussie d'une Organisation
-- =============================================================================
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OABCDE', 'TestOrg1', '678901234', 'fournisseur');
SELECT 'Test 1 Passed: Organisation inserted successfully.' AS TestStatus;
-- =============================================================================
-- Test 2: Insertion réussie d'une Cellule
-- =============================================================================
INSERT INTO "SCA".Cellule (idcellule, longueur, largeur, hauteur, masse_maximale)
VALUES ('C00001', 10.0, 5.0, 3.0, 1000.0);
SELECT 'Test 2 Passed: Cellule inserted successfully.' AS TestStatus;

-- =============================================================================
-- Test 3: Insertion réussie d'un Colis
-- =============================================================================

INSERT INTO "SCA".Colis (idcolis, date_creation, statut)
VALUES ('CO00001', '2025-06-20', 'bon etat');
SELECT 'Test 3 Passed: Colis inserted successfully.' AS TestStatus;


-- =============================================================================
-- Test 4: Insertion réussie d'une Zone
-- =============================================================================

INSERT INTO "SCA".Zone (idzone, nom)
VALUES ('ZREC01', 'Zone de Reception 1');
SELECT 'Test 4 Passed: Zone inserted successfully.' AS TestStatus;
-- =============================================================================
-- Test 5: Insertion réussie d'un Individu et d'un Repertoire
-- =============================================================================
INSERT INTO "SCA".individu (idindividu, nom, adresse, telephone)
VALUES ('I00001', 'John Doe', '456 Av. Test', '698765432');

INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OTRANA', 'Transporteur XYZ', '612345678', 'transporteur');

INSERT INTO "SCA".Repertoire (idindividu, idorganisation, role)
VALUES ('I00001', 'OTRANA', 'conducteur');
SELECT 'Test 5 Passed: Individu and Repertoire inserted successfully.' AS TestStatus;

-- =============================================================================
-- Test 6: Insertion réussie d'un Produit Materiel
-- =============================================================================
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OFOURA', 'Fournisseur ABC', '654321098', 'fournisseur');

INSERT INTO "SCA".Produit (idproduit, idfournisseur, nom, description, prix_unitaire, marque, modele, categorie)
VALUES ('P00001', 'OFOURA', 'Boite Carton', 'Grande boite pour emballage', 5.0, 'PackCorp', 'XL-Box', 'materiel d''emballage');

INSERT INTO "SCA".ProduitMateriel (idproduit, longueur, largeur, hauteur, masse)
VALUES ('P00001', 50.0, 40.0, 30.0, 2.0);
SELECT 'Test 6 Passed: Produit Materiel inserted successfully.' AS TestStatus;

-- =============================================================================
-- Test 7: Insertion réussie d'un Lot
-- =============================================================================
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OFOURB', 'Fournisseur DEF', '666555444', 'fournisseur');

INSERT INTO "SCA".Produit (idproduit, idfournisseur, nom, description, prix_unitaire, marque, modele, categorie)
VALUES ('P00002', 'OFOURB', 'SmartPhone X', 'Dernier modele de smartphone', 500.0, 'TechGiant', 'ModelX', 'produit de vente');

INSERT INTO "SCA".Lot (idlot, idproduit, quantite, date_creation, statut, origine, nombre_utilisations, condition)
VALUES ('L00001', 'P00002', 100, '2025-06-15', 'bon etat', 'neuf', 0, 'utilisable');
SELECT 'Test 7 Passed: Lot inserted successfully.' AS TestStatus;


-- =============================================================================
-- Test 8: Insertion réussie d'un Bon de Réception (avec colis et transporteur existants)
-- =============================================================================

INSERT INTO "SCA".Colis (idcolis, date_creation, statut)
VALUES ('CO00002', '2025-06-19', 'bon etat');


INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OTRANB', 'Express Log', '622334455', 'transporteur');
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OFOURC', 'Global Prod', '699887766', 'fournisseur');

INSERT INTO "SCA".Bonreception (idbonreception, idcolis, idtransporteur, date_creation, idfournisseur, statut, remarques)
VALUES ('R00001', 'CO00002', 'OTRANB', '2025-06-20', 'OFOURC', 'bon etat', 'Aucune');
SELECT 'Test 8 Passed: Bonreception inserted successfully.' AS TestStatus;

-- =============================================================================
-- Test 9: Insertion réussie de ContenuColis (réception)
--         Cela devrait passer le trigger `trg_check_reception_consistency`
--         (même si la vérification est limitée sans une table de détails de bon de réception).
-- =============================================================================

INSERT INTO "SCA".Colis (idcolis, date_creation, statut)
VALUES ('CO00003', '2025-06-20', 'bon etat');

INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OTRANC', 'Speedy Cargo', '611223344', 'transporteur');
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OFOURD', 'Tech Supplies', '633445566', 'fournisseur');

INSERT INTO "SCA".Bonreception (idbonreception, idcolis, idtransporteur, date_creation, idfournisseur, statut, remarques)
VALUES ('R00002', 'CO00003', 'OTRANC', '2025-06-20', 'OFOURD', 'bon etat', 'Marchandise conforme');

INSERT INTO "SCA".Produit (idproduit, idfournisseur, nom, description, prix_unitaire, marque, modele, categorie)
VALUES ('P00003', 'OFOURD', 'Souris sans fil', 'Souris optique', 15.0, 'Logi', 'M185', 'produit de vente');

INSERT INTO "SCA".Lot (idlot, idproduit, quantite, date_creation, statut, origine, nombre_utilisations, condition)
VALUES ('L00002', 'P00003', 50, '2025-06-20', 'bon etat', 'neuf', 0, 'utilisable');

INSERT INTO "SCA".ContenuColis (idcolis, idlot, quantite, date_MAJ)
VALUES ('CO00003', 'L00002', 20, '2025-06-21');
SELECT 'Test 9 Passed: ContenuColis (reception) inserted successfully.' AS TestStatus;

-- =============================================================================
-- Test 10: Insertion réussie de ContenuColis (expédition) avec stock suffisant
--          Cela devrait passer le trigger `trg_check_expedition_availability`.
-- =============================================================================
-- Préparer les données nécessaires: Produit, Lot, Cellule, InventaireEmplacement, Colis
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type) VALUES ('OFOURE', 'ElectroInc', '677889900', 'fournisseur');
INSERT INTO "SCA".Produit (idproduit, idfournisseur, nom, description, prix_unitaire, marque, modele, categorie) VALUES ('P00004', 'OFOURE', 'Clavier RGB', 'Clavier mecanique gaming', 80.0, 'GamersBrand', 'K100', 'produit de vente');
INSERT INTO "SCA".Lot (idlot, idproduit, quantite, date_creation, statut, origine, nombre_utilisations, condition) VALUES ('L00003', 'P00004', 100, '2025-06-18', 'bon etat', 'neuf', 0, 'utilisable');
INSERT INTO "SCA".Cellule (idcellule, longueur, largeur, hauteur, masse_maximale) VALUES ('C00002', 5.0, 5.0, 5.0, 500.0);
INSERT INTO "SCA".InventaireEmplacement (idcellule, idlot, quantite, datemaj) VALUES ('C00002', 'L00003', 50, '2025-06-20'); -- Stock de 50 claviers

INSERT INTO "SCA".Colis (idcolis, date_creation, statut) VALUES ('COEXP01', '2025-06-21', 'bon etat');

-- Simuler l'ajout au colis d'expédition
INSERT INTO "SCA".ContenuColis (idcolis, idlot, quantite, date_MAJ)
VALUES ('COEXP01', 'L00003', 10, '2025-06-21'); -- Demande 10, stock 50, devrait passer
SELECT 'Test 10 Passed: ContenuColis (expedition) inserted successfully with sufficient stock.' AS TestStatus;

-- =============================================================================
-- Test 11: Insertion réussie d'un Bon d'Expédition (date après réception)
--          Cela devrait passer le trigger `trg_check_expedition_date`.
-- =============================================================================
-- Créer un colis et son bon de réception
INSERT INTO "SCA".Colis (idcolis, date_creation, statut) VALUES ('COEXP02', '2025-06-10', 'bon etat');
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone,  type) VALUES ('OTRAND', 'Fast Courier', '655443322', 'transporteur');
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone,  type) VALUES ('OFOURF', 'Supplier A', '610203040', 'fournisseur');
INSERT INTO "SCA".Bonreception (idbonreception, idcolis, idtransporteur, date_creation, idfournisseur, statut, remarques)
VALUES ('R00003', 'COEXP02', 'OTRAND', '2025-06-12', 'OFOURF', 'bon etat', 'OK');

-- Créer une organisation destinataire
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type) VALUES ('ODESTA', 'Client Alpha', '601020304', 'destinataire');

-- Insérer le bon d'expédition avec une date postérieure à la réception
INSERT INTO "SCA".Bonexpedition (idbonexpedition, idcolis, idtransporteur, date_creation, iddestinataire, statut, remarques)
VALUES ('E00001', 'COEXP02', 'OTRAND', '2025-06-15', 'ODESTA', 'bon etat', 'Pret pour envoi');
SELECT 'Test 11 Passed: Bonexpedition inserted successfully with valid date.' AS TestStatus;

-- Réactiver les messages (optionnel)
-- \set QUIET off

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

create or replace function "EMIR".Tache_EVA(idindividu "SCA".idindividu)
returns table(
    _idtache "SCA".idtache,
    _idcellule "SCA".idcellule,
    _idlot "SCA".idlot,
    _date_creation date,
    _description text,
    _statut text,
    _type text
)
as $$
begin
return query select idtache,idcellule,idlot,date_creation,description,statut,type from "SCA".Tache;
end; $$ language plpgsql;

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

-- =============================================================================
-- Tests pour la fonctionnalité de livraison
-- =============================================================================

-- Test 12: Confirmation de livraison d'un colis
-- Prérequis: Utiliser un colis existant avec bon d'expédition
-- Exemple d'utilisation:
-- CALL "EMIR".ConfirmerLivraison_INS('COEXP02', '2025-06-16');
-- SELECT 'Test 12 Passed: Livraison confirmée avec succès.' AS TestStatus;

-- =============================================================================
-- Exemples d'utilisation des nouvelles fonctionnalités
-- =============================================================================

-- Exemple 1: Confirmer la livraison d'un colis (date actuelle)
-- CALL "EMIR".ConfirmerLivraison_INS('COEXP02');

-- Exemple 2: Confirmer la livraison d'un colis avec une date spécifique
-- CALL "EMIR".ConfirmerLivraison_INS('COEXP02', '2025-06-16');

-- Exemple 3: Voir tous les colis livrés
-- SELECT * FROM "EMIR".colis_livres();

-- Exemple 4: Voir les colis livrés entre deux dates
-- SELECT * FROM "EMIR".colis_livres('2025-06-01', '2025-06-30');

-- Exemple 5: Voir les statistiques de livraison
-- SELECT * FROM "EMIR".statistiques_livraison();

-- Exemple 6: Voir les statistiques de livraison pour un mois
-- SELECT * FROM "EMIR".statistiques_livraison('2025-06-01', '2025-06-30');

-- Exemple 7: Voir l'inventaire (excluant les colis livrés)
-- SELECT * FROM "SCA".inventaire;

-- Exemple 8: Voir les colis en cours d'expédition
-- SELECT * FROM "SCA".ColisEnExpedition;

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
return query select id, timestamp,level,message,extra from "SCA".Tache where _timestamp between _date1 and _date2;
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
return query select id, timestamp,level,message,extra from "SCA".Tache where _timestamp >= _date;
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
return query select id, timestamp,level,message,extra from "SCA".Tache where _timestamp <= _date;
end; $$ language plpgsql;
*