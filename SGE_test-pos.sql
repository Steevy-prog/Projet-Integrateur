-- Start a transaction block
BEGIN;

-- Set a savepoint (optional, but good for nested rollbacks if you had more complex logic)
SAVEPOINT initial_data_load;

-- Informative message for starting data load
RAISE NOTICE '--- Starting data insertion demonstration process (no permanent changes will be made) ---';

-- ====================================================================================
-- SCA SCHEMA DATA
-- ====================================================================================
RAISE NOTICE 'Attempting to insert data into "SCA" schema tables...';

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".REF_Marque...';
    INSERT INTO "SCA".REF_Marque (idmarque, nom, pays_origine, date_creation) VALUES
    ('MAR001', 'Samsung', 'Corée du Sud', '2023-01-15 10:00:00'),
    ('MAR002', 'Apple', 'États-Unis', '2023-02-20 11:30:00'),
    ('MAR003', 'Sony', 'Japon', '2023-03-01 14:00:00');
    RAISE NOTICE 'Successfully inserted into "SCA".REF_Marque (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".REF_Marque: %', SQLERRM;
        ROLLBACK TO initial_data_load; -- Rollback to the savepoint
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".REF_Modele...';
    INSERT INTO "SCA".REF_Modele (idmodele, idmarque, nom, type_produit, date_creation) VALUES
    ('MOD001', 'MAR001', 'Galaxy S23', 'Smartphone', '2023-01-20 10:30:00'),
    ('MOD002', 'MAR002', 'iPhone 15', 'Smartphone', '2023-02-25 12:00:00'),
    ('MOD003', 'MAR003', 'Bravia XR', 'TV', '2023-03-05 15:00:00');
    RAISE NOTICE 'Successfully inserted into "SCA".REF_Modele (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".REF_Modele: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".REF_Specialite...';
    INSERT INTO "SCA".REF_Specialite (idspecialite, nom, description, date_creation) VALUES
    ('SPEC001', 'Manipulation Lourde', 'Compétence pour manipuler des charges lourdes.', '2022-05-10 09:00:00'),
    ('SPEC002', 'Conduite Express', 'Maîtrise de la conduite rapide et sécurisée.', '2022-06-15 10:00:00'),
    ('SPEC003', 'Gestion des Stock', 'Optimisation et organisation des inventaires.', '2022-07-20 11:00:00');
    RAISE NOTICE 'Successfully inserted into "SCA".REF_Specialite (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".REF_Specialite: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".REF_Competence...';
    INSERT INTO "SCA".REF_Competence (idcompetence, nom, description, niveau_requis, date_creation) VALUES
    ('COMP001', 'Forklift Operation', 'Opération de chariot élévateur.', 'Certifié', '2022-08-01 08:00:00'),
    ('COMP002', 'Data Entry Speed', 'Vitesse de saisie de données.', 'Intermédiaire', '2022-09-05 09:00:00'),
    ('COMP003', 'Troubleshooting IT', 'Diagnostic et résolution de problèmes IT.', 'Avancé', '2022-10-10 10:00:00');
    RAISE NOTICE 'Successfully inserted into "SCA".REF_Competence (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".REF_Competence: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Organisation...';
    INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type) VALUES
    ('OABCDE', 'GlobalTech Inc.', '678901234', 'fournisseur'),
    ('OFGHIJ', 'LocalRetail Co.', '698765432', 'destinataire'),
    ('OKLMNO', 'SCA Logistics', '654123789', 'SAC');
    RAISE NOTICE 'Successfully inserted into "SCA".Organisation (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Organisation: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Cellule...';
    INSERT INTO "SCA".Cellule (idcellule, longueur, largeur, hauteur, masse_maximale) VALUES
    ('CABCDE', 10.5, 5.2, 3.0, 1000.0),
    ('CFGHIJ', 8.0, 4.0, 2.5, 750.0),
    ('CKLMNO', 12.0, 6.0, 4.0, 1500.0);
    RAISE NOTICE 'Successfully inserted into "SCA".Cellule (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Cellule: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Colis...';
    INSERT INTO "SCA".Colis (idcolis, date_creation, expected_date, receiving_org, statut) VALUES
    ('COABCD', '2024-06-01', '2024-06-10', 'OFGHIJ', 'Attente'),
    ('COEFGH', '2024-06-05', '2024-06-15', 'OFGHIJ', 'Transit'),
    ('COIJKL', '2024-06-08', '2024-06-18', 'OFGHIJ', 'Livre');
    RAISE NOTICE 'Successfully inserted into "SCA".Colis (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Colis: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Zone...';
    INSERT INTO "SCA".Zone (idzone, nom) VALUES
    ('ZABCDE', 'Zone A - Stockage Sec'),
    ('ZFGHIJ', 'Zone B - Réfrigéré'),
    ('ZKLMNO', 'Zone C - Quai de Chargement');
    RAISE NOTICE 'Successfully inserted into "SCA".Zone (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Zone: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".individu...';
    INSERT INTO "SCA".individu (idindividu, nom, prenom, adresse, telephone) VALUES
    ('IABCDE', 'Doe', 'John', '123 Main St', '677112233'),
    ('IFGHIJ', 'Smith', 'Jane', '456 Oak Ave', '699445566'),
    ('IKLMNO', 'Brown', 'Peter', '789 Pine Rd', '655778899');
    RAISE NOTICE 'Successfully inserted into "SCA".individu (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".individu: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Utilisateur...';
    INSERT INTO "SCA".Utilisateur (idutilisateur, idindividu, username, statut, niveau_acces) VALUES
    ('UABCDE', 'IABCDE', 'johndoe', 'actif', 'admin'),
    ('UFGHIJ', 'IFGHIJ', 'janesmith', 'actif', 'manager'),
    ('UKLMNO', 'IKLMNO', 'peterb', 'en attente_validation', 'employe');
    RAISE NOTICE 'Successfully inserted into "SCA".Utilisateur (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Utilisateur: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Conducteur...';
    INSERT INTO "SCA".Conducteur (idconducteur, idutilisateur, numero_permis, type_permis, date_obtention_permis, date_expiration_permis, experience_annees, statut, note_evaluation) VALUES
    ('CDABCD', 'UABCDE', 'ABC12345678', 'B', '2010-01-01', '2025-01-01', 14, 'disponible', 4.50),
    ('CDEFGH', 'UFGHIJ', 'DEF90123456', 'C', '2015-05-10', '2026-05-10', 9, 'en livraison', 4.20);
    RAISE NOTICE 'Successfully inserted into "SCA".Conducteur (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Conducteur: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".ConducteurSpecialite...';
    INSERT INTO "SCA".ConducteurSpecialite (idconducteur, idspecialite, date_obtention, niveau, certifie, date_expiration) VALUES
    ('CDABCD', 'SPEC002', '2023-01-01', 'Avancé', TRUE, '2025-01-01');
    RAISE NOTICE 'Successfully inserted into "SCA".ConducteurSpecialite (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".ConducteurSpecialite: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Bonreception...';
    INSERT INTO "SCA".Bonreception (idbonreception, idcolis, date_creation, idfournisseur, statut, remarques) VALUES
    ('RABCDE', 'COABCD', '2024-06-02', 'OABCDE', 'Accepte', 'Colis reçu en bon état.'),
    ('RFGHIJ', 'COEFGH', '2024-06-06', 'OABCDE', 'en attente', 'Vérification en cours.');
    RAISE NOTICE 'Successfully inserted into "SCA".Bonreception (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Bonreception: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Bonexpedition...';
    INSERT INTO "SCA".Bonexpedition (idbonexpedition, idcolis, idtransporteur, date_creation, iddestinataire, statut, remarques) VALUES
    ('EABCDE', 'COIJKL', 'CDABCD', '2024-06-09', 'OFGHIJ', 'Livre', 'Livré avec succès au destinataire.'),
    ('EFGHIJ', 'COEFGH', 'CDEFGH', '2024-06-12', 'OFGHIJ', 'Transit', 'En route vers la destination.');
    RAISE NOTICE 'Successfully inserted into "SCA".Bonexpedition (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Bonexpedition: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Repertoire...';
    INSERT INTO "SCA".Repertoire (idrepertoire, date_debut, date_fin, idindividu, idorganisation, role) VALUES
    ('REP001', '2023-01-01', '2024-12-31', 'IABCDE', 'OKLMNO', 'Admin'),
    ('REP002', '2023-02-01', NULL, 'IFGHIJ', 'OKLMNO', 'manager');
    RAISE NOTICE 'Successfully inserted into "SCA".Repertoire (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Repertoire: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Produit...';
    INSERT INTO "SCA".Produit (idproduit, idfournisseur, nom, description, prix_unitaire, idmodele, categorie) VALUES
    ('PABCDE', 'OABCDE', 'Smartphone X', 'Dernier modèle de smartphone.', 800.00, 'MOD001', 'produit de vente'),
    ('PFGHIJ', 'OABCDE', 'Carton 50x50', 'Carton d''emballage renforcé.', 2.50, NULL, 'materiel d''emballage'),
    ('PIJKLM', 'OABCDE', 'Logiciel CRM', 'Système de gestion de la relation client.', 1200.00, NULL, 'produit de vente');
    RAISE NOTICE 'Successfully inserted into "SCA".Produit (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Produit: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".ProduitMateriel...';
    INSERT INTO "SCA".ProduitMateriel (idproduit, longueur, largeur, hauteur, masse) VALUES
    ('PABCDE', 0.15, 0.07, 0.01, 0.200),
    ('PFGHIJ', 0.50, 0.50, 0.30, 0.500);
    RAISE NOTICE 'Successfully inserted into "SCA".ProduitMateriel (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".ProduitMateriel: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".ProduitLogiciel...';
    INSERT INTO "SCA".ProduitLogiciel (idproduit, version, license) VALUES
    ('PIJKLM', '3.0', 'Enterprise License');
    RAISE NOTICE 'Successfully inserted into "SCA".ProduitLogiciel (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".ProduitLogiciel: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Lot...';
    INSERT INTO "SCA".Lot (idlot, idproduit, quantite, date_creation) VALUES
    ('LABCDE', 'PABCDE', 100, '2024-05-20'),
    ('LFGHIJ', 'PFGHIJ', 500, '2024-05-25');
    RAISE NOTICE 'Successfully inserted into "SCA".Lot (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Lot: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".LotEmballage...';
    INSERT INTO "SCA".LotEmballage (idproduit, quantite, date_creation, statut, nbuses, condition) VALUES
    ('PFGHIJ', 200, '2024-04-10', 'neuf', 0, 'utilisable'),
    ('PFGHIJ', 50, '2024-03-01', 'recupere', 5, 'a recycler');
    RAISE NOTICE 'Successfully inserted into "SCA".LotEmballage (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".LotEmballage: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".ContenuColis...';
    INSERT INTO "SCA".ContenuColis (idcontenu, idcolis, idlot, date_MAJ) VALUES
    ('CON001', 'COABCD', 'LABCDE', '2024-06-01'),
    ('CON002', 'COEFGH', 'LFGHIJ', '2024-06-05');
    RAISE NOTICE 'Successfully inserted into "SCA".ContenuColis (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".ContenuColis: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".entrepot...';
    INSERT INTO "SCA".entrepot (idcellule, position) VALUES
    ('CABCDE', 'ZABCDE'),
    ('CFGHIJ', 'ZABCDE');
    RAISE NOTICE 'Successfully inserted into "SCA".entrepot (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".entrepot: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".RapportException...';
    INSERT INTO "SCA".RapportException (idrapport, idcolis, type, date_creation, description, statut) VALUES
    ('RABCDE', 'COEFGH', 'lors de la reception du colis', '2024-06-07', 'Colis endommagé à la réception.', 'Ouvert');
    RAISE NOTICE 'Successfully inserted into "SCA".RapportException (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".RapportException: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".InventaireEmplacement...';
    INSERT INTO "SCA".InventaireEmplacement (idinventaire, idcellule, idlot, datemaj) VALUES
    ('INV001', 'CABCDE', 'LABCDE', '2024-06-10'),
    ('INV002', 'CFGHIJ', 'LFGHIJ', '2024-06-12');
    RAISE NOTICE 'Successfully inserted into "SCA".InventaireEmplacement (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".InventaireEmplacement: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Travailleur...';
    INSERT INTO "SCA".Travailleur (idtravailleur, idutilisateur, date_embauche, poste, departement, salaire_horaire, statut, date_derniere_evaluation) VALUES
    ('TRABCD', 'UKLMNO', '2023-03-01', 'Magasinier', 'Logistique', 15.00, 'actif', '2024-03-01');
    RAISE NOTICE 'Successfully inserted into "SCA".Travailleur (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Travailleur: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".TravailleurCompetence...';
    INSERT INTO "SCA".TravailleurCompetence (idtravailleur, idcompetence, niveau_maitrise, date_acquisition, certifie, date_derniere_evaluation) VALUES
    ('TRABCD', 'COMP001', 'Avancé', '2023-04-15', TRUE, '2024-04-15');
    RAISE NOTICE 'Successfully inserted into "SCA".TravailleurCompetence (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".TravailleurCompetence: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Tache...';
    INSERT INTO "SCA".Tache (idtache, idtravailleur, idcellule, idlot, date_creation, date_echeance, duree_estimee, description, priority, statut, type) VALUES
    ('TABCDE', 'TRABCD', 'LABCDE', 'COABCD', '2024-06-11', '2024-06-12', 4, 'Déplacer colis COABCD vers zone de tri.', 'Haute', 'en cours', 'Manutention'),
    ('TEFGHI', 'TRABCD', 'LFGHIJ', 'COEFGH', '2024-06-13', '2024-06-14', 2, 'Vérifier inventaire cellule CFGHIJ.', 'Moyenne', 'en cours', 'Inventaire');
    RAISE NOTICE 'Successfully inserted into "SCA".Tache (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Tache: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Vehicule...';
    INSERT INTO "SCA".Vehicule (idvehicule, immatriculation, idmodele, annee_fabrication, types, capacite_charge, capacite_volume, date_acquisition, statut, kilometrage_actuel) VALUES
    ('VABCDE', 'AB-123-CD', 'MOD003', 2020, 'camion', 5000.0, 30.0, '2021-01-01', 'disponible', 125000.50);
    RAISE NOTICE 'Successfully inserted into "SCA".Vehicule (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Vehicule: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".ConsommationVehicule...';
    INSERT INTO "SCA".ConsommationVehicule (idconsommation, idvehicule, consommation_moyenne, date_mesure, conditions_mesure, kilometrage_debut, kilometrage_fin, litres_consommes, type_trajet) VALUES
    ('CONS001', 'VABCDE', 8.50, '2024-06-01', 'Autoroute sèche', 120000.0, 120500.0, 42.50, 'autoroute');
    RAISE NOTICE 'Successfully inserted into "SCA".ConsommationVehicule (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".ConsommationVehicule: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Logs...';
    INSERT INTO "SCA".Logs (level, message) VALUES
    ('INFO', 'User UABCDE logged in.'),
    ('WARN', 'Low stock for product PFGHIJ.');
    RAISE NOTICE 'Successfully inserted into "SCA".Logs (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Logs: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".LogsExtra...';
    INSERT INTO "SCA".LogsExtra (log_id, cle, valeur) VALUES
    ((SELECT id FROM "SCA".Logs WHERE message = 'User UABCDE logged in.' LIMIT 1), 'user_id', 'UABCDE'),
    ((SELECT id FROM "SCA".Logs WHERE message = 'Low stock for product PFGHIJ.' LIMIT 1), 'product_id', 'PFGHIJ');
    RAISE NOTICE 'Successfully inserted into "SCA".LogsExtra (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".LogsExtra: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".LocalisationOrganisation...';
    INSERT INTO "SCA".LocalisationOrganisation (idorganisation, adresse, ville, region, pays, latitude, longitude) VALUES
    ('OABCDE', '100 Main Street', 'Douala', 'Littoral', 'Cameroun', 4.0511, 9.7679),
    ('OFGHIJ', '200 Market Road', 'Yaounde', 'Centre', 'Cameroun', 3.8480, 11.5021);
    RAISE NOTICE 'Successfully inserted into "SCA".LocalisationOrganisation (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".LocalisationOrganisation: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".LivraisonConducteurColis...';
    INSERT INTO "SCA".LivraisonConducteurColis (idconducteur, idbonexpedition, date_affectation, statut) VALUES
    ('CDABCD', 'EABCDE', '2024-06-09', 'Livre');
    RAISE NOTICE 'Successfully inserted into "SCA".LivraisonConducteurColis (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".LivraisonConducteurColis: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "SCA".Bugreport...';
    INSERT INTO "SCA".Bugreport (idutilisateur, description, statut) VALUES
    ('UABCDE', 'Le bouton de rapport ne fonctionne pas sur la page d''inventaire.', 'open');
    RAISE NOTICE 'Successfully inserted into "SCA".Bugreport (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "SCA".Bugreport: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

-- ====================================================================================
-- CREDENTIALS SCHEMA DATA
-- ====================================================================================
RAISE NOTICE 'Attempting to insert data into CREDENTIALS schema tables...';

BEGIN
    RAISE NOTICE 'Attempting to insert into "CREDENTIALS".application_theme...';
    INSERT INTO "CREDENTIALS".application_theme (theme_name, interface, theme_qss) VALUES
    ('Dark Mode', 'Main App', '/* Dark theme QSS here */'),
    ('Light Mode', 'Main App', '/* Light theme QSS here */');
    RAISE NOTICE 'Successfully inserted into "CREDENTIALS".application_theme (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "CREDENTIALS".application_theme: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "CREDENTIALS".PasswordPolicies...';
    INSERT INTO "CREDENTIALS".PasswordPolicies (setting_name, setting_value, setting_group, description) VALUES
    ('min_length', '8', 'password_complexity', 'Minimum password length'),
    ('require_uppercase', 'true', 'password_complexity', 'Require at least one uppercase letter');
    RAISE NOTICE 'Successfully inserted into "CREDENTIALS".PasswordPolicies (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "CREDENTIALS".PasswordPolicies: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "CREDENTIALS".Credentials...';
    INSERT INTO "CREDENTIALS".Credentials (email, mot_de_passe_hash, idutilisateur) VALUES
    ('john.doe@example.com', 'hashed_password_john_doe_123', 'UABCDE'),
    ('jane.smith@example.com', 'hashed_password_jane_smith_456', 'UFGHIJ');
    RAISE NOTICE 'Successfully inserted into "CREDENTIALS".Credentials (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "CREDENTIALS".Credentials: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "CREDENTIALS".organisation...';
    INSERT INTO "CREDENTIALS".organisation (idorganisation, mdpOrg) VALUES
    ('OABCDE', 'org_password_1'),
    ('OFGHIJ', 'org_password_2');
    RAISE NOTICE 'Successfully inserted into "CREDENTIALS".organisation (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "CREDENTIALS".organisation: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

-- ====================================================================================
-- EXTERNE SCHEMA DATA
-- ====================================================================================
RAISE NOTICE 'Attempting to insert data into EXTERNE schema tables...';

BEGIN
    RAISE NOTICE 'Attempting to insert into "EXTERNE".Colis...';
    INSERT INTO "EXTERNE".Colis (idorg, idpcolis, date_creation, expected_date, receiving_org, statut) VALUES
    ('OABCDE', 'PCOABCDE', '2024-05-28', '2024-06-05', 'OFGHIJ', 'Accepte'),
    ('OABCDE', 'PCOFGHIJ', '2024-06-01', '2024-06-10', 'OFGHIJ', 'en attente');
    RAISE NOTICE 'Successfully inserted into "EXTERNE".Colis (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "EXTERNE".Colis: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "EXTERNE".Lot...';
    INSERT INTO "EXTERNE".Lot (idorg, idplot, idproduit, quantite, date_creation, statut) VALUES
    ('OABCDE', 'PLABCDE', 'PABCDE', 50, '2024-05-25', 'standard'),
    ('OABCDE', 'PLFGHIJ', 'PIJKLM', 5, '2024-05-30', 'neuf');
    RAISE NOTICE 'Successfully inserted into "EXTERNE".Lot (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "EXTERNE".Lot: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "EXTERNE".ContenuColis...';
    INSERT INTO "EXTERNE".ContenuColis (idpcontenu, idorg, idpcolis, idplot, date_MAJ) VALUES
    ('PCON001', 'OABCDE', 'PCOABCDE', 'PLABCDE', '2024-05-29'),
    ('PCON002', 'OABCDE', 'PCOFGHIJ', 'PLFGHIJ', '2024-06-02');
    RAISE NOTICE 'Successfully inserted into "EXTERNE".ContenuColis (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "EXTERNE".ContenuColis: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

BEGIN
    RAISE NOTICE 'Attempting to insert into "EXTERNE".inquiries...';
    INSERT INTO "EXTERNE".inquiries (idutilisateur, idinq, type, period, status, description) VALUES
    ('UABCDE', 'INQABCD', 'missing package', '2024-06-15 10:00:00', 'open', 'Package for order #12345 not received.'),
    ('UFGHIJ', 'INQEFGH', 'billing issue', '2024-06-20 14:30:00', 'resolved', 'Double charge on invoice #9876.');
    RAISE NOTICE 'Successfully inserted into "EXTERNE".inquiries (in transaction).';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error inserting into "EXTERNE".inquiries: %', SQLERRM;
        ROLLBACK TO initial_data_load;
END;

-- Rollback the entire transaction. NO data will be permanently saved.
RAISE NOTICE '--- All data insertion attempts completed. Rolling back transaction. NO data has been saved permanently. ---';
ROLLBACK;