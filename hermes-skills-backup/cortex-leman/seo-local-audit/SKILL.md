---
name: seo-local-audit
description: "Use when auditing local business SEO FR-CH."
---

# SEO Local Audit Agent

Audit SEO local automatisé pour commerces FR-CH. 8 dimensions scorées, rapport markdown + plan d'action prioritaire.

## Trigger
- "audit SEO de [commerce]"
- "analyse le référencement de [commerce]"
- Intégré au pipeline SocialPulse après DIAGNOSER (scoring lead → audit SEO → BUILDER optimise)

## Architecture

Agent SocialPulse : `/home/tars/socialpulse-mvp/annemasse-agency/agents/seo_agent.py`

### 8 Dimensions auditées

| # | Dimension | Ce qu'elle vérifie | Sans site |
|---|-----------|-------------------|-----------|
| 1 | **Visibilité Google** | Recherche nom+ville, signaux GBP, avis | Poids 3x |
| 2 | **Santé site web** | Title, meta desc, h1/h2, viewport, HTTPS, OG tags, canonical | Poids 0 |
| 3 | **Données structurées** | JSON-LD LocalBusiness (adresse, horaires, téléphone, geo, rating) | Poids 0 |
| 4 | **Citations locales** | PagesJaunes, Yelp, Facebook, Google Maps | Poids 2x |
| 5 | **Réseaux sociaux** | Détection liens FB/IG/LinkedIn/TikTok/YT dans le HTML | Poids 1x |
| 6 | **Performance** | Load time, page size, scripts, domaines externes, lazy load, CSS | Poids 0 |
| 7 | **Qualité contenu** | Word count, NAP (nom/adresse/tél), liens internes, alt images, FAQ | Poids 0 |
| 8 | **Mots-clés** | Recommandations par secteur + ville (advisory, non scoré) | Advisory |

### Scoring

- Score global pondéré 0-100
- Sans site web : dimensions web = poids 0, visibilité Google et citations = poids majoré
- Niveau : 🟢 75+ | 🟡 50-74 | 🟠 25-49 | 🔴 <25

## Usage CLI

```bash
cd /home/tars/socialpulse-mvp/annemasse-agency

# Audit standalone
python3 agents/seo_agent.py \
  --name "Nom Commerce" \
  --city "Annemasse" \
  --sector "Restaurant" \
  --website "https://exemple.fr" \
  --phone "0450639292" \
  --address "7 Route de Vernier, 74100 Annemasse"

# Sans site web (le scénario SocialPulse typique)
python3 agents/seo_agent.py \
  --name "Nom Commerce" \
  --city "Annemasse" \
  --sector "Restaurant"
```

### API Python

```python
import sys; sys.path.insert(0, "agents")
from seo_agent import run_audit

result = run_audit({
    "name": "Il Vesuvio",
    "city": "Annemasse",
    "sector": "Restaurant",
    "website": "https://il-vesuvio.fr",
    "phone": "0450639292",
    "address": "7 Route de Vernier, 74100 Annemasse"
})

print(result["global_score"])     # int 0-100
print(result["scores"])            # dict {dimension: score}
print(result["report"])            # markdown FR
print(result["recommendations"])   # list[{priority, action, effort, impact}]
print(result["json_path"])         # path to JSON output
```

## Output

- **JSON** : `output/seo-audits/<slug>-<timestamp>.json`
- **Markdown** : `output/seo-audits/<slug>-<timestamp>.md`

Le rapport markdown contient :
1. Score global + tableau récap
2. Scores par dimension avec statut couleur
3. Détails techniques par dimension
4. Recommandations mots-clés (primary, longue traîne, marque)
5. Plan d'action prioritisé (CRITIQUE > HAUTE > MOYENNE > BASSE) avec effort + impact

## Intégration SocialPulse

Position dans le pipeline :

```
SCOUT (trouve commerce) → DIAGNOSER (score lead) → SEO_AUDIT (ce skill) → BUILDER (génère site optimisé)
```

Le SEO audit :
1. Identifie les gaps SEO avant génération du site
2. Le BUILDER reçoit les recommandations et génère un site avec les fixes intégrés
3. Le rapport est un **deliverable vendable** standalone (audit → upsell site + maintenance SEO)

## Limitations connues

- **Google Search** peut être bloqué (rate limiting / CAPTCHA). Le score de visibilité tombe à 5/100 dans ce cas.
- **PagesJaunes** bloque souvent (403). Yelp reste plus accessible.
- L'audit performance est **heuristique** (pas PageSpeed Insights API) : count scripts, page size, load time mesuré côté serveur.
- Pour tester un site local (généré par BUILDER) : lancer `python3 -m http.server` dans le dossier client puis pointer `--website http://localhost:PORT`.

## Secteurs supportés

Restaurant, Salon de coiffure, Plombier/Chauffagiste, Boulangerie, Garage auto, Avocat, Immobilier, Cabinet comptable, Kiné/Ostéopathe, Fleuriste + fallback générique.
