# Promo Vidéo Client — Recipe (non-finance)

Vidéo promotionnelle pour un client (atelier, événement, service) — **sans** les contraintes AMF. Pipeline simplifié : Edge TTS segmenté → visuels Seedream parallèle → assemblage ffmpeg avec overlays texte + CTA.

Validé projet Culture en Saveur (atelier cuisine enfants), 2026-07-24.

## Structure narrative 7 scènes (~44s)

| # | Rôle | Durée type | Contenu visuel |
|---|---|---|---|
| 1 | Hook | 4-5s | Image d'accroche émotionnelle (enfants, épices) |
| 2 | Reveal | 5-6s | Révéler le périmètre (pays, thèmes) |
| 3 | Immersion | 5-7s | Action concrète (cuisine, création) |
| 4 | Moment fort | 5-6s | Élément différenciant émotionnel (ici: appel vidéo orphelinat) |
| 5 | Rassurance | 8-10s | Sécurité, encadrement, groupes par âge |
| 6 | Offre | 3-4s | Promotion (10% 2e enfant) |
| 7 | CTA | 7-9s | Tarifs, dates, contact, inscription |

**Principe** : placer l'élément le plus émotionnel/différenciant en scène 4 (pas en anecdote). C'est ce qui fait partager.

## Pipeline technique

### 1. TTS segmenté (Edge TTS)

Générer **un MP3 par scène** (pas un seul bloc) pour pouvoir caler les visuels exactement sur les timings.

```bash
edge-tts --voice fr-FR-DeniseNeural --rate="+5%" \
  --text "Texte scène 1..." --write-media assets/vo_01.mp3
# Répéter pour chaque scène
```

Mesurer les durées exactes avec `ffprobe` → calculer les timings cumulés → adapter les durées visuelles.

### 2. Visuels Seedream (génération parallèle)

ThreadPoolExecutor(max_workers=3) — voir `references/kie-ai-seedream-image-api.md` pour les détails API et coûts.

- 14 crédits/image, 100-280s latence
- Prompt en anglais, aspect_ratio "9:16", quality "high"
- Pour le background CTA (scène 7) : si Seedream timeout/crédits épuisés, fallback gradient ffmpeg (`-f lavfi -i "color=..."`) — 0 crédit, 1s

### 3. Assemblage ffmpeg (filter_complex en une passe)

Structure du filter_complex :
1. Scale + crop chaque image vers 1080×1920 + `setsar=1`
2. `concat=n=7:v=1:a=0` des flux vidéo
3. `drawtext` overlays pour les titres de scène (SANS emojis !)
4. `drawtext` overlays pour le CTA final (multiligne)
5. `ass=` burn-in des sous-titres
6. Map vidéo + audio VO concaténé

**Pièges** :
- Pas d'emojis dans drawtext (voir SKILL.md)
- Escape `:`, `'`, `,` dans les textes drawtext
- `ass=` filter (pas `subtitles=`) pour les sous-titres ASS sur Linux

### 4. Output

- Codec : libx264 preset medium CRF 20
- Audio : AAC 128k
- `+faststart` obligatoire pour streaming
- 5-10 MB typique pour ~44s 9:16 (largement sous 50MB TG)

## Différences vs pipeline finance (LEC)

| Aspect | Pipeline finance | Pipeline promo client |
|---|---|---|
| Conformité | AMF L541-1 obligatoire | Aucune |
| Intro/outro signature | OBLIGATOIRE | Optionnel |
| BGM | Stellardrone -22dB | Optionnel |
| Structure | Hook → data → CTA abonnement | Hook → immersion → CTA contact |
| Visuels | Grok Imagine (ambiance tech) | Seedream (scènes narratives) |
| Durée | 45-60s | 40-45s |
| Coût visuels | ~$0.02/acteur (6 variants) | ~98 crédits pour 7 images |

## Signature sonore (stingers + BGM)

### Option A — Stingers synthétisés (numpy, gratuit)

Pour une signature sonore courte (1-3s) sans API externe : synthèse numpy pure (sine waves + envelopes + noise). Script type : `gen_stingers.py` — 3 concepts par batch (ex: marimba arpège + shimmer bell + sizzle, ou cloche + kalimba + claps). Format MP3 44.1kHz.

Patterns par univers :
- **Cuisine/famille** : majeur joyeux (marimba/kalimba/bell) + textures culinaires (sizzle, claps)
- **Histoire/épique** (Sankofa) : pentatonique mineure mystique (kora/djembe)
- **Finance** (LEC) : géométrique, minimaliste

### Option B — BGM Suno (via Kie.ai, ~$0.06)

Pour un ambient bed sous la voix off (~60s+) : `references/kie-suno-music-api.md`. Mixer à -22dB à -28dB sous la VO selon la durée (plus long = plus discret).

### Option C — Les deux combinés (validé Culture en Saveur)

Stinger signature en intro (2s, plein volume) + BGM Suno en bed sous la VO (-25dB). Le stinger crée l'identité de marque, le BGM crée l'ambiance.

## Fichiers de référence (projet Culture en Saveur)

- `/home/tars/culture-en-saveur/script/script_v1.md` — Script 7 scènes
- `/home/tars/culture-en-saveur/scripts/build_video.py` — Générateur ffmpeg filter_complex
- `/home/tars/culture-en-saveur/scripts/gen_stingers.py` — Synthèse stingers numpy (3 variants)
- `/home/tars/culture-en-saveur/assets/subtitles.ass` — Sous-titres ASS
