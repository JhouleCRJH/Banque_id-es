# Dessine les icônes de l'application (ampoule JH : marine + vert) dans le dossier icones/.
# Lancer : python outils/icones.py   (demande Pillow)
from pathlib import Path
from math import cos, sin, radians
from PIL import Image, ImageDraw

ICI = Path(__file__).resolve().parent.parent
SORTIE = ICI / "icones"
SORTIE.mkdir(exist_ok=True)

MARINE_HAUT = (31, 70, 112)   # dégradé du fond, du haut...
MARINE_BAS = (20, 46, 74)     # ...vers le bas (couleur JH #1a3a5c au centre)
MARINE = (26, 58, 92)         # #1a3a5c
VERT = (82, 164, 49)          # #52a431
VERT_CLAIR = (127, 203, 92)   # #7fcb5c
BLANC = (255, 255, 255)
T = 1024                      # dessin à 1024 px, réduit ensuite (bords lisses)


def fond(taille):
    """Fond carré plein (l'iPhone arrondit les coins lui-même)."""
    im = Image.new("RGB", (taille, taille), MARINE)
    d = ImageDraw.Draw(im)
    for y in range(taille):
        t = y / (taille - 1)
        c = tuple(round(a + (b - a) * t) for a, b in zip(MARINE_HAUT, MARINE_BAS))
        d.line([(0, y), (taille, y)], fill=c)
    return im


def ligne_ronde(d, a, b, largeur, couleur):
    d.line([a, b], fill=couleur, width=largeur)
    r = largeur / 2
    for x, y in (a, b):
        d.ellipse([x - r, y - r, x + r, y + r], fill=couleur)


def ampoule():
    """Ampoule sur fond transparent, 1024 x 1024."""
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy, r = 512, 450, 210
    # rayons de lumière
    for ang in (-170, -130, -90, -50, -10):
        a = radians(ang)
        p1 = (cx + 262 * cos(a), cy + 262 * sin(a))
        p2 = (cx + 330 * cos(a), cy + 330 * sin(a))
        ligne_ronde(d, p1, p2, 36, VERT_CLAIR)
    # globe + col
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLANC)
    d.polygon([(365, 600), (659, 600), (604, 722), (420, 722)], fill=BLANC)
    # filament : deux tiges reliées par une boucle
    ligne_ronde(d, (480, 612), (480, 530), 22, MARINE)
    ligne_ronde(d, (544, 612), (544, 530), 22, MARINE)
    d.arc([469, 498, 555, 562], start=180, end=360, fill=MARINE, width=22)
    # culot vert
    d.rounded_rectangle([414, 737, 610, 779], radius=21, fill=VERT)
    d.rounded_rectangle([424, 792, 600, 834], radius=21, fill=VERT)
    d.rounded_rectangle([462, 846, 562, 880], radius=17, fill=VERT)
    return im


def icone(taille, echelle=1.0):
    """Fond + ampoule ; echelle < 1 laisse une marge (icône « maskable » d'Android)."""
    base = fond(T)
    a = ampoule()
    if echelle != 1.0:
        n = round(T * echelle)
        a = a.resize((n, n), Image.LANCZOS)
        calque = Image.new("RGBA", (T, T), (0, 0, 0, 0))
        calque.paste(a, ((T - n) // 2, (T - n) // 2))
        a = calque
    base.paste(a, (0, 0), a)
    return base.resize((taille, taille), Image.LANCZOS)


icone(180).save(SORTIE / "apple-touch-icon.png", optimize=True)        # iPhone / iPad
icone(192).save(SORTIE / "icone-192.png", optimize=True)
icone(512).save(SORTIE / "icone-512.png", optimize=True)
icone(512, 0.78).save(SORTIE / "icone-maskable-512.png", optimize=True)
icone(32).save(SORTIE / "favicon-32.png", optimize=True)
print("icônes écrites dans", SORTIE)
