# Master Prompt Template — Seedance 2.5

> Volé de @YourAlphaMom (1142 likes, 11 août 2026) — le prompt vidéo IA le plus abouti vu à ce jour.
> 30 secondes natives, ZÉRO montage post-production.
> Source: x.com/i/status/2086883879705571790

## Règle d'or

Ce template REMPLACE "Expect Magic" pour la vidéo. En vidéo, on décrit TOUT.

## Structure (8 sections obligatoires)

```
CAMERA:     Type caméra + aesthetic + mouvement + règles de transition
LOOK:       Qualité visuelle, texture, grain, couleur, skin tones
STYLE:      Ton, mood, pacing, type de contenu
CHARACTER:  Description physique EXHAUSTIVE + vêtements + "looks like X, not Y"
SETTING:    Environnement détaillé, objets présents
CONTINUITY: Anti-hallucination EXPLICITE (liste négative)
STORYBOARD: Cuts numérotés (~3s chacun) avec angle + action + dialogue
FINAL:      Directive summary (priorités + ton général)
```

## Variantes de structure

### A) STORYBOARD détaillé (épique/historique — Sankofa)
Cuts longs (~5s), descriptions riches, pas de dialogue synchronisé sauf voix off.

### B) SEQUENCE punchy (vlog/short — Baobab Kids, contenu social)
Cuts courts (~2-3s), descriptions courtes numérotées, dialogue direct.

### C) VOICEOVER mode (day-in-the-life, documentary)
Pas de dialogue lip-sync. Audio = narration off-camera par-dessus les images.
```
(~3s, [ANGLE])
[Action détaillée].
VOICEOVER ([CHARACTER]): "[texte]"
```

### D) SETTING PROGRESSION (voyage/épopée)
Le lieu change à chaque cut. L'éclairage change aussi (warm → cool → intense).
```
Setting Progression
[Location A: description + lighting] → [Location B: description + lighting] → [Location C: description + lighting]
```

## Anti-patterns

| Erreur | Pourquoi | Correctif |
|---|---|---|
| Prompt court "Expect Magic" | Seedance hallucine sans structure | 8 sections obligatoires |
| Pas de CONTINUITY RULES | Duplicated limbs, face changes | Liste négative explicite |
| Pas de STORYBOARD | Cuts aléatoires, pas de timing | Cuts numérotés avec durée |
| Pas de dialogue | Gaspi audio natif Seedance 2.5 | Dialogue inclus par cut |
| Character vague | Déformation du visage entre cuts | Character sheet EMBEDDED |
| Pas de FINAL INSTRUCTION | Le modèle perd le fil | Directive summary |

## Références (autres tweets @YourAlphaMom)

- CHASE day-in-the-life (357 likes, x.com/i/status/2084728365668348364): VOICEOVER + SETTING PROGRESSION
- MILA backstage (227 likes, x.com/i/status/2085428157495283935): SEQUENCE format (storyboard court, punchy)
- GTA6 fake leak (334 likes, x.com/i/status/2069466868528869800): Hook trompeur viral ("Leak? Non, IA")

## Benchmark multi-modèle (YourAlphaMom)

- Seedance 2.0/2.5 = ROI action/scènes complexes (1-4 tentatives)
- Gemini Omni Flash = meilleur en text rendering
- Veo 3.1 = dégradation constante
- Kling 3.0 = character inconsistency en mouvement
