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
    _mot_de_passe TEXT
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
        'en attente_validation', 'employe'
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
                d.email,
                uc.niveau_acces,
                uc.statut,
                uc.type_utilisateur
            FROM "SCA".UtilisateursComplets uc NATURAL JOIN "CREDENTIALS".credentials d
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
    email "SCA".email,
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
        d.email,
        uc.niveau_acces,
        uc.statut,
        uc.date_inscription,
        uc.date_derniere_connexion
    FROM "SCA".UtilisateursComplets uc NATURAL JOIN "CREDENTIALS".credentials d
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

CREATE OR REPLACE PROCEDURE "EMIR".NModifier_utilisateur(
    usernameanc "SCA".username,
    usernamenouv "SCA".username,
    _email "SCA".email,
    _niveau_acces text
)
AS $$
declare
    _idutilisateur "SCA".idutilisateur;
BEGIN
        select idutilisateur into _idutilisateur from "SCA".Utilisateur  where username = usernameanc;

        UPDATE "CREDENTIALS".Credentials
        SET email = _email
        WHERE idutilisateur = _idutilisateur;

        UPDATE "SCA".utilisateur
        SET niveau_acces = _niveau_acces
        WHERE idutilisateur = _idutilisateur;
        -- Si ID utilisateur change, mise à jour des IDs liés
        IF usernameanc <> usernamenouv THEN
            UPDATE "SCA".Utilisateur
            SET username = usernamenouv
            WHERE username = usernameanc;
        END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION "CREDENTIALS".connexion_travailleur(
    _username TEXT,
    _ancien_mot_de_passe TEXT
)
RETURNS TEXT AS $$
DECLARE
    v_poste TEXT;
BEGIN
    SELECT t.poste INTO v_poste
    FROM "SCA".Utilisateur u
    JOIN "CREDENTIALS".Credentials c ON u.idutilisateur = c.idutilisateur
    JOIN "SCA".Travailleur t ON t.idutilisateur = u.idutilisateur
    WHERE u.username = _username
      AND c.mot_de_passe_hash = encode(digest(_ancien_mot_de_passe, 'sha256'), 'hex');

    RETURN v_poste;
END;
$$ LANGUAGE plpgsql;