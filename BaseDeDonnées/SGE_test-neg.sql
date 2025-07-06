--script pour les test négatifs
-- TEST 1 : Violation de domaine - email mal formé
BEGIN;
  INSERT INTO "CREDENTIALS".Credentials (email, mot_de_passe_hash, idutilisateur)
  VALUES ('not-an-email', 'hashed_pwd', 'UABCDE');
ROLLBACK;

-- TEST 2 : Clé étrangère inexistante - idutilisateur inconnu
BEGIN;
  INSERT INTO "CREDENTIALS".Credentials (email, mot_de_passe_hash, idutilisateur)
  VALUES ('test@example.com', 'hash', 'UNONEXIST');
ROLLBACK;

-- TEST 3 : Valeur qui ne respecte pas le domaine - idorg mal formé
BEGIN;
  INSERT INTO "SCA".Organisation(idorganisation, nom, telephone, type)
  VALUES ('123456', 'Test Org', '699999999', 'fournisseur');
ROLLBACK;

-- TEST 4 : Enum invalide pour statut utilisateur
BEGIN;
  INSERT INTO "SCA".Utilisateur(idutilisateur, idindividu, username, statut)
  VALUES ('UABCDE', 'IABCDE', 'user_test', 'ghost');
ROLLBACK;

-- TEST 5 : Numéro de téléphone invalide
BEGIN;
  INSERT INTO "SCA".individu(idindividu, nom, prenom, adresse, telephone)
  VALUES ('IABCDE', 'Jean', 'Paul', 'Douala', '12345');
ROLLBACK;

-- TEST 6 : Produit sans fournisseur existant
BEGIN;
  INSERT INTO "SCA".Produit(idproduit, idfournisseur, nom, description, prix_unitaire)
  VALUES ('PABCDE', 'ONONEXIST', 'Produit Test', 'Test', 2000);
ROLLBACK;

-- TEST 7 : Clé primaire dupliquée (id déjà utilisé)
BEGIN;
  -- suppose que 'C001' existe déjà
  INSERT INTO "SCA".Cellule(idcellule, longueur, largeur, hauteur, masse_maximale)
  VALUES ('CABCDE', 1.0, 1.0, 1.0, 1.0);
  INSERT INTO "SCA".Cellule(idcellule, longueur, largeur, hauteur, masse_maximale)
  VALUES ('CABCDE', 2.0, 2.0, 2.0, 2.0);
ROLLBACK;

-- TEST 8 : CHECK sur dims (valeur négative)
BEGIN;
  INSERT INTO "SCA".Cellule(idcellule, longueur, largeur, hauteur, masse_maximale)
  VALUES ('C9999', -1.0, 1.0, 1.0, 100.0);
ROLLBACK;

-- TEST 9 : Valeur non conforme à l’énumération etatcolis
BEGIN;
  INSERT INTO "SCA".Colis(idcolis, date_creation, expected_date, receiving_org, statut)
  VALUES ('COABCD1', CURRENT_DATE, CURRENT_DATE + INTERVAL '3 days', 'OABCDE', 'perdu'); -- "perdu" en minuscules
ROLLBACK;

-- TEST 10 : Mauvais format de username
BEGIN;
  INSERT INTO "SCA".Utilisateur(idutilisateur, idindividu, username)
  VALUES ('U00001', 'IABCDE', '??user!!');
ROLLBACK;