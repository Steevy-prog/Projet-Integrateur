-- SGE_test-pos.sql
-- Script SQL pour les tests unitaires positifs

-- Désactiver les messages pour des sorties plus propres (optionnel, dépend du client SQL)
-- \set QUIET on

-- Démarrer une transaction pour chaque bloc de test afin de pouvoir faire un ROLLBACK
-- et maintenir l'état de la base de données propre entre les tests.

-- =============================================================================
-- Test 1: Insertion réussie d'une Organisation
-- =============================================================================
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OABCDE', 'TestOrg1', '678901234', 'fournisseur');
SELECT 'Test 1 Passed: Organisation inserted successfully.' AS TestStatus;
-- =============================================================================
-- Test 2: Insertion réussie d'une Cellule
-- =============================================================================
INSERT INTO "SCA".Cellule (idcellule, longueur, largeur, hauteur, masse_maximale)
VALUES ('C00001', 10.0, 5.0, 3.0, 1000.0);
SELECT 'Test 2 Passed: Cellule inserted successfully.' AS TestStatus;

-- =============================================================================
-- Test 3: Insertion réussie d'un Colis
-- =============================================================================

INSERT INTO "SCA".Colis (idcolis, date_creation, statut)
VALUES ('CO00001', '2025-06-20', 'bon etat');
SELECT 'Test 3 Passed: Colis inserted successfully.' AS TestStatus;


-- =============================================================================
-- Test 4: Insertion réussie d'une Zone
-- =============================================================================

INSERT INTO "SCA".Zone (idzone, nom)
VALUES ('ZREC01', 'Zone de Reception 1');
SELECT 'Test 4 Passed: Zone inserted successfully.' AS TestStatus;
-- =============================================================================
-- Test 5: Insertion réussie d'un Individu et d'un Repertoire
-- =============================================================================
INSERT INTO "SCA".individu (idindividu, nom, adresse, telephone)
VALUES ('I00001', 'John Doe', '456 Av. Test', '698765432');

INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OTRANA', 'Transporteur XYZ', '612345678', 'transporteur');

INSERT INTO "SCA".Repertoire (idindividu, idorganisation, role)
VALUES ('I00001', 'OTRANA', 'conducteur');
SELECT 'Test 5 Passed: Individu and Repertoire inserted successfully.' AS TestStatus;

-- =============================================================================
-- Test 6: Insertion réussie d'un Produit Materiel
-- =============================================================================
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OFOURA', 'Fournisseur ABC', '654321098', 'fournisseur');

INSERT INTO "SCA".Produit (idproduit, idfournisseur, nom, description, prix_unitaire, marque, modele, categorie)
VALUES ('P00001', 'OFOURA', 'Boite Carton', 'Grande boite pour emballage', 5.0, 'PackCorp', 'XL-Box', 'materiel d''emballage');

INSERT INTO "SCA".ProduitMateriel (idproduit, longueur, largeur, hauteur, masse)
VALUES ('P00001', 50.0, 40.0, 30.0, 2.0);
SELECT 'Test 6 Passed: Produit Materiel inserted successfully.' AS TestStatus;

-- =============================================================================
-- Test 7: Insertion réussie d'un Lot
-- =============================================================================
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OFOURB', 'Fournisseur DEF', '666555444', 'fournisseur');

INSERT INTO "SCA".Produit (idproduit, idfournisseur, nom, description, prix_unitaire, marque, modele, categorie)
VALUES ('P00002', 'OFOURB', 'SmartPhone X', 'Dernier modele de smartphone', 500.0, 'TechGiant', 'ModelX', 'produit de vente');

INSERT INTO "SCA".Lot (idlot, idproduit, quantite, date_creation, statut, origine, nombre_utilisations, condition)
VALUES ('L00001', 'P00002', 100, '2025-06-15', 'bon etat', 'neuf', 0, 'utilisable');
SELECT 'Test 7 Passed: Lot inserted successfully.' AS TestStatus;


-- =============================================================================
-- Test 8: Insertion réussie d'un Bon de Réception (avec colis et transporteur existants)
-- =============================================================================

INSERT INTO "SCA".Colis (idcolis, date_creation, statut)
VALUES ('CO00002', '2025-06-19', 'bon etat');


INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OTRANB', 'Express Log', '622334455', 'transporteur');
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OFOURC', 'Global Prod', '699887766', 'fournisseur');

INSERT INTO "SCA".Bonreception (idbonreception, idcolis, idtransporteur, date_creation, idfournisseur, statut, remarques)
VALUES ('R00001', 'CO00002', 'OTRANB', '2025-06-20', 'OFOURC', 'bon etat', 'Aucune');
SELECT 'Test 8 Passed: Bonreception inserted successfully.' AS TestStatus;

-- =============================================================================
-- Test 9: Insertion réussie de ContenuColis (réception)
--         Cela devrait passer le trigger `trg_check_reception_consistency`
--         (même si la vérification est limitée sans une table de détails de bon de réception).
-- =============================================================================

INSERT INTO "SCA".Colis (idcolis, date_creation, statut)
VALUES ('CO00003', '2025-06-20', 'bon etat');

INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OTRANC', 'Speedy Cargo', '611223344', 'transporteur');
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type)
VALUES ('OFOURD', 'Tech Supplies', '633445566', 'fournisseur');

INSERT INTO "SCA".Bonreception (idbonreception, idcolis, idtransporteur, date_creation, idfournisseur, statut, remarques)
VALUES ('R00002', 'CO00003', 'OTRANC', '2025-06-20', 'OFOURD', 'bon etat', 'Marchandise conforme');

INSERT INTO "SCA".Produit (idproduit, idfournisseur, nom, description, prix_unitaire, marque, modele, categorie)
VALUES ('P00003', 'OFOURD', 'Souris sans fil', 'Souris optique', 15.0, 'Logi', 'M185', 'produit de vente');

INSERT INTO "SCA".Lot (idlot, idproduit, quantite, date_creation, statut, origine, nombre_utilisations, condition)
VALUES ('L00002', 'P00003', 50, '2025-06-20', 'bon etat', 'neuf', 0, 'utilisable');

INSERT INTO "SCA".ContenuColis (idcolis, idlot, quantite, date_MAJ)
VALUES ('CO00003', 'L00002', 20, '2025-06-21');
SELECT 'Test 9 Passed: ContenuColis (reception) inserted successfully.' AS TestStatus;

-- =============================================================================
-- Test 10: Insertion réussie de ContenuColis (expédition) avec stock suffisant
--          Cela devrait passer le trigger `trg_check_expedition_availability`.
-- =============================================================================
-- Préparer les données nécessaires: Produit, Lot, Cellule, InventaireEmplacement, Colis
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type) VALUES ('OFOURE', 'ElectroInc', '677889900', 'fournisseur');
INSERT INTO "SCA".Produit (idproduit, idfournisseur, nom, description, prix_unitaire, marque, modele, categorie) VALUES ('P00004', 'OFOURE', 'Clavier RGB', 'Clavier mecanique gaming', 80.0, 'GamersBrand', 'K100', 'produit de vente');
INSERT INTO "SCA".Lot (idlot, idproduit, quantite, date_creation, statut, origine, nombre_utilisations, condition) VALUES ('L00003', 'P00004', 100, '2025-06-18', 'bon etat', 'neuf', 0, 'utilisable');
INSERT INTO "SCA".Cellule (idcellule, longueur, largeur, hauteur, masse_maximale) VALUES ('C00002', 5.0, 5.0, 5.0, 500.0);
INSERT INTO "SCA".InventaireEmplacement (idcellule, idlot, quantite, datemaj) VALUES ('C00002', 'L00003', 50, '2025-06-20'); -- Stock de 50 claviers

INSERT INTO "SCA".Colis (idcolis, date_creation, statut) VALUES ('COEXP01', '2025-06-21', 'bon etat');

-- Simuler l'ajout au colis d'expédition
INSERT INTO "SCA".ContenuColis (idcolis, idlot, quantite, date_MAJ)
VALUES ('COEXP01', 'L00003', 10, '2025-06-21'); -- Demande 10, stock 50, devrait passer
SELECT 'Test 10 Passed: ContenuColis (expedition) inserted successfully with sufficient stock.' AS TestStatus;

-- =============================================================================
-- Test 11: Insertion réussie d'un Bon d'Expédition (date après réception)
--          Cela devrait passer le trigger `trg_check_expedition_date`.
-- =============================================================================
-- Créer un colis et son bon de réception
INSERT INTO "SCA".Colis (idcolis, date_creation, statut) VALUES ('COEXP02', '2025-06-10', 'bon etat');
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone,  type) VALUES ('OTRAND', 'Fast Courier', '655443322', 'transporteur');
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone,  type) VALUES ('OFOURF', 'Supplier A', '610203040', 'fournisseur');
INSERT INTO "SCA".Bonreception (idbonreception, idcolis, idtransporteur, date_creation, idfournisseur, statut, remarques)
VALUES ('R00003', 'COEXP02', 'OTRAND', '2025-06-12', 'OFOURF', 'bon etat', 'OK');

-- Créer une organisation destinataire
INSERT INTO "SCA".Organisation (idorganisation, nom, telephone, type) VALUES ('ODESTA', 'Client Alpha', '601020304', 'destinataire');

-- Insérer le bon d'expédition avec une date postérieure à la réception
INSERT INTO "SCA".Bonexpedition (idbonexpedition, idcolis, idtransporteur, date_creation, iddestinataire, statut, remarques)
VALUES ('E00001', 'COEXP02', 'OTRAND', '2025-06-15', 'ODESTA', 'bon etat', 'Pret pour envoi');
SELECT 'Test 11 Passed: Bonexpedition inserted successfully with valid date.' AS TestStatus;

-- Réactiver les messages (optionnel)
-- \set QUIET off
-- =============================================================================
-- Tests pour la fonctionnalité de livraison
-- =============================================================================

-- Test 12: Confirmation de livraison d'un colis
-- Prérequis: Utiliser un colis existant avec bon d'expédition
-- Exemple d'utilisation:
-- CALL "EMIR".ConfirmerLivraison_INS('COEXP02', '2025-06-16');
-- SELECT 'Test 12 Passed: Livraison confirmée avec succès.' AS TestStatus;

-- =============================================================================
-- Exemples d'utilisation des nouvelles fonctionnalités
-- =============================================================================

-- Exemple 1: Confirmer la livraison d'un colis (date actuelle)
-- CALL "EMIR".ConfirmerLivraison_INS('COEXP02');

-- Exemple 2: Confirmer la livraison d'un colis avec une date spécifique
-- CALL "EMIR".ConfirmerLivraison_INS('COEXP02', '2025-06-16');

-- Exemple 3: Voir tous les colis livrés
-- SELECT * FROM "EMIR".colis_livres();

-- Exemple 4: Voir les colis livrés entre deux dates
-- SELECT * FROM "EMIR".colis_livres('2025-06-01', '2025-06-30');

-- Exemple 5: Voir les statistiques de livraison
-- SELECT * FROM "EMIR".statistiques_livraison();

-- Exemple 6: Voir les statistiques de livraison pour un mois
-- SELECT * FROM "EMIR".statistiques_livraison('2025-06-01', '2025-06-30');

-- Exemple 7: Voir l'inventaire (excluant les colis livrés)
-- SELECT * FROM "SCA".inventaire;

-- Exemple 8: Voir les colis en cours d'expédition
-- SELECT * FROM "SCA".ColisEnExpedition;
