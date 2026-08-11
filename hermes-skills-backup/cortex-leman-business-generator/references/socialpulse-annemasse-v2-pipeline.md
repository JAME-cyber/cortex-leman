---
name: socialpulse-annemasse-v2-pipeline
version: 1.0.0
description: |
  SocialPulse Annemasse Agency v2 — Pipeline "Déjà Fait".
  7 agents (Scout, Diagnoser, Builder v2, Filmer v2, Pitcher, Checker, Mobile).
  Coût $0/batch (Overpass API + ffmpeg + Edge TTS, tout local).
  Différence vs v4: v4 = infrastructure de confiance (journal WORM, médiateur);
  Annemasse v2 = exécution à coût zéro pour générer des assets avant le pitch.
---

# SocialPulse Annemasse Agency v2 — Pipeline "Déjà Fait"

## CONCEPT

**Angle de vente**: "Voici votre site et votre vidéo. On active quand vous voulez."

Au lieu de pitcher un service ("on peut vous faire un site"), on génère les assets
AVANT le contact. Le PME voit SON site, SA vidéo, SON numéro. Conversion massivement
supérieure au cold pitch classique.

## ARCHITECTURE

```
SCOUT (Overpass API gratuit)
  → découverte leads (OpenStreetMap, $0)
    ↓
DIAGNOSER (score automatisé)
  → scoring, website_status, sector mapping
    ↓
BUILDER v2 (agents/builder_v2.py)
  → index.html + mentions-legales.html par client
  → SEO local, FormSubmit, dark theme, 8 secteurs
    ↓
FILMER v2 (agents/filmer_v2.py)
  → key-events.md + shots.json + vo-script.txt
  → vo-generate.sh (Edge TTS) + build.sh (ffmpeg)
    ↓
PITCHER v2 (agents/pitcher_v2.py) → CHECKER → MOBILE (existants)
```

> **Note**: PITCHER v2 remplace l'ancien PitcherAgent statique par un moteur
> conversationnel (state machine 10 états, intent detection FR, no-show recovery).
> Voir `references/socialpulse-pitcher-v2-conversational-agent.md` pour le détail.

### Stack technique

| Composant | Techno | Coût |
|-----------|--------|------|
| Scout | Overpass API (OSM) | $0 |
| Diagnoser | Local Python | $0 |
| Builder v2 | Template HTML + FormSubmit | $0 |
| Filmer v2 | Edge TTS + ffmpeg + seedance prompts | $0 |
| Dashboard | HTML statique | $0 |
| **Total par batch** | | **$0** |

## PATTERN: ADAPTER POUR ORCHESTRATEUR EXISTANT

Quand on branche de nouveaux générateurs (v2) dans un orchestrator qui attend
une interface `(state, journal)`, on crée un **adaptateur**.

### Fichier: `agents/v2_adapter.py`

```python
class BuilderV2Adapter:
    def __init__(self, state, journal):
        self.state = state
        self.journal = journal

    def run(self, campaign, max_builds=5):
        queue = self.state.get_queue()
        clients_dir = Path(__file__).parent.parent / "clients"

        top_leads = sorted(
            [l for l in queue if l.get("status") == "diagnosed"],
            key=lambda x: x.get("score", 0),
            reverse=True
        )[:max_builds]

        for lead in top_leads:
            # ISOLER chaque client dans son sous-dossier
            from builder_v2 import _slug
            slug = _slug(lead.get("name", "client"))
            client_dir = clients_dir / slug
            client_dir.mkdir(parents=True, exist_ok=True)

            result = generate_landing(lead, client_dir)
            # ... maj lead status, journal, etc.
```

### Branchement dans l'orchestrator

```python
# Avant (anciens agents inline):
self.builder = BuilderAgent(self.state, self.journal)

# Après (adaptateurs v2):
from v2_adapter import BuilderV2Adapter, FilmerV2Adapter
self.builder = BuilderV2Adapter(self.state, self.journal)
self.filmer = FilmerV2Adapter(self.state, self.journal)
```

Aucune rupture — les 5 autres agents restent intacts.

## PITFALLS RENCONTRÉS

### 1. Convention de l'output directory

**Problème**: `generate_landing(lead, output_dir)` écrit dans
`output_dir/index.html`, PAS dans `output_dir/<slug>/index.html`.

**Solution**: L'adaptateur doit créer `output_dir/<slug>/` et passer CE chemin
comme `output_dir`, pas le dossier parent `clients/`.

```python
# FAUX — écrase le même index.html à chaque appel
result = generate_landing(lead, clients_dir)

# CORRECT — isole chaque client
client_dir = clients_dir / slug
client_dir.mkdir(parents=True, exist_ok=True)
result = generate_landing(lead, client_dir)
```

### 2. Clés de retour différentes

Les générateurs v2 retournent des dicts avec des clés différentes de ce que
l'adaptateur attend. **Toujours vérifier les clés réelles** avec un test
individuel avant de câbler l'adaptateur.

```python
# Builder v2 retourne:
{"slug", "landing", "legal", "size_bytes", "size_kb", "url"}
# PAS: {"index_path"} ← erreur fréquente

# Filmer v2 retourne:
{"slug", "dir", "files", "cta_text", "tagline"}
# PAS: {"video_dir"} ← erreur fréquente
```

### 3. Filmer écrit dans le même dossier que Builder

Le FILMER v2 écrit directement dans `client_dir/` (pas dans un sous-dossier
`video/`). Les fichiers générés sont: `key-events.md`, `shots.json`,
`vo-script.txt`, `vo-generate.sh`, `build.sh`.

### 4. f-string + shell heredoc = explosion de braces

**Problème**: Quand on génère un fichier `build.sh` qui contient un heredoc
Python (`{AUDIO}`, `{CLIP}` etc.), les f-strings Python interprètent les
accolades du shell comme des variables Python.

**Solution**: Utiliser un template raw string au niveau module + `.replace()`:

```python
# Module-level constant (PAS de f-string)
_BUILD_SH_TEMPLATE = r'''#!/bin/bash
set -e
BASE="$(dirname "$0")"
CLIPS="$BASE/clips"
AUDIO="$BASE/audio"
# ... bash avec heredoc Python (accolades intactes)
'''

# Dans la fonction — remplacer les placeholders
build_sh = _BUILD_SH_TEMPLATE
build_sh = build_sh.replace("__SLUG__", slug)
build_sh = build_sh.replace("__AUDIO_PATH__", audio_abs_path)
```

### 5. Port conflict avec http.server

Quand on lance `python3 -m http.server 8765` alors qu'un autre serveur tourne
déjà sur ce port, le nouveau serveur échoue silencieusement et l'ancien continue
de répondre (404 depuis un autre cwd). Toujours `kill` les anciens processus
avant de bind un port.

```bash
# Trouver et tuer l'ancien serveur
ps aux | grep "http.server 8765" | grep -v grep
kill <PID>

# OU utiliser un port différent
python3 -m http.server 8766
```

## CONVENTIONS DE GÉNÉRATEURS STANDALONE

Pour que les générateurs BUILDER/FILMER restent réutilisables (standalone OU via
adaptateur), respecter ces conventions:

| Convention | Règle |
|-----------|-------|
| Entrée | `generate_landing(lead: dict, output_dir: Path) -> dict` |
| Output | Écrit dans `output_dir/index.html` (adaptateur isole par slug) |
| Slug | Fonction `_slug(name: str) -> str` (lowercase, accents retirés, mots reliés par `-`) |
| Retour | Dict avec `{"slug", "size_bytes", "size_kb", "url"}` minimum |
| Demo mode | `python3 builder_v2.py --demo` génère un lead factice pour test |
| Lint | `python3 -m py_compile` passe sans erreur |

## COUVERTURE SECTEURS

Builder v2 et Filmer v2 ont des configs pour 8 secteurs:

| Secteur | Config clé |
|---------|-----------|
| Restaurant | Horaires, menu highlights, réservation |
| Coiffure | Services, tarifs, galerie |
| Plombier | Interventions 24/7, devis gratuit |
| Garage | Réparations, contrôle technique |
| Boulangerie | Pain du jour, spécialités |
| Immobilier | Biens, estimation, contact |
| Avocat | Domaines d'expertise, consultation |
| Fleuriste | Bouquets, occasions, livraison |

Fallback générique pour secteurs non listés.

## FICHIERS CLÉS

```
annemasse-agency/
├── orchestrator.py              # Orchestrator principal (7 agents)
├── dashboard.py                 # Dashboard HTML interactif
├── agents/
│   ├── builder_v2.py            # Générateur landing page (standalone)
│   ├── filmer_v2.py             # Générateur pipeline vidéo (standalone)
│   └── v2_adapter.py            # Adaptateurs Builder/Filmer → orchestrator
├── clients/                     # Assets générés par client
│   └── <slug>/
│       ├── index.html           # Landing page
│       ├── mentions-legales.html
│       ├── key-events.md        # Concept narratif vidéo
│       ├── shots.json           # Prompts seedance
│       ├── vo-script.txt        # Script VO français
│       ├── vo-generate.sh       # Edge TTS → .wav
│       └── build.sh             # ffmpeg → .mp4 9:16
├── state/
│   ├── lead-queue.json          # Queue des leads
│   └── stats.json               # Stats globales
└── logs/
    └── journal-*.json           # Journal WORM hash-chainé
```

## COMMANDES

```bash
python3 orchestrator.py --status          # État du système
python3 orchestrator.py --agent scout     # Discovery
python3 orchestrator.py --agent diagnoser # Scoring
python3 orchestrator.py --agent builder   # Build landing pages
python3 orchestrator.py --agent filmer    # Generate video pipelines
python3 orchestrator.py --full            # Full pipeline (7 agents)
python3 dashboard.py                      # Regénère le dashboard
```
