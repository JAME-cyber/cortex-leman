---
name: ai-film-production-bible
description: "Use when making AI videos. Higgsfield production bible."
---

# AI Film Production Bible

Source : Higgsfield "Cully Hill Boys" brief — feature film généré à 100% en AI.
$2M de R&D, 137 plans, 600 assets, 473K générations. 100% open-source (prompts + assets publics).
Scales down to team of one. tweet: x.com/i/status/2086868445543707065

## 1. CHARACTER SHEETS (Assets)

### Format
- **3 panels en 1 image** : corps entier frontal + corps entier dos + gros plan portrait
- Portrait en **three-quarter view** (visage à 2 angles : front + côté)
- Le prompt le dit explicitement : "the same person, consistent across all panels"

### Règles critiques
- **Retirer la tête** des panels full-body → seule source du visage = portrait rapproché
- **Fond** : gris neutre uni, lumière douce, PAS d'ombres dures
- **Bannir le mot "studio"** → le modèle dessine un vrai studio avec lumières/stands
  - Écrire à la place : "no studio, no equipment, no walls"
- **Bannir le rim light** → l'edge glow se propage à toutes les scènes
- **Mains vides** sur le sheet → chaque objet est son propre asset

### States & Versions
- Chaque état = un asset séparé (pas une note)
- Exemple : Cal propre → Cal mouillé → Cal ensanglanté = 3 assets
- Variante = modifier seulement ce qui change, garder le reste intact
- Jamais overwrite : versionner (@char_CB_Cal_v1, _v2, _v3)

### Naming convention
```
@char_PROJECT_name_v#         — personnage
@loc_PROJECT_scene_v#         — lieu
@prop_PROJECT_scene_v#        — accessoire
```

### Stress test
- 10 générations (actions, shot sizes, lieux différents)
- Reconnaissable dans 10/10
- Tester perso + lieu ENSEMBLE (ils s'influencent)

## 2. LOCATIONS

- Générer en **three-quarter view** (pas frontal — frontal = wallpaper plat)
- **1 anchor** par lieu : colonne, lampe, fauteuil
- **1 logique lumière** : 1 source, 1 direction d'ombres
- Pas de personnes, pas d'armes dans le plate
- Langage de vraies surfaces : rouille, fissures, scotch, traces de doigts

### Reverse angle hack
- Générer vidéo du lieu vide (camera walk-through)
- Screenshot l'angle voulu → Seedream/Nano Banana pour améliorer texture
- 1 image → kit lieu complet

## 3. LE SQUELETTE 15 BLOCKS

Chaque plan sérieux suit cet ordre EXACT :
```
SCENE CONTEXT · ACTIVE REFERENCES · LOCATION MAP · FIRST FRAME AND SPATIAL 
BLOCKING · FORMAT MODE · OPTICS · CAMERA · ACTION TIMING · PHYSICS · 
LIGHTING · AUDIO · CHARACTER ACTING · STYLE · QUALITY · POSITIVE CONSTRAINTS
```

**PAS de block négatif.** Une interdiction s'écrit comme le résultat désiré :
- ❌ "does NOT fall on his back"
- ✅ "falls on his stomach"

## 4. OPTICS (en degrés, pas mm)

Ladder : 180° · 135° · 107° · 84° · 63° · 47° · 29° · 18° · 12° · 8°
- Zone native fiable : **29°–84°**
- Le contenu décide la lentille, pas le nombre
- 1 lentille par shot, FOV change only on hard cuts

## 5. GÉOGRAPHIE

### Master shot
- Wide avec blocking fixé, ~1 seconde, pas de répliques ni action
- Le modèle "photographie" l'arrangement → le retient pour les shots suivants
- Sans lui : les personnages se téléportent/changent de place

### Spatial map
- Plan d'étage en quelques lignes, écrit 1 fois par scène
- Collé IDENTIQUE dans chaque shot de la scène
- Tie les corps à des landmarks visibles (lampe, 2e rang de chaises, porte)
- Dire de quel côté est la caméra + quelle ligne elle ne traverse jamais

## 6. ACTING

### Behavior, not feelings
- Scène vivante = perso qui VEUT quelque chose, obstacle, lutte
- Changer la tactique : plaisante → échec → pousse → échec → supplie
- Chaque changement = événement visible (pause, posture, tempo)

### Physics, not adjectives
- ❌ "sad", "angry", "shocked" → shallow
- ✅ Muscles : tremblement, mâchoire serrée, pommettes tendues, expiration nasale
- + 1 ligne de monologue intérieur (non dit) → micro-expressions

### Micro-events
- Phased blinking : "1 lazy blink → quick DOUBLE-BLINK → 1 HARD reset-blink"
- Toujours écrire la direction du regard
- 1 micro-event visible toutes les 1-2 secondes en plan statique

## 7. VOIX

- Pas un asset : un set de conditions écrites (register, timbre, tempo, accent)
- **Collé verbatim** dans chaque prompt — JAMAIS changer un synonyme
- Changer le wording élargit ce que le modèle sample → dérive vocale
- 1 clip = 1 locuteur, 1 ligne courte
- **Speech count lock** : verrouiller le nombre EXACT de mots parlés dans le plan.
  Sans lock, le modèle ajoute des mumbles ou des lignes dans une autre langue.
  Exemple : "SPEECH COUNT LOCK: exactly ONE line — \"Pull it, Oli.\" at ~6.0s"

## 8. LOOK & COULEUR

- Décidé en PRE-PROD, pas en post
- Visual bible avant le 1er shot
- Frame = 80-85% base field, 10-15% accents, 5% counter-note
- L'accent = un objet avec source réelle (porte verte, lampe sodium)

## 9. RÈGLES QUI SAUVENT DES GÉNÉRATIONS

| Problème | Solution |
|---|---|
| Modèle dessine l'interdit | Bannir nom par nom + contrainte exacte |
| Hauteur incorrecte | "NOT taller by a single centimeter; if in doubt, shorter" |
| Objets dupliqués | Écrire count frame par frame |
| Émotion caricaturale | Clamper : "rage-twisted = failed; soft beaming = failed; deadpan = failed" |
| Action complexe bloquée | Ouvrir le prompt par l'action déjà en cours |
| Foule >15 personnes | Collapse en 3-5 figures → bodies pressed against stage |
| Portes s'ouvrent seules | Lock : "every door VISIBLE stays SHUT and MOTIONLESS" |
| Le modèle tire vers le présent | **Epoch lock** : "nothing in frame is newer than [YEAR]". Le modèle ajoute des smartphones/écrans/voitures modernes par défaut. Pour Sankofa/Baobab : "nothing newer than 1300 CE, no plastic, no metal tools, no glass windows" |

### Règle d'époque (Epoch Lock) — CRITIQUE pour Sankofa/Baobab
- L'année n'est pas déco, c'est une **hard rule**
- Le modèle tire l'image vers "aujourd'hui" par défaut
- Sans epoch lock : un figurant tient un iPhone dans l'Empire du Mali
- Application : "nothing in frame is newer than [year], no smartphones, no glowing screens, no modern cars, no plastic, no synthetic fabrics"

## 10. MUSIC / LIP-SYNC

- Modèle ne peut pas rapper → track enregistré D'ABORD
- Couper en blocks ~12s (cuts sur respirations, jamais mid-word)
- Chaque block = fichier vidéo image noire + audio du morceau
- Le fichier EST la chanson : "his mouth carves EVERY syllable of the Video 1 vocal"
- LIP-SYNC LOCK : frame-accurate, pas de drift

## 11. PRODUCTION WORKFLOW

- Générer en batches, changements chirurgicaux (1 ligne change, reste word-for-word)
- Log de versioning obligatoire (Cully Hill Boys = 137 entrées: version, ce qui change, verdict)
- L'edit tourne EN PARALLÈLE de la génération
- Cuts plus agressifs que ressenti → trim 0.5s début et fin de chaque clip
- "SFX only. No music." obligatoire dans chaque prompt
- Post-prod : polish pass frame par frame AVANT color
- Couleur = unification d'abord

## 12. TEXT-TO-VIDEO ONLY (Hard Rule)

- **Pas de starting frame, pas d'image-to-video**
- Chaque plan naît des références + texte : les assets portent l'image, le wording porte la géométrie
- C'est plus difficile, mais c'est ce qui rend chaque plan cohérent avec l'univers
- L'I2V importe une image externe qui peut casser la cohérence stylistique

## 13. HYBRID FALLBACK (quand l'IA échoue)

- Certaines actions ne génèrent pas : combat rapproché, deux corps en contact physique, lutte pour une arme
- Symptômes : membres fusionnés, armes qui disparaissent/réapparaissent, objets qui changent de main
- **Solution hybride** : filmer en réel (stunt performers, b-roll) et intégrer en post
- Pas un échec — c'est la méthode de production professionnelle ($2M film l'utilise)
- Application Sankofa : scènes de combat (Nzinga vs Portugais, Amanirenas) → b-roll réel si Seedance échoue

## APPLICATION CORTEX LEMAN

### Sankofa (Shorts verticaux)
- Simplifier à 6-8 blocks essentiels (format court)
- Character sheets = CRITIQUE (1 héros par vidéo)
- 1 lieu par Short
- Optics : rester en zone native 29-84°
- **Epoch lock obligatoire** : "nothing newer than [year CE]" selon l'épisode
- **Speech count lock** sur chaque plan avec VO
- **Hybrid fallback** : combat rapproché → b-roll réel

### Baobab Kids (Long-form 5-10min)
- Full 15-block skeleton applicable
- Character consistency = priorité #1
- Visual bible par épisode (monde = conte africain)
- **Epoch lock critique** : contes africains = objets naturels uniquement
- **T2V-only** : cohérence du style cartoon garanti

### Stack mapping
| Block brief | Notre outil |
|---|---|
| Character sheets | Higgsfield (Nano Banana 2, illimité) |
| Location plates | Higgsfield |
| Video generation | Flova (Baobab) / Higgsfield (Sankofa) |
| Prompts | Claude via Hermes |
| Assembly | ffmpeg |
| Combat/stunts (fallback) | B-roll réel + post-prod |
