# OpenMontage — Full Video Production Alternative

When the lightweight Edge TTS + FFmpeg pipeline isn't enough (need multi-scene, AI imagery, music, real footage), OpenMontage is the upgrade path.

## What It Is

OpenMontage (github.com/calesthio/OpenMontage) — 32k+ stars, AGPL-3.0, Python + Remotion.
Agent-first video production: describe what you want → agent handles research, scripting, assets, voice, music, editing, rendering.

Installed at `/home/tars/OpenMontage/` (cloned 2026-07-04).

## When to Use OpenMontage vs Lightweight Pipeline

| Need | Use |
|------|-----|
| Quick 60-90s brief with TTS + text overlays | **Edge TTS pipeline** (this skill's `scripts/generate_video.py`) |
| Multi-scene explainer with AI-generated visuals | **OpenMontage** |
| Cinematic trailer with music | **OpenMontage** (needs API keys: FAL, Suno, etc.) |
| Ad variants for Darkom-Debarras | **OpenMontage** (Clip Factory pipeline) |
| Zero-cost video with offline TTS | **OpenMontage** (Piper TTS + Remotion, $0) |

## Zero-Key Path (No API Keys Needed)

```bash
cd /home/tars/OpenMontage

# List available zero-key demos
.venv/bin/python render_demo.py --list

# Render a demo (Remotion only, Piper TTS, no cloud calls)
.venv/bin/python render_demo.py focusflow-pitch
```

Output: `projects/demos/renders/{name}.mp4`

## Low-RAM Workaround (CRITICAL)

**Problem:** On machines with <4GB RAM, Remotion's headless Chrome gets OOM-killed mid-render (~frame 234/675).

**Fix:** Render at half resolution with single-threaded concurrency:

```bash
cd /home/tars/OpenMontage/remotion-composer

npx --yes remotion render src/index.tsx Explainer \
  ../projects/demos/renders/output.mp4 \
  --props public/demo-props/{demo}.json \
  --codec h264 \
  --concurrency 1 \
  --scale 0.5
```

This produces 960×540 (half of 1920×1080) — sufficient for web content.
Render time: ~5 min for 22s video on 3.8GB RAM machine.

**If scale 0.5 still crashes:** try `--scale 0.25` (480×270, preview quality).

## Full Production (With API Keys)

Add keys to `/home/tars/OpenMontage/.env`:

```bash
FAL_KEY=...          # FLUX images + Kling/Veo video
OPENAI_API_KEY=...   # GPT Image 2 + OpenAI TTS
SUNO_API_KEY=...     # Music generation
```

Then instruct the agent (via Hermes/AI coding assistant) with a natural language prompt.

## Pipelines Available

| Pipeline | Use Case | Cost Range |
|----------|----------|------------|
| Animated Explainer | Educational/marketing content | $0.15-$1 |
| Cinematic | Trailers, brand films | $1-$3 |
| Clip Factory | Repurpose long content → shorts | Varies |
| Documentary Montage | Real footage from free archives | $0 |
| Talking Head | Presentations, vlogs | $0+ |
| Localization & Dub | Multi-language distribution | $0.50+ |

## Costs Observed (2026-07-04)

- Zero-key demo (22.5s, 960×540): **$0**, 1.8 MB
- FLUX image-based animation (12 images): **$0.15/video**
- Product ad (OpenAI only): **$0.69**
- Full cinematic (Veo + Suno): **~$3**

## Constraints on This Machine

- **No GPU**: local video gen (wan2.1, hunyuan) unavailable. Cloud APIs only.
- **3.8GB RAM**: must use `--scale 0.5 --concurrency 1`. Full-res render crashes.
- **Remotion bundle cached**: first render downloads Chrome Headless Shell (~92MB), subsequent renders skip this.
- **AGPL-3.0 license**: safe for internal use and client deliverables. NOT safe for SaaS redistribution without open-sourcing modifications.

## Full Agent Production Flow

OpenMontage is designed to be driven by an AI coding assistant (Claude Code, Cursor, Hermes). The agent reads pipeline manifests (YAML), stage director skills (Markdown), and calls Python tools.

To use with Hermes:
1. Read `/home/tars/OpenMontage/AGENT_GUIDE.md` for routing rules
2. Read `/home/tars/OpenMontage/PROJECT_CONTEXT.md` for project structure
3. Pick a pipeline based on the video type needed
4. The agent executes: research → proposal → script → scene_plan → assets → edit → compose
5. Creative decision points pause for human approval
