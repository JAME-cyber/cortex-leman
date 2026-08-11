# Seedance 2.5 — Master Prompt Structure (8 Sections)

> Source: @YourAlphaMom (Alpha Mom), tweet 2086883879705571790, 1142 likes, 11 août 2026.
> Le prompt vidéo IA le plus abouti observé. 30s natives SANS montage post-production.
> Règle d'or: en vidéo, on décrit TOUT. "Expect Magic" ne s'applique PAS ici.

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

## Section par section

### CAMERA
Type de caméra (DV 16mm / drone / cinema / smartphone / gimbal). Aesthetic de mouvement (handheld / tripod / crane). Règles spécifiques: "never show camera setup", "use clean jump cuts", "keep realistic hand shake", "delayed autofocus", "occasional motion blur".

### LOOK
Grain, blur, noise, bloom, contrast, saturation. Skin tones (realistic/believable). Lighting type et direction.

### STYLE
Ton (playful/epic/documentary/dark). Pacing (fast cuts/slow burns/sustained). Type (vlog/cinematic/historical). Continuité du style: "not a polished commercial, feels real".

### CHARACTER
⚠️ RÈGLE ABSOLUE Sankofa: TOUJOURS description ethnique explicite ("dark-skinned West African man").

Nom, âge, genre, origine/ethnicité. Visage: forme, yeux, nez, bouche, peau, cheveux. Corps: taille, build. Vêtements: détaillés, couleur, coupe. Accessoires. "Looks like [référence], not [contre-référence]".

### SETTING
Lieu précis. Éléments présents: mobilier, objets, décor. Atmosphère: calme/animé/sombre. Personnes en arrière-plan.

### IMPORTANT CONTINUITY RULES (anti-hallucination)
Liste négative EXPLICITE — c'est ce qui empêche les hallucinations:
- "The same [character] must remain fully consistent in every shot."
- "No face changes, no hairstyle changes, no outfit changes, no body changes."
- "No extra people appearing [unless specified]."
- "No duplicated limbs. No broken hands."
- "No disappearing objects. No broken equipment."
- "No impossible movements. No camera visible."

### STORYBOARD
Cuts numérotés avec ~durée par cut, angle caméra, action détaillée, ET dialogue.
Format standard:
```
1. (~3s, arm's-length selfie)
[Action détaillée].
Dialogue: "[texte]"
```

### FINAL INSTRUCTION
Directive summary: "The result must feel like [TYPE]. Prioritize [P1], [P2], [P3]. Keep it [adjectives]."

## 4 Variantes de structure

### A) STORYBOARD détaillé (épique/historique — Sankofa)
Cuts longs (~5s), descriptions riches, pas de dialogue synchronisé sauf voix off.

### B) SEQUENCE punchy (vlog/short — Baobab Kids, contenu social)
Cuts courts (~2-3s), descriptions courtes numérotées, dialogue direct.
Source: @YourAlphaMom MILA backstage tweet (227 likes).

### C) VOICEOVER mode (day-in-the-life, documentary)
Pas de dialogue lip-sync. Audio = narration off-camera par-dessus les images.
```
(~3s, [ANGLE])
[Action détaillée].
VOICEOVER ([CHARACTER]): "[texte]"
```
Source: @YourAlphaMom CHASE tweet (357 likes).

### D) SETTING PROGRESSION (voyage/épopée)
Le lieu change à chaque cut. L'éclairage change aussi (warm → cool → intense).
```
Setting Progression
[Location A: description + lighting] → [Location B: description + lighting] → [Location C: description + lighting]
```
Parfait pour: Mansa Moussa (palais → désert → Le Caire → retour).

## Patterns viraux observés

| Pattern | Source | Likes | Application |
|---|---|---|---|
| Hook trompeur "Fake leak?" | GTA6 tweet | 334 | Sankofa: "Archive découverte? Non, IA" |
| DV camcorder aesthetic | Gym vlog | 1142 | Authenticité, nostalgie |
| Voiceover off-camera | CHASE tweet | 357 | Storytelling riche sans lip-sync |
| Setting progression | CHASE tweet | 357 | Voyage multi-lieux |

## Anti-patterns

| Erreur | Correctif |
|---|---|
| Prompt court "Expect Magic" | 8 sections obligatoires |
| Pas de CONTINUITY RULES | Liste négative explicite |
| Pas de STORYBOARD | Cuts numérotés avec durée |
| Pas de dialogue/voiceover | Gaspi audio natif Seedance 2.5 |
| Character vague | Character sheet EMBEDDED |
| Pas de FINAL INSTRUCTION | Directive summary obligatoire |

## Check-list avant génération

- [ ] CAMERA décrit le type, le mouvement, et les règles
- [ ] LOOK décrit grain, couleur, lighting, skin tones
- [ ] STYLE définit le ton et le pacing
- [ ] CHARACTER a une description physique complète + ethnicité explicite
- [ ] SETTING décrit le lieu et les objets présents
- [ ] CONTINUITY RULES a une liste négative explicite
- [ ] STORYBOARD a des cuts numérotés avec durée + angle + action + dialogue
- [ ] FINAL INSTRUCTION résume les priorités
- [ ] Total ≈ 80-120 mots minimum (trop court = hallucination)
