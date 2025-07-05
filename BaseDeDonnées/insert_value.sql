-- INSERT INTO "SCA".individu (idindividu, nom, prenom, adresse, telephone)
-- VALUES
--     (1, 'Dupont', 'Jean', '123 Rue de la Paix, Paris', '0612345678'),
--     (2, 'Martin', 'Sophie', '456 Avenue des Champs, Lyon', '0798765432'),
--     (3, 'Bernard', 'Pierre', '789 Boulevard Saint-Michel, Marseille', '0655551234'),
--     (4, 'Dubois', 'Marie', '10 Allée des Roses, Nice', '0677778888'),
--     (5, 'Petit', 'Thomas', '25 Rue des Fleurs, Toulouse', '0711223344'),
--     (6, 'Durand', 'Laura', '30 Avenue de la Liberté, Bordeaux', '0699887766'),
--     (7, 'Leroy', 'Nicolas', '5 Impasse du Soleil, Strasbourg', '0765432109'),
--     (8, 'Moreau', 'Camille', '15 Place de la Comédie, Montpellier', '0623456789'),
--     (9, 'Simon', 'Antoine', '22 Rue du Château, Rennes', '0787654321'),
--     (10, 'Laurent', 'Emma', '8 Boulevard des Arts, Lille', '0633445566');


CREATE TABLE "SCA".Utilisateur(
    idutilisateur "SCA".idutilisateur NOT NULL,
    idindividu "SCA".IDindividu NOT NULL,
    username "SCA".username NOT NULL UNIQUE,
    date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_derniere_connexion TIMESTAMP,
    statut "SCA".statut_utilisateur DEFAULT 'en attente_validation',
    niveau_acces "SCA".niveau_acces DEFAULT 'employe',
    CONSTRAINT Utilisateur_CC0 PRIMARY KEY (idutilisateur),
    CONSTRAINT Utilisateur_CR0 FOREIGN KEY (idindividu) REFERENCES "SCA".individu(idindividu) ON DELETE CASCADE
);

-- CREATE TABLE "CREDENTIALS".application_theme(
--                                                 theme_name TEXT,
--                                                 interface TEXT,
--                                                 theme_qss TEXT,
--                                                 CONSTRAINT application_theme_CC0 PRIMARY KEY (theme_name, interface)
-- );


-- CREATE TABLE "SCA".Logs (
--                             id SERIAL PRIMARY KEY,
--                             timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--                             level VARCHAR(10),            -- e.g. 'INFO', 'ERROR', 'DEBUG'
--                             message TEXT,
--                             extra JSONB                   -- pour des infos supplémentaires optionnelles
-- );


INSERT INTO "SCA".Logs (timestamp, level, message, extra)
VALUES
    ('2024-06-25 10:00:00', 'INFO', 'User login successful for user_id: 101', NULL),
    ('2024-06-25 10:05:15', 'ERROR', 'Failed to connect to database', '{"error_code": 500, "module": "auth"}'),
    ('2024-06-25 10:10:30', 'DEBUG', 'Processing data batch 123', '{"batch_id": 123, "records_count": 1500}'),
    ('2024-06-25 10:15:45', 'INFO', 'Report generated successfully: DailySales.pdf', NULL),
    ('2024-06-25 10:20:00', 'WARN', 'Disk space low on server A', '{"server_name": "ServerA", "free_space_gb": 10}'),
    ('2024-06-25 10:25:10', 'ERROR', 'Invalid input received from API endpoint', '{"endpoint": "/api/data", "input_data": "{invalid_json}"}'),
    ('2024-06-25 10:30:20', 'INFO', 'Scheduled task "Cleanup" completed', NULL),
    ('2024-06-25 10:35:30', 'DEBUG', 'Cache hit for key: user_profile_456', '{"cache_key": "user_profile_456"}'),
    ('2024-06-25 10:40:40', 'INFO', 'New user registered: alice.smith@example.com', NULL),
    ('2024-06-25 10:45:50', 'ERROR', 'File not found during import operation', '{"file_path": "/data/import/missing.csv", "operation": "import"}');


# INSERT INTO "CREDENTIALS".PasswordPolicies (setting_name, setting_value, setting_group, description) VALUES
# ('min_length', '8', 'password_policy', 'Minimum number of characters required for a password.'),
# ('require_uppercase', 'True', 'password_policy', 'Boolean: Does password require an uppercase letter?'),
# ('require_lowercase', 'True', 'password_policy', 'Boolean: Does password require a lowercase letter?'),
# ('require_number', 'True', 'password_policy', 'Boolean: Does password require a number?'),
# ('require_special', 'True', 'password_policy', 'Boolean: Does password require a special character?'),
# ('password_expiration_days', '0', 'password_policy', 'Number of days after which password expires (0 for never).'),
# ('enforce_expiration', 'False', 'password_policy', 'Boolean: Is password expiration enforced?');