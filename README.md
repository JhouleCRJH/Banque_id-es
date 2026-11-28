# Banque d'idées (en ligne)

Version en ligne de la banque d'idées : connexion par courriel, partage idée par idée et mise à jour en direct.

- `index.html` : l'application (aucune idée n'est enregistrée dans ce fichier).
- `cloud.js` : connexion, chargement et enregistrement dans Supabase, partage par courriel.
- `outils/build.py` : régénère `index.html` à partir du fichier HTML local (`python3 outils/build.py source.html index.html`). Il retire les données et les chemins du poste.

Les idées sont protégées dans Supabase par des règles d'accès : le propriétaire voit tout, une personne invitée voit seulement les idées partagées avec son courriel.

## Fiche v2 (2026-11-25)
`outils/patch_v2.py` ajoute la nouvelle fiche (sections pliables, photos par section avec annotation, échéancier,
points forts et faiblesses, horodateur, banque d'étiquettes par projet, bandeau photo/couleur/logo, échéance des points).
Après un nouveau `outils/build.py`, relancer `python3 outils/patch_v2.py`. Les données existantes ne changent pas de forme :
les nouveaux champs s'ajoutent seulement.

## Application sur le téléphone (2026-11-26)
L'application s'installe sur l'écran d'accueil (iPhone : Safari › Partager › « Sur l'écran d'accueil » ; Android : Chrome › ⋮ › « Installer l'application ») et s'ouvre en plein écran.
- `manifest.webmanifest` : nom, couleurs, icônes.
- `icones/` : icônes faites par `outils/icones.py` (ampoule marine et verte ; relancer le script pour les refaire).
- `outils/patch_pwa.py` ajoute les balises du téléphone dans `index.html`. **Après un nouveau `outils/build.py` puis `outils/patch_v2.py`, relancer `python outils/patch_pwa.py`**, sinon l'icône disparaît de l'iPhone.
- Pas de « service worker » : la page est toujours lue en ligne, donc jamais de vieille version gardée sur le téléphone.
- Dans l'application installée sur l'iPhone, se connecter avec le **code** reçu par courriel (un clic sur le lien ouvrirait Safari, pas l'application).

## Connexion par mot de passe (2026-11-26, cloud.js v7)
Le filtre Proofpoint de la messagerie bloquait les courriels de connexion. La connexion habituelle se fait maintenant avec **courriel + mot de passe** (rempli par le trousseau iCloud et Face ID sur iPhone et iPad).
- Première connexion ou mot de passe oublié : lien « Recevoir un code » → code par courriel → l'application propose ensuite de créer le mot de passe.
- Changer son mot de passe : bouton 🔑 en bas à droite (section « Mon mot de passe » du panneau).
- Les modèles de courriel Supabase (« Magic link or OTP » et « Confirm sign up ») envoient seulement un code, sans lien.
- Après une modification de `cloud.js`, augmenter le numéro dans `cloud.js?v=` (index.html et outils/build.py) pour que les téléphones prennent la nouvelle version.

## Avancement de la programmation pliable (2026-11-28)
`outils/patch_avancement.py` rend la section « Avancement de la programmation » pliable comme les autres :
un clic sur son en-tête plie ou déplie toute la section, et le sous-titre « Activités » plie ou déplie seulement
le graphique d'activité, les versions et le journal des modifications. « Tout plier » et « Tout déplier » agissent aussi sur les deux.
Ordre après une régénération : `build.py`, `patch_v2.py`, `patch_avancement.py`, puis `patch_pwa.py`.
