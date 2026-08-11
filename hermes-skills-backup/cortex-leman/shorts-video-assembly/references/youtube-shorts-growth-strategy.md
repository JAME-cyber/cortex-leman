# YouTube Shorts Growth Strategy

Insights validés via contre-analyse Sonnet 4.6 (OpenRouter, août 2026) sur chaîne Sankofa Histoire (4 vidéos, 0 subs).

## ⚠️ La zone grise algorithmique (60s-3min)

**RÈGLE ABSOLUE :** Sur YouTube, choisir < 60s (Shorts purs, feed dédié) OU > 3min (vidéos longues, monétisation AdSense). JAMAIS entre les deux.

| Durée | Comportement algo | Avantages |
|-------|-------------------|-----------|
| < 60s | Feed Shorts dédié | Distribution gratuite sans audience, viralité rapide |
| 60s-3min | **Zone grise** — ni Short ni longue | **Pire des deux mondes** — pas de feed Shorts, pas de monétisation |
| > 3min | Vidéo longue | AdSense, recommandations sidebar, watch time |

**Diagnostic typique :** vidéos 80-120s à 4-5 vues = probablement dans la zone grise. La correction = recouper en <60s ou étendre en >3min.

## Priorité #1 : Rétention, pas SEO

Avec 0 subs, aucune optimisation SEO/thumbnail/cadence ne fonctionne si le contenu ne retient pas. YouTube distribue une vidéo avec 70% de rétention même sur une petite chaîne. Il ne distribuera jamais une vidéo avec 25% de rétention.

**Workflow de validation :**
1. YouTube Studio → Analytics → Rétention d'audience par vidéo
2. Identifier le point de décrochage exact
3. Si < 40% → problème contenu (hook faible, pas SEO)
4. Si > 60% → problème distribution (appliquer tactiques externes)

## Hooks : les 3 premières secondes sont TOUT

Patterns de hooks validés pour format court historique :
```
"[Fait contre-intuitif] — et pourtant, c'est une histoire vraie."
"En [année], [personnage] a fait quelque chose que personne n'a osé."
"Ce que les manuels scolaires ne t'ont jamais dit sur [sujet]."
```

Le "swipe away rate" (pourcentage de gens qui quittent immédiatement) est le KPI #1 du feed Shorts.

## Distribution externe — les vrais leviers à 0 subs

YouTube ne distribuera pas une chaîne à 0 subs. Il faut apporter le premier trafic soi-même.

| Canal | Pertinence | Notes |
|-------|-----------|-------|
| **TikTok** | ⭐⭐⭐⭐⭐ | Crossposting direct, feed dédié, viralité |
| **Instagram Reels** | ⭐⭐⭐⭐⭐ | Crossposting direct, audience diasporique |
| **WhatsApp** | ⭐⭐⭐⭐ | Canal viral #1 pour audience diasporique africaine |
| **Twitter/X** | ⭐⭐⭐ | Thread + extrait vidéo = impressions organiques |
| **Facebook** | ⭐⭐⭐ | Audience diasporique > Reddit pour cette niche |
| Reddit | ⭐ | Quasi inexistant pour histoire africaine FR |

## Audience diasporique — particularités

- **Mobile-first 85%+** — tout doit être pensé mobile
- **WhatsApp** = canal de partage viral #1 (pas Reddit)
- **Facebook** >> Reddit pour cette audience
- Pensé pour le partage mobile/WhatsApp, pas pour le référencement desktop

## ❌ Conseils obsolètes/dangereux

| Conseil | Verdict |
|---------|---------|
| `#Shorts` dans le titre | ❌ YouTube détecte auto par ratio + durée. Le hashtag pollue le titre. |
| Cadence 1/jour × 30 jours | ❌ Sacrifie qualité/recherche. Algo 2025-26 = watch time, pas cadence brute. |
| Community tab à 100 subs | ❌ Fausse priorité à 0 subs |

## Format 80-120s → Short <60s : plan de coupe

Voir `references/video-recutting-workflow.md` pour le pattern technique complet.

Principe : chaque vidéo est recoupée en gardant le hook + les segments les plus visuels + CTA. Segments de transition et de détail sont coupés. Nouveau CTA TTS généré si l'original contient des références temporelles obsolètes ("Demain", "la semaine prochaine").

## KPIs 30/60/90 jours

| Phase | KPIs |
|-------|------|
| J30 (Validation) | Rétention >55%, 1 vidéo >100 vues, 20-30 subs |
| J60 (Distribution) | CTR >4%, 1 vidéo >500 vues |
| J90 (Scale) | 200-400 subs, 3-4 vidéos >1K vues, 1 source trafic externe stable |

## Contre-analyse comme méthode

Pattern validé : soumettre recommandations à un second modèle (Sonnet 4.6 via OpenRouter) pour contre-analyse critique. Le second modèle identifie les angles morts, conseils dangereux, et priorités manquées que le premier modèle (GLM-5.2) n'a pas vus.

```python
# Pattern via execute_code
import json, os, urllib.request
body = {
    'model': 'anthropic/claude-sonnet-4.6',
    'messages': [{'role': 'user', 'content': prompt}],
    'max_tokens': 4000, 'temperature': 0.7
}
# POST to https://openrouter.ai/api/v1/chat/completions
# Key from ~/.hermes/.env → OPENROUTER_API_KEY
```

Budget : ~$0.01-0.02 par contre-analyse. ROI : éviter des heures de travail sur la mauvaise stratégie.
