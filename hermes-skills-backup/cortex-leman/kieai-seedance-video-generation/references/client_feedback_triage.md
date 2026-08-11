# Client Feedback Triage — 3-Level Classification for Video Production

> When a client sends detailed per-video feedback (like Linda's CES review), classify each item
> into one of three execution tiers BEFORE starting any work. This determines the sequence,
> credit consumption, and whether new AI generation is needed.

## The 3 levels

### Level 1 — Code-only (immediate, 0 credits)
Changes that require **only** editing the build script (Python/ffmpeg pipeline) and re-rendering.

**Examples:**
- Text corrections (typos, "à Petit-Lancy" → "au Petit-Lancy")
- Removing a duplicate video from the deliverable set
- Shortening/trimming an existing clip (removing a loop, cutting a segment)
- Adjusting subtitle text
- Swapping background music file
- Reordering existing clips in a video
- Merging two videos into one (new config combining existing clips)
- Improving CTA text legibility (font size, color, position)

**Action:** Edit the build config directly, re-render, deliver. No credits consumed.

### Level 2 — Clip regeneration (credits required)
Changes that require **new AI-generated clips** because the existing clip cannot be fixed via code.

**Examples:**
- "The henna artist should be a Somali woman with a headscarf" (ethnicity/apparel change)
- "Show the full process: plant → powder → paste → design" (new content sequence)
- "Reduce the number of children" when the clip has too many (re-generation needed)
- "Add kora and other instruments" (new visual content)
- "Show adult monitors clearly" (new content)
- "Decor should be neutral, not one region of Africa" (scene redesign)

**Action:**
1. Write new prompts via LLM delegation (see `references/llm_prompt_delegation.md`)
2. Classify by model: identity-critical → Hailuo Pro, decor/landscape → Seedance
3. Budget per clip (~205cr Seedance 720p, ~45cr Hailuo Pro, ~59cr Seedream→Hailuo pipeline)
4. Submit batch, poll, download
5. Vision QA each clip before rebuild (see `scripts/visual_qa_gpt.py` or OmniRoute)
6. Update build config to point at new clips, re-render

### Level 3 — Blocked (client action required)
Changes that cannot be done without client-supplied materials or decisions.

**Examples:**
- "Use the same typography as the visual I will send you" → blocked until visual arrives
- "I want a different background music" → blocked unless client specifies a style or provides a file
- "Adjust the poster images to match Cameroon's style" → needs visual reference

**Action:** Document in feedback file, inform client, do NOT block Level 1/2 work on it.

## Execution order

```
Level 1 (code-only) FIRST → immediate wins, no cost
Level 2 (clip regen) SECOND → batch all prompts, submit together
Level 3 (blocked) THIRD → log and escalate to client
```

## Feedback file structure

Save the complete client feedback in the project research dir before starting:

```
research/linda_feedback_v2.md  (or <client>_feedback_v<round>.md)
```

Structure per video/section:
- What the client liked (preserve)
- What needs changing
- Classification: [CODE] / [REGEN] / [BLOCKED]
- Status: pending → in_progress → done

## Validated example (CES v2, Aug 1, 2026)

Linda's 12-section feedback for "Éveil aux Saveurs Africaines":

| Feedback section | Level | Action taken |
|-----------------|-------|-------------|
| "au Petit-Lancy" typo | CODE | Already fixed in all CTAs |
| V4 is duplicate, remove it | CODE | Removed from deliverable set |
| Merge V2+V3 into one video | CODE | New `activites` config, existing clips |
| T3 Nil: shorten seq2, remove plant loop | CODE | Trimmed clips, swapped plant→henna transition |
| Visio: boy with flag + orphanage | REGEN | New v2_visio clip generated |
| Henné: Somali woman + process | REGEN | New v2_henna clip generated |
| Music: fewer children + kora | REGEN | New v2_music clip generated |
| Rhône: safety vests + monitors | REGEN | New v2_rhone clip generated |
| Contes: Somali storyteller + cushions | REGEN | New v2_contes clip generated |
| Street food: neutral decor + diverse | REGEN | New v2_street_food clip generated |
| Typo/graphic from reference visual | BLOCKED | Waiting for Linda to send visual |
| New background music | BLOCKED → resolved | Afroswing track already in place |

**Result:** 4 code-only fixes + 6 clip regenerations (6×205cr = 1230cr ≈ $6.15) + 2 blocked items
logged. All done in a single session without mid-stream blocking.

## Credit budget for typical feedback round

| Scenario | Clips | Credits | USD |
|----------|-------|---------|-----|
| Minor feedback (code-only) | 0 | 0 | $0 |
| 3 clips regenerated (Seedance) | 3 | 615 | $3.08 |
| 6 clips regenerated (Seedance) | 6 | 1230 | $6.15 |
| Full series overhaul (8+ clips) | 8 | 1640+ | $8.20+ |

**Always check credits before submitting.** If a batch fails mid-way (credits exhausted), the
remaining clips need a separate re-submission after recharge — the script should handle partial
success gracefully and log which clips succeeded vs. failed.
