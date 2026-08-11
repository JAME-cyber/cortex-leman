# Hybrid Budget-Constrained Video Pipeline

Pattern validated Aug 2026 on african-heroes "Abla Pokou" (vertical 9:16 YouTube Short).

## The problem

A full-video pipeline (9-10 beats × Seedance T2V clips at ~78cr each) costs ~700+ credits. When budget is limited (e.g. 256cr), you can't generate all clips as video.

## The solution — hybrid 3-tier allocation

Split beats into 3 tiers based on dramatic importance:

| Tier | How many beats | Visual treatment | Cost per beat |
|------|---------------|------------------|---------------|
| **Tier 1 — Key dramatic moments** | 3 beats | Seedance T2V video clip (5s, 480p) | ~78cr |
| **Tier 2 — Supporting visuals** | 3-4 beats | Seedream image + Ken Burns (static → zoom/pan) | ~14cr |
| **Tier 3 — Text-driven beats** | 2-3 beats | Caption fullscreen (PIL, no image) | 0cr |

**Total for 10-beat video: ~250cr** (vs ~700cr all-video).

### How to pick Tier 1 beats

Choose the 3 beats where:
- **Movement is the message** (an army advancing, a crowd marching, an action scene)
- **Static images would feel dead** (the whole point of the beat is kinetic energy)
- **Emotional peak** (sacrifice, climax, transformation)

Avoid Tier 1 for:
- Establishing shots (rivers, landscapes — Ken Burns works great)
- Identity/title cards (text-only is cleaner)
- Epilogue/heritage (static image is fine)

### Reuse strategy for Tier 2

You don't need a unique image per beat. Reuse strategically:
- 2 hero images can cover 4-5 beats with different Ken Burns directions (zoom_in vs zoom_out vs pan) and different caption overlays
- The viewer won't notice reuse if captions and audio change

### Caption-only beats (Tier 3)

Use for:
- **Hook/identity**: "Her name was..." (text reveals are dramatic)
- **CTA**: Subscribe/follow cards
- **Transitions**: Short beats that bridge two visual scenes

## Budget tracking

Always check credits BEFORE starting:
```python
from kie_client import KieClient
kc = KieClient()
credits = kc.get_credits()
cost_t1 = n_t1_clips * 78
cost_t2 = n_t2_images * 14
total = cost_t1 + cost_t2
assert total <= credits, f"Need {total}cr, only have {credits}cr"
```

## Validated example — Abla Pokou (Aug 2026)

| Beat | Content | Tier | Source |
|------|---------|------|--------|
| 01 Hook | Woman at river | T2 | Seedream image + Ken Burns |
| 02 Rivière | Sacrifice of water | T2 | Seedream image (reuse) + Ken Burns |
| 03 Identity | "Her name is Abla Pokou" | T3 | Caption fullscreen |
| 04 Context | Ashanti army advancing | **T1** | **Seedance T2V clip** |
| 05 March | The exodus | **T1** | **Seedance T2V clip** |
| 06 Comoé | River in flood | T2 | Seedream image (reuse) + Ken Burns |
| 07 Sacrifice | The sacrifice of her son | **T1** | **Seedance T2V clip** |
| 08 Baouli | Birth of a people | T2 | Seedream image (reuse) + Ken Burns |
| 09 Heritage | Village legacy | T2 | Seedream image + Ken Burns |
| 10 CTA | Subscribe | T3 | Caption fullscreen |

**Result**: 3 video clips (234cr) + 1 new image (14cr) = 248cr total. Video: 126.5s, 51MB, 1080×1920.

## FFmpeg build pipeline structure

```
For each beat:
  Tier 1 → scale 496×864 clip to 1080×1920 + freeze/loop to match TTS duration
  Tier 2 → PIL pre-resize image + ffmpeg crop (Ken Burns) to 1080×1920
  Tier 3 → PIL caption PNG → ffmpeg loop to 1080×1920

Then:
  1. Build each segment (video + caption overlay)
  2. Concat all segments
  3. Mix: TTS audio + BGM (VO=2.5, music=0.12) + subtitles
  4. Append outro
```

See `references/ffmpeg-kenburns-pitfalls.md` for the Ken Burns implementation details.
