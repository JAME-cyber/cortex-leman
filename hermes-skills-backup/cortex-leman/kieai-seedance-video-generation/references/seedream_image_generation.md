# kie.ai Seedream 5.0 Pro — Image Generation

## When to use
- Generating static images (posters, flyers, b-roll, illustrations) via kie.ai
- Any Seedream / Seedance image-to-video reference frame generation
- Culture en Saveur, african-heroes, Cortex Leman visual assets

## Model IDs
| Model | ID | Use case |
|-------|----|----------|
| Seedream 5.0 Pro | `seedream/5-pro-text-to-image` | Client deliverables (recommended) |
| Seedream 5.0 Lite | `seedream/5-lite-text-to-image` | Rapid prototyping |
| Seedream 4.5 | `seedream/4-5-text-to-image` | Legacy |
| Flux 2 Pro | `flux2/pro-text-to-image` | Alternative style |

## API Workflow (same 3-step pattern as video)

### Step 1: Submit
```python
POST https://api.kie.ai/api/v1/jobs/createTask
payload = {
    "model": "seedream/5-pro-text-to-image",
    "input": {
        "prompt": "...",
        "aspect_ratio": "3:4",
        "quality": "high",
        "output_format": "png",
        "nsfw_checker": False,
    },
}
```

### Step 2: Poll
```
GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=xxx
```
Same states as video: `waiting` → `queuing` → `generating` → `success` | `fail`

On success, `data.resultJson` (JSON string) contains `{"resultUrls": ["https://tempfile.aiquickdraw.com/..."]}`

### Step 3: Download
**IMAGES can be downloaded directly** from `tempfile.aiquickdraw.com` (unlike video which needs the `/download-url` endpoint). Simple `requests.get(url)`.

## Key Parameters
| Param | Supported values | Notes |
|-------|-----------------|-------|
| aspect_ratio | `1:1`, `4:3`, `3:4`, `16:9`, `9:16`, `21:9` | **NOT `4:5`** — API rejects it. Use `3:4` for vertical posters. |
| quality | `high` (default) | **REQUIRED field** — omitting it returns `code: 500, msg: "This field is required"`. Always include explicitly in raw API calls. |
| output_format | `png` | |
| negative_prompt | **NOT supported** on `gen_image()` wrapper or raw API | Fold negatives into the main prompt text instead |

## Cost (as of Jul 2026)
| Image type | Credits | ~USD | Gen time |
|-----------|---------|------|----------|
| 3:4 portrait, high quality | ~28 | ~$0.28 | ~150s |
| 16:9 landscape, complex prompt | ~28 | ~$0.28 | **300s+** |

## KieClient Wrapper (`african-heroes/scripts/kie_client.py`)

### ⚠️ camelCase vs snake_case trap
- **Raw API** returns `data.taskId` (camelCase)
- **KieClient wrapper** normalizes to `task_id` internally — use `kc.gen_image()` and it handles parsing
- If writing raw API calls (bypassing wrapper): use `data["taskId"]`, NOT `data["task_id"]`

### ⚠️ Hardcoded 300s poll timeout
`_poll_task()` has `timeout: int = 300`. Complex 16:9 prompts with long descriptions can exceed this.
**Fix**: bypass the wrapper for complex images — write a standalone script with `timeout=600`.

### gen_image() signature
```python
kc.gen_image(
    prompt="...",
    out_path="output.png",
    model="seedream_5_pro",      # key from MODELS dict
    aspect_ratio="3:4",          # NOT "4:5"
    quality="high",
    output_format="png",
    skip_if_exists=True,
)
# Returns: True on success/skip
```

## Generation Time by Complexity (observed Jul 2026)
| Prompt type | Aspect | Time | Notes |
|------------|--------|------|-------|
| Single subject, 3:4 | Portrait | ~30s | Pyramids + food elements |
| Multi-subject parallel, 3:4 | Portrait | ~60-120s | 2 concurrent images |
| Triptyque + all activities, 16:9 | Landscape | **308s** | success state reached at 308s |
| Retry 16:9 after timeout | Landscape | **328s** | confirmed: needs 600s timeout |

## Parallel Generation
`ThreadPoolExecutor(max_workers=2)` works for concurrent image generation. Each image gets its own taskId. Monitor with `as_completed()`.

## Reusable Prompt Templates

### Cel-Shaded Anime Reference Frame (Pattern #51, VALIDATED Jul 31 2026)

**Use when:** generating stylized reference frames for the Seedream→Hailuo I2V pipeline (59cr vs 205cr Seedance direct). Best for african-heroes combat/action/historical scenes.

**Key principle:** Explicit negative style exclusion forces the model out of its flat-illustration default. "NOT cartoon NOT Disney NOT Pixar" is mandatory — without it, 3D prompts produce flat Canva-like results (validated pitfall #9 in SKILL.md).

**Template (swap `{VARIABLES}`):**
```
Cel-shaded 3D anime, semi-realistic CGI, hand-painted textures. NOT cartoon,
NOT Disney, NOT Pixar, NOT flat illustration. Heavy dramatic shadows, visible
film grain, painterly brush strokes visible on surfaces.

{SUBJECT} — full physical description: age, skin tone, ethnic facial features,
clothing/armor with material details. {ACTION_OR_POSE}.

{ENVIRONMENT} — setting with lighting, atmospheric details, background elements.

Style: cel-shaded 3D anime, hand-painted textures, heavy inked shadow lines,
visible brushwork on {SURFACES}, film grain overlay, semi-realistic proportions.
Dramatic chiaroscuro lighting. {GENRE} anime aesthetic.
PROHIBITED: no flat plastic rendering, no cartoon simplicity, no Disney style,
no text, no watermark, no logo, no border.
```

**Validated example:** Mansa Musa procession (golden-hour desert, caravan, royal regalia, 9:16 high). Tested Seedream 5.0 Pro → Hailuo 2.3 Pro I2V → approved by user Jul 31 2026. Cost: 59cr total. Script: `scripts/seedream_hailuo_pipeline.py`.

### Papercraft Travel Poster (Pattern #24, @Naiknelofar788)
Adapted for Culture en Saveur with palette constraint. See:
`/home/tars/culture-en-saveur/scripts/gen_papercraft_cameroon_somalia.py`

Template variable: `{DESTINATION}` — swap country/landmarks/food, keep the rest fixed for series coherence.

**Palette adaptation guardrail**: Original tweet uses "soft pastel skies". For Culture en Saveur, replace with: terracotta orange, warm ochre, golden amber, deep cacao brown, soft ivory cream. The brand identity is warm earthy tones, NOT pastels.

### Working prompt — single country poster (testé Égypte, Cameroun, Somalie)

Template qui a produit 3 posters cohérents. Variables entre `{}`.

```
Create an elegant handcrafted 3D paper quilling and layered papercraft travel poster for {COUNTRY} in the style of a premium vintage travel scrapbook.

Artistically recreate {COUNTRY}'s most iconic landmarks and symbols: {LANDMARKS}.

Use intricate paper quilling, precision paper cutouts, layered cardstock, embossed paper textures, rolled paper coils, and delicate handcrafted details. Arrange the landmarks into a cohesive, storybook-like composition with a sense of depth and perspective.

Include charming local elements: {LOCAL_ELEMENTS}.

Use warm golden-hour lighting, with a palette of terracotta orange, warm ochre, golden amber, deep cacao brown, and soft ivory cream — NO pastel blue or cold tones.

Add the destination name "{TITLE}" in large bold vintage travel-poster typography at the top, in warm gold lettering on dark cacao background.

Highly detailed, premium craftsmanship, whimsical, colorful, nostalgic, editorial-quality travel art, ultra-high resolution, vertical poster composition.
```

Variables testées:
| Pays | TITLE | LANDMARKS | LOCAL_ELEMENTS |
|------|-------|-----------|----------------|
| Égypte | ÉGYPTE | Great Pyramids of Giza, the Sphinx, the Nile river with felucca boats, hieroglyphs, date palms | koshari pot, lotus flowers, woven baskets, golden sand dunes |
| Cameroun | CAMEROUN | Mount Cameroon volcano, Bamoun architecture with carvings, Ndop indigo cloth patterns, wooden masks, tam-tam drums | ndolé (bitterleaf stew), plantains, cocoa pods, red hibiscus |
| Somalie | SOMALIE | Laas Geel cave paintings, Mogadishu coral stone architecture, dhow boats, frankincense trees | canjeero flatbread, frankincense resin, Somali camels, woven nomadic mats |

Script de génération parallèle: `/home/tars/culture-en-saveur/scripts/gen_papercraft_cameroon_somalia.py`

### ⚠️ GUARDRAIL: Cross-check ALL brief activities before prompting

**Leçon (session jul 2026)**: Le premier poster programme ne couvrait que les 3 pays (triptyque géographique). L'utilisateur a corrigé: il manquait le henné, les sorties au bord du Léman/Rhône, la visio orphelinat, les contes, le thé, la musique (djembe), l'anthropologue.

**Process obligatoire**:
1. Lire le brief complet (`research/client_brief.md`)
2. Lister TOUTES les activités/éléments mentionnés
3. Vérifier que le prompt les incluit TOUS avant de soumettre
4. Un prompt 16:9 coûte 28 crédits et 300s+ — ne pas gâcher sur un prompt incomplet

### Working prompt — programme complet avec TOUTES les activités (testé + approuvé, 16:9)

Pour un visuel groupant plusieurs pays + toutes les activités du programme + titre événement + dates/lieu:

```
Create an elegant handcrafted 3D paper quilling and layered papercraft poster representing a summer cultural camp for children called "ÉVEIL AUX SAVEURS AFRICAINES", in the style of a premium vintage travel scrapbook.

The poster is divided into three cohesive sections flowing left to right, connected by a stylized paper-cut map of Africa at the center:
LEFT SECTION — ÉGYPTE: Great Pyramids, Sphinx, Nile felucca, koshari pot, date palms
CENTER SECTION — CAMEROUN: Mount Cameroon volcano, Bamoun carvings, Ndop indigo patterns, ndolé stew, wooden masks
RIGHT SECTION — SOMALIE: Laas Geel cave paintings, Mogadishu coral architecture, dhow boats, canjeero bread, frankincense trees

AROUND THE THREE SECTIONS, include these camp activity vignettes:
- An ornate hand with intricate HENNA floral and geometric patterns in terracotta
- A TEA SET with ornate glasses and a steaming pot, with open books for STORYTELLING
- A TABLET showing children waving — VIDEO CALL to an orphanage
- An ANTHROPOLOGIST'S DESK with artifacts, magnifying glass, and sketchbook
- MUSICAL INSTRUMENTS: djembe drum and kalimba with floating musical notes
- A RIVER SCENE with children playing at the WATER'S EDGE (Lake Geneva/Rhône)

At the top, the title "ÉVEIL AUX SAVEURS AFRICAINES" in large bold vintage travel-poster typography in warm gold lettering on dark cacao background. Below the title, small handcrafted paper-cut text reading "10-14 AOÛT 2026 · MQP PETIT-LANCY, GENÈVE".

Use warm golden-hour lighting, with a palette of terracotta orange, warm ochre, golden amber, deep cacao brown, and soft ivory cream — NO pastel blue or cold tones.

Highly detailed, premium craftsmanship, whimsical, colorful, nostalgic, editorial-quality travel art, ultra-high resolution, horizontal landscape poster composition.
```

⚠️ Format 16:9 = timeout>300s. Utiliser script raw API standalone avec `timeout=600` (voir `gen_papercraft_programme_v2.py`).
⚠️ Le state API est `success` (minuscule), pas `SUCCESS`/`SUCCEEDED`. Le parser doit checker exactement `== "success"`.

### Explosive Fragmentation Poster (VALIDATED Aug 3, 2026)

**Use when:** "sublimer" a person into a dynamic, exploding poster — athlete branding, hero intro card, dramatic key visual. Two validated variants: photorealistic mixed-media collage and cel-shaded anime.

**Technique:** Subject's realistic portrait at center → edges dissolve into fragmented domain-specific elements radiating outward. Visual hierarchy: most intact at top (head/shoulders crystal clear), progressively abstract toward bottom. Background = dark gradient with warm spotlight glow behind torso. Abundant negative space in lower third for text overlay.

**Art direction:** double-exposure photography + cut paper collage + watercolor bleeding + grunge texture overlay. Mediums explicitly listed in prompt. Palette specified with hex values.

**Two validated variants:**

| Variant | Style tokens | Key difference |
|---------|-------------|----------------|
| Photorealistic | "Mixed-media editorial collage", "double-exposure photography meets paper-cut collage", Behance/ArtStation quality | Fragmented elements are photorealistic shards |
| Cel-shaded anime | "Cel-shaded 3D anime, NOT cartoon NOT Disney NOT Pixar", shounen manga explosion panel, hand-painted textures, ink lineart, speed lines | Fragmented elements use manga speed lines + ink-wash gradients |

**Template (swap `{VARIABLES}`):**
```
{STYLE_TOKENS} — vertical 9:16 composition.

{SUBJECT_DESCRIPTION} — full physical description from vision_describe_image.py output:
ethnicity, skin tone, age, hair, eyes, facial features, body type, clothing.
His/her expression is {EMOTION}.

His/her realistic portrait occupies the CENTER, sharp and hyper-detailed.
From the edges, the body EXPLODES and DISSOLVES into a dynamic cascade of
fragmented elements radiating outward and downward:

{DOMAIN_FRAGMENTS} — 3-4 categories of domain-specific breakage elements.
Each with material texture, color, motion direction.

Energy effects — {SPEED_EFFECTS} bursting from behind the figure,
impact sparks in {COLOR_1} and {COLOR_2}, motion blur trails.

The fragmentation follows clear VISUAL HIERARCHY: most realistic and intact
at the top (head crystal clear), progressively more abstract and dissolved
toward the bottom (legs become pure {ABSTRACT_ENDING} merging into background).

BACKGROUND: deep charcoal black gradient (#1A1A1A) at edges transitioning to
warm amber glow ({AMBER_HEX}) behind torso — stadium spotlight rim lighting.
Abundant negative space in lower third for text placement.

ART DIRECTION: {MEDIUM_LIST}. Palette: {HEX_COLORS}.

Quality: Behance featured, ArtStation quality, museum-quality, 8K.

NO text, no watermark, no logo, no border, no typography.
```

**Validated example (basketball athlete):** Young Black teen, polo+shorts → exploding into basketball leather shards + parquet planks + net strands + speed lines. Photorealistic variant rated 8/10 by vision QA. Anime variant adds shounen manga explosion panel composition with radial speed lines and ink-wash bleeding. Cost: ~28cr each, ~160s generation time. Script: `/tmp/gen_basketball_poster.py` (photorealistic), `/tmp/gen_basketball_poster_anime.py` (anime).

**Key lesson:** Run `scripts/vision_describe_image.py` on the subject's photo FIRST to get exhaustive physical description, then paste that description into the template's `{SUBJECT_DESCRIPTION}` slot. Do NOT describe the person from memory — the vision model catches details (skin undertone, hair curl pattern, clothing brand cues) that humans miss.
