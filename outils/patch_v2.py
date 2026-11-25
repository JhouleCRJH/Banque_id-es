#!/usr/bin/env python3
"""Applique la fiche v2 (2026-11-25) au module de l'app dans index.html.
Ajoute : sections pliables, photos par section (annotation), échéancier, points forts/faiblesses,
horodateur, banque d'étiquettes par projet, bandeau (photo, couleur, logo), échéance des points.
Les fonctions existantes (Points à corriger, Notes, Liens) restent identiques."""
import sys, pathlib
ICI = pathlib.Path(__file__).resolve().parent
cible = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ICI.parent / "index.html")
s = cible.read_text(encoding="utf-8")
i = s.find('id="jh-app-module"'); a = s.find(">", i) + 1; b = s.find("</script>", a)
m = s[a:b]
if "JH v8" in m:
    sys.exit("Déjà appliqué.")
jh8 = (ICI / "v2" / "jh8.js").read_text(encoding="utf-8")
css = (ICI / "v2" / "jh8.css").read_text(encoding="utf-8")

def rep(old, new, n=1):
    global m
    c = m.count(old)
    if c != n:
        sys.exit(f"Motif trouvé {c} fois (attendu {n}) : {old[:90]}")
    m = m.replace(old, new)

# 1. anciennes versions gardées sous un autre nom (non utilisées)
rep("function x_({", "function x_Ancien({")
rep("function JhChoixEtiquettes({", "function JhChoixEtiquettesAncien({")
rep("function kn({", "function knAncien({")
# 2. nouveaux composants
rep("function kt({", jh8 + "\nfunction kn(p){return(0,L.jsx)(JhSection,p)}\nfunction kt({")
# 3. kt : doc courant pour le bandeau et le bilan général
rep("g10=e19.genre??\"logiciel\",v10=av[g10];",
    "g10=e19.genre??\"logiciel\",v10=av[g10];window.__jh8Doc=a10;window.__jh8Idees={...Object.fromEntries((a10?.idees??[]).map(i=>[i.id,i])),[e19.id]:e19};")
# 4. photos collées (Ctrl+V) : section active
rep('n11.push({id:ak(),src:e21,legende:"",ajouteLe:', 'n11.push({id:ak(),src:e21,legende:"",section:jh8SectionCourante(),ajouteLe:')
# 5. bandeau cliquable dans la fiche
rep('(0,L.jsx)(x_,{idee:e19,hauteur:"h-40 sm:h-48",grand:true})', '(0,L.jsx)(x_,{idee:e19,hauteur:"h-40 sm:h-48",grand:true,onMaj:t10})')
# 6. zones photo dans les 4 sections
for k, t in [("probleme", "probleme"), ("donneesPlan", "donneesPlan"), ("listes", "listes"), ("interface", "interfaceUi")]:
    rep("(0,L.jsx)(kn,{titre:v10.%s.t," % t, '(0,L.jsx)(kn,{jhPh:"%s",jhIdee:e19,jhMaj:t10,titre:v10.%s.t,' % (k, t))
# 7. « Photos et croquis » remplacée par Points forts et faiblesses
a2 = m.find('(0,L.jsx)(kn,{titre:"Photos et croquis"'); b2 = m.find('(0,L.jsx)(kn,{titre:"Points à corriger"', a2)
assert 0 < a2 < b2 and b2 - a2 < 4000, (a2, b2)
m = m[:a2] + '(0,L.jsx)(kn,{titre:"Points forts et faiblesses",info:"forces",compte:jh8CompteForces(e19),children:(0,L.jsx)(JhForces,{idee:e19,onMaj:t10})}),' + m[b2:]
# 8. Horodateur avant les notes
rep('(0,L.jsx)(kn,{titre:"Notes",', '(0,L.jsx)(kn,{titre:"Versions et journal des modifications",info:"suivi",compte:jh8CompteSuivi(e19),children:(0,L.jsx)(JhSuivi,{idee:e19,onMaj:t10})}),(0,L.jsx)(kn,{titre:"Horodateur et bilan du temps",info:"horodateur",compte:jh8CompteHoro(e19),children:(0,L.jsx)(JhHorodateur,{idee:e19,onMaj:t10,doc:a10})}),(0,L.jsx)(kn,{titre:"Notes",')
# 9. outils de la fiche + échéancier
rep("e19.dev&&(0,L.jsx)(xA,", '(0,L.jsx)(JhOutilsFiche,{idee:e19,doc:a10}),(0,L.jsx)(kn,{titre:"Échéancier",info:"echeancier",compte:jh8CompteEch(e19),children:(0,L.jsx)(JhEcheancier,{idee:e19,onMaj:t10})}),e19.dev&&(0,L.jsx)(xA,')
# 10. Points à corriger : seulement la banque d'étiquettes du projet et l'échéance
rep("(0,L.jsx)(JhCorrections,{items:e19.corrections,", "(0,L.jsx)(JhCorrections,{onMajIdee:t10,items:e19.corrections,")
rep("function JhCorrections({items:e19,onChange:t10,", "function JhCorrections({onMajIdee:OMI,items:e19,onChange:t10,")
rep("[etiqAttente,setEtiqAttente]=(0,D.useState)([]),", "[etiqAttente,setEtiqAttente]=(0,D.useState)([]),[echN,setEchN]=(0,D.useState)(\"\"),")
p0 = m.find("perso=(()=>{let m10=new Set;for(let x10 of DOC?.idees??[I2??{}])")
p1 = m.find("})(),u10=()=>{let e20=jhSeparer(n10);", p0)
assert 0 < p0 < p1 and p1 - p0 < 600
m = m[:p0] + "perso=[...new Set([...jhBanque(I2),...etiqAttente])]" + m[p1 + 4:]
rep("...etiqAttente.length?{etiquettes:[...etiqAttente]}:{},...0===n11&&P2.length?{photos:P2}:{}}));t10(e21=>[...e21,...o11]),i10(\"\"),Q2([])}",
    "...etiqAttente.length?{etiquettes:[...etiqAttente]}:{},...echN?{ech:echN}:{},...0===n11&&P2.length?{photos:P2}:{}}));t10(e21=>[...e21,...o11]),i10(\"\"),Q2([]),setEchN(\"\")}")
rep("basculerEtiq=(id2,nom)=>{if(\"nouveau\"===id2)",
    "basculerEtiq=(id2,nom)=>{OMI&&!jhBanque(I2).includes(nom)&&OMI(i=>({etiquettesBanque:[...new Set([...jhBanque(i),nom])]}));if(\"nouveau\"===id2)")
rep("(0,L.jsx)(JhChoixEtiquettes,{choisies:liste,perso,onBasculer:g10=>basculerEtiq(id2,g10),",
    "(0,L.jsx)(JhChoixEtiquettes,{choisies:liste,perso,onRetirerBanque:OMI?g10=>OMI(i=>({etiquettesBanque:jhBanque(i).filter(x=>x!==g10)})):void 0,onBasculer:g10=>basculerEtiq(id2,g10),")
rep('photo${e20.photos.length>1?"s":""}`:"")})]}),(0,L.jsx)("button",{type:"button",className:"jh2-photo-btn jh2-copier-un"',
    'photo${e20.photos.length>1?"s":""}`:"")}),(0,L.jsx)(JhEcheance,{valeur:e20.ech,fait:e20.fait,onChange:v=>c10(e20.id,{ech:v||void 0})})]}),(0,L.jsx)("button",{type:"button",className:"jh2-photo-btn jh2-copier-un"')
rep('rangeeEtiq("nouveau",etiqAttente)]}),G2(null),',
    'rangeeEtiq("nouveau",etiqAttente),(0,L.jsx)("div",{className:"jh8-ajout-ech",children:(0,L.jsx)(JhEcheance,{valeur:echN,onChange:setEchN,libelle:"Échéance du prochain point"})})]}),G2(null),')

s = s[:a] + m + s[b:]
s = s.replace("</head>", '<style id="jh8-style">\n' + css + "</style>\n</head>", 1)
cible.write_text(s, encoding="utf-8")
print("OK", len(m))
