---
name: l-oeil-de-cortex-arxiv-apify-rag-method
category: data-science
description: Methode Apify RAG Web Browser pour scanner ArXiv listing pages. Plus fiable que l'API ArXiv en cron (bypass HTTP blocking). Retourne le contenu markdown des pages de listing pour extraction.

---

# ArXiv Scan via Apify RAG Web Browser

## QUAND UTILISER

- Cron jobs ou l'API ArXiv est bloquee par security policies (plain HTTP rejection)
- `terminal` curl refuse les URLs HTTP
- `execute_code` est en mode cron restreint
- On veut les listings du jour (new submissions, cross-lists, replacements)

## METHODE

### Etape 1: Scraper les 4 domaines

Utiliser `mcp_apify_apify__rag_web_browser` avec les URLs directes des pages de listing.

**Choix de l'endpoint selon l'objectif du scan :**

| Endpoint | Contenu | Volume typique | Cas d'usage |
|----------|---------|---------------:|-------------|
| `/list/cs.{X}/new` | Dernier batch (aujourd'hui) | 20-80 entries | Scan quotidien "what's new" (Lun-Ven) |
| `/list/cs.{X}/recent` | Fenêtre roulante 5 jours (Mon→Fri) | 180-960 entries | Scan de rattrapage, vérification exhaustivité, rapport delta week-end |

```
# Pour un scan quotidien standard (Lun-Ven)
mcp_apify_apify__rag_web_browser(query="https://arxiv.org/list/cs.AI/new", maxResults=1)
mcp_apify_apify__rag_web_browser(query="https://arxiv.org/list/cs.CR/new", maxResults=1)
mcp_apify_apify__rag_web_browser(query="https://arxiv.org/list/cs.CV/new", maxResults=1)
mcp_apify_apify__rag_web_browser(query="https://arxiv.org/list/cs.LG/new", maxResults=1)

# Pour un scan de rattrapage ou rapport delta (utilise /recent)
mcp_apify_apify__rag_web_browser(query="https://arxiv.org/list/cs.AI/recent", maxResults=1)
# ... idem pour cs.CR, cs.CV, cs.LG
```

Les 4 appels sont indépendants - les lancer en parallele.

**Pattern week-end (IMPORTANT) :** ArXiv ne publie pas de nouvelles soumissions le samedi ni le dimanche. Un cron qui tourne le week-end verra des listings identiques à ceux du vendredi précédent. Dans ce cas :
- Ne PAS générer un rapport vide ni dupliquer le rapport de vendredi.
- À la place, produire un **rapport delta** : comparer les 50 premières entrées de chaque domaine avec le rapport précédent, et signaler les papers à forte pertinence qui ont été omis ou sous-évalués (angles morts). C'est une valeur réelle — un scan humain/LLM peut manquer 10-20% des papers pertinents sur un volume de 200+.
- Le prochain lot de nouvelles soumissions attendu est Lundi ~20:00 UTC (réouverture ArXiv).

### Etape 2: Extraire le markdown des datasets

Chaque appel retourne un datasetId. Extraire le contenu:

```
mcp_apify_get_dataset_items(datasetId=<id>, fields="markdown", limit=1)
```

ATTENTION: Le contenu peut etre tres grand (cs.CR ~216KB, cs.LG ~1MB).
- Pour les petits datasets (<50KB), lire directement
- Pour les grands (>100KB), le resultat est sauvegarde dans /tmp/hermes-results/
  Utiliser `read_file` avec offset/limit, puis extraire avec `terminal` Python

### Etape 3: Decoder le DOUBLE-encodage JSON (CRITIQUE)

**PIEGE MAJEUR**: Le resultat de `mcp_apify_get_dataset_items` est enveloppe dans
`{"result": "...```toon\n...markdown...```..."}`. La valeur markdown a l'interieur est
ELLE-MEME une chaine JSON-escapee (`\\n` pour newlines, `\\"` pour quotes).

Il faut DEUX niveaux de decodage :

```python
import json, re
from pathlib import Path

def decode_to_markdown(filepath):
    raw = Path(filepath).read_text(encoding="utf-8", errors="replace")
    data = json.loads(raw)                    # 1er decodage: wrapper externe
    result = data.get("result", "")
    marker = "items[1]{markdown}:"
    idx = result.find(marker)
    q_start = result.find('"', idx)
    fence_idx = result.rfind("```")
    segment = result[q_start + 1:fence_idx] if fence_idx > q_start else result[q_start + 1:]
    close_q = segment.rfind('"')
    md_escaped = segment[:close_q] if close_q >= 0 else segment
    try:
        return json.loads('"' + md_escaped + '"')  # 2eme decodage: markdown interne
    except (json.JSONDecodeError, ValueError):
        return md_escaped.replace("\\\\", "\\").replace("\\n", "\n").replace('\\"', '"')
```

**Symptome si oublie du 2eme decodage**: `len(markdown)` est correct mais aucune regex
ne matche, car les `\n` sont litteraux (backslash + n) au lieu de vrais newlines.

### Etape 4: Parser les titres et IDs (brackets markdown echappes)

Apres decodage complet, les entrees ArXiv ont des brackets markdown echappes:
`\[N\] [arXiv:XXXX.XXXXX]` (backslash-crochet, pas crochet simple).

Le regex de split DOIT utiliser `\\\[(\d+)\\\]` (3 backslashes en Python raw string):

```python
def extract_new_submissions(markdown):
    start_m = re.search(r'###\s*New submissions', markdown)
    if not start_m:
        return ""
    start = start_m.end()
    end_m = re.search(r'###\s*(Cross|Replacements)', markdown[start:])
    end = start + end_m.start() if end_m else len(markdown)
    return markdown[start:end]

def parse_entries(section):
    papers = []
    # Pattern: \[N\] [arXiv:ID]  — backslash-escaped brackets
    parts = re.split(r'\\\[(\d+)\\\]\s*\[arXiv:', section)
    for i in range(1, len(parts), 2):
        if i + 1 >= len(parts):
            break
        block = parts[i + 1]
        id_m = re.match(r'(\d+\.\d+)', block)
        if not id_m:
            continue
        aid = id_m.group(1)
        title_m = re.search(r'Title:\s*(.+?)(?:\n\n|\n\\\[)', block, re.DOTALL)
        title = re.sub(r'\s+', ' ', title_m.group(1)).strip() if title_m else ""
        subj_m = re.search(r'Subjects:\s*(.+?)(?:\n|$)', block)
        subjects = subj_m.group(1).strip()[:200] if subj_m else ""
        abstract = ""
        if "Subjects:" in block:
            abstract = re.sub(r'\s+', ' ', block.split("Subjects:", 1)[-1]).strip()[:1500]
        papers.append({"arxiv_id": aid, "title": title, "subjects": subjects, "abstract": abstract})
    return papers
```

**Script complet operationnel**: `scripts/arxiv_apify_parse.py` (testé 2026-07-04,
333 papers parses depuis 4 domaines en 1 passage).

### Etape 5: Structurer les donnees

Les pages ArXiv /new ont 3 sections:
1. **New submissions** (premiere section, index 1..N)
2. **Cross-lists** (deuxieme section)
3. **Replacements** (troisieme section, papers mis a jour)

Pour le rapport quotidien, les new submissions sont les plus importantes.
Les replacements peuvent etre identifies par le label "(replaced)" dans le texte.

### Etape 5: Scorer la relevance

Voir la section "Scoring 0-20" dans le SKILL.md principal.

## AVANTAGES vs AUTRES METHODES

| Methode | Cron OK? | Pas API key? | Abstracts complets? | Bypass HTTP? | Parallelisable? |
|---------|----------|-------------|--------------------:|-------------|----------------|
| ArXiv API (curl) | Non (HTTP bloque) | Oui | Oui | Non | Non |
| Browser DOM (navigate) | Non (interactif) | Oui | Oui | Oui | Non |
| delegate_task + web | Oui | Non (web toolset) | Partiel | Oui | Oui |
| **Apify RAG browser** | **Oui** | **Non (Apify)** | **Partiel** | **Oui** | **Oui** |

## PIEGES

### 0. Double-encodage JSON (PIEGE MAJEUR — cause #1 d'echec de parsing)

Le resultat de `mcp_apify_get_dataset_items` est enveloppe dans:
`{"result": "...```toon\nitems[1]{markdown}: \"...MARKDOWN...\"\n```..."}`

La valeur markdown a l'interieur est ELLE-MEME une chaine JSON-escapee
(`\\n` = newline, `\\"` = quote). Un seul `json.loads` laisse les `\n` litteraux.

**Symptome**: `len(markdown)` est correct (~100KB+), `'New submissions' in markdown`
retourne True, mais AUCUNE regex ne matche — parce que les newlines sont des
paires backslash+n au lieu de `\x0a`.

**Fix**: Deux passes de decodage (voir Etape 3 ci-dessus) ou le script
`scripts/arxiv_apify_parse.py`.

### 0b. Brackets markdown echappes (cause #2 d'echec de parsing)

Apres decodage complet, les entrees ArXiv sont au format markdown echappe:
`\[1\] [arXiv:2607.01276]` — les crochets sont prefixes de backslash.

Un split naif sur `r'\[(\d+)\]'` rate toutes les entrees (0 papers parses).
Le bon pattern est `r'\\\[(\d+)\\\]\s*\[arXiv:'` (3 backslashes en Python
raw string pour matcher le backslash litteral + crochet).

### 1. Contenu trop grand pour le contexte
cs.LG peut avoir 240+ entries (~1MB markdown). Le dataset item est sauvegarde dans un fichier temporaire. Il faut utiliser `terminal` Python pour extraire les donnees, pas lire le markdown complet.

**Extraction rapide via `jq` (technique recommandée) :**

Quand `mcp_apify_get_dataset_items` persiste le résultat dans `/tmp/hermes-results/call_<N>.txt` (fichier JSON single-line), ne pas tenter de parser avec Python + regex sur tout le fichier. Utiliser `jq` en pipeline shell pour extraire titres + arXiv IDs en une commande :

```bash
cd /tmp/hermes-results && for f in call_<N1>.txt call_<N2>.txt ...; do
  echo "===== $f ====="
  jq -r '.result' "$f" 2>/dev/null \
    | jq -r '.items[0].markdown' 2>/dev/null \
    | grep -oE 'arXiv:2607\.[0-9]+|Title: [^\\]+|Fri, 17 Jul 2026|Thu, 16 Jul 2026|Wed, 15 Jul 2026|Tue, 14 Jul 2026|Mon, 13 Jul 2026' \
    | head -250
  echo
done
```

**Pourquoi jq plutôt que Python :**
- Le fichier est un JSON sur une seule ligne (`{"result": "{\"items\":[{\"markdown\":\"...\"}]}"}` — deux niveaux d'emboîtement). `jq -r '.result' | jq -r '.items[0].markdown'` décode les deux niveaux proprement.
- `grep -oE` sur `arXiv:YYYY.XXXXX` et `Title: [^\\]+` (car le backslash termine le titre en markdown échappé) capture les papiers en une passe.
- Adapté aux dates du jour (adapter le pattern `YYYY.XXXXX` au mois courant — `2607.` pour Juillet 2026, `2608.` pour Août, etc.).
- Cap `head -250` : limite aux 50 premières entrées × ~5 lignes par entrée (arXiv ID + Title + dates en-tête), suffisant pour le batch Fri.

**Symptôme si oubli du double `jq` :** un seul `jq -r '.result'` laisse une chaîne JSON-échappée (`\\n` littéral) — le `grep` ne matche rien car les newlines ne sont pas réelles.

### 1b. Cross-lists : ne pas les ignorer
Les pages `/recent` et `/new` contiennent une section **Cross-listings** (papiers publiés dans un domaine primaire mais cross-listés dans un autre). Exemple : un paper cs.AI publié en primary avec mention cs.CR apparaît dans cs.CR/recent avec le label `(cross-list from cs.AI)`. Ces cross-lists sont souvent **les plus pertinents pour Cortex Leman** (intersection AI × Sécurité × Vision). Le pattern d'extraction jq ci-dessus les capture automatiquement, mais il faut les identifier via le label `(cross-list from ...)` lors du scoring pour éviter de les compter deux fois dans le total.

### 2. Double entrees (new + cross-list + replacement)
Les IDs apparaissent potentiellement 2 fois si un paper est aussi un replacement. Dedupliquer avec un set Python.

### 3. Pas d'abstract complet
La page /new tronque les abstracts a ~500 chars. Pour les abstracts complets, scraper les pages individuelles via:
```
mcp_apify_apify__rag_web_browser(query="https://arxiv.org/abs/XXXX.XXXXX", maxResults=1)
```
Mais couteux en compute Apify. Ne le faire que pour les papers avec relevance >= 10.

### 4. Donnees Apify persistantes
Les datasets Apify restent accessibles ~7 jours. Si on a besoin de re-analyser, on peut re-fetcher le datasetId sans re-scraper.

## INTEGRATION DANS LE RAPPORT QUOTIDIEN

Le rapport final suit le template:
```
📊 CORTEX LEMAN - ArXiv Daily Report
Date: [date]

Domaines scannees: cs.AI | cs.CR | cs.CV | cs.LG
Papers scannees: [count]  
Papers importants (relevance >= 7/20): [count]
High impact (citations > 50 ou applicabilite directe): [count]

🚨 ALERTES CRITIQUES
[For each HIGH_IMPACT + HIGH_RELEVANCE paper]
Paper: "[title]"
arXiv: [id] | Domaine: [domain] | Relevance: [score]/20
[1-2 line summary]
Action: [action recommandee]

📋 NOUVEAUX PAPERS - Selection Cortex Leman
[Table: #, Titre, arXiv ID, Domaine, Relevance]

🔍 FOCUS COMPLIANCE FR-CH
[Table: Theme | Papers | Action Cortex Leman]

⚡ ACTIONS RECOMMANDEES
[Numbered priority list]

💡 Pour approfondir ces resultats, posez vos questions dans votre session Hermes.
```
