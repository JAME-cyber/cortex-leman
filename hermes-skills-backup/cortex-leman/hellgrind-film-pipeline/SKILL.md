---
name: hellgrind-film-pipeline
description: Use when writing cinematic AI video prompts.
---

# Hell Grind Film Pipeline

Production-ready system extracted from Higgsfield's $500K AI feature film "HELL GRIND"
(95 min, Cannes 2026 Marché du Film, 100% AI-generated).

Source: [higgsfield.ai/@higgsfield.studio/projects/hell-grind](https://higgsfield.ai/@higgsfield.studio/projects/hell-grind)

## When to use

- Writing Seedance 2.0 video prompts that need to work on first generation
- Building character sheets with identity consistency across shots
- Writing living character performances (behavior, not emotions)
- Managing spatial continuity across multi-shot scenes
- Any cinematic AI video generation task (commercials, shorts, features)

## The 5 Golden Rules

1. **Assets first.** Do not generate a single shot until every character, location and prop is locked and stress-tested.
2. **Describe everything, every time.** The model has no memory. The descriptor goes into every prompt, word for word.
3. **Change one thing at a time.** One line per iteration, everything into the log.
4. **Give the model less freedom.** A corner instead of a room, an anchor instead of open space.
5. **If a shot won't come together — simplify the shot, not the words.** Split it, remove an action, change the angle.

## 3 Sub-Skills (load from references/)

### 1. CINEDANCE V4 — Video Prompt Director (33KB)
File: `references/cinedance-v4.md`

4-D methodology: **Deconstruct → Diagnose → Develop → Deliver**
- Internal reasoning agent that converts scene input → production-ready Seedance prompt
- Prompt skeleton order: Header → Characters → Locations → STRICT block → GEO LAYOUT → Scene context → Action beats → Style Prefix
- Includes: spatial blocking, optics selection, physics validation, reference control, continuity QA

### 2. Acting System — Living Performance (25KB)
File: `references/hellgrind-acting-system.md`

Core axiom: **Acting is BEHAVIOR under pressure, not display of emotion.**

5 Pillars: Objective → Obstacle & Stakes → Tactics → Beats → Subtext

Key techniques:
- Write physics, not adjectives (tremble, jaw clenched, not "angry")
- INNER (unspoken) monologue lines
- Phased blinking (lazy → DOUBLE-BLINK → reset-blink)
- Micro-life rule: 1 visible event per 1-2 seconds
- Positive form only (model ignores negatives)
- Dialogue format: voice+emotion → "line" → physical action → facial reaction

### 3. LIRA — Image Prompt Optimizer (12KB)
File: `references/lira-image-prompts.md`

4-D methodology for images: **Deconstruct → Diagnose → Develop → Deliver**

Model-specific knowledge:
- **Soul Cinema**: best skin texture, creative (multiple face variants per prompt)
- **Nano Banana Pro**: point edits (scars, blood, jacket) via masks on original
- **Seedream 4.5**: texture/slop cleanup
- **GPT Image 2**: text in frame, props, reverse angles of locations

## Key Techniques Summary

### Character Sheets (Headless Hack)
- Close-up face + full body front (**NO HEAD**) + full body back
- Neutral grey background, flat light, real skin with visible pores
- 3/4 view portrait (not straight-on)
- Why headless: model took face from tiny/blurry full-body on wide shots

### The "No Double Pass" Rule
- An image never runs through a model twice in full
- Point changes via masks: model edits the changed part → composite on original
- After 2 passes: face turns symmetrical, plastic, lifeless

### GEO SPATIAL LAYOUT
```
GEO SPATIAL LAYOUT (locked across every shot):
— LANDMARK: raised circular platform at CENTER.
— SECOND OBJECT: at the edge, MID-RIGHT.
— 180° AXIS: camera ALWAYS stays on the field side — NEVER crosses.
— BACK-LIGHTING: glow from BEHIND, rim-lighting silhouettes.
```
- Positions from landmarks in meters: "at the altar", "3m away"
- Sides from camera only: "frame-left" and "frame-right"

### First Second Wide Shot
- 1 sec of wide at scene start: model "photographs" the arrangement
- Hack: someone says "hm" during that second
- Prevents character swapping/teleporting

### Style Prefix (paste at end of every prompt)
```
Style: 8K IMAX. Photorealistic — no 3D render, no game engine.
Cinematography: floating immersive camera; natural motivated light.
Lighting: Natural light only — contre-jour, atmospheric haze.
Color: 60:30:10 — dominant / secondary / accent.
Camera: Physical cine lens. 180° shutter motion blur.
Skin: Pore-level realism — vellus hair, asymmetric moles, capillary flush.
Acting: Hollywood — micro-pauses, precise eye-line, catch-lights, visible breath.
Physics: Gravity and inertia respected — mass has real weight.
Continuity: Characters, props, environment identical across cuts.
Technical: 24fps smooth motion. 8K detail. No jitter.
Audio: Environmental SFX only. No music. No subtitles.
```
+ Technical tags: `Photoreal. NON-IP. [aspect ratio]. [duration]s. SFX only. NO CGI. Cinematic.`

### State Splitting
- Wet/wounded/changed = separate assets (@hero, @hero_wet, @hero_blood)
- Locations: day/night/rain = 3 separate assets
- Props: full/bloodied/hidden versions

### The 10-15 Rule
If a shot doesn't work after 10-15 iterations: **stop**. Simplify the shot, not the words.

## Workflow: How to use

1. **Pre-production**: Build all character sheets + locations + props → stress test (10 gens each)
2. **Lock voice**: register, tempo, accent, manner — one prompt per character, never changes
3. **Write shotlist**: each shot gets full prompt with skeleton order
4. **Generate**: scene by scene, one line change per iteration, log everything
5. **Edit in parallel**: cut aggressively, trim 0.5s from start/end of every clip
6. **Cleanup pass**: fix fingers, boiling textures, fake text — before color
7. **Color**: unify first (every gen has built-in grade), then refine

## Pitfalls

- **NEVER** bake cinematic look (grain, lenses) into character sheets — kills light reactivity
- **NEVER** overload a beat (>3 sentences/beat = model smears it)
- **NEVER** mix character states in one prompt
- **NEVER** use emotion words ("sad", "angry") — use muscle physics instead
- **NEVER** write negative actions ("does NOT fall") — model ignores or does opposite
- **NEVER** run an image through a model twice in full — use masks
- Bilingual prompt (EN first, Chinese below) = more stable on difficult shots
