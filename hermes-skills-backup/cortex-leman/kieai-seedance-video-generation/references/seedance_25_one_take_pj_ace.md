# Seedance 2.5 — One-Take Filmmaking (PJ Ace Playbook)

**Source**: @PJaccetturo (PJ Ace, Genre.ai, 300M+ vues), X Article, Aug 4 2026
**Engagement**: 413 likes, 41 RT
**Article**: x.com/i/article/2084475675810189313

PJ Ace dirige la #1 agence AI-native. Sa thèse: le format viral 2026 = **30s, un seul plan, zéro cut**. Seedance 2.5 fait du single-shot 4K continu avec audio natif en un pass.

## La Formule (5 Parties)

```
Subject + Action + Camera + Lighting + Style (+ Audio)
```

En oublier une = le modèle improvise = drift.

### 1. Subject — précis
Pas "a woman" → "a woman in her thirties with short dark hair, wearing a beige trench coat."
Attributs concrets (âge, vêtements, couleur, matière, expression) = ancrages qui tiennent sur 30s.
Pour produits: nommer objet + matière + finition.

### 2. Action — un arc clair
Décrire un mouvement avec début et fin: "she picks up the cup, takes a sip, and sets it down."
UN arc continu > liste de jump-cuts. Si plusieurs beats → séquence fluide, pas événements séparés.

### 3. Camera — shot + move
Spécifier: shot size (wide, medium, close-up) + angle (eye-level, low, overhead) + movement (voir syntax ci-dessous).

### 4. Lighting — mood
"Golden hour backlight", "soft overcast daylight", "moody neon from the left", "high-key studio lighting".
Seedance 2.5 output 4K 10-bit → le détail de lumière survive dans le fichier final.

### 5. Style — look global
"cinematic, shallow depth of field, 35mm film grain", "clean commercial product look", "documentary handheld", "anime cel-shaded".

### 6. Audio (optional, 2.5 only)
Décrire le son attendu. Le modèle génère l'audio synchronisé.

## Camera Movement Syntax

Combiner **max 1-2 moves** par clip. Plus = muddy/unstable.

| Move | Effet | Example |
|------|-------|---------|
| **Dolly in / push in** | Révélation, emphasis | "slow dolly-in to a close-up" |
| **Dolly out / pull back** | Révéler le contexte | "pull back to reveal the full room" |
| **Pan left / right** | Pivot horizontal | "smooth pan right across the skyline" |
| **Tilt up / down** | Pivot vertical | "tilt up from the shoes to the face" |
| **Orbit / arc** | Cercle autour du sujet | "slow 180-degree orbit around the car" |
| **Crane up / down** | Élévation/descente | "crane up from street level to rooftop" |
| **Tracking / follow** | Suit un sujet en mouvement | "tracking shot following the runner" |
| **Handheld** | Shake naturel, docu | "handheld documentary feel" |
| **Static / locked-off** | Aucun mouvement, produit/interview | — |

Toujours paupier avec un mot de vitesse: "slow", "smooth", "fast".

## 10 Prompts Copy-Paste (extraits du guide)

### Product reveal
> A matte black wireless speaker rotating slowly on a white pedestal, water droplets beading on its fabric grille. Slow 360-degree orbit, then a gentle dolly-in to the logo. Clean high-key studio lighting, soft reflections. Premium commercial product look, 4K, crisp detail. Subtle ambient electronic hum.

### Cinematic character intro
> A detective in a long coat steps out of the rain into a dim doorway, water dripping from the brim of his hat, looking off-screen. Slow dolly-in from a wide shot to a medium close-up. Moody blue night light with a single warm streetlamp. Noir cinematic look, film grain. Rain ambience and distant thunder.

### Nature / B-roll
> Morning mist drifting over a pine forest valley as the sun breaks through the trees. Slow crane up revealing the layered mountain ridges beyond. Warm golden-hour backlight, volumetric god rays. Cinematic documentary look, deep 4K detail. Birdsong and a soft breeze.

### Real estate walkthrough
> A bright modern living room with floor-to-ceiling windows and minimalist furniture. Smooth forward tracking shot gliding from the entryway through to the balcony view. Natural midday light, airy and clean. Architectural-tour look, sharp 4K detail.

## Application Sankofa / African Heroes

Le format one-take 30s est l'évolution naturelle des Shorts actuels (fragments 10s montés).

| Scène Sankofa | Application One-Take |
|---------------|----------------------|
| Mansa Moussa au Caire | Tracking shot suivant la caravane à travers le marché, un seul plan continu |
| Reine Nzinga en audience | Slow dolly-in sur le trône, du général au visage |
| Bataille d'Adoua | Crane up révélant l'armée éthiopienne depuis les collines |
| Tombouctou savants | Orbit autour des manuscrits, lumière dorée |

**Seedance 2.5 disponible sur kie.ai depuis août 2026** (confirmé 11 août). Pricing: 720p T2V $0.315/s, 720p I2V $0.190/s, 480p T2V $0.140/s, 480p I2V $0.085/s. High-tier top-up = -10% supplémentaire. Features: 30s max, 4K natif, 50 refs multimodales, first/last frame chaining, generate_audio natif, 3D white-model. URL: https://kie.ai/seedance-2-5

## Différence vs Patterns Existants

| Pattern existant | Ce qu'ajoute PJ Ace |
|------------------|---------------------|
| #15 (epic escalation 6-shot) | One-take = UN plan, pas 6 cuts. Plus dur mais plus premium |
| #30 (imperfect cinema) | PJ Ace formule les 5 couches de façon explicite et reproductible |
| #28 (JSON storyboard Kling) | One-take = pas besoin de storyboard multi-scènes, juste 5 couches dans un prompt |

Le one-take est le **format le plus rapide à produire** (1 prompt = 1 clip fini) et le **plus premium visuellement** (continuité spatiale parfaite).
