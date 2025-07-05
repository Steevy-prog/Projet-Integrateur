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
    i.adresse,
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

CREATE OR REPLACE FUNCTION "SCA".idtache_CONF(v TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN v ~ '^T[A-Z0-9]{5}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".idtache_CONV(v TEXT)
RETURNS "SCA".idtache AS $$
BEGIN
    IF "SCA".idtache_CONF(v) THEN
        RETURN v::"SCA".idtache;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "SCA".idtache_VAL(v TEXT)
RETURNS "SCA".idtache AS $$
BEGIN
    IF NOT "SCA".idtache_CONF(v) THEN
        RAISE EXCEPTION 'Valeur non conforme pour idtache: %', v;
    END IF;
    RETURN v::"SCA".idtache;
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
    _expected_date text,
    _receiving_org text,
    _statut text
)
as $$
begin
    insert into "SCA".Colis(idcolis, date_creation, expected_date, receiving_org, statut) values ("SCA".idcolis_conv(_idcolis), _date_creation::date, _expected_date::date, "SCA".idorg_conv(_receiving_org), _statut::"SCA".etatcolis);
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
    _adresse text,
    _telephone text
)
as $$
begin
    insert into "SCA".Individu(idindividu, nom, prenom, adresse, telephone) values ("SCA".idindividu_conv(_idindividu), "SCA".nom_conv(_nom), "SCA".nom_conv(_prenom), "SCA".adresse_conv(_adresse), "SCA".numero_conv(_telephone));
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
)
as $$
begin
    insert into "SCA".Lot(idlot, idproduit, quantite, date_creation) values ("SCA".idlot_conv(_idlot), "SCA".idproduit_conv(_idproduit), "SCA".dims_conv(_quantite), _date_creation::date);
end; $$ language plpgsql;

-- 13. CONTENUCOLIS
create or replace procedure "EMIR".ContenuColis_INS(
    _idcolis text,
    _idlot text,
    _date_MAJ text
)
as $$
begin
    insert into "SCA".ContenuColis(idcolis, idlot, date_maj) values ("SCA".idcolis_conv(_idcolis), "SCA".idlot_conv(_idlot), _date_MAJ::date);
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
    _datemaj text
)
as $$
begin
    insert into "SCA".InventaireEmplacement(idcellule, idlot, datemaj) values ("SCA".idcellule_conv(_idcellule), "SCA".idlot_conv(_idlot), _datemaj::date);
end; $$ language plpgsql;

create or replace procedure "EMIR".Credentials_INS(
    _email text,
    _mot_de_passe_hash text,
    _idutilisateur text,
    _date_creation text
)
as $$
begin
    insert into "CREDENTIALS".Credentials(email, mot_de_passe_hash, idutilisateur, date_creation) values ("SCA".email_CONV(_email), _mot_de_passe_hash, "SCA".idutilisateur_CONV(_idutilisateur), _date_creation::date);
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

-- 22. LOTEMBALLAGE
create or replace procedure "EMIR".LotEmballage_INS(
    _idproduit text,
    _quantite text,
    _date_creation text,
    _statut text DEFAULT 'neuf',
    _nbuses int DEFAULT 0,
    _condition text DEFAULT 'utilisable'
)
as $$
begin
    insert into "SCA".LotEmballage(idproduit, quantite, date_creation, statut, nbuses, condition)
    values (
        "SCA".idproduit_conv(_idproduit),
        "SCA".dims_conv(_quantite),
        _date_creation::date,
        _statut::"SCA".etat_lot,
        _nbuses,
        _condition::"SCA".condition_materiel
    );
end; $$ language plpgsql;


CREATE OR REPLACE PROCEDURE "EMIR".Bugreport_INS(
    _idutilisateur TEXT,
    _description TEXT,
    _date_creation TIMESTAMP DEFAULT NULL,
    _statut "EXTERNE".etatinq DEFAULT 'closed'
)
AS $$
BEGIN
    INSERT INTO "SCA".Bugreport(idutilisateur, description, date_creation, statut)
    VALUES (
        "SCA".idutilisateur_CONV(_idutilisateur),
        _description,
        COALESCE(_date_creation, CURRENT_TIMESTAMP),
        COALESCE(_statut, 'ouvert')
    );
END;
$$ LANGUAGE plpgsql;

create or replace procedure "EMIR".PContenuColis_INS(
    _idorg text,
    _idpcolis text,
    _idplot text,
    _date_MAJ text
)
as $$
begin
    insert into "EXTERNE".ContenuColis(idorg,idPcolis, idPlot, date_maj) values ("SCA".idorg_conv(_idorg),"EXTERNE".idpcolis_conv(_idpcolis), "EXTERNE".idplot_conv(_idplot), _date_MAJ::date);
end; $$ language plpgsql;

create or replace procedure "EMIR".PColis_INS(
    _idorg text,
    _idpcolis text,
    _date_creation text,
    _expected_date text,
    _receiving_org text,
    _statut text
)
as $$
begin
    insert into "EXTERNE".Colis(idorg,idpcolis, date_creation, expected_date, receiving_org, statut) values ("SCA".idorg_conv(_idorg),"EXTERNE".idpcolis_conv(_idpcolis), _date_creation::date, _expected_date::date, "SCA".idorg_conv(_receiving_org), _statut::"SCA".retatcolis);
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

CREATE OR REPLACE PROCEDURE "EMIR".Tache_INS(
    _idtache TEXT,
    _idtravailleur TEXT,
    _idcellule TEXT,
    _idcolis TEXT,
    _date_creation TEXT,
    _date_echeance TEXT,
    _duree_estimee INT,
    _description TEXT,
    _priority TEXT,
    _statut TEXT,
    _type TEXT
)
AS $$
BEGIN
    INSERT INTO "SCA".Tache(idtache, idtravailleur, idcellule, idcolis, date_creation, date_echeance, duree_estimee, description, priority, statut, type) VALUES ("SCA".idtache_CONV(_idtache),"SCA".idtravailleur_CONV(_idtravailleur),"SCA".idcellule_CONV(_idcellule),"SCA".idcolis_CONV(_idcolis),_date_creation::date,_date_echeance::date,_duree_estimee,_description,_priority,_statut,_type);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".PasswordPolicies_INS(
    _setting_name TEXT,
    _setting_value TEXT,
    _setting_group TEXT,
    _description TEXT
)
AS $$
BEGIN
    INSERT INTO "CREDENTIALS".PasswordPolicies(setting_name, setting_value, setting_group, description) VALUES (_setting_name, _setting_value, _setting_group, _description);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".CredentialsOrganisation_INS(
    _idorganisation TEXT,
    _mdpOrg TEXT
)
AS $$
BEGIN
    INSERT INTO "CREDENTIALS".organisation(idorganisation, mdpOrg) VALUES ("SCA".idorg_conv(_idorganisation), _mdpOrg);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".Logs_INS(
    _timestamp TIMESTAMP DEFAULT NULL,
    _level VARCHAR(10),
    _message TEXT,
    _extra JSONB DEFAULT NULL
)
AS $$
BEGIN
    INSERT INTO "SCA".Logs(timestamp, level, message, extra) VALUES (COALESCE(_timestamp, CURRENT_TIMESTAMP), _level, _message, _extra);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".LocalisationOrganisation_INS(
    _idorganisation TEXT,
    _adresse TEXT,
    _ville TEXT,
    _region TEXT,
    _pays TEXT DEFAULT 'Cameroun',
    _latitude DOUBLE PRECISION DEFAULT NULL,
    _longitude DOUBLE PRECISION DEFAULT NULL,
    _date_ajout DATE DEFAULT NULL
)
AS $$
BEGIN
    INSERT INTO "SCA".LocalisationOrganisation(idorganisation, adresse, ville, region, pays, latitude, longitude, date_ajout) VALUES ("SCA".idorg_conv(_idorganisation),_adresse,_ville,_region,COALESCE(_pays, 'Cameroun'),_latitude,_longitude,COALESCE(_date_ajout, CURRENT_DATE));
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".LivraisonConducteurColis_INS(
    _idconducteur TEXT,
    _idbonexpedition TEXT,
    _date_affectation DATE DEFAULT NULL,
    _statut TEXT DEFAULT 'Attente'
)
AS $$
BEGIN
    INSERT INTO "SCA".LivraisonConducteurColis(idconducteur, idbonexpedition, date_affectation, statut) VALUES ("SCA".idconducteur_CONV(_idconducteur),"SCA".Bonexped_CONV(_idbonexpedition),COALESCE(_date_affectation, CURRENT_DATE),COALESCE(_statut, 'Attente'));
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".inquiries_INS(
    _idinq         "EXTERNE".Idinquire,
    _idutilisateur "SCA".idutilisateur,
    _type          "EXTERNE".typeinquire,
    _period        timestamp,
    _status        "EXTERNE".etatinq,
    _description   text
)
AS $$
BEGIN
    INSERT INTO "EXTERNE".inquiries(idinq, idutilisateur, type, period, status, description)
    VALUES (_idinq, _idutilisateur, _type, _period, _status, _description);
END;
$$ LANGUAGE plpgsql;
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
    return query select idorganisation, nom, telephone, adresse, type from "SCA".Organisation;
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
    return query select idcellule, longueur, largeur, hauteur, masse_maximale from "SCA".Cellule;
end; $$ language plpgsql;

-- 3. COLIS
create or replace function "EMIR".Colis_EVA()
    returns table (
                      _idcolis "SCA".Idcolis,
                      _date_creation date,
                      _statut "SCA".etatcolis
                  ) as $$
begin
    return query select idcolis, date_creation, statut from "SCA".Colis;
end; $$ language plpgsql;

-- 4. ZONE
create or replace function "EMIR".Zone_EVA()
    returns table (
                      idzone "SCA".Idzone,
                      nom "SCA".Nom
                  ) as $$
begin
    return query select idzone, nom from "SCA".Zone;
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
    return query select idbonreception, idcolis, date_creation, idfournisseur, statut, remarques from "SCA".Bonreception;
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
    return query select idbonexpedition, idcolis, date_creation, iddestinataire, statut, remarques from "SCA".Bonexpedition;
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
    return query select idindividu, nom, prenom, adresse, telephone from "SCA".Individu;
end; $$ language plpgsql;

-- 8. REPERTOIRE
create or replace function "EMIR".Repertoire_EVA()
    returns table (
                      idindividu "SCA".IDindividu,
                      idorganisation "SCA".idOrg,
                      role "SCA".roles
                  ) as $$
begin
    return query select idindividu, idorganisation, role from "SCA".Repertoire;
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
    return query select idproduit, idfournisseur, nom, description, prix_unitaire, marque, modele, categorie from "SCA".Produit;
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
    return query select idproduit, longueur, largeur, hauteur, masse from "SCA".ProduitMateriel;
end; $$ language plpgsql;

create or replace function "EMIR".Tache_EVA(_idtravailleur "SCA".idtravailleur)
    returns table(
                     _idtache "SCA".idtache,
                     _idtravailleur "SCA".idtravailleur,
                     _idcellule "SCA".idcellule,
                     _idcolis "SCA".idcolis,
                     _date_creation date,
                     _date_echeance date,
                     _duree_estimé int,
                     _description text,
                     _statut text,
                     _type text
                 )
as $$
begin
    return query select idtache,idcellule,idcolis,date_creation,date_echeance,duree_estimee,description,statut,type from "SCA".Tache where idtravailleur = _idtravailleur;
end; $$ language plpgsql;

-- 11. PRODUITLOGICIEL
create or replace function "EMIR".ProduitLogiciel_EVA()
    returns table (
                      idproduit "SCA".Idproduit,
                      version "SCA".Nom,
                      license "SCA".Nom
                  ) as $$
begin
    return query select idproduit, version, license from "SCA".ProduitLogiciel;
end; $$ language plpgsql;

-- 12. LOT
create or replace function "EMIR".Lot_EVA()
    returns table (
                      idlot "SCA".idlot,
                      idproduit "SCA".Idproduit,
                      quantite "SCA".dims,
                      date_creation date
                  ) as $$
begin
    return query select idlot, idproduit, quantite, date_creation from "SCA".Lot;
end; $$ language plpgsql;

-- 13. CONTENUCOLIS
create or replace function "EMIR".ContenuColis_EVA()
    returns table (
                      idcolis "SCA".Idcolis,
                      idlot "SCA".Idlot,
                      date_maj date
                  ) as $$
begin
    return query select idcolis, idlot, date_maj from "SCA".ContenuColis;
end; $$ language plpgsql;

-- 14. ENTREPOT
create or replace function "EMIR".Entrepot_EVA()
    returns table (
                      idcellule "SCA".Idcellule,
                      zone "SCA".idzone
                  ) as $$
begin
    return query select idcellule, zone from "SCA".Entrepot;
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
    return query select idrapport, idcolis, type, date_creation, description, statut from "SCA".RapportException;
end; $$ language plpgsql;

-- 17. INVENTAIREEMPLACEMENT
create or replace function "EMIR".InventaireEmplacement_EVA()
    returns table (
                      idcellule "SCA".Idcellule,
                      idlot "SCA".Idlot,
                      datemaj date
                  ) as $$
begin
    return query select idcellule, idlot,datemaj from "SCA".InventaireEmplacement;
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
    return query select idtravailleur, idutilisateur, date_embauche, poste, departement, salaire_horaire, statut, competences, date_derniere_evaluation from "SCA".Travailleur;
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
    return query select idvehicule, immatriculation, marque, modele, annee_fabrication, type, capacite_charge, capacite_volume, date_acquisition, statut, kilometrage_actuel, date_derniere_maintenance, prochaine_maintenance, carburant, consommation_moyenne from "SCA".Vehicule;
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
    return query select idconducteur, idutilisateur, numero_permis, type_permis, date_obtention_permis, date_expiration_permis, experience_annees, statut, date_derniere_evaluation, note_evaluation, specialites from "SCA".Conducteur;
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
    return query select idutilisateur, idindividu, username, date_inscription, date_derniere_connexion, statut, niveau_acces from "SCA".Utilisateur;
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
    return query select email, mot_de_passe_hash, idutilisateur, date_creation from "CREDENTIALS".Credentials;
end; $$ language plpgsql;

-- 22. LOTEMBALLAGE
create or replace function "EMIR".LotEmballage_EVA()
    returns table (
        idlotemballage integer,
        idproduit "SCA".Idproduit,
        quantite "SCA".dims,
        date_creation date,
        statut "SCA".etat_lot,
        nbuses int,
        condition "SCA".condition_materiel
    ) as $$
begin
    return query select idlotemballage, idproduit, quantite, date_creation, statut, nbuses, condition from "SCA".LotEmballage;
end; $$ language plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".Bugreport_EVA()
RETURNS TABLE (
    id INTEGER,
    idutilisateur "SCA".idutilisateur,
    description TEXT,
    date_creation TIMESTAMP,
    statut "SCA".statut
) AS $$
BEGIN
    RETURN QUERY SELECT id, idutilisateur, description, date_creation, statut FROM "SCA".Bugreport;
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

create or replace function "EMIR".PContenuColis_EVA(_idorg "SCA".idorg)
returns table (
    _idpcolis "EXTERNE".idpcolis,
    _idplot "EXTERNE".idplot,
    _date_maj date
)
as $$
begin
  return query select idpcolis,idplot,date_maj from "EXTERNE".ContenuColis where idorg = _idorg;
end; $$ language plpgsql;

create or replace function "EMIR".PContenuColis_EVA1()
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

CREATE OR REPLACE FUNCTION "EMIR".LivraisonConducteurColis_EVA()
RETURNS TABLE (
    idlivraison INTEGER,
    idconducteur "SCA".idconducteur,
    idbonexpedition "SCA".Bonexped,
    date_affectation DATE,
    statut "SCA".etatcolis
) AS $$
BEGIN
    RETURN QUERY
    SELECT idlivraison, idconducteur, idbonexpedition, date_affectation, statut
    FROM "SCA".LivraisonConducteurColis;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".Logs_EVA()
RETURNS TABLE (
    id INTEGER,
    timestamp TIMESTAMP,
    level VARCHAR,
    message TEXT,
    extra JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT id, timestamp, level, message, extra
    FROM "SCA".Logs;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".LocalisationOrganisation_EVA()
RETURNS TABLE (
    idlocalisation INTEGER,
    idorganisation "SCA".idOrg,
    adresse "SCA".Adresse,
    ville VARCHAR,
    region VARCHAR,
    pays VARCHAR,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    date_ajout DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT idlocalisation, idorganisation, adresse, ville, region, pays, latitude, longitude, date_ajout
    FROM "SCA".LocalisationOrganisation;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".PasswordPolicies_EVA()
RETURNS TABLE (
    setting_name VARCHAR,
    setting_value VARCHAR,
    setting_group VARCHAR,
    description VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT setting_name, setting_value, setting_group, description
    FROM "CREDENTIALS".PasswordPolicies;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".CredentialsOrganisation_EVA()
RETURNS TABLE (
    idorganisation "SCA".idOrg,
    mdpOrg TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT idorganisation, mdpOrg
    FROM "CREDENTIALS".organisation;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".inquiries_EVA(_idutilisateur "SCA".idutilisateur)
RETURNS TABLE (
    idinq        "EXTERNE".Idinquire,
    type         "EXTERNE".typeinquire,
    period       timestamp,
    status       "EXTERNE".etatinq,
    description  text
) AS $$
BEGIN
    RETURN QUERY
    SELECT idinq, type, period, status, description
    FROM "EXTERNE".inquiries
    WHERE idutilisateur = _idutilisateur;
END;
$$ LANGUAGE plpgsql;
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

-- 22. LOTEMBALLAGE
create or replace procedure "EMIR".LotEmballage_RET(
    _idlotemballage integer
)
as $$
begin
    delete from "SCA".LotEmballage where idlotemballage = _idlotemballage;
end; $$ language plpgsql;


CREATE OR REPLACE PROCEDURE "EMIR".Bugreport_RET(
    _id INTEGER
)
AS $$
BEGIN
    DELETE FROM "SCA".Bugreport WHERE id = _id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".PColis_RET(
    _idpcolis TEXT
)
AS $$
BEGIN
    DELETE FROM "EXTERNE".Colis
    WHERE idpcolis = "EXTERNE".idpcolis_conv(_idpcolis);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".PLot_RET(
    _idplot TEXT
)
AS $$
BEGIN
    DELETE FROM "EXTERNE".Lot
    WHERE idplot = "EXTERNE".idplot_conv(_idplot);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".PContenuColis_RET(
    _idorg TEXT,
    _idpcolis TEXT,
    _idplot TEXT
)
AS $$
BEGIN
    DELETE FROM "EXTERNE".ContenuColis
    WHERE idorg = "SCA".idorg_conv(_idorg)
      AND idpcolis = "EXTERNE".idpcolis_conv(_idpcolis)
      AND idplot = "EXTERNE".idplot_conv(_idplot);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".Tache_RET(
    _idtache TEXT
)
AS $$
BEGIN
    DELETE FROM "SCA".Tache
    WHERE idtache = "SCA".idtache_conv(_idtache);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".Credentials_RET(
    _email TEXT
)
AS $$
BEGIN
    DELETE FROM "CREDENTIALS".Credentials
    WHERE email = "SCA".email_conv(_email);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".PasswordPolicies_RET(
    _setting_name TEXT
)
AS $$
BEGIN
    DELETE FROM "CREDENTIALS".PasswordPolicies
    WHERE setting_name = _setting_name;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".LocalisationOrganisation_RET(
    _idlocalisation INTEGER
)
AS $$
BEGIN
    DELETE FROM "SCA".LocalisationOrganisation
    WHERE idlocalisation = _idlocalisation;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".Logs_RET(
    _id INTEGER
)
AS $$
BEGIN
    DELETE FROM "SCA".Logs
    WHERE id = _id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".CredentialsOrganisation_RET(
    _idorganisation TEXT
)
AS $$
BEGIN
    DELETE FROM "CREDENTIALS".organisation
    WHERE idorganisation = "SCA".idorg_conv(_idorganisation);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE "EMIR".LivraisonConducteurColis_RET(
    _idlivraison INTEGER
)
AS $$
BEGIN
    DELETE FROM "SCA".LivraisonConducteurColis
    WHERE idlivraison = _idlivraison;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".inquiries_RET(_idinq "EXTERNE".Idinquire)
RETURNS TABLE (
    idutilisateur "SCA".idutilisateur,
    type          "EXTERNE".typeinquire,
    period        timestamp,
    status        "EXTERNE".etatinq,
    description   text
) AS $$
BEGIN
    RETURN QUERY
    SELECT idutilisateur, type, period, status, description
    FROM "EXTERNE".inquiries
    WHERE idinq = _idinq;
END;
$$ LANGUAGE plpgsql;


