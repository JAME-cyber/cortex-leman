# Grid Story Prompting Technique

**Source:** @chrisdadiva tutorial (x.com/i/status/2086018407745396909, 3741 likes, 856 RT, août 2026)
**Validated for:** Nano Banana 2 (image grids), adaptable to Seedream 5.0 Pro

## Concept

Au lieu de générer des images/scènes une par une, un **seul prompt décrit 9 scènes séquentielles** dans une grille narrative. Le modèle génère une grille de 9 panels cohérents (même personnage, même décor, angles/actions différents).

## Avantages

1. **Cohérence personnages** — tous les panels partagent le même rendu car générés en un seul passage
2. **Économie de prompts** — 1 prompt au lieu de 9 séparés
3. **Continuité narrative** — la séquence d'actions est visuellement cohérente
4. **Sélection** — génère 9 options, on garde les meilleures pour animation

## Template de prompt

```
Create a 9-story grid story. [STYLE DESCRIPTION]. 
[CHARACTER DESCRIPTION with visual anchor]. 
Scene 1: [action]. Scene 2: [action]. Scene 3: [action]. 
...jusqu'à 9 scènes...
Keep characters consistent across all 9 panels. 
[lighting/mood/child-friendly modifiers].
```

## Exemple validé (DaDiva — style 3D cartoon)

```
Create a 9-story grid story. 3D cartoon style for children, vibrant colors, 
soft lighting. A colorful African village at the foot of giant baobab trees. 
Anansi, a cute brown spider with big eyes and a tiny Kente cloth hat, 
sneaks through the village sniffing the air. A wise hornbill bird with 
glasses sits on a branch watching. The spider finds a golden palace in 
the distance. He rubs his hands together with a mischievous grin. 
Camera angles: wide village shot, close-up Anansi face, aerial village, 
Anansi sneaking behind huts, hornbill on branch, palace exterior. 
Keep characters consistent across all 9 panels. Child-friendly, not scary.
```

## Workflow de production

1. Générer le character sheet séparément (multi-angle: front, side, 3/4)
2. Pour chaque acte narratif → 1 grid story prompt (9 panels)
3. Sélectionner les 4-5 meilleurs panels par grid
4. Chaque panel sélectionné → Seedance I2V (image-to-video, 10-12s)
5. Concaténer les clips animés selon le script VO

## Usage par projet

| Projet | Grid story适用 | Style |
|---|---|---|
| Baobab Kids | ✅ Principal — contes enfants | 3D cartoon, vibrant |
| Sankofa | Partiel — cohérence multi-scène | Documentaire cinématique |
| Mansa Moussa | Partiel — character consistency entre scènes | Photoréaliste épique |

## Différence vs prompting scène-par-scène

| Approche | Cohérence perso | Coût prompts | Sélection |
|---|---|---|---|
| Scène par scène (Sankofa actuel) | Variable — drift entre clips | 1 prompt/clip | Binaire (garder/jeter) |
| Grid story (9 panels) | Forte — un seul passage | 1 prompt/9 options | Riche (9→4-5 gardés) |

## Nano Banana 2 (Gemini) — Character Sheets GRATUITS

Source: @chrisdadiva tutorial (août 2026). Nano Banana 2 via Gemini génère des character sheets multi-angle **à zéro coût**, contrairement à Seedream (kie.ai, payant).

**Workflow économique:**
1. Nano Banana 2 (gratuit) → character sheets + grid story panels
2. Seedance 2.5 I2V (payant) → animation des panels sélectionnés uniquement

Réduit le coût de production en éliminant la génération d'images payante pour le pre-viz et l'exploration de personnages.

## Self-Insertion Hero Pattern

Source: @0x_fokki (109 likes, août 2026). Étudiant Pékin, $50 Seedance → clip Spider-Man viral.

**Formule:** Photo personnelle → Seedance I2V → la personne devient le héros dans n'importe quel univers.

- Photo = identity lock (remplace le character sheet)
- Seedance = action generator
- CapCut/ffmpeg = finish
- Format reproductible: swap character/location/adventure = variations infinies

Cas d'usage: contenu personnalisé enfants (enfant = héros de son conte), marketing "success story" PME.
