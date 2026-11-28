#!/usr/bin/env python3
"""Rend la section « Avancement de la programmation » pliable (2026-11-28, JH v9).
- Un clic sur l'en-tête plie ou déplie toute la section, comme les autres sections de la fiche.
- Le sous-titre « Activités » plie ou déplie seulement le graphique d'activité, les versions et le journal.
- Les boutons « Tout plier » et « Tout déplier » de la fiche agissent aussi sur les deux.
Ordre après une régénération : build.py, patch_v2.py, patch_avancement.py, puis patch_pwa.py.
Lancer : python3 outils/patch_avancement.py [index.html]"""
import sys, pathlib
ICI = pathlib.Path(__file__).resolve().parent
cible = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ICI.parent / "index.html")
s = cible.read_bytes().decode("utf-8")
i = s.find('id="jh-app-module"'); a = s.find(">", i) + 1; b = s.find("</script>", a)
m = s[a:b]
if "JH v9" in m:
    sys.exit("Déjà appliqué.")
if "JH v8" not in m:
    sys.exit("Lancer d'abord outils/patch_v2.py.")

JS = r'''/* ===== JH v9 : « Avancement de la programmation » pliable (section entière, ou activités seules) 2026-11-28 ===== */
function jh9Pli(k){let lire=()=>{try{return"1"===localStorage.getItem("jhe-idees-pli:"+k)}catch{return false}};let[f,setF]=(0,D.useState)(lire);(0,D.useEffect)(()=>{let g=e=>setF(!!e.detail);window.addEventListener("jh8-plier",g);return()=>window.removeEventListener("jh8-plier",g)},[]);return[f,()=>{let v=!f;setF(v);try{localStorage.setItem("jhe-idees-pli:"+k,v?"1":"0")}catch{}}]}
function jh9Entete(f,bas,tDeplier,tPlier){return{role:"button",tabIndex:0,"aria-expanded":!f,title:f?tDeplier:tPlier,onClick:e=>{if(e.target.closest?.(".jh2-info,a,button,input,select,textarea"))return;bas()},onKeyDown:e=>{("Enter"===e.key||" "===e.key)&&e.target===e.currentTarget&&(e.preventDefault(),bas())}}}
function jh9Chev(){return(0,L.jsx)("span",{className:"jh8-chev","aria-hidden":"true",children:(0,L.jsx)("svg",{viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round",children:(0,L.jsx)("path",{d:"m6 9 6 6 6-6"})})})}
function jh9Pluriel(n,mot){return n+" "+mot+(n>1?"s":"")}
'''

CSS = """.jh9-avancement>.jh8-entete{margin:-4px -6px 8px}
.jh9-avancement.jh8-ferme{padding-top:8px;padding-bottom:8px}
.jh9-avancement.jh8-ferme>.jh8-entete{margin:-4px -6px}
.jh9-avancement .jh9-sous{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem;min-height:36px;margin:12px -6px 0}
.jh9-sous h4{display:inline-flex;align-items:center;gap:.4rem}
.jh9-sous .jh8-chev,.jh9-sous .jh8-chev svg{width:18px;height:18px}
"""

def rep(old, new):
    global m
    c = m.count(old)
    if c != 1:
        sys.exit(f"Motif trouvé {c} fois (attendu 1) : {old[:90]}")
    m = m.replace(old, new)

# 1. aides et état plié (section entière : « avancement », activités : « avancement-activites »)
rep("function xA({idee:e19,doc:t10,onMaj:r10}){let n10=e19.dev,",
    JS + 'function xA({idee:e19,doc:t10,onMaj:r10}){let[jhF,jhBas]=jh9Pli("avancement"),[jhFA,jhBasA]=jh9Pli("avancement-activites"),n10=e19.dev,')
# 2. en-tête cliquable + corps masqué quand la section est pliée
rep('return(0,L.jsxs)("section",{className:"rounded-2xl border border-[#1A3A5C]/15 bg-white/70 p-4 sm:p-5",children:[(0,L.jsxs)("div",{className:"mb-3 flex flex-wrap items-baseline justify-between gap-2",children:[(0,L.jsxs)("h3",{className:"flex items-center gap-2 text-[16px] font-bold",children:[(0,L.jsx)(oM,{className:"h-4 w-4"})," Avancement de la programmation",(0,L.jsx)(JhInfo,{cle:"avancement"})]}),(0,L.jsxs)("span",{className:"font-display text-[22px] font-extrabold",style:{color:i10.couleur},children:[o10," %"]})]}),',
    'return(0,L.jsxs)("section",{className:"jh9-avancement rounded-2xl border border-[#1A3A5C]/15 bg-white/70 p-4 sm:p-5"+(jhF?" jh8-ferme":""),"data-section":"avancement",children:[(0,L.jsxs)("div",{className:"jh8-entete flex flex-wrap items-center justify-between gap-2",...jh9Entete(jhF,jhBas,"Déplier la section","Plier la section"),children:[(0,L.jsxs)("h3",{className:"flex items-center gap-2 text-[16px] font-bold",children:[jh9Chev(),(0,L.jsx)(oM,{className:"h-4 w-4"})," Avancement de la programmation",(0,L.jsx)(JhInfo,{cle:"avancement"})]}),(0,L.jsxs)("span",{className:"font-display text-[22px] font-extrabold",style:{color:i10.couleur},children:[o10," %"]})]}),!jhF&&(0,L.jsxs)(L.Fragment,{children:[')
# 3. sous-titre « Activités » : graphique, versions et journal pliables à part
rep('(0,L.jsx)("div",{className:"mt-3",children:(0,L.jsx)(xE,{valeurs:n10.activite})}),',
    '(0,L.jsxs)("div",{className:"jh9-sous jh8-entete"+(jhFA?" jh8-ferme":""),...jh9Entete(jhFA,jhBasA,"Déplier les activités","Plier les activités"),children:[(0,L.jsxs)("h4",{className:"text-[14px] font-bold text-jh-navy",children:[jh9Chev(),"Activités"]}),(0,L.jsx)("span",{className:"jh2-compte",children:jh9Pluriel(n10.versions.length,"version")+" · "+jh9Pluriel(n10.journal.length,"modification")})]}),!jhFA&&(0,L.jsxs)(L.Fragment,{children:[(0,L.jsx)("div",{className:"mt-2",children:(0,L.jsx)(xE,{valeurs:n10.activite})}),')
# 4. fermer les deux groupes ajoutés
rep('.map(e20=>(0,L.jsx)(xC,{e:e20},e20.id))})]})}',
    '.map(e20=>(0,L.jsx)(xC,{e:e20},e20.id))})]})]})]})}')

s = s[:a] + m + s[b:]
s = s.replace("</head>", '<style id="jh9-style">\n' + CSS + "</style>\n</head>", 1)
cible.write_bytes(s.encode("utf-8"))
print("OK", len(m))
