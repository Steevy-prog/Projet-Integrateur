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
    RETURN (
        SELECT *
        FROM "SCA".Bonreception
        WHERE date_creation = current_date);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".colis_entrants_date(_date TEXT)
    RETURNS SETOF "SCA".Bonreception AS $$
BEGIN
    RETURN (
        SELECT *
        FROM "SCA".Bonreception
        WHERE date_creation = _date::date);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "EMIR".colis_sortants_jour()
    RETURNS SETOF "SCA".Bonexpedition AS $$
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

create or replace function "EMIR".Tache_EVA(_idindividu "SCA".idindividu)
    returns table(
                     _idtache "SCA".idtache,
                     _idtravailleur "SCA".idtravailleur,
                     _idcellule "SCA".idcellule,
                     _idlot "SCA".idlot,
                     _date_creation date,
                     _description text,
                     _statut text,
                     _type text
                 )
as $$
begin
    return query select idtache,idcellule,idlot,date_creation,description,statut,type from "SCA".Tache where idtravailleur = _idtravailleur;
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