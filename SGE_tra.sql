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
    _expected_date date,
    _receiving_organisation "SCA".idOrg,
    _statut "SCA".etat
)
as $$
begin
    update "SCA".Colis
    set date_creation = _date_creation::date,
        expected_date = _expected_date::date,
        receiving_organisation = "SCA".idOrg_conv(_receiving_organisation),
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
    _idtransporteur "SCA".idconducteur,
    _date_creation date,
    _iddestinataire "SCA".idOrg,
    _statut "SCA".etat,
    _remarques text
)
as $$
begin
    update "SCA".Bonexpedition
    SET idcolis = "SCA".Idcolis_CONV(_idcolis),
        idtransporteur = "SCA".idconducteur_CONV(_idtransporteur),
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
    _prenom "SCA".Nom,
    _adresse "SCA".Adresse,
    _telephone "SCA".Numero
)
as $$
begin
    update "SCA".Individu
    SET nom = "SCA".Nom_CONV(_nom),
        prenom = "SCA".Nom_CONV(_prenom),
        adresse = "SCA".Adresse_CONV(_adresse),
        telephone = "SCA".Numero_CONV(_telephone)
    WHERE idindividu = "SCA".IDindividu_CONV(_idindividu);
end; $$ language plpgsql;

-- 8. REPERTOIRE
CREATE OR REPLACE PROCEDURE "EMIR".Repertoire_MOD(
    _idrepertoire TEXT,
    _date_debut DATE DEFAULT NULL,
    _date_fin DATE DEFAULT NULL,
    _idindividu TEXT DEFAULT NULL,
    _idorganisation TEXT DEFAULT NULL,
    _role TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".Repertoire
    SET
        date_debut = COALESCE(_date_debut, date_debut),
        date_fin = COALESCE(_date_fin, date_fin),
        idindividu = COALESCE("SCA".idindividu_conv(_idindividu), idindividu),
        idorganisation = COALESCE("SCA".idorg_conv(_idorganisation), idorganisation),
        role = COALESCE(_role::"SCA".roles, role)
    WHERE idrepertoire = "SCA".idrepertoire_conv(_idrepertoire);
END;
$$ LANGUAGE plpgsql;

-- 9. PRODUIT
CREATE OR REPLACE PROCEDURE "EMIR".Produit_MOD(
    _idproduit TEXT,
    _idfournisseur TEXT DEFAULT NULL,
    _nom TEXT DEFAULT NULL,
    _description TEXT DEFAULT NULL,
    _prix_unitaire FLOAT DEFAULT NULL,
    _idmodele TEXT DEFAULT NULL,
    _categorie TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".Produit
    SET
        idfournisseur = COALESCE("SCA".idorg_conv(_idfournisseur), idfournisseur),
        nom = COALESCE("SCA".nom_conv(_nom), nom),
        description = COALESCE(_description, description),
        prix_unitaire = COALESCE(_prix_unitaire, prix_unitaire),
        idmodele = COALESCE("SCA".idmodele_conv(_idmodele), idmodele),
        categorie = COALESCE(_categorie::"SCA".categorie_produit, categorie)
    WHERE idproduit = "SCA".idproduit_conv(_idproduit);
END;
$$ LANGUAGE plpgsql;

-- 10. PRODUITMATERIEL
CREATE OR REPLACE PROCEDURE "EMIR".ProduitMateriel_MOD(
    _idproduit TEXT,
    _longueur TEXT DEFAULT NULL,
    _largeur TEXT DEFAULT NULL,
    _hauteur TEXT DEFAULT NULL,
    _masse TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".ProduitMateriel
    SET
        longueur = COALESCE("SCA".dims_conv(_longueur), longueur),
        largeur = COALESCE("SCA".dims_conv(_largeur), largeur),
        hauteur = COALESCE("SCA".dims_conv(_hauteur), hauteur),
        masse = COALESCE("SCA".dims_conv(_masse), masse)
    WHERE idproduit = "SCA".idproduit_conv(_idproduit);
END;
$$ LANGUAGE plpgsql;

-- 11. PRODUITLOGICIEL
CREATE OR REPLACE PROCEDURE "EMIR".ProduitLogiciel_MOD(
    _idproduit TEXT,
    _version TEXT DEFAULT NULL,
    _license TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".ProduitLogiciel
    SET
        version = COALESCE("SCA".nom_conv(_version), version),
        license = COALESCE("SCA".nom_conv(_license), license)
    WHERE idproduit = "SCA".idproduit_conv(_idproduit);
END;
$$ LANGUAGE plpgsql;

-- 12. LOT
create or replace procedure "EMIR".Lot_MOD(
    _idlot "SCA".idlot,
    _idproduit "SCA".Idproduit,
    _quantite "SCA".dims,
    _date_creation date
)
as $$
begin
    update "SCA".Lot
    SET idproduit = "SCA".Idproduit_CONV(_idproduit),
        quantite = "SCA".dims_CONV(_quantite),
        date_creation = _date_creation::date
    WHERE idlot = "SCA".Idlot_CONV(_idlot);
end; $$ language plpgsql;

-- 13. CONTENUCOLIS
CREATE OR REPLACE PROCEDURE "EMIR".ContenuColis_MOD(
    _idcontenu TEXT,
    _idcolis TEXT DEFAULT NULL,
    _idlot TEXT DEFAULT NULL,
  
    _date_maj DATE DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".ContenuColis
    SET
        idcolis = COALESCE("SCA".idcolis_conv(_idcolis), idcolis),
        idlot = COALESCE("SCA".idlot_conv(_idlot), idlot),
        date_maj = COALESCE(_date_maj, date_maj)
    WHERE idcontenu = "SCA".idcontenu_conv(_idcontenu);
END;
$$ LANGUAGE plpgsql;

-- 14. ENTREPOT
CREATE OR REPLACE PROCEDURE "EMIR".Entrepot_MOD(
    _idcellule TEXT,
    _position TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".entrepot
    SET
        position = COALESCE("SCA".idzone_conv(_position), position)
    WHERE idcellule = "SCA".idcellule_conv(_idcellule);
END;
$$ LANGUAGE plpgsql;

-- 15. RAPPORTEXCEPTION
CREATE OR REPLACE PROCEDURE "EMIR".RapportException_MOD(
    _idrapport TEXT,
    _idcolis TEXT DEFAULT NULL,
    _type TEXT DEFAULT NULL,
    _date_creation DATE DEFAULT NULL,
    _description TEXT DEFAULT NULL,
    _statut TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".RapportException
    SET
        idcolis = COALESCE("SCA".idcolis_conv(_idcolis), idcolis),
        type = COALESCE(_type::"SCA".rapports, type),
        date_creation = COALESCE(_date_creation, date_creation),
        description = COALESCE(_description, description),
        statut = COALESCE(_statut::"SCA".etatexception, statut)
    WHERE idrapport = "SCA".idrapport_conv(_idrapport);
END;
$$ LANGUAGE plpgsql;

-- 16. INVENTAIREEMPLACEMENT
CREATE OR REPLACE PROCEDURE "EMIR".InventaireEmplacement_MOD(
    _idinventaire TEXT,
    _idcellule TEXT DEFAULT NULL,
    _idlot TEXT DEFAULT NULL,
    _datemaj DATE DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".InventaireEmplacement
    SET
        idcellule = COALESCE("SCA".idcellule_conv(_idcellule), idcellule),
        idlot = COALESCE("SCA".idlot_conv(_idlot), idlot),
        datemaj = COALESCE(_datemaj, datemaj)
    WHERE idinventaire = "SCA".idinventaire_conv(_idinventaire);
END;
$$ LANGUAGE plpgsql;

-- 17. TRAVAILLEUR
CREATE OR REPLACE PROCEDURE "EMIR".Travailleur_MOD(
    _idtravailleur TEXT,
    _idutilisateur TEXT DEFAULT NULL,
    _date_embauche DATE DEFAULT NULL,
    _poste TEXT DEFAULT NULL,
    _departement TEXT DEFAULT NULL,
    _salaire_horaire DECIMAL(10,2) DEFAULT NULL,
    _statut TEXT DEFAULT NULL,
    _date_derniere_evaluation DATE DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".Travailleur
    SET
        idutilisateur = COALESCE("SCA".idutilisateur_conv(_idutilisateur), idutilisateur),
        date_embauche = COALESCE(_date_embauche, date_embauche),
        poste = COALESCE("SCA".nom_conv(_poste), poste),
        departement = COALESCE("SCA".nom_conv(_departement), departement),
        salaire_horaire = COALESCE(_salaire_horaire, salaire_horaire),
        statut = COALESCE(_statut::"SCA".statut_travailleur, statut),
        date_derniere_evaluation = COALESCE(_date_derniere_evaluation, date_derniere_evaluation)
    WHERE idtravailleur = "SCA".idtravailleur_conv(_idtravailleur);
END;
$$ LANGUAGE plpgsql;

-- 18. TACHE
CREATE OR REPLACE PROCEDURE "EMIR".Tache_MOD(
    _idtache TEXT,
    _idtravailleur TEXT DEFAULT NULL,
    _idcellule TEXT DEFAULT NULL,
    _idcolis TEXT DEFAULT NULL,
    _date_creation DATE DEFAULT NULL,
    _date_echeance DATE DEFAULT NULL,
    _duree_estimee INT DEFAULT NULL,
    _description TEXT DEFAULT NULL,
    _priority TEXT DEFAULT NULL,
    _statut TEXT DEFAULT NULL,
    _type TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".Tache
    SET
        idtravailleur = COALESCE("SCA".idtravailleur_conv(_idtravailleur), idtravailleur),
        idcellule = COALESCE("SCA".idcellule_conv(_idcellule), idcellule),
        idcolis = COALESCE("SCA".idcolis_conv(_idcolis), idcolis),
        date_creation = COALESCE(_date_creation, date_creation),
        date_echeance = COALESCE(_date_echeance, date_echeance),
        duree_estimee = COALESCE(_duree_estimee, duree_estimee),
        description = COALESCE(_description, description),
        priority = COALESCE(_priority, priority),
        statut = COALESCE(_statut, statut),
        type = COALESCE(_type, type)
    WHERE idtache = "SCA".idtache_conv(_idtache);
END;
$$ LANGUAGE plpgsql;

-- 19. VEHICULE
CREATE OR REPLACE PROCEDURE "EMIR".Vehicule_MOD(
    _idvehicule TEXT,
    _immatriculation TEXT DEFAULT NULL,
    _idmodele TEXT DEFAULT NULL,
    _annee_fabrication INTEGER DEFAULT NULL,
    _types TEXT DEFAULT NULL,
    _capacite_charge TEXT DEFAULT NULL,
    _capacite_volume TEXT DEFAULT NULL,
    _date_acquisition DATE DEFAULT NULL,
    _statut TEXT DEFAULT NULL,
    _kilometrage_actuel DECIMAL(10,2) DEFAULT NULL,
    _date_derniere_maintenance DATE DEFAULT NULL,
    _prochaine_maintenance DATE DEFAULT NULL,
    _carburant VARCHAR(20) DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".Vehicule
    SET
        immatriculation = COALESCE("SCA".nom_conv(_immatriculation), immatriculation),
        idmodele = COALESCE("SCA".idmodele_conv(_idmodele), idmodele),
        annee_fabrication = COALESCE(_annee_fabrication, annee_fabrication),
        types = COALESCE(_types::"SCA".type_vehicule, types),
        capacite_charge = COALESCE("SCA".dims_conv(_capacite_charge), capacite_charge),
        capacite_volume = COALESCE("SCA".dims_conv(_capacite_volume), capacite_volume),
        date_acquisition = COALESCE(_date_acquisition, date_acquisition),
        statut = COALESCE(_statut::"SCA".statut_vehicule, statut),
        kilometrage_actuel = COALESCE(_kilometrage_actuel, kilometrage_actuel),
        date_derniere_maintenance = COALESCE(_date_derniere_maintenance, date_derniere_maintenance),
        prochaine_maintenance = COALESCE(_prochaine_maintenance, prochaine_maintenance),
        carburant = COALESCE(_carburant, carburant)
    WHERE idvehicule = "SCA".idvehicule_conv(_idvehicule);
END;
$$ LANGUAGE plpgsql;

-- 20. CONDUCTEUR
CREATE OR REPLACE PROCEDURE "EMIR".Conducteur_MOD(
    _idconducteur TEXT,
    _idutilisateur TEXT DEFAULT NULL,
    _numero_permis TEXT DEFAULT NULL,
    _type_permis VARCHAR(10) DEFAULT NULL,
    _date_obtention_permis DATE DEFAULT NULL,
    _date_expiration_permis DATE DEFAULT NULL,
    _experience_annees INTEGER DEFAULT NULL,
    _statut TEXT DEFAULT NULL,
    _date_derniere_evaluation DATE DEFAULT NULL,
    _note_evaluation DECIMAL(3,2) DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".Conducteur
    SET
        idutilisateur = COALESCE("SCA".idutilisateur_conv(_idutilisateur), idutilisateur),
        numero_permis = COALESCE("SCA".nom_conv(_numero_permis), numero_permis),
        type_permis = COALESCE(_type_permis, type_permis),
        date_obtention_permis = COALESCE(_date_obtention_permis, date_obtention_permis),
        date_expiration_permis = COALESCE(_date_expiration_permis, date_expiration_permis),
        experience_annees = COALESCE(_experience_annees, experience_annees),
        statut = COALESCE(_statut::"SCA".statut_conducteur, statut),
        date_derniere_evaluation = COALESCE(_date_derniere_evaluation, date_derniere_evaluation),
        note_evaluation = COALESCE(_note_evaluation, note_evaluation)
    WHERE idconducteur = "SCA".idconducteur_conv(_idconducteur);
END;
$$ LANGUAGE plpgsql;

-- 21. UTILISATEUR
CREATE OR REPLACE PROCEDURE "EMIR".Utilisateur_MOD(
    _idutilisateur TEXT,
    _idindividu TEXT DEFAULT NULL,
    _username TEXT DEFAULT NULL,
    _date_inscription TIMESTAMP DEFAULT NULL,
    _date_derniere_connexion TIMESTAMP DEFAULT NULL,
    _statut TEXT DEFAULT NULL,
    _niveau_acces TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".Utilisateur
    SET
        idindividu = COALESCE("SCA".idindividu_conv(_idindividu), idindividu),
        username = COALESCE("SCA".username_conv(_username), username),
        date_inscription = COALESCE(_date_inscription, date_inscription),
        date_derniere_connexion = COALESCE(_date_derniere_connexion, date_derniere_connexion),
        statut = COALESCE(_statut::"SCA".statut_utilisateur, statut),
        niveau_acces = COALESCE(_niveau_acces::"SCA".niveau_acces, niveau_acces)
    WHERE idutilisateur = "SCA".idutilisateur_conv(_idutilisateur);
END;
$$ LANGUAGE plpgsql;

-- 22. CREDENTIALS
CREATE OR REPLACE PROCEDURE "EMIR".Credentials_MOD(
    _email TEXT,
    _mot_de_passe_hash TEXT DEFAULT NULL,
    _idutilisateur TEXT DEFAULT NULL,
    _date_creation TIMESTAMP DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "CREDENTIALS".Credentials
    SET
        mot_de_passe_hash = COALESCE(_mot_de_passe_hash, mot_de_passe_hash),
        idutilisateur = COALESCE("SCA".idutilisateur_conv(_idutilisateur), idutilisateur),
        date_creation = COALESCE(_date_creation, date_creation)
    WHERE email = "SCA".email_conv(_email);
END;
$$ LANGUAGE plpgsql;

-- 23. PASSWORDPOLICIES
CREATE OR REPLACE PROCEDURE "EMIR".PasswordPolicies_MOD(
    _setting_name TEXT,
    _setting_value TEXT DEFAULT NULL,
    _setting_group TEXT DEFAULT NULL,
    _description TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "CREDENTIALS".PasswordPolicies
    SET
        setting_value = COALESCE(_setting_value, setting_value),
        setting_group = COALESCE(_setting_group, setting_group),
        description = COALESCE(_description, description)
    WHERE setting_name = _setting_name;
END;
$$ LANGUAGE plpgsql;

-- 24. LOCALISATIONORGANISATION
CREATE OR REPLACE PROCEDURE "EMIR".LocalisationOrganisation_MOD(
    _idlocalisation INTEGER,
    _idorganisation TEXT DEFAULT NULL,
    _adresse TEXT DEFAULT NULL,
    _ville TEXT DEFAULT NULL,
    _region TEXT DEFAULT NULL,
    _pays VARCHAR(60) DEFAULT NULL,
    _latitude DOUBLE PRECISION DEFAULT NULL,
    _longitude DOUBLE PRECISION DEFAULT NULL,
    _date_ajout DATE DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".LocalisationOrganisation
    SET
        idorganisation = COALESCE("SCA".idorg_conv(_idorganisation), idorganisation),
        adresse = COALESCE("SCA".adresse_conv(_adresse), adresse),
        ville = COALESCE(_ville, ville),
        region = COALESCE(_region, region),
        pays = COALESCE(_pays, pays),
        latitude = COALESCE(_latitude, latitude),
        longitude = COALESCE(_longitude, longitude),
        date_ajout = COALESCE(_date_ajout, date_ajout)
    WHERE idlocalisation = _idlocalisation;
END;
$$ LANGUAGE plpgsql;

-- 25. CREDENTIALS.CredentialsOrganisation
CREATE OR REPLACE PROCEDURE "EMIR".CredentialsOrganisation_MOD(
    _idorganisation TEXT,
    _mdpOrg TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "CREDENTIALS".organisation
    SET
        mdpOrg = COALESCE(_mdpOrg, mdpOrg)
    WHERE idorganisation = "SCA".idorg_conv(_idorganisation);
END;
$$ LANGUAGE plpgsql;

-- 26. LIVRAISONCONDUCTEURCOLIS MODIFICATION
CREATE OR REPLACE PROCEDURE "EMIR".LivraisonConducteurColis_MOD(
    _idlivraison INTEGER,
    _idconducteur TEXT DEFAULT NULL,
    _idbonexpedition TEXT DEFAULT NULL,
    _date_affectation DATE DEFAULT NULL,
    _statut TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".LivraisonConducteurColis
    SET
        idconducteur = COALESCE("SCA".idconducteur_conv(_idconducteur), idconducteur),
        idbonexpedition = COALESCE("SCA".Bonexped_conv(_idbonexpedition), idbonexpedition),
        date_affectation = COALESCE(_date_affectation, date_affectation),
        statut = COALESCE(_statut::"SCA".etatcolis, statut)
    WHERE idlivraison = _idlivraison;
END;
$$ LANGUAGE plpgsql;


-- 28. EXTERNE.COLIS
CREATE OR REPLACE PROCEDURE "EMIR".PColis_MOD(
    _idpcolis TEXT,
    _idorg TEXT DEFAULT NULL,
    _date_creation DATE DEFAULT NULL,
    _expected_date DATE DEFAULT NULL,
    _receiving_org TEXT DEFAULT NULL,
    _statut TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "EXTERNE".Colis
    SET
        idorg = COALESCE("SCA".idorg_conv(_idorg), idorg),
        date_creation = COALESCE(_date_creation, date_creation),
        expected_date = COALESCE(_expected_date, expected_date),
        receiving_org = COALESCE("SCA".idorg_conv(_receiving_org), receiving_org),
        statut = COALESCE(_statut::"SCA".retatcolis, statut)
    WHERE idpcolis = "EXTERNE".idpcolis_conv(_idpcolis);
END;
$$ LANGUAGE plpgsql;

-- 29. EXTERNE.LOT
CREATE OR REPLACE PROCEDURE "EMIR".PLot_MOD(
    _idplot TEXT,
    _idorg TEXT DEFAULT NULL,
    _idproduit TEXT DEFAULT NULL,
    _quantite TEXT DEFAULT NULL,
    _date_creation DATE DEFAULT NULL,
    _statut TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "EXTERNE".Lot
    SET
        idorg = COALESCE("SCA".idorg_conv(_idorg), idorg),
        idproduit = COALESCE("SCA".idproduit_conv(_idproduit), idproduit),
        quantite = COALESCE("SCA".dims_conv(_quantite), quantite),
        date_creation = COALESCE(_date_creation, date_creation),
        statut = COALESCE(_statut::"SCA".etat_lot, statut)
    WHERE idplot = "EXTERNE".idplot_conv(_idplot);
END;
$$ LANGUAGE plpgsql;

-- 30. EXTERNE.CONTENUCOLIS
CREATE OR REPLACE PROCEDURE "EMIR".PContenuColis_MOD(
    _idpcontenu TEXT,
    _idorg TEXT DEFAULT NULL,
    _idpcolis TEXT DEFAULT NULL,
    _idplot TEXT DEFAULT NULL,
    _quantite TEXT DEFAULT NULL,
    _date_maj DATE DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "EXTERNE".ContenuColis
    SET
        idorg = COALESCE("SCA".idorg_conv(_idorg), idorg),
        idpcolis = COALESCE("EXTERNE".idpcolis_conv(_idpcolis), idpcolis),
        idplot = COALESCE("EXTERNE".idplot_conv(_idplot), idplot),
        quantite = COALESCE("SCA".dims_conv(_quantite), quantite),
        date_maj = COALESCE(_date_maj, date_maj)
    WHERE idpcontenu = "SCA".idpcontenu_conv(_idpcontenu);
END;
$$ LANGUAGE plpgsql;

-- 31. EXTERNE.INQUIRIES
CREATE OR REPLACE PROCEDURE "EMIR".inquiries_MOD(
    _idinq TEXT,
    _idutilisateur TEXT DEFAULT NULL,
    _type TEXT DEFAULT NULL,
    _period TIMESTAMP DEFAULT NULL,
    _status TEXT DEFAULT NULL,
    _description TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "EXTERNE".inquiries
    SET
        idutilisateur = COALESCE("SCA".idutilisateur_conv(_idutilisateur), idutilisateur),
        type = COALESCE(_type::"EXTERNE".typeinquire, type),
        period = COALESCE(_period, period),
        status = COALESCE(_status::"EXTERNE".etatinq, status),
        description = COALESCE(_description, description)
    WHERE idinq = "EXTERNE".idinquire_conv(_idinq);
END;
$$ LANGUAGE plpgsql;

-- 32. BUGREPORT
CREATE OR REPLACE PROCEDURE "EMIR".Bugreport_MOD(
    _id INTEGER,
    _idutilisateur TEXT DEFAULT NULL,
    _description TEXT DEFAULT NULL,
    _date_creation TIMESTAMP DEFAULT NULL,
    _statut TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".Bugreport
    SET
        idutilisateur = COALESCE("SCA".idutilisateur_conv(_idutilisateur), idutilisateur),
        description = COALESCE(_description, description),
        date_creation = COALESCE(_date_creation, date_creation),
        statut = COALESCE(_statut::"EXTERNE".etatinq, statut)
    WHERE id = _id;
END;
$$ LANGUAGE plpgsql;

-- 33. CONDUCTEURSPECIALITE
CREATE OR REPLACE PROCEDURE "EMIR".ConducteurSpecialite_MOD(
    _idconducteur VARCHAR(50),
    _idspecialite VARCHAR(50),
    _date_obtention DATE DEFAULT NULL,
    _niveau VARCHAR(50) DEFAULT NULL,
    _certifie BOOLEAN DEFAULT NULL,
    _date_expiration DATE DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".ConducteurSpecialite
    SET
        date_obtention = COALESCE(_date_obtention, date_obtention),
        niveau = COALESCE(_niveau, niveau),
        certifie = COALESCE(_certifie, certifie),
        date_expiration = COALESCE(_date_expiration, date_expiration)
    WHERE idconducteur = _idconducteur AND idspecialite = _idspecialite;
END;
$$ LANGUAGE plpgsql;

-- 34. TRAVAILLEURCOMPETENCE
CREATE OR REPLACE PROCEDURE "EMIR".TravailleurCompetence_MOD(
    _idtravailleur VARCHAR(50),
    _idcompetence VARCHAR(50),
    _niveau_maitrise VARCHAR(50) DEFAULT NULL,
    _date_acquisition DATE DEFAULT NULL,
    _certifie BOOLEAN DEFAULT NULL,
    _date_derniere_evaluation DATE DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".TravailleurCompetence
    SET
        niveau_maitrise = COALESCE(_niveau_maitrise, niveau_maitrise),
        date_acquisition = COALESCE(_date_acquisition, date_acquisition),
        certifie = COALESCE(_certifie, certifie),
        date_derniere_evaluation = COALESCE(_date_derniere_evaluation, date_derniere_evaluation)
    WHERE idtravailleur = _idtravailleur AND idcompetence = _idcompetence;
END;
$$ LANGUAGE plpgsql;

-- 35. CONSOMMATIONVEHICULE
CREATE OR REPLACE PROCEDURE "EMIR".ConsommationVehicule_MOD(
    _idconsommation VARCHAR(50),
    _idvehicule VARCHAR(50) DEFAULT NULL,
    _consommation_moyenne DECIMAL(5,2) DEFAULT NULL,
    _date_mesure DATE DEFAULT NULL,
    _conditions_mesure TEXT DEFAULT NULL,
    _kilometrage_debut DECIMAL(10,2) DEFAULT NULL,
    _kilometrage_fin DECIMAL(10,2) DEFAULT NULL,
    _litres_consommes DECIMAL(8,2) DEFAULT NULL,
    _type_trajet VARCHAR(50) DEFAULT NULL,
    _date_creation TIMESTAMP DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".ConsommationVehicule
    SET
        idvehicule = COALESCE(_idvehicule, idvehicule),
        consommation_moyenne = COALESCE(_consommation_moyenne, consommation_moyenne),
        date_mesure = COALESCE(_date_mesure, date_mesure),
        conditions_mesure = COALESCE(_conditions_mesure, conditions_mesure),
        kilometrage_debut = COALESCE(_kilometrage_debut, kilometrage_debut),
        kilometrage_fin = COALESCE(_kilometrage_fin, kilometrage_fin),
        litres_consommes = COALESCE(_litres_consommes, litres_consommes),
        type_trajet = COALESCE(_type_trajet, type_trajet),
        date_creation = COALESCE(_date_creation, date_creation)
    WHERE idconsommation = _idconsommation;
END;
$$ LANGUAGE plpgsql;

-- 36. LOGSEXTRA
CREATE OR REPLACE PROCEDURE "EMIR".LogsExtra_MOD(
    _id INTEGER,
    _log_id INTEGER DEFAULT NULL,
    _cle VARCHAR(100) DEFAULT NULL,
    _valeur TEXT DEFAULT NULL,
    _date_creation TIMESTAMP DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".LogsExtra
    SET
        log_id = COALESCE(_log_id, log_id),
        cle = COALESCE(_cle, cle),
        valeur = COALESCE(_valeur, valeur),
        date_creation = COALESCE(_date_creation, date_creation)
    WHERE id = _id;
END;
$$ LANGUAGE plpgsql;

-- 37. APPLICATION_THEME
CREATE OR REPLACE PROCEDURE "EMIR".application_theme_MOD(
    _theme_name TEXT,
    _interface TEXT,
    _theme_qss TEXT DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "CREDENTIALS".application_theme
    SET
        theme_qss = COALESCE(_theme_qss, theme_qss)
    WHERE theme_name = _theme_name AND interface = _interface;
END;
$$ LANGUAGE plpgsql;
