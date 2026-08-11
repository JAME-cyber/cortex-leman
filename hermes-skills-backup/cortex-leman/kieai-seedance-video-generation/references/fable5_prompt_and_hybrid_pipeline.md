# Fable 5 Prompt Engineering + Hybrid Real/AI Pipeline

**Validated Aug 3, 2026** — Basketball short "RISE — Le Grind" project.

## 1. Claude Fable 5 via OpenRouter for Hailuo I2V Prompts

Fable 5 (anthropic/claude-fable-5 on OpenRouter) produces **production-grade video prompts** with:
- Forensic identity lock (face + body + clothing)
- Camera direction with specific shot types
- Exhaustive PROHIBITED negative prompt list
- Style tokens (cel-shaded anime, film grain, etc.)

### System Prompt Template (reusable)

```
You are a Seedance/Hailuo video prompt engineer expert. You write production-grade
prompts for AI video generation (Hailuo 2.3 Pro I2V, 6s, 768p, 9:16 vertical).

RULES:
- Triple identity lock: face + body + clothing described with forensic precision
- Cel-shaded anime style: "NOT cartoon NOT Disney NOT Pixar, cel-shaded 3D anime,
  hand-painted textures, heavy dramatic shadows, visible brush strokes, film grain"
- Camera direction with specific shot types
- Lighting and color palette
- Audio atmosphere tags
- Exhaustive PROHIBITED negative prompt list
- Max 1200 characters (Hailuo limit)
- The prompt must describe MOTION and ACTION, not just a static scene
- Output ONLY the raw prompt text, no JSON, no explanation
```

### Calling Pattern

```python
import re, requests

# Read OpenRouter key from .hermes/.env
with open('/home/tars/.hermes/.env') as f:
    for line in f:
        line = line.strip()
        if line.startswith('OPENROUTER_API_KEY=sk-or'):
            key = line.split('=',1)[1]
            break

r = requests.post("https://openrouter.ai/api/v1/chat/completions",
    json={
        "model": "anthropic/claude-fable-5",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": scene_description}
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    },
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hermes.local",
        "X-Title": "Video Prompt Gen"
    },
    timeout=60)
prompt = r.json()["choices"][0]["message"]["content"]
```

### Key Insight

Fable 5 naturally produces the right structure (identity → motion → camera → lighting → style → audio → PROHIBITED) in ~1000-1400 chars — within Hailuo's 1500 char limit. No manual condensing needed. Output quality: QA 7-9/10 on generated clips.

## 2. Hybrid Real Footage + AI Anime Pipeline

**Problem**: AI-generated anime clips clash stylistically with real footage when intercut naively.

**Solution**: Position the AI clips as **narrative devices** — flash-forward dreams, aspirations, future self — rather than pretending they're the same reality.

### Arc Structure (validated, QA 8/10)

| Beat | Source | Role | Duration |
|------|--------|------|----------|
| Hook | Poster anime (zoom-in) | Visual impact | 3s |
| Grind | Real footage cuts (1.5s each) | Authentic effort | 9s |
| Dream | AI anime clips (Hailuo I2V) | Aspiration rising | 10s |
| Payoff | AI anime climax | The reward | 5s |
| Outro | Text/title card | Call to action | 5s |

### Why It Works

- Real footage carries **emotional authenticity** (real sweat, real effort)
- AI clips carry **visual spectacle** (impossible camera moves, ideal lighting)
- The contrast IS the story: "this is where I am → this is where I'm going"

### Implementation Notes

1. Extract 1.5s segments from real footage at varied timestamps (keeps it dynamic)
2. Generate AI clips from a **single reference poster** for identity consistency
3. Alternate real/AI cuts in the middle section for rhythm
4. Use the same VO track across both (unifies the audio space)

## 3. Contact Sheet QA via OpenRouter Gemini (Reusable Script)

Quick QA for generated video clips without manual viewing:

```python
import base64, re, requests
from PIL import Image
import io

# Extract mid-frame from each clip
# ffmpeg -y -ss 2.5 -i clip.mp4 -frames:v 1 frame.jpg

# Make contact sheet (2-3 rows × cols)
frames = [Image.open(f"frame_{i}.jpg") for i in range(1, N+1)]
w, h = 270, 480
cols, rows = 3, (N + 2) // 3
sheet = Image.new("RGB", (w*cols, h*rows), (0,0,0))
for i, f in enumerate(frames):
    f.thumbnail((w, h))
    sheet.paste(f, ((i%cols)*w, (i//cols)*h))
sheet.save("contact.jpg", quality=80)

# Send to Gemini 2.5 Flash via OpenRouter
img = sheet.copy()
img.thumbnail((640, 640))
buf = io.BytesIO()
img.save(buf, format="JPEG", quality=75)
b64 = base64.b64encode(buf.getvalue()).decode()

msg = {
    "model": "google/gemini-2.5-flash",
    "messages": [{"role": "user", "content": [
        {"type": "text", "text": "Rate each clip 1-10 on: style, consistency, dynamism. One line each."},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
    ]}],
    "max_tokens": 500
}
r = requests.post("https://openrouter.ai/api/v1/chat/completions",
    json=msg,
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    timeout=30)
print(r.json()["choices"][0]["message"]["content"])
```

**Key**: Use `max_tokens: 500` for QA scoring (short answers). Use `max_tokens: 2000` for detailed frame analysis. Thumbnail to 640px before base64 encoding to stay under API limits.

## 4. ffmpeg Audio Mixing Pitfall: `-shortest` + amix

**Pitfall**: When mixing a short VO track (~14s) with longer ambient audio (~30s) using `amix`, adding `-shortest` to the final merge cuts the ENTIRE video to the shorter audio stream.

**Wrong**:
```
ffmpeg -i video.mp4 -i amix.wav -shortest -c:v libx264 out.mp4
```
Result: video truncated to 14s instead of 32s.

**Correct**: Use `duration=longest` on the amix filter, and DON'T use `-shortest` on the final merge:
```
-filter_complex "[0:a]volume=2.0[vo];[1:a]volume=0.15,atrim=duration=30[amb];[vo][amb]amix=inputs=2:duration=longest:dropout_transition=0[a]"
```
Then merge WITHOUT `-shortest`:
```
ffmpeg -i video.mp4 -i amix.wav -map 0:v -map [a] -c:v libx264 out.mp4
```

## 5. Reference Image Upload for Hailuo I2V

To use a local image as `image_url` for Hailuo, upload to a public host:

```bash
# catbox.moe — free, no account, instant
curl -s -F "reqtype=fileupload" -F "fileToUpload=@image.png" https://catbox.moe/user/api.php
# Returns: https://files.catbox.moe/xxxxx.png
```

Works for PNG up to ~8MB. URL is permanent and accessible by kie.ai servers.

## 6. OpenRouter API Key Location

**Key is in `/home/tars/.hermes/.env`**, NOT `.bashrc`.

```python
import os
with open('/home/tars/.hermes/.env') as f:
    for line in f:
        line = line.strip()
        if line.startswith('OPENROUTER_API_KEY=sk-or'):
            os.environ['OPENROUTER_API_KEY'] = line.split('=',1)[1]
            break
```

Verify Fable 5 availability: `GET https://openrouter.ai/api/v1/models` → search for `anthropic/claude-fable-5`.

## 7. kie.ai Does NOT Support Video-to-Video / Style Transfer

**Verified Aug 3, 2026** via exhaustive scan of kie.ai site menu + docs.kie.ai + API endpoint probing.

All video models on kie.ai are **T2V (text-to-video) or I2V (image-to-video) only**:

| Family | Models | V2V? |
|--------|--------|------|
| Kling | 2.1, 2.5, 2.6, 3.0, 3 Turbo | T2V + I2V |
| Hailuo | 2.3 | T2V + I2V |
| Seedance | 1.5 Pro, 2.0, 2.5 | T2V + I2V |
| Veo | 3.1 | T2V + I2V |
| Wan | 2.2-2.7 | T2V + I2V |
| Others | Runway, PixVerse, Grok Imagine, MiniMax | None |

**For video-to-anime style transfer** (the "Moorhie/Moorphie" TikTok effect — real footage → anime frame-by-frame), kie.ai has NO equivalent. Options:
- **DomoAI** — leader in V2V style transfer (~$15/mo, API available)
- **Kaiber** — similar (~$5/mo)

Do NOT waste time scanning kie.ai for V2V endpoints in future sessions — it doesn't exist. The correct approach for anime clips remains: **Fable 5 prompt → Hailuo I2V from reference poster**.

For the **full short film build pipeline** (ffmpeg concat, subtitle specs, audio mixing, cost breakdown, PITFALL #54 on polling), see `references/hybrid_short_pipeline.md`.
