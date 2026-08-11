# Sankofa Brand Pack — Reference Application

First real application of the content-channel-branding methodology.
Project: `~/african-heroes/` — chaîne histoire africaine sourcée (FR).
Date: July 2026.

## Naming Decision

**Selected:** Sankofa (Adinkra symbol, Akan/Ghana)
**Meaning:** "San kɔ fa" = "Reviens et récupère-le" — return to the past to retrieve what was forgotten.
**Why it won over candidates:**

| Candidate | Origin | Rejected because |
|-----------|--------|------------------|
| Anansi | Ashanti trickster spider | "Spider" may repel part of audience |
| Maât | Egyptian goddess of truth | Too Egypt-specific, narrows scope |
| Griot | West African storyteller | Cliché, overused by other creators |
| Baobab | Tree of palaver | Good but generic, less symbolic depth |

**Logo concept:** Sankofa bird — body pointing forward, head turned backward, egg in beak. The egg = the future, retrieved from the past. Geometric/stylized version (not the flat traditional Adinkra illustration).

## Palette

| Role | Name | Hex |
|------|------|-----|
| Primary | Or Sankofa | `#E8A33D` |
| Secondary | Terre cuite | `#B5522E` |
| Deep | Anthracite | `#1A1A1A` |
| Light | Sable | `#F4E8D0` |

## Typography

- Titles/thumbnails: Playfair Display (serif editorial)
- Body/slides: Inter (sans-serif)
- Accent: Playfair Display Italic

## Taglines

- Principal: "L'histoire qu'on n'a pas racontée."
- Court (stinger): "Retourne la chercher."

## Logo SVG Source

Located at `~/african-heroes/CHANNEL/branding/logo_sankofa.svg`.
Structure: anthracite circle (400×400, stroke #E8A33D) → geometric bird (body forward, head backward, #E8A33D) → egg (ellipse #F4E8D0, stroke #E8A33D) → tail feathers (#B5522E).

**Render pipeline:**
```bash
python3.12 -m pip install cairosvg --break-system-packages
python3.12 -c "import cairosvg; cairosvg.svg2png(url='logo_sankofa.svg', write_to='logo_sankofa.png', output_width=400, output_height=400)"
```

**QC without vision (GLM-5.2 error 1210):**
```python
from PIL import Image, ImageStat
img = Image.open('logo_sankofa.png')
stat = ImageStat.Stat(img)
print(f'Brightness: {stat.mean[0]/255:.2f}')  # 0.16 expected (dark bg intentional)
print(f'Contrast: {stat.stddev[0]:.1f}')       # >40 = good
```

## Logo Illustré (Seedream 5.0 Pro)

Located at `~/african-heroes/CHANNEL/branding/logo_sankofa_seedream.png` (2048×2048).

Generated via kie.ai Seedream 5.0 Pro API. Prompt: Sankofa bird (head turned backward, egg in beak), sculptural 3D style, golden amber palette, anthracite background, volumetric lighting, no text. See `references/kieai-seedream-image-api.md` in the `faceless-explainer-video` skill for the complete API reference.

**Two logo variants in production:**
- `logo_sankofa.svg/png` (400×400) — geometric vector, for avatar/favicon/small UI
- `logo_sankofa_seedream.png` (2048×2048) — illustrated premium, for thumbnails/channel art/intros

**Telegram delivery note:** the 2048px PNG is 5.9 MB. Create a 1024px thumbnail (1.4 MB) for quick previews:
```python
from PIL import Image
img = Image.open('logo_sankofa_seedream.png')
img.thumbnail((1024, 1024), Image.LANCZOS)
img.save('logo_sankofa_tg.png', 'PNG', optimize=True)
```

## First Video Production (Nzinga Short 9:16)

`~/african-heroes/CHANNEL/video1_nzinga/` — 111s Short, 12 MB, H.264 1080×1920.

### Évolution des versions (v1 → v5)

| Version | Problème | Fix |
|---------|----------|-----|
| v1 (5.5 MB) | B-roll non utilisé (composite ffmpeg KO) | — |
| v2 (2.7 MB) | B-roll partiel (3/5), caption en bas | Ken Burns fallback |
| v3 (2.7 MB) | 9/9 b-roll mais fond blanc sur b-roll | — |
| v4 (11.5 MB) | Fix `omit_background=True` → b-roll visible | ✅ |
| v5 (11.5 MB) | Layout inversé : desc en haut, subs en bas | ✅ |
| v6 (11.8 MB) | Intro signature prépendue (logo Seedream + stinger Kalimba) | ✅ Final |

### Architecture finale (build_v2.py)

1. **TTS**: edge-tts HenriNeural, -5% pitch → 9 MP3 beats + durations.json
2. **Captions**: Playwright capture HTML → PNG transparent (`omit_background=True`)
3. **B-roll segments**: Seedream PNG plein écran + Ken Burns slow zoom (8% over duration)
4. **Overlay**: ffmpeg `[0:v][1:v]overlay=0:0` → caption PNG sur b-roll video
5. **Concat**: filter_complex concat des 9 segments
6. **Audio mux**: concat MP3 → AAC 192k
7. **Subs + BGM**: ASS subtitles (PlayResY=1920, MarginV=120, sable color) + BGM -28dB

### B-roll générés (9/9 Seedream 5.0 Pro, 9:16)

1. `01_nzinga_portrait` — portrait royal
2. `02_tapis_scene` — scène du tapis (négociation)
3. `03_carte_angola` — carte ancienne Angola
4. `04_imbangala_battle` — bataille Imbangala
5. `05_statue_luanda` — statue moderne Luanda
6. `06_nzinga_horseback` — charge à cheval
7. `07_nzinga_young_training` — entraînement jeune
8. `08_nzinga_old_treaty` — signature traité 74 ans
9. `09_nzinga_dutch_alliance` — alliance néerlandaise

### Intro Signature Animée

`~/african-heroes/CHANNEL/branding/intro_sankofa.mp4` (5s, 372 KB final)

**Stinger audio choisi:** Kalimba (synthétisé — voir `templates/gen_stingers.py`). L'utilisateur a reçu 4 variants (Kora, Kalimba, Balafon, Djembe+Kora) et choisi le Kalimba pour son timbre boisé et doux. Copié comme `stinger_sankofa.mp3`.

Pattern reproduit de L'Effet Composé : HTML SVG animé → capture frame par frame (Playwright, 30fps) → encode x264 → mux stinger audio (apad pour durée).

**⚠️ Logo Seedream (PNG illustré) — pas le SVG géométrique.** L'utilisateur a explicitement validé le logo illustré Seedream (`logo_sankofa_seedream.png`) comme logo officiel. Le SVG géométrique (`logo_sankofa.svg`) est réservé aux petits formats (avatar/favicon).

**⚠️ Le logo PNG ne peut PAS être embeddé dans un `<image>` SVG** (Playwright/Chromium ne le rend pas). Solution: `<img>` HTML en overlay absolu par-dessus le SVG. Voir `references/playwright-svg-image-gotcha.md`.

Timeline animation:
- 0-1.5s: Particules dorées + cercle se dessine (strokeDashoffset)
- 0.8-2.0s: **Logo Seedream** apparaît (scale 0.85→1.0 + fade) — `<img>` HTML overlay
- 2.0-2.6s: Pulse lumineux sur l'œuf
- 2.4-3.2s: Texte "SANKOFA" apparaît (amberMetal gradient)
- 3.0-3.8s: Shine sweep doré traverse le texte
- 3.4-4.0s: Divider s'étend
- 3.8-4.5s: Tagline "Retourne la chercher."
- 4.2-4.8s: Subtitle "Symbole Adinkra · Peuple Akan"

**Capture script:** `scripts/capture_brand_intro.py` (générique, prend HTML + output + stinger optionnel).

## Guardrail Pattern — Validated on Nzinga Script

The script `~/african-heroes/scripts/video1_nzinga.md` validated the content guardrails:

1. **Registre indicator:** "Historique" stated at the top of the script
2. **Myth/history distinction:** the carpet scene is flagged as "rapporté par un missionnaire néerlandais" (not asserted as fact)
3. **Sources ≥2 per key claim:** Heywood 2017 + Miller 1976 for treaty dates, Matamba conquest
4. **Name spelling:** Nzinga (not Jinga), Mbandi, João Correia de Sousa — checked against a whitelist
5. **Moral complexity preserved:** Nzinga's manipulative alliances and morally questionable choices are mentioned, not sanitized
6. **Sources slide:** present at end (Heywood, Miller, Wikipedia, Portuguese archives)

This guardrail pattern mirrors the LEC AMF anti-conseil pattern but adapted for historical integrity instead of financial regulation.

## YouTube Channel Launch Pack (August 2026)

Generated the full YouTube asset pack using PIL-only pipeline (no Playwright/browser needed).

| Asset | File | Dimensions | Source |
|-------|------|-----------|--------|
| Profile picture | `branding/youtube/profile_picture_800.png` | 800×800 | Logo Seedream resize |
| Banner | `branding/youtube/banner_youtube.png` | 2560×1440 | PIL gradient + Adinkra pattern |
| Thumbnail Nzinga | `branding/youtube/thumbnail_nzinga.png` | 1280×720 | broll/01_nzinga_portrait.png |
| Thumbnail Mami Wata | `branding/youtube/thumbnail_mami_wata.png` | 1280×720 | Still from broll_video (ffmpeg -ss 2) |
| Metadata | `branding/youtube/channel_metadata.md` | — | Description, keywords, tags, titles |

Banner QA: 8.5/10 (Gemini). Right-side Adinkra pattern solved initial "too empty" failure.

**Episodes produced:** 2/5 (Nzinga 1:54, Mami Wata ~2min). 3 scripts ready (Abla Pokou, Yennenga, Olapa) awaiting production.

## Editorial Guardrails Document

Located at `~/african-heroes/CHANNEL/EDITORIAL.md`. Key rules:
- Distinction Histoire / Légende / Mythe is OBLIGATORY in every script
- "La tradition orale raconte..." not "il est prouvé que..."
- No afrocentrism (don't attribute African origins without proof — e.g., false Olmec claims)
- No romanticization of colonial violence, but also no sanitizing of African political complexity
