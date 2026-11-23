import re,sys,json
src,dst=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
# 1. vider les données
i=s.find('id="jh-idees-data"'); a=s.find('>',i)+1; b=s.find('</script>',a)
s=s[:a]+s[b:]
# 2. module
tag='<script type="module">'
a=s.find(tag); b=s.find('</script>',a)
mod=s[a+len(tag):b]
def fin_crochet(t,k):
    prof=0;q=None;j=k
    while j<len(t):
        c=t[j]
        if q:
            if c=='\\': j+=2; continue
            if c==q: q=None
        else:
            if c in '"\'`': q=c
            elif c=='[': prof+=1
            elif c==']':
                prof-=1
                if prof==0: return j+1
        j+=1
    raise Exception('crochet')
k=mod.find(',ax=[')+4
e=fin_crochet(mod,k)
mod=mod[:k]+'[]'+mod[e:]
reps=[('R2.current=e19;','R2.current=e19;window.__jhSetDoc=t10;'),
 ('if(!r11)return{doc:t11,origine:','if(window.JHCLOUD)r11=null;if(!r11)return{doc:t11,origine:'),
 ('return await aL(JH_PFX+"doc:"+e20.docId,e20),"indexeddb"','if(window.JHCLOUD)return await window.JHCLOUD.sauver(e20);return await aL(JH_PFX+"doc:"+e20.docId,e20),"indexeddb"')]
for x,y in reps:
    assert mod.count(x)==1,x
    mod=mod.replace(x,y)
mod=re.sub(r'dossierIdeesUrl:"file:///[^"]*"','dossierIdeesUrl:""',mod)
mod=mod.replace('racineNom:"01-JÉRÉMIE HOULE"','racineNom:"Dossier"').replace('OBSI_JAY/Jérémie/','OBSI/')
s=s[:a]+'<script type="text/plain" id="jh-app-module">'+mod+s[b:]
# 3. retirer le script des photos locales (chemin du poste)
s=re.sub(r'<script id="jh7-photos">[\s\S]*?</script>','',s)
# 4. connexion
head='<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.49.4/dist/umd/supabase.min.js"></script><script src="cloud.js"></script>'
s=s.replace('</head>',head+'</head>',1)
s=s.replace('<title>','<title>',1)
open(dst,'w',encoding='utf-8').write(s)
print(len(s))
