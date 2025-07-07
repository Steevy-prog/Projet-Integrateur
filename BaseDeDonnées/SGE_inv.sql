--script pour les invariants requis
-- types, vues, routines et triggers

-- Trigger function to confirm product availability for expedition


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

--INSERT INTO "SCA".Logs (timestamp, level, message) VALUES
   -- ('2024-07-01 08:00:00', 'INFO', 'Démarrage du système'),
    --('2024-07-01 08:05:00', 'WARNING', 'Connexion lente à la base de données'),
    --('2024-07-01 08:10:00', 'ERROR', 'Erreur lors de l\'importation des données');