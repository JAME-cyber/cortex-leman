# Seedance Directing Engine & Model Mechanics

**Source**: [Emily2040/seedance-2.0](https://github.com/Emily2040/seedance-2.0) — v6.7.0, 5.7k⭐, MIT
**Author**: @IamEmily2050, viral on Douyin
**Scope**: Seedance 2.0 (NOT 2.5) — but the craft principles apply to any model
**Accessed**: Aug 1, 2026

## Core Principle

> "Direct the scene, don't decorate it."

Don't ask for "cinematic" — decide what the scene DOES to the audience, then make every craft choice serve that one intention.

**Slop**: `epic cinematic shot of a woman reading a letter, emotional, beautiful lighting`

**Directed**: `A woman at a kitchen table reads the letter twice, then her hands lower it and go still. Camera: medium close-up at eye level, a slow push-in that settles when her hands stop. Soft window light keeps her face plain. Sound: room tone, one chair scrape, near-silence.`

## The Director's Read (5 questions)

1. **Function** — introduce, deepen, turn, or pay off?
2. **The turn** — the value shift (safe→threatened, hope→despair, stranger→ally)
3. **POV** — whose experience? Where does the audience's body stand?
4. **Power** — who has it, who wants it, where does it move?
5. **Subtext** — what is true but unsaid?

## Coherence Principle

One intention per scene. Every instrument plays the same note:

| Instrument | Carries |
|---|---|
| Shot size | Distance = intimacy or judgment |
| Angle/height | Power and sympathy |
| Lens feel | Psychological space |
| Camera movement | Audience's impulse (push-in=realization, pull-back=abandon) |
| Lighting | Emotional exposure |
| Blocking | Relationship in space |
| Performance | Truth of the moment (one legible gesture) |
| Sound | What the ear feels |
| Cut/duration | Breath and pressure |

## 10 Scene-Types

| Type | Coherent setup | Slop to refuse |
|---|---|---|
| Intimate dialogue | MCU, eye-level, long lens, soft key, sparse sound | Roaming camera, big coverage |
| Confrontation | Opposed angles, height=status, warm/cool split | Symmetrical neutrality |
| Reveal | Withhold then disclose, camera discovers with subject | Everything at once |
| Decision | Push-in to isolate, world quiets, one gesture commits | Dialogue doing body's work |
| Arrival | Wide, motivated env light, ambient sound | Pretty vista, no subject |
| Pursuit | Tracking/handheld, screen-direction, contrast, sound thickens | Stacked moves = chaos |
| Transformation | Locked camera, light tracks change, one cause | Spectacle without anchor |
| Comedic beat | Locked frame, clean geography, deadpan hold | Busy camera on timing |
| Emotional low | Distance+stillness, cool soft light, negative space | Score-driven sentiment |
| Product hero | Controlled move context→detail, motivated hero light | "Dynamic" drifting camera |

## 6 Director Voices

| Voice | Camera | Light | Best for |
|---|---|---|---|
| Observational naturalist | Invisible, still/subtle | Available/motivated, soft | Grounded drama, doc |
| Composed classicist | Deliberate, balanced | Sculpted, clean | Prestige, premium ad |
| Kinetic visceral | Handheld, tracking | Hard, high contrast | Action, sport |
| Expressive stylist | Designed, bold | Dramatic, pushed | Music video, fashion |
| Intimate minimalist | Close lenses, small moves | Single soft source | Personal, lonely |
| Graphic formalist | Locked/geometric | Hard, shaped | Brand, deadpan comedy |

Choose ONE voice at project start, apply to every clip. Deviation = deliberate turn signal.

## 8 Model Mechanics

| # | Mechanism | Practical consequence |
|---|---|---|
| 1 | Attention = budget | Word order = priority. Slop wastes budget. Subject+action FIRST. |
| 2 | Pull toward familiar | Name dense visual clusters (film noir) > adjectives (beautiful). Rare combos = instability. |
| 3 | No NOT | "No blood" summons blood. Describe what IS there. Negation only in constraint slots. |
| 4 | Time = trajectory | One physical cause with consequences > 5 stage directions. Model smooths unmotivated changes. |
| 5 | Errors compound | Identity drifts with clip length + chained continuations. Re-anchor with ORIGINAL refs, not outputs. ~4-5 gens max before reset. |
| 6 | References > text | Don't re-describe a reference image. Prompt only what the image can't show: change over time, camera, sound. |
| 7 | Detail ∝ screen area | Face at 2% of frame = 2% representation. Important details = own shot. Text = post. |
| 8 | Audio+video = joint | Sound generated WITH picture. Name sounds per shot = sync targets. Dialogue = stable face + short line. |

### Diagnosis table

| Symptom | Mechanism | Lever |
|---|---|---|
| Generic despite long prompt | 1 (attention diluted) | Cut slop, priorities first |
| Style flicker | 2 (cluster hopping) | Repeat exact anchor phrase every shot |
| Excluded thing appears | 3 (negation) | Describe positive replacement |
| Action skipped/mushy | 4 (no trajectory) | One cause, visible consequences, endpoint |
| Identity decays | 5 (compounding) | Shorter clip, re-anchor original ref |
| Ref fights prompt | 6 (conflicting) | Delete re-description, state non-transfer |
| Small detail breaks | 7 (capacity) | Enlarge in frame or own shot |
| Lips/sound desync | 8 (joint overloaded) | Lock face, shorten line, name sound |

## Retake Protocol

### 5 verdicts
| Verdict | When | Action |
|---|---|---|
| Keep | Primary spend delivered, nothing fatal | Lock, log, move on |
| Fix in post | Flaw in post domain (color, text, sound) | Never burn takes on post-fixable |
| Edit | Composition OK, one layer wrong | Preserve take, change layer |
| Re-roll | Prompt right, unlucky sample | Same prompt, new seed. Max 2-3 |
| Rewrite | Same flaw 2+ takes = systematic | Diagnose by mechanism, change prompt |

### One-variable rule
Change ONE thing per retake: one prompt clause OR seed OR mode OR reference.

### Attempt budget
Set BEFORE take 1: 5 standard / 10 fast. At half-budget with no progress → change strategy.

### Shot log
```
Take N · changed: [variable] · seed: [same/new] · verdict: [keep/post/edit/re-roll/rewrite] · evidence: [phrase]
```
Two takes same flaw = automatic rewrite.

### Cost awareness
- Draft cheap (fast tier, short durations), lock expensive (standard, full length)
- Ten 4s drafts answer more questions than one failed 15s take

## Validated Application: Pattern #68 (Aug 1, 2026)

@IamEmily2050 applied this Directing Engine to a **MiniMax H3** K-drama test (15s, 4 shots, 3 lines of Korean dialogue). The result validated 6 novel techniques not present in any prior pattern:

1. **Anatomical anti-mirror spec** — "anatomical right ear only", "keys handled only by anatomical right hand", "Never mirror these details" — prevents L/R inversion between shots
2. **Dialogue timing windows** — each line has a precise time window (3.7-4.6s, 7.9-9.6s) with micro-actions filling the gaps (swallow, breath, listening)
3. **Micro-beat acting** — emotion described as physical gesture, not named: "stopped breath, released jaw, eyes focusing on nothing" instead of "she looks devastated"
4. **Subtext → physical action mapping** — each line explained in dramatic psychology (WHY) then translated to physical gesture (HOW)
5. **Anti-melodrama negative stack** — the most aggressive negative list to date: no crying, no tears, no gasping, no knitted brows, no clenched fists — forces underplayed naturalism
6. **Production sound engineering** — room tone layers named individually (fridge, HVAC, traffic), boom+lav perspective, -6 dBFS, no hard-gate

**Cross-ref**: Pattern #68 in `seedance_patterns_library.md`. The 12-section prompt architecture is: REFERENCE USE → IDENTITY LOCKS → SCENE → DIALOGUE → SCREEN GEOGRAPHY → SHOT LIST → ACTING → LIGHT → CAMERA → PRODUCTION SOUND → NEGATIVES.
