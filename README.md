# Projet Vending Machine

Gestion de distributeurs automatiques connectes.

## Deploiement InfinityFree

1. Envoyer le contenu du projet dans le dossier `htdocs` du compte InfinityFree.
2. Garder `index.php` et `.htaccess` a la racine de `htdocs`.
3. Importer `database/vending_machine_db.sql` dans une base MySQL InfinityFree.
4. Creer `config/database.local.php` avec le format de `config/database.local.example.php`, puis renseigner les identifiants MySQL fournis par InfinityFree.
5. Les routes fonctionnent avec `index.php?page=dashboard` et aussi avec les URLs reecrites comme `/dashboard` si `.htaccess` est actif.

Les dossiers applicatifs sensibles (`config`, `controllers`, `models`, `views`, `database`, `python`) sont bloques par `.htaccess`.
