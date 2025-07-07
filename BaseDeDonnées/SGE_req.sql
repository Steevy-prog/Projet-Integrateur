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
    RETURN QUERY (
        SELECT *
        FROM "SCA".Bonreception
        WHERE date_creation = current_date);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".colis_entrants_date(_date TEXT)
    RETURNS SETOF "SCA".Bonreception AS $$
BEGIN
    RETURN QUERY (
        SELECT *
        FROM "SCA".Bonreception
        WHERE date_creation = _date::date);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".colis_sortants_jour()
    RETURNS SETOF "SCA".Bonexpedition AS $$
BEGIN
    RETURN QUERY (
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

CREATE OR REPLACE FUNCTION "EMIR".avgitemsreception()
RETURNS INTEGER AS $$
DECLARE
    nb_colis INTEGER;
BEGIN
    SELECT COUNT(DISTINCT idcolis)
    INTO nb_colis
    FROM "SCA".bonreception
    WHERE date_creation = CURRENT_DATE;

    RETURN nb_colis;
END;
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



CREATE OR REPLACE FUNCTION "EMIR".avgitemsexpedition()
RETURNS INTEGER AS $$
DECLARE
    nb_colis INTEGER;
BEGIN
    SELECT COUNT(DISTINCT idcolis)
    INTO nb_colis
    FROM "SCA".Bonexpedition
    WHERE date_creation = CURRENT_DATE;

    RETURN nb_colis;
END;
$$ LANGUAGE plpgsql;


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
    INSERT INTO "SCA".Logs (level, message)
    VALUES ('INFO', 'Colis livré avec succès');

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
    select coalesce(sum("SCA".Produit.prix_unitaire*"SCA".lot.quantite),0) into valeur_livree from "SCA".colis
    join "SCA".bonexpedition on ("SCA".colis.idcolis = "SCA".bonexpedition.idcolis)
    join "SCA".ContenuColis on ("SCA".bonexpedition.idcolis = "SCA".contenucolis.idcolis)
    join "SCA".Lot on ("SCA".ContenuColis.idlot = "SCA".Lot.idlot)
    join "SCA".Produit on ("SCA".Lot.idproduit = "SCA".Produit.idproduit)
    where "SCA".colis.statut = 'livre'::"SCA".etat
     AND (_date_debut IS NULL OR "SCA".bonexpedition.date_creation >= _date_debut)
      AND (_date_fin IS NULL OR "SCA".bonexpedition.date_creation <= _date_fin);
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

--TRIGGER AUTOMATIQUE POUR nbuses
CREATE OR REPLACE FUNCTION "SCA".lotemballage_set_recycle() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.nbuses >= 3 THEN
        NEW.condition := 'a recycler';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_lotemballage_nbuses ON "SCA".LotEmballage;
CREATE TRIGGER trg_lotemballage_nbuses
BEFORE INSERT OR UPDATE ON "SCA".LotEmballage
FOR EACH ROW
EXECUTE FUNCTION "SCA".lotemballage_set_recycle();

-- TRIGGER pour Travailleur
CREATE OR REPLACE FUNCTION "SCA".check_travailleur_dates() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.date_derniere_evaluation IS NOT NULL AND NEW.date_derniere_evaluation < NEW.date_embauche THEN
        RAISE EXCEPTION 'La date de dernière évaluation (%), ne peut pas être antérieure à la date d''embauche (%)', NEW.date_derniere_evaluation, NEW.date_embauche;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_travailleur_dates ON "SCA".Travailleur;
CREATE TRIGGER trg_travailleur_dates
BEFORE INSERT OR UPDATE ON "SCA".Travailleur
FOR EACH ROW
EXECUTE FUNCTION "SCA".check_travailleur_dates();

-- TRIGGER pour Conducteur
CREATE OR REPLACE FUNCTION "SCA".check_conducteur_dates() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.date_expiration_permis < NEW.date_obtention_permis THEN
        RAISE EXCEPTION 'La date d''expiration du permis (%) ne peut pas être antérieure à la date d''obtention (%)', NEW.date_expiration_permis, NEW.date_obtention_permis;
    END IF;
    IF NEW.date_derniere_evaluation IS NOT NULL AND NEW.date_derniere_evaluation < NEW.date_obtention_permis THEN
        RAISE EXCEPTION 'La date de dernière évaluation (%) ne peut pas être antérieure à la date d''obtention du permis (%)', NEW.date_derniere_evaluation, NEW.date_obtention_permis;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_conducteur_dates ON "SCA".Conducteur;
CREATE TRIGGER trg_conducteur_dates
BEFORE INSERT OR UPDATE ON "SCA".Conducteur
FOR EACH ROW
EXECUTE FUNCTION "SCA".check_conducteur_dates();

-- TRIGGER pour Vehicule
CREATE OR REPLACE FUNCTION "SCA".check_vehicule_dates() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.date_derniere_maintenance IS NOT NULL AND NEW.date_derniere_maintenance < NEW.date_acquisition THEN
        RAISE EXCEPTION 'La date de dernière maintenance (%) ne peut pas être antérieure à la date d''acquisition (%)', NEW.date_derniere_maintenance, NEW.date_acquisition;
    END IF;
    IF NEW.prochaine_maintenance IS NOT NULL AND NEW.date_derniere_maintenance IS NOT NULL AND NEW.prochaine_maintenance < NEW.date_derniere_maintenance THEN
        RAISE EXCEPTION 'La prochaine maintenance (%) ne peut pas être antérieure à la dernière maintenance (%)', NEW.prochaine_maintenance, NEW.date_derniere_maintenance;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_vehicule_dates ON "SCA".Vehicule;
CREATE TRIGGER trg_vehicule_dates
BEFORE INSERT OR UPDATE ON "SCA".Vehicule
FOR EACH ROW
EXECUTE FUNCTION "SCA".check_vehicule_dates();

-- TRIGGER pour Tache
CREATE OR REPLACE FUNCTION "SCA".check_tache_dates() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.date_echeance < NEW.date_creation THEN
        RAISE EXCEPTION 'La date d''échéance (%) ne peut pas être antérieure à la date de création (%)', NEW.date_echeance, NEW.date_creation;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_tache_dates ON "SCA".Tache;
CREATE TRIGGER trg_tache_dates
BEFORE INSERT OR UPDATE ON "SCA".Tache
FOR EACH ROW
EXECUTE FUNCTION "SCA".check_tache_dates();

create or replace function "EMIR".Logs_get(_date1 timestamp,_date2 timestamp)
    returns table(
                     _id int,
                     _timestamp timestamp,
                     _level varchar(10),
                     _message text
                 )
as $$
begin
return query select id,timestamp,level,message from "SCA".Logs where timestamp between _date1 and _date2;
end; $$ language plpgsql;

create or replace function "EMIR".Logs_gethigher(_date timestamp)
    returns table(
                     _id int,
                     _timestamp timestamp,
                     _level varchar(10),
                     _message text
                 )
as $$
begin
return query select id, timestamp,level,message from "SCA".Logs where timestamp >= _date;
end; $$ language plpgsql;

create or replace function "EMIR".Logs_getlower(_date timestamp)
    returns table(
                     _id int,
                     _timestamp timestamp,
                     _level varchar(10),
                     _message text
                 )
as $$
begin
return query select id, timestamp,level,message from "SCA".Logs where timestamp <= _date;
end; $$ language plpgsql;

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

create or replace function "EMIR".getvaluecol(_idorg "SCA".idorg,_idcolis "EXTERNE".idpcolis)
returns int as $$
begin
    return(
    select sum("SCA".Produit.prix_unitaire * "EXTERNE".lot.quantite) from "EXTERNE".ContenuColis
    join "EXTERNE".Lot on ("EXTERNE".ContenuColis.idplot = "EXTERNE".Lot.idplot)
    join "SCA".Produit on ("EXTERNE".Lot.idproduit = "SCA".Produit.idproduit)
    where "EXTERNE".ContenuColis.idorg = _idorg and "EXTERNE".ContenuColis.idpcolis = _idcolis);
end;
$$ language plpgsql;

create or replace function "EMIR".getvaluecol(_idcolis "SCA".idcolis)
returns int as $$
begin
    return(
    select sum("SCA".Produit.prix_unitaire * "SCA".lot.quantite) from "SCA".ContenuColis
    join "SCA".Lot on ("SCA".ContenuColis.idlot = "SCA".Lot.idlot)
    join "SCA".Produit on ("SCA".Lot.idproduit = "SCA".Produit.idproduit)
    where "SCA".ContenuColis.idcolis = _idcolis);
end;
$$ language plpgsql;

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

create or replace function "EMIR".getsupplier(_idcolis "SCA".idcolis)
returns setof "SCA".idorg as $$
    begin
        return query select idfournisseur from "SCA".bonreception
        where idcolis = _idcolis
        LIMIT 1;
    end;
$$ language plpgsql;

create or replace function "EMIR".getnameandid()
returns table(
id "SCA".idindividu,
first_name "SCA".nom,
last_name "SCA".nom
)
as $$
begin
return query
select idindividu,nom,prenom from "SCA".individu;
end;
$$ language plpgsql;