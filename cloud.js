/* Banque d'idées en ligne : connexion, chargement depuis Supabase, enregistrement,
   mise à jour en direct et partage idée par idée par courriel. */
(function () {
  "use strict";
  var SUPABASE_URL = "https://rlnrngjyvycnprpkjixy.supabase.co";
  var SUPABASE_CLE = "sb_publishable_BPO9ysMQSHjdunX_NCkI3g_j9vuRICN";
  var APP_URL = location.origin + location.pathname;

  var sb = null, moi = null, monCourriel = "";
  var dernier = {};      // id -> JSON des données tel que connu du serveur
  var proprio = {};      // id -> uuid du propriétaire
  var monRole = {};      // id -> 'proprietaire' | 'editeur' | 'lecteur'
  var file = Promise.resolve();
  var etatEl = null;

  /* ---------- petites aides ---------- */
  function el(tag, attrs, enfants) {
    var e = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === "texte") e.textContent = attrs[k];
      else if (k === "style") e.style.cssText = attrs[k];
      else if (k.slice(0, 2) === "on") e.addEventListener(k.slice(2), attrs[k]);
      else e.setAttribute(k, attrs[k]);
    }
    (enfants || []).forEach(function (c) { if (c) e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
  }
  function etat(txt, erreur) {
    if (!etatEl) return;
    etatEl.textContent = txt;
    etatEl.style.background = erreur ? "#d93848" : "#1a3a5c";
    clearTimeout(etat._t);
    if (!erreur) etat._t = setTimeout(function () { etatEl.textContent = "☁ À jour"; etatEl.style.background = "#1a3a5c"; }, 2500);
  }
  function fixeStyles() {
    var css = "" +
      "#jhc-voile{position:fixed;inset:0;z-index:99999;background:linear-gradient(135deg,#1a3a5c,#0f2238);display:flex;align-items:center;justify-content:center;font-family:'Open Sans',Calibri,Arial,sans-serif}" +
      "#jhc-voile .b{background:#fff;border-radius:16px;padding:32px;width:min(420px,92vw);box-shadow:0 20px 60px rgba(0,0,0,.35);color:#2d2d2d}" +
      "#jhc-voile h1{font-size:22px;font-weight:800;color:#1a3a5c;margin:0 0 6px}" +
      "#jhc-voile p{font-size:14px;margin:0 0 14px;line-height:1.45;color:#475569}" +
      ".jhc-in{width:100%;border:1px solid #cbd5e1;border-radius:10px;padding:10px 12px;font-size:15px;margin:0 0 12px;outline:none}" +
      ".jhc-in:focus{border-color:#52a431}" +
      ".jhc-btn{background:#52a431;color:#fff;border-radius:999px;padding:10px 18px;font-weight:700;font-size:14px;cursor:pointer;border:0}" +
      ".jhc-btn.sec{background:#e2e8f0;color:#1a3a5c}.jhc-btn:disabled{opacity:.5}" +
      ".jhc-err{color:#d93848;font-size:13px;min-height:18px}" +
      "#jhc-barre{position:fixed;right:16px;bottom:16px;z-index:9999;display:flex;gap:8px;align-items:center;font-family:'Open Sans',Calibri,Arial,sans-serif}" +
      "#jhc-etat{color:#fff;background:#1a3a5c;border-radius:999px;padding:6px 12px;font-size:12px;font-weight:600}" +
      "#jhc-panneau{position:fixed;right:16px;bottom:64px;z-index:9999;width:min(440px,94vw);max-height:76vh;overflow:auto;background:#fff;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.3);padding:18px;font-family:'Open Sans',Calibri,Arial,sans-serif;color:#2d2d2d;font-size:14px}" +
      "#jhc-panneau h2{font-size:17px;font-weight:800;color:#1a3a5c;margin:0 0 10px}" +
      "#jhc-panneau h3{font-size:13px;font-weight:700;color:#1a3a5c;margin:14px 0 6px;text-transform:uppercase;letter-spacing:.03em}" +
      ".jhc-ligne{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:6px 8px;border-radius:8px;cursor:pointer}" +
      ".jhc-ligne:hover{background:#f1f5f9}.jhc-ligne.sel{background:#e8f4e1}" +
      ".jhc-pastille{font-size:11px;background:#e8f4e1;color:#2f6b1a;border-radius:999px;padding:2px 8px;white-space:nowrap}" +
      ".jhc-x{color:#d93848;cursor:pointer;font-weight:700;padding:0 6px}" +
      "html[data-jhc-cloud] button[data-jhc-cache]{display:none!important}";
    document.head.appendChild(el("style", { texte: css }));
  }

  /* ---------- connexion ---------- */
  function ecranConnexion() {
    var voile = el("div", { id: "jhc-voile" });
    var boite = el("div", { "class": "b" });
    voile.appendChild(boite);
    document.body.appendChild(voile);
    var courriel = "";

    function etape1() {
      boite.innerHTML = "";
      var inp = el("input", { "class": "jhc-in", type: "email", placeholder: "votre.courriel@exemple.com", autocomplete: "email" });
      var err = el("div", { "class": "jhc-err" });
      var btn = el("button", { "class": "jhc-btn", texte: "Recevoir mon code" });
      function envoyer() {
        courriel = inp.value.trim().toLowerCase();
        if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(courriel)) { err.textContent = "Entrez une adresse courriel valide."; return; }
        btn.disabled = true; err.textContent = "";
        sb.auth.signInWithOtp({ email: courriel, options: { shouldCreateUser: true, emailRedirectTo: APP_URL } }).then(function (r) {
          btn.disabled = false;
          if (r.error) { err.textContent = traduireErreur(r.error); return; }
          etape2();
        });
      }
      btn.addEventListener("click", envoyer);
      inp.addEventListener("keydown", function (e) { if (e.key === "Enter") envoyer(); });
      [el("h1", { texte: "Banque d'idées" }),
       el("p", { texte: "Entrez votre courriel. Vous recevrez un lien de connexion (ou un code). Aucun mot de passe à retenir." }),
       inp, err, btn].forEach(function (c) { boite.appendChild(c); });
      setTimeout(function () { inp.focus(); }, 50);
    }
    function etape2() {
      boite.innerHTML = "";
      var inp = el("input", { "class": "jhc-in", inputmode: "numeric", placeholder: "Code reçu par courriel", autocomplete: "one-time-code" });
      var err = el("div", { "class": "jhc-err" });
      var btn = el("button", { "class": "jhc-btn", texte: "Me connecter" });
      function verifier() {
        var code = inp.value.replace(/\s/g, "");
        if (!code) { err.textContent = "Entrez le code reçu."; return; }
        btn.disabled = true;
        sb.auth.verifyOtp({ email: courriel, token: code, type: "email" }).then(function (r) {
          btn.disabled = false;
          if (r.error) err.textContent = traduireErreur(r.error);
        });
      }
      btn.addEventListener("click", verifier);
      inp.addEventListener("keydown", function (e) { if (e.key === "Enter") verifier(); });
      [el("h1", { texte: "Vérifiez vos courriels" }),
       el("p", { texte: "Un courriel a été envoyé à " + courriel + ". Cliquez sur le lien qu'il contient, ou entrez ici le code s'il y en a un." }),
       inp, err, btn, " ",
       el("button", { "class": "jhc-btn sec", texte: "Changer d'adresse", onclick: etape1 })].forEach(function (c) { boite.appendChild(c); });
      setTimeout(function () { inp.focus(); }, 50);
    }
    etape1();
    return voile;
  }
  function traduireErreur(e) {
    var m = (e && (e.code || e.message)) || "";
    if (/not_authorized|not authorized/i.test(m)) return "Les courriels de connexion ne sont pas encore activés pour cette adresse. Avisez la personne qui vous a invité.";
    if (/rate|429/i.test(m)) return "Trop de demandes. Attendez quelques minutes et réessayez.";
    if (/expired|invalid/i.test(m)) return "Ce code est invalide ou expiré. Demandez-en un nouveau.";
    return "Erreur : " + (e.message || m);
  }

  /* ---------- chargement ---------- */
  function chargerTout() {
    return sb.from("idees").select("id,proprietaire,numero,donnees,modifie_le").order("numero", { ascending: true }).then(function (r) {
      if (r.error) throw r.error;
      return sb.from("partages_idees").select("idee_id,courriel,role").then(function (p) {
        if (p.error) throw p.error;
        var roles = {};
        p.data.forEach(function (x) { if (x.courriel === monCourriel) roles[x.idee_id] = x.role; });
        return r.data.map(function (row) {
          noter(row, roles[row.id]);
          return row.donnees;
        });
      });
    });
  }
  function noter(row, role) {
    var d = row.donnees || {};
    d.id = row.id;
    dernier[row.id] = JSON.stringify(d);
    proprio[row.id] = row.proprietaire;
    monRole[row.id] = row.proprietaire === moi.id ? "proprietaire" : (role || monRole[row.id] || "lecteur");
  }

  function demarrerApp(idees) {
    var doc = {
      version: 1, docId: "jhe-banque-idees-en-ligne", titre: "Banque d'idées",
      modifieLe: new Date().toISOString(), notesGenerales: "", recents: [], supprimees: [],
      idees: idees, liaisons: {}
    };
    var donnees = document.getElementById("jh-idees-data");
    donnees.textContent = JSON.stringify(doc).replace(/</g, "\\u003c");
    window.JHCLOUD = { sauver: sauver };
    document.documentElement.setAttribute("data-jhc-cloud", "1");
    var src = document.getElementById("jh-app-module").textContent;
    var s = document.createElement("script");
    s.type = "module";
    s.textContent = src;
    document.body.appendChild(s);
    barre();
    cacherEnregistrerFichier();
    // Ctrl+S enregistrait dans un fichier : en ligne, tout est déjà enregistré
    window.addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && (e.key === "s" || e.key === "S")) { e.preventDefault(); e.stopImmediatePropagation(); etat("☁ Déjà enregistré en ligne"); }
    }, true);
    ecouterEnDirect();
  }

  /* L'app d'origine enregistre aussi dans un fichier HTML/Word/Obsidian : inutile en ligne. */
  function cacherEnregistrerFichier() {
    var obs = new MutationObserver(function () {
      document.querySelectorAll("button:not([data-jhc-cache])").forEach(function (b) {
        var t = (b.getAttribute("title") || "") + " " + (b.textContent || "");
        if (/Obsidian|Enregistrer dans le fichier/.test(t)) b.setAttribute("data-jhc-cache", "1");
      });
    });
    obs.observe(document.body, { childList: true, subtree: true, characterData: true });
  }

  /* ---------- enregistrement ---------- */
  function sauver(doc) {
    var copie = doc.idees.slice();
    file = file.then(function () { return envoyer(copie); }).catch(function (e) {
      console.error(e); etat("⚠ Non enregistré : " + (e.message || e), true);
    });
    return Promise.resolve("indexeddb");
  }
  function envoyer(idees) {
    var vus = {}, taches = [];
    idees.forEach(function (i) {
      vus[i.id] = 1;
      var j = JSON.stringify(i);
      if (dernier[i.id] === j) return;
      if (dernier[i.id] === undefined) {
        taches.push(sb.from("idees").insert({ id: i.id, numero: i.numero || null, donnees: i }).then(function (r) {
          if (r.error) throw r.error;
          dernier[i.id] = j; proprio[i.id] = moi.id; monRole[i.id] = "proprietaire";
        }));
      } else if (monRole[i.id] === "lecteur") {
        // lecture seule : on ignore les changements locaux
      } else {
        taches.push(sb.from("idees").update({ numero: i.numero || null, donnees: i }).eq("id", i.id).select("id").then(function (r) {
          if (r.error) throw r.error;
          if (!r.data || !r.data.length) throw new Error("accès refusé pour l'idée « " + (i.titre || i.id) + " »");
          dernier[i.id] = j;
        }));
      }
    });
    Object.keys(dernier).forEach(function (id) {
      if (vus[id]) return;
      var q = proprio[id] === moi.id
        ? sb.from("idees").delete().eq("id", id)
        : sb.from("partages_idees").delete().eq("idee_id", id).eq("courriel", monCourriel);
      taches.push(q.then(function (r) { if (r.error) throw r.error; delete dernier[id]; }));
    });
    if (!taches.length) return Promise.resolve();
    etat("☁ Enregistrement…");
    return Promise.all(taches).then(function () { etat("☁ Enregistré"); });
  }

  /* ---------- mise à jour en direct ---------- */
  function appliquer(fn) { if (window.__jhSetDoc) window.__jhSetDoc(function (d) { return d ? fn(d) : d; }); }
  function rechargerIdee(id) {
    return sb.from("idees").select("id,proprietaire,numero,donnees,modifie_le").eq("id", id).maybeSingle().then(function (r) {
      if (r.error || !r.data) return;
      if (dernier[id] === JSON.stringify(Object.assign({}, r.data.donnees, { id: id }))) return;
      return sb.from("partages_idees").select("role").eq("idee_id", id).eq("courriel", monCourriel).maybeSingle().then(function (p) {
        noter(r.data, p.data && p.data.role);
        var idee = r.data.donnees;
        appliquer(function (d) {
          var existe = d.idees.some(function (x) { return x.id === id; });
          return Object.assign({}, d, { idees: existe ? d.idees.map(function (x) { return x.id === id ? idee : x; }) : d.idees.concat([idee]) });
        });
      });
    });
  }
  function retirerIdee(id) {
    delete dernier[id];
    appliquer(function (d) { return Object.assign({}, d, { idees: d.idees.filter(function (x) { return x.id !== id; }) }); });
  }
  function ecouterEnDirect() {
    sb.channel("banque-idees")
      .on("postgres_changes", { event: "*", schema: "public", table: "idees" }, function (ev) {
        if (ev.eventType === "DELETE") { if (ev.old && ev.old.id && dernier[ev.old.id] !== undefined) retirerIdee(ev.old.id); return; }
        var n = ev.new || {};
        if (n.modifie_par === moi.id && dernier[n.id] !== undefined) return;
        rechargerIdee(n.id);
      })
      .on("postgres_changes", { event: "*", schema: "public", table: "partages_idees" }, function (ev) {
        var o = ev.eventType === "DELETE" ? ev.old : ev.new;
        if (!o) return;
        if (ev.eventType === "DELETE") {
          if (proprio[o.idee_id] && proprio[o.idee_id] !== moi.id && (!o.courriel || o.courriel === monCourriel)) {
            // vérifier si on y a encore accès
            sb.from("idees").select("id").eq("id", o.idee_id).maybeSingle().then(function (r) { if (!r.data) retirerIdee(o.idee_id); });
          }
        } else if (o.courriel === monCourriel) {
          monRole[o.idee_id] = o.role;
          rechargerIdee(o.idee_id);
        }
        if (panneauOuvert) rafraichirPanneau();
      })
      .subscribe();
  }

  /* ---------- barre et panneau de partage ---------- */
  var panneau = null, panneauOuvert = false, selection = null, filtre = "";
  function barre() {
    etatEl = el("span", { id: "jhc-etat", texte: "☁ À jour", title: "Vos changements sont enregistrés en ligne automatiquement" });
    var b = el("div", { id: "jhc-barre" }, [
      etatEl,
      el("button", { "class": "jhc-btn", texte: "👥 Partager", onclick: basculerPanneau })
    ]);
    document.body.appendChild(b);
  }
  function basculerPanneau() {
    panneauOuvert = !panneauOuvert;
    if (!panneauOuvert) { if (panneau) panneau.remove(); panneau = null; return; }
    panneau = el("div", { id: "jhc-panneau" });
    document.body.appendChild(panneau);
    rafraichirPanneau();
  }
  function ideesActuelles() {
    // état connu du serveur (à jour après chaque enregistrement)
    return Object.keys(dernier).map(function (id) { var x = JSON.parse(dernier[id]); return x; })
      .sort(function (a, b) { return (a.numero || 0) - (b.numero || 0); });
  }
  function rafraichirPanneau() {
    if (!panneau) return;
    sb.from("partages_idees").select("idee_id,courriel,role").then(function (r) {
      var partages = r.data || [];
      var parIdee = {};
      partages.forEach(function (p) { (parIdee[p.idee_id] = parIdee[p.idee_id] || []).push(p); });
      dessinerPanneau(parIdee);
    });
  }
  function dessinerPanneau(parIdee) {
    panneau.innerHTML = "";
    var toutes = ideesActuelles();
    var miennes = toutes.filter(function (i) { return proprio[i.id] === moi.id; });
    var recues = toutes.filter(function (i) { return proprio[i.id] !== moi.id; });

    panneau.appendChild(el("div", { style: "display:flex;justify-content:space-between;align-items:center" }, [
      el("h2", { texte: "Partager des idées" }),
      el("span", { "class": "jhc-x", texte: "✕", title: "Fermer", onclick: basculerPanneau })
    ]));
    panneau.appendChild(el("p", { style: "font-size:12px;color:#64748b;margin:0 0 8px", texte: "Connecté : " + monCourriel }));

    if (selection && proprio[selection] === moi.id) {
      var idee = toutes.filter(function (i) { return i.id === selection; })[0];
      if (idee) { dessinerDetail(idee, parIdee[selection] || []); return; }
    }

    if (miennes.length) {
      panneau.appendChild(el("p", { style: "font-size:13px;margin:0 0 8px", texte: "Choisissez une idée, puis entrez le courriel de la personne. Elle verra seulement les idées que vous lui partagez." }));
      var rech = el("input", { "class": "jhc-in", placeholder: "Rechercher une idée…", value: filtre });
      rech.addEventListener("input", function () { filtre = rech.value; dessinerListe(); });
      panneau.appendChild(rech);
      var liste = el("div");
      panneau.appendChild(liste);
      var dessinerListe = function () {
        liste.innerHTML = "";
        var f = filtre.toLowerCase();
        var tri = miennes.slice().sort(function (a, b) { return (parIdee[b.id] ? 1 : 0) - (parIdee[a.id] ? 1 : 0) || (a.numero || 0) - (b.numero || 0); });
        tri.filter(function (i) { return !f || ((i.numero + " " + (i.titre || "")).toLowerCase().indexOf(f) >= 0); }).forEach(function (i) {
          var n = (parIdee[i.id] || []).length;
          liste.appendChild(el("div", { "class": "jhc-ligne", onclick: function () { selection = i.id; dessinerPanneau(parIdee); } }, [
            el("span", { texte: "#" + (i.numero || "") + " " + (i.titre || "(sans titre)") }),
            n ? el("span", { "class": "jhc-pastille", texte: n + " personne" + (n > 1 ? "s" : "") }) : null
          ]));
        });
      };
      dessinerListe();
    }
    if (recues.length) {
      panneau.appendChild(el("h3", { texte: "Partagées avec moi" }));
      recues.forEach(function (i) {
        panneau.appendChild(el("div", { "class": "jhc-ligne", style: "cursor:default" }, [
          el("span", { texte: "#" + (i.numero || "") + " " + (i.titre || "(sans titre)") }),
          el("span", { "class": "jhc-pastille", texte: monRole[i.id] === "editeur" ? "peut modifier" : "lecture seule" })
        ]));
      });
    }
    panneau.appendChild(el("div", { style: "margin-top:14px;text-align:right" }, [
      el("button", { "class": "jhc-btn sec", texte: "Me déconnecter", onclick: function () { sb.auth.signOut().then(function () { location.reload(); }); } })
    ]));
  }
  function dessinerDetail(idee, partages) {
    panneau.appendChild(el("button", { "class": "jhc-btn sec", style: "padding:4px 12px;font-size:12px;margin-bottom:8px", texte: "← Toutes les idées", onclick: function () { selection = null; rafraichirPanneau(); } }));
    panneau.appendChild(el("h3", { texte: "#" + (idee.numero || "") + " " + (idee.titre || "") }));
    if (!partages.length) panneau.appendChild(el("p", { style: "font-size:13px;color:#64748b", texte: "Cette idée n'est partagée avec personne." }));
    partages.forEach(function (p) {
      var sel = el("select", { "class": "jhc-in", style: "width:auto;margin:0;padding:4px 6px;font-size:12px" }, [
        el("option", { value: "editeur", texte: "peut modifier" }), el("option", { value: "lecteur", texte: "lecture seule" })
      ]);
      sel.value = p.role;
      sel.addEventListener("change", function () {
        sb.from("partages_idees").update({ role: sel.value }).eq("idee_id", idee.id).eq("courriel", p.courriel).then(function (r) { if (r.error) etat("⚠ " + r.error.message, true); else etat("☁ Droit modifié"); });
      });
      panneau.appendChild(el("div", { "class": "jhc-ligne", style: "cursor:default" }, [
        el("span", { texte: p.courriel }),
        el("span", { style: "display:flex;gap:4px;align-items:center" }, [
          sel,
          el("span", { "class": "jhc-x", texte: "Retirer", title: "Retirer l'accès", onclick: function () {
            sb.from("partages_idees").delete().eq("idee_id", idee.id).eq("courriel", p.courriel).then(function (r) { if (r.error) etat("⚠ " + r.error.message, true); rafraichirPanneau(); });
          } })
        ])
      ]));
    });
    panneau.appendChild(el("h3", { texte: "Inviter une personne" }));
    var inp = el("input", { "class": "jhc-in", type: "email", placeholder: "courriel@exemple.com" });
    var role = el("select", { "class": "jhc-in" }, [
      el("option", { value: "editeur", texte: "Peut modifier (collaboration)" }), el("option", { value: "lecteur", texte: "Lecture seule" })
    ]);
    var err = el("div", { "class": "jhc-err" });
    var btn = el("button", { "class": "jhc-btn", texte: "Partager et préparer l'invitation" });
    btn.addEventListener("click", function () {
      var c = inp.value.trim().toLowerCase();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(c)) { err.textContent = "Entrez une adresse courriel valide."; return; }
      btn.disabled = true;
      sb.from("partages_idees").upsert({ idee_id: idee.id, courriel: c, role: role.value }).then(function (r) {
        btn.disabled = false;
        if (r.error) { err.textContent = "Erreur : " + r.error.message; return; }
        var sujet = "Invitation : idée « " + (idee.titre || "") + " »";
        var corps = "Bonjour,\n\nJe t'invite à travailler avec moi sur l'idée « " + (idee.titre || "") + " » dans ma banque d'idées.\n\n" +
          "1. Ouvre ce lien : " + APP_URL + "\n2. Entre ton adresse courriel (" + c + ") et confirme avec le lien ou le code reçu.\n\n" +
          "Tu verras seulement les idées que je partage avec toi.\n\nMerci!";
        location.href = "mailto:" + encodeURIComponent(c) + "?subject=" + encodeURIComponent(sujet) + "&body=" + encodeURIComponent(corps);
        etat("☁ Partagé avec " + c);
        rafraichirPanneau();
      });
    });
    [inp, role, err, btn,
     el("p", { style: "font-size:12px;color:#64748b;margin-top:10px", texte: "Le bouton ouvre un courriel prêt à envoyer dans votre messagerie. L'accès est actif dès maintenant, même si vous n'envoyez pas le courriel." })
    ].forEach(function (c) { panneau.appendChild(c); });
  }

  /* ---------- import initial de la banque (propriétaire, une seule fois) ---------- */
  function ecranImport(voile, suite) {
    var boite = voile.querySelector(".b");
    boite.innerHTML = "";
    var err = el("div", { "class": "jhc-err" });
    var fichier = el("input", { type: "file", accept: ".html,.htm,.json", style: "margin:0 0 12px" });
    var btn = el("button", { "class": "jhc-btn", texte: "Importer mes idées" });
    btn.addEventListener("click", function () {
      var f = fichier.files && fichier.files[0];
      if (!f) { err.textContent = "Choisissez votre fichier Idees_Logiciels_Skills_Agents.html."; return; }
      btn.disabled = true; err.textContent = "Lecture du fichier…";
      f.text().then(function (t) {
        var doc;
        if (/\.json$/i.test(f.name)) doc = JSON.parse(t);
        else {
          var m = /<script[^>]*\bid=["']?jh-idees-data["']?[^>]*>([\s\S]*?)<\/script>/.exec(t);
          if (!m) throw new Error("Ce fichier ne contient pas de banque d'idées.");
          doc = JSON.parse(m[1]);
        }
        if (!doc || !Array.isArray(doc.idees)) throw new Error("Ce fichier ne contient pas de banque d'idées.");
        var supp = {}; (doc.supprimees || []).forEach(function (x) { supp[x] = 1; });
        var lignes = doc.idees.filter(function (i) { return i && i.id && !supp[i.id]; })
          .map(function (i) { return { id: i.id, numero: i.numero || null, donnees: i }; });
        var paquets = [];
        for (var k = 0; k < lignes.length; k += 8) paquets.push(lignes.slice(k, k + 8));
        var fait = 0;
        return paquets.reduce(function (p, paq) {
          return p.then(function () {
            return sb.from("idees").upsert(paq).then(function (r) {
              if (r.error) throw r.error;
              fait += paq.length; err.textContent = "Envoi : " + fait + " / " + lignes.length + " idées…";
            });
          });
        }, Promise.resolve());
      }).then(function () { err.textContent = ""; suite(); }).catch(function (e) {
        btn.disabled = false; err.textContent = "Erreur : " + (e.message || e);
      });
    });
    [el("h1", { texte: "Bienvenue!" }),
     el("p", { texte: "Votre banque en ligne est vide. Choisissez votre fichier actuel (Idees_Logiciels_Skills_Agents.html) pour y copier toutes vos idées et leurs photos. Votre fichier n'est pas modifié." }),
     fichier, err, btn, " ",
     el("button", { "class": "jhc-btn sec", texte: "Commencer vide", onclick: function () { suite(); } })
    ].forEach(function (c) { boite.appendChild(c); });
  }

  /* ---------- démarrage ---------- */
  function apresConnexion(session, voile) {
    moi = session.user;
    monCourriel = (moi.email || "").toLowerCase();
    var go = function () {
      chargerTout().then(function (idees) {
        var aMoi = idees.some(function (i) { return proprio[i.id] === moi.id; });
        if (!idees.length && !aMoi && !voile._importVu) {
          voile._importVu = true;
          ecranImport(voile, go);
          return;
        }
        voile.remove();
        demarrerApp(idees);
      }).catch(function (e) {
        var b = voile.querySelector(".b");
        b.innerHTML = "";
        b.appendChild(el("h1", { texte: "Connexion impossible" }));
        b.appendChild(el("p", { texte: "Le serveur ne répond pas : " + (e.message || e) + ". Réessayez dans un instant (si la base a été mise en pause, elle redémarre en quelques minutes)." }));
        b.appendChild(el("button", { "class": "jhc-btn", texte: "Réessayer", onclick: function () { location.reload(); } }));
      });
    };
    go();
  }

  function init() {
    fixeStyles();
    if (!window.supabase || !window.supabase.createClient) {
      document.body.appendChild(el("p", { style: "padding:40px;font-family:sans-serif", texte: "Impossible de charger le module de connexion. Vérifiez votre connexion Internet." }));
      return;
    }
    sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_CLE, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true, flowType: "implicit" } });
    var voile = ecranConnexion();
    var parti = false;
    function essai(session) {
      if (parti || !session) return;
      parti = true;
      if (location.hash && /access_token|error/.test(location.hash)) history.replaceState(null, "", APP_URL);
      var b = voile.querySelector(".b");
      b.innerHTML = "";
      b.appendChild(el("h1", { texte: "Chargement…" }));
      b.appendChild(el("p", { texte: "Ouverture de vos idées." }));
      apresConnexion(session, voile);
    }
    sb.auth.getSession().then(function (r) { essai(r.data && r.data.session); });
    sb.auth.onAuthStateChange(function (_ev, session) { setTimeout(function () { essai(session); }, 0); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
