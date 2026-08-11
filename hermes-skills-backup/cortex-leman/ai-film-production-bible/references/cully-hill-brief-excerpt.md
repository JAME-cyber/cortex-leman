# Cully Hill Boys — Brief Original (Extrait)

Source : https://higgsfield.ai/original-series/cully-hill-boys/full-film
Film AI généré à 100% via Higgsfield/Seedance. 137 plans, 600 assets.

## Logline
Action-comedy : 3 rappeurs londoniens ratés qui, en voulant faire leur clip,
tombent sur £2M de drogue dans une coque de bateau. Tous les jours suivent.

## Outils utilisés
- **Seedance** : chaque plan vidéo + speech
- **Soul Cinema** : character sheets (visages)
- **Seedream + Nano Banana** : edits, reverse angles, retouches
- **Claude** : prompts (2 chats séparés — un pour images, un pour vidéo)
  - Raison du split : "the rules of one job poison the other"
  - Chat images : flat light + anti-CG wording
  - Chat vidéo : FOV en degrés + motivated light

## Pipeline en bref
1. Script → breakdown en shotlist (chaque shot = une card)
2. Card : SCENE CONTEXT → ACTIVE REFERENCES → LOCATION MAP → FIRST FRAME → 
   FORMAT → OPTICS → CAMERA → ACTION TIMING → PHYSICS → LIGHTING → AUDIO → 
   CHARACTER ACTING → STYLE → QUALITY → POSITIVE CONSTRAINTS
3. Pre-prod : Character sheets + Location plates (assets)
4. Stress test : 10 générations par perso
5. Production : batches chirurgicaux + versioning log
6. Edit parallèle à la génération
7. Post-prod : polish → couleur → son

## Exemple de prompt complet (Scene 102F)

```
OPTICS: 200mm long telephoto (FOV ≈12°) — heavy compression, SHALLOW depth 
of field; a tight CLOSE-UP two-shot of the two lads' faces, corridor 
compressed and soft behind.

CAMERA: ONE continuous shot on a BREATHING HANDHELD — a calm living float 
(SETTLE feel) on Cal & Horace, who watch OLI off-screen behind the camera; 
their eyelines sit just BESIDE and slightly ABOVE the lens — NEVER into the 
lens. When they leave, the CAMERA STAYS PUT — no pan, no follow.

LIGHTING: overhead cool-white FLUORESCENT box-fixtures, cool downward pools; 
cold cyan-teal field, red-brick + white-painted brick; lone warm note = small 
dull-RED FIRE-EXIT glow deep behind them.

REFERENCES
@loc_CB_commons_backstage: cool-white fluorescent, white-painted brick + red 
brick walls, WHITE DOOR (SHUT), dark column mid-corridor, dark-GREEN fire-exit 
doors (SHUT). Controls geometry/materials/light/atmosphere ONLY — not framing.

@char_CB_Kel (CAL — beaten, frame-LEFT): late-20s, thin/exhausted, messy dark 
hair, stubble, FACE scrapes + scalp HEAD WOUND, BLOODIED dirty white tee, grey 
cargo trousers, blue trainers. The TALLER of the two. 100% matches.

@char_CB_Horace (HORACE — frame-RIGHT): younger man, curly black hair, glasses, 
light beard; GREEN cropped jacket over navy tee, baggy grey jeans, olive 
trainers; ~10 CM SHORTER than Cal. 100% matches.

THE SHOT
0.0s–3.0s — tight two-shot: CAL (frame-LEFT, taller) and HORACE (frame-RIGHT) 
watch OLI (OFF-SCREEN). At ~1.5s first unseen kick → faces SOUR.
3.0s–6.0s — ~4.0s second unseen kick fails → CAL heavy SIGH, hand down face.
6.0s–8.5s — HORACE: "Pull it, Oli." — tiny eye-roll. NOBODY speaks after.
8.5s–11.0s — ~9.0s unseen door opens → both SILENT, tiny relieved nods.
11.0s–13.5s — exchanged look → both walk PAST camera → camera STAYS PUT.

POSITIVE LOCKS
HEIGHT RULER: Cal TALLER. OFF-SCREEN LOCK: Oli NEVER visible. IN-FRAME DOORS 
LOCK: every door SHUT + MOTIONLESS. EYELINE LOCK: beside lens, NEVER into it. 
SPEECH COUNT LOCK: exactly ONE line — "Pull it, Oli." at ~6.0s. Colour 60:30:10.
```

## Locks utilisés (~150 total, ~80 se terminent par "= failed take")
- HEIGHT LOCK
- OFF-SCREEN LOCK  
- IN-FRAME DOORS LOCK
- EYELINE LOCK
- SPEECH COUNT LOCK
- EVENT TIMECODES
- LIP-SYNC LOCK (HARD)
- MOUTH OWNERSHIP
- MANNER LOCK (comportement fixé par perso, collé verbatim)
