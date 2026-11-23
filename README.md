# Banque d'idées (en ligne)

Version en ligne de la banque d'idées : connexion par courriel, partage idée par idée et mise à jour en direct.

- `index.html` : l'application (aucune idée n'est enregistrée dans ce fichier).
- `cloud.js` : connexion, chargement et enregistrement dans Supabase, partage par courriel.
- `outils/build.py` : régénère `index.html` à partir du fichier HTML local (`python3 outils/build.py source.html index.html`). Il retire les données et les chemins du poste.

Les idées sont protégées dans Supabase par des règles d'accès : le propriétaire voit tout, une personne invitée voit seulement les idées partagées avec son courriel.
