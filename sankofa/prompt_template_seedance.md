# Seedance 2.5 — Master Prompt Template

> Volé de @YourAlphaMom (1142 likes, 11 août 2026) — le prompt le plus abouti vu à ce jour.
> 30 secondes natives, ZÉRO montage post-production.
> Règle d'or: ce template REMPLACE "Expect Magic" pour la vidéo. En vidéo, on décrit TOUT.

---

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

---

## Template (copier et adapter)

### CAMERA:
[TYPE DE CAMÉRA: DV 16mm / drone / cinema / smartphone / etc.] [AESTHETIC: handheld / tripod / crane / gimbal / etc.] [STYLE DE MOUVEMENT]. Important: [RÈGLES SPÉCIFIQUES — ex: "never show camera setup", "use clean jump cuts", "keep realistic hand shake"].

### LOOK:
[QUALITÉ VISUELLE: grain, blur, noise, bloom, contrast, saturation]. [SKIN TONES: realistic/believable]. [LIGHTING: type et direction].

### STYLE:
[TON: playful/epic/documentary/dark]. [PACING: fast cuts/slow burns/sustained]. [TYPE: vlog/cinematic/historical]. [CONTINUITY DU STYLE: "not a polished commercial, feels real"].

### CHARACTER:
[NOM DU PERSONNAGE] is a [ÂGE] [GENRE] [ORIGINE/ETHNICITÉ — TOUJOURS explicite]. [VISAGE: forme, yeux, nez, bouche, peau, cheveux — précis]. [CORPS: taille, build]. [VÊTEMENTS: détaillés, couleur, coupe]. [ACCESSOIRES]. Looks like [RÉFÉRENCE], not [CONTRE-RÉFÉRENCE].

⚠️ RÈGLE ABSOLUE: Pour Sankofa, TOUJOURS "dark-skinned" ou description ethnique explicite. Pour Baobab, style "3D cartoon character".

### SETTING:
[LIEU PRÉCIS]. [ÉLÉMENTS PRÉSENTS: mobilier, objets, décor]. [ATMOSPHÈRE: calme/animé/sombre]. [PERSONNES EN ARRIÈRE-PLAN: oui/non, combien].

### IMPORTANT CONTINUITY RULES:
The same [character] must remain fully consistent in every shot. No face changes, no hairstyle changes, no outfit changes, no body changes. No extra people appearing [unless specified]. No duplicated limbs. No broken hands. No disappearing objects. No broken equipment. No impossible movements. No camera visible.

### STORYBOARD ([DURÉE TOTALE]s total, [NOMBRE] cuts):

1. (~[DURÉE]s, [ANGLE])
[Action détaillée].
Dialogue: "[texte]"

2. (~[DURÉE]s, [ANGLE])
[Action détaillée].
Dialogue: "[texte]"

[Répéter pour chaque cut]

### FINAL INSTRUCTION:
The result must feel like [TYPE DE CONTENU]. Prioritize [PRIORITÉ 1], [PRIORITÉ 2], [PRIORITÉ 3]. Keep it [ADJECTIFS].

---

## Exemple: Sankofa — Mansa Moussa, Cut 1

### CAMERA:
Cinematic wide-angle establishing shot on a crane rig, slowly descending from above. Smooth, majestic, deliberate motion. Important: no handheld shake, no zoom. The camera move should feel like a documentary about an empire.

### LOOK:
Warm golden-hour light, deep amber and gold tones, subtle film grain, rich saturated colors, cinematic contrast. Realistic skin tones, dark skin glowing in golden light.

### STYLE:
Epic historical documentary. The tone is awe-struck, reverent, majestic. Slow, deliberate pacing. Each frame should feel like a painting.

### CHARACTER:
Mansa Moussa is a dark-skinned West African man in his early 40s. He has a strong, dignified face, sharp cheekbones, a trimmed black beard, deep brown eyes, and a calm expression of absolute power. He wears a golden crown, flowing royal blue and gold robes, and an ornate golden staff. Large gold rings on his fingers. Looks like a mighty emperor, not a warrior.

### SETTING:
A vast sun-drenched palace courtyard in 14th-century Timbuktu. Mud-brick architecture with intricate carvings, gold accents, palm trees, a reflecting pool. Guards with spears line the sides but stand still.

### IMPORTANT CONTINUITY RULES:
The same man must remain fully consistent. No face changes, no outfit changes. No duplicated guards. No disappearing staff. No broken architecture.

### STORYBOARD (30s total, 6 cuts):

1. (~5s, crane descending from above)
The camera descends from the sky to reveal the vast courtyard of the palace. Golden light bathes everything.
Dialogue: none.

2. (~5s, medium tracking shot)
Mansa Moussa walks slowly through the courtyard, staff in hand, robes flowing behind him. Guards bow as he passes.
Dialogue: none.

[... continuer pour les 4 autres cuts ...]

### FINAL INSTRUCTION:
The result must feel like a cinematic historical documentary about the richest man who ever lived. Prioritize majestic scale, golden warmth, consistent character, and believable 14th-century Mali. Keep it epic, dignified, and awe-inspiring.

---

## Anti-patterns (ce qu'il NE FAUT PAS faire)

| Erreur | Pourquoi | Correctif |
|---|---|---|
| Prompt court "Expect Magic" | Seedance hallucine sans structure | 8 sections obligatoires |
| Pas de CONTINUITY RULES | Duplicated limbs, face changes | Liste négative explicite |
| Pas de STORYBOARD | Cuts aléatoires, pas de timing | Cuts numérotés avec durée |
| Pas de dialogue | Gaspi audio natif Seedance 2.5 | Dialogue inclus par cut |
| Character vague | Déformation du visage entre cuts | Character sheet EMBEDDED |
| Pas de FINAL INSTRUCTION | Le modèle perd le fil | Directive summary |

---

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
Parfait pour: voyage d'un personnage à travers plusieurs lieux (Mansa Moussa: palais → désert → Le Caire → retour).

```
Setting Progression
[Location A: description + lighting] → [Location B: description + lighting] → [Location C: description + lighting]
```

- [ ] CAMERA décrit le type, le mouvement, et les règles
- [ ] LOOK décrit grain, couleur, lighting, skin tones
- [ ] STYLE définit le ton et le pacing
- [ ] CHARACTER a une description physique complète + "dark-skinned" explicite
- [ ] SETTING décrit le lieu et les objets présents
- [ ] CONTINUITY RULES a une liste négative explicite
- [ ] STORYBOARD a des cuts numérotés avec durée + angle + action + dialogue
- [ ] FINAL INSTRUCTION résume les priorités
- [ ] Total ≈ 80-120 mots (trop court = hallucination, trop long = confusion)
