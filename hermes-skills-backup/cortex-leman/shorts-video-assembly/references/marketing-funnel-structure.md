# Marketing Funnel Structure — Pattern narratif promotionnel

## Problème

Les vidéos promo ont tendance à empiler contenu → prix → outro sans structure persuasive. Résultat: informatif mais pas convaincant. Le pattern "feature dump" (liste d'activités + prix) ne convertit pas.

## Pattern: Funnel 4 phases (Hook → Build → Climax → CTA)

Inspiré de l'analyse d'une pub Club Med (73s, 19M vues, youtube/lQ2yQQYj3m8). L'utilisateur a demandé: "j'aime bien comment elle est orchestrée si on peut reprendre le funnel".

### Structure

| Phase | % vidéo | Objectif | Technique |
|-------|---------|----------|-----------|
| **Hook** | ~15% | Capter l'attention, créer curiosité | Question rhétorique visuelle + stinger brand |
| **Build** | ~50% | Prouver la promesse, défiler les features | 1 feature = 1 cut court (2-5s), mot-clé unique par plan |
| **Climax** | ~15% | Bascule rationnel → émotionnel | Shots plus longs (4-6s), groupe/bien-être, VO émotionnelle |
| **CTA** | ~20% | Action directe | Prix + dates + contact, sobre et clair |

### VO script template (Club Med style)

```
HOOK:   "Et si [audience] [désir transformateur] ?"
BUILD:  "[Feature]. [Bénéfice court]."
        "[Feature]. [Bénéfice court]."
        "[Feature]. [Bénéfice court]."
        "[Feature]. [Bénéfice court]."
CLIMAX: "[Promesse émotionnelle large — amitié, souvenirs, aventure]."
CTA:    "Réservez ! [Dates] [Lieu] [Prix]."
```

**Exemple CES T4 (validé juil. 2026):**
- Hook: "Et si vos enfants voyageaient en Afrique cet été ?"
- Build: "Henné. Des motifs qui racontent des histoires." / "Tambours. L'énergie collective du Cameroun." / "Nature. Baignade au Rhône." / "Contes. Récits somaliens et thé aux épices."
- Climax: "Une semaine d'aventure, d'amitiés et de souvenirs pour la vie."
- CTA: "Réservez vos places ! 10-14 août, Petit-Lancy. 85 CHF / semaine."

### Points critiques

1. **Hook = question rhétorique**, pas une affirmation. La question force l'engagement mental du spectateur.
2. **Build = mots-clés uniques** — chaque plan a UN mot fort (Henné/Tambours/Nature/Contes), pas de phrase complexe.
3. **Climax = shots plus longs** que le build (facteur 1.3-1.5x). Ralentir le rythme de coupe signale "voici l'essentiel".
4. **CTA peut être portée par la VO seule** sur l'outro/sunset — pas besoin d'une card prix séparée si l'outro visuel suffit. L'utilisateur a corrigé: "il faut enlever le dernier clip de prix car on le voit déjà précédemment".
5. **Prix en VO** — intégrer les tarifs dans la narration CTA plutôt que dans une card séparée. Plus fluide, moins répétitif.

### Timing recommandé (~40-50s total)

```
Stinger:    0 - 3.5s    (brand signature)
Hook:       3.5 - 7.5s  (question + visuel)
Build:      7.5 - 28s   (4 segments × 5s, cuts rapides)
Climax:     28 - 35s    (1-2 segments, shots longs)
CTA/Outro:  35 - 45s    (VO prix sur sunset)
```

### Distinction avec le pattern multi-segment standard

- **Pattern standard** (clip-vo-timing.md): Intro → Segment1 → Segment2 → ... → CTA card → Outro
- **Pattern funnel** (ce fichier): Hook question → Build rapide → Climax émotionnel → CTA intégré à l'outro

Le funnel est preferable pour les vidéos **promotionnelles** (conversion, inscription). Le pattern standard reste valable pour les vidéos **informatives** (présentation d'un programme, documentation).

## Implémentation

Voir `templates/build_funnel.py` pour le script de build complet avec:
- VO segments court+punchy (pas de narration longue)
- Slow-mo setpts sur tous les clips (voir clip-vo-timing.md §2)
- Audio separation stinger→VO→musique (voir unified-intro-stinger.md §2)
- Subtitles ASS avec timing par phase
