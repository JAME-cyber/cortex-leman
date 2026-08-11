# Gemini Omni — Workflow de génération vidéo T2V (free tier)

## Modèle

- **Type**: Text-to-Video, 10s/clip, 1080p, 24fps
- **Accès**: gemini.google.com (web UI uniquement, pas d'API publique)
- **Free promo**: 10 générations par compte (fenêtre limitée ~48h)
- **Blocage automation**: Google refuse le login headless ("navigateur ou application non sécurisés"). Workflow semi-automatisé obligatoire.

## Workflow semi-automatisé (validé Sankofa/Amanirenas, août 2026)

```
1. Agent écrit les prompts (80-100 mots, anglais)
2. User copie-colle dans Gemini web UI (nouveau chat à chaque prompt)
3. User télécharge la vidéo générée et l'envoie à l'Agent
4. Agent QA: extraction frames ffmpeg → or_vision.py (NVIDIA Llama 3.2 11B, ~5s/frame)
5. Agent verdict: Accepté / Retry / Fail
```

## Règles de prompting CRITIQUES

### Représentation raciale (biais du modèle)
- **TOUJOURS** spécifier "dark-skinned" / "deep brown skin" explicitement
- Sans cette mention, Gemini default = peau claire
- Décrire les détails physiques: "natural curly black hair", "high cheekbones", etc.
- Exemple validé: Prompt 3 v1 (sans "dark-skinned") → peau claire. Retry avec "dark-skinned Nubian" → peau sombre correcte.

### Complexité des scènes
| Type de scène | Taux de succès | Note |
|---|---|---|
| Portrait close-up (1 perso) | ✅ Excellent | Meilleur cas d'usage |
| Establishing landscape (0 perso) | ✅ Bon | Pyramides, Nil, ville |
| Battle (1 action claire) | ✅ Bon | Combat, armée en marche |
| Multi-personnages (≥3) | ⚠️ Dérive | Le modèle perd le sujet à mi-clip |
| Foule + interaction | ❌ Fail | Négociations, cérémonies |
| Documentary (paysage seul) | ✅ Excellent | Pyramides seules au lever du soleil |

### Safety filters (mots déclencheurs)
- "bloody" → blocage immédiat ("dangerous situations")
- "battle" → OK si pas de sang explicite
- "war" → OK dans contexte historique
- Solution: "white linen bandage" au lieu de "bloody bandage", "wounded" au lieu de "bleeding"

### Contamination de contexte
- Les prompts consécutifs dans le même chat se contaminent
- Symptôme: clip N reprend des éléments du clip N-1 (ex: armée romaine apparaît dans un prompt de pyramides seules)
- **RÈGLE: Nouveau chat Gemini entre CHAQUE prompt**

### Retry strategy
- Échec (peau claire, élément manquant) → prompt renforcé avec PLUS de détails physiques, pas moins
- Échec (safety filter) → reformuler les mots déclencheurs
- Échec (dérive multi-personnages) → simplifier à 1 personnage + decor
- Échec (contamination) → nouveau chat + prompt identique

## QA Pipeline (extraction frames + vision)

```bash
# Extraire 4 frames réparties sur le clip
VIDEO="/home/tars/.hermes/cache/videos/video_XXX.mp4"
ffmpeg -y -i "$VIDEO" -vf "select='eq(n\,0)+eq(n\,60)+eq(n\,120)+eq(n\,180)'" -vsync vfr /tmp/gemini_qa_%02d.jpg

# Analyser avec or_vision.py (NVIDIA Llama 3.2 11B, ~5s, gratuit)
python3 ~/.hermes/skills/devops/vision-analysis-fallback/scripts/or_vision.py \
  /tmp/gemini_qa_01.jpg \
  "Specific yes/no questions about: skin color, clothing, props, setting, lighting"
```

## Stratégie de scoring (7 clips solides sur 10 = suffisant pour un Short)

| Score | Critère | Action |
|---|---|---|
| ✅✅ Excellent | Tous les éléments du prompt présents + qualité cinématique | Accepter |
| ✅ Bon | 80%+ des éléments, légers défauts | Accepter |
| ⚠️ Moyen | 60-80% des éléments, ambigu | Accepter comme B-roll |
| ⚠️ Faible | Dérive/incohérence, mais début utilisable | Accepter comme B-roll |
| ❌ Fail | Contamination, safety block, sujet ignoré | Retry avec prompt corrigé |

## Anti-duplication: TOUJOURS session_search avant analyser
Si Tars drop une URL/repo/tweet → session_search(auteur+titre) avant d'analyser. Re-partage souvent contenu déjà traité.
