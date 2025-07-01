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