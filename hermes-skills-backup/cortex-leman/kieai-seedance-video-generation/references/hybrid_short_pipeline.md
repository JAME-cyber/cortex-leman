# Hybrid Real Footage + AI Anime Short Film Pipeline

**Validated Aug 3, 2026** on basketball short "RISE — Le Grind" (V1→V4).

## When to Use

When a user provides REAL footage (training videos, personal clips) that doesn't match the desired visual style (anime, cinematic, etc.). The stylistic clash between real footage and AI clips is used as a NARRATIVE FEATURE, not a defect.

## Narrative Structure

| Act | Source | Role |
|-----|--------|------|
| 1. Hook | AI poster (zoom-in) | Establishes style + character identity |
| 2. Reality/Grind | Real footage (fast cuts) | Authentic effort, the work nobody sees |
| 3. Dream/Future | AI clips (Hailuo I2V from poster) | The aspiration — what the grind leads to |
| 4. Payoff | AI clip (aged-up character, e.g. NBA arena) | The transformation completed |
| 5. Outro | Text overlay on poster | Call to action / title card |

## Pipeline Steps

### 1. Generate Style Anchor Poster
- Model: Seedream 5.0 Pro, 9:16 (1530×2720)
- Identity: Qwen-VL forensic analysis of user photos → unified prompt (pitfall #51)
- QA: external vision model, target 9+/10 likeness

### 2. Upload Poster for I2V Reference
```bash
curl -s -F "reqtype=fileupload" -F "fileToUpload=@poster.png" https://catbox.moe/user/api.php
# Returns: https://files.catbox.moe/xxxxx.png
```

### 3. Generate Anime Clips (Hailuo 2.3 Pro I2V)
- Model: `hailuo/2-3-image-to-video-pro`
- Cost: 45cr per clip (6s, 768P)
- Image ref: catbox URL from step 2
- For character age-up (teen→adult): use Claude Fable 5 to write the prompt (pitfall #52)
- Batch submit ALL clips, then poll (parallelizes KIE backend)

### 4. Extract Real Footage Segments
```bash
ffmpeg -y -ss {start} -t 1.5 -i real_clip.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,eq=gamma=1.3:brightness=0.05:saturation=1.35:contrast=1.15" \
  -c:v libx264 -preset ultrafast -crf 20 -pix_fmt yuv420p -an \
  segment_N.mp4
```
- Cuts: 1.5s each (TikTok pacing)
- Color grading: gamma 1.3 + saturation 1.35 + contrast 1.15 (dramatic look)
- ALWAYS normalize to 30fps before concat

### 5. Concat Sequence (interleave real + anime)
```
intro.mp4 → real_1 → real_2 → real_3 → anime_1 → real_4 → real_5 → anime_2 → real_6 → anime_3(payoff)
```

### 6. Audio Mix
- VO: ElevenLabs Adam (`pNInz6obpgDQGcFmaJgB`, `eleven_multilingual_v2`)
  - Key in `~/crypto-project/.env` as `ELEVENLABS_API_KEY`
  - Direct API call (not Hermes text_to_speech — key not in env)
- Ambient: extract from real footage, volume 0.15
- Mix: `amix=inputs=2:duration=longest` (NOT `duration=first` — see pitfall #53)
- Do NOT use `-shortest` in final merge (see pitfall #53)

### 7. Subtitles (96pt ASS)
```
Style: Poppins SemiBold, 96pt, white text, black outline 5px, shadow 3px
MarginV: 300 (positioned in lower third for mobile readability)
```

### 8. Output
- Full quality: libx264 ultrafast CRF 23, 1080×1920
- Telegram: scale 810×1440, CRF 28, mono 128k (~12-19MB)

## Cost Breakdown (4 anime clips)

| Item | Credits | USD |
|------|---------|-----|
| Poster (Seedream) | ~28 | $0.14 |
| 4 × Hailuo Pro clip | 180 | $0.90 |
| Fable 5 prompt (OpenRouter) | ~$0.02 | $0.02 |
| **Total** | **~208** | **~$1.06** |

## Key Decisions
- **Hailuo over Seedance**: identity lock across clips > motion fluidity for character consistency
- **Fable 5 for aged-up prompts**: writes production-grade Hailuo prompts with triple identity lock
- **Real footage color grading**: the real clips must LOOK treated (not raw phone footage) to reduce the real/anime clash
- **Interleaving**: alternating real/anime every 2-3 segments creates rhythm and prevents either style from feeling monotonous

## PITFALL #54: kie.ai Polling — `state` not `status` + double-serialized resultJson

**Validated Aug 3, 2026** — caused 8-min polling timeouts despite clips being ready in ~109s.

### The Bug

The kie.ai `recordInfo` endpoint returns:
```json
{
  "code": 200,
  "data": {
    "taskId": "...",
    "state": "success",         // ← NOT "status", and lowercase "success" not "SUCCESS"
    "resultJson": "{\"resultUrls\":[\"https://...\"]}",  // ← STRING, not parsed JSON
    "failCode": null,
    "failMsg": null,
    "costTime": 109,
    "creditsConsumed": 45.0
  }
}
```

**Three traps in one response:**
1. Field is `state`, NOT `status` — polling code checking `data.get("status")` always returns `None`
2. Value is lowercase `"success"` — case-sensitive checks for `"SUCCESS"` will also fail
3. `resultJson` is a **JSON string** (double-serialized) — must `json.loads(resultJson)` then access `['resultUrls'][0]`

### Correct Polling Code

```python
import json, requests, time

def poll_kie(task_id, api_key, timeout=300):
    headers = {"Authorization": f"Bearer {api_key}"}
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )
        data = r.json().get("data", {})
        state = data.get("state", "")  # ← "state" NOT "status"
        
        if state == "success":         # ← lowercase
            result = json.loads(data["resultJson"])  # ← double-deserialize
            video_url = result["resultUrls"][0]
            return video_url
        elif state in ("failed", "error"):
            raise RuntimeError(f"Task failed: {data.get('failMsg')}")
        
        time.sleep(5)
    raise TimeoutError(f"Polling timeout for {task_id}")
```

### Faster Alternative: Skip Polling, Batch Check

Since Hailuo Pro clips complete in ~100-110s, you can submit all clips, wait 2 min, then batch-check all task IDs at once (no per-clip polling loop needed):

```bash
for tid in $(cat *_v2_taskid.txt); do
    curl -s "https://api.kie.ai/api/v1/jobs/recordInfo?taskId=$tid" \
        -H "Authorization: Bearer $KEY" | python3 -c "
import sys,json
d=json.load(sys.stdin)['data']
print(f\"{d['taskId'][:8]}: state={d['state']}\")
if d['state']=='success':
    url=json.loads(d['resultJson'])['resultUrls'][0]
    print(f'  → {url}')
"
done
```

## Known Limitations
- Hailuo I2V clips are 768×1364 (not 1080×1920) — upscaled in concat
- Character age-up via I2V: face stays slightly youthful (the poster is the teen version)
- Real footage framerates vary (25/30/60fps) — MUST normalize all to 30fps before concat
- **Character identity drift across clips** (Fable 5 V2 clips): face age fluctuates, outfit color drifts (navy→black). QA score 6/10 on V5. Mitigation: use Seedance Character Consistency (3-photo identity lock) instead of Hailuo for multi-clip identity fidelity.
