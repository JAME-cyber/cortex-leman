# Mansa Moussa — Prompts Seedance 2.5 (kie.ai)

**Modèle**: bytedance/seedance-2-5 sur kie.ai
**Format**: Vertical 9:16, 720p, 11 clips
**Style**: Documentaire historique cinématique, ton chaud/doré
**Voice**: fr-FR-HenriNeural, rate -5%, pitch -5Hz (déjà générée: vo_mansa.mp3, 93.7s)
**Audio natif**: generate_audio=true sur clips ambiant (pas sur clips avec VO par-dessus)

---

## STRATÉGIE CHARACTER CONSISTENCY (nouveau 2.5)

Seedance 2.5 supporte **50 références multimodales**. On utilise 2-3 refs de personnage par clip.

### Étape 0 — Générer le character sheet Mansa (AVANT les clips)

**Prompt Seedream 5.0 Pro** (kie.ai, image-to-image) pour créer 3 références:
```
Character sheet of Mansa Moussa, a powerful dark-skinned West African king in his 40s, 
short beard, strong jaw, dignified expression. Wearing a golden crown, royal blue and 
gold robes with intricate Malian patterns. Three angles: front view, profile, three-quarter. 
Neutral studio background. Cinematic lighting, ultra-detailed, 4K.
```
→ Sauver comme `mansa_ref_front.jpg`, `mansa_ref_profile.jpg`, `mansa_ref_3q.jpg`

Ces 3 images seront passées comme `reference_image_urls` dans CHAQUE clip où Mansa apparaît.

---

## CHAINING STRATEGY (nouveau 2.5)

**first_frame_url / last_frame_url** = continuité visuelle entre clips connectés.

| Clip → Clip | Chain | Méthode |
|---|---|---|
| 2 (Trône) → 3 (Mines) | ❌ Non — coupe narrative | Cuts normaux |
| 3 (Mines) → 4 (Caravane) | ✅ Oui — l'or devient la caravane | last_frame de 3 → first_frame de 4 |
| 4 (Caravane) → 5 (Le Caire) | ✅ Oui — caravane entre dans la ville | last_frame de 4 → first_frame de 5 |
| 7 (Prière) → 8 (Tombouctou) | ✅ Oui — coucher de soleil → aube construction | last_frame de 7 → first_frame de 8 |
| 8 (Construction) → 9 (Université) | ✅ Oui — même lieu, temps qui passe | last_frame de 8 → first_frame de 9 |
| 10 (Carte) → 11 (Héritage) | ❌ Non — rupture symbolique | Cuts normaux |

---

## CHAPITRE 1: L'EMPIRE (0-18s)

### Clip 1 — Carte de l'Empire du Mali (0-4s, durée: 4s)
**Refs**: Aucune (paysage pur)
**Audio natif**: Non (VO par-dessus)
```
Cinematic high-altitude aerial shot descending toward the Mali Empire in 1312. 
Vast golden West African savanna, the Niger river winding through the landscape, 
ancient walled cities with mud-brick walls visible in the distance. 
Slow crane down from clouds to reveal the scale of the empire. 
Warm golden hour backlight, volumetric god rays through dust haze. 
Epic documentary style, 4K detail, film grain. Dark-skinned African horsemen 
appear in the foreground as the camera settles. No text overlay.
```

### Clip 2 — Mansa Moussa sur son trône (4-10s, durée: 6s)
**Refs**: `@Image1` (mansa_ref_front), `@Image2` (mansa_ref_3q)
**Audio natif**: Non (VO par-dessus)
```
@Image1 @Image2 show the king. Mansa Moussa, a powerful dark-skinned West African 
king in his 40s with short beard and dignified expression, sitting on a golden throne 
in a grand palace with carved wooden pillars. He wears a golden crown, royal blue and 
gold robes with intricate Malian patterns, holding a golden scepter. 
Slow dolly-in from a wide shot to a medium close-up, revealing his face. 
Warm torchlight flickering, golden glow on his skin. Advisors in colorful traditional 
garments stand in the background, out of focus. 
Cinematic regal atmosphere, shallow depth of field, 35mm film look. No text overlay.
```

### Clip 3 — Les mines d'or (10-18s, durée: 8s)
**Refs**: Aucune (paysage + figurants)
**Audio natif**: Oui (generate_audio=true) — sons de pioche, rivière, cris
```
Ancient West African gold mines at dawn. Dark-skinned miners digging and panning 
for gold dust in a rocky riverbed, muscular arms working the earth. Golden nuggets 
glistening in morning sunlight, water splashing. Workers carrying woven baskets 
of gold ore up a dusty path. 
Slow tracking shot following a basket from the riverbed to the surface, revealing 
the scale of the operation — hundreds of workers. 
Warm earthy tones, dust particles floating in golden light, heat shimmer. 
Documentary cinematic style, deep focus. No text overlay.
```
**→ last_frame à sauver pour chain vers Clip 4**

---

## CHAPITRE 2: LE PÈLERINAGE (18-47s)

### Clip 4 — La caravane gigantesque (18-23s, durée: 5s)
**Refs**: `@Image1` (mansa_ref_3q) pour Mansa à cheval
**first_frame_url**: last_frame du Clip 3 (transition: l'or devient la caravane)
**Audio natif**: Oui (generate_audio=true) — sabots, vent du désert, chants
```
@Image1 shows the king on horseback. Epic wide aerial shot of a massive caravan 
crossing the Sahara desert — 60,000 people stretching to the horizon. Soldiers on 
horseback carrying golden staffs, 80 camels loaded with gold bags. Mansa Moussa at 
the center on a richly decorated horse, golden robes catching the sun. 
Slow crane up revealing the endless column of people and animals across golden sand 
dunes, heat shimmer distorting the horizon. 
Harsh midday desert sun, warm amber tones, sand particles in the air. 
Epic documentary scale, cinematic wide angle. No text overlay.
```
**→ last_frame à sauver pour chain vers Clip 5**

### Clip 5 — Le Caire (23-33s, durée: 10s)
**Refs**: `@Image1` (mansa_ref_3q) pour Mansa
**first_frame_url**: last_frame du Clip 4 (transition: caravane entre dans la ville)
**Audio natif**: Oui (generate_audio=true) — foule, marchands, appels
```
@Image1 shows the king. 14th century Cairo, bustling marketplace near the city gates. 
Mansa Moussa's caravan arriving through massive stone archways. Crowds of Egyptians 
in turbans and robes watching in awe. Gold coins being tossed to people who scramble 
to catch them. Mansa Moussa on horseback, regal and generous, golden robes shining. 
Smooth forward tracking shot through the market, passing merchants and camels, 
following Mansa's progression. Mamluk architecture, minarets, colorful awnings. 
Warm dusty afternoon light, atmospheric haze, golden tones. 
Documentary cinematic, rich color, shallow depth of field on key moments. No text overlay.
```

### Clip 6 — Choc économique (33-42s, durée: 9s)
**Refs**: Aucune (action close-up)
**Audio natif**: Oui (generate_audio=true) — sons de pièces, murmures
```
Extreme close-up of gold coins being poured into the calloused hands of an Egyptian 
merchant. Gold flowing like water, coins spilling between fingers. The merchant's 
eyes widen with disbelief. Slow motion, golden particles catching light. 
Then smooth dolly out to reveal a marketplace scene where merchants look confused, 
arguing, pointing at scales. A hand writes new prices on a board. 
Dramatic side lighting, golden glow contrasting with worried faces. 
Cinematic dramatic style, shallow focus, film grain. No text overlay.
```

### Clip 7 — Mansa Moussa priant (42-47s, durée: 5s)
**Refs**: `@Image1` (mansa_ref_profile) pour silhouette
**Audio natif**: Non (VO + silence spirituel)
```
@Image1 shows the man's profile. Mansa Moussa, dignified, kneeling in prayer facing 
Mecca, his golden robes spread on the sand. Rows of soldiers praying behind him in 
perfect formation. 
Static wide shot, silhouettes against a massive orange desert sunset. 
Golden hour backlight, long shadows stretching across the sand, warm amber sky. 
Peaceful, spiritual, reverent atmosphere. Cinematic, deep focus, film grain. No text overlay.
```
**→ last_frame à sauver pour chain vers Clip 8**

---

## CHAPITRE 3: L'HÉRITAGE (47-94s)

### Clip 8 — Construction de Tombouctou (47-56s, durée: 9s)
**Refs**: Aucune (paysage architectural)
**first_frame_url**: last_frame du Clip 7 (transition: coucher → aube)
**Audio natif**: Oui (generate_audio=true) — chants de travail, mortier
```
Construction of the Djinguereber Mosque in Tombouctou, 14th century. Workers building 
with mud bricks, applying wet adobe to the rising walls. The distinctive pyramidal 
minaret taking shape against a pale dawn sky. 
Slow tilt up from the foundation — hands mixing mud, laying bricks — to reveal 
the growing structure against the sky. Workers like ants on scaffolding. 
Soft early morning light, cool blue warming to gold as the sun rises. 
Documentary cinematic, architectural scale, film grain. No text overlay.
```
**→ last_frame à sauver pour chain vers Clip 9**

### Clip 9 — Université de Tombouctou (56-67s, durée: 11s)
**Refs**: Aucune (décor intérieur)
**first_frame_url**: last_frame du Clip 8 (transition: extérieur → intérieur, temps qui passe)
**Audio natif**: Oui (generate_audio=true) — murmures, pages qui se tournent
```
Inside a 14th century West African university in Tombouctou. Dark-skinned scholars 
in white robes reading ancient manuscripts at wooden desks, astronomical charts and 
geometric patterns on the walls. Students gathered around a teacher who points to 
a star chart. Parchment scrolls, ink pots, morning light through latticed windows. 
Slow tracking shot moving through the hall, past desks and scholars, as if walking 
through the university. Soft pools of warm daylight on each desk, dust motes in 
golden beams. Scholarly, contemplative atmosphere. 
Documentary cinematic, shallow depth of field, rich warm tones. No text overlay.
```

### Clip 10 — Carte catalane 1375 (67-77s, durée: 10s)
**Refs**: Aucune (objet inanimé)
**Audio natif**: Non (VO importante)
```
Close-up of the Catalan Atlas of 1375, ancient parchment unrolled on a wooden table. 
Camera slowly dollies in and zooms into the figure of a black king seated in West 
Africa, holding a golden nugget. The gold leaf on the map catches candlelight. 
Detail of the medieval script and illustrations — camels, cities, rivers. 
Flickering candlelight, warm sepia tones, antique parchment texture visible. 
Museum documentary style, extreme detail, shallow focus, subtle handheld feel. No text overlay.
```

### Clip 11 — Pyramides/héritage final (77-94s, durée: 17s)
**Refs**: Aucune (paysage moderne)
**Audio natif**: Oui (generate_audio=true) — vent du désert, ambiance contemplative
```
Modern-day aerial shot of the Djinguereber Mosque in Tombouctou, still standing after 
700 years. The ancient mud-brick structure glowing in deep golden sunset light. 
Slow crane up and orbit around the mosque, then rising higher to reveal the vast 
Sahara desert stretching to the horizon. Sand dunes, sparse vegetation, a few figures 
walking in the distance. 
Golden hour to twilight transition, warm amber fading to deep blue, stars beginning 
to appear. Epic, nostalgic, reverent atmosphere. 
Cinematic documentary, deep focus, epic scale, film grain. No text overlay.
```

---

## RÉCAPITULATIF TECHNIQUE

| Clip | Durée | Res | Refs | Audio | Chain | Coût 720p T2V |
|---|---|---|---|---|---|---|
| 0 (char sheet) | — | image | — | — | — | Seedream (gratuit) |
| 1 — Carte empire | 4s | 720p | 0 | Non | — | $1.26 |
| 2 — Trône | 6s | 720p | 2 | Non | — | $1.89 |
| 3 — Mines d'or | 8s | 720p | 0 | Oui | → out | $2.52 |
| 4 — Caravane | 5s | 720p | 1 | Oui | in→out | $1.58 |
| 5 — Le Caire | 10s | 720p | 1 | Oui | in | $3.15 |
| 6 — Choc éco | 9s | 720p | 0 | Oui | — | $2.84 |
| 7 — Prière | 5s | 720p | 1 | Non | → out | $1.58 |
| 8 — Construction | 9s | 720p | 0 | Oui | in→out | $2.84 |
| 9 — Université | 11s | 720p | 0 | Oui | in | $3.47 |
| 10 — Carte catalane | 10s | 720p | 0 | Non | — | $3.15 |
| 11 — Héritage final | 17s | 720p | 0 | Oui | — | $5.36 |
| **TOTAL** | **94s** | | | | | **$29.62** |

*Note: Prix basés sur T2V 720p à $0.315/s. Avec high-tier top-up (-10%) = ~$26.66.*

---

## INSTRUCTIONS DE GÉNÉRATION (kie.ai Playground)

1. **Aller sur** https://kie.ai/seedance-2-5
2. **Settings par clip**:
   - Resolution: **720p**
   - Aspect ratio: **9:16** (vertical)
   - Duration: selon tableau ci-dessus
   - generate_audio: selon tableau
   - output_format: mp4
3. **Pour les clips avec Mansa** (2, 4, 5, 7): uploader les character refs dans `reference_image_urls`
4. **Pour les clips chainés** (4, 5, 8, 9): utiliser `first_frame_url` avec la last_frame du clip précédent
5. **Prompt**: copier-coller le prompt, en remplaçant `@Image1` etc. par les refs uploadées
6. **Sauvegarder** chaque clip comme `clip_NN.mp4` dans `/home/tars/sankofa/mansa_moussa/clips/`

## CHECKLIST POST-GÉNÉRATION

- [ ] QA vision sur chaque clip (or_vision.py) — vérifier cohérence Mansa, pas d'hallucinations
- [ ] Sauver les last_frames des clips 3, 4, 7, 8 pour chaining
- [ ] Si un clip est faible → regénérer avec prompt ajusté
- [ ] Concaténer selon build_mansa.sh
- [ ] Burn-in ASS (chapitres jaunes + subs blancs)
- [ ] Générer thumbnail (thumbnail_mansa_moussa.jpg déjà créé)
- [ ] Upload sur @sankofa-histoire
