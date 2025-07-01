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

