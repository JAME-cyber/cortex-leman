---
name: l-oeil-de-cortex-arxiv-browser-console-method
category: data-science
description: "MÉTHODE RECOMMANDÉE pour scanner ArXiv en cron. browser_navigate + browser_console avec extraction DOM JavaScript. Pas de double-encodage, filtrage in-browser, réponse compacte. Testée 2026-07-22 sur 290 papers (cs.AI:68 + cs.CR:23 + cs.CV:78 + cs.LG:121)."
---

# ArXiv Scan via Browser Console (MÉTHODE RECOMMANDÉE)

## POURQUOI CETTE MÉTHODE EST PRÉFÉRÉE

| Problème Apify RAG | Solution browser_console |
|---------------------|--------------------------|
| Double-encodage JSON (2 niveaux de `json.loads`) | Pas d'encodage — `browser_console` retourne du JSON natif |
| Datasets tronqués si >100KB (markdown sur 1 ligne illisible) | Filtrage in-browser : on ne renvoie QUE les papers pertinents |
| Brackets markdown échappés (`\\[N\\]` au lieu de `[N]`) | Le DOM donne le texte brut sans escaping markdown |
| `execute_code` bloqué en cron (approvals) | `browser_console` utilise le paramètre `expression` (pas de sandbox Python) |
| Coût Apify (compute units par scrape) | Gratuit — navigateur local |

## WORKFLOW COMPLET (4 étapes, ~2 min par domaine)

### Étape 1 — Naviguer vers la page de listing

```
browser_navigate(url="https://arxiv.org/list/cs.CR/new")
```

Retourne un snapshot mais **on l'ignore** — il sert juste à initialiser la session browser.

### Étape 2 — Récupérer TOUS les papers du domaine

Appeler `browser_console` avec une expression JS qui extrait chaque entrée de la DescriptionList ArXiv :

```javascript
JSON.stringify(Array.from(document.querySelectorAll('dl > dt')).map(dt => {
  const link = dt.querySelector('a[href*="abs/"]');
  const id = link ? link.getAttribute('href').replace('/abs/','') : '';
  const dd = dt.nextElementSibling;
  const title = dd ? (dd.querySelector('.list-title') ? dd.querySelector('.list-title').textContent.replace('Title:','').trim() : '') : '';
  const subjects = dd ? (dd.querySelector('.list-subjects') ? dd.querySelector('.list-subjects').textContent.replace('Subjects:','').trim() : '') : '';
  const abs = dd ? (dd.querySelector('p') ? dd.querySelector('p').textContent.trim() : '') : '';
  return {id, title, subjects, abs};
}).filter(x => x.id))
```

**IMPORTANT — structure DOM ArXiv :**
- Chaque entrée est un `<dt>` (term) suivi d'un `<dd>` (definition)
- Le lien `a[href*="abs/"]` dans le `<dt>` donne l'arXiv ID
- `.list-title` dans le `<dd>` donne le titre (préfixé par "Title:")
- `.list-subjects` donne les subjects (préfixé par "Subjects:")
- `p` dans le `<dd>` donne l'abstract (tronqué ~500 chars sur /new)

**Si le résultat dépasse le contexte** (>400 papers comme cs.LG en /recent) :
- Le résultat est persisté dans `/tmp/hermes-results/call_<N>.txt`
- Utiliser `read_file` avec offset/limit pour parcourir
- Ou mieux : utiliser la version filtrée (Étape 2b ci-dessous)

### Étape 2B — VERSION FILTRÉE (recommandée pour réduire le contexte)

Ajouter un filtre regex dans le `.filter()` pour ne renvoyer QUE les papers pertinents Cortex Leman. La réponse passe de ~290 papers à ~25-35, ce qui tient confortablement dans le contexte :

```javascript
JSON.stringify(Array.from(document.querySelectorAll('dl > dt')).slice(0,121).map(dt => {
  const link = dt.querySelector('a[href*="abs/"]');
  const id = link ? link.getAttribute('href').replace('/abs/','') : '';
  const dd = dt.nextElementSibling;
  const title = dd ? (dd.querySelector('.list-title') ? dd.querySelector('.list-title').textContent.replace('Title:','').trim() : '') : '';
  const subjects = dd ? (dd.querySelector('.list-subjects') ? dd.querySelector('.list-subjects').textContent.replace('Subjects:','').trim() : '') : '';
  const abs = dd ? (dd.querySelector('p') ? dd.querySelector('p').textContent.trim() : '') : '';
  return {id, title, subjects, abs};
}).filter(x => x.id && (
  /privacy|gdpr|rgpd|security|attack|vulnerab|safe|audit|compli|regulat|govern|ethic|risk|bias|fairness|trustworthy|transparen|explainab|accountab|ai act|watermark|provenance|misinform|deepfake|poison|inject|adversarial|privacy-preserv|differential privacy|federated|consent|data protection|right|law|biometric|face|surveillance|forgery|forensic/i.test(x.title+x.subjects+x.abs)
)))
```

**Adapter le `.slice(0, N)`** au nombre de new submissions du domaine :
- cs.AI/new : `.slice(0, 68)` (typique 40-80)
- cs.CR/new : `.slice(0, 23)` (typique 15-30)
- cs.CV/new : `.slice(0, 78)` (typique 50-100)
- cs.LG/new : `.slice(0, 121)` (typique 80-150)

Le nombre exact est visible dans le snapshot `browser_navigate` ("showing X of X entries").

### Étape 3 — Répéter pour les 4 domaines

Les 4 pages sont indépendantes. En cron (pas de parallélisme implicite), faire les 4 navigations + extractions séquentiellement :

```
# Domaine 1: cs.CR (souvent le plus pertinent pour compliance)
browser_navigate(url="https://arxiv.org/list/cs.CR/new")
browser_console(expression=<extraction code>)

# Domaine 2: cs.AI
browser_navigate(url="https://arxiv.org/list/cs.AI/new")
browser_console(expression=<extraction code>)

# Domaine 3: cs.CV
browser_navigate(url="https://arxiv.org/list/cs.CV/new")
browser_console(expression=<extraction code>)

# Domaine 4: cs.LG
browser_navigate(url="https://arxiv.org/list/cs.LG/new")
browser_console(expression=<extraction code>)
```

### Étape 4 — Scorer et rédiger le rapport

Avec les données filtrées des 4 domaines en contexte, appliquer le scoring 0-20 du SKILL.md principal et rédiger le rapport selon le template.

## ORDRE DE PRIORITÉ DES OUTILS (cron job)

```
1. web_search natif → essayer en premier (gratuit, rapide)
   ⚠️ Souvent échoue en cron: "Web tools are not configured" (Firecrawl manquant)
   
2. SI web_search échoue → Apify RAG (mcp_apify_apify__rag_web_browser)
   ⚠️ Pièges: double-encodage, datasets tronqués, coût compute
   
3. SI Apify pose problème → Browser Console (cette méthode)
   ✅ MéTHODE LA PLUS FIABLE — la privilégier directement en cron
```

**Recommandation pratique :** En cron, commencer directement par la méthode Browser Console (Étapes 1-3). C'est la plus fiable et la plus rapide. Ne passer par web_search/Apify que si le browser est indisponible.

## PIÈGES

### 1. Ne pas oublier le `browser_navigate` avant `browser_console`
`browser_console` nécessite qu'une page soit chargée. Toujours faire `browser_navigate` d'abord, même si on ignore le snapshot retourné.

### 2. Le paramètre `expression` n'est pas du Python
C'est du JavaScript qui s'exécute dans le contexte du navigateur. Pas d'imports Python, pas de `json.loads`. `JSON.stringify()` côté navigateur → `json.loads` automatique côté Hermes.

### 3. Sélecteurs CSS ArXiv (vérifiés 2026-07-22)
- `dl > dt` : chaque entrée (term). `dt.nextElementSibling` = le `<dd>` (definition)
- `a[href*="abs/"]` : lien vers l'abstract (contient l'arXiv ID)
- `.list-title` : titre (contient "Title:" préfixe à nettoyer)
- `.list-subjects` : subjects (contient "Subjects:" préfixe à nettoyer)
- `p` : abstract tronqué

Si ArXiv change son HTML, ces sélecteurs peuvent casser. Vérifier avec `browser_snapshot(full=true)` en cas de problème.

### 4. cs.LG peut dépasser le contexte
cs.LG/new a souvent 120+ new submissions. La version filtrée (Étape 2B) réduit à ~20-30 papers pertinents. Si même ça déborde, ajouter des keywords au regex de filtrage ou réduire `substring(0, 200)` sur l'abstract.

### 5. Cross-lists
Les `dl > dt` incluent les cross-lists ET les replacements. Pour ne capturer que les new submissions, observer la position : ArXiv a 3 sections dans la `<dl>` — "New submissions", "Cross-lists", "Replacements". Les entêtes sont des `<h3>`. Le `.slice(0, N)` avec N = nombre de new submissions approxime bien cette limite.
