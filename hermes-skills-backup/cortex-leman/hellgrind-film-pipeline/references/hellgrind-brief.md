# HELL GRIND — Production Brief (Higgsfield AI, $500K, 95min, Cannes 2026)

## Logline
A street thief walks into a simple job — lifting a nameless artifact from a museum. But the artifact wakes Hell, and demons take the girl he loves. The price of getting her back is three ancient artifacts. Each one is paid for in blood.

## Numbers
- 95-minute feature film
- 15 people
- Budget under $500K
- 14 days of generation
- Screened at Cannes 2026 Marché du Film
- Every frame generated. No cameras, no actors, no sets.

## Stack
- Video & speech: Seedance 2.0
- Faces & locations: Soul Cinema
- Image edits: Nano Banana Pro and Seedream 4.5
- Text in frame, props, reverse angles: GPT Image 2

## Key Rules Extracted

### 1. Assets First
- Asset = text descriptor + reference image
- Character sheet: close-up face + full body front (headless) + full body back
- Neutral grey background, flat light, real skin with pores
- 3/4 view portrait works best
- Stress test: 10 generations in different poses/light, must be recognizable 10/10
- Voice locked in pre-production: register, tempo, accent, manner — never changes
- Behavior profile: one paragraph per hero — movement, hands, habits, eyes, breakdown mode

### 2. State Splitting
- @roco, @roco_wet, @roco_blood — separate assets per state
- Locations: day, night, rain = 3 assets
- Props: multiple versions for different shots

### 3. The "No Head" Hack
- Full-body figure on character sheet has NO head
- Prevents model from using tiny/blurry face on wide shots
- Forces model to take face from close-up only

### 4. Image Never Runs Through Model Twice
- Point changes (scars, blood, jacket) via masks on original
- Every extra pass destroys texture, drifts colors
- After 2 passes: face turns symmetrical, plastic, lifeless

### 5. GEO SPATIAL LAYOUT
- Floor plan of the place: landmarks, left/right, camera position
- Written once per scene, pasted into every shot
- Prevents teleporting, swapping places, camera jumping
- Positions from landmarks in meters: "at the altar", "3m away"
- Sides only from camera: "frame-left" and "frame-right"
- Never cross the 180° axis line

### 6. First Second = Wide Shot
- 1 sec at start: model "photographs" the arrangement
- Hack: someone says "hm" during that second
- Cost: 1 sec runtime. Saving: hours of reshoots.

### 7. Write Behavior, Not Feelings
- Goal + obstacle + changing strategy = living scene
- Physics not adjectives: tremble, jaw clenched, cheekbones tight
- INNER (unspoken) monologue lines
- Phased blinking: lazy → DOUBLE-BLINK → reset-blink
- Micro-life rule: 1 visible event per 1-2 seconds
- Positive form only (model ignores negatives)

### 8. Dialogue Prompt Format
voice+emotion → "line" → physical action → facial reaction
- Lines ONLY in audio section
- Hard block: everyone speaks ONLY quoted line, others silent
- Feed tail of previous line for lip/rhythm continuity

### 9. Prompt Skeleton (order never changes)
1. Header: "EXACT N CHARACTERS — NO DUPLICATES"
2. Character descriptions (word for word)
3. Location references
4. STRICT block (frame constants)
5. GEO SPATIAL LAYOUT
6. Scene context
7. Action beat by beat
8. Style Prefix (same every time)

### 10. Style Prefix
Style: 8K IMAX. Photorealistic — no 3D render, no game engine.
Lighting: Natural light only — contre-jour, atmospheric haze.
Color: 60:30:10 — dominant/secondary/accent.
Camera: Physical cine lens. 180° shutter motion blur.
Skin: Pore-level realism.
Acting: Hollywood — micro-pauses, precise eye-line, catch-lights, visible breath.
Physics: Gravity and inertia respected.
Continuity: Characters, props, environment identical across cuts.
Audio: SFX only. No music. No subtitles.

### 11. The 10-15 Rule
- If a shot doesn't work in 10-15 iterations: stop
- Simplify the shot: split in two, remove action, change angle
- Problem is not the wording, it's the shot

### 12. Post-Production
- Edit ran in parallel with generation
- Cut more aggressively than feels right
- Trim first/last 0.5s of every clip (edges drift)
- Cleanup pass before color: extra fingers, boiling textures, fake text
- Color: unification first, then refine (look baked into location assets)
- No voice re-recording: clean Seedance lip-sync directly
- Sound design on continuous ambiences

## Five Compressed Rules
1. Assets first. Do not generate a single shot until everything is locked.
2. Describe everything, every time. The model has no memory.
3. Change one thing at a time. One line per iteration.
4. Give the model less freedom. Corner not room, anchor not space.
5. If a shot won't come together — simplify the shot, not the words.
