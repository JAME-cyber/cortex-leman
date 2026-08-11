# Seedance 2.0 — Prompting Patterns Library (Condensed)

> Curated from X/Twitter analysis (Jul 2026). Full annotated library with sources:
> `/home/tars/culture-en-saveur/research/seedance_patterns_library.md` (56 patterns #14-#69 + 3 annexes)

## Quick Decision Table

| Need | Pattern | ID |
|------|---------|-----|
| Multi-character consistency | Triple identity lock | #14 |
| Epic/battle (single subject) | 6-shot escalation | #15 |
| Automate narrative structure | LLM storybreaker pipeline | #16 |
| Authentic amateur (TikTok/Reels) | Raw smartphone / faux UGC | #18 |
| Documentary realism (travel) | Travel vlog + wardrobe lock | #19 |
| Complex combat (spatial continuity) | Dark cinematic epic | #22 |
| Premium brand/advertising | Commercial hero shots | #23 |
| Technical deconstruction/assembly | Architectural storyboard | #25 |
| Typography + human subjects | Typographic Force (GPT Image 2) | #26 |
| Commercial fashion/product arc | 4-Act Commercial Arc (timeline + audio) | #27 |
| Complex multi-beat scenes (cinema) | JSON Storyboard Schema (Kling 3.0) | #28 ⭐ |
| Abstract/oniric/surreal subjects | Prose évocatrice (anti-structure) | #29 |
| Continuous take + camera authenticity | Imperfect Cinema (Section+Timeline) | #30 |
| Fight scene / action complex multi-cut | Two-Stage Choreography Pipeline (Storyboard→Video) | #31 ⭐⭐ |
| Showcase multi-destinations / quick montage | Scene-by-Scene Timeline | #32 |
| Pipeline complet film IA (6 outils, festivals) | End-to-End AI Film Pipeline (macro workflow) | #33 |
| Travel/fashion multi-biome + wardrobe morph | Multi-Biome Wardrobe Morph | #34 |
| Clonage vidéo + character swap | Video Clone & Character Swap (video-to-video) | #35 |
| Storyboard BD stylisé → animation | Comic Grid Pipeline (GPT Image 2 → Seedance) | #36 |
| Sound design inline via tags audio | Audio Tag Notation | #37 |
| Cuisine/process en prose narrative séquentielle | Narrative Prose Sequence (3-act natural) | #38 |
| Publicité produit premium avec reference lock | Luxury Product Commercial Timeline (7-segment) | #39 |
| Vlog/social avec dialogue parlé par segment | Vlog Dialogue Track (Seedance 2.0 Mini) | #40 |
| Série animée: pre-production system 6 stages | Anime Pre-Production Pipeline (APOB + GPT Image 2) | #41 |
| Partition musicale complète + sound design spatial | Sound Design Bible (BPM + instruments + perspective) | #42 |
| Mascotte 2D cartoon dans monde réel (compositing hybride) | Mixed Media Composite (Live-Action + 2D Sticker) | #43 |
| Transformation spatiale: camera fixe + construction logique | Architectural Renovation Morph | #44 |
| Plan-séquence continu sans cut (multi-scènes en un take) | One-Shot Continuous Camera Path | #45 |
| Boucle parfaite: première frame = dernière (Shorts/Reels) | Seamless Loop | #46 |
| Product ad with exact packaging (14-attr lock) | Product-1:1 Spec Commercial | #69 |
| Long-form compilation (30-60s via extensions) | Extension Chaining | #47 |
| Transitions calées sur beat drops musicaux | Audio-Synced Scene Transitions | #48 |
| Multi-part spatial continuity + style exclusion | SET LAYOUT Spatial Lock + GPT Image 2 | #49 |
| Court-métrage narratif 2-part (dialogue + continuité) | Two-Part Storytelling Prompt | #50 |
| Animation non-Pixar / cel-shaded premium (2s segments) | Timestepped Cel-Shaded Anime | #51 |
| Cooking fantasy chorégraphié (caméra extrême + object-transition) | Fantasy Cooking Choreography | #52 |
| Dual-character identity lock via VS card (contrast + palette split) | Versus-Card Paired Identity Lock | #53 |
| Miniature humain dans monde réel (scale comedy) | Miniature Human Composite Comedy | #54 |
| Character consistency multi-angle (12+ clips, cheapest path) | Character Sheet Multi-Cut via Hailuo/MiniMax H3 | #55 |
| Top-down assembly / construction logic | Sequential Assembly Choreography (Hailuo H3) | #56 |
| Emotional arc via lighting + small-action→large-payoff | Emotional Amplification Micro-Techniques | #57 |
| Action sequence with characters on a moving vehicle | Vehicle-Anchored Action Sequence (Seedance 2.0) | #58 |
| Multi-character spatial consistency (blocking reference) | Still Frame Blocking + Shot List Separation | #59 |
| Universal prompt structure (⭐ use as BASE for ALL prompts) | Structured Section Header Template + Self-Shot UGC | #60 |
| In-video UI overlays (logos, HUDs, maps, tickers) | In-Video HUD/UI Overlay Generation | #61 |
| ⭐ UNIVERSAL PROMPT TEMPLATE (7 labeled sections) | Structured Section Header + Self-Shot UGC | #60 |

## Style Spectrum — Aesthetic directions catalogued

```
Photoréaliste → Cel-shaded anime (#51) → LEGO/brickfilm → 2D sticker (#43) → Comic/ink (#36)
```

| Style | Pattern | Status | Notes |
|-------|---------|--------|-------|
| Photoréaliste documentary | #30, #32, #38 | ✅ Validated | Default for CES/Cortex Leman |
| Cel-shaded anime | #51 | 🔄 Direction | "NOT cartoon NOT Disney NOT Pixar" — anti-flat-render |
| LEGO / brickfilm / stop-motion toy | — | 🔄 Direction | Plastic toy look, limited articulations, visible bricks. Spotted Jul 2026 (@Jvnior, 44.4k views). No prompt extracted yet. Potential: educational/kids content, CES mascottes |
| 2D sticker cartoon (composite) | #43 | ✅ Validated | Flat 2D in photoreal world, 142% bookmark ratio |
| Comic/ink (Spider-Verse) | #36 | ✅ Validated | Style transfers from GPT Image 2 storyboard |
| Cooking fantasy chorégraphié (caméra extrême + object-transition) | Fantasy Cooking Choreography | #52 |
| Dual-character identity lock via VS card (contrast + palette split) | Versus-Card Paired Identity Lock | #53 |

## Style Spectrum — Aesthetic directions catalogued

```
JSON structured ←———→ Hybrid sections ←———→ Timeline simple ←———→ Prose pure
   #28                  #30/#31/#42           #25/#27/#34/#39      #29/#38
 (machine)          (human + machine)        (technical)          (artistic)
                                                                         ↑
                                                                   #43 (hybrid media)
```

**Rule:**
- Subject **concrete/actional** (battle, product, assembly) → structured (#25, #27, #28, #31)
- Subject **abstract/dreamlike/surreal** → prose free (#29)
- Subject **realistic/documentary** but needs authenticity → imperfect cinema (#30)
- Subject **complex action needing continuity** (fight, sport) → two-stage pipeline (#31)
- Subject **multi-location showcase** (travel, activities) → scene-by-scene (#32) or wardrobe morph (#34)
- Subject **existing video to adapt** → video clone + character swap (#35)
- Subject **needs stylized animation** → comic grid pipeline (#36)
- **Sound design needed inline** → audio tags (#37, basic) or sound design bible (#42, full score + spatial SFX)
- Subject **cooking/process/simple sequential** → narrative prose sequence (#38, ~100 mots, easiest)
- Subject **product/luxury ad** → luxury product commercial timeline (#39, @image_1 product lock + sensory/product alternation)
- Subject **vlog/social content with talking character** → vlog dialogue track (#40, dialogue per segment, Seedance Mini synced audio)
- Subject **recurring animated series** → anime pre-production pipeline (#41, 6-stage system with character sheet + story bible)
- Subject **mascot/brand character in real environment** → mixed media composite (#43, live-action + flat 2D sticker, cross-layer interaction, slapstick comedy arc)
- Subject **transformation spatiale / renovation / before-after** → architectural renovation morph (#44, absolute camera lock + sequential construction logic)
- Subject **immersive walkthrough / property tour / event discovery** → one-shot continuous camera path (#45, no cuts, spatial transitions via doorways/corners)
- Subject **TikTok/Reels viral loop** → seamless loop (#46, first frame = last frame, rotation 360° / motion cycle / spatial return)
- Subject **long-form 30-60s video** → extension chaining (#47, chain 15s segments with explicit continuity)
- Subject **music-driven pacing / beat-synced cuts** → audio-synced transitions (#48, @Audio1 track upload + beat-mapped timeline)
- Subject **court-métrage narratif avec dialogue** → two-part storytelling (#50, 2 prompts consécutifs Part1/Part2, dialogue inline `Character (emotion): "line"`)
- Subject **animation premium non-Pixar** → timestepped cel-shaded anime (#51, segments 2s, "NOT cartoon NOT Disney NOT Pixar", beat-synced audio)
- Subject **cooking/cuisine fantasy avec camera extrême** → fantasy cooking choreography (#52, object-as-transition, 4th wall break, personality directive, 1500+ mots scene-by-scene)
- Subject **2 persos en rivalité/compétition** → versus-card paired identity lock (#53, GPT Image V2 VS card comme single-asset reference, contrast-based lock + palette split empêche drift/blend)
- Subject **miniature/petit personnage dans monde réel** → miniature human composite comedy (#54, scale-as-narrative, explicit size lock "exactly 15cm", object recontextualization, freeze-frame ending, contact shadows ×2)
- Subject **construction/assembly process top-down** → sequential assembly choreography (#56, fixed top-down camera, layer-by-layer with per-material texture, hero shot final beat, Hailuo H3)
- Subject **needs emotional amplification** → inject emotional amplification micro-techniques (#57, A: time-of-day as lighting arc jour→golden hour→nuit, B: small action→large visual payoff, injectable into any existing pattern)
- Subject **action/combat with characters on a vehicle** → vehicle-anchored action sequence (#58, characters locked to positions on mobile object, camera angles as implicit storyboard without timestamps, genre mashup token)
- Subject **multi-character scene needing spatial blocking** → still frame blocking (#59, generate static frame with all characters positioned → use as I2V reference → prompt text handles ONLY camera+dialogue)
- **⭐ UNIVERSAL PROMPT TEMPLATE** → use structured section header (#60, 7 labeled sections: Main Subject→Location→Visual Style→Camera Style→Timeline→Audio→Goal, applicable to ALL prompts regardless of subject)

---

## #30 — Imperfect Cinema: Hybrid Section+Timeline (NEW Jul 2026) ⭐
**Source:** @bmx_ai13 — "The Street Moves. He Doesn't." via Seedance 2.0
**Engagement:** 76 likes, **47 bookmarks** (62% save ratio = community reference prompt)

### 4 innovations

**① Fake dolly zoom via diagonal movement:**
Camera advances diagonally while zoom reverses (45-50mm → 22-24mm), timed so subject stays same apparent height. Background stretches laterally (parallax: taxis, crosswalk stripes) while subject remains anchored. NOT a real Vertigo effect.

**② Deliberate imperfection injection (counter-pattern):**
Instead of demanding perfection, the prompt **demands defects** for authenticity:

| Imperfection | Effect |
|---|---|
| "tiny operator sway" | Gimbal operator sway |
| "natural footstep rise-and-fall" | Camera breathes with steps |
| "slight horizon breathing" | Horizon micro-vibrations |
| "mild rolling shutter" | Rolling shutter on corrections |
| "realistic autofocus micro-adjustments" | Micro focus hunting |
| "subtle lens breathing" | Lens breathing |

→ Model generates footage that looks like a real camera, not clean CGI. **Perfection kills authenticity.**

**③ Hybrid SECTION + timeline structure:**
Named sections in CAPS (`SUBJECT`, `ENVIRONMENT`, `IMAGE QUALITY`, `MUSIC`) with detailed timeline (0-3s, 3-10s, 10-13s, 13-15s) between them. **Readable by human AND machine.**

**④ Musical direction with BPM + visual sync:**
`92-100 BPM, warm kick, soft rim clicks. Subtly swell during dolly-zoom section, land on clean final hit.` — most precise audio direction seen, including dynamic arc synced to visual action.

### Template
```
Create a [durée], [ratio] photorealistic cinematic [genre] in [setting].
One continuous take, no cuts, no text, arrows, cursor, tutorial graphics or logos.
The core visual is [primary camera effect].

SUBJECT: one consistent [full physical description]. Keep face, hair, outfit,
proportions identical throughout. [Behavioral constraint: "He never poses".]

ENVIRONMENT: [detailed setting]. Avoid readable brand names. [Light conditions].

0-Xs: [initial camera position, subject entry, gimbal imperfections]
X-Xs: [primary camera movement + parallax + technical specs (24fps, shutter blur)]
X-Xs: [subject reaction (glance), preserve gait/cloth movement]
X-Xs: [foreground occlusion, organic settle, no freeze]

IMAGE QUALITY: [sensor specs + grain + contrast + exhaustive negative constraints]
MUSIC: [genre + BPM + instruments + dynamic arc synced to visual + exclusions]
```

### Applications
- **Culture en Saveur**: ⭐⭐⭐ Child walking through market/kitchen, continuous take, deliberate imperfections for authenticity
- **Cortex Leman**: ⭐⭐⭐ Documentary brand content — camera imperfection gives reportage authenticity, premium but not "AI clean"
- **african-heroes**: ⭐⭐ Following a historical character through a market/landscape (Tombouctou, Zanzibar)

---

## #29 — Prose Évocatrice / Surreal (NEW Jul 2026)
**Source:** @AllaAisling — "Hollow World" via Seedance 2.0 in Krea AI
**Tool:** Seedance 2.0 (our stack) via Krea AI interface

### Concept
**Anti-pattern** by design. Zero structure: no timeline, no beats, no JSON. A single paragraph of **continuous poetic prose** that works precisely because the subject is impossible to code in JSON.

**Full prompt:**
> "The camera races low over rolling terrain that bends upward at the edges instead of falling away, rivers climb the walls, forests hang overhead, and mountains grow downward from a ceiling of land. Two traversal craft fly the inside of a hollow world while the camera struggles to keep up with the inverted geometry. They climb toward the central sun and emerge into a sky filled with hundreds of nested hollow worlds, each one visible through the next."

### 3 techniques
1. **Impossible physics** — rivers climb walls, inverted mountains. Model forced to generate geometry outside training data.
2. **Camera as character** — "the camera struggles to keep up" → camera has intent and emotion.
3. **Scale revelation** — ending: emergence → hundreds of nested hollow worlds. Cosmic escalation in one sentence.

### Template
```
The camera [living action] over/on/through [impossible environment].
[Element A] [impossible verb], [Element B] [impossible verb],
[Element C] [impossible verb].
[Subject] traverses this space while the camera [emotional reaction].
[Cosmic escalation / scale revelation ending].
```

### Why it works
Structured patterns (#25/#27/#28) excel at **consistency**. But consistency kills surreal creativity. Free prose lets the model **interpret contradictions freely**, producing visuals no JSON could specify.

### Applications
- **african-heroes**: ⭐⭐⭐ Myths/legends — African cosmogonies, spirits, spiritual worlds, Anansi, Yoruba creation myths. Impossible physics = native mythological register.
- **Cortex Leman**: ⭐⭐ Conceptual/abstract brand content, visual metaphors for tech services
- **Culture en Saveur**: ⭐⭐ "Cooking as magical world" from inside (floating ingredients, giant utensils, kids exploring edible universe)

---

## #28 — JSON Storyboard Schema ⭐ (LLM-native)
**Source:** @im_shahid7 — "The Dragon Era" via Kling AI Video 3.0
**Workflow:** LLM generates JSON storyboard → video model executes beat-by-beat

### Why it's the most advanced structured pattern
The prompt is a **JSON object** — machine-readable, directly generable by an LLM. Unlike free-text timelines (#25, #27), this format is **LLM-native**: a Claude/Opus can produce the full schema from a simple synopsis.

### Schema structure
```json
{
  "Scene": "name",
  "Duration": "10s",
  "Aspect_Ratio": "16:9",
  "Overall_Style": "...",
  "Emotional_Arc": "chaos → fury → dominance → swarm",
  "Reference_Lock": { "SCENE_ID": "persistent scene description" },
  "Character_IDs": { "NAME": { "Visual": "...", "Voice": "none" } },
  "Location_IDs": { "LOCATION": "..." },
  "Motion_Pacing": "intense, chaotic",
  "Beats": [
    {
      "Beat": "Beat 1",
      "Time": "0s-2.5s",
      "Reference_Lock": "SCENE_ID",
      "Continue_From": null,
      "Beat_Action": {
        "Start_Frame": "...", "Main_Action": "...",
        "Background_Action": "...",
        "Micro_Timeline": { "0.0s-0.9s": "...", "0.9s-1.8s": "..." },
        "End_Frame": "..."
      },
      "Camera": {
        "Camera_Target_Lock": "...",
        "Shot_Distance_And_Lens": "wide 28mm",
        "Camera_Angle": "LOW ANGLE (-30°)",
        "Camera_Position_Around_Target": "FRONT-LEFT (+35°)",
        "Camera_Movement": "slow push-in",
        "Camera_Stability": "chaotic"
      },
      "Lighting_VFX": "...",
      "Sound": "..."
    }
  ]
}
```

### 3 innovations unique to #28
1. **Continue_From** — explicit chaining: End_Frame of beat N = Start_Frame of beat N+1
2. **Micro_Timeline** — sub-second precision INSIDE each beat
3. **JSON format** — LLM can generate the entire schema automatically

### Applications
- **african-heroes**: Battles/myths (Adoua, Chaka Zulu, Samori Touré) — Reference_Lock ensures armor/set consistency across beats
- **Cortex Leman**: Complex multi-beat brand content
- **Culture en Saveur**: Overkill but schema is adaptable for pedagogical sequences

---

## #27 — 4-Act Commercial Arc (timeline + audio direction)
**Source:** @itxabdullaa — FILA-style fashion ad via Vivago AI

### Structure (3 prompt sections)
```
① Sequence (timeline):
0-2s: Macro product details (zipper, texture, stitching, reflections)
2-5s: Action (putting on product, dolly push-in)
5-8s: Movement (runway walk, tracking, low-angle, whip-pan)
8-12s: Editorial poses (camera orbit, rim light, slow-motion)
12-15s: Hero ending (push-in, negative space for logo)

② Style: dense keywords (ARRI Alexa, Cooke Anamorphic, Vogue, cuts 0.5-1s, grading)
③ Audio: genre + sync with cuts + explicit exclusions
   "Modern upbeat electronic, deep cinematic bass, synchronized with cuts.
    No voiceover. No dialogue. No ambient sounds. No subtitles."
```

### Key difference vs #25
| #25 Architectural | #27 Commercial |
|---|---|
| Motion strict (1 axis, 60% dim) | Fast energetic cuts (0.5-1s) |
| Seamless loop | Hero ending (no loop) |
| No audio | Audio directed in prompt |

### Applications
- **Cortex Leman**: Brand content premium, product demos
- **Culture en Saveur**: "macro→action→hero" transposable (macro ingredients → cooking → final plate)

---

## #26 — Typographic Force (GPT Image 2)
**Source:** @MrLarus — "AI Visual Systems Vol.17.3: Force & Form"
**Tool:** ChatGPT-Image2 (GPT Image 2) — excels at typo/image integration (weakness of Seedream/Flux)

### Concept
Typography = interactive surface, not overlay. Human subjects stay whole/photorealistic while physical forces (water, impact, softness) break through and deform the text.

> "The people stay whole, while motion and space break through the letters."

### 4 directions (portrait 9:16)
1. **WAVE CUT** — waves carving water AND typography (bright)
2. **RIM RISE** — subject reaching above frame, interacting with letters (medium contrast)
3. **IMPACT FRAME** — power toward lens (dark/dramatic)
4. **SOFT SWIRL** — handcrafting sweetness (very bright, cream palette)

### Prompt template
```
[Physical force] interacting with bold [typography style] text.
Human subjects remain whole and photorealistic while [motion/element]
breaks through the letters. [Art direction].
Palette: [warm cream/beige | dark dramatic | bright soft].
9:16 portrait composition.
```

### Applications
- **Culture en Saveur**: "Soft Swirl" = cooking/kids, cream palette matches brand
- **Cortex Leman**: "Impact Frame" for tech brand content

---

## #25 — Architectural Storyboard Technique
**Source:** @LeeLinAI123 — Yellow Crane Tower 3D deconstruction
**Workflow:** Opus 5 (Claude) writes technical spec → Seedance 2.0 executes layer-by-layer 3D assembly

### Template
```
Video Description: Create a [durée]s, [ratio] [genre] video showing [sujet].

Core Instruction: [ pédagogical goal ]. Every component must be [visibility constraint].

Motion Style:
- All components [motion type] along [axis].
- Only one group moves at a time while others remain stationary.
- Active component = 100% brightness, inactive = ~60% dimmed.
- ~0.15s pause after each group settles.

Timeline ([sequence]):
0.0-X.Xs: [phase 1]
X.X-X.Xs: [phase 2]
...

Negative Constraints: No [exhaustive list of failure modes].
```

### Key innovations
1. Timeline to the tenth of a second
2. Conditional brightness (active=100%, inactive=60%)
3. Rhythmic pauses (0.15s between steps)
4. Seamless loop
5. Exhaustive negatives

### Applications
- **african-heroes**: Reconstruct monuments layer by layer
- **Culture en Saveur**: Ingredient decomposition, instrument assembly
- **Cortex Leman**: Product/architectural demos

---

## #31 — Two-Stage Choreography Pipeline (Storyboard→Video) ⭐⭐ MOST SOPHISTICATED
**Source:** @KimAkiyama81 (Viper Studios) — Fight scene via Seedance 2.0 in Topview AI
**Engagement:** 79 likes, 5.2K vues, 62 bookmarks (78% save ratio)
**Full thread recovery technique:** see `references/x_thread_recovery.md`

### Architecture: pipeline in 2 stages (image → video)

```
Stage 1: STORYBOARD PROMPT (image)     → 12-panel pencil-and-ink board
                                              ↓ used as motion reference
Stage 2: SEEDANCE 2.0 PROMPT (video)   → photoreal live-action footage
```

**Fundamental innovation:** the storyboard uses **featureless mannequins** (blank oval heads, no faces, no costume detail). This forces the model to think in terms of **pure movement** (vectors, arcs, speeds) rather than appearance. The video prompt then translates those movements into photoreal action with **state locks** (HARD LOCK constraints).

### Stage 1 — Choreography Storyboard (12 panels, 4×3 grid)

| Technique | Description |
|-----------|-------------|
| **Laban Movement Analysis** | Real dance notation. GOLD = light/sudden/free (protagonist), RED = heavy/direct/bound (antagonist). Colored motion vectors overlaid on mannequins. |
| **Featureless mannequins** | Blank oval heads, zero face/costume. Board specifies PURE MOVEMENT, not appearance. |
| **Camera setup taxonomy** | 5 angles reused across panels: A=wide profile, B=low angle, C=overhead, D=OTS, E=lateral tracking |
| **Scale lock** | Size/mass ratio maintained in every panel |
| **Dismemberment continuity** | Per-panel state tracking: "left arm severed panel 6 → stump from 6-12, forearm on ground from 7+" |
| **Bracketed sections** | `[HEADER]`, `[BOARD]`, `[STYLE]`, `[REFERENCES]`, `[CONTINUITY]`, `[RULES]`, `[BEATS]` |

### Stage 2 — Seedance 2.0 Video Prompt (14 sections)

| Section | Role |
|---------|------|
| `SCENE CONTEXT` | Setting, frame-left/frame-right positioning |
| `ACTIVE REFERENCES` | Lock: `@char_X`, `@loc_X`, `@prop_X` + "100% matches the reference" |
| `LOCATION MAP` | Foreground / Midground / Background described separately |
| `FIRST FRAME / BLOCKING` | Exact visual state of frame 0 |
| `FORMAT MODE` | "Timed multishot. Hard cuts at stated seconds only" |
| `OPTICS` | FOV in degrees per cut (63°/84°/47°/29°), "35mm anamorphic, oval bokeh" |
| `ACTION` | Timeline 0.0-15s with speeds (60 km/h, 25 km/h) + `HARD CUT` markers |
| `PERFORMANCE` | Facial expressions, breathing, eye tracking per beat |
| `PHYSICS` | Mass behavior (floor shudders), friction marks, sparks, dust |
| `LIGHTING` | 5600K Kelvin, "stands one stop down", "soft sky fill" |
| `COLOR GRADE` | "Steel blue-grey, crushed blacks, retained midtones" |
| `AUDIO` | Sound design synced: impacts, blade whoosh, crowd roar |
| `POSITIVE LOCKS` | **HARD LOCK** — absolute constraints (katana in grip, pistols holstered, screen direction, crowd capacity, dismemberment state) |

### Abstract template (for adaptation)
```
# STAGE 1: STORYBOARD (image generation)
[HEADER]: title, format, camera (e.g. ARRI ALEXA 35)
[BOARD]: NxM panels, ratio, style (pencil-and-ink mannequins)
[STYLE]: colored movement notation — PROTAGONIST=color1 (agile), ANTAGONIST=color2 (mass)
[REFERENCES]: silhouettes only, featureless, scale lock
[CONTINUITY]: prop/extra state per panel, screen direction locked
[RULES]: camera setups (A-E), style locks
[BEATS]: each panel = camera setup + mid-transit action + movement vectors

# STAGE 2: VIDEO PROMPT (Seedance)
SCENE CONTEXT: setting, frame-left/frame-right positioning
ACTIVE REFERENCES: @char_X (100% matches), @loc_X, @prop_X
LOCATION MAP: foreground/midground/background separate
FIRST FRAME / BLOCKING: exact frame-0 visual state
FORMAT MODE: Timed multishot, hard cuts at specified seconds
OPTICS: FOV per cut in degrees, character lens
CAMERA: position per cut
ACTION: timeline 0.0-15s with speeds + HARD CUT
PERFORMANCE: expressions, breathing, gaze per beat
PHYSICS: mass, friction, particles (sparks/dust)
LIGHTING: Kelvin, direction, differential stops
COLOR GRADE: palette + saturation + blacks
AUDIO: sound design sync per beat
POSITIVE LOCKS: HARD LOCK — props, wardrobe, direction, state continuity
```

### Why it's the most sophisticated pattern
- **Two-stage pipeline** (image→video) instead of single-stage — mannequin storyboard forces movement-first thinking
- **Laban Movement Analysis** = movement quality (light/heavy, sudden/sustained, free/bound), not just position
- **State tracking** (dismemberment continuity) + **POSITIVE LOCKS** = absolute prop/direction consistency
- **Combines** #14 (identity lock), #25 (timeline), #28 (structured schema), #30 (cinema specs)

### Applications
- **african-heroes**: ⭐⭐⭐ Historical battles (Chaka Zulu vs rivals, Nzinga resistance, Adoua). Laban notation distinguishes African combat styles (masai jumping, Egyptian dam-boxing, Angolan capoeira)
- **Cortex Leman**: ⭐ Product/process storyboards for corporate content
- **Culture en Saveur**: ❌ Too violent/specialized for children's cooking content

---

## #32 — Scene-by-Scene Timeline (Entry-Level Pattern)
**Source:** @noorlewisx — Travel vlog 15s via Seedance 2.0 / WaveSpeed AI
**Engagement:** 358 likes, 15.5K views — **most viral pattern** (accessible format)

### Structure: 3-part prompt (~300 words)
```
Part 1: Global description (character lock + style keywords)
Part 2: N scenes with timing (Scene 1 (0-2s): action + setting + camera)
Part 3: Style block (global look + transitions + grade)
```

### Why it works as entry-level
- **~300 words** vs 1000+ for #28/#31. Accessible to non-experts.
- **7 scenes = sweet spot**: enough to tell a story, not enough to lose coherence.
- **Implicit transitions**: "smooth transitions" in style block suffices — no HARD CUTs needed.
- **Text overlay native**: can request on-screen text (e.g., CTA in last scene).
- **Character consistency implicit**: no reference lock needed, global description suffices.

### Template
```
[GLOBAL: recurring character + ambiance + technical keywords]

Scene 1 (0–Xs): [action + setting + camera]
Scene 2 (X–Ys): [action + setting + camera]
...
Scene N (Z–15s): [action + ending + optional text overlay]

Style: [aesthetic keywords + transitions + color grading + vibe]
```

### Applications
- **Culture en Saveur**: ⭐⭐⭐ **PERFECT** — 7 brief activities = 7 scenes of 2s each. Immediately usable.
- **Cortex Leman**: ⭐⭐ Brand content multi-services showcase
- **african-heroes**: ⭐⭐ "7 historical sites of Africa" — travel vlog format diversification

---

## #33 — End-to-End AI Film Pipeline (Macro Workflow)
**Source:** @rich_odinn — X Article "How to Make an AI Film"
**Type:** Pipeline/workflow (not a prompt) — 6-tool chain + economics

### Pipeline
```
Claude (script + shot list + prompts per frame)
    ↓ Style Bible
Midjourney (character design multi-angle → reference lock)
    ↓
Runway Gen-4 / Kling 2.5 (video, consistent character)
    ↓
ElevenLabs (voice directed like an actor: emotional notes, pacing, breath)
    ↓
Suno / Udio (original score scene-by-scene, not continuous track)
    ↓
DaVinci Resolve (edit + color grade — human craft, most important step)
```

### Key principles
- **Style Bible FIRST**: generate same character at multiple angles in MJ before animating anything
- **Claude as assistant director**: screenplay + shot list + visual prompts referencing Style Bible
- **Score scene-by-scene**: generate per-scene to match emotional arc, not one continuous track
- **DaVinci = most important step**: "Pacing and sound design are still entirely human craft"

### Economics
| Revenue | Amount |
|---------|--------|
| Festival prizes | $1M (Astana AIFF) — "lottery ticket" |
| **Brand AI commercials** | **$3,000–$25,000/project** |
| Festival scouting | Reply AIFF Venice, LifeArt, WAIFF |

### Festival eligibility
- Minimum 50-70% AI-generated visual content
- Production log documenting which tools generated which shots
- Original music ONLY (copyright = instant disqualification)
- Original voices (no unlicensed clones)

### Timeline
9-min short = **6-10 weeks** for a small team. Not a weekend.

### GLM-5.2 vs Claude in this pipeline
- Script/screenplay FR: GLM competitive (FR = strong training language)
- Shot list structured: Equal (technical format = GLM strength)
- JSON Storyboard (#28): Equal (machine format)
- Ultra-detailed visual prompts (#31 level): Claude superior (aesthetic nuance + long-context continuity)
- **Strategy**: GLM for 80% of Tars pipeline, Claude API for 20% expert

### Applications
- **african-heroes**: ⭐⭐⭐ Exact pipeline for 9-min animated episodes
- **Cortex Leman**: ⭐⭐⭐ $3-25K/project = direct pricing data for client offering
- **Culture en Saveur**: ⭐ Too heavy (6-10 weeks) for 15s promo — but Style Bible principle applies

---

## #34 — Multi-Biome Wardrobe Morph
**Source:** @itsshara_ai — Seedance 2.0 via Invideo

### Concept
One character traverses 3+ biomes in 15s. Identity stays locked (face/hair/build via @img1) but outfit changes **completely** at each hard cut. Each biome has its own camera angle + sound design.

### Structure: N segments × ~5s, repeated template
```
[CONTINUATION LOCK: "continuing directly from Part N"]
[REFERENCE: @imgN, "matching her exact face, hair, and build in every angle"]

(Ts1–Ts2) — BIOME_1 — CAMERA_TYPE_1:
  Hard cut — wardrobe transforms the instant the world changes.
  [environment] [lighting] [wardrobe = "COMPLETELY DIFFERENT... not a variation"]
  Camera: [movement + lens spec]
  Audio: [biome-specific sound design]

(Ts2–Ts3) — BIOME_2 — CAMERA_TYPE_2: [même template]
(Ts3–Ts4) — BIOME_3 — CAMERA_TYPE_3: [même template]

Overall: [quality lock] + [consistency: "Same 35mm anamorphic lens character throughout"] + [negatives]
```

### 3 innovations
1. **Wardrobe Transformation on Hard Cut** — inverse of #31 state tracking: controlled state change planned per cut
2. **One Camera Angle Per World** — crane → tracking → push-through. Prevents visual monotony
3. **Lens Character Consistency** — same 35mm anamorphic + film grain across all biomes unifies disparate environments

### Applications
- **african-heroes**: ⭐⭐⭐ Hero through epochs/biomes — Mansa Musa: Cairo (desert) → Mecca (pilgrimage) → Niani (forest)
- **Cortex Leman**: ⭐⭐ Brand content "même modèle à Genève/Lausanne/Zermatt"
- **Culture en Saveur**: ⭐⭐ "Même enfant découvrant 7 activités"

---

## #35 — Video Clone & Character Swap (Video-to-Video) ⭐ NEW PARADIGM
**Source:** @itsshara_ai — 203 likes, 11.7K views (most viral tweet from this account)

### Paradigm shift
All patterns #14-#34 = **text-to-video** (describe what you want to see).
#35 = **video-to-video** (start from existing video, swap one element).

### 3-step workflow
```
1. Reference video → Seedance 2.0 (source of motion + composition + timing)
2. Character sheet → GPT Image 2 (new character design)
3. One prompt: "recreate exactly, only replace the character"
```

> "AI video is no longer about generating from scratch. It's about directing."

Motion, composition, and timing are **inherited** from the source video — no need to recreate them. Only the character changes.

### Applications
- **african-heroes**: ⭐⭐⭐ Recreate known historical scenes (battle paintings, engravings) with African characters
- **Cortex Leman**: ⭐⭐ Recreate known ads with client branding: "Recreate this Nike ad exactly, only replace the athlete"
- **Culture en Saveur**: ❌ Not applicable

---

## #36 — Comic Grid Pipeline (GPT Image 2 → Seedance 2.0)
**Source:** @itsshara_ai — 184 likes, 72 replies, 8.6K views

### 2-stage pipeline for stylized animation

**Stage 1 (GPT Image 2):** Generate a **16-panel comic grid** in a specific visual style (e.g., Spider-Verse). Each panel = one action beat. The visual style (ink linework, halftone, neon streaks) is defined HERE and transfers to the animation.

**Stage 2 (Seedance 2.0):**
> "Animate this 16-panel comic storyboard into a single continuous 15-second cinematic sequence."

The Stage 2 prompt:
- Rephrases narrative beats as **cinematic prose** (not panel-by-panel)
- Maps motion: "quick dynamic cuts synced exactly to each beat above"
- Adds format: "smooth 24fps motion, vertical 9:16 aspect ratio"
- Cleanup: "the panel captions were only for the storyboard stage, the final video itself must be completely clean"

### Why it works
The comic grid serves as a **double reference lock** — it locks both the narrative beats AND the visual style. Seedance sees the Spider-Verse style in the grid and reproduces it in animation. Unlike #31 (mannequin storyboard = movement only), here the storyboard transfers **aesthetic style** directly.

### vs #31
| #31 (Choreography) | #36 (Comic Grid) |
|---------------------|-------------------|
| Mannequin storyboard (pencil-and-ink, no faces) | Comic grid (stylized, Spider-Verse) |
| Style applied in video prompt | **Style transfers visually** from storyboard |
| Focus: movement (Laban notation) | Focus: narrative + aesthetic |

### Applications
- **african-heroes**: ⭐⭐ Youth animation — historical narrative as stylized comic → animation
- **Culture en Saveur**: ⭐⭐⭐ Spider-Verse style = eye-catching for kids 4-12. Ink + neon = modern and attractive
- **Cortex Leman**: ⭐ Stylized brand content (limited)

---

## #37 — Audio Tag Notation
**Source:** @itsshara_ai — 11 likes, 617 views (niche but unprecedented)

### Concept
Inline audio tags in the video prompt to request synthesized sound design directly in the generated video.

**Example (Cyborg Ronin):**
```
[Visual description + action]
[Rhythm/pacing keywords]
<blade slashes> <impacts> <gunfire> <rain> <whooshes>
[Negative constraints]
```

Audio tags = `<sound_description>` placed after visual description, before negatives.

### Why notable
Unprecedented across all catalogued patterns. No other creator uses angle-bracket notation for sound design. If Seedance interprets these tags (needs verification), it eliminates the need for post-production sound design — the audio is integrated at generation time.

### Audio tag libraries by project
- **african-heroes**: `<shields clashing>` `<war drums>` `<spear impacts>` `<battle cries>` `<distant gallops>`
- **Culture en Saveur**: `<sizzling>` `<children laughing>` `<pot bubbling>` `<utensils clinking>`
- **Cortex Leman**: `<office ambience>` `<keyboard typing>` `<coffee machine>` (limited utility)

### Applications
- **african-heroes**: ⭐⭐⭐ Battles: shields, drums, spears, cries, gallops
- **Culture en Saveur**: ⭐⭐ Cooking ambience: sizzling, laughing, bubbling
- **Cortex Leman**: ⭐ Not critical for brand content

---

## #38 — Narrative Prose Sequence (3-Act Natural) ⭐ ENTRY-LEVEL FOR PROCESS/COOKING
**Source:** @noorwithwifi (NoorAI) — Anime cooking video via Seedance 2.0
**Engagement:** 290 likes, 10K views, 168 bookmarks (58% save ratio)

### Concept
One continuous prose paragraph. No sections, no timestamps, no JSON. Natural narrative structure ("Begin... then... Finally") replaces technical timing. The absolute entry-level pattern — ~100 words.

### Template
```
[STYLE LOCK opening: "cinematic [X]-style"]

[ACT 1 - "Begin with"]: [action + detailed ingredients/elements]
[ACT 2 - "then"]: [process + setting + sensory details]
[ACT 3 - "Finally"]: [completion/plating/final action]

[STYLE BLOCK closing: lighting + vibe + camera + transitions + visual quality]
```

### Why it works
- **3 natural acts** suffice to structure 12.5s — no micro-timing needed
- **Style mentioned 2×** (opening + closing) — reinforcement lock
- **Precise sensory details**: "marbled beef", "crackling campfire", "steaming broth" — guide model on textures and motion
- **Implicit transitions**: "smooth transitions" = 1 word instead of specifying each HARD CUT
- **Extreme simplicity**: ~100 words, accessible to anyone. Lowest barrier to entry.

### vs other patterns
| vs #32 (Scene-by-Scene) | vs #29 (Prose) |
|--------------------------|----------------|
| #32 = explicit timestamps. #38 = transition words | #29 = surreal/dreamlike. #38 = sequential/process |
| #32 = N equal scenes. #38 = 3 unequal acts | #29 = atmosphere. #38 = concrete steps |

### Adaptation for Culture en Saveur (ready-to-use)
```
Create a cinematic anime-style cooking video showing children preparing
authentic African cuisine at a colorful summer camp kitchen. Begin with
children washing colorful vegetables, preparing spices, and mixing flour,
then cook ingredients in large pots over a warm stove while laughing and
sharing tasks. Finally, plate the dishes in ceramic bowls, garnish with
fresh herbs, and show the children proudly presenting their creations.
Capture warm golden lighting, joyful camp vibes, detailed food close-ups,
smooth transitions, and beautiful anime-inspired visuals.
```

### Applications
- **Culture en Saveur**: ⭐⭐⭐ **PERFECT** — literally the use case. Immediate adaptation: pho → African cuisine, campsite → MQP kitchen
- **african-heroes**: ⭐⭐ Traditional cooking as companion content (yassa, mafé, dibi)
- **Cortex Leman**: ⭐⭐ Brand content "process" — manufacturing a service/product

---

## #39 — Luxury Product Commercial Timeline (7-Segment Alternated)
**Source:** @AIwithJessica — Luxury fragrance campaign via Seedance 2.0 / thankyouai_hq
**Engagement:** 265 likes, 36K views, 69 replies — **viral**

### Concept
7-segment timeline for premium product advertising. Product locked via @image_1 reference (product lock) across all shots. Systematic alternation between **sensory macro** (ingredients/materials) and **product hero** (the product itself).

### Structure: 3 parts (~450 words)

**Part 1 — Header + Product Lock:**
```
[Campaign/brief] | [duration], [aspect ratio], [setting],
[transition policy: "hard jump cuts only, no transitions"]

The product is the [item] in @image_1: [detailed shape/materials/colors].
Keep the [product] design, proportions, label, colors, and materials identical
to @image_1 in every product shot.
```

**Part 2 — Timeline 7 segments alternated:**

| # | Type | Role |
|---|------|------|
| 1 | Sensory macro | Atmosphere |
| 2 | Sensory macro | Atmosphere |
| 3 | **Product hero** | Anchors brand |
| 4 | Sensory macro | Atmosphere |
| 5 | **Product hero** | Anchors brand |
| 6 | **Product hero + env** | Brand in context |
| 7 | **Product hero finale** | Money shot |

Alternation pattern: A-A-B-A-B-B-B (escalation toward product)

**Part 3 — Style Block:**
```
Ultra-photorealistic [genre] commercial, premium [category] campaign,
[brief-specific palette].
[material physics: glass refraction, reflections, etc.],
[natural lighting type], cinematic depth of field, luxury editorial photography,
steady camera motion, no distortion, maintain exact [product] proportions throughout.
```

### 3 innovations
1. **Product Reference Lock (@image_1)** — product consistency across 4 shots. We'd seen character lock (#31, #34); this is product lock. Critical for brands.
2. **Sensory Macro ↔ Product Hero alternation** — sensory shots (ingredients/textures) build atmosphere, product shots anchor brand. Premium rhythm.
3. **Transition Policy in Header** — "hard jump cuts only, no transitions" declared upfront, not in footer.

### Adaptation for Cortex Leman (client brand content)
```
Luxury product campaign for [CLIENT PRODUCT] | 15 seconds, 16:9,
[setting], hard jump cuts only, no transitions.

The product is the [item] in @image_1: [description].
Keep the [product] design, proportions, label, colors, and materials identical
to @image_1 in every product shot.

[00:00-00:02] [Sensory macro: ingredient/material 1]
[00:02-00:04] [Sensory macro: atmospheric element 2]
[00:04-00:06] [Product hero: product on pedestal, eye-level dolly]
[00:06-00:08] [Sensory macro: texture/detail]
[00:08-00:10] [Product hero: product in context + accessories]
[00:10-00:12] [Product + environment: shadows/natural light]
[00:12-00:15] [Product hero finale: money shot + blurred background]

Style: Ultra-photorealistic [genre] commercial, [palette],
[material physics], steady camera, maintain exact proportions throughout.
```

### Applications
- **Cortex Leman**: ⭐⭐⭐ **PERFECT** — exact format for client brand content. Pricing: $3-25K/project (cf #33)
- **Culture en Saveur**: ⭐⭐ "Event as product" — show event as premium product
- **african-heroes**: ⭐ Not applicable (not a narrative/historical format)

---

## #40 — Vlog Dialogue Track (Seedance 2.0 Mini) ⭐ SOCIAL-NATIVE WITH SYNCED AUDIO
**Source:** @AIwithJessica — Portugal Match Day Vlog via Seedance 2.0 Mini / Pollo AI
**Engagement:** 387 likes, 44.5K views, 50 bookmarks

### Concept
Each 3s timeline segment has its own **spoken dialogue line**. Seedance 2.0 Mini generates frame-accurate synced audio (voice + SFX) in a single pass — no post-production audio editing needed.

### Structure
```
[Title + Duration + Parts]

PART 1 · 0–15s — [Theme 1]

0–3s | [Segment Name]
[Action description + camera]
Dialogue: "[exact spoken line]"

3–6s | [Segment Name]
[Action description + camera]
Dialogue: "[exact spoken line]"

Seamless Transition: [transition rule between parts]

PART 2 · 15–30s — [Theme 2]
[... continue with Dialogue: per segment ...]
```

### 3 innovations
1. **Dialogue inline per segment** — each beat has its own spoken line. Seedance Mini = frame-accurate audio in single pass. Revolutionary for vlog/social format.
2. **Camera Angle Continuity** — "Same selfie angle, now seated" = seamless transition without hard cut. Character maintains framing across cuts.
3. **GRWM (Get Ready With Me)** — native TikTok/Reels/Shorts format. Selfie cam + back cam alternation mimics authentic vlog style.

### Why it matters technically
Seedance 2.0 Mini (via Pollo AI) is the first model generating **synchronized dialogue + SFX** in one pass. No separate audio editing, no lip-sync post-prod. Just write the dialogue in the prompt.

### Adaptation for Culture en Saveur (vlog event enfants)
```
Culture en Saveur Vlog (20s)
PART 1 · 0–10s — Arrivée et préparation

0–3s | Entrée au MQP
Enfant court vers la cuisine du MQP Petit-Lancy, caméra selfie frontale.
Dialogue: "Vite, on est en retard! J'ai trop hâte de cuisiner!"

3–6s | Tablier
L'enfant met son tablier, caméra au niveau des yeux.
Dialogue: "Mon tablier! Aujourd'hui on fait quoi?"

6–10s | Découverte des ingrédients
Plan table: légumes, épices africaines colorées. Caméra top-down macro.
Dialogue: "Regarde tous ces légumes! Ça sent trop bon!"
```

### Applications
- **Culture en Saveur**: ⭐⭐⭐ Vlog with talking children. Social-native, max authenticity. Audio in one pass = huge production gain.
- **Cortex Leman**: ⭐⭐ Influencer/vlog brand content. AI persona speaking to audience.
- **african-heroes**: ⭐ Too casual for historical narration

---

## #41 — Anime Pre-Production Pipeline (APOB AI + GPT Image 2 + Seedance 2.0) ⭐⭐ FOR RECURRING SERIES
**Source:** @AIwithJessica / @apob_ai — Anime Creation Playbook article
**Engagement:** 141 likes, 34.8K views

### Concept
Complete **6-stage pre-production system**. Not "prompt → video" but a structured pipeline that turns a story idea into a repeatable storytelling system. Each stage builds on the previous one's output.

### The 6 stages
```
1. AI Influencer Generator → Character identity base (reusable face)
2. Character Sheet (GPT Image 2) → 6-angle ref: front, side, back, close-up, fighting stance, dynamic pose
3. Story Bible Image → "Emotional north star" (environment + lighting + tone + symbolic object)
4. 16-Panel Storyboard (GPT Image 2) → Detailed narrative beats panel by panel
5. Chat to Edit → Continuity pass (revisions without full restart)
6. Seedance 2.0 → Animation with time-coded direction + CHARACTER LOCK + STYLE + CAMERA + MOTION + LIGHTING + ENDING
```

### Key innovations

**① Character Sheet multi-view (Stage 2)** — locks 6 views per character before any animation:
```
For each character, show front view, side view, back view,
close-up face expression, fighting stance pose, and dynamic dance pose.
Character lock: [Name] always has [features]. Do not swap outfits, hair colors, powers, genders, or identities.
```
More robust than text-only character lock (#31, #34).

**② Story Bible "emotional north star" (Stage 3)** — one image captures the entire mood:
```
A cinematic first frame that captures environment, lighting, emotional tone,
and symbolic object. This image tells every later generation what the film
should FEEL like, not only what it should contain.
```

**③ Edit stage (Stage 5)** — partial revisions without restart:
> "Return to Chat to Edit, adjust storyboard, strengthen one keyframe, or rewrite only the time-coded section that failed."

**④ Director mindset** — "Iterate like a director, not a gambler". Review criteria: character consistency, visual consistency, emotional clarity, camera support, series potential.

### vs #33 (End-to-End Film Pipeline)
| #33 (6 disparate tools) | #41 (unified platform) |
|--------------------------|------------------------|
| MJ + Runway/Kling + ElevenLabs + Suno + Resolve | APOB + GPT Image 2 + Seedance (3 tools, 1 platform) |
| Live-action focus | Anime/stylized focus |
| No edit stage | Chat to Edit = partial revisions |
| Character = MJ images | Character sheet 6-view lock |

### Adaptation for african-heroes (série animée historique)
```
Stage 1: AI Influencer Generator → Create [African hero] (e.g., Chaka Zulu)
         reusable face across episodes
Stage 2: Character Sheet → 6 views: front, side, back, portrait, battle stance, ceremonial
         Lock: skin, scarifications, weapons, period clothing
Stage 3: Story Bible → "Emotional north star": savanna at sunset, golden light, Impi army formation
Stage 4: 16-Panel Storyboard → Battle of Gqokli Hill, panel by panel
Stage 5: Chat to Edit → Verify historical continuity (weapons, uniforms, formations). Correct anachronisms.
Stage 6: Seedance 2.0 → Animation with CHARACTER LOCK + TIMELINE + CAMERA + MOTION + LIGHTING + ENDING
```

### Applications
- **african-heroes**: ⭐⭐⭐ **PERFECT** — exact pipeline for historical animated series. Character sheet = hero locked across episodes. Story Bible = visual consistency. Edit stage = historical corrections.
- **Culture en Saveur**: ⭐⭐ Reusable youth mascot across promo content
- **Cortex Leman**: ⭐⭐ Brand mascot/character. Content series with consistent AI persona

---

## #42 — Sound Design Bible (Full Musical Score + Spatial SFX)
**Source:** @bmx_ai13 — Nighttime urban fashion run via Seedance 2.0
**Engagement:** 260 likes, 9.6K views, **271 bookmarks (104% ratio — exceeds likes!)**
**Author:** Same as #30 (Imperfect Cinema). @bmx_ai13 masters 2 layers: visual (#30) + audio (#42).

### Concept
First pattern with a **complete musical score** integrated into the video prompt. Goes far beyond #37 audio tags — this is a full **music direction bible** with BPM, instrument list, synced timeline, and spatial sound design with perspective tracking.

### 2 audio sections (appended after shot sequence)

**AUDIO / MUSIC** — full score direction:
```
[BPM range] [genre] [energy descriptor].
[Instrument list: kick, bass, percussion, synths, pads, etc.]

0–Xs: [dynamic level + instruments]
X–Ys: [change: beat drops/strips/returns]
Y–Zs: [final: max momentum then abrupt stop]
```

**REALISTIC SOUND DESIGN** — spatial SFX:
```
[Inventory: footsteps, traffic, machinery, breathing, reverb, hum,
door chime, ambient, object handling, etc.]
[Acoustic per environment: tile vs concrete vs outdoor]
Sound perspective must follow camera distance naturally.
```

### 3 innovations
1. **BPM-precise musical score** — 150-158 BPM with instrument list and dynamic timeline synced to visual beats
2. **Acoustic material tracking** — footsteps change sound per surface (tile/concrete/stairs/shop)
3. **Perspective tracking** — audio follows camera distance naturally (closer = louder)

### Audio pattern escalation
| Pattern | Audio Layer | Level |
|---------|------------|-------|
| #37 | SFX tags `<gunfire>` | Basic |
| #40 | Spoken dialogue per segment | Intermediate |
| **#42** | **Full score + spatial SFX + perspective** | **Expert** |

### Template
```
[SHOT SEQUENCE as #30/#32]

AUDIO / MUSIC:
[Genre] [BPM range] [energy descriptor].
[Instrument list]

[Timeline synced:]
0–[X]s: [dynamic + instruments]
[X–Y]s: [change]
[Y–Z]s: [final momentum + abrupt stop]

REALISTIC SOUND DESIGN:
[Inventory by environment]
Sound perspective must follow camera distance naturally.
```

### Applications
- **african-heroes**: ⭐⭐⭐ Epic tribal score (djembe, kudu horn, assegai) + battle SFX
- **Culture en Saveur**: ⭐⭐ Joyful kitchen ambience + children sounds
- **Cortex Leman**: ⭐⭐⭐ Brand sonic identity. Each client gets audio signature (BPM + instruments + trade SFX)

---

## #43 — Mixed Media Composite: Live-Action + 2D Sticker ⭐⭐⭐ VIRAL Mascot Format
**Source:** @leo_xiaolei (多肉) — Capybara cooking chaos via Seedance 2.0
**Engagement:** 353 likes, 20.9K views, **503 bookmarks (142% ratio — highest in catalog)**
**Format:** 10s, 9:16 portrait, **first non-English prompt (Chinese)**

### Concept
*Who Framed Roger Rabbit* in AI generation. **Two visual layers** in the same scene:
- Layer 1: photoreal live-action (real kitchen, real human hands with visible pores)
- Layer 2: flat 2D sticker cartoon character (outline, paper texture, NOT re-lit by real light)

### 5 innovations

**① Mixed Media Composite** — "全程保持纯2D平面质感，不被真实光照重打光" (stays flat 2D, not re-lit by real light).

**② Physical Cross-Layer Interaction** — real human hands grab, bonk, and feed the cartoon character.

**③ Cartoon Physics Tags:**
| Tag | Effect |
|-----|--------|
| `Duang` / Cartoon Bump | Red bump on head |
| `Swirl Eyes` (蚊香眼) | Spiral eyes (dizzy) |
| `Fountain Tears` | Blue tears as water jets |
| `X Eyes` | X eyes (K.O.) |
| `Dizzy Stars` | Stars circling head |
| `Soul Smoke` | Soul smoke from nose |

**④ Mascot Character Lock** — reusable character across video series (Capybara Lulu: yellow body, orange shorts, mandarin on head).

**⑤ Slapstick Comedy Arc** (4 acts in 10s):
```
[0-3s] Chaos (mascot causes disaster)
[3-5s] Punishment (human bonks mascot)
[5-8s] Forced remedy (mascot cries, human forces fix)
[8-10s] K.O. (overdose, X eyes, soul departs)
```

### Template
```
【风格】Live-Action + Flat 2D Sticker Composite, [POV type], [quality], [orientation]
【时长】[Duration], [aspect ratio]
【场景】[Realistic environment with lighting]
【角色】[Mascot name] ([locked appearance + personality + 2D rule])
       Real human hands enter frame.

[0-Xs] Shot 1: [Comedy beat + cross-layer interaction + cartoon physics tag]
音效：[SFX]
[repeat per shot]
```

### Why 142% bookmark ratio (highest in entire catalog)
1. Visual contrast attracts the brain 2. 9:16 viral native 3. Brandable mascot 4. Universal slapstick 5. POV immersion

### Applications
- **Culture en Saveur**: ⭐⭐⭐ **PARFAIT** — Mascotte 2D chef cartoon dans vraie cuisine event. Enfants interagissent. 9:16 natif social.
- **Cortex Leman**: ⭐⭐⭐ Client mascot 2D interacting with real products. Brand viral content.
- **african-heroes**: ⭐⭐ Trickster legends (Anansi 2D in photoreal African village). Lighter than #41 anime.

---

## #44 — Architectural Renovation Morph (Camera Lock + Construction Logic)
**Source:** @Naiknelofar788 — Home renovation reveal via Seedance 2.0

### Concept
Fixed-camera transformation sequence. Camera stays **absolutely locked** (no zoom, no pan, no tilt) for the full 15s while a dilapidated interior rebuilds itself sequentially following logical construction order: floor → walls → details → furniture.

### 3 innovations

**① Absolute Camera Lock** — unlike #30 (continuous camera movement) or #43 (dynamic multi-shot), #44 mandates zero camera motion. The transformation happens *within* the frame. This is the inverse pole of the camera spectrum.

**② Sequential Construction Logic** — transformation follows real-world construction sequence, not random morphing:
```
Floor (tile/hardwood) → Walls (paint/cladding) → Architectural details (moldings/fixtures) → Furniture/decor
```

**③ First Explicit Negative Prompt Section** — a dedicated `Negative:` block calling out exact failure modes (people, camera movement, deformation). Not inline constraints (#30) but a standalone section.

### Template
```
Create a [duration], [ratio] video of a dilapidated [room type] undergoing complete renovation.

Camera: ABSOLUTELY FIXED. No zoom, pan, or movement of any kind. Tripod-locked perspective throughout.

Transformation sequence (must follow this construction order):
0-3s: Floor — cracked concrete transforms into [flooring material]
3-7s: Walls — stained/damaged walls rebuild into [wall finish]
7-11s: Details — moldings, light fixtures, windows install
11-15s: Furniture — [furniture pieces] materialize

Negative: No people, no animals, no camera movement, no zoom, no deformation,
no morphing of furniture into other objects, no text overlays.
```

### Applications
- **Cortex Leman**: ⭐⭐⭐ Real estate client content (before/after renovation, property flipping)
- **Culture en Saveur**: ⭐⭐ Event space transformation (empty hall → decorated event space)
- **african-heroes**: ⭐⭐ Historical monument reconstruction (Tombouctou mosques, Great Zimbabwe)

---

## #45 — One-Shot Continuous Camera Path ⭐⭐ FUNDAMENTAL CAMERA TECHNIQUE
**Source:** [OpusClip Blog — How to Create One-Shot Continuous Videos with Seedance 2.0](https://www.opus.pro/blog/one-shot-continuous-video-seedance) (fév 2026)

### Concept
Single unbroken camera movement flowing through multiple scenes/environments with ZERO cuts. Camera becomes a character discovering space. This is the most powerful camera technique Seedance 2.0 supports natively.

### 5 techniques
1. **Camera Path Mapping** — sketch floor plan before prompt: start → transition mechanism → end
2. **Spatial Transitions** — physical elements: doorways, corners, stairs, curtains, fog, arches. NO teleportation.
3. **Multi-Reference Assets** — @Image1/@Image2 per key scene, model navigates between them
4. **"All-around Reference" mode** — Seedance multimodal: images + reference video + audio + text
5. **Continuity Markers** — QC: smooth movement, logical transitions, lighting evolves, style consistent

### Sub-techniques
- **Vertical Space Exploration** — camera rises/descends through floors (RDC → roof → sky)
- **Speed Variation** — slow contemplative → accelerate → decelerate. Break monotony.
- **Rack Focus Transition** — focus shift through surface (glass partition) to new scene
- **Extension Chaining** — see #47 for 30-60s one-shots

### Template (Real Estate)
```
Generate a 15-second continuous one-shot video.
The camera starts at [START POINT] (@Image1 for style reference).
It pushes forward through [TRANSITION 1] into [SCENE 2].
Without cutting, the camera pans left, gliding past [DETAIL],
and continues forward through [TRANSITION 2] that opens onto [SCENE 3].
One continuous, flowing movement with no cuts.
Speed: slow in [SCENE 1], accelerating through [TRANSITION],
decelerating at [FINAL REVEAL].
```

### Template (Restaurant/Hospitality)
```
Generate a 15-second continuous one-shot.
Camera enters through the front door (@Image1), floats past the bar,
moves through the dining room with warm lighting, glides into the kitchen
to see the chef at work, and exits through a back patio into golden hour.
One continuous take, smooth Steadicam quality.
Reference @Video1 for camera movement style.
```

### Applications
- **Cortex Leman**: ⭐⭐⭐ Real estate virtual tours, restaurant showcases, event previews. Most monetizable.
- **Culture en Saveur**: ⭐⭐⭐ Walkthrough event space (empty hall → kitchen setup → kids cooking → buffet)
- **african-heroes**: ⭐⭐ Continuous historical site reconstitution (enter city → market → palace)

---

## #46 — Seamless Loop (TikTok/Reels Watch-Time Multiplier)
**Source:** Technique standard Seedance 2.0

### Concept
Video where last frame connects perfectly to first. Creates infinite loop. Essential for Shorts/Reels where loops = view multiplier.

### 3 core techniques
1. **Frame-Match Constraint** — prompt MUST describe end state = initial state
2. **Circular Narrative** — action returns to start (360° rotation, cyclic motion, spatial return)
3. **Negative Prompt** — `"no fade to black, no title cards, no end screens"`

### 4 loop strategies
| Strategy | Mechanism | Reliability |
|----------|-----------|-------------|
| **Rotation 360°** | Camera orbits subject. Frame 0 = Frame 360 | Highest |
| **Motion Cycle** | Cyclic action (kneading, wheel, pendulum) | High |
| **Spatial Return** | Character leaves, journeys, returns to start | Medium |
| **Match Cut to Loop** | End motion connects to start motion | Medium |

### Template (Rotation 360° Product)
```
Generate a seamless looping 10-second video.
Camera orbits 360° around [PRODUCT] (@Image1) on a pedestal.
Studio lighting, seamless white cyclorama background.
The final frame must match the first frame exactly —
continuous loop with no visible cut point.
Negative: no text, no fade, no transition effects.
```

### Template (Motion Cycle Cooking)
```
Generate a 10-second seamless loop.
Chef's hands knead dough on a flour-dusted wooden board (@Image1).
Camera fixed overhead, 45° angle.
The kneading motion is perfectly cyclic — push forward, fold,
rotate 90°, push forward again. Final position = initial position.
Warm kitchen lighting. Loop with zero visible cut.
```

### Applications
- **All projects**: ⭐⭐⭐ Algorithmic boost on Shorts/Reels (loops = watch-time multiplier)
- **Cortex Leman**: ⭐⭐ Product showcase loop for e-commerce/social
- **Culture en Saveur**: ⭐⭐ Cyclic cooking actions (kneading, stirring)

---

## #47 — Extension Chaining (30-60s Long-Form)
**Source:** [OpusClip Blog](https://www.opus.pro/blog/one-shot-continuous-video-seedance) — Extensions section

### Concept
Exceed 15s limit by chaining extensions. Each adds 4-15s. Build 30-60s one-shots with maintained continuity.

### Workflow
1. **Seed generation (0-15s)** — standard prompt with full setup
2. **Extension prompt** — describes EXPLICIT continuity: "Continue from [LAST STATE] into..."
3. **QC junction** — verify: style consistent, camera fluid, no visual "pop"
4. **Repeat** — max 4 extensions (60s practical limit, beyond = drift)

### Rule
Each extension MUST contain: reference to previous final state + transition description (no cut) + style/lighting/palette maintenance.

### Template (Extension segment)
```
Continue from the previous scene.
The camera, having just passed through [LAST ELEMENT],
continues moving forward into [NEW ENVIRONMENT].
Without cutting, the camera [NEW ACTION/PATH].
Maintain the same [LIGHTING/STYLE/PALETTE] as the previous segment.
The camera now reveals [NEW REVEAL] before transitioning toward...
```

### Concrete example — 45s Real Estate Tour
```
SEGMENT 1 (0-15s): "Camera enters front door, pushes through hallway
into open-plan living room with mountain view..."

SEGMENT 2 (15-30s): "Continue from the living room. The camera,
having reached the window with the mountain view, pans right and
moves through an open archway into a modern kitchen. Marble island,
brass fixtures. Camera glides past the island toward wine cellar..."

SEGMENT 3 (30-45s): "Continue from the wine cellar. The camera exits
through a side door onto a terrace. Golden hour. Camera descends
steps to reveal infinity pool. Arrives at pool edge, tilts up to sky. End."
```

### Combinatorics
- + #45 (One-Shot) → 30-60s continuous one-shot
- + #48 (Audio-Sync) → Musical one-shot over 45s
- + #46 (Loop) → Long-form loop

### Cost (kie.ai): 3 segments × 15s ≈ 1845 credits (~$1.85)

### Applications
- **Cortex Leman**: ⭐⭐⭐ 45-60s property tours, brand films, hospitality showcases
- **Culture en Saveur**: ⭐⭐ Complete event film (arrival → setup → cooking → buffet)
- **african-heroes**: ⭐⭐ Extended historical scenes (battle, ceremony, voyage)

---

## #48 — Audio-Synced Scene Transitions (Beat-Mapped Timeline)
**Source:** [OpusClip Blog](https://www.opus.pro/blog/one-shot-continuous-video-seedance) — Audio-Synced Scene Changes

### Concept
Scene transitions locked to musical structure (beat drops, buildups, breaks). Upload track (@Audio1) + describe WHEN visual shifts happen. Différent from #42 (descriptive audio) — here AUDIO DRIVES VISUAL.

### 3 techniques
1. **Beat-Mapped Timeline** — identify track key moments (drop at 5s, breakdown at 10s), align transitions
2. **Energy Matching** — visual intensity follows musical energy curve
3. **Synced Camera Behavior** — camera speed/movement driven by music (burst through door ON beat drop)

### Template (Music Video)
```
Generate a 15-second continuous one-shot synced to @Audio1.
Camera starts in a dark corridor lit by neon strips.
It pushes forward through the corridor, turning corners
as the bass builds.
At the beat drop (approximately 5 seconds), the camera
bursts through a door into a large open space filled with
floating geometric shapes and volumetric light.
The camera spirals upward through the shapes.
At 10 seconds (breakdown section), the camera breaks through
the ceiling into an open sky filled with stars.
One continuous upward journey, accelerating as the music builds.
```

### Template (Brand Commercial)
```
Generate a 15-second video synced to @Audio1.
[0-3s] Slow push-in on product (@Image1) in darkness. Music: ambient intro.
[3-5s] Light builds as beat builds. Product details emerge.
[5s ON BEAT DROP] Hard cut to product in full glory, dramatic studio lighting.
[5-10s] Product hero shots, camera moves with rhythm.
[10-13s] Breakdown: macro details, slow motion textures.
[13-15s] Final beat: pull back to wide, logo reveal, fade to black ON final note.
```

### Différence with #42 (Sound Design Bible)
| | #42 Sound Bible | #48 Audio-Sync |
|---|---|---|
| **Direction** | Visual → Audio (image determines sound) | Audio → Visual (music determines image) |
| **Control** | Descriptive (BPM, instruments, acoustics) | Temporal (beat drops, sync points) |
| **Usage** | Atmosphere, immersion | Energy, pacing, hype |
| **Input** | No track upload needed | Track (@Audio1) mandatory |

### Applications
- **Cortex Leman**: ⭐⭐⭐ Music-synced commercials, brand content, hype reels
- **Culture en Saveur**: ⭐⭐ Event teaser on upbeat music (buildup → drop → explosion)
- **african-heroes**: ⭐⭐ Action/battle scenes synced to African percussion

---



## #49 — SET LAYOUT Spatial Lock + GPT Image 2 Keyframe Pipeline (NEW Jul 2026)
**Source:** @itsshara_ai — thread 2082332177405227484, 27s video, 186 likes
**Stack:** GPT Image 2 (keyframes) → Seedance 2.0 (animation)

### 3 techniques

**① `SET LAYOUT:` — Spatial Geometry Lock**
A dedicated block that fixes character/object positions in physical space across multi-part prompts. More explicit than identity lock (#14) — locks WHERE things are, not just WHAT they look like.

```
SET LAYOUT: Skater remains on the rooftop level throughout this part.
Street level with the boy is visible far below, established via
establishing wide shot only.

SET LAYOUT: Skater launches from the fixed rooftop edge position
established in Part 1. The kite falls in a fixed downward arc past
the building's edge. The boy remains fixed on the street below,
looking up.
```

Key: each part RE-DECLARES the spatial state, referencing positions "established in Part 1". This prevents the model from teleporting characters or remixing geography between segments.

**② `NOT photorealistic` — Explicit Style Exclusion**
Inverse style declaration: instead of requesting a style, you EXPLICITLY exclude the default. Prevents the model from defaulting to photorealism when you want CGI/animated.

```
...polished CGI animated feature film quality rendering, NOT photorealistic...
...CGI animated feature film quality 3D animation style, NOT photorealistic.
```

Works because Seedance's default for high-detail prompts is photorealism. The negative style declaration overrides this default.

**③ `Continue seamlessly` — Cross-Part Continuity Lock**
Opening line of Part 2+ that inherits all visual state from Part 1:

```
Continue seamlessly from the previous scene. Maintain the exact same
characters, clothing, facial features, lighting, rooftop and street
environment, and CGI animated feature film quality 3D animation style,
NOT photorealistic.
```

Combines: continuation directive + enumerated state inheritance + style re-lock. More explicit than #47 extension chaining (which focuses on camera path continuity, not character/style state).

**④ GPT Image 2 → Seedance 2.0 Pipeline**
The emerging workflow: GPT Image 2 generates hero keyframes (character design, environment, lighting reference), then Seedance 2.0 animates them with the continuity locks above. This splits control: image generation for appearance, video generation for motion.

### Template (Multi-Part Cinematic Short)
```
PART 1 (0–15s):

[STYLE LOCK: cinematic style keywords, NOT photorealistic / NOT [unwanted default]]

[Character description with physical details]
[Environment description with lighting]

SET LAYOUT: [Character A position]. [Character B position].
[Spatial relationship between characters].

[Action with dialogue in quotes, emotion tags in parens]
Dialogue format: Character (emotion): "line"

PART 2 (15–30s):

Continue seamlessly from the previous scene. Maintain the exact same
characters, clothing, facial features, lighting, [environment],
and [style keywords], NOT [unwanted default].

SET LAYOUT: [Re-declare ALL positions, referencing Part 1 positions].
[New spatial relationships for this part].

[Action resolution with dialogue]
[Camera direction for ending]
```

### vs related patterns
| | #49 SET LAYOUT | #14 Identity Lock | #47 Extension Chaining |
|---|---|---|---|
| **What it locks** | Spatial positions + style | Character appearance | Camera path + time |
| **Multi-part** | Yes (explicit) | Per-cut | Yes (sequential) |
| **Key token** | `SET LAYOUT:` | `@img1` + PROHIBITED | "Continue from..." |
| **Best for** | Multi-character scenes with fixed geography | Solo character consistency | Long-form one-shots |

### Applications
- **african-heroes**: ⭐⭐⭐ Multi-part historical scenes (battle positioning, ceremony geography). `SET LAYOUT:` prevents armies/characters from teleporting between segments.
- **Cortex Leman**: ⭐⭐ Product demos with multiple stations (kitchen → counter → dining)
- **Culture en Saveur**: ⭐⭐ Kitchen scenes where animatrice position must stay fixed relative to children

---

### #14 — Triple Identity Lock (multi-character)
3 redundant layers: (1) upload ref images, (2) exhaustive feature list, (3) PROHIBITED list naming exact failure modes.
- Cuts ≤2s to prevent identity drift
- Negative prompting > positive description

### #16 — LLM Storybreaker Pipeline
LLM decomposes narrative into chronological beats BEFORE Seedance executes each beat.
`Script → Claude produces beats → Seedance executes each beat with director tokens`

### #18 — Raw Smartphone / Faux UGC
Tokens: "super casual real smartphone home video", "slight authentic handheld shake",
"rapid-fire montage with constant quick jump cuts every 1-2s"

### #22 — Dark Cinematic Epic / Mythological (God Mode)
Complex combat/spatial continuity. Heavy negative constraints on body part duplication.
Director tokens: dolly zoom, bullet time, one-take.

### #23 — Commercial / Brand Content Premium
Hero shots with product focus. Volumetric lighting, god rays, lens flares.
Pair with #16 (storybreaker) for structured ad narratives.

### #50 — Two-Part Storytelling Prompt (Pixar-style)
**Source:** @itsshara_ai — 15s court-métrage en 2 prompts consécutifs (Part 1: 0-7s + Part 2: 7-15s).
- Part 1: setup + conflict, style lock en début ("cinematic Pixar-style 3D animation")
- Part 2: "Continue seamlessly. Same characters, clothing, lighting." → resolution → cut to black
- Dialogue inline: `Character (emotion): "line"` (pas de TTS séparé)
- Arc complet en 15s: setup → conflict → resolution
- ⚠️ Style Pixar = rendu plat sur Seedance (validé pitfall #9). Storytelling pattern excellent, style à éviter. Combiner avec #51 pour rendu premium.

### #51 — Timestepped Cel-Shaded Anime (2s segments)
**Source:** @TechieBySA — Seedance 2.0 + GPT Image 2. 15s décomposé en segments de 2s.
- **Style anti-Pixar:** `"cel-shaded 3D anime, semi-realistic CGI, hand-painted textures, NOT cartoon NOT Disney NOT Pixar, heavy shadows, film grain"`
- **Structure:** `[0:00-0:02] Action + camera A→B→C`, etc. Granularité maximale pour action physique complexe
- **Audio:** beat structure qui dicte le cutting rhythm, pas juste atmosphère. "Every cut synced to the beat"
- Plus fin que #32 (scene-by-scene ~3s). Idéal pour combat/sport/danse chorégraphiés
- african-heroes ⭐⭐⭐ (Chaka Zulu, Nzinga), CES (activités dynamiques)

### #52 — Fantasy Cooking Choreography
**Source:** @auqibhabib — GPT Image 2 + Seedance 2.0 via OpenArt AI, 1500+ mots, cooking fantasy photoréaliste.
- **Object-as-transition:** objet lancé vers caméra → whip-pan → cut seamless scène suivante. Nouveau — aucun pattern précédent.
- **Camera choreography extrême:** rush low → 360° orbit → whip-pan → tracking → slow-mo particules. Plus dense que #31.
- **Breaking 4th wall:** perso regarde caméra, smirk/wink, dialogue direct au viewer
- **Personality directive:** "confident, mischievous, cute, slightly flirty, never overly sexualized" — arc psychologique
- **Multi-character comedy ensemble:** chaque perso secondaire a dialogue + réaction distincts (raffine #14)
- **Copyright safety:** "must not directly recreate any copyrighted character"
- **Texture tokens anti-flat:** skin/hair/fabric/steam/flour/broth/noodle/ceramic/wood/stone
- **Audio diegetic only:** no music, environmental + cooking sounds + dialogue court
- CES ⭐⭐⭐ (cuisine performance), african-heroes ⭐⭐ (transitions objets rituels)

---

### #53 — Versus-Card Paired Identity Lock
**Source:** [@NexlowX](https://x.com/NexlowX/status/2081470276479357205) — GPT Image V2 + Seedance 2.0, 7,4k vues (26 juil. 2026)

**Résout le problème de drift/blend entre 2 personnages en mouvement rapide.** Au lieu de créer 2 character sheets séparés, on génère une seule carte "VS" (versus-card) où les deux persos sont définis **en contraste l'un contre l'autre**.

**Insight clé :** "The character sheet isn't the asset — the VS layout is." La carte VS n'est pas du branding décoratif, c'est l'identity lock qui fait tout le travail.

**Pipeline (6 étapes):**
1. **GPT Image V2 → VS card** — 2 persos côte à côte, chacun avec stats + style tags + color palette
2. **Définir en opposition** — "flow king vs the rebel", "blue palette vs purple palette". Le contraste empêche le drift.
3. **Lock art direction** — reference frame (ex: Spider-Verse painterly comic, golden hour) héritée sur tous les shots
4. **Storyboard race avec géographie partagée** — bridge → traffic → park → rooftops → airborne sunset. Same 2 chars, one continuous chase
5. **Seedance anime chaque shot** avec la VS card comme **paired identity reference** (single asset, pas 2 images séparées)
6. **Palette split maintenu partout** — Jaylen always reads blue, Riven always reads purple-red

**3 innovations:**
1. **Paired identity as single asset** — passe les 2 persos comme UNE image de référence. Seedance ne peut pas warper/blender l'un vers l'autre car ils sont locked en contraste
2. **Contrast-based lock** — définition par opposition (style + palette), pas par description isolée. Le modèle a une raison de les garder distincts
3. **Per-character color coding** — palette fixe par perso → tracking visuel à haute vitesse sans confusion

**Use cases:** rivalités, compétitions, duos, intros de show/game avec persos jumelés

**Projets:** african-heroes ⭐⭐⭐ (rivalités historiques: Chaka Zulu vs Dingiswayo, Samori Touré vs Français, Nzinga vs Portugais), CES ⭐⭐ (duos/compétitions)

### #54 — Miniature Human Composite Comedy
**Source:** @kingofdairyque (Simply Ray) — Seedance 2.0 via Pollo AI, 10,6k vues (27 juil. 2026).
- **Scale-as-narrative:** femme 15cm dans monde food réel. Chaque shot = mécanique créative (escalade pancake, surf fraise, patinage beurre).
- **Explicit size lock:** `"Height remains exactly 15 cm"` + same face/outfit/proportions en Strict Requirements.
- **Object recontextualization:** fraise=surfboard, beurre=ice slide, myrtille=adventure ball — chaque objet recontextualisé par la perspective miniature.
- **Contact shadows ×2:** dans style lock ET strict requirements — critique pour l'illusion composite.
- **Freeze-frame ending:** 0.3s freeze avec scale contrast maximal = tableau final.
- **Ultra-strict negative:** `"No CGI, no cartoon, no doll, no figurine"` force photoréalisme absolu.
- Structure: 5-shot timeline 3s, vertical 9:16, SFX per shot.
- CES ⭐⭐⭐ (miniature food comedy viral TikTok/Reels), african-heroes ⭐ (esprit ancestral miniature)

### #55 — Character Sheet Multi-Cut via Hailuo/MiniMax H3 ⭐⭐⭐ CHEAPEST CHARACTER CONSISTENCY
**Source:** @SharaI — Hailuo 2.3 Pro I2V, validated Jul 30, 2026. See `references/hailuo_video_pricing.md` for full pricing.
- **Single reference image → 12+ consistent clips across angles.** Hailuo's I2V with a character sheet produces more consistent facial identity than Seedance across cuts.
- **~4.5× cheaper than Seedance:** 45cr/clip (Hailuo Pro 6s 768p) vs 205cr/clip (Seedance 5s 720p).
- **Pipeline:** Seedream 5.0 Pro generates character sheet (14cr) → Hailuo 2.3 Pro I2V animates each angle (45cr/clip).
- **Batch validated:** 5 sheets + 6 clips = ~441cr, all successful.
- **Use when:** identity preservation is #1 requirement (educational kids series, recurring characters).
- **NOT for:** landscape/decor clips where motion quality > identity (use Seedance instead).

### #56 — Sequential Assembly Choreography (Hailuo H3)
**Source:** @Maercihh — MiniMax H3, extracted Jul 31, 2026.
- Top-down fixed camera, layer-by-layer construction with per-material texture + destination
- Hero shot final beat
- ⭐⭐⭐ pour CES/african-heroes/Cortex Leman product films

### #57 — Emotional Amplification Micro-Techniques
**Source:** @aiwithaly — extracted Jul 31, 2026.
- **A: Time-of-day as narrative arc** — lighting progresses jour→golden hour→nuit with emotion. Not static lighting, it PROGRESSES with the arc.
- **B: Small action → large visual payoff** — intimate gesture (one fox, one lantern) → cosmic result (hundreds of lights). The delta between action and payoff = emotion.
- Injectable into ANY existing pattern (not standalone)
- ⭐⭐ pour african-heroes/CES/Cortex Leman

---

## Pattern #58 — Vehicle-Anchored Action Sequence + Camera-Sequence-as-Narrative + Genre-Mashup-Token
- Characters locked to positions on a moving object ("inside the cab", "rear platform") — anchor travels with action, more robust than static SET LAYOUT
- 8 camera angles without timestamps as implicit storyboard (each angle = 1 beat)
- "Mad Max × Korean action-comedy" token blends two cultural archetypes
- Character sheet posted in reply → Seedance I2V with reference image
- ⭐⭐⭐ pour CES/african-heroes action sequences
- Source: @Just_sharon7, x.com/i/status/2082791809898651724

---

## Pattern #59 — Still Frame Blocking + Shot List Separation
- Generate a static frame with ALL characters positioned → use as I2V reference for subsequent shots
- Prompt text handles ONLY camera + dialogue; spatialization lives in the reference image
- "Everything about who stands where lives in that one image slot"
- Resolves drift in multi-character scenes more cleanly than SET LAYOUT
- MiniMax H3 origin (12-slot Omni Reference) but technique works on Seedance I2V
- ⭐⭐⭐ pour african-heroes/Cortex Leman multi-character scenes
- Source: @Iancu_ai, x.com/i/status/2083022769386553358

---

## Pattern #60 — Structured Section Header Template + Self-Shot UGC (⭐ UNIVERSAL TEMPLATE)
- 7 labeled sections: `Main Subject → Location → Visual Style → Camera Style → Timeline → Audio → Goal`
- Use as BASE STRUCTURE for ALL prompts regardless of model
- "Self-Shot UGC" token: *"filmed by the subject herself"* → handheld shake, autofocus hunting, imperfect framing (authenticity)
- Audio section embedded: SFX + dialogue + "No music" directive (if model supports native audio)
- Seedance 2.5 / Dreamina, 30s, 2560×1440
- Pitfall: text-based negatives ("No commercial elements") less effective than PROHIBITED lists (#14)
- Source: @Strength04_X, x.com/i/status/2083131866580672827

---

## Pattern #61 — In-Video HUD/UI Overlay Generation
- Model generates UI overlays DIRECTLY in the video — no post-production
- Prompt section: `Gameplay UI: Display a realistic [genre] HUD inspired by [references] (without copying exact copyrighted assets). Include: * [element 1] * [element 2]...`
- Clause "fully integrated" = HUD reacts to content (hit markers appear on impact)
- Anti-cinematic companion directive: *"Avoid cinematic camera moves — everything should feel like genuine live footage"*
- Transposable: CES (logo+dish+price overlay), Cortex Leman (product UI mockup), african-heroes (animated maps), LEC (crypto ticker)
- ⚠️ Pitfall: text-heavy HUDs risky (weak text rendering). Prefer graphic overlays (bars, icons, shapes)
- Source: @Just_sharon7, x.com/i/status/2083064417798025721

### #58 — Vehicle-Anchored Action Sequence (Seedance 2.0)
**Source:** Mad Max × Korean comedy clip — extracted Jul 31, 2026.
- **Vehicle as spatial anchor:** characters locked to positions on a mobile object ("inside the cab", "rear platform"). Anchor travels with action — more robust than static SET LAYOUT (#49).
- **Camera sequence as narrative driver:** 8 camera angles WITHOUT explicit timestamps. Each angle = 1 beat. More fluid than #31/#51 which micro-time everything.
- **Genre mashup token:** "Mad Max × Korean action-comedy" — two cultural archetypes blended instead of single style lock.
- Character sheet posted in reply → Seedance I2V with reference image.
- ⭐⭐⭐ pour CES/african-heroes action sequences

### #59 — Still Frame Blocking + Shot List Separation ⭐⭐⭐
**Source:** @Iancu_ai — MiniMax H3 thread, x.com/i/status/2083022769386553358 (Jul 31, 2026).
- **Generate a static frame first** with all characters positioned across the room
- **Use that frame as I2V reference** for the next generation shot
- **Prompt text handles ONLY camera + dialogue** — spatialization lives entirely in the image reference
- *"Everything about who stands where lives in that one image slot. The shot list only has to carry camera and dialogue."*
- Resolves drift in multi-character scenes more cleanly than text-only SET LAYOUT (#49)
- Origin: MiniMax H3 (12 reference slots), but the technique transfers to Seedance I2V
- ⭐⭐⭐ pour african-heroes (battle blocking), CES (kitchen staging), Cortex Leman (event scenes)

### #60 — Structured Section Header Template + Self-Shot UGC ⭐ UNIVERSAL TEMPLATE
**Source:** @Strength04_X — Seedance 2.5 on Dreamina, x.com/i/status/2083131866580672827 (Jul 31, 2026).
**⭐ USE AS BASE STRUCTURE FOR ALL PROMPTS — regardless of model or subject**

**7 labeled sections:**
```
Main Subject: [qui, âge, tenue, trait de personnalité, skin texture]
Location: [où, heure, éléments décoratifs précis, "No commercial elements"]
Visual Style: [rendu, mood, light direction]
Camera Style: [type de caméra + défauts: shake, focus hunting, grain]
Timeline (30 sec):
  00:00–00:03 → [action précise]
  00:03–00:06 → [action + dialogue si applicable]
  ... (10 beats de 3s pour 30s)
Audio: [SFX environnementaux, dialogue noté, "No music"]
Goal: [intention émotionnelle en une phrase]
```

**3 innovations:**
1. **Section headers as concern separation** — each aspect of the shot lives in its own block. No mixing action/style/camera in continuous prose. Model processes each independently then fuses.
2. **Self-Shot UGC token** — *"filmed by the subject herself"* → transforms camera language to handheld shake, autofocus hunting, imperfect framing, natural zoom. Authenticity counter to "too cinematic".
3. **Audio section embedded** — SFX + dialogue in the prompt itself. If Seedance 2.5 supports native audio → eliminates ffmpeg SFX post-prod.

**Seedance 2.5 specs:** 30s/generation (2× Seedance 2.0), Dreamina platform, 2560×1440 natif.
**Pitfall:** "No commercial elements" / "No stabilization" in text work less well than PROHIBITED lists (#14). Reserve negatives for style/mood sections, not failure modes.

---
