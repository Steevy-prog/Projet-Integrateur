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
    _prix "SCA".prix,
    _marque "SCA".Nom,
    _modele "SCA".Nom,
    _categorie "SCA".categorie_produit
)
as $$
begin
    update "SCA".Produit
    SET idfournisseur = "SCA".idOrg_CONV(_idfournisseur),
        nom = "SCA".Nom_CONV(_nom),
        description = _description,
        prix = "SCA".prix_CONV(_prix),
        categorie = _categorie::"SCA".categorie_produit,
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
    _statut "SCA".etatexception
)
as $$
begin
    update "SCA".RapportException
    SET idcolis = "SCA".Idcolis_CONV(_idcolis),
        type = _type::"SCA".rapports,
        date_creation = _date_creation::date,
        description = _description,
        statut = _statut::"SCA".etatexception
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
    _idutilisateur "SCA".idutilisateur,
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
        idutilisateur = "SCA".idutilisateur_CONV(_idutilisateur),
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

-- 22. LOTEMBALLAGE MODIFICATION
create or replace procedure "EMIR".LotEmballage_MOD(
    _idlotemballage integer,
    _idproduit text,
    _quantite text,
    _date_creation text,
    _statut text,
    _nbuses int,
    _condition text
)
as $$
begin
    update "SCA".LotEmballage
    set idproduit = "SCA".idproduit_conv(_idproduit),
        quantite = "SCA".dims_conv(_quantite),
        date_creation = _date_creation::date,
        statut = _statut::"SCA".etat_lot,
        nbuses = _nbuses,
        condition = _condition::"SCA".condition_materiel
    where idlotemballage = _idlotemballage;
end; $$ language plpgsql;

-- 23. BUGREPORT MODIFICATION
create or replace procedure "EMIR".Bugreport_MOD(
    _id INTEGER,
    _idutilisateur TEXT DEFAULT NULL,
    _description TEXT DEFAULT NULL,
    _date_creation TIMESTAMP DEFAULT NULL,
    _statut "SCA".statut DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".Bugreport
    SET
        idutilisateur = COALESCE("SCA".idutilisateur_CONV(_idutilisateur), idutilisateur),
        description = COALESCE(_description, description),
        date_creation = COALESCE(_date_creation, date_creation),
        statut = COALESCE(_statut, statut)
    WHERE id = _id;
END;
$$ LANGUAGE plpgsql;

-- 24. LOGS MODIFICATION
create or replace procedure "EMIR".Logs_MOD(
    _id INTEGER,
    _timestamp TIMESTAMP DEFAULT NULL,
    _level VARCHAR(10) DEFAULT NULL,
    _message TEXT DEFAULT NULL,
    _extra JSONB DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".Logs
    SET
        timestamp = COALESCE(_timestamp, timestamp),
        level = COALESCE(_level, level),
        message = COALESCE(_message, message),
        extra = COALESCE(_extra, extra)
    WHERE id = _id;
END;
$$ LANGUAGE plpgsql;

-- 25. CREDENTIALS.Credentials
create or replace procedure "EMIR".CredentialsOrganisation_MOD(
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
create or replace procedure "EMIR".LivraisonConducteurColis_MOD(
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

-- 27. LOCALISATIONORGANISATION MODIFICATION
create or replace procedure "EMIR".LocalisationOrganisation_MOD(
    _idlocalisation INTEGER,
    _idorganisation TEXT DEFAULT NULL,
    _adresse TEXT DEFAULT NULL,
    _ville TEXT DEFAULT NULL,
    _region TEXT DEFAULT NULL,
    _pays TEXT DEFAULT NULL,
    _latitude DOUBLE PRECISION DEFAULT NULL,
    _longitude DOUBLE PRECISION DEFAULT NULL,
    _date_ajout DATE DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "SCA".LocalisationOrganisation
    SET
        idorganisation = COALESCE("SCA".idorg_conv(_idorganisation), idorganisation),
        adresse = COALESCE(_adresse, adresse),
        ville = COALESCE(_ville, ville),
        region = COALESCE(_region, region),
        pays = COALESCE(_pays, pays),
        latitude = COALESCE(_latitude, latitude),
        longitude = COALESCE(_longitude, longitude),
        date_ajout = COALESCE(_date_ajout, date_ajout)
    WHERE idlocalisation = _idlocalisation;
END;
$$ LANGUAGE plpgsql;

-- 28. PASSWORDPOLICIES MODIFICATION
create or replace procedure "EMIR".PasswordPolicies_MOD(
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

-- 29. CREDENTIALS.Credentials
create or replace procedure "EMIR".Credentials_MOD(
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

-- 30. TACHE MODIFICATION
create or replace procedure "EMIR".Tache_MOD(
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

-- 31. EXTERNE.Lot MODIFICATION
create or replace procedure "EMIR".PLot_MOD(
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

-- 32. EXTERNE.ContenuColis MODIFICATION
create or replace procedure "EMIR".PContenuColis_MOD(
    _idorg TEXT,
    _idpcolis TEXT,
    _idplot TEXT,
    _quantite TEXT DEFAULT NULL,
    _date_MAJ DATE DEFAULT NULL
)
AS $$
BEGIN
    UPDATE "EXTERNE".ContenuColis
    SET
        quantite = COALESCE("SCA".dims_conv(_quantite), quantite),
        date_maj = COALESCE(_date_MAJ, date_maj)
    WHERE idorg = "SCA".idorg_conv(_idorg)
      AND idpcolis = "EXTERNE".idpcolis_conv(_idpcolis)
      AND idplot = "EXTERNE".idplot_conv(_idplot);
END;
$$ LANGUAGE plpgsql;

-- 33. EXTERNE.Colis MODIFICATION
create or replace procedure "EMIR".PColis_MOD(
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
