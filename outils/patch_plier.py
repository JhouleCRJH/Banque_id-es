#!/usr/bin/env python3
"""Rend pliables les sections de la fiche qui ne l'étaient pas encore.
JH v9 (2026-11-28) : « Avancement de la programmation »
- Un clic sur l'en-tête plie ou déplie toute la section, comme les autres sections de la fiche.
- Le sous-titre « Activités » plie ou déplie seulement le graphique d'activité, les versions et le journal.
JH v10 (2026-11-28) : « Impact et effort » et « Cadrage de l'idée »
- Un clic sur l'en-tête plie ou déplie la section. Pliée, « Impact et effort » garde un résumé
  (pastille de priorité, Impact x/5 · Effort y/5) et « Cadrage de l'idée » garde son pourcentage.
JH v11 (2026-11-28) : en thème sombre, le pourcentage d'avancement (fiche et Atelier) prend une couleur claire;
  sur téléphone, les boutons d'étape de l'avancement passent sur 2 rangées.
Les boutons « Tout plier » et « Tout déplier » de la fiche agissent sur toutes ces sections.
Chaque étape déjà présente dans le fichier est sautée : sans danger à relancer.
Ordre après une régénération : build.py, patch_v2.py, patch_plier.py, puis patch_pwa.py.
Lancer : python3 outils/patch_plier.py [index.html]"""
import sys, pathlib
ICI = pathlib.Path(__file__).resolve().parent
cible = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ICI.parent / "index.html")
s = cible.read_bytes().decode("utf-8")
i = s.find('id="jh-app-module"'); a = s.find(">", i) + 1; b = s.find("</script>", a)
m = s[a:b]
if "JH v8" not in m:
    sys.exit("Lancer d'abord outils/patch_v2.py.")
styles = ""
fait = []

def rep(old, new):
    global m
    c = m.count(old)
    if c != 1:
        sys.exit(f"Motif trouvé {c} fois (attendu 1) : {old[:90]}")
    m = m.replace(old, new)

# ---------- JH v9 : Avancement de la programmation ----------
JS9 = r'''/* ===== JH v9 : « Avancement de la programmation » pliable (section entière, ou activités seules) 2026-11-28 ===== */
function jh9Pli(k){let lire=()=>{try{return"1"===localStorage.getItem("jhe-idees-pli:"+k)}catch{return false}};let[f,setF]=(0,D.useState)(lire);(0,D.useEffect)(()=>{let g=e=>setF(!!e.detail);window.addEventListener("jh8-plier",g);return()=>window.removeEventListener("jh8-plier",g)},[]);return[f,()=>{let v=!f;setF(v);try{localStorage.setItem("jhe-idees-pli:"+k,v?"1":"0")}catch{}}]}
function jh9Entete(f,bas,tDeplier,tPlier){return{role:"button",tabIndex:0,"aria-expanded":!f,title:f?tDeplier:tPlier,onClick:e=>{if(e.target.closest?.(".jh2-info,a,button,input,select,textarea"))return;bas()},onKeyDown:e=>{("Enter"===e.key||" "===e.key)&&e.target===e.currentTarget&&(e.preventDefault(),bas())}}}
function jh9Chev(){return(0,L.jsx)("span",{className:"jh8-chev","aria-hidden":"true",children:(0,L.jsx)("svg",{viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round",children:(0,L.jsx)("path",{d:"m6 9 6 6 6-6"})})})}
function jh9Pluriel(n,mot){return n+" "+mot+(n>1?"s":"")}
'''

CSS9 = """.jh9-avancement>.jh8-entete{margin:-4px -6px 8px}
.jh9-avancement.jh8-ferme{padding-top:8px;padding-bottom:8px}
.jh9-avancement.jh8-ferme>.jh8-entete{margin:-4px -6px}
.jh9-avancement .jh9-sous{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem;min-height:36px;margin:12px -6px 0}
.jh9-sous h4{display:inline-flex;align-items:center;gap:.4rem}
.jh9-sous .jh8-chev,.jh9-sous .jh8-chev svg{width:18px;height:18px}
"""

if "JH v9" not in m:
    # 1. aides et état plié (section entière : « avancement », activités : « avancement-activites »)
    rep("function xA({idee:e19,doc:t10,onMaj:r10}){let n10=e19.dev,",
        JS9 + 'function xA({idee:e19,doc:t10,onMaj:r10}){let[jhF,jhBas]=jh9Pli("avancement"),[jhFA,jhBasA]=jh9Pli("avancement-activites"),n10=e19.dev,')
    # 2. en-tête cliquable + corps masqué quand la section est pliée
    rep('return(0,L.jsxs)("section",{className:"rounded-2xl border border-[#1A3A5C]/15 bg-white/70 p-4 sm:p-5",children:[(0,L.jsxs)("div",{className:"mb-3 flex flex-wrap items-baseline justify-between gap-2",children:[(0,L.jsxs)("h3",{className:"flex items-center gap-2 text-[16px] font-bold",children:[(0,L.jsx)(oM,{className:"h-4 w-4"})," Avancement de la programmation",(0,L.jsx)(JhInfo,{cle:"avancement"})]}),(0,L.jsxs)("span",{className:"font-display text-[22px] font-extrabold",style:{color:i10.couleur},children:[o10," %"]})]}),',
        'return(0,L.jsxs)("section",{className:"jh9-avancement rounded-2xl border border-[#1A3A5C]/15 bg-white/70 p-4 sm:p-5"+(jhF?" jh8-ferme":""),"data-section":"avancement",children:[(0,L.jsxs)("div",{className:"jh8-entete flex flex-wrap items-center justify-between gap-2",...jh9Entete(jhF,jhBas,"Déplier la section","Plier la section"),children:[(0,L.jsxs)("h3",{className:"flex items-center gap-2 text-[16px] font-bold",children:[jh9Chev(),(0,L.jsx)(oM,{className:"h-4 w-4"})," Avancement de la programmation",(0,L.jsx)(JhInfo,{cle:"avancement"})]}),(0,L.jsxs)("span",{className:"font-display text-[22px] font-extrabold",style:{color:i10.couleur},children:[o10," %"]})]}),!jhF&&(0,L.jsxs)(L.Fragment,{children:[')
    # 3. sous-titre « Activités » : graphique, versions et journal pliables à part
    rep('(0,L.jsx)("div",{className:"mt-3",children:(0,L.jsx)(xE,{valeurs:n10.activite})}),',
        '(0,L.jsxs)("div",{className:"jh9-sous jh8-entete"+(jhFA?" jh8-ferme":""),...jh9Entete(jhFA,jhBasA,"Déplier les activités","Plier les activités"),children:[(0,L.jsxs)("h4",{className:"text-[14px] font-bold text-jh-navy",children:[jh9Chev(),"Activités"]}),(0,L.jsx)("span",{className:"jh2-compte",children:jh9Pluriel(n10.versions.length,"version")+" · "+jh9Pluriel(n10.journal.length,"modification")})]}),!jhFA&&(0,L.jsxs)(L.Fragment,{children:[(0,L.jsx)("div",{className:"mt-2",children:(0,L.jsx)(xE,{valeurs:n10.activite})}),')
    # 4. fermer les deux groupes ajoutés
    rep('.map(e20=>(0,L.jsx)(xC,{e:e20},e20.id))})]})}',
        '.map(e20=>(0,L.jsx)(xC,{e:e20},e20.id))})]})]})]})}')
    styles += '<style id="jh9-style">\n' + CSS9 + "</style>\n"
    fait.append("v9 Avancement de la programmation")

# ---------- JH v10 : Impact et effort, Cadrage de l'idée ----------
JS10 = r'''/* ===== JH v10 : sections « Impact et effort » et « Cadrage de l'idée » pliables 2026-11-28 ===== */
function JhBlocPli({cle,classe,titre,droite,resume,children:c}){let[f,bas]=jh9Pli(cle);return(0,L.jsxs)("section",{className:classe+" jh10-bloc"+(f?" jh8-ferme":""),"data-section":cle,children:[(0,L.jsxs)("div",{className:"jh8-entete flex flex-wrap items-center justify-between gap-2",...jh9Entete(f,bas,"Déplier la section","Plier la section"),children:[(0,L.jsxs)("h3",{className:"jh2-titre-ligne text-[16px] font-bold",children:[jh9Chev(),...titre]}),(0,L.jsxs)("span",{className:"jh10-droite",children:[f?resume??null:null,droite??null]})]}),f?null:Array.isArray(c)?(0,L.jsxs)(L.Fragment,{children:c}):c]})}
'''

CSS10 = """.jh10-bloc>.jh8-entete{margin:-4px -6px 8px}
.jh10-bloc.jh8-ferme{padding-top:8px;padding-bottom:8px}
.jh10-bloc.jh8-ferme>.jh8-entete{margin:-4px -6px}
.jh10-droite,.jh10-resume{display:inline-flex;align-items:center;gap:8px;flex-wrap:wrap}
"""

if "JH v10" not in m:
    if "JH v9" not in m:
        sys.exit("L'étape v9 manque.")
    # 1. composant de section pliable, à côté de la fiche
    rep("function kt({", JS10 + "function kt({")
    # 2. Impact et effort : titre ajouté, résumé visible quand la section est pliée
    rep('(0,L.jsxs)("div",{className:"rounded-2xl border border-white bg-white/60 p-4",children:[(0,L.jsxs)("div",{className:"grid gap-4 sm:grid-cols-2",children:[(0,L.jsx)(xL,{libelle:"Impact",',
        '(0,L.jsxs)(JhBlocPli,{cle:"impact-effort",classe:"rounded-2xl border border-white bg-white/60 p-4",titre:["Impact et effort"],resume:(0,L.jsxs)("span",{className:"jh10-resume",children:[(0,L.jsx)("span",{className:"puce",style:{background:p10.couleur+"1A",color:p10.couleur},children:p10.nom}),(0,L.jsx)("span",{className:"text-[13px] text-slate-600",children:"Impact "+e19.impact+"/5 · Effort "+e19.effort+"/5"})]}),children:[(0,L.jsxs)("div",{className:"grid gap-4 sm:grid-cols-2",children:[(0,L.jsx)(xL,{libelle:"Impact",')
    # 3. Cadrage de l'idée : l'en-tête existant devient cliquable, le pourcentage reste visible
    rep('(0,L.jsxs)("section",{className:"rounded-2xl border border-[#52A431]/25 bg-gradient-to-br from-white/85 to-[#52A431]/[0.06] p-4 sm:p-5",children:[(0,L.jsxs)("div",{className:"mb-1 flex items-baseline justify-between gap-3",children:[(0,L.jsxs)("h3",{className:"jh2-titre-ligne text-[16px] font-bold",children:["Cadrage de l\'idée",(0,L.jsx)(JhInfo,{cle:"cadrage"})]}),(0,L.jsxs)("span",{className:"font-mono text-[20px] font-medium text-jh-vertfonce",children:[m10," %"]})]}),',
        '(0,L.jsxs)(JhBlocPli,{cle:"cadrage",classe:"rounded-2xl border border-[#52A431]/25 bg-gradient-to-br from-white/85 to-[#52A431]/[0.06] p-4 sm:p-5",titre:["Cadrage de l\'idée",(0,L.jsx)(JhInfo,{cle:"cadrage"})],droite:(0,L.jsxs)("span",{className:"font-mono text-[20px] font-medium text-jh-vertfonce",children:[m10," %"]}),children:[')
    styles += '<style id="jh10-style">\n' + CSS10 + "</style>\n"
    fait.append("v10 Impact et effort, Cadrage de l'idée")

# ---------- JH v11 : pourcentage d'avancement lisible en thème sombre ----------
# La couleur de l'étape (bleu marine pour « En développement ») disparaissait sur le fond foncé.
CSS11 = """/* JH v11 : pourcentage d'avancement lisible en thème sombre */
html[data-jh-theme=sombre] .jh11-pct[data-etape=prototype]{color:#8cbbe6!important}
html[data-jh-theme=sombre] .jh11-pct[data-etape=developpement]{color:#a9cdf0!important}
html[data-jh-theme=sombre] .jh11-pct[data-etape=essais]{color:#f2b84b!important}
html[data-jh-theme=sombre] .jh11-pct[data-etape=en-service]{color:#7fd35a!important}
/* sur téléphone, les 4 boutons d'étape passent sur 2 rangées : « En développement » ne déborde plus */
@media (max-width:520px){.jh9-avancement [role=group][aria-label="Étape"]{display:grid;grid-template-columns:1fr 1fr}}
"""

if 'id="jh11-style"' not in s:
    # fiche de l'idée
    rep('(0,L.jsxs)("span",{className:"font-display text-[22px] font-extrabold",style:{color:i10.couleur},children:[o10," %"]})',
        '(0,L.jsxs)("span",{className:"jh11-pct font-display text-[22px] font-extrabold","data-etape":i10.k,style:{color:i10.couleur},children:[o10," %"]})')
    # cartes de l'Atelier
    rep('(0,L.jsxs)("span",{className:"font-display text-[22px] font-extrabold leading-none",style:{color:i11.couleur},children:[o11," %"]})',
        '(0,L.jsxs)("span",{className:"jh11-pct font-display text-[22px] font-extrabold leading-none","data-etape":i11.k,style:{color:i11.couleur},children:[o11," %"]})')
    styles += '<style id="jh11-style">\n' + CSS11 + "</style>\n"
    fait.append("v11 pourcentage lisible en thème sombre, étapes sur 2 rangées au téléphone")

if not fait:
    sys.exit("Déjà appliqué.")
s = s[:a] + m + s[b:]
s = s.replace("</head>", styles + "</head>", 1)
cible.write_bytes(s.encode("utf-8"))
print("OK :", ", ".join(fait))
