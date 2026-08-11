---
name: content-channel-branding
description: "Brand a content channel (YouTube, podcast, social) from scratch: naming from cultural archives, visual identity system, tagline, thumbnail template, intro/stinger spec. Covers the full identity pack delivered as markdown briefs + SVG/PNG assets."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [branding, naming, visual-identity, youtube, podcast, content-channel]
    related_skills: [faceless-explainer-video, le-contre-point-podcast]
---

# Content Channel Branding

Full identity pack for a faceless YouTube channel or podcast: name, tagline, palette, typography, logo, thumbnail template, intro/stinger. Delivered as structured markdown briefs + SVG/PNG assets ready for production.

## When to Use

- User wants to create a new YouTube channel or podcast brand
- User asks for a name, logo, or visual identity for a content project
- User asks to "look in the archives" for a culturally grounded name
- Branding is the blocker before scriptwriting or video production can start

## The Naming Methodology — Draw From Cultural Archives

Do NOT invent names from scratch. The strongest content-channel names are **already grounded in a symbol, archetype, or tradition** that the target audience recognizes. The name carries its own meaning — you don't have to explain it.

### Step 1: Extract the brand's core verb

Before searching for names, state what the channel DOES in one verb phrase:
- "Recover forgotten stories" → look-back / retrieval symbols
- "Explain complex systems" → illumination / connection symbols
- "Deconstruct myths" → truth / discernment symbols

### Step 2: Search cultural archives matching the verb

Search across these source pools (use Apify RAG browser or web_extract on Wikipedia):

| Source pool | Example | Best for |
|-------------|---------|----------|
| Adinkra symbols (Akan/Ghana) | Sankofa ("go back and get it") | Heritage, memory, wisdom |
| Mythological figures | Anansi (storyteller), Maât (truth) | Narrative, justice, craft |
| Historical archetypes | Griot (oral historian) | Tradition, transmission |
| Proverbs / idioms | "Ba-ouli" (the child is dead) | Emotional, specific |
| Geocultural symbols | Baobab (tree of palaver) | Pan-regional, natural |

### Step 3: Score candidates against 6 criteria

| Criterion | Why it matters |
|-----------|----------------|
| **Meaning alignment** | Does the symbol's traditional meaning match the channel's mission? |
| **Visual derivability** | Can a designer extract a logo from it? (Sankofa bird = obvious) |
| **Pronounceability** | Can a non-native speaker say it? (3 syllables max, phonetic) |
| **Pan-audience reach** | Does the target audience (diaspora + general) recognize it? |
| **Availability** | Is the name already saturated on YouTube/podcast directories? |
| **No negative connotations** | Check the symbol isn't co-opted by something contradictory |

Present 3-4 candidates in a comparison table with a clear recommendation.

### Step 4: The "draw from the archives" user signal

When the user says "regarde dans les archives" or "trouve un nom qui parle à tout le monde," they are asking for Step 2-3 specifically. They do NOT want a invented/branded name (like "Baobab Studios"). They want a **real cultural symbol** whose meaning IS the brand. The name must pre-exist the channel — you are discovering it, not creating it.

## Visual Identity System

Once the name is validated, produce these deliverables in parallel:

### Palette (4 colors max)

| Role | Name | Usage |
|------|------|-------|
| Primary | [Symbol-derived] | Logo, accents, text highlight |
| Secondary | [Complement] | Thumbnail backgrounds, titles |
| Deep | [Dark anchor] | Main background, strong text |
| Light | [Neutral] | Slide backgrounds, text-on-dark |

**Rule:** The primary color must dominate thumbnails (brightness ≥0.95 on subject, per TARS QC standards).

### Typography

- **Titles/thumbnails:** Editorial serif (Playfair Display, Cormorant) — signals authority + craft
- **Body/slides:** High-legibility sans-serif (Inter, Poppins)
- **Accent:** Serif italic for citations/quotes

### Logo

Produce as SVG (vector, scalable) + PNG render:
- Geometric/stylized, not literal illustration — must be legible at 80×80 (avatar size)
- Monochrome version must work (favicon test)
- Include the symbol's iconic element (Sankofa's bird+egg, Anansi's web, etc.)

**Render pipeline:** Write SVG → install cairosvg (`python3.12 -m pip install cairosvg --break-system-packages`) → render PNG via `cairosvg.svg2png()`. GLM-5.2 vision is KO (error 1210), so validate visually with PIL ImageStat (brightness, contrast, extrema) and deliver the PNG to the user for human validation.

### Thumbnail template

Fixed structure for brand recognition:
- Left: portrait illustration of the subject (digital illustration, never stock photo)
- Right: 3-4 words max (serif bold, primary color on deep background)
- Watermark: logo symbol at 10% opacity, bottom-left
- Border: thin primary-color line (2px)

### Intro/Stinger (3-5 seconds)

Break down frame-by-frame:
1. Element appears (fire, circle, thread — derived from symbol)
2. Element condenses into the logo shape
3. Logo + channel name in primary color (serif)
4. Fade to content

**Animation capture:** HTML/CSS/JS animated intro → Playwright frame-by-frame capture → ffmpeg encode. See `scripts/capture_brand_intro.py` for the reference implementation (pattern from L'Effet Composé).

**Audio stinger — SYNTHESIZE, don't download.** Generate brand signature audio procedurally with numpy (Karplus-Strong for strings, additive synthesis for bells, sine+noise for drums, filtered noise for textures like sizzle/wind chimes). No API calls, no sample licensing, no Pixabay scraping. See `references/audio-stinger-synthesis.md` for the full technique bank. Two template families: `templates/gen_stingers.py` (African instruments: Kora, Kalimba, Balafon, Djembe) and `templates/gen_stingers_warm.py` (warm/organic textures: Marimba, Sizzle, Dinner bell, Wind chimes — for family/food/community brands). Output MP3 + OGG (for Telegram voice bubbles).

**Ambient music bed — numpy OR Suno via Kie.ai.** Stingers are 2-3s brand signatures. For a full-length background music bed (30-90s), two options depending on budget and quality bar:
- **numpy synthesis (free, immediate):** Loop a kalimba/marimba arpeggio + pad for the video duration. Lower fidelity but zero cost. Good for short promos where VO dominates.
- **Suno V4.5+ via Kie.ai (12 credits ≈ $0.06, ~30-90s generation):** Cloud-based, full-fidelity instrumental. Use `instrumental: true` (NOT `make_instrumental` — triggers 422) + `custom_mode: true` with a style prompt (genre + mood + instruments + "no vocals, instrumental only"). Returns 2 variations (MP3s, 2-4 min each). See `templates/gen_music_suno.py` for the complete API client (create task → poll → download MP3s). **Check credit balance first** via GET `https://api.kie.ai/api/v1/chat/credit` — if < 12, tell the user to recharge before proceeding. **Correct endpoints** (validated Jul 2026): create = `POST /api/v1/jobs/createTask` with `model: "ai-music-api/generate"` (NOT `POST /api/v1/jobs` which 404s), poll = `GET /api/v1/jobs/recordInfo?taskId=<id>`, response = `data.resultJson` is a **JSON string** that must be parsed → `{data: [{audio_url, duration, ...}]}`.

**Suno prompting — ask for an artist reference UPFRONT (validated Jul 2026, Culture en Saveur).** Users struggle to describe the music they want in abstract genre terms. The efficient flow:
1. **Ask immediately**: "Tu as une référence artiste ou un titre YouTube?" before generating anything.
2. **If YouTube link**: `yt-dlp --dump-json --no-download <url>` extracts title, artist, description, tags → use these to anchor the Suno `tags` field.
3. **If artist name**: translate the artist's signature sound into Suno tags (ex: "burnaboy style" → `afrobeats, afroswing, deep warm bassline, catchy highlife guitar, dancehall rhythm fusion`).
4. **If exact prompt provided**: use verbatim — don't "improve" it.
5. **No reference**: start broad (`afrobeats, instrumental, upbeat, danceable`) and iterate. Expect 3-5 generations.

**Iteration cost awareness**: each miss = 12 credits (~$0.06). 5 iterations = 60 credits. Budget for it. Don't apologize for each generation — just deliver and ask "celle-ci ou l'autre?" The user expects iteration on creative direction.

**Tag field structure** (comma-separated, max ~200 chars): `genre, reference artist style, key instruments, mood, tempo (BPM), production quality, "instrumental" flag is in the API input not tags`. Example validated: `afrobeats, afroswing, burnaboy style, instrumental, deep warm bassline, catchy highlife guitar melody, dancehall rhythm fusion, smooth mid-tempo groove, shaker and conga percussion, melodic saxophone accents, feel-good summer vibe, danceable, 104 BPM`.

**Delivery:** Generate ALL stinger variants, then send them to the user **one per turn** (one `MEDIA:` tag per assistant response, wait for the next turn before sending the next). Multiple `MEDIA:` tags in a single response may not all deliver on Telegram — only the first arrives reliably. After sending, explicitly ask "Tu en as bien reçu les N ?" to catch delivery failures early. User picks their favorite from the batch.

## Deliverables Structure

```
<project>/CHANNEL/branding/
├── IDENTITE.md          # Full brief: name, tagline, palette, typo, thumbnail spec, intro spec, VO direction
├── logo.svg             # Vector logo
└── logo.png             # Rendered preview (400×400 or higher)
```

## TARS Preferences (Embedded)

These are user-specific quality standards validated in session:

1. **No opaque overlays on broll** — background must stay visible. Reject "too dark" overlays. Layout reference: CNBC.
2. **Thumbnail brightness ≥0.95** on subject. Reject <0.8.
3. **Always test 1 section before full build** — validate the visual direction on one segment before producing the whole video.
4. **Dual output:** clips (short-term, immediate trigger) + long-form podcast material (long-term capitalization). Brand must work in both formats.
5. **Guardrails pattern:** LLM generates content + deterministic rule engine downstream can override. The LLM is never the final authority on regulated or factual content.

## B-Roll Immersif Layout (Variant D — b-roll plein écran + caption overlay)

> **USER PREFERENCE (Thierry, July 2026 — african-heroes/Sankofa):** "Il nous faut des illustrations du personnage en de toutes ses actions en arrière pour plus d'immersion." Le format slides opaques est REJETÉ pour le contenu narratif/historique. Chaque beat doit avoir son illustration d'action dédiée en plein écran.

### Architecture

```
Chaque beat = 1 b-roll plein écran (Ken Burns slow zoom)
            + 1 caption PNG transparent (overlay en bas ou en haut)
```

Le b-roll remplace la slide opaque. La caption (texte descriptif + kicker) est un PNG transparent overlay posé dessus via ffmpeg.

### Layout inversé (description en haut, sous-titres en bas)

> **USER CORRECTION (Thierry, July 2026):** "Penses-tu qu'il serait préférable de mettre les sous-titres en bas et la description en haut?" — OUI. Description + kicker en haut (gradient sombre descendant), sous-titres ASS en bas (bottom-center, MarginV=120). Évite le chevauchement.

### ⚠️ CRITIQUE — Playwright `omit_background=True` obligatoire

Le piège qui a coûté 3 itérations : si les captions PNG sont capturées sans `omit_background=True`, Playwright rend un fond BLANC OPAQUE qui masque TOTALEMENT les b-roll en arrière-plan. Résultat : l'utilisateur voit un écran blanc au lieu des illustrations.

```python
# ✅ CORRECT — transparent pour overlay
page.screenshot(path=str(out_png), omit_background=True)

# ❌ FAUTIF — fond blanc opaque (défaut Playwright)
page.screenshot(path=str(out_png))
```

Le HTML doit aussi avoir `html { background: transparent }` et `body { background: transparent }` explicitement.

### Vérification du fix

```python
from PIL import Image
img = Image.open("caption.png")
print(f"Mode: {img.mode}")  # Doit être RGBA (pas RGB)
# Extract une frame de la vidéo finale et vérifie brightness
# B-roll = sombre (~47). Caption opaque = très clair (~211). Si ~211 → bug.
```

### ASS subtitle styling pour layout inversé

```
Style: Default,Arial,42,&H00F4E8D0,&H000000FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,4,1,2,80,80,120,1
```

| Param | Valeur | Raison |
|-------|--------|--------|
| Alignment | 2 | Bottom-center |
| MarginV | 120 | 120px du bas — sous la zone b-roll |
| PrimaryColour | `&H00F4E8D0` | Sable — contraste sur b-roll sombre |
| Outline | 4 | Lisibilité maximale |

## Branding Placement Strategy — Short-Form vs Long-Form

> **USER VALIDATED (Thierry, July 2026 — Sankofa Nzinga v7):** L'intro complète (5s) NE se place PAS au début des shorts 9:16. Elle tue le hook. Stratégie validée :

| Format | Début | Pendant | Fin |
|--------|-------|---------|-----|
| **Short 9:16** (~2 min) | Hook narratif direct (0s) — pas d'intro | Watermark logo discret (80px, 40% opacity, coin inférieur droit) | **Outro signature court** (2.5s) — logo animé + tagline + stinger |
| **Long-form** (podcast, 10-30 min) | Intro complète (5s) | Watermark | Outro signature |

**Règle d'or shorts :** Les 3 premières secondes = TOUT. Une intro logo de 5s = ~40% du public qui swipe avant le contenu.

### Watermark overlay (pendant la vidéo)

Logo petit (80×80px), semi-transparent (40% opacity), coin inférieur droit. Créé via PIL :

```python
from PIL import Image
logo = Image.open(logo_path).convert("RGBA").resize((80, 80), Image.LANCZOS)
alpha = logo.split()[3].point(lambda a: int(a * 0.4))
logo.putalpha(alpha)
canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
canvas.paste(logo, (1080 - 100, 1920 - 100), logo)
canvas.save("watermark.png")
```

Appliqué via ffmpeg overlay pendant l'encodage final. **⚠️ Nécessite `-filter_complex`, pas `-vf`** (voir pitfall #12).

### Outro signature court (2.5s)

Même pipeline Playwright frame-by-frame que l'intro, mais plus court. Contenu : cercle qui se dessine (stroke-dasharray animé) → logo fade-in → titre chaîne (serif, couleur primaire) → divider → tagline → sous-titre chaîne. Stinger audio mixé via ffmpeg (même stinger que l'intro, trimmed à 2.5s).

### Build pipeline avec branding (short-form)

L'ordre d'intégration pour les shorts 9:16 :

```
[1/5] Captions (Playwright, omit_background=True)
[2/5] Build segments (b-roll + caption overlay)
[3/5] Concat segments → silent video
[4/5] Audio mux (TTS concat → AAC)
[5/5] Subs + BGM + Watermark (tout en une passe via filter_complex)
[6/5] ★ POSTPEND OUTRO (concat v+a)
```

L'intro complète (5s) n'est PAS utilisée pour les shorts — réservée au long-form.

## YouTube Channel Assets (PIL-Only Pipeline)

When Playwright/browser is unavailable, generate the full YouTube asset pack — banner (2560×1440), thumbnails (1280×720), and profile pic (800×800) — using pure PIL (Pillow). The banner uses a warm gradient + Adinkra geometric pattern overlay (avoids "right side too empty" QA failure). Thumbnails use a full-bleed character image with dark gradient overlay for text readability. See `references/youtube-channel-assets-pil.md` for the complete generation code and YouTube spec reference (safe zone math, QA workflow, video frame extraction for thumbnails).

YouTube metadata (description, keywords, tags, SEO titles, launch strategy) template: `templates/youtube_metadata_template.md`. Fill and copy directly to YouTube Studio.

### Banner safe zone

YouTube banner total is 2560×1440 but only **1546×423 centered** (507px from left, 508px from top) is visible on all devices. All text must fit inside this zone. Content outside is desktop/TV only.

### Thumbnail QA

After generating thumbnails, ALWAYS run vision QA via OpenRouter Gemini fallback before delivery. Check: text readability at small size, no overlap with character image, primary color dominance, composition balance. Target ≥8/10.

## Pitfalls

1. **Inventing a name instead of finding one** — if the user says "archives," they want a real cultural symbol, not a brainstormed brand name
2. **Too many candidates** — present 3-4 max with a clear recommendation, not 10 options
3. **Literal logo illustration** — geometric/stylized reads better at small sizes than detailed art
4. **Vision-based QA on GLM-5.2** — error 1210 (vision KO). Use PIL ImageStat metrics + deliver PNG to user for human validation instead
5. **Forgetting dual-interpreter check** — cairosvg installs on 3.12 only; if `python3 -c "import cairosvg"` fails, use `python3.12`
6. **Skipping guardrails in scriptwriting** — every script must pass the rule-engine checklist (sources, name spelling, myth/history distinction) before production
7. **Playwright omit_background oublié** — sans `omit_background=True`, les captions PNG ont un fond blanc opaque qui masque les b-roll. Toujours vérifier `img.mode == "RGBA"`
8. **Slides opaques sur contenu narratif** — pour l'histoire/narratif, utiliser b-roll plein écran (Variant D). Les slides opaques sont pour le contenu data/finance (Variant B/C)
9. **⚠️ SVG `<image href="data:...">` ne rend PAS dans Chromium/Playwright** — le logo PNG incorporé en data URI dans un `<image>` SVG reste invisible (0% pixels détectés). Coût: 4 itérations. **Fix:** utiliser un `<img>` HTML en position absolue par-dessus le SVG, pas un `<image>` SVG. Voir `references/playwright-svg-image-gotcha.md` pour le diagnostic complet et la solution.
10. **`element.style.opacity` vs `setAttribute('opacity')` sur SVG** — sur les éléments SVG (`<circle>`, `<image>`, `<path>`), `style.opacity` peut échouer silencieusement. Toujours utiliser `element.setAttribute('opacity', value)` pour les éléments SVG. Pour les éléments HTML (`<img>`, `<div>`), `style.opacity` fonctionne normalement.
11. **Perte du logo choisi par l'utilisateur** — quand plusieurs variantes de logo sont générées (ex: SVG géométrique + Seedream illustré), l'utilisateur en choisit UNE. Tous les assets downstream (intro, thumbnails, overlays) DOIVENT utiliser la variante choisie. Si l'utilisateur dit "ce n'est pas le logo que j'ai choisi", vérifier immédiatement quel fichier PNG/SVG est référencé et le remplacer. Ne jamais réutiliser le SVG par défaut si l'utilisateur a validé une version illustrée.
12. **ffmpeg overlay avec 2 inputs nécessite `-filter_complex`** — utiliser `-vf "overlay=..."` avec une image overlay en 2ème input échoue avec : *"Simple filtergraph was expected to have exactly 1 input and 1 output. However, it had 2 input(s)"*. **Fix :** tout passer en `-filter_complex` avec labels explicites : `"[0:v][1:v]overlay=x=W-w-20:y=H-h-20,subtitles='...'[vout]"`. Coût : 2 itérations sur Nzinga v7.
13. **ffmpeg overlay syntaxe `enable`** — ne pas écrire `overlay=enable='1'=x=W-w-20` (syntaxe invalide). Pour un overlay permanent, simplement omettre `enable` : `overlay=x=W-w-20:y=H-h-20`.
14. **Ne pas séquentialiser les patches de build** — quand on modifie un build script complexe (build_v2.py) avec plusieurs changements (retrait intro, ajout watermark, ajout outro, offset subs), faire un changement à la fois et tester. Sinon on accumule des bugs (variable permutée, offset oublié) qui coûtent 3+ itérations de build complet sur CPU lent.
15. **Voice swap en cascade** — changer la voix TTS (ex: DeniseNeural → HenriNeural) change les durées de chaque segment (+37% pour HenriNeural). Il faut recalculer EN CASCADE: durées VO → durées scènes → timestamps sous-titres → timings overlays → fichier concat → rebuild complet. Ne jamais juste re-générer les MP3 et reconcaténer sans recalculer les timings downstream. Toujours mesurer les nouvelles durées avec ffprobe avant de rebuild.
16. **ffmpeg concat avec chemins relatifs** — le fichier de concat ffmpeg (`-f concat -safe 0 -i list.txt`) exige des chemins ABSOLUS quand le working directory ne correspond pas. Avec des chemins relatifs: `Error opening input files: No such file or directory`. Fix: `file '/absolute/path/to/file.mp3'` dans le fichier de liste.
17. **Réutilisation cross-projet de la voix** — l'utilisateur peut demander "remplace par la voix de [autre projet]" (ex: Culture en Saveur → "celle de Sankofa"). D'abord chercher la voix utilisée dans l'autre projet (grep `--voice` dans ses scripts), puis appliquer le pattern du pitfall #15. Ne pas deviner — toujours confirmer la voix exacte depuis le code source de l'autre projet.
18. **Récupération d'assets clients depuis Linktree UGC CDN** — les pages FB/IG sont login-gated, mais le Linktree d'une organisation expose souvent de vraies photos et le logo officiel dans le DOM. Le CDN Linktree (`ugc.production.linktr.ee/<uuid>_<filename>`) est accessible sans auth. **Étapes :** (1) `browser_navigate` sur le Linktree, (2) `browser_get_images` pour lister les URLs d'images dans le DOM, (3) `curl` chaque URL avec `--max-time 25` (les gros fichiers timeout à 30s par défaut). **Format HEIC :** certaines photos smartphones (ex: HONOR) sont téléchargées en HEIC. PIL ne peut pas les ouvrir sans `pillow-heif`. Install: `VIRTUAL_ENV=<venv-path> uv pip install pillow-heif` puis `pillow_heif.register_heif_opener()` avant `Image.open()`. Convertir vers JPEG pour ffmpeg. **Logo :** peut être très lourd en PNG (700KB base64) — pour l'embarquer dans un HTML d'intro, resize à 400px + flatten sur background + JPEG q90 (76KB vs 349KB PNG).
19. **Suno music generation via Kie.ai — endpoints et format de réponse** — la création de tâche Suno utilise `POST /api/v1/jobs/createTask` avec `model: "ai-music-api/generate"` (slug marketplace, pas `V4_5PLUS`), et le polling se fait via `GET /api/v1/jobs/recordInfo?taskId=<id>`. Le champ instrumental est `instrumental` (bool), PAS `make_instrumental` (422 error). La réponse est asynchrone (30-90s). Le `resultJson` est une **chaîne JSON** (pas un dict) qui doit être `json.loads()` → `{code:200, data:[{audio_url, duration, stream_audio_url, ...}]}`. Les URLs MP3 sont dans le champ `audio_url` de chaque track. Le modèle `V4_5PLUS` ne fonctionne PAS comme model slug pour `createTask` — utiliser `ai-music-api/generate`. Anciens endpoints qui 404: `POST /api/v1/jobs`, `POST /api/v1/generate` (exige un callBackUrl qu'on n'a pas en local). **Diagnostic path** (4 erreurs en cascade): 404 sur `/api/v1/jobs` → 422 sur `/api/v1/generate` (missing callBackUrl) → 422 `instrumental cannot be null` → succès sur `createTask` avec le bon model slug. Toujours dumper `list(data.keys())` et `resultJson[:500]` si les URLs audio ne sont pas trouvées — la structure de réponse peut varier entre modèles Suno.

## Reference: Audio Stinger Synthesis

Procedural audio generation for brand signatures — no external samples or APIs. Two families: (1) African instruments (Karplus-Strong kora/kalimba, additive bell balafon, sine+noise djembe) and (2) warm/organic textures (marimba, sizzle, dinner bell, wind chimes, soft clap) for family/food/community brands. Scale choice matters: pentatonic minor = mystical/epic, major = joyful/inviting. See `references/audio-stinger-synthesis.md` for the full technique bank, `templates/gen_stingers.py` for the instrument family, and `templates/gen_stingers_warm.py` for the texture family.

## Reference: Intro/Outro → Video Integration

How to integrate brand intros, outros, and watermarks with content videos: placement strategy (short vs long-form), watermark overlay via filter_complex, intro prepend (long-form only), outro postpend (all formats), and subtitle/BGM sync management. See `references/intro-video-integration.md`.

## Reference: Playwright SVG Image Gotcha

When building animated intros with Playwright, SVG `<image href="data:...">` tags fail silently in headless Chromium. See `references/playwright-svg-image-gotcha.md` for the diagnosis methodology, the HTML `<img>` overlay fix, and base64 embedding optimization (JPEG flatten → 10× smaller).

## Reference: Client Asset Extraction

How to extract real client photos and logos when FB/IG are login-gated: Linktree UGC CDN scraping, HEIC format conversion via pillow-heif, logo base64 optimization for HTML intros, and OCR.space fallback for vision-free QA. See `references/client-asset-extraction.md`.

20. **ffmpeg `amix=duration=first` coupe l'audio au plus court input** (USER CORRECTION juil. 2026, Culture en Saveur): quand on mixe plusieurs sources audio (stinger 2s + VO 30s + musique 60s), `amix=inputs=3:duration=first` coupe TOUT au duration du premier input déclaré (le stinger = 2s). Résultat: la vidéo fait 30s mais le son s'arrête à 5s. L'utilisateur entend le stinger puis plus rien. **Fix**: **toujours** utiliser `amix=inputs=N:duration=longest` (ou `duration=total`). Vérifier avec `ffprobe -select_streams a -show_entries stream=duration` que l'audio couvre toute la vidéo. Coût: 1 re-build.

21. **edge-tts API changes — `--write-audio` → `--write-media`** (juil. 2026): le flag CLI `--write-audio` a été renommé `--write-media` dans les versions récentes d'edge-tts. L'ancien flag échoue silencieusement (produit un fichier MP3 de 0 bytes sans erreur explicite). Diagnostic: `ls -la file.mp3` montre 0 bytes → le flag est mauvais. **Fix**: utiliser `--write-media` au lieu de `--write-audio`. Vérifier la taille du fichier après génération.

22. **Voix TTS supprimées sans préavis** (juil. 2026): `fr-CH-HenriNeural` a été retirée du catalogue edge-tts sans migration. `edge-tts --list-voices | grep fr-` pour voir les voix disponibles avant de générer. Voix CH valides (juil. 2026): `fr-CH-ArianeNeural` (F), `fr-CH-FabriceNeural` (M). Fallback FR: `fr-FR-DeniseNeural` (F, chaleureuse). **Toujours** vérifier `--list-voices` si une voix previously working échoue avec `NoAudioReceived`.

23. **Désynchronisation VO → clips dans l'assemblage Shorts** (USER SIGNAL juil. 2026, Culture en Saveur T1): quand on assemble des clips vidéo (5s fixes) avec une VO plus longue (6-9s/segment), les clips défilent plus vite que la narration. L'utilisateur voit le clip Somalie pendant que la VO parle encore de l'Égypte. **Fix**: étirer chaque clip vidéo à la durée exacte de sa VO correspondante via `setpts=factor*PTS` où `factor = vo_duration / clip_duration`. Construire le timeline à partir des durées VO mesurées (ffprobe), pas à partir des durées clip fixes. Voir script `build_t1_v2.py` (Culture en Saveur) pour le pattern complet.

24. **Seedance 2.0 Fast image-to-video via Kie.ai** (juil. 2026): pipeline complet pour animer des images statiques en clips vidéo. Coût: 165 crédits/clip ($0.825), 5 clips = 825 crédits ($4.13). Nécessite upload préalable des images via `POST https://kieai.redpandaai.co/api/file-stream-upload` (gratuit, 24-72h rétention) pour obtenir une URL publique utilisée comme `first_frame_url`. Voir `references/kieai-seedance-i2v.md` pour le pipeline complet (upload + generate + poll + download).

25. **OCR.space API — `curl -F` multipart fonctionne, `urllib.request` échoue** (juil. 2026, Culture en Saveur V1): l'API OCR.space rejette les requêtes JSON `urllib.request` avec HTTP 400 (Bad Request) ou 502 (Bad Gateway), même avec `base64Image` et les bons paramètres. La solution fiable est **`curl` avec multipart form-data** : `curl -s -X POST 'https://api.ocr.space/parse/image' -H 'apikey: helloworld' -F 'language=fre' -F 'OCREngine=2' -F 'scale=true' -F "file=@/path/to/image.jpg"`. La clé `helloworld` (free tier, 25k req/mois) suffit pour l'extraction de texte depuis des carousels Instagram, flyers, et screenshots. OCREngine=2 = neural, meilleur sur texte stylisé/fontes custom. Toujours utiliser curl plutôt que urllib pour cette API.

26. **Polices système Tars — substituts validés pour Playfair/Poppins** (juil. 2026): Playfair Display, Poppins, Montserrat et Inter ne sont **pas installés** sur Tars. Substituts validés présents dans le système : `Noto Serif Display` (substitut Playfair, serif éditorial), `Noto Sans` (substitut Poppins/Inter, sans-serif lisible), `DejaVu Sans` (fallback). Vérifier avec `fc-match "Noto Serif Display"` avant utilisation. Chemins : `/usr/share/fonts/truetype/noto/NotoSerifDisplay-Bold.ttf`, `/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf`, `/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf`. Dans les sous-titres ASS, utiliser `Noto Sans` comme Fontname (pas Montserrat qui n'existe pas). Pour installer les vraies polices : `apt install fonts-playfair-display fonts-poppins` ou télécharger depuis Google Fonts.

27. **Extraction de code graphique depuis un visuel client existant** (juil. 2026, Culture en Saveur V1): quand l'utilisateur a DÉJÀ un visuel (carousel Instagram, flyer, affiche), ne pas proposer un code graphique invented — **extraire** le sien d'abord. Workflow validé (3 étapes, sans vision car GLM-5.2 KO) : (1) **OCR** via `curl -F` OCR.space (pitfall #25) pour récupérer mission, tagline, slogan, services listés ; (2) **Color analysis** via PIL : `img.resize((150,150))` → `Counter(getdata()).most_common(20)` pour palette dominante, puis filtrer les pixels saturés (`max(r,g,b) - min(r,g,b) > 50`) et grouper en buckets de 30 pour identifier les couleurs de marque réelles ; (3) **Cross-check** : aligner la palette extraite avec la palette proposée. Si l'utilisateur a déjà terracotta + ocre + crème dans son visuel, le code graphique DOIT utiliser ces mêmes teintes, pas des valeurs invented. Le user ne devrait pas pouvoir distinguer le code graphique extrait de son visuel original. Voir `references/client-brand-extraction.md` pour le workflow complet.

## Reference: Seedream 5.0 Image Generation (kie.ai)

Static image generation via Seedream 5.0 Pro — same kie.ai platform as Seedance video, same credit pool. Covers API signature (`kc.gen_image()`), supported aspect ratios (4:5 NOT supported → use 3:4), negative prompt workaround (no separate param — embed in prompt text), cost (~28 credits/image), polling timeout (always background), and Pattern #24 (Papercraft travel poster template). See `references/kieai-seedream-image-generation.md`.

## Reference: Seedance Image-to-Video

Animate static images (Seedream/FLUX) into video clips via Seedance 2.0 Fast on Kie.ai. Full pipeline: file upload → generate → poll → download. 165 credits/clip. See `references/kieai-seedance-i2v.md`.

## Reference: Client Brand Extraction

Extract brand identity (palette, tagline, mission, slogan) from an existing client visual (carousel IG, flyer) when vision is unavailable. OCR + PIL color analysis workflow. See `references/client-brand-extraction.md`.

## Client-Facing Deliverables — Branded by Default

> **USER PREFERENCE (Thierry, July 2026 — Culture en Saveur):** When producing any client-facing document (questionnaire, brief, proposal, creative review), ALWAYS default to a branded DOCX with logo + palette + polished typography. Do NOT produce raw data formats (CSV, plain markdown, TXT) for client delivery — even if technically sufficient. The user explicitly corrected a CSV questionnaire into a branded Word document: "fais moi un tableau avec le logo dessus, un beau tableau."

### Decision tree

| Deliverable type | Format | Why |
|-----------------|--------|-----|
| Client questionnaire / Q&A form | **Branded DOCX** (logo, palette, table Q/R) | Client writes directly in Word/Google Docs — professional, on-brand |
| Internal data / pipeline config | CSV, JSON, YAML | Machine-readable, not for client eyes |
| Creative brief / treatment | **Branded DOCX** or polished PDF | Presentation quality expected |
| Asset list / production tracker | XLSX (branded header) | Spreadsheet is OK but brand the header |

### docx-js branded document pattern

Use the `docx` npm package (`npm install docx`). Key techniques:
- **Logo**: `ImageRun` with `type: 'png'` + `transformation: { width, height }` in EMU (1 inch = 914400 EMU, but docx-js uses points: 120 ≈ 1 inch)
- **Colored section headers**: `TableCell` with `columnSpan: 3` + `shading.fill` = brand dark color + text in brand accent color
- **Numbered cells**: small `TableCell` with terracotta fill + white bold number
- **Answer cells**: white background, `HeightRule.ATLEAST` 800 twips, optional italic hint in gray
- **Table borders**: `BorderStyle.SINGLE` with brand color
- **Footer**: brand slogan in accent color + contact info in gray

Full working template: `templates/gen_branded_questionnaire.js`.

For multi-section client briefs (context + categorized questions + pricing tables + next steps), use `templates/gen_client_brief.js` — a generalized docx-js template with brand constants block, helper functions (heading, questionItem, answerLine, cell, headerCell), and A4 layout. Adapted from Culture en Saveur "Brief Ateliers Adultes" (Aug 2026). Pair with `references/swiss-digital-marketing-pricing.md` for CHF rate tables.

### CSV UTF-8 BOM for Excel FR (internal use only)

When CSV IS appropriate (internal data, not client-facing): use `encoding='utf-8-sig'` (BOM) + `delimiter=';'` for Excel FR compatibility. Without BOM, Excel FR garbles accents. But remember — this is the fallback, not the default for client delivery.

28. **Livrables client en format brut au lieu de branded DOCX** (USER CORRECTION juil. 2026, Culture en Saveur): l'utilisateur a demandé un CSV de questions pour que Linda puisse répondre. Le CSV a été produit correctement (UTF-8 BOM, séparateur `;`). Mais l'utilisateur a immédiatement corrigé : "fais moi un tableau avec le logo dessus, un beau tableau." **Règle**: pour tout livrable destiné à un client final (Linda, un partenaire, un prospect), produire par DÉFAUT un document Word brandé (logo + palette + typo éditoriale + table structurée). Le CSV/YAML/JSON est pour l'usage interne (pipeline, config, data). Ne pas attendre que l'utilisateur corrige — anticiper. Voir `templates/gen_branded_questionnaire.js` pour le template docx-js complet.

29. **⚠️ Le piège de surproduction — valider le funnel avant d'étendre la production** (CONTRE-ANALYSE GPT-5.6 juil. 2026, Culture en Saveur): quand on dispose d'un pipeline vidéo IA performant (Seedream → Seedance → TTS → ffmpeg), la tentation est de produire toujours plus de vidéos (V2, V3, V4...) avant d'avoir validé que c'est ce qui fait convertir le client final. Sur Culture en Saveur, 5 vidéos sophistiquées ont été produites MAIS aucun funnel d'inscription, aucune FAQ parent, aucun message WhatsApp transférable, aucune réponse du client à un questionnaire de 29 questions n'existait. GPT-5.6 a diagnostiqué : "en avance sur les actifs de production, en retard sur la preuve d'adéquation client, la conversion, la sécurité/consentements, et le cadrage économique." **Règle de séquençage** : pour un projet client avec événement à date fixe, l'ordre correct est (1) valider les fondamentaux (parcours d'inscription, infos pratiques, consentements, trust signals) → (2) produire le contenu de conversion (FAQ, flyer, message transférable) → (3) THEN étendre la production vidéo si pertinent. **Signal d'alerte** : si vous avez produit 3+ livrables sans feedback client, ou si le client n'a pas encore répondu à un briefing/questionnaire, **geler la production** et dispatcher une contre-analyse projet via `hermes -z -m openai/gpt-5.6-luna --provider openrouter` (pattern documenté dans le skill `critical-objective-analysis`, section "Counter-Analysis for Mid-Project Direction Review"). Coût : ~$0.12. Les vidéos existantes ne sont pas perdues — elles servent de b-roll et contenu de notoriété. Mais elles ne doivent pas dicter la stratégie. **Les 3 questions à se poser avant de produire la vidéo suivante** : (a) Est-ce qu'un parent peut s'inscrire sans poser 5 questions ? (b) Est-ce qu'on a au moins un contenu avec le vrai visage du client (pas TTS) ? (c) Est-ce que le périmètre de la prestation est chiffré ?

30. **⚠️ Cohérence visuelle — ne pas rupturer le feed existant d'un client** (USER CORRECTION juil. 2026, Culture en Saveur): quand on découvre un nouveau pattern visuel (ex: papercraft travel poster, mixed-media collage), la tentation est de l'appliquer immédiatement au feed du client. MAIS si le client a DÉJÀ un feed FB/IG avec une esthétique établie (photos authentiques, b-roll photo-réaliste, ambiance naturelle), imposer un style illustratif/stylisé ruptur la cohérence et jure avec l'identité existante. L'utilisateur a corrigé : "faut garder le visuel qui a été fait auparavant comme sur leur page Facebook." **Règle** : (1) analyser le feed existant avant de proposer un nouveau style (PIL color analysis sur photos réelles + assets déjà produits) ; (2) les styles illustratifs (papercraft, collage, watercolor) sont réservés aux **supports hors-feed** — flyers, posters impression, cartes de fin de camp, couvertures album, invitations — LÀ OÙ l'illustratif apporte une valeur que la photo ne peut pas ; (3) le feed reste dans le registre déjà établi (photo-réaliste si c'est ce que le client poste). Ne jamais substituer un pattern stylisé au feed existant sans validation explicite.

31. **ffmpeg `apad -t <float>` interprété comme nom de fichier** (juil. 2026, Culture en Saveur) : pour padder un stinger audio court (2s) à la durée d'une vidéo signature silencieuse (3.5s), la syntaxe `ffmpeg -i video.mp4 -i stinger.mp3 -map 0:v -map 1:a -apad -t 3.5 out.mp4` échoue avec *"Unable to choose an output format for '3.5'"*. ffmpeg parse le float comme un nom de fichier de sortie. **Fix** : utiliser `-filter_complex` avec `apad=pad_dur=<dur>` : `ffmpeg -i video.mp4 -i stinger.mp3 -filter_complex "[1:a]apad=pad_dur=1.500[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest out.mp4`. Calculer `pad_dur = video_dur - audio_dur` en amont via ffprobe.

32. **ffmpeg 7.x — zoompan `min()` sans quotes + tpad dans la même filterchain** (juil. 2026, Culture en Saveur) : la combinaison `scale=...,crop=...,zoompan=z=min(zoom+0.0006,1.12):d=73:s=1080x1920:fps=24,tpad=stop_mode=clone:stop_duration=1.06` échoue au parsing (erreur autour de `,tpad`). Deux problèmes : (a) `min()` doit être quotée `z='min(zoom+0.0006,1.12)'` ; (b) `tpad` après `zoompan` dans la même chaîne peut casser. **Fix fiable** : splitter en 2 passes — passe 1 extraire la slice brute (`-ss -t -c:v libx264`), passe 2 appliquer `scale+crop+zoompan` séparément avec `z` quoté. Pour étendre un clip au-delà de la durée source, utiliser `-stream_loop N` en input plutôt que `tpad`.

33. **Téléchargement de polices Google Fonts — raw.githubusercontent.com retourne du HTML** (juil. 2026, Culture en Saveur) : les URLs `raw.githubusercontent.com/google/fonts/.../*.ttf` redirigent parfois vers une page de login GitHub au lieu du fichier binaire. Résultat : `file Montserrat-Bold.ttf` retourne "HTML document" au lieu de "TrueType font". **Fix validé** : passer par le CSS API de Google Fonts — `urllib.request` sur `https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap` (avec un User-Agent header pour obtenir `woff2` ou `ttf`), parser le CSS pour extraire l'URL `src: url(...)`, puis télécharger le fichier binaire depuis `fonts.gstatic.com`. Vérifier avec `file *.ttf` → doit dire "TrueType Font data". Le CDN `cdn.jsdelivr.net` (Fontsource) fonctionne aussi mais sert du `woff2`, pas du `ttf` — PIL accepte les deux mais ffmpeg `drawtext` nécessite du TTF/OTF.

34. **⚠️ Palette source confusion — extraire depuis la charte d'identité, PAS depuis un flyer événementiel** (USER CORRECTION juil. 2026, Culture en Saveur) : un client peut avoir PLUSIEURS documents graphiques Canva — un roll-up/charte d'identité (couleurs de marque permanentes) ET des flyers événementiels (couleurs ponctuelles qui peuvent différer). Sur Culture en Saveur, la palette officielle Terracotta (crème `#f5e8d3`, terracotta foncé `#a00000`, ocre `#b58761`, cacao `#492e21`) a été ignorée car un autre document Canva (flyer événementiel) utilisait une palette Bleu/Orange/Vert différente. Tout le pipeline a été rebuilt en palette Canva-bleu pendant 3 heures avant que l'utilisateur ne dise "on va revenir à celui par défaut." **Règle** : (1) Toujours demander **quel document est la charte officielle** avant d'extraire une palette ; (2) Prioriser par ordre d'autorité : charte graphique écrite > roll-up/banner > flyer événement > post Instagram ; (3) Si `brand_identity.md` existe déjà dans le projet (extrait d'un asset précédent), l'utiliser comme source de vérité ; (4) Un flyer ponctuel ne JAMAIS override une charte existante. Coût : ~3h de build + rebuild pour rien.

35. **⚠️ End card completeness audit — checklist obligatoire avant livraison** (juil. 2026, Culture en Saveur) : un end card/CTA frame peut sembler complet mais omettre des infos critiques pour la conversion. Sur Culture en Saveur V1, l'end card avait : dates ✅, lieu ✅, âge ✅, téléphone ✅ — mais MANQUAIT : tarifs (85/55 CHF + fratrie), adresse exacte (n° de rue), horaires, email, Instagram, lien d'inscription, angle de conversion. **Checklist end card** (à exécuter AVANT le build final) :
    - [ ] Nom de l'événement/association
    - [ ] Dates (du / au)
    - [ ] Horaires complets
    - [ ] Lieu + adresse postale complète (n° rue + code postal + ville)
    - [ ] Tranche d'âge / public cible
    - [ ] Tarifs (toutes les formules + réductions)
    - [ ] Téléphone (format international si transfrontalier)
    - [ ] Email
    - [ ] Instagram + autres réseaux sociaux
    - [ ] Lien d'inscription / Linktree
    - [ ] Tagline/slogan de marque
    - [ ] Logo
    Valider via Qwen 2.5 VL 72B (`qwen/qwen2.5-vl-72b-instruct` via OpenRouter) qui lit l'image et liste tout le texte visible — puis comparer avec la checklist. Voir `references/conversion-first-content.md` pour la checklist complète et le pattern de validation.

36. **Conversion angle mining — l'argument de vente réel est enfoui dans le questionnaire** (juil. 2026, Culture en Saveur) : sur 17 réponses au questionnaire de découverte, l'argument de conversion le plus puissant ("les ateliers ont lieu la semaine précédant la rentrée scolaire, les parents peuvent préparer cette période plus sereinement" — Q14) n'était PAS dans le brief client ni dans les USP listées. Il était dans une réponse libre à la fin du questionnaire. **Règle** : avant de scripter une vidéo de conversion, lire TOUTES les réponses du questionnaire de découverte en cherchant des angles que le client mentionne accessoirement mais qui résolvent un problème concret pour le client final (ex: garde d'enfants pendant la semaine de boulot, pas juste "découverte culturelle"). L'argument de conversion n'est pas "ce qui est noble" — c'est "ce qui résout le problème pratique du parent/client."

37. **Message WhatsApp transférable — livrable obligatoire pour tout projet événementiel** (juil. 2026, Culture en Saveur) : les vidéos ne se diffusent pas seules. Le canal réel de conversion pour un événement local (asso, camp enfants, marché) est le **groupe WhatsApp parent/communautaire** — pas Instagram. Un parent transfère un message à un autre parent. Ce message doit être : (1) **court** (< 800 caractères), (2) **auto-suffisant** (toutes les infos critiques sans besoin de cliquer), (3) **emoji-formaté** pour la lisibilité en mobile, (4) inclure un seul lien (Linktree ou inscription). **Format validé** : voir `templates/whatsapp_transferable_template.txt`. Toujours produire CE livrable en parallèle de la vidéo — la vidéo attire l'attention, le WhatsApp convertit.

## Reference: Conversion-First Content

Quand le pipeline vidéo tourne bien mais que la conversion stagne : cross-source data mining (brief + questionnaire + charte + contre-analyse GPT-5.6), end card completeness audit (checklist 12 items + validation Qwen 2.5 VL), conversion angle mining (l'argument réel est dans les réponses libres du questionnaire), sequencing rule pour projets événementiels, et livrables conversion-first prioritisés. See `references/conversion-first-content.md`.

## Reference: WhatsApp Transférable

Template de message WhatsApp parent-à-parent pour événements locaux (camps, asso, marché). Règles de format (< 800 chars, auto-suffisant, emoji-formaté, 1 seul lien) + templates camp enfants et catering + stratégie de diffusion (transfert, pas post). See `templates/whatsapp_transferable_template.txt`.

38. **⚠️ Voice-to-text client input — interpréter l'intention, pas les mots** (USER CORRECTION août 2026, Culture en Saveur): les messages du client (Linda) sont souvent dictés en voice-to-text et transcrits par l'utilisateur (Tars) dans le même mode. Sur Culture en Saveur, Linda a dicté (en anglais, ce qui est inhabituel) : *"Ilymouris"* — transcription phonétique déformée. Le sens était "Île Maurice" (probable). De même, *"Little Nancy"* = Petit-Lancy (GE). **Règle** : (1) ne jamais prendre un nom propre transcript voice-to-text au pied de la lettre — toujours noter "(à confirmer)" à côté de la transcription littérale ; (2) contextualiser géographiquement (un atelier cuisine africaine à Genève mentionnant un lieu qui ressemble à un nom local → vérifier les lieux partenaires connus) ; (3) lister les interprétations possibles dans le brief client et laisser le client valider. Coût si non détecté : un livrable avec un nom de pays erroné.

39. **Vérification DOCX sans LibreOffice — fallback pandoc + zip inspection** (août 2026, Culture en Saveur) : quand `soffice`/LibreOffice n'est pas installé et ne peut pas l'être (pas de sudo), la vérification visuelle standard (DOCX → PDF → images → vision_analyze) n'est pas disponible. **Fallback validé** : (1) `python3 -c "import zipfile, xml.dom.minidom as m; z=zipfile.ZipFile('file.docx'); d=z.read('word/document.xml').decode(); print(f'XML valid: {bool(m.parseString(d))}')"` pour valider le XML ; (2) `for f in z.namelist(): if 'media' in f and z.read(f): print(f'  image: {f} ({len(z.read(f))} bytes)')` pour vérifier que les images sont embarquées ; (3) `pandoc -t plain file.docx | head -40` et `tail -40` pour vérifier le rendu texte (tables, headings, ordre des sections). Ce fallback capte : XML corrompu, images manquantes, erreurs d'ordre des cellules, placeholders restants. Il NE capte PAS : spacing, rendu couleur, sizing d'images — pour ça il faut soffice.

## Reference: Swiss Digital Marketing Pricing

Tarif marché CHF pour video production, community management, audit RGPD-IA, et consulting. Inclut tarif association (remise 30-45%) et principes pricing (Luke Pierce pattern: cost-based, sell audit first, retainer après preuve). See `references/swiss-digital-marketing-pricing.md`.

## Reference: YouTube Channel Assets (PIL-Only)

When Playwright/browser is unavailable: generate banner, thumbnails, profile pic using pure PIL. YouTube spec reference (banner 2560×1440, safe zone 1546×423, thumbnails 1280×720), warm gradient + Adinkra pattern overlay for banner fill, video frame extraction for character thumbnails, and Gemini QA workflow. See `references/youtube-channel-assets-pil.md`. Channel metadata (description, keywords, tags, SEO titles, launch strategy): `templates/youtube_metadata_template.md`.

## Reference: Intro → Video Integration

How to prepend a brand intro (animated logo + stinger) to a content video while keeping subtitles, BGM, and audio in sync. Covers the 3-step pipeline (concat v+a, offset subs, delay BGM) and the pitfalls that break sync. See `references/intro-video-integration.md`.

## Reference: YouTube Video Upload (Headless)

Upload finished videos to YouTube from a headless server via Data API v3 (resumable upload). Covers OAuth2 token exchange without browser GUI, chunked upload, thumbnail attachment, and token refresh. youtubeuploader CLI does NOT work headless — use the Python API approach instead. See `references/youtube-api-upload.md`.
