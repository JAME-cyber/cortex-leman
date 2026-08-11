---
name: signal-deliberation
description: "Use when vetting new tech via 3 divergent agents."
version: 1.0.0
metadata:
  hermes:
    tags: [veille, deliberation, multi-agent, fan-out, radar, decision]
---

# Signal Deliberation

Évalue un signal entrant (URL, tweet, annonce, outil, pattern) via une délibération multi-agents divergente, puis rend un verdict actionnable. Utilisé automatiquement par les radars cron ET manuellement quand Tars drop une ressource.

## Déclencheurs

- **Manuel:** Tars drop une URL/tweet/news → `signal-deliberation`
- **Automatique:** Radars cron (Video AI Radar, Project Radar) détectent une nouveauté → invoquent la délibération
- **Programmé:** Daily Radar trouve un signal chaud → délibération avant livraison

## Architecture

```
SIGNAL (URL/tweet/news/tool)
    │
    ▼
PHASE 1 — COLLECTE (web_extract/web_search)
    │
    ▼
PHASE 2 — FAN-OUT (3 agents parallèles)
    ├─ AGENT 1: Ingénieur (réalité technique)
    ├─ AGENT 2: Stratège (impact business)
    └─ AGENT 3: Sceptique (risques/pièges)
    │
    ▼
PHASE 3 — SYNTHÈSE + ANTI-SYCOPHANCY GATE
    │
    ▼
PHASE 4 — VERDICT: IMPLEMENTER / SURVEILLER / IGNORER
```

## Projets de référence (contexte agents)

Les agents DOIVENT évaluer le signal contre ces projets actifs:

| Projet | Description | Stack/Pipeline |
|--------|-------------|----------------|
| **Sankofa** | YouTube Shorts histoire africaine (@sankofa-histoire, 4 shorts live) | Seedance 2.5 via kie.ai, ffmpeg, edge-tts, VO fr-FR-HenriNeural |
| **Baobab Kids** | Cartoon 3D enfants (pilote Anansi prêt, en attente) | 3D animation IA, Kamo-1 surveillé |
| **Cortex Leman** | Agents IA PME FR-CH (services récurrents) | Hermes Agent, PRISME, google-reviews-agent, pipeline B2B |
| **AlConst** | Consulting digital Tars (client externe) | Site statique, Stripe, bilingue FR/EN |

## PHASE 1 — Collecte du signal

### Si le signal est une URL
```python
from hermes_tools import web_extract, web_search

result = web_extract(urls=["<URL>"], char_limit=8000)
content = result["results"][0]["content"]

if len(content) < 500:
    search = web_search(query="<mots-clés du signal>", limit=3)
```

### Si le signal est un tweet X
```bash
curl -sL "https://api.vxtwitter.com/<tweet_id>" | python3 -m json.tool
```

### Si le signal est texte libre
Utiliser directement comme input pour les agents.

### Si le signal est une vidéo
```bash
yt-dlp -o "/tmp/signal_video.mp4" --max-filesize 200M "<URL>"
ffmpeg -i /tmp/signal_video.mp4 -vf "select='eq(n\,0)+eq(n\,30)+eq(n\,60)+eq(n\,90)'" -vsync vfr /tmp/signal_frame_%02d.jpg
# Analyser frames via or_vision.py (skill vision-analysis-fallback)
```

**IMPORTANT:** Si le signal provient déjà d'un radar, la Phase 1 est déjà faite. Passer à la Phase 2.

## PHASE 2 — Fan-out (3 agents divergents)

Lancer les 3 agents en parallèle via `delegate_task` en mode batch.

### Agent 1 — L'Ingénieur (réalité technique)

**Prompt:**
```
Tu es un ingénieur technique expert en IA, vidéo, et automatisation.
Stack disponible: Hermes Agent (cron, skills, delegate_task), kie.ai (Seedance 2.5),
ffmpeg, edge-tts, Docker, Python, terminal Linux.

Signal à évaluer: [INSÉRER LE SIGNAL ICI]

Analyse en MAX 10 lignes:
1. Est-ce techniquement implémentable aujourd'hui avec notre stack?
2. Quel effort? (heures/jours/semaines)
3. Y a-t-il des dépendances cachées? (macOS only, hardware spécifique, API fermée, lock-in)
4. Est-ce du vaporware (promesses sans livraison)?
5. VERDICT TECHNIQUE: READY / BETA / VAPORWARE

Sois honnête et précis. Si tu ne sais pas, dis "INCONNU".
```

### Agent 2 — Le Stratège (impact business)

**Prompt:**
```
Tu es un stratège produit. Projets actifs:
- Sankofa: YouTube Shorts histoire africaine (4 shorts live, croissance organique)
- Baobab Kids: Cartoon 3D enfants (pilote prêt, non lancé)
- Cortex Leman: Agents IA PME FR-CH (pre-revenue, pipeline B2B en place)
- AlConst: Consulting digital (site prêt, en attente déploiement)

Signal à évaluer: [INSÉRER LE SIGNAL ICI]

Analyse en MAX 10 lignes:
1. Quel projet en bénéficie le PLUS?
2. Quel avantage concurrentiel concret? (sois spécifique, pas "ça améliore tout")
3. ROI estimé: temps d'investissement vs gain probable?
4. Faut-il se précipiter (fenêtre courte) ou attendre (ça va mûrir)?
5. VERDICT STRATÉGIQUE: HIGH IMPACT / MEDIUM / LOW / DISTRACTION

Challenge l'enthousiasme facile. Si c'est "cool mais inutile", dis-le.
```

### Agent 3 — Le Sceptique (risques et pièges)

**Prompt:**
```
Tu es un sceptique radical et impitoyable. Ton job est de CASSER l'enthousiasme.

Signal à évaluer: [INSÉRER LE SIGNAL ICI]

Analyse en MAX 10 lignes:
1. Est-ce un piège marketing? (Bait: gratuit → payant, open → closed, beta → jamais)
2. Quels risques cachés? (sécurité, privacy, coût caché, dépendance fournisseur)
3. Quelle probabilité que ça meure dans 6 mois? (historique de la boîte, marché)
4. Quel est le WORST CASE SCENARIO si on adopte?
5. Si on IGNORE complètement cette nouveauté, qu'est-ce qu'on perd vraiment?

Sois agressif. Mieux vaut rater une opportunité que courir dans un mur.
```

## PHASE 3 — Synthèse + Anti-sycophancy

### 3a. Synthèse préliminaire

```
SIGNAL: [titre court + lien]

⚙️ TECHNIQUE: [verdict ingénieur — 1 ligne]
🎯 STRATÉGIE: [verdict stratège — 1 ligne]
⚠️ RISQUES: [verdict sceptique — 1 ligne]

CONVERGENCE: [Les 3 agents sont-ils d'accord? Où divergent-ils?]
```

### 3b. Anti-sycophancy gate

```bash
python3 ~/.hermes/scripts/anti_sycophancy.py --file /tmp/signal_synth.txt --model glm-5.2 --json
```

| Score | Action |
|---|---|
| 0-14 | LOW → Synthèse acceptée, passer au verdict |
| 15-39 | CAUTION → Revoir les claims "READY" et "HIGH IMPACT" avec -1 niveau |
| 40+ | CRITICAL → Re-collecter 1 source supplémentaire, redélibérer |

### 3c. Règles de résolution des conflits

| Situation | Résolution |
|---|---|
| 3 agents OK | ✅ IMPLEMENTER — Confiance haute |
| 2 OK + 1 sceptique NO | ⚠️ IMPLEMENTER avec caveat — Noter le risque |
| 1 OK + 2 NO | ⏸️ SURVEILLER — Pas maintenant, revoir dans 30j |
| 3 agents NO | ❌ IGNORER — Skip définitif |
| Ingénieur = VAPORWARE | ❌ IGNORER (override) |
| Stratège = DISTRACTION | ❌ IGNORER (override) |

## PHASE 4 — Verdict final

Format de livraison:

```
📡 SIGNAL: [Titre — max 60 chars]
🔗 [Lien]

⚙️ TECHNIQUE: [verdict — 1 ligne]
🎯 STRATÉGIE: [verdict — 1 ligne]
⚠️ RISQUES: [verdict — 1 ligne]

✅ VERDICT: IMPLEMENTER / SURVEILLER / IGNORER

📋 ACTION: [si IMPLEMENTER — prochaine étape concrète]
           [si SURVEILLER — quoi monitorer et quand revoir]
           [si IGNORER — pourquoi]
```

## Mémoire et apprentissage

### Sauvegarde des verdicts

```python
fact_store(
    action="add",
    category="tool" or "general",
    content="[Signal] — Verdict: [IMPLEMENTER/SURVEILLER/IGNORER] — [raison 1 ligne]",
    tags="signal-deliberation,[projet-impacté],[domaine]"
)
```

Si signal IMPLEMENTER et reste pertinent dans le temps → sauvegarder en skill.
Si signal IGNORER mais revient → re-délibérer avec un 4e agent (opportuniste).

## Limites

- **Pas pour des décisions triviales** — implémenter directement.
- **Pas pour du contenu analytique long** — utiliser `academic-research-pipeline` d'abord.
- **Coût:** ~3000 tokens par délibération. Latence: ~60-90s.

## Anti-patterns

- ❌ Délibérer sur un outil déjà connu
- ❌ Délibérer si le signal est un duplicate (toujours `session_search` d'abord)
- ❌ Lancer les 3 agents si le signal est trivial
- ❌ Ignorer le verdict sceptique
- ❌ Oublier l'anti-sycophancy gate

## Référence: skills utilisés

- **fan-out-fan-in**: décomposition en shards parallèles
- **critical-objective-analysis**: framework d'évaluation factuelle
- **anti-sycophancy** (`~/.hermes/scripts/anti_sycophancy.py`): gate de rigueur
