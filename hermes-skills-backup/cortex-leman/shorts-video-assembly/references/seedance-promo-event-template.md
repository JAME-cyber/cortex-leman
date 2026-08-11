# Seedance Promo Event Template — Pattern G appliqué (événement multi-activité)

Template issu de Culture en Saveur V2 (juil 2026). Prompt Seedance 2.0 qui couvre **toutes** les activités d'un brief événementiel, pas seulement l'activité dominante. Voir Guardrail 2 du skill parent.

## Contexte

Le V1 ne couvrait que la cuisine (activité dominante). L'utilisateur a relevé l'omission ("il manque pas des activités?") — le brief listait 8 activités. Le V2 ci-dessous couvre les 8 avec un shot narratif chacune.

## Structure du prompt (8 beats pour 15s)

Chaque beat = 1 activité du brief, ~2s chacun. L'ordre suit une logique émotionnelle:

| Beat | Activité | Rôle narratif |
|------|----------|---------------|
| 1 | Hook sensoriel (épices) | Capte l'attention sans être encore "l'activité" |
| 2 | Cuisine 3 pays | Activité dominante — posée tôt mais pas monopolisante |
| 3 | Anthropologue / patrimoine | Élargit au-delà de la cuisine |
| 4 | Henné / motifs | Intimité, artisanat |
| 5 | Contes + thé aux épices | Chaleur, tradition orale |
| 6 | Musique (djembe) + bricolage | Énergie, rythme |
| 7 | Visio orphelinat | **Pic émotionnel** — connexion humaine réelle |
| 8 | Sunset collectif | Résolution, identité commune |

**Leçon clé**: l'activité émotionnellement la plus forte (visio orphelinat) va en position 7 (avant-dernier), pas en premier. Le hook est sensoriel (épices), pas narratif.

## Prompt Seedance complet (V2 — validé)

```
Cinematic commercial for a children's African cultural workshop called "Culture en Saveurs".

Opening: extreme close-up of colorful African spices — golden turmeric, deep red paprika, cinnamon sticks — being sprinkled onto a wooden cutting board, warm golden kitchen light, steam rising, shallow depth of field.

Transition to a bright kitchen: diverse children aged 6-10 in colorful aprons joyfully cooking together. A girl with braided hair stirs Egyptian koshari, a boy shapes Cameroonese plantain fritters, another child prepares Somalian sambusa. Their faces show wonder and pride.

Shift to a classroom setting: an anthropologist shows ancient Egyptian artifacts to fascinated children. The kids lean forward excitedly as they examine a pyramid model. A child traces hieroglyphs on papyrus paper with focused concentration.

Transition to an intimate henna scene: a woman gently applies intricate henna patterns on a child's hand. Somali motifs, geometric designs. The child watches in awe.

Cut to a warm circle gathering: children sit on cushions, a storyteller performs with expressive gestures. Somali tales, animal fables. The children listen with wide eyes and laughter. Cups of spiced tea with cardamom and cloves steam softly.

Rhythmic montage: children playing traditional African drums together, hands on djembe, joyful synchronized beats. Children doing crafts — building a pyramid from clay, painting African textile patterns.

Emotional moment: a large screen shows a video call with smiling children in a Cameroon orphanage. The local children wave enthusiastically, exchanging words and gestures across the screen, faces glowing with connection.

Final shot: golden sunset, silhouettes of all children and animators outdoors, arms raised in joy. African textile patterns subtly overlay the frame.

Style: ultra-realistic, warm golden tones with vibrant African colors (terracotta, saffron, deep green, indigo). Cinematic lighting, high-end commercial quality, 8K, shallow depth of field, smooth camera movements. Joyful, heartwarming, educational atmosphere. Premium cultural event commercial.
```

## Params Seedance

```json
{
  "model": "bytedance/seedance-2",
  "input": {
    "prompt": "<above>",
    "generate_audio": true,
    "resolution": "720p",
    "aspect_ratio": "9:16",
    "duration": 15,
    "nsfw_checker": false
  }
}
```

- **Coût**: ~615 crédits (~$0.62)
- **Temps génération**: ~5 min (queue + render)
- **Output**: 720×1280, 15s, H.264 + AAC

## Pipeline complet (intro + Seedance + end card)

```
[Intro card PIL 1.5s] → [Seedance 15s] → [End card PIL 2.5s] = ~19s total
```

Voir section "Promo Seedance pattern" dans le SKILL.md parent pour les détails ffmpeg (silent audio, concat re-encode, end card structure).

## Référence implémentation

- Script génération: `~/culture-en-saveur/scripts/test_seedance_promo_v2.py`
- Script cards: `~/culture-en-saveur/scripts/create_cards.py` + `create_end_card.py`
- Output final: `~/culture-en-saveur/renders/promo_final_v2.mp4` (19.2s, 4.9 MB)

## Adaptation à d'autres événements

Pour réutiliser ce template sur un autre événement:
1. Extraire la liste complète d'activités du brief client (grep)
2. Mapper chaque activité à un beat narratif (~2s)
3. Identifier le pic émotionnel → le placer en avant-dernier
4. Garder un hook sensoriel en beat 1 (pas narratif)
5. Terminer par un shot collectif de résolution
6. La palette de couleurs doit refléter l'identité visuelle du client (extraire du logo)
