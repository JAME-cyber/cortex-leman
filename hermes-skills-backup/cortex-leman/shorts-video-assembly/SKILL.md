---
name: shorts-video-assembly
version: 1.0.0
description: >
  Assemblage de vidéos courtes verticales (9:16, YouTube Shorts/TikTok/IG Reels)
  multi-segments: intro + title card + clips animés (IA ou stock) + VO + musique + sous-titres + CTA.
  Pattern réutilisable: Culture en Saveur (campagne événement, funnel marketing), LEC Shorts crypto, cortex-leman-video-brief, african-heroes Sankofa (documentaire historique).
  Couvre le pipeline complet: sync VO-clip, rendering, compositing audio multi-pistes, funnel marketing (Hook-Build-Climax-CTA),
  chirurgie de clips (1 clip a la fois), batch builder unifie, migration scripts standalone vers master builder,
  format documentaire Sankofa (burn-in ASS 3-actes, thumbnails clean-frame, edge-tts HenriNeural -5Hz).
  Complementaire a le-contre-point-podcast (long-form 16:9) et cortex-leman-video-brief (single-segment 60-90s).
  References: clip-vo-timing.md, marketing-funnel.md, cta-unification.md, telegram-delivery.md, batch-quality-upgrade.md, sankofa-format.md.
  Scripts: yt_upload.py (YouTube Data API v3 headless upload — see scripts/yt_upload.py).
references/marketing-funnel.md (Funnel narratif Hook→Build→Climax→CTA: analyse depuis vidéo ref, batch builder pour campagne entière, VO punchy rewrite, ⚠ hook pacing: contexte asso AVANT question (sinon entrée trop rapide), ⚠ brand identity compliance: charte fonts/couleurs/logo/dates/contact sur hook cards + sous-titres, ⚠ font validation: variants corrompus (HTML au lieu de TTF), ⚠ PIL API: Image.Resampling.LANCZOS (pas Image.LANCZOS), ⚠ séparation audio stinger/content via adelay, ⚠ redondance CTA quand VO prix sur sunset, ⚠ anti-redondance clip unique par segment, ⚠ vérifier identité clip AVANT suppression (extraire frames + confirmer), ⚠ extraction photos produit depuis clips existants (gratuit), ⚠ correction luminosité clips IA via ffmpeg eq, ⚠ démarrage musique différé à segment spécifique via adelay, ⚠ cascade d'indices hardcoded après suppression de segment (6 points synchronisés), clips: chaque build=clip DIFFÉRENT m, ⚠ migration standalone→master funnel builder (hériter pipeline canonique), ⚠ batch compression 12+ vidéos (sous-lots de 3-4 ou background parallèle)atcher contenu, ⚠ sunset ping-pong 3-seg quand VO>clip, clips_ext climax override).
templates/build_funnel.py (template de build funnel complet single-vidéo: slow-mo setpts, audio separation via adelay, ping-pong outro, subtitles ASS — copier et adapter).
templates/build_funnel_all.py (batch builder multi-vidéos: config dict par vidéo, pipeline commun — voir references/marketing-funnel.md pour exemple de config).
references/cta-unification.md (CTA standardisé + swap CTA depuis vidéo référence: CUT > RECREATE, vision analysis via Qwen VL workaround).
references/unified-outro.md (outro campaign-wide: pricing card EXISTANT inchangé + clip animé APRÈS, jamais overlay).
references/unified-intro-stinger.md (stinger brand signature en ouverture: wrapper 3-segments stinger→body→outro en une passe ffmpeg, compression escalation).
templates/build_branded_batch.py (template batch: prepend stinger + append outro sur N vidéos, auto-compress TG).
category: cortex-leman
---

# Shorts Video Assembly — Pipeline multi-segments 9:16

## Quand utiliser
- Vidéo promotionnelle courte (15-45s) avec plusieurs segments: intro, clips pays/thème, CTA
- Quand chaque clip doit être synchronisé à sa propre narration VO
- Quand il faut composer audio multi-pistes (VO + musique + stinger)
- Pour Zankofa/Culture en Saveur, LEC Shorts, ou tout Short brandé multi-scènes

## Pre-delivery checklist (OBLIGATOIRE — 3 omissions répétées en une session)
Avant de déclarer une vidéo "livrée", vérifier ces points qui sont oublés systématiquement:
1. **Audio présent?** — `ffprobe -show_entries stream=codec_type` → doit contenir `audio`. Le mux video-only est le piège #1.
2. **Sous-titres présents?** — Sauf si l'utilisateur a explicitement dit de ne pas en mettre. Si recyclage de clips qui ont déjà du texte burned-in, utiliser le pattern "Clean Assets" (voir `references/clean-teaser-build.md`).
3. **Musique cohérente cross-vidéo?** — Toutes les vidéos d'une même campagne/client doivent utiliser le **même track musical**. Vérifier les scripts de build des autres vidéos de la campagne avant d'en choisir un nouveau. Ex: si le teaser utilise `afroswing_v2.mp3`, le catering et le T2 doivent aussi utiliser `afroswing_v2.mp3`. L'utilisateur corrige systématiquement ce manque de cohésion.du texte burned-in, placer les sous-titres en HAUT (`Alignment 8, MarginV=1700`) pour éviter la collision.
3. **Sous-titres lisibles?** — Phrases longues → couper avec `\N` (voir `references/ffmpeg-zoompan-subtitles.md`). Taille police ≤38px pour vidéos texte-dense. Vérifier que rien ne dépasse de l'écran.
4. **Zoom centré?** — Si zoompan utilisé, vérifier `x='iw/2-(iw/zoom/2)'` et `y='ih/2-(ih/zoom/2)'`. Sans ça, le zoom fuit vers le coin haut-gauche (voir `references/ffmpeg-zoompan-subtitles.md`).
5. **Zéro clip en double?** — Chaque segment doit avoir une source visuelle différente. Pas de loop du même clip N fois (rejet utilisateur systématique).
6. **Texte audit?** — Voir `references/text-qa-checklist.md` — orthographe, noms propres, accord verbe-sujet FR. déjà du texte burned-in, les sous-titres vont se superposer → utiliser des assets propres (voir `clean-teaser-build.md`).
3. **Texte overlay vérifié?** — Voir `references/text-qa-checklist.md`. Trois fautes ont échappé en juil. 2026 (Poids→Pois, École→Maison de Quartier, Inscrivez→Inscrivez-vous). Audit orthographique ET factuel obligatoire: VO, drawtext, PIL text, ASS subtitles.
4. **End card complète?** — Voir `references/endcard-completeness-checklist.md`. Vérifier âge, prix, horaires, email exact, lieu officiel. déjà du texte burned-in → NE PAS ajouter de sous-titres ASS par-dessus (double overlay). Demander à l'utilisateur.
3. **Audit orthographique** — Lister TOUT le texte affiché (hook cards, overlays drawtext, sous-titres ASS, end cards) et relire. Fautes typiques: "Poids chiches"→"Pois chiches", noms de lieux incohérents ("École de Quartier" vs "Maison de Quartier" pour le même lieu).

## ⚠️ La zone grise algorithmique (60s-3min) — FORMAT OBLIGATOIRE

**RÈGLE ABSOLUE (validée août 2026) :** Sur YouTube, choisir < 60s (Shorts purs) OU > 3min (vidéos longues). JAMAIS entre les deux. Les vidéos 80-120s sont dans une **zone grise** — ni distribuées dans le feed Shorts ni monétisables. C'est le pire des deux mondes.

**Si une chaîne a des vidéos 80-120s à <10 vues :** le problème est probablement le format, pas le SEO. Recouper en <60s (feed Shorts = distribution gratuite) ou étendre en >3min (monétisation).

Priorité #1 à 0 subs : **rétention** (analyser le décrochage dans YouTube Studio). SEO/thumbnails/cadence = multiplicateurs de zéro si le contenu ne retient pas.

## References
- `references/ffmpeg-zoompan-subtitles.md` — zoompan centré + ASS \N line breaks + ancrage géographique prompts Seedance + alignement audio cross-video + anti-loop
- `references/campaign-audit-and-trust-video.md` — LLM-driven campaign audit pattern (Claude Sonnet 4 via OpenRouter) + Trust/Safety programme video template (animateurs visibles, cards confiance/sécurité) complémentaires
- `references/clean-teaser-build.md` — **Teaser 100% clean: éviter le recyclage de clips long-form**. Voir aussi le pitfall #4 ci-dessous.
- `references/youtube-shorts-growth-strategy.md` — Stratégie croissance Shorts : zone grise, rétention > SEO, hooks 3s, distribution externe (TikTok/Reels/WhatsApp), audience diasporique, KPIs 30/60/90j, contre-analyse OpenRouter
- `references/video-recutting-workflow.md` — Recoupe vidéo longue (80-120s) → Short <60s : plan coupe par segment, CTA TTS régénéré, template build_short.py, délégation parallèle

## Pitfalls

### Pipeline alternatif: Text-Overlay Production (sans clips IA)

Pour le contenu data-driven (prix, comparaisons, chiffres) où le visuel est secondaire au message, un pipeline sans clips IA existe:

- Claude Fable 5 (OpenRouter) → script enhanced + visual directions + overlay timing
- Edge TTS FR (+12%) → VO
- ffmpeg drawtext overlays sur fonds colorés (lavfi color)
- Musique procédurale (sine lowpass, 0.12 volume)
- Vision QA frames clés via OpenRouter

Production en <5min, ~$0.20/video. Détails complets: `references/text-overlay-production.md`.

---

1. **VIDÉO DE RÉFÉRENCE → CUT, PAS RECREATE** → Quand l'utilisateur envoie une vidéo avec un segment qu'il aime, couper et incorporer le footage, JAMAIS recréer en PIL/code. L'utilisateur a corrigé 3 fois en 1 session pour ce pattern. Voir `references/cta-unification.md` (swap) et `references/unified-outro.md`.

2. **OUTRO ANIMÉ ≠ OVERLAY** → le pricing card existant reste un segment séparé, intact. Le clip animé (silhouettes, sunset, brand) s'append APRÈS le pricing, pas en background par-dessus. L'utilisateur a explicitement rejeté l'overlay des prix sur le sunset. Voir `references/unified-outro.md`.

3. **NE PAS REFORMULER LES PRIX** → toujours extraire le pricing exact des build scripts existants (`grep CHF`, `prix`, `formule`). Garder le wording identique. Voir `references/unified-outro.md`.

4. **BOUCLER UN CLIP = INTERDIT** → clips IA 5s vs VO 8-12s. Multi-angle cuts ou zoom lent, jamais loop. Voir `references/clip-vo-timing.md`.

5. **CATERING ≠ WORKSHOP** → le CTA d'une vidéo catering (menu + prix par plat) est différent du CTA d'une vidéo stage (tarif journée/demi). Ne pas appliquer le même CTA partout aveuglément.

6. **RECYCLAGE DE CLIPS LONG-FORM = double texte** — Extraire des clips d'une vidéo long-form (ex: V1 PRO 100s) pour faire un teaser court génère un conflit visuel: le texte burned-in des clips originaux reste visible ET les nouveaux sous-titres/overlays se superposent par-dessus. L'utilisateur rejettera systématiquement le résultat. **Solution**: build le teaser à partir d'assets 100% propres (intro steam/spice + Seedance clips sans texte + papercrafts/posters avec overlays drawtext + end card). Ne JAMAIS `-ss` extraire d'une vidéo déjà rendue avec du texte.
- `references/seedance-prompting-patterns.md` — Bibliothèque 9 patterns Seedance (A-I)
- `references/procedural-bg-patterns.md` — Backgrounds PIL sans IA (wax/pan-africain, palettes)
- `references/teaser-cut-from-longform.md` — Recyclage clips V1 PRO → teaser 15-22s WhatsApp/Reels
- `references/seedance-promo-event-template.md` — Template scénario promo événement
- `references/kieai-seedance-api.md` — API KIE Seedance (endpoints, polling, download)
- `references/kieai-seedream-image-api.md` — API KIE Seedream (images fixes)
- `references/twitter-video-analysis.md` — Analyse vidéo de référence depuis X/Twitter (vxtwitter, scene detection, contact sheet)
- `references/endcard-completeness-checklist.md` — Checklist end card (infos clés obligatoires)
- `references/brand-alignment-workflow.md` — Audit identité visuelle client avant production

## Ne PAS utiliser pour
- Vidéos long-form 16:9 → `le-contre-point-podcast`
- Vidéos single-segment 60-90s simples → `cortex-leman-video-brief`

## ⚠ PITFALLS (LIVED — USER CORRECTIONS)

1. **CLIP REDUNDANCY** — Ne JAMAIS utiliser le même clip 3× pour remplir un Build. Avant d'assigner des clips à des segments, faire un audit complet : `find assets -name "*.mp4"` en incluant TOUS les sous-dossiers (`seedance_t3_v2/`, `seedance_catering/`, etc.). Le user corrège systématiquement les clips redondants — chaque plan Build doit montrer quelque chose de visuellement distinct.

2. **LOCATION ACCURACY** — Un service basé à Genève/Petit-Lancy doit utiliser les clips `_gva` (kiosk_chef_gva.mp4, kiosk_order_gva.mp4), PAS les versions génériques. Vérifier le suffixe `_gva` pour les clips de localisation Suisse.

3. **CTA CARD REDUNDANCY** — Quand la VO annonce déjà les prix ("85 CHF la semaine"), NE PAS ajouter de carte prix visuelle séparée. Le sunset outro sert de support visuel, la VO porte l'info prix. Carte prix = redondance.

4. **AUDIO SEPARATION STINGER** — Le stinger (3.5s) doit jouer seul. Musique et VO démarrent APRÈS via `adelay=3700|3700` (stinger_dur + 200ms gap). Sans ça, les sons se chevauchent.

5. **SUNSET PING-PONG 3-SEGMENT** — Pour les VOs CTA longues (>8s), un ping-pong forward+reverse (8.4s) ne suffit pas. Utiliser forward+reverse+forward (12.6s) puis `trim` à la durée voulue.

6. **SLOW-MO NOT LOOPS** — Pour étirer un clip court (5.04s) à la durée de la VO (5.2-5.6s), utiliser `setpts=1.05*PTS` (ralenti subtil invisible), JAMAIS de loop. Facteurs 1.02-1.18 = imperceptibles.
- Podcasts multi-voix → `financial-content-pipeline`

## ⚠️ Pitfall: Sous-titres ASS qui chevauchent le texte burned-in des clips source

Quand on recycle des clips d'une vidéo existante (ex: extrait du V1 PRO pour un teaser), ces clips ont **déjà du texte burned-in** dans le bas/centre de l'image. Si les sous-titres ASS sont placés en bas (Alignment 2, MarginV ~120-200), ils se superposent au texte existant → illisible.

**Fix:** Placer les sous-titres ASS **en haut** (Alignment 8) avec MarginV élevé (1600-1700 sur 1920px) quand les clips source ont déjà du texte burned-in. Avant de générer les sous-titres, **extraire une frame d'un clip source** et vérifier où se trouve le texte existant.

Alternative: générer deux couches de sous-titres à des positions différentes si nécessaire (ex: informations clés en haut, captions dynamiques en bas), mais JAMAIS superposer au texte burned-in.

---

## ⚠️ Production Checklist obligatoire (avant livraison)

Trop souvent l'agent livre une vidéo sans audio ni sous-titres, puis l'utilisateur doit les réclamer. Ces éléments sont **obligatoires**, pas optionnels. Vérifier AVANT de déclarer la vidéo prête :

| # | Élément | Détail | Oubli fréquent |
|---|---------|--------|----------------|
| 1 | **Intro/stinger** | Prépend systématiquement le stinger ou l'intro officielle du projet (ex: `intro_steam_spice.mp4` pour Culture en Saveur). Si la vidéo a plusieurs versions, l'intro va sur TOUTES. | L'agent oublie de l'ajouter même après qu'il ait été ajouté à la vidéo précédente |
| 2 | **Piste audio** | Musique de fond mixée à 0.10-0.12 volume + fade in/out. Source: assets/music/ du projet. Si VO présente, mixer VO à 2.5 et music à 0.12. | Vidéo livrée muette — l'utilisateur doit réclamer le son |
| 3 | **Sous-titres ASS** | Burn-in obligatoire (hardcoded dans la vidéo). Format ASS avec MarginV=120 (bas d'écran), palette charte. Un sous-titre par segment/menu item/plat. | L'agent produit des motion graphics avec texte graphique mais pas de sous-titres narration |
| 4 | **Compression TG** | CRF 26, maxrate 3200k, scale 720:1280, +faststart. Max 50MB (idéalement <5MB pour share WhatsApp). | — |
| 5 | **Vérification audio** | `ffprobe -show_entries stream=codec_type` doit retourner `audio,aac`. Si seulement `video`, la piste audio manque. | — |

**Template de sous-titres ASS (format vertical 9:16, bas d'écran):**
```ini
[Script Info]
PlayResX: 720
PlayResY: 1280

[V4+ Styles]
Style: Default,Montserrat Bold,42,&H00F5E8D3,&H000000FF,&H00000000,&H49000000,-1,0,0,0,100,100,0,0,1,3,2,2,60,60,120,1

[Events]
Dialogue: 0,0:00:03.50,0:00:06.00,Default,,0,0,120,,TEXTE ICI
```

**Template commande ffmpeg complète (vidéo + audio + sous-titres):**
```bash
ffmpeg -y -i video_silent.mp4 -i music.aac \
  -vf "subtitles=subtitles.ass" \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ac 2 \
  -map 0:v:0 -map 1:a:0 -shortest \
  video_complete.mp4
```

## Architecture du pipeline

### Structure type (template timeline)
```
[Logo/Intro 3s] → [Title Card 4-5s] → [Clip 1 ~6s] → [Clip 2 ~6s] → [Clip 3 ~5s] → [CTA 10s]
```
Total typique: 30-40s. Chaque segment vidéo est **étiré/compressé** pour matcher exactement la durée de son VO.

### Ordre de production (obligatoire)
1. **Générer les VO** (edge-tts) pour chaque segment → mesurer les durées réelles avec `ffprobe`
2. **Calculer la timeline** depuis les durées VO réelles (pas d'estimations)
3. **Préparer les segments vidéo**: stretch avec `setpts` pour matcher les durées VO
4. **Préparer le title card** (PIL + assets visuels)
5. **Concaténer** les segments vidéo
6. **Composer l'audio**: `amix=duration=longest` (VO + musique + stinger)
7. **Ajouter sous-titres** ASS/SRT
8. **Build final**: mux vidéo + audio + subs

## edge-tts (VO française)

### CLI — flags valides July 2026
```bash
# ✅ CORRECT (July 2026)
edge-tts --voice fr-FR-DeniseNeural --text "Texte" --write-media output.mp3

# ❌ FAUX — --write-audio deprecated, produit fichier 0-byte silencieusement
edge-tts --voice fr-FR-DeniseNeural --text "Texte" --write-audio output.mp3
```

### Voix françaises valides (July 2026)
- `fr-FR-DeniseNeural` — F, chaleureuse, défaut recommandé
- `fr-FR-HenriNeural` — M, France
- `fr-CH-ArianeNeural` — F, Suisse
- `fr-CH-FabriceNeural` — M, Suisse
- `fr-CH-HenriNeural` — **❌ SUPPRIMÉ** (July 2026)

### Vérification voix avant hardcoded
```bash
edge-tts --list-voices 2>/dev/null | grep "^fr-"
```
**Toujours vérifier** — edge-tts déprécie des voix sans notification.

### Quirk argparse: `--rate` et `--pitch` avec signe négatif
edge-tts utilise argparse qui interprète les valeurs commençant par `-` (ex: `-5%`) comme des options. Deux patterns valides:

```python
# ✅ Pattern 1: utiliser = (le plus robuste)
cmd = ["edge-tts", "--voice", voice, f"--rate={rate}", "--text", text, "--write-media", out]

# ✅ Pattern 2: passer comme argument positionnel via =
subprocess.run(f'edge-tts --voice {voice} --rate={rate} --text "{text}" --write-media {out}', shell=True)

# ❌ FAUX — argparse voit "-5%" comme un flag inconnu → "expected one argument"
cmd = ["edge-tts", "--voice", voice, "--rate", "-5%", "--text", text, "--write-media", out]
```

Si VO échoue silencieusement sur tous les segments, vérifier ce pattern en premier (le message d'erreur argparse est noyé dans stderr).

### Diagnostique fichier VO vide
```bash
ls -la output.mp3   # si 0 bytes → flag --write-audio obsolète ou voix inexistante
```

## Synchronisation clip ↔ VO

### Principe
Chaque segment vidéo doit durer **exactement** la durée de son VO correspondant. Si la VO fait 6.2s et le clip source 5s, étirer le clip.

### Calcul du facteur setpts
```python
import subprocess, json

def get_duration(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json",
                        "-show_format", str(path)], capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def stretch_video(src, target_dur, out, overlay=None):
    src_dur = get_duration(src)
    factor = target_dur / src_dur
    # setpts factor stretches/compresses video duration
```

### Alignment VO/clip (leçon clé)
- **Chaque VO pays doit jouer SUR son clip pays**, pas sur le suivant
- Le VO d'intro ("Cet été...") joue sur un **title card dédié**, pas sur le premier clip
- Sans cela, la VO Égypte commence pendant qu'on voit encore le title card → désynchronisation perçue

## Audio multi-pistes: amix

### Règle absolue: `duration=longest`
```
# ✅ CORRECT — audio complet sur toute la durée vidéo
[stinger][vo][music]amix=inputs=3:duration=longest:dropout_transition=0[aout]

# ❌ FAUX — coupe au stinger (le plus court, ~3s), audio tronqué à 5s sur 23s de vidéo
[stinger][vo][music]amix=inputs=3:duration=first:dropout_transition=0[aout]
```

### Diagnostic audio coupé
```bash
ffprobe -v error -select_streams a -show_entries stream=duration -of csv=p=0 video.mp4
# Si audio dur << video dur → amix duration=first (bug)
```

### Niveaux audio recommandés — CORRIGÉ (juil. 2026)

**⚠️ ERREUR PRÉCÉDENTE**: VO=100%, Musique=35%, Stinger=80% avec `amix` SANS `normalize=0` → la voix est **inaudible sur mobile**. L'utilisateur a rapporté "pas de son" même avec audio techniquement présent.

**Cause racine**: `amix=inputs=3` sans `normalize=0` divise chaque piste par N (ici 3 = -10 dB). VO à 100% devient ~33%. La musique à 35% + stinger à 80% créent un mur basse-fréquence (top freqs: 66-70Hz au lieu de 200-400Hz). Speech band energy chute à 35% → la voix est présente spectralement mais noyée.

**Niveaux corrigés** (avec `normalize=0`):
- VO: **250%** (volume=2.5 — la parole doit DOMINER, amix ne divisera plus)
- Musique: **12%** (volume=0.12 — vraiment en fond, ne masque pas la VO)
- Stinger: **30%** (volume=0.3 — impact bref mais ne parasite pas)

```python
# ✅ CORRIGÉ — VO dominante, musique discrète, normalize=0 obligatoire
f"[1:a]volume=0.3,adelay={delay}|{delay}[stinger];"
f"[2:a]adelay={delay}|{delay},volume=2.5[vo];"
f"[3:a]volume=0.12,afade=t=out:st={dur-1.5}:d=1.5[music];"
f"[stinger][vo][music]amix=inputs=3:duration=longest:dropout_transition=0:normalize=0[aout]"

# ❌ ANCIEN (PROBLÉMATIQUE) — amix divise par 3, VO enterrée
f"[2:a]adelay={delay}|{delay},volume=1.0[vo];"           # trop faible
f"[3:a]volume=0.35,afade=t=out..."                       # musique trop forte
f"[stinger][vo][music]amix=inputs=3:...dropout_transition=0[aout]"  # pas de normalize=0
```

### Ducking automatique (anti-tambours désynchronisés)

**⚠️ PROBLÈME (juil. 2026)**: Une musique percussive (tambours, djembé, afrobeat) mixée en volume constant à 0.12 sous la VO donne une impression de **désynchronisation**: les drums jouent tout du long, même pendant les pauses de la parole, créant une dissonance perçue ("tes tambours c'est pas synchronisés avec le speech").

**Cause**: Le volume fixe ne fait pas la différence entre "VO en train de parler" et "VO en pause". Pendant les pauses, les percussions ressortent et cassent le rythme narratif.

**Solution 1 — Ducking manuel par segment** (préférable pour le contrôle):
Au lieu d'une seule piste musique continue, ducker la musique sur les timestamps où la VO parle:
```python
# Ducker la musique quand la VO est active (sidechain compression manuel)
# VO timestamps: [(0, 9), (9, 23.4), (23.4, 36), ...] — dérivés des durées VO
# Entre les segments: musique remonte (interludes musicaux)
f"[1:a]volume=0.12,"
f"sidechaincompress=threshold=0.5:ratio=8:attack=5:release=200"
f"[bgm]"
```

**Solution 2 — Interludes musicaux** (structuré):
Couper la musique pendant les segments VO, jouer un stinger musical court (0.5-1s) **entre** les segments comme transition:
```
[Seg VO 1 + musique ducked] → [stinger 0.5s] → [Seg VO 2 + musique ducked] → ...
```
Avantage: les tambours deviennent des ponctuations rythmiques entre les phrases, pas un mur continu.

**Solution 3 — Sélection musicale adaptée** (préventif):
Préférer une musique ambient/mélodique (ex: `ambient_v1.mp3`, `sunset_v1.mp3`) à une musique percussive (`afrobeat_v1.mp3`) quand le ducking n'est pas implémenté. L'ambient masque moins la VO et ne crée pas de désync perçu.

**Checklist anti-désync**:
- [ ] Musique ducked ou coupée pendant les segments VO actifs
- [ ] Si musique percussive: interludes entre segments (pas continu)
- [ ] Tester: écouter sans la vidéo — les tambours suivent-ils le rythme de la parole ou jouent-ils indépendamment?
- [ ] Si la VO parle de "tambours" (ex: "que la fête commence"), synchroniser un swell musical sur ce moment précis

### Vérification durée vidéo ≥ durée VO (OBLIGATOIRE avant mux final)

Avant de muxer vidéo + audio, **toujours** vérifier que la vidéo concaténée est au moins aussi longue que la VO. Sinon le dernier mot sera coupé (pitfall #33).

```bash
video_dur=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 video.mp4)
vo_dur=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 vo_full.mp3)
python3 -c "
vd,ad=float('$video_dur'),float('$vo_dur')
if vd < ad: print(f'MISMATCH: video {vd:.1f}s < VO {ad:.1f}s, {ad-vd:.1f}s will be cut')
else: print(f'OK: video {vd:.1f}s >= VO {ad:.1f}s')
"
```

Si `video_dur < vo_dur`: ffprobe chaque segment, identifier le segment sous-dimensionné, le reconstruire avec la bonne durée (ex: cuts à `dur/4` au lieu d'une valeur fixe).

### Sidechain ducking — pattern 3 passes (robuste)

**⚠️ PROBLÈME (juil. 2026)**: un `-filter_complex` unique avec `sidechaincompress` + `amix` échoue avec "Stream specifier 'X' matches no streams" quand les labels utilisés ressemblent à des stream specifiers. Les labels `[vo]`, `[n]`, `[voc]`, `[m]` sont interprétés par ffmpeg comme des références de flux (`[v:0]`, `[a:0]`) et causent une erreur `Invalid argument`. 3 échecs consécutifs observés avant de trouver le fix.

**Labels problématiques** (TOUS échouent): `[vo]` (conflit "v"=video), `[n]`, `[m]`, `[voc]`, `[v]`, `[a]`, `[s]`.

**Solution — 3 passes séparées en WAV intermédiaire**:

```bash
# Pass 1: Prep music (trim, volume, fades)
ffmpeg -y -i music.mp3 \
  -t $VO_DUR -af "volume=0.15,afade=t=in:d=1.5,afade=t=out:st=${FADE_OUT}:d=1.5" \
  -c:a pcm_s16le music_prep.wav

# Pass 2: Boost VO
ffmpeg -y -i vo_full.mp3 -af "volume=2.5" -c:a pcm_s16le vo_boost.wav

# Pass 3: Sidechain compress + amix (labels multi-syllabes OK)
ffmpeg -y -i music_prep.wav -i vo_boost.wav \
  -filter_complex "[0:a][1:a]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=300[bg];[1:a][bg]amix=inputs=2:duration=first:normalize=0[out]" \
  -map "[out]" -t $VO_DUR -c:a aac -b:a 192k final_audio.aac
```

**Règle de nommage des labels**: utiliser des noms multi-syllabes qui ne ressemblent pas à des specifiers (`[bg]`, `[ducked]`, `[out]`, `[mixed]` = OK). Les labels d'une seule lettre ou qui commencent par `v`/`a`/`s` = KO. Le 3-passes permet aussi de tester chaque étape indépendamment (vérifier music_prep.wav et vo_boost.wav avant le mix final).

## Promo slicing — réutilisation d'un clip multi-scènes (anti-gaspillage crédits)

Quand les crédits IA sont insuffisants pour générer des clips individuels par segment, un **clip promo multi-scènes** (ex: Seedance 15s contenant 7 scènes séquentielles: spices→cooking→classroom→henné→drums→visio→sunset) peut être **slicé en sous-segments** qui matchent les beats VO.

### Technique `ffmpeg -ss` + `tpad`

```python
def slice_promo(src, start, end, out_path, target_dur):
    """Extract a time slice from promo, extend to target_dur with tpad clone."""
    slice_dur = end - start
    cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", str(src),
           "-t", f"{slice_dur:.2f}",
           "-vf", (f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                   f"zoompan=z='min(zoom+0.0008,1.12)':d={int(target_dur*FPS)}:s=1080x1920:fps={FPS},"
                   f"tpad=stop_mode=clone:stop_duration={max(0, target_dur-slice_dur):.2f}"),
           "-c:v", "libx264", "-preset", "fast", "-crf", "20",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", str(out_path)]
```

**Avantages**: 1 clip promo = 7+ segments visuels différents (zéro loop). `tpad=stop_mode=clone` fige la dernière frame pour combler l'écart sans répétition visible. `zoompan` ajoute un slow zoom continu qui masque la transition entre la partie animée et la partie clonée.

**Mapping promo → segments**: il faut connaître le timeline du clip promo. Si le prompt original décrit les scènes séquentiellement (spices, cooking, classroom, henné, drums, visio, sunset), estimer ~2s par scène pour un clip 15s. Documenter ce timeline dans le script de build pour référence.

**Limitation**: la résolution de chaque slice = durée scène / durée totale. Un clip 15s avec 7 scènes donne ~2s par scène. Pour des VO de 9-14s par segment, le slice doit être étendu de 7-12s via `tpad`+`zoompan` — acceptable mais pas aussi dynamique qu'un clip dédié.

## drawtext sur b-roll video (single-pass, sans PIL)

Quand le texte overlay doit être brûlé directement sur du b-roll vidéo (pas une carte PIL séparée), **ne pas utiliser PIL overlay + ffmpeg compositing** (lent, timeout sur CPU). Utiliser **drawtext en single-pass** dans le `-vf` ffmpeg directement.

### Technique `textfile=` (OBLIGATOIRE pour le français)

Les apostrophes (`'`), deux-points (`:`), et caractères accentués du français cassent systématiquement le `drawtext` en mode inline (`text='...'`). La solution robuste est d'écrire chaque texte dans un fichier `.txt` et utiliser `textfile=`:

```python
from pathlib import Path

# Écrire les textes dans des fichiers (zéro escaping)
Path("txt/s0_label.txt").write_text("L'ORIGINE", encoding="utf-8")
Path("txt/s0_title.txt").write_text("La cuisine, un langage", encoding="utf-8")
Path("txt/s0_sub.txt").write_text("qui nous rassemble", encoding="utf-8")

vf = (
    f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
    f"drawbox=x=0:y=0:w=iw:h=35:color=0xA0392B@1.0:t=fill,"           # top bar (35px)
    f"drawbox=x=0:y=ih-35:w=iw:h=35:color=0xA0392B@1.0:t=fill,"        # bottom bar (35px)
    f"drawbox=x=0:y=1430:w=iw:h=200:color=0x492E21@0.70:t=fill,"       # text band (lower third)
    f"drawtext=fontfile={POPPINS}:textfile=txt/s0_label.txt:fontsize=24:fontcolor=0xF5E8D3:"
    f"x=(w-text_w)/2:y=1460:box=1:boxcolor=0xA0392B@0.9:boxborderw=12,"
    f"drawtext=fontfile={PFAIR}:textfile=txt/s0_title.txt:fontsize=46:fontcolor=0xF5E8D3:"
    f"x=(w-text_w)/2:y=1510,"
    f"drawtext=fontfile={POPPINS_REG}:textfile=txt/s0_sub.txt:fontsize=26:fontcolor=0xB58761:"
    f"x=(w-text_w)/2:y=1580"
)
```

**⚠️ HAUTEUR DE BANDEAU — RÈGLE DE SIZING (leçon juil. 2026)**: un bandeau de 60px en haut ET en bas **bloque les sous-titres ASS** (qui sont positionnés avec MarginV=120 depuis le bas). L'utilisateur a corrigé: "réduire le bandeau car on ne voit pas les sous-titres".

**Règle de cohabitation bandeau + sous-titres**:
| Élément | Position Y (1080×1920) | Hauteur max |
|---|---|---|
| Bandeau top | y=0 | **35px** (pas plus) |
| Lower-third text band | y=1430–1630 | 200px, semi-transparent (alpha 0.70) |
| Sous-titres ASS | MarginV=120 (depuis bas) | ~y=1700–1820 |
| Bandeau bottom | y=ih-35 | **35px** (pas plus) |

Si bandeau > 35px, les sous-titres sont masqués. Validé par Qwen 2.5 VL qui confirme "bandeaus appear thin enough, subtitles visible" avec 35px.

**Avantages vs PIL overlay**:
- ~10x plus rapide (1 pass ffmpeg vs generate PNG + overlay composite)
- Pas de problème d'escaping (`textfile=` lit le fichier brut)
- Le b-roll vidéo reste animé derrière le texte (contrairement à une carte PIL statique)
- Fonctionne avec `-stream_loop` pour étendre les clips courts

**⚠️ PROBLÈME AVEC `textfile=` ET L'ENCODING (juil. 2026)**: dans certains cas, `textfile=` avec drawtext produit un fichier de sortie de ~48 bytes (complètement vide). La cause est subtile: le fichier `.txt` peut être valide en UTF-8 mais le filtre drawtext échoue silencieusement si le path contient des caractères spéciaux ou si l'encodage du fichier n'est pas détecté correctement. 

**Fix**: quand `textfile=` échoue (fichier < 1KB en sortie), basculer vers `text=` inline avec escaping manuel des apostrophes (`\'`) et deux-points (`\:`):
```python
# Fallback quand textfile= échoue
vf = (
    f"drawtext=fontfile={POPPINS}:text='EVEIL AUX SAVEURS AFRICAINES':fontsize=24:..."
    f"drawtext=fontfile={PFAIR}:text='La semaine avant la rentrée':fontsize=46:..."
)
```
L'escaping des apostrophes françaises n'est PAS nécessaire si on utilise des guillemets simples pour délimiter `text=` et que le texte ne contient pas de `:`. Vérifier toujours la taille du fichier de sortie après drawtext (`> 1KB = OK`).

### Extension b-roll court avec `stream_loop`

Quand le clip b-roll (5s) est plus court que la VO (9-14s), utiliser `-stream_loop` au lieu de `setpts` (qui ralentit/distord):

```python
loops = max(1, int(vo_dur / clip_dur) + 1)
cmd = ["ffmpeg", "-y", "-stream_loop", str(loops), "-i", clip,
       "-i", vo_path, "-vf", vf, "-t", f"{vo_dur:.2f}", ...]
```

`stream_loop` répète le clip naturellement. `setpts` étire temporellement (ralenti).

**⚠️ SEUIL DE LOOP VISIBLE (leçon juil. 2026)**: `stream_loop` au-delà de **1.5x la durée du clip source** produit une répétition perceptible que l'utilisateur remarque immédiatement ("loops", "pourquoi on voit la même chose"). Un clip 5s loopé 2-3x pour un segment 9-14s = répétition évidente.

**Règle de décision**:
| Ratio segment/clip | Méthode | Pourquoi |
|---|---|---|
| ≤1.3x (5s→6.5s) | `stream_loop 1` + trim | Répétition imperceptible |
| 1.3x–1.5x (5s→7s) | `stream_loop 1` + crossfade fin | Transition masque le loop |
| >1.5x (5s→9s+) | **Ken Burns sur still** OU **2 clips différents avec crossfade** | `stream_loop` devient visible |

**Alternatives préférables au loop >1.5x**:
1. **Deux clips différents** avec crossfade 0.3s: génère plus de variété, coupe la monotonie
2. **Ken Burns sur image fixe**: `-loop 1 -t {dur}` + `zoompan` filter sur une Seedream PNG
3. **Split-screen**: clip court + carte texte superposée qui change à mi-parcours

## Title card (PIL)

### Structure
- Fond: couleur sombre brandée OU photo de lieu (assombrie à 55% pour lisibilité)
- Titre principal: 80px DejaVuSans-Bold, or (#FFD700)
- Sous-titre: 48px, blanc
- Drapeaux officiels (si pays): 180×120px, spacing 120px minimum
- Bas: nom projet + dates + lieu

### Drapeaux — RÈGLE ABSOLUE
**JAMAIS dessiner de drapeaux en PIL.** Les symboles héraldiques (Aigle de Saladin, étoiles, armoiries) sont méconnaissables en pixel art.

```python
import urllib.request

# ✅ Télécharger les drapeaux officiels haute résolution
for code in ["eg", "cm", "so"]:
    urllib.request.urlretrieve(
        f"https://flagcdn.com/w640/{code}.png",
        f"assets/flags/{code}.png"
    )
```

### Photo de fond (lieu réel)
Pour Zankofa/Culture en Saveur, utiliser une photo réelle du lieu (Maison de Quartier):
1. Rechercher sur le site des architectes ou de la commune
2. Télécharger la plus haute résolution disponible
3. `Image.blend(photo, dark_overlay, 0.30)` pour lisibilité texte **ET** visibilité du lieu
4. Ajouter mention du lieu en bas du title card

**⚠️ Niveau d'assombrissement**: 55% = trop sombre, l'utilisateur ne voit pas le bâtiment ("on voit pas très bien la maison de quartier"). 30% = bon équilibre. Le texte reste lisible car il a son propre outline/shadow, pas besoin d'un fond très sombre.

### Recherche photo de lieu
- Sites d'architectes (ex: `guenin-architectes.ch`) — galerie projet avec photos haute résolution
- Sites communaux (`lancy.ch`) — annuaires, pages d'associations
- Pattern: chercher `"{nom lieu}" architectes` ou `"{nom lieu}" {commune} bâtiment`

## Sous-titres ASS

### Format .ass pour sous-titres stylisés
```ass
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: Default,DejaVu Sans,48,&H00FFFFFF,&H00000000,&H80000000,-1,0,3,1,2,50,50,120

[Events]
Format: Layer, Start, End, Style, Name, Text
Dialogue: 0,0:00:03.0,0:00:07.2,Default,,En Égypte, le koshari...
```

### Burn-in ffmpeg
```bash
ffmpeg -i video.mp4 -vf "ass=subtitles.ass" -c:v libx264 -crf 20 -preset fast video_subs.mp4
```

## Compression Telegram (<50 MB) + normalisation audio

Pour livrer via bot Telegram, compresser si >50 MB. **ATTENTION**: Toujours normaliser l'audio lors de la compression TG — l'audio edge-TTS est typiquement à -28 dB (inaudible sur mobile).

```bash
# ✅ CORRECT — compression + boost audio pour mobile
ffmpeg -y -i input.mp4 \
  -c:v libx264 -preset fast -crf 26 \
  -maxrate 3200k -bufsize 6400k \
  -af "volume=15dB,alimiter=limit=0.95" \
  -b:a 128k -movflags +faststart \
  output_tg.mp4
```

**Règle audio**: edge-TTS produit un mean_volume de ~-28 dB. Pour mobile/Telegram, viser -14 dB (broadcast standard). `volume=15dB,alimiter=limit=0.95` est le fix fiable. Le `loudnorm` two-pass de ffmpeg échoue souvent en single-pass (pas de changement effectif).

Pour le format court (<40s, 1080×1920), la vidéo est généralement <15 MB mais l'audio reste trop faible — **toujours appliquer le boost audio**, même sans compression vidéo.

## Timeline mixed-media (stills + clips + PIL cards)

Un build Shorts n'est pas obligatoirement tout-vidéo. Le pattern **mixed-media** (validé V1 Culture en Saveur, juil. 2026) combine dans le même timeline :

| Type de segment | Source | Méthode ffmpeg |
|----------------|--------|----------------|
| Intro animée | `intro_steam_spice.mp4` (Playwright capture) | `-t 3.0` tronqué + scale/crop |
| Title card / Hook card | PIL-généré `.jpg` (code graphique) | `-loop 1 -t {dur}` (still → video) |
| Image IA fixe | Seedream `.png` 9:16 | `-loop 1 -t {dur}` + Ken Burns optionnel |
| Clip vidéo IA | Seedance `.mp4` 5s | `setpts` stretch à durée VO |
| CTA card | PIL-généré `.jpg` | `-loop 1 -t {dur}` |

**Avantage** : maximise la réutilisation d'assets existants sans regénérer. Si on a 7 images Seedream + 5 clips + 2 PIL cards, on peut assembler une vidéo 70s complète sans nouvelle génération IA.

### Helper `make_still` (image → segment vidéo)

```python
def make_still(image_path, target_dur, output_path):
    subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(image_path),
        "-t", f"{target_dur:.2f}",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "24", "-an",
        str(output_path)
    ], capture_output=True)
```

Tous les segments (stills + clips) doivent avoir les **mêmes specs codec** (libx264, crf 20, yuv420p, 24fps, 1080x1920) pour que le concat `-c copy` fonctionne sans re-encodage.

## QC validation — extraction de frames

Après chaque build, extraire des frames à des timestamps clés pour vérifier :

```python
import subprocess
from PIL import Image, ImageStat

timestamps = [(2, 'intro'), (6, 'hook'), (12, 'scene1'), (40, 'clip'), (65, 'cta')]
for ts, name in timestamps:
    out = f'/tmp/qc_{name}.jpg'
    subprocess.run(['ffmpeg', '-y', '-ss', str(ts), '-i', video,
                    '-frames:v', '1', '-q:v', '2', out], capture_output=True)
    img = Image.open(out)
    stat = ImageStat.Stat(img)
    brightness = round(stat.mean[0])  # <60 = sombre, >200 = clair/blanc
    stddev = round(stat.stddev[0])    # <30 = plat/uni, >60 = détaillé
    print(f'{name}: brightness={brightness} stddev={stddev}')
```

**Interprétation** :
- `stddev < 30` sur un segment b-roll = image plate, probablement un écran noir ou un card vide
- `brightness > 230` sur un segment b-roll = probablement un card blanc qui remplace l'image prévue
- Tous les frames extraits doivent avoir la bonne résolution (1080×1920)

**Contact sheet** pour visionnement humain (quand Vision GLM est KO) :
```python
imgs = [Image.open(f).resize((270, 480)) for f in frame_paths]
sheet = Image.new('RGB', (270*4, 480*2), (40, 40, 40))
for i, img in enumerate(imgs):
    sheet.paste(img, ((i%4)*270, (i//4)*480))
sheet.save('/tmp/contact_sheet.jpg', quality=85)
```
Livrer le contact sheet au user pour validation visuelle quand l'auto-vision échoue.

## Pattern de script Python (template)

Voir `templates/build_shorts.py` pour un script complet prêt à copier:
- Génération VO par segment
- Calcul automatique des durées
- Stretch vidéo avec setpts
- Title card PIL
- Concat + amix + subs
- Build final avec vérification audio

**Référence mixed-media** : `scripts/build_v1_presentation.py` (Culture en Saveur V1) montre le pattern complet avec intro vidéo + PIL cards + images IA + clip vidéo stretché + sous-titres ASS + audio multi-pistes, le tout en un seul script Python (~200 lignes).

## Workflow de debugging (priorité)

1. **Audio coupé/manquant**: vérifier `amix duration=longest` + ffprobe audio dur vs video dur
2. **Audio inaudible sur mobile**: vérifier `mean_volume` avec `ffmpeg -i video.mp4 -af volumedetect -vn -sn -f null /dev/null 2>&1 | grep mean_volume`. Si < -20 dB → booster avec `volume=15dB,alimiter=limit=0.95`. edge-TTS produit typiquement -28 dB (trop faible).
3. **VO désynchronisée**: vérifier que chaque clip est stretched à sa VO duration exacte
4. **Drapeaux moches/invisibles**: utiliser flagcdn.com (officiels), jamais PIL hand-draw
5. **VO file 0 bytes**: flag `--write-media` (pas `--write-audio`), voix existe toujours
6. **Vision analyze KO (1210)**: fallback Qwen 2.5 VL 72B via OpenRouter (gratuit, excellent OCR FR) pour vérification texte + couleurs. Script: `python3 scripts/vision_check.py <image> [question]`
7. **Fichier vidéo illisible (moov atom manquant)**: timeout ffmpeg → fichier corrompu sur disque. Vérifier avec `ffprobe -v error` après chaque encodage.
8. **Dernier mot VO coupé**: vérifier `video_dur >= vo_dur` avant le mux final. Si video < VO, un segment est sous-dimensionné (ffprobe chaque segment). Aussi: ne JAMAIS encoder en AAC deux fois — étapes intermédiaires en WAV, AAC seulement au mux final (pitfall #33-#34).

## Technical Pitfalls (Patched Jul 2026)

### Zoompan centering (zoom not centered by default)
`zoompan` defaults to top-left origin. For centered zoom on static images:
```
# CORRECT — centered zoom
zoompan=z='min(zoom+0.0012,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=FRAMES:s=1080x1920:fps=24

# WRONG — zoom anchored top-left (user-visible defect)
zoompan=z='min(zoom+0.0012,1.12)':d=FRAMES:s=1080x1920:fps=24
```
**Symptom:** User reported "le zoom n'est pas centré" — image zoomed into upper-left corner.

### VO/SUB text separation (edge-tts reads \N literally)
Same text CANNOT be used for both TTS and subtitle file when subtitles need `\N` line breaks. Edge-TTS reads `\N` as literal text. Use dual dictionaries:
```python
VO_SEGMENTS = [("vo_00", "Clean text for TTS here")]  # NO \N
SUB_TEXT = {"vo_00": r"Clean text\N with line breaks"}  # \N OK for ASS
```

### Subtitle font size + overflow (44pt too large)
Font size 44 with long French sentences overflows 1080x1920. Reduce to **38pt** + `\N` breaks for sentences >6 words.

### Multi-clip quality upgrade pattern
Keep same build script structure (timeline, audio mix, subtitle timing). Only swap video source paths to new clip directory + regenerate VO for fresh timing.

## Reference scripts (Jul 2026 — Culture en Saveur)
- Programme V0: `scripts/build_programme_v0.py` (54s, animatrice visible, planning jour par jour, trust badges)
- T1 V2 quality upgrade: `scripts/build_t1_v2.py` (35s, 3 cooking clips with instructor)
- T3 V2 quality upgrade: `scripts/build_t3_v2.py` (37s, Nil aerial + ecology)
- Quality upgrade generation: `scripts/gen_quality_upgrade.py` (batch 5 clips, detailed prompts)
- Location: `~/culture-en-saveur/`
- **Scripts**: `scripts/build_t1_v3.py` (T1 Cuisine), `scripts/gen_seedance_videos.py` (génération clips IA)
- **Assets**: `assets/book_series/videos/` (clips Seedance), `assets/flags/` (drapeaux flagcdn), `assets/maison_quartier/` (photos lieu)
- **Output**: `output/T1_cuisine_final.mp4`
- **Séries**: T1 (Cuisine 3 pays), T2 (Visio orphelinat), T3 (Nil/écosystème)
- **Détails**: voir `references/zankofa-build-details.md`

## Promo Seedance pattern (intro + IA video + end card)

Quand le client veut tester la génération vidéo IA end-to-end (ex: promo événement), le pattern est:

```
[Intro card PIL 1-2s] → [Seedance 2.0 video 10s] → [End card PIL 2-3s]
```

### End card structure (validé Culture en Saveur)
- Fond: gradient sombre warm (charcoal→terracotta) + radial glow
- Logo (cream circle bg) en haut
- **Dates en gros** (accent color: saffron/terracotta)
- Lieu + tranche d'âge (cream)
- CTA button: téléphone d'inscription (terracotta rounded rect)
- Drapeaux officiels flagcdn.com en bas (cercles masqués)
- Tagline pays: "Égypte · Cameroun · Somalie"

### ⚠️ ffmpeg silent audio for PIL cards
Les images PIL converties en vidéo avec `-loop 1` n'ont **pas de piste audio**. Le concat avec la vidéo Seedance (qui a de l'audio) échoue si les segments n'ont pas tous une piste audio.

### ⚠️ Pitfalls ffmpeg (filterchains)

| Pitfall | Symptôme | Solution |
|---------|----------|----------|
| `zoompan` + `tpad` dans la même filterchain | `Error parsing filterchain` — ffmpeg refuse `zoompan=...,tpad=...` | **Split en 2 passes**: (1) `ffmpeg -ss -t` pour extraire le clip brut, (2) `-stream_loop -vf zoompan` pour le scale+zoom+loop |
| GitHub `google/fonts/raw/` pour télécharger fonts | `file` montre "HTML document" au lieu de "TrueType Font data" | Google Fonts CSS API → gstatic.com (voir `references/brand-alignment-workflow.md` §3) |
| Caractères accentués dans `drawtext text=` | Erreur parsing ou texte coupé | Utiliser `textfile=` avec fichier UTF-8 au lieu de `text=` inline |
| `min()` sans guillemets dans `zoompan z=` | Parse error | Toujours wrapper: `z='min(zoom+0.0005,1.10)'` avec **simple quotes** |
| Character consistency entre clips IA | Visages/tenues changent entre segments — utilisateur signale "alignement des personnages" | Non corrigeable en post-prod. Doit être géré à la génération via pattern #14 (triple identity lock + ref sheet). Voir `references/seedance-prompting-patterns.md` |

**Fix**: générer une piste audio silencieuse pour chaque card:
```bash
ffmpeg -y \
  -loop 1 -t 1.5 -i intro_card.png \
  -f lavfi -i "anullsrc=channel_layout=stereo:sample_rate=44100" \
  -vf "fade=t=in:st=0:d=0.3,fade=t=out:st=1.2:d=0.3" \
  -c:v libx264 -pix_fmt yuv420p -r 24 \
  -c:a aac -b:a 128k -shortest \
  intro_card_video.mp4
```

Sans `anullsrc` + `-c:a aac`, le `concat demuxer` échoue silencieusement (vidéo partiellement assemblée ou erreur).

### Concat mixed sources (re-encode obligatoire)
```bash
# concat_list.txt
file 'intro_card_video.mp4'
file 'seedance_promo.mp4'
file 'end_card_video.mp4'

ffmpeg -y -f concat -safe 0 -i concat_list.txt \
  -c:v libx264 -pix_fmt yuv420p -r 24 \
  -c:a aac -b:a 128k -ar 44100 -ac 2 \
  -movflags +faststart \
  promo_final.mp4
```

**Toujours re-encoder** (`-c:v libx264`), pas `-c copy` — les sources mixtes (PIL stills + Seedance mp4) ont des codecs/timebases différents.

### Référence implémentation
- Script: `scripts/test_seedance_promo.py` (pipeline complet: submit → poll → download → transcode)
- Cards: `scripts/create_cards.py` + `scripts/create_end_card.py` (PIL génération intro/end)
- Output: `renders/promo_final_v1.mp4` (14.2s, 3.2MB, 720×1280)

## Intro/signature branding (série de vidéos)

Quand une série de vidéos promotionnelles partagent la même identité (ex: V1/V2/V3/V4 pour le même événement/client), chaque vidéo doit ouvrir avec une **signature d'intro** cohérente qui identifie immédiatement la marque.

**⚠️ OUBLI FRÉQUENT (juil. 2026)**: l'utilisateur signale "il manque la signature d'introduction aussi ce branding" après livraison. Le build s'est concentré sur le contenu des segments mais a négligé l'opening brand identity.

### Pattern d'intro recommandé (1.5–2.5s)

```
[Intro branding 1.5-2.5s] → [Hook/Title card] → [Segments] → [CTA/End card]
```

L'intro branding contient:
- **Logo** (texte stylisé si pas de logo vectoriel) — animation fade-in + scale
- **Tagline** courte (3 mots max: "Découvrir · Inspirer · Transmettre")
- **Palette officielle** — fond terracotta/ocre, texte crème
- **Audio stinger** court (0.5-1s) synchronisé avec l'apparition du logo

### Implémentation ffmpeg

```python
def make_intro(logo_text, tagline, duration=1.5):
    """Génère un segment d'intro branding animé."""
    # PIL: créer le frame base (logo + tagline sur fond terracotta)
    img = Image.new("RGB", (1080, 1920), (0xA0, 0x39, 0x2B))
    draw = ImageDraw.Draw(img)
    f_logo = ImageFont.truetype(PFAIR, 72)
    f_tag = ImageFont.truetype(POPPINS, 28)
    draw.text(..., logo_text, font=f_logo, fill=(0xF5, 0xE8, 0xD3))
    draw.text(..., tagline, font=f_tag, fill=(0xB5, 0x87, 0x61))

    # FFmpeg: animer avec fade + scale + silent audio pour concat
    cmd = ["ffmpeg", "-y",
        "-loop", "1", "-i", intro_png,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-vf", f"scale=1080:1920,fade=t=in:st=0:d=0.4,fade=t=out:st={duration-0.3}:d=0.3,"
               f"zoompan=z='min(zoom+0.0015,1.05)':d={int(duration*24)}:s=1080x1920",
        "-t", f"{duration:.2f}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "24",
        "-c:a", "aac", "-b:a", "128k", "-shortest",
        str(output)]
```

### Checklist intro branding

Avant de concaténer les segments, vérifier:
- [ ] L'intro branding est le **premier** segment du concat (avant le hook)
- [ ] L'intro utilise les fonts officiels (Playfair/Poppins ou fonts du client)
- [ ] La palette correspond à `research/brand_identity.md`
- [ ] L'audio stinger (si présent) est court et ne déborde pas sur le hook
- [ ] La même intro est réutilisée pour TOUTES les vidéos de la série (consistance)
- [ ] **Choisir le bon type d'intro**: logo statique zoompan (1.5s, simple) OU signature animée frame-by-frame (3s, premium réutilisable). La signature animée vaut le coût de génération pour une série de 3+ vidéos — elle devient l'identité reconnaissable de la marque.

### Variante: intro vidéo vs intro PIL

Si un clip IA existe spécifiquement pour l'intro (ex: main qui épice, vapeur qui monte), utiliser le clip vidéo avec overlay logo au lieu d'un PIL statique:
```python
# B-roll vidéo + logo overlay + fade
vf = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"\
     f"drawbox=x=0:y=750:w=iw:h=400:color=0x492E21@0.7:t=fill,"\
     f"drawtext=fontfile={PFAIR}:textfile=intro_logo.txt:fontsize=72:fontcolor=0xF5E8D3:x=(w-text_w)/2:y=820,"\
     f"fade=t=in:st=0:d=0.4,fade=t=out:st={dur-0.3}:d=0.3"
```

### Variante: signature marketing animée (PIL frame-by-frame)

Pour une signature **réutilisable** (tampon brand reveal 3s identique sur toutes les vidéos d'une série), générer frame-par-frame en PIL puis encoder:

```python
import math
from PIL import Image, ImageDraw, ImageFont

# Animation: stamp drops in (bounce) → content fades → hold → pulse
for frame_num in range(FRAMES):
    t = frame_num / FPS
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img, "RGBA")  # RGBA pour alpha

    # Phase 1 (0-0.5s): cercle terracotta bounce-in
    if t < 0.5:
        progress = t / 0.5
        scale = 1 + 0.3 * (1 - progress) * math.sin(progress * math.pi * 2)
    elif t < 2.5:
        scale = 1.0
    else:
        scale = 1.0 + 0.02 * math.sin((t-2.5) * math.pi * 2)

    # Cercle concentrique (stamp)
    r_outer = int(280 * scale)
    r_inner = int(255 * scale)
    draw.ellipse([cx-r_outer, cy-r_outer, cx+r_outer, cy+r_outer], fill=TERRA)
    draw.ellipse([cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner], fill=CREAM)

    # Phase 2 (0.3s+): contenu fade-in
    content_alpha = min(1.0, max(0, (t - 0.3) / 0.5))
    if content_alpha > 0:
        a = int(255 * content_alpha)
        # Icône + logo text + tagline avec alpha
        draw.text(..., fill=(*TERRA, a))

    # Phase 3 (1.0s+): date/lieu en bas
    if t > 1.0:
        bar_alpha = min(1.0, (t - 1.0) / 0.4)
        # Date + lieu avec fade-in

    img.save(f"/tmp/sig_frames/frame_{frame_num:04d}.png")

# Encode
subprocess.run(["ffmpeg", "-y", "-framerate", "30", "-i", "frame_%04d.png",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-pix_fmt", "yuv420p", "-r", "30", "-an", "signature.mp4"])
```

**Pattern validé** (Culture en Saveur juil. 2026): cercle terracotta + contenu fade + date/lieu. 90 frames à 30fps = 3s. Taille finale ~0.1MB (très léger, réutilisable).

**⚠️ RÈGLE: toujours utiliser le logo OFFICIEL du client quand il existe** (juil. 2026). L'utilisateur a rejeté une signature avec tampon/logo dessiné en PIL et a corrigé: "on va garder le logo officiel". Ne JAMAIS créer une approximation IA d'un élément de branding que le client possède déjà (logo, icône, monogramme). L'authenticité prime sur l'esthétique.

### Technique: signature avec logo officiel opaque

Quand le fichier logo officiel est un PNG RGBA avec fond opaque (pas de vraie transparence — alpha=255 partout), il faut **retirer le fond** avant de l'animer sur un nouveau background:

```python
from PIL import Image

logo = Image.open("logo_officiel.png").convert("RGBA")
bg_pixel = logo.getpixel((5, 5))  # sample corner = background color

# Chroma key: remplacer les pixels proches du fond par transparent
logo_data = list(logo.getdata())
new_data = []
for px in logo_data:
    r, g, b, a = px
    if abs(r - bg_pixel[0]) < 12 and abs(g - bg_pixel[1]) < 12 and abs(b - bg_pixel[2]) < 12:
        new_data.append((r, g, b, 0))  # transparent
    else:
        new_data.append(px)
logo_transparent = Image.new("RGBA", logo.size)
logo_transparent.putdata(new_data)

# Crop au contenu réel
bbox = logo_transparent.getbbox()
logo_cropped = logo_transparent.crop(bbox) if bbox else logo_transparent
```

Puis animer frame-par-frame: fade-in + scale-up (0.85→1.0, easeOutCubic) + hold avec breathing subtil + tagline/date/lieu en bas. **Référence script**: `scripts/build_signature_official.py`.

**Checklist choix signature**:
- [ ] Le client a-t-il un logo officiel (fichier image)? → OUI = l'utiliser, ne pas dessiner
- [ ] Le logo a-t-il un fond opaque? → Chroma key removal obligatoire
- [ ] La signature est-elle réutilisée sur 3+ vidéos? → Investir dans l'animation frame-by-frame
- [ ] Le logo transparent reste-t-il lisible sur le fond crème/terracotta? → Vérifier le contraste

**Préfixer à chaque vidéo de la série**:
```bash
ffmpeg -y -i signature.mp4 -i video.mp4 \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" \
  -map "[v]" -map 1:a \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -r 24 \
  -c:a aac -b:a 192k -movflags +faststart video_branded.mp4
```

**Référence implémentation**: `~/culture-en-saveur/assets/signature_ces.mp4` (3s, 0.1MB). Script: `/tmp/build_signature.py`.

## Insertion de photo réelle dans un segment vidéo existant (Ken Burns)

Quand le client fournit (ou qu'on découvre via `references/visual-asset-discovery.md`)
une photo réelle à intégrer dans une vidéo déjà assemblée, il n'est pas nécessaire
de tout reconstruire. On peut **remplacer une portion d'un segment b-roll** par la photo
avec un effet Ken Burns (zoom lent sur image fixe).

### Pattern: split segment + Ken Burns + re-concat

```
Segment S2 original (16s, tout Seedance b-roll)
  → S2a: 5s du b-roll original (tronqué)
  → S2b: 11s de la photo avec zoompan (Ken Burns)
  → Concat S2a + S2b = nouveau S2 (16s)
  → Re-appliquer lower-third text (drawbox + drawtext)
  → Re-concat dans la timeline globale
```

### Filtre zoompan pour still photo (landscape → portrait crop)

```python
# Photo 1200x900 (landscape) → 1080x1920 (portrait 9:16) avec zoom lent
total_frames = int(photo_dur * FPS)  # ex: 11s * 24fps = 264 frames
vf = (
    f"scale=1188:2112:force_original_aspect_ratio=increase,"  # upscale
    f"crop=1080:1920,"                                          # crop center
    f"setsar=1,"
    # Ken Burns: zoom progressif de 1.0 à 1.08
    f"zoompan=z='min(zoom+0.0003,1.08)':d={total_frames}:s=1080x1920:fps={FPS}"
)

subprocess.run([
    "ffmpeg", "-y",
    "-loop", "1", "-i", str(photo_path),
    "-vf", vf,
    "-t", f"{photo_dur:.2f}",
    "-c:v", "libx264", "-preset", "fast", "-crf", "18",
    "-pix_fmt", "yuv420p", "-r", str(FPS), "-an",
    str(output_clip)
])
```

**Paramètres recommandés**:
- `zoom+0.0003` = zoom très lent (1.0 → 1.08 sur 11s). Pour 5s, utiliser `0.0006`.
- `crf=18` (plus haute qualité que d'habitude car l'image fixe montre chaque artefact).
- Toujours `-loop 1` pour les images statiques.
- `d={total_frames}` obligatoire (sinon zoompan produit 1 seule frame).

### Timing: où couper le segment original

La photo doit apparaître au moment où la VO la mentionne. Par exemple:
- VO S2: *"Culture en Saveurs est née de Linda... Ses parents ont fondé l'orphelinat Joie de Vivre au Cameroun."*
- La mention de l'orphelinat commence à ~4.6s dans le segment.
- Donc: 5s de b-roll intro, puis 11s de photo pendant la mention.

**Règle**: mesurer le timestamp de la mention clé dans la VO (avec Audacity ou en écoutant),
et caler le cut du segment ~0.5s avant ce timestamp pour une transition naturelle.

### Re-concat et rebuild

Après avoir créé le nouveau S2 (S2a + S2b + text overlay), remplacer `v1pro_s2_text.mp4`
par le nouveau segment dans la liste de concat, puis rebuild:
1. Concat tous segments vidéo
2. Mux vidéo + audio (audio inchangé — la VO n'a pas bougé)
3. Burn subtitles
4. Concat signature
5. Compress TG

**Référence script**: `~/culture-en-saveur/scripts/insert_orphelinat_photo.py` (pipeline
complet: split → Ken Burns → concat → text → mux → subs → signature → TG).

## Palette swap — changer la charte d'un build existant (Option A)

Quand un build vidéo existe déjà avec une palette A (ex: Terracotta/Cream) et qu'on veut le réaligner vers une palette B (ex: palette Canva Bleu/Orange/Vert), **ne pas réécrire le script de zéro**. Cloner le script, substituer les constantes, rebuild.

### Workflow (3 étapes)

1. **Identifier toutes les constantes de couleur** dans le script source (grep `0xA0392B`, `CREAM`, `TERRA`, etc.)
2. **Créer un mapping** ancienne palette → nouvelle palette et remplacer en bloc
3. **Adapter les overlays** (`drawbox`, `drawtext`, PIL `ImageDraw`) avec les nouvelles couleurs + fonts

### Template de constantes (script de build Canva-style)

```python
# === CANVA PALETTE ===
BLEU_FONCE = "0x003366"    # Titres principaux (remplace Terracotta)
ORANGE     = "0xFF6600"     # Accents, CTA (remplace Ochre)
VERT       = "0x006600"     # Formes, logo
BLEU_CLAIR = "0x66CCFF"     # Secondaires, subtitles (remplace Cream)
NOIR       = "0x1A1A1A"     # Texte courant
BLANC      = "0xFFFFFF"     # Fond

# RGB tuples pour PIL
RGB_BLEU   = (0x00, 0x33, 0x66)
RGB_ORANGE = (0xFF, 0x66, 0x00)
RGB_VERT   = (0x00, 0x66, 0x00)
RGB_BLEU_C = (0x66, 0xCC, 0xFF)
RGB_NOIR   = (0x1A, 0x1A, 0x1A)
RGB_BLANC  = (0xFF, 0xFF, 0xFF)

# Fonts (remplacer PlayfairDisplay → Montserrat)
MONT_BOLD = "assets/fonts/Montserrat-Bold.ttf"
MONT_REG  = "assets/fonts/Montserrat-Regular.ttf"
```

### Overlays drawtext adaptés (single-pass, b-roll animé derrière)

```python
# Bandeaux top/bottom + lower-third zone + accent orange
vf = (
    f"drawbox=x=0:y=0:w=iw:h=40:color={BLEU_FONCE}@1.0:t=fill,"
    f"drawbox=x=0:y=ih-40:w=iw:h=40:color={BLEU_FONCE}@1.0:t=fill,"
    f"drawbox=x=0:y=1430:w=iw:h=220:color={BLEU_FONCE}@0.78:t=fill,"
    # Accent: barre orange horizontale au-dessus du label
    f"drawbox=x={W//2-120}:y=1442:w=240:h=4:color={ORANGE}@1.0:t=fill,"
    # Label — Montserrat Bold, blanc, dans box orange semi-transparent
    f"drawtext=fontfile={MONT_BOLD}:textfile={lf}:fontsize=26:fontcolor={BLANC}:"
    f"x=(w-text_w)/2:y=1466:box=1:boxcolor={ORANGE}@0.85:boxborderw=14,"
    # Title — Montserrat Bold, blanc, grand
    f"drawtext=fontfile={MONT_BOLD}:textfile={tf}:fontsize=48:fontcolor={BLANC}:"
    f"x=(w-text_w)/2:y=1518,"
    # Subtitle — Poppins Regular, bleu clair
    f"drawtext=fontfile={POPPINS_REG}:textfile={sf}:fontsize=28:fontcolor={BLEU_CLAIR}:"
    f"x=(w-text_w)/2:y=1596"
)
```

### Animated cards (PIL) adaptés

Les title cards et end cards générés en PIL doivent reprendre:
- **Fond blanc** (si palette claire) au lieu de cream/terracotta
- **Barres top/bottom** dans la couleur dominante (bleu foncé)
- **Accent orange** comme séparateur (remplace la ligne ochre)
- **Boutons CTA** en orange avec coins arrondis (`rounded_rectangle`)
- **Cercles colorés** (3-pays card): vert/orange/bleu au lieu de terracotta uniforme

### Sous-titres ASS — conversion couleur

Adapter le style ASS pour matcher la nouvelle palette:

```python
# Style ASS: Montserrat Bold, texte blanc, outline bleu foncé
content = content.replace(
    "Style: Default,Poppins,42,&H00F5E8D3,&H000000FF,&H00492E21,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,80,80,120,1",
    "Style: Default,Montserrat,44,&H00FFFFFF,&H000000FF,&H00003366,&HCC000000,-1,0,0,0,100,100,0,0,1,3,1,2,80,80,120,1"
)
# ASS color format: &HAABBGGRR (alpha + BGR little-endian)
```

### Output séparé

Toujours écrire le build dans un dossier séparé (`renders/pro_build/canva/`) pour ne pas écraser les segments de l'ancienne palette. Le script source original reste intact comme fallback.

### Référence implémentation

Script complet: `~/culture-en-saveur/scripts/build_canva_style.py` — build V1 Pro complet avec palette Canva (7 segments + 3-pays card + end card + subtitles + signature + compression TG).

## Alignement des personnages (cohérence visuelle multi-clips)

**⚠️ Priorité utilisateur** (juil. 2026): quand on recrée le style graphique d'une vidéo multi-segments, l'utilisateur attend que **tous les personnages/enfants gardent la même apparence** à travers les clips. Ce n'est pas juste les couleurs et fonts — c'est la cohérence identitaire des sujets filmés/générés.

**Règle**: lors d'un palette swap ou rebuild, vérifier:
- [ ] Les clips Seedance source gardent les mêmes enfants/personnages à travers les segments (identity lock pattern #14)
- [ ] Si les clips proviennent d'un promo multi-scènes slicé, les personnages doivent être cohérents entre les slices
- [ ] Les photos réelles (ex: orphelinat) utilisées en Ken Burns doivent représenter les mêmes personnes mentionnées dans la VO
- [ ] Ne pas mixer des clips avec des enfants différents entre segments sans transition claire

Voir pattern #14 (triple verrouillage d'identité) dans `references/seedance-prompting-patterns.md` pour la technique de verrouillage facial/corporel multi-clips.

## Extraction de style Canva → reproduction vidéo

Quand le client a une plaquette/flyer Canva existante et veut une vidéo animée cohérente avec ce style: on **reproduit le style** (palette, fonts, formes), jamais on **extrait** les éléments (résolution trop faible + licence Canva). Workflow: OCR Qwen 2.5 VL → ADN graphique → motion design + IA. Voir `references/canva-style-extraction.md`.

## Compléments avec autres skills

| Skill | Usage |
|---|---|
| `cortex-leman-video-brief` | Single-segment 60-90s, Edge TTS base, Pexels stock |
| `le-contre-point-podcast` | Long-form 16:9, ElevenLabs George, multi-slide, Veo b-roll |
| `financial-content-pipeline` | Podcasts multi-voix, guardrail AMF |
| `cloud-music-generation` | Musique de fond (Kie.ai/Suno) |

## Guardrails obligatoires (AVANT tout build)

### GUARDRAIL 1: Validation des clips (anti-loop, anti-gaspillage)
**TOUJOURS** exécuter `scripts/validate_clips.py` avant de lancer un build. Ce script vérifie:
- Qu'aucun clip source n'est utilisé plus d'une fois (loop détecté)
- Que le nombre de clips uniques ≥ nombre de segments stretch
- Que tous les clips référencés existent physiquement

```bash
python3 scripts/validate_clips.py scripts/build_tN_theme.py
# Exit 1 = BLOQUÉ, ne pas lancer le build
```

**Règle**: 1 segment vidéo = 1 clip unique. Si vous avez 3 segments clip mais seulement 1 clip source, **IL MANQUE DES CLIPS** — ne pas looper. Le looping a déjà causé un gaspillage de crédits et une frustration utilisateur.

### GUARDRAIL 2: Validation du contenu (VO ET prompts Seedance) contre le brief client
**TOUJOURS** relire le brief client complet avant d'écrire les textes VO **OU** les prompts Seedance. Erreurs qui ont déjà coûté cher:
- Inventer des activités non prévues ("animaux, plantes, écosystèmes" pour T3 Nil — le brief disait "patrimoine, pyramides, hiéroglyphes")
- Omettre des noms propres importants (orphelinat "Joie de Vivre" pour T2 Visio)
- Rendre flou ce qui est précis dans l'agenda (crire "en classe" au lieu de "Lundi 11h30")
- Oublier une activité phare (sortie au Rhône chaque après-midi)
- **Prompt Seedance V1 ne couvrait que la cuisine → utilisateur: "il manque pas des activités?"** — le brief listait 8 activités (cuisine + anthropologue + henné + contes + thé + djembe + bricolage + visio orphelinat) mais le prompt n'en couvrait qu'une. Chaque activité du brief doit avoir au moins un shot dans le prompt vidéo. L'activité dominante ne doit pas éclipser les autres.

**Checklist VO** avant génération edge-tts:
- [ ] Noms propres du brief présents (orphelinats, lieux, intervenants)
- [ ] Activités citées existent dans l'agenda jour-par-jour
- [ ] Dates, lieux, prix exacts du brief
- [ ] Aucune activité inventée non prévue par le client

**Checklist Seedance prompt** avant submit (narration visuelle):
- [ ] **Extraire la checklist complète d'activités du brief** (grep: activité/atelier/cuisine/peinture/jeu/bricolage/art/visio/henné/contes/musique)
- [ ] Chaque activité → au moins 1 shot dans le prompt Seedance (ex: 8 activités = 8+ shots narrative beats)
- [ ] Noms propres visuellement représentés (orphelinat, pyramides, motifs somaliens)
- [ ] L'activité dominante (ex: cuisine) ne monopolise pas le prompt — diversifier les beats

**⚠️ Cette règle s'applique AUSSI aux images/posters IA** (pas seulement aux clips vidéo). Un poster "programme complet" doit représenter TOUTES les activités du brief, pas seulement les 3 pays principaux. Leçon (juil. 2026): poster généré avec seulement Égypte/Cameroun/Somalie → utilisateur: "il manque le henné, les sortis sur le bord du leman". Le prompt V2 a intégré henné + thé/contes + visio orphelinat + anthropologue + musique + sorties Rhône → accepté. **Pour tout visuel de synthèse (poster programme, flyer global, affiche récap), relire le brief et lister chaque activité avant de rédiger le prompt image.**

### GUARDRAIL 3: Ordre de génération clips IA
1. Écrire les VO depuis le brief (pas inventées)
2. Pour chaque segment clip, vérifier qu'un clip unique existe ou créer un prompt
3. Compter: segments needing clips vs clips available → gap = clips à générer
4. Vérifier solde de crédits avant de lancer la génération Seedance
5. **JAMAIS lancer un build tant que tous les clips ne sont pas prêts**

### GUARDRAIL 4: Cohérence visuelle avec l'existant (anti-rupture de style)
**AVANT** de recommander ou d'appliquer un nouveau style visuel (pattern IA, effet artistique, générateur image) sur un projet client existant, **TOUJOURS**:

1. **Auditer l'identité en place** — examiner les assets existants du projet (logo, photos réelles reçues du client, feed FB/IG, cards déjà produites, code graphique établi)
2. **Extraire la palette réelle** — utiliser PIL `Image.getcolors()` sur les assets existants pour confirmer les couleurs dominantes, pas se fier à la mémoire
3. **Vérifier la compatibilité** — un style illustratif/whimsical (ex: papercraft, watercolor, anime) RUPTURE avec un feed photo-réaliste authentique. Si le client poste déjà des photos réelles (enfants, ateliers, plats), un nouveau style illustratif doit être classé hors-feed
4. **Définir le périmètre** — Feed FB/IG = rester dans le registre établi (photo-réaliste ou IA photo-réaliste). Supports hors-feed (flyers, posters impression, cartes fin de camp, couvertures album) = style illustratif acceptable
5. **Adapter la palette du pattern** — remplacer les couleurs du prompt original par la charte du projet (ex: pas de "soft pastel skies" si la charte est terracotta/cacao/crème)

**Leçon (Culture en Saveur, juil 2026):** l'agent a recommandé un style papercraft travel poster pour le projet sans vérifier le feed FB/IG existant. L'utilisateur a corrigé: "faut garder le visuel qui a été fait auparavant comme sur leur page Facebook". Le feed existant est photo amateur authentique (enfants en activité, lumière naturelle). Le papercraft a été reclassé: supports impression uniquement. **La règle générale: un nouveau pattern visuel trouvé sur X/Twitter ne s'applique à un projet existant qu'après audit de compatibilité, jamais par défaut.**

**Trouver des photos réelles d'une organisation/lieu**: quand le brief mentionne une organisation spécifique (orphelinat, association, école) et que le client n'a pas fourni de photos, la méthodologie de découverte multi-plateforme (site officiel galeries JS, cross-page Facebook discovery, comptes IG affiliés) est documentée dans `references/visual-asset-discovery.md`. Cas validé: Orphelinat Joie de Vivre (Banfelouk, Cameroun) — 6 photos récupérées depuis 3 sources en ~30 min.

## Brand identity alignment (réalignement charte officielle)

Quand un client transmet ses documents graphiques officiels (roll-up, flyer, logo) en cours de projet, TOUS les assets existants (title cards, CTA cards, sous-titres, promos) doivent être réalignés à la charte réelle.

### Workflow (obligatoire)

1. **Extraire l'identité** depuis les documents reçus:
   - PDF → `pdftoppm -png -r 200 input.pdf /tmp/page` pour rendre les pages en image
   - Image → PIL `getcolors()` pour extraire la palette dominante réelle (pas se fier à la mémoire)
   - OCR du texte → Qwen 2.5 VL 72B via OpenRouter (voir pitfall #9) pour extraire taglines, contacts, slogans
2. **Créer une source de vérité** `research/brand_identity.md` contenant: palette hex officielle, typographies, taglines, coordonnées, valeurs à projeter. Ce fichier devient la référence pour TOUS les futurs builds.
3. **Télécharger les fonts officiels** depuis Google Fonts (GitHub raw URLs)
4. **Créer un générateur de cartes unifié** `scripts/gen_brand_cards.py` qui produit toutes les cartes (title, CTA, hook) en une seule exécution, avec la charte officielle
5. **Patcher les styles ASS** dans tous les build scripts: nom de font + couleurs ASS (RGB → `&HAABBGGRR`)
6. **Reconstruire** toutes les vidéos (séquentiellement, pas en parallèle — voir pitfall #16)

### Variables fonts Google Fonts — RÈGLE

**Toujours** utiliser le variable font (fichier unique) avec `set_variation_by_axes()`, jamais les URLs GitHub de fichiers statiques séparés qui retournent souvent du HTML 404 silencieusement.

```python
# ✅ CORRECT — variable font, poids dynamique
path = f"{FONT_DIR}/PlayfairDisplay-Variable.ttf"
fnt = ImageFont.truetype(path, size)
weight_map = {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}
fnt.set_variation_by_axes([weight_map.get(weight, 700)])

# ❌ FAUX — GitHub raw URLs retournent du HTML pour les fichiers statiques
curl -sL "https://github.com/google/fonts/raw/main/ofl/playfairdisplaystatic/PlayfairDisplay-Bold.ttf"
# → file format: HTML document (erreur 404 de GitHub)
```

**Vérifier** après téléchargement: `file font.ttf` doit afficher "TrueType Font data", pas "HTML document".

### ASS subtitle color conversion

Convertir RGB → ASS `&HAABBGGRR` (alpha + BGR inversé):

```python
def to_ass(rgb):
    r, g, b = rgb
    return f"&H00{b:02X}{g:02X}{r:02X}"

# Crème (0xF5, 0xE8, 0xD3) → &H00D3E8F5
# Cacao (0x49, 0x2E, 0x21) → &H00212E49
```

Le format ASS encode: byte 0 = alpha (00=opaque), puis BGR en little-endian.

### Validation post-build

Après réalignement, vérifier que TOUTES les cartes contiennent la terracotta officielle:

```python
from PIL import Image
img = Image.open("title_card.jpg").convert("RGB")
colors = img.getcolors(maxcolors=65536)
terracotta_found = any(
    abs(c[0]-0xA0)<40 and abs(c[1]-0x39)<30 and abs(c[2]-0x2B)<30
    for count, c in colors
)
```

Puis validation visuelle via Qwen 2.5 VL 72B (OpenRouter) qui lit le texte et confirme les couleurs.

### Référence implémentation
- Charte source: `~/culture-en-saveur/research/brand_identity.md`
- Générateur cartes: `~/culture-en-saveur/scripts/gen_brand_cards.py`
- Fonts: `~/culture-en-saveur/assets/fonts/` (PlayfairDisplay-Variable.ttf + Poppins-*.ttf)
- **Workflow complet détaillé**: `references/brand-alignment-workflow.md`

## Téléchargement fiable de Google Fonts (méthode CSS API)

GitHub raw URLs (`github.com/google/fonts/raw/.../FontName-Bold.ttf`) retournent systématiquement du HTML (page 404/login) au lieu du fichier binaire TTF. Le `file` du téléchargé affiche `HTML document` et PIL échoue avec `OSError: unknown file format`.

**Méthode fiable** — Google Fonts CSS API → extraire les URLs `fonts.gstatic.com`:

```python
import urllib.request, re

css_url = "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap"
req = urllib.request.Request(css_url, headers={"User-Agent": "Mozilla/5.0"})
css = urllib.request.urlopen(req, timeout=10).read().decode()

# Parser les bloces @font-face pour extraire weight → URL
blocks = css.split("@font-face")
urls = {}
for block in blocks:
    weight_m = re.search(r"font-weight:\s*(\d+)", block)
    url_m = re.search(r"src:\s*url\((https://[^)]+)\)", block)
    if weight_m and url_m:
        urls[weight_m.group(1)] = url_m.group(1)

# Télécharger chaque poids
mapping = {"400": "Montserrat-Regular.ttf", "600": "Montserrat-SemiBold.ttf", "700": "Montserrat-Bold.ttf"}
for weight, fname in mapping.items():
    if weight in urls:
        urllib.request.urlretrieve(urls[weight], fname)
```

**Toujours vérifier** après téléchargement: `file Font.ttf` doit afficher `TrueType Font data`, pas `HTML document`.

Cette méthode fonctionne pour TOUTES les polices Google Fonts (Montserrat, Poppins, Playfair, etc.). Le User-Agent header est obligatoire — sans lui, l'API retourne une CSS simplifiée sans les URLs `fonts.gstatic.com`.

## External LLM Audit Pattern (Pre-Delivery Review)

Before finalizing a full video series, send the complete project context to an external model (Claude Sonnet 4 via OpenRouter) for a critical audit. This catches narrative gaps, missing trust elements, and marketing confusion that tunnel-visioned production misses.

### When to audit
- After completing 3+ videos in a series
- Before delivering to client
- When user asks "regardons si nous devons retoucher quelque-chose"

### Audit prompt structure
Send: (1) project context summary, (2) per-video VO scripts, (3) visual segment descriptions, (4) ask for: narrative coherence, message clarity, trust gaps, risks, top 5 recommendations, critical missing elements.

### Common audit findings (from Culture en Saveur Jul 2026)
| Finding | Fix |
|---------|-----|
| No adult/animator visible | Add Seedance clips with animatrice guiding children |
| Unclear program (what do kids DO?) | Create "Programme" video with day-by-day planning |
| No trust signals (safety, allergies, certifications) | Add info cards: lieu, horaires, protocole allergies, animatrice certifiée |
| Too many concepts in one series | Each video = one clear theme (cuisine, visio, écologie, programme) |
| Contact looks unprofessional | Upgrade from WhatsApp-only to web/form + phone + email |

### Trust/Safety card elements (for children's programs)
When building info cards for youth programs (camps, ateliers, associations):
- **Lieu précis**: Full address/neighborhood
- **Horaires**: Drop-off/pickup times
- **Encadrement**: Animator name + qualification ("animatrice certifiée")
- **Sécurité**: Allergy protocol, insurance RC mention
- **Prix transparent**: What's included (meals, materials)
- **Places limitées**: Creates urgency + implies quality supervision

## Pitfalls (video assembly)

Specific to building/encoding video files:

2. **Drapeaux PIL = rejet utilisateur** → l'Aigle de Saladin dessiné à la main est méconnaissable. Utiliser `flagcdn.com/w640/{code}.png`.

3. **Clip VO non-sync** → chaque clip DOIT être stretché (`setpts`) à la durée exacte de sa VO. Une VO qui déborde sur le clip suivant = désynchronisation.

4. **`--write-audio` obsolète** → `--write-media` depuis July 2026. Fichier 0-byte = flag erroné.

5. **`fr-CH-HenriNeural` supprimé** → toujours vérifier voix avec `--list-voices` avant hardcoded. Remplacement validé: `fr-FR-DeniseNeural`.

6. **Overlay drapeau sur clip vidéo rejeté** → l'utilisateur préfère les drapeaux uniquement sur le title card, pas sur chaque clip. **Ne pas ajouter d'overlays sur les clips par défaut.** Si l'utilisateur les demande, les faire faciles à retirer.

7. **Drapeaux trop proches / chevauchement** → spacing minimum 120px entre drapeaux 180×120px. Sans cela, le drapeau égyptien (large avec aigle) empiète sur le camerounais.

8. **Fond trop sombre** → 55% d'assombrissement rend le bâtiment invisible. Utiliser 30%. Le texte reste lisible grâce à son outline, pas besoin d'un fond noir.

9. **Vision analyze GLM-5.2 error 1210** → fallback Qwen 2.5 VL 72B via OpenRouter (excellent OCR FR) pour vérification texte + couleurs. Alternative: numpy/PIL pixel analysis pour couleurs seulement. `vision_analyze` échoue avec GLM-5.2 car le modèle n'accepte que le texte (error 1210: "messages.content.type is invalid, allowed values: ['text']"). **⚠️ Nom de modèle OpenRouter**: `qwen/qwen2.5-vl-72b-instruct` et `qwen/qwen-2.5-vl-72b-instruct` fonctionnent. Le suffixe `:free` (`qwen/qwen-2.5-vl-72b-instruct:free`) → 404 "No endpoints found" — ce modèle n'a pas de tier free, utiliser l'identifiant sans suffixe. Script: `scripts/vision_check.py`.

10. **Clips Seedance IA (5s chacun)** → coûte ~165 crédits/clip sur Kie.ai. Générer tous les clips en un batch. Voir `references/zankofa-build-details.md` pour le pipeline Seedance complet. **Pour le prompting des clips**, voir `references/seedance-prompting-patterns.md` — bibliothèque de 7 patterns vidéo (A: identity lock, B: epic 6-shot, C: LLM storybreaker, D: raw UGC, E: travel vlog, F: dark cinematic epic, G: commercial brand content) + 2 patterns image (H: mixed-media collage, I: papercraft travel poster Seedream 5.0) + Dreamina comme alternative 4K à kie.ai. **Pour la génération programmatique** via API kie.ai, voir `templates/seedance_generate.py` (script standalone) et `references/kieai-seedance-api.md` (doc endpoints vidéo, params, pricing). **Pour la génération d'images Seedream 5.0** (posters, flyers, visuels impression), voir `references/kieai-seedream-image-api.md` (doc endpoints image, pitfalls camelCase, timeout 16:9). **Pour un template de promo événementiel multi-activité** (Pattern G appliqué avec checklist complète d'activités du brief), voir `references/seedance-promo-event-template.md`.

20. **API kie.ai camelCase + timeout Seedream 16:9** → 3 pièges concomitants lors de la génération d'images Seedream 5.0 via API directe: (a) `data.taskId` en camelCase, pas `task_id` → KeyError silencieux; (b) `state: "success"` en minuscule → un check `if state in ("SUCCEEDED","SUCCESS")` ne matche jamais, boucle infinie jusqu'au timeout; (c) le `KieClient.gen_image()` interne a un timeout de 300s, insuffisant pour les prompts 16:9 complexes (~330s en pratique) → l'image EST générée côté serveur mais le client timeout avant de la récupérer. **Fix**: appeler l'API directement avec timeout=600s, parser `data["taskId"]`, checker `state == "success"`, puis `json.loads(data["resultJson"])["resultUrls"][0]`. Référence script: `~/culture-en-saveur/scripts/gen_papercraft_programme_v2.py`. Voir `references/kieai-seedream-image-api.md`.

11. **Arrêter un build en cours** → l'utilisateur peut demander d'arrêter ("non arrête le build si tu n'a pas lancé"). Toujours avoir le `session_id` du process background en main pour `process kill` immédiat. Ne pas relancer sans instruction explicite.

12. **Multiplication de vidéos de série** → les scripts de build (T1, T2, T3) sont presque identiques. Le template `templates/build_shorts.py` est la base. Créer un script par vidéo (build_tN_theme.py) qui diffère uniquement par: VO_SEGMENTS, title card text, clip sources, accent color.

16. **JAMAIS de builds ffmpeg en parallèle sur CPU** → lancer 2+ scripts de build simultanément (background) fait que les deux `ffmpeg` finaux (avec `subtitles` + `filter_complex` + `amix`) se disputent le CPU et **hangent indéfiniment** à l'étape "FINAL BUILD". Solution: lancer **séquentiellement en foreground** (`timeout=300`), jamais en parallèle. Un build seul en foreground prend ~20-30s sur CPU; deux en parallèle ne terminent jamais.

17. **Download Seedance direct = 403 Forbidden** → les URLs `tempfile.aiquickdraw.com` dans `resultUrls` refusent le download direct. **Toujours** passer par `POST /api/v1/common/download-url` qui génère une URL Cloudflare R2 signée (valide 20 min). Le template `seedance_generate.py` fait déjà ceci dans `download_video()`.

18. **PIL cards sans piste audio brisent le concat** → les images PIL converties via `-loop 1 -t {dur}` n'ont pas d'audio. Concaténer avec une vidéo Seedance (qui a audio) → échec. Fix: ajouter `-f lavfi -i "anullsrc=channel_layout=stereo:sample_rate=44100"` + `-c:a aac -shortest` lors de la création du card vidéo.

19. **Concat mixed sources nécessite re-encode** → PIL cards (libx264) + Seedance mp4 (timebase/codec potentiellement différent) → `-c copy` échoue. Toujours utiliser `-c:v libx264 -c:a aac` lors du concat final.

14. **Looper un clip pour remplir des segments vides = GASPILLAGE** → Si vous avez 1 clip pour 3 segments, NE PAS looper le même clip 3x. Cela produit une vidéo répétitive que l'utilisateur remarque immédiatement ("pourquoi nous avons un seul clip à la fois"). L'utilisateur paie pour les clips IA en crédits — looper = gaspillage des crédits déjà dépensés sur le build. Solution: générer les clips manquants AVANT le build (voir Guardrail 3).

15. **VO inventée non basée sur le brief = ERREUR GRAVE** → L'utilisateur exige que chaque détail VO corresponde à l'agenda client. Erreurs typiques: inventer "écosystème, animaux, plantes" au lieu de "pyramides, hiéroglyphes"; omettre le nom de l'orphelinat; écrire "en classe" au lieu du créneau précis. **Relire le brief intégral avant chaque VO** (voir Guardrail 2).

16. **GitHub raw font URLs retournent du HTML** → les URLs `github.com/google/fonts/raw/main/ofl/.../FontName-Bold.ttf` retournent souvent un HTML 404 qui PIL charge silencieusement puis échoue avec `OSError: unknown file format`. **Toujours** utiliser le variable font (fichier unique) avec `set_variation_by_axes()` pour les poids. Vérifier avec `file font.ttf` après téléchargement.

21. **PIL `ImageFont.truetype(path, size, index=N)` échoue sur variable fonts** → un variable font `.ttf` contient plusieurs instances nommées (Regular, Medium, SemiBold, Bold...). PIL ne supporte pas le paramètre `index=` de manière fiable pour sélectionner un poids dans un variable font — il peut retourner `OSError: invalid argument` ou charger le mauvais poids silencieusement. **Utiliser `set_variation_by_axes()`** pour les variable fonts, et garder les fichiers statiques (Bold.ttf, SemiBold.ttf) séparément pour `ImageFont.truetype()` direct quand `set_variation_by_axes` n'est pas disponible.

```python
# ✅ CORRECT — variable font + set_variation_by_axes
path = f"{FONT_DIR}/PlayfairDisplay-Variable.ttf"
fnt = ImageFont.truetype(path, 56)
fnt.set_variation_by_axes([700])  # 400=Regular, 700=Bold

# ✅ AUSSI CORRECT — fichier statique séparé (si disponible)
fnt = ImageFont.truetype(f"{FONT_DIR}/PlayfairDisplay-Bold.ttf", 56)

# ❌ FAUX — index=3 sur variable font → OSError ou mauvais poids
fnt = ImageFont.truetype(path, 56, index=3)
```

22. **Vérifier les fichiers font après téléchargement** → utiliser `file font.ttf` (commande shell). Un `.ttf` valide affiche `TrueType Font data`. Un fichier HTML affiche `HTML document`. **Toujours** vérifier avant de référencer dans un script de build — un font corrompu fait échouer PIL au runtime, pas au chargement du script.

17. **ImageDraw.Draw(img) oublié après draw_gradient_bg** → quand on dessine un gradient avant le texte, l'objet `draw` utilisé pour le gradient n'est pas le même que celui qui crée `ImageDraw.Draw(img)`. Toujours appeler `draw = ImageDraw.Draw(img)` APRÈS `draw_gradient_bg()` et AVANT tout `draw.text()`. `NameError: name 'draw' is not defined` = cette erreur.

18. **FFmpeg timeout → fichier corrompu sans moov atom** → si un timeout (foreground ou background) interrompt ffmpeg pendant l'encodage, le fichier `.mp4` est créé sur disque mais **incomplet**: le moov atom (metadata) n'est jamais écrit. Le fichier existe (`ls` montre la taille), `ffprobe` retourne "Invalid data found" ou "moov atom not found", et le lecteur vidéo échoue silencieusement. Toujours vérifier avec `ffprobe -v error` après chaque encodage, même quand le fichier existe. Fix: relancer avec un timeout généreux (timeout=300 pour vidéos <60s). Vérifier avec: `python3 -c "data=open('file.mp4','rb').read(100000); print('OK' if b'moov' in data else 'CORRUPT')"`.

19. **"Pas de son" = audio inaudible, pas absent** → l'utilisateur dit "pas de son" même quand ffprobe confirme une piste AAC valide. Diagnostic multi-couches obligatoire: (1) ffprobe show_streams confirme la piste existe; (2) ffmpeg -af volumedetect donne le mean_volume — si < -20 dB, c'est inaudible sur mobile; (3) analyse FFT pour vérifier que l'énergie est dans la bande voix (300-3400Hz) et pas en bourdonnement basse-fréquence (top freqs <100Hz = musique qui écrase la VO). Un fichier avec -29 dB RMS et top freqs à 70Hz = l'utilisateur entend un mur de basse, pas la voix. Fix: normalize=0 sur amix + VO à volume=2.5 + musique à 0.12. Script de diagnostic: scripts/audio_analysis.py (wave puis RMS par segment puis FFT speech band %).

20. **Compression TG n'amplifie pas l'audio** → ré-encoder pour Telegram avec -c copy ou sans filtre audio préserve le niveau faible. Le boost volume=15dB,alimiter=limit=0.95 aide mais le vrai fix est à la source: corriger le mix amix dans le build script (pitfall #19), pas dans la compression TG. Toujours d'abord fixer le build source, ensuite compresser pour TG avec le même boost pour double garantie.

21. **`stream_loop` >1.5x = loops visibles** → un clip 5s loopé pour un segment 9-14s produit une répétition évidente que l'utilisateur remarque ("loops"). Le calcul `loops = max(1, int(dur / src_dur) + 1)` sans garde-fou génère 2-3 répétitions du même contenu. Règle: si segment > 1.5× clip source, utiliser Ken Burns sur still OU deux clips différents avec crossfade. Voir section "Extension b-roll court" pour la table de décision complète.

22. **Musique percussive continue = désync perçue** → une musique avec tambours/djembé mixée en volume fixe (même ducked à 0.12) donne l'impression que les percussions ne suivent pas le speech ("tes tambours c'est pas synchronisés"). Cause: le volume constant ne distingue pas "VO active" de "VO en pause". Fix: ducking sidechain OU interludes musicaux entre segments OU préférer ambient/mélodique quand ducking non implémenté. Voir section "Ducking automatique".

23. **Oubli de l'intro/signature branding** → après avoir concentré le build sur les segments contenu, l'utilisateur signale "il manque la signature d'introduction aussi ce branding". Toujours inclure un segment d'intro branding (1.5-2.5s) avec logo + tagline + palette officielle comme PREMIER élément du concat, avant le hook. Voir section "Intro/signature branding".

24. **Asset gap non communiqué avant build** → quand la bibliothèque ne couvre pas tous les segments du brief (ex: henné, tambours, sport absents), lancer le build quand même en réutilisant des clips non-pertinents produit une vidéo qui rate des activités clés ("tu as raté l'art du henné"). **Toujours**: (1) inventorier les assets vs besoins du brief AVANT le build, (2) identifier les gaps explicites, (3) communiquer les gaps + options (recharge crédits / images statiques / Ken Burns) à l'utilisateur AVANT de lancer, pas après la livraison.

25. **ffmpeg filter labels = stream specifiers** → les labels `[vo]`, `[voc]`, `[n]`, `[m]`, `[v]` dans un `-filter_complex` sont interprétés comme des stream specifiers (v=video, a=audio) → erreur "Stream specifier 'X' matches no streams" / "Invalid argument". **3 échecs consécutifs** observés avant diagnostic. **Fix**: utiliser des labels multi-syllabes (`[bg]`, `[ducked]`, `[out]`) ou splitter en passes séparées avec fichiers WAV intermédiaires. Voir section "Sidechain ducking — pattern 3 passes".

26. **VO concat tronquée** → `ffmpeg -f concat` sur des MP3 edge-tts peut produire un fichier beaucoup plus court que la somme des durées (22s au lieu de 73s) sans erreur. Cause: différences de sample rate ou format entre les fichiers MP3 individuels. **Fix**: toujours vérifier la durée du fichier concaténé avec `ffprobe` avant de l'utiliser dans le mix audio. Si la durée est incorrecte, utiliser un pré-concat en WAV (`-c:a pcm_s16le`) puis encoder en AAC, ou générer un `v1_full.mp3` consolidé en une passe edge-tts si possible.

27. **Signature marketing animée PIL frame-by-frame** → pour une signature réutilisable (tampon/brand reveal 3s), générer N frames PIL avec animation math (bounce easing, fade alpha, scale pulse) puis encoder avec `ffmpeg -framerate 30 -i frame_%04d.png`. Pattern validé (Culture en Saveur juil. 2026): cercle terracotta qui bounce-in + contenu fade-in + date/lieu en bas. La signature est préfixée à chaque vidéo via `[0:v][1:v]concat=n=2:v=1:a=0`. **Ne pas oublier l'audio**: si la signature n'a pas d'audio et la vidéo oui, le concat `a=0` préserve l'audio de la vidéo principale (`-map 1:a`).

28. **Ne jamais dessiner un logo/branding que le client possède déjà** → l'utilisateur a rejeté une signature avec tampon terracotta dessiné en PIL et corrigé: "on va garder le logo officiel". Si le projet contient un fichier logo officiel (`logo_*.png`, `brand_identity.md` mentionnant un logo), **toujours** l'utiliser comme base de la signature/branding, jamais le remplacer par une approximation dessinée. Technique: chroma-key removal du fond opaque du logo (`remove_background()`), crop au bbox, puis animation frame-by-frame (fade+scale+hold). Script: `scripts/build_signature_official.py`. L'authenticité de la marque prime sur l'esthétique de l'animation.

29. **Multi-passes FFmpeg → corruption moov atom → préférer single-pass** (juil. 2026) → un build en 4 étapes séparées (build vidéo segments → concat → mux audio → burn subtitles → concat signature) timeout à 300s et laisse un `V1_PRO_branded.mp4` corrompu (moov atom not found). Le fichier existe sur disque mais `ffprobe` retourne "Invalid data found". **Fix**: combiner subtitles + signature concat en **une seule passe** `filter_complex`:
```bash
ffmpeg -y \
  -i muxed.mp4 \
  -i signature.mp4 \
  -filter_complex "
    [0:v]subtitles='subs.ass',setpts=PTS-STARTPTS[v0];
    [1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,setpts=PTS-STARTPTS[v1];
    [v0][v1]concat=n=2:v=1:a=0[v]
  " \
  -map "[v]" -map "0:a" \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p -r 24 \
  -c:a aac -b:a 192k -movflags +faststart \
  output_final.mp4
```
Avantages: 1 encode au lieu de 3, pas de fichiers intermédiaires corrompus, timeout réduit de 300s à ~120s.

30. **Générer de nouveaux clips IA plutôt que recycler** (préférence utilisateur juil. 2026) → l'utilisateur a explicitement demandé "génère de nouveau clips vidéos sans prendre les anciennes" même quand d'anciens clips existent et sont réutilisables. **Préférence: fresh content > recycled content** quand le budget crédits le permet. Vérifier le solde KIE avant de décider. Si >200 crédits et 4 clips à générer (~165 crédits/clip = ~660 nécessaires), préférer générer du neuf. Ne recycler un ancien clip que: (a) si l'utilisateur le demande explicitement (ex: "garde le clip 1:01-1:02"), ou (b) si le budget ne permet pas la génération neuve.

31. **Anti-générique: systématiquement comparer au brief/source** (préférence utilisateur juil. 2026) → l'utilisateur a corrigé plusieurs fois que le contenu était "trop générique". Énoncé explicite: "assure de toujours comparer les données pour pas être dans le générique". **Règle**: avant chaque build, relire la source de vérité (questionnaire, brief, entretien) et vérifier que chaque segment contient des **détails spécifiques** (noms propres, lieux, dates, histoire personnelle), pas des affirmations génériques applicables à n'importe quel projet. Exemple:
   - ❌ "Une femme métisse a créé cette association" (générique)
   - ✅ "Linda, femme métisse. Ses parents ont fondé l'orphelinat Joie de Vivre au Cameroun. Elle s'y rend régulièrement." (spécifique)

32. **OCR assets via Qwen 2.5 VL — script `scripts/vision_check.py`** (juil. 2026) → `vision_analyze` (outil Hermes) échoue systématiquement avec GLM-5.2 (error 1210: "messages.content.type is invalid, allowed values: ['text']"). **Fallback validé**: script Python qui envoie l'image (base64) à Qwen 2.5 VL 72B via OpenRouter API pour OCR + analyse visuelle. Utiliser pour: (a) OCR de documents/images du projet, (b) vérification visuelle de frames vidéo (contact sheet), (c) validation de couleurs/texte après build. Script: `scripts/vision_check.py` (encode base64, POST OpenRouter, print response). Limitation: 1 image par appel (pas de batch natif). Usage: `python3 scripts/vision_check.py <image_path> [question]`.

33. **`-shortest` coupe le dernier mot de la VO** (juil. 2026) → le mux final vidéo+audio avec `-shortest` tronque la VO de ~2.7s, assez pour couper le mot final ("Transmettre"). L'utilisateur a signalé "il manque le mot transmettre à la fin". **Cause racine**: non pas `-shortest` seul, mais un **segment vidéo trop court** (S6 = 8s au lieu de 12.2s à cause de cuts mal calculés en Python : `dur_s6/4 = 3.06` mais les cuts originaux étaient à `2.0s` fixes). Le segment court fait que la vidéo concaténée (94s) < VO (96.7s), et `-shortest` coupe l'audio. **Règle de vérification OBLIGATOIRE avant mux final**:
    ```bash
    # Vérifier que video_dur >= vo_dur (sinon l'audio sera coupé)
    video_dur=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 video.mp4)
    vo_dur=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 vo_full.mp3)
    python3 -c "vd,ad=float('$video_dur'),float('$vo_dur'); print(f'MISMATCH: video {vd:.1f}s < VO {ad:.1f}s, {-vd+ad:.1f}s cut') if vd < ad else print(f'OK: video {vd:.1f}s >= VO {ad:.1f}s')"
    ```
    Si `video_dur < vo_dur`, le segment le plus court est le coupable — vérifier chaque segment avec ffprobe et reconstruire celui qui est sous-dimensionné.

34. **Encodage AAC intermédiaire tronque ~0.2s** (juil. 2026) → le mix audio `sidechaincompress + amix` encodé en `.aac` perd ~0.2s en queue (96.45s au lieu de 96.67s). Sur 3 mots finaux ("Découvrir. Inspirer. Transmettre."), 0.2s = le dernier mot coupé. **Fix**: produire le mix en **WAV** (`-c:a pcm_s16le`) au lieu de AAC pour l'étape intermédiaire, puis laisser le mux final faire l'encodage AAC:
    ```bash
    # ✅ Mix en WAV (préserve durée exacte)
    ffmpeg -y -i music_prep.wav -i vo_boost.wav \
      -filter_complex "...amix=inputs=2:duration=longest:normalize=0[out]" \
      -map "[out]" -c:a pcm_s16le audio_mix.wav   # WAV, pas AAC

    # Puis mux final (WAV → AAC UNE seule fois, au mux, pas avant)
    ffmpeg -y -i video.mp4 -i audio_mix.wav \
      -map 0:v -map 1:a -c:v libx264 -c:a aac -b:a 192k output.mp4
    ```
    **Règle**: ne jamais encoder en AAC deux fois. Un seul passage AAC, au mux final. Toutes les étapes intermédiaires en WAV (`pcm_s16le`).

36. **Background ffmpeg processes en série → races sur fichiers intermédiaires** (juil. 2026) → quand un build vidéo nécessite plusieurs étapes ffmpeg dépendantes (signature concat → compression TG), les lancer comme background processes **séparés** provoque une race condition: le second process lit le fichier de sortie du premier **avant** que celui-ci ait fini d'écrire le moov atom. Résultat: `ffprobe` retourne "moov atom not found" ou "Invalid data found", le fichier semble exister sur disque (`ls` montre une taille) mais est corrompu. **Fix**: (a) chaîner les étapes dépendantes dans **un seul** script bash avec `&&` entre chaque commande ffmpeg, lancé comme un seul `terminal(background=true)` — le `&&` garantit que l'étape N+1 ne démarre qu'après le code de sortie 0 de l'étape N; (b) ne jamais lancer un second `terminal(background=true)` qui dépend du fichier de sortie d'un premier background encore en cours; (c) si on doit absolument séquentialiser via `process wait`, toujours vérifier `ffprobe -v error` sur le fichier intermédiaire avant de le consommer.

37. **Zoompan CPU-intensif + Python subprocess timeout → fichier tronqué mais valide** (juil. 2026) → un script Python (`subprocess.run(capture_output=True)` par défaut sans timeout explicite, mais tué par le timeout terminal de 300s) qui enchaîne plusieurs appels ffmpeg dont un `zoompan` sur image fixe peut dépasser le budget pendant le burn des sous-titres. Le fichier de sortie **existe et est techniquement valide** (moov atom présent grâce à `+faststart`, ffprobe le lit sans erreur) mais sa **durée est tronquée** (89s au lieu de 96.7s). L'utilisateur perçoit une coupure en fin de vidéo.

    **Cause racine**: `zoompan` sur une image fixe de 11s à 24fps = 264 frames × computation scale+crop+zoom = ~0.2x speed sur CPU (~55s pour 11s de vidéo). Si le pipeline Python fait split → Ken Burns → concat → text → mux → burn subs → signature → compress, le zoompan + le burn subs (re-encode complet) accumulent ~200s, proches du timeout 300s.

    **Diagnostic OBLIGATOIRE après chaque build multi-étapes** (pas juste ffprobe "existe"):
    ```bash
    # Vérifier que la durée de sortie = durée attendue
    expected=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 muxed_source.mp4)
    actual=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 output_final.mp4)
    python3 -c "
    e,a=float('$expected'),float('$actual')
    if a < e - 0.5: print(f'TRUNCATED: output {a:.1f}s vs expected {e:.1f}s, {e-a:.1f}s lost')
    else: print(f'OK: {a:.1f}s ≈ {e:.1f}s')
    "
    ```

    **Fix**: (a) ne JAMAIS wrapper un pipeline ffmpeg multi-étapes dans un seul script Python `subprocess.run` — préférer un script bash unique avec `&&` entre étapes, lancé via `terminal(background=true, timeout=600)`; (b) si on découvre qu'une étape a été interrompue (durée tronquée), identifier le **dernier fichier intermédiaire valide** (ex: `muxed.mp4` à 96.7s) et re-runner **uniquement** les étapes à partir de ce point, pas tout reconstruire; (c) pour les zoompan sur images fixes, utiliser `-preset ultrafast` (l'image fixe supporte une compression agressive sans perte visible) et `threads=0`.

35. **End card incomplet vs flyer officiel — données manquantes + typos** (juil. 2026) → L'utilisateur a demandé "vérifie que tous les éléments du flyer sont dans la vidéo". La vérification a révélé que l'end card omettait: âge (4-12 ans), prix (85/55 CHF), horaires (8h30-13h30 / 13h30-18h30), réduction sibling (-10%), et contenait une **typo email** (`cultureensaveurs@gmail.com` avec S au lieu de `cultureensaveur@gmail.com` sans S) propagée sur 16 occurrences dans les scripts. **Règle**: avant de générer un end card, extraire SYSTÉMATIQUEMENT chaque élément de données du document source officiel (flyer, brochure, questionnaire) et cocher une checklist complète (dates, lieu, âge, prix, horaires, réductions, téléphone, email, réseaux sociaux, tagline, QR code). Après génération, vérifier via Qwen VL que TOUS les éléments sont présents et que l'email est orthographié exactement comme sur le flyer (comparer lettre par lettre). Si une typo email est trouvée, grep ALL occurrences dans tous les scripts du projet avant de corriger. **Checklist complète + layout pattern**: voir `references/endcard-completeness-checklist.md`.
