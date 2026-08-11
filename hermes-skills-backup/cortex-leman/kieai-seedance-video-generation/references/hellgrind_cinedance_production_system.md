# Hellgrind CINEDANCE Production System (Higgsfield AI, $500K Feature Film)

**Source**: Higgsfield Studio open-sourced their entire production pipeline for "HELL GRIND" — a 95-min AI feature film (Cannes 2026 Marché du Film, $500K budget, 15 people, 14 days generation). All prompts, keyframes, assets, and 3 skill bundles released Aug 4, 2026.

**Files downloaded to** `~/hellgrind-skills/`: `cinedance.md` (33KB), `acting.md` (26KB), `lira.md` (12KB), `brief.md` (5KB). All scanned clean (no injection, no suspicious URLs).

This reference condenses the techniques most actionable for our Seedance 2.0 pipeline.

---

## The 3 Skill Bundles

### CINEDANCE V4 — Seedance 2.0 Prompt Director
A system prompt for Claude that converts scene descriptions into production-ready Seedance 2.0 video prompts. It enforces all rules below automatically. Load it as a system prompt, feed it scene descriptions, get back compliant prompts.

**Key output structure** (order never changes):
1. Header: `EXACT N CHARACTERS — NO DUPLICATES`
2. Character descriptors (word for word from asset registry)
3. Location references (with inheritance ban)
4. STRICT block (frame constants)
5. GEO SPATIAL LAYOUT (floor plan map)
6. Scene context
7. Action beat by beat (max 3 sentences/beat, 8-14 total for 15s)
8. Style Prefix (identical every time)

### ACTING SYSTEM — Living Performance
How to write behavior instead of emotions. See "Acting Techniques" below.

### LIRA — Image Prompt Director
Same concept as CINEDANCE but for image generation. Knows weak points of each image model (Seedream, Nano Banana Pro, GPT Image 2).

---

## Core Techniques (Steal & Apply)

### 1. Asset = Descriptor + Reference Image
- **Descriptor**: Full text description of character/place — pasted word-for-word into EVERY prompt
- **Reference image**: Used as anchor by the model
- Together they prevent identity drift across shots

### 2. The "Headless Character Sheet" Hack
Character sheet = 3 images: close-up face + full body front (**NO HEAD**) + full body back.
- Removing the head from the full-body figure forces the model to take the face ONLY from the close-up
- On wide shots, the model was using the tiny blurry face from the full-body figure — headless fixes this entirely

### 3. State Splitting
Each visual state = separate asset:
- `@roco`, `@roco_wet`, `@roco_blood` — never mix states in one descriptor
- Locations: day/night/rain = 3 separate assets
- Props: multiple versions (full, bloodied, hidden)

### 4. Image Never Runs Through Model Twice
- Point changes (scars, blood, jacket) done via masks on original image
- Every extra full pass destroys texture and drifts colors
- After 2 passes: face turns symmetrical, plastic, lifeless
- Rule: model makes the edit → final assembled with masks on original

### 5. Neutral Boring Character Sheets
- Neutral grey background, flat light, real skin with visible pores
- NO film grain or cinematic lenses baked into the sheet
- Cinema look lives in locations + video prompts, NOT in character sheets
- 3/4 view portrait (face turned slightly) works best

### 6. Stress Test Before Locking
10 generations in different poses and different light. Character must be recognizable 10/10. Test NOT alone — next to other assets, in light of real scenes. If test fails, problem is the description, not the model.

### 7. GEO SPATIAL LAYOUT Block
Floor plan of the place written once per scene, pasted into every shot:
```
GEO SPATIAL LAYOUT (locked across every shot — pure spatial map):
— PLATFORM = raised circular stone disc at the edge of a cliff.
— ALTAR-MONOLITH: at the cliff edge, MID-RIGHT position.
— RITUAL CENTER: CENTER-LEFT, ~3 m from the altar.
— 180° AXIS: camera ALWAYS stays on the corpse-field side.
— BACK-LIGHTING: crimson horizon glow from BEHIND the platform.
```
- Sides only from camera: "frame-left" and "frame-right" (NOT "to the left of the hero")
- Positions from landmarks in meters: "at the altar", "3m away"
- Prevents: teleporting, swapping places, camera jumping axis

### 8. First Second = Wide Shot
1 second at scene start, no lines, no action. Model "photographs" the arrangement and holds it in every following shot. Hack: have someone say "hm" during that second (helps Seedance treat the wide as separate shot). Cost: 1 sec runtime. Saving: hours of reshoots.

### 9. Style Prefix (Copy-Paste Every Prompt)
```
Style: 8K IMAX. Photorealistic — no 3D render, no game engine.
Cinematography: floating immersive camera, natural motivated light, painterly frames.
Lighting: Natural light only — contre-jour backlight, atmospheric haze.
Color: 60:30:10 — dominant/secondary/accent.
Camera: Physical cine lens. 180° shutter motion blur.
Skin: Pore-level realism — vellus hair, asymmetric moles, capillary flush.
Acting: Hollywood — micro-pauses, precise eye-line, catch-lights, visible breath.
Physics: Gravity and inertia respected. No floating props.
Continuity: Characters, props, environment identical across cuts.
Audio: SFX only. No music. No subtitles.
```
Close with: `Photoreal. NON-IP. [aspect ratio]. [duration]s. SFX only. NO CGI. Cinematic.`

### 10. The 10-15 Rule
If a shot doesn't work in 10-15 iterations → STOP. Simplify the shot: split in two, remove an action, change the angle. The problem is not the wording.

---

## Acting Techniques (from ACTING SYSTEM)

### Write Physics, Not Adjectives
- ❌ "sad, angry, shocked" → model improvises, gives shallow result
- ✅ "jaw clenched with rage, cheekbones drawn tight, light exhale through nose"

### INNER Monologue
One line of inner thought per action stretch, marked `INNER (unspoken)`. Model builds micro-expressions from the goal.

### Phased Blinking
`one lazy blink → quick DOUBLE-BLINK → HARD reset-blink` — cheapest sign of a living face.

### Micro-Life Rule
One visible micro-event every 1-2 seconds: breath lifts chest, nostril moves, brow tenses and relaxes. Describe stillness as held tension, never as freeze.

### Positive Form Only
Model ignores negatives. ❌ "does NOT fall on his back" → ✅ "falls on his stomach."

### Dialogue Prompt Format
```
voice+emotion → "line in quotes" → physical action → facial reaction
```
Example: `Tense voice, low register — "We can't stay here" — he steps back, eyes scanning the door, jaw locked.`

Lines ONLY in audio section. Hard block: `everyone speaks ONLY the line in quotes; whoever has no line stays completely silent.`

### Power = Stillness
Most dangerous person moves least and speaks quietest. Scariest lines in everyday tone.

### Two Emotions at Once
One "pure" emotion on close-up looks fake. More alive when two feelings read: "he helps — and hates that he helps."

---

## Post-Production

- Edit ran **in parallel** with generation (not after)
- Cut more aggressively than feels right
- Trim first/last 0.5s of every clip (edges drift)
- Cleanup pass before color: extra fingers, boiling textures, fake text on signs
- Color: unification first (each generation arrives with own grade), then refine
- No voice re-recording: clean Seedance lip-sync directly (noise removal, timbre evening)
- Sound design on continuous ambiences (one shared atmosphere glues shots)

---

## 5 Golden Rules (Compressed)

1. **Assets first.** Do not generate a single shot until every character, location, prop is locked and stress-tested.
2. **Describe everything, every time.** The model has no memory. Descriptor goes into every prompt, word for word.
3. **Change one thing at a time.** One line per iteration, everything into the log.
4. **Give the model less freedom.** A corner instead of a room, an anchor instead of open space, a map instead of hope.
5. **If a shot won't come together — simplify the shot, not the words.** Split in two, remove action, change angle.

---

## Extraction Technique: Intercepting Fetch URLs in React SPAs

The Hellgrind skill files (.md) were behind React buttons with no direct download links. Method:

1. Navigate to the page in browser
2. Inject fetch/XHR interceptor via `browser_console`:
```javascript
window._interceptedUrls = [];
var origFetch = window.fetch;
window.fetch = function() {
    window._interceptedUrls.push({type: 'fetch', url: arguments[0]});
    return origFetch.apply(this, arguments);
};
```
3. Click the download button (via `browser_click` or console `.click()`)
4. Read intercepted URLs: `JSON.stringify(window._interceptedUrls)`
5. Download the file directly via `curl`

Works for any React/Vue SPA that fetches files from CloudFront/S3 on button click.

---

## Security Scan Pattern for Downloaded External Files

Before trusting external .md/.json files, scan for:
- `<script>`, `javascript:`, inline event handlers (`onclick=`, `onerror=`)
- `eval(`, `exec(`, `__import__`, `subprocess`, `os.system`
- `curl | bash`, `base64 -d`, null bytes
- `<iframe>`, `<img onerror>`, `<svg onload>`
- Suspicious URLs (not matching known-safe domains)
- Non-ASCII character percentage (obfuscation indicator)

Script saved inline during session — reproduce with regex scan against DANGER_PATTERNS list.
