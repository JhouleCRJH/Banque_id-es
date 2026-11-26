# Ajoute à index.html ce qu'il faut pour installer l'application sur un téléphone
# (icône sur l'écran d'accueil, ouverture plein écran). Sans danger à relancer : le bloc
# <!--jh-pwa--> ... <!--/jh-pwa--> est remplacé, jamais doublé.
# Ordre après une régénération : build.py, patch_v2.py, puis patch_pwa.py.
# Lancer : python outils/patch_pwa.py [index.html]
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
cible = Path(sys.argv[1]) if len(sys.argv) > 1 else ICI / "index.html"

BLOC = """<!--jh-pwa-->
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icones/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="icones/favicon-32.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Idées">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="theme-color" content="#1a3a5c">
<!--/jh-pwa-->"""

# lecture / écriture en octets : les fins de ligne du fichier restent telles quelles
s = cible.read_bytes().decode("utf-8")
s = re.sub(r"<!--jh-pwa-->[\s\S]*?<!--/jh-pwa-->\r?\n?", "", s)
assert s.count("</head>") >= 1, "pas de </head> dans " + str(cible)
s = s.replace("</head>", BLOC + "\n</head>", 1)
cible.write_bytes(s.encode("utf-8"))
print("bloc téléphone ajouté à", cible)
