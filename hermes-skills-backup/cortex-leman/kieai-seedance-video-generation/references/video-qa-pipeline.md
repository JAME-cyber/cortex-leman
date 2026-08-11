# Video QA Pipeline — Frame Extraction + Free Vision Analysis

## When to Use

After a user sends an AI-generated video (via Telegram or otherwise) and you need to:
- Verify the video matches the prompt criteria
- Check character appearance (skin tone, clothing, wounds)
- Assess cinematic quality
- Decide whether to accept or retry

## Pipeline

### Step 1: Extract Frames

```bash
VIDEO="/path/to/video.mp4"
DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$VIDEO")
echo "Duration: ${DURATION}s"

# Extract 3-4 frames evenly spaced (adjust frame numbers based on fps/duration)
ffmpeg -y -i "$VIDEO" -vf "select='eq(n\,0)+eq(n\,60)+eq(n\,120)+eq(n\,180)'" -vsync vfr /tmp/frame_%02d.jpg
```

For a 10s video at 24fps: frame 0 = start, frame 60 = 2.5s, frame 120 = 5s, frame 180 = 7.5s.

### Step 2: Analyze Each Frame with NVIDIA Vision (FREE)

```bash
python3 ~/.hermes/skills/devops/vision-analysis-fallback/scripts/or_vision.py \
  /tmp/frame_01.jpg \
  "Describe what you see. Check: [list specific criteria from prompt]. Be specific about skin color, clothing, setting."
```

Run first and last frames in parallel (two terminal calls in one turn). ~5s per frame.

### Step 3: Report

Create a pass/fail table per criterion:

```
| Criterion | Verdict | Detail |
|---|---|---|
| Dark-skinned character | ✅/❌ | ... |
| Wound/bandage visible | ✅/❌ | ... |
| Camera direction followed | ✅/❌ | ... |
```

### Step 4: Retry Prompt (if needed)

If physical traits (skin tone, wounds, scars) are wrong, generate a reinforced prompt:
- Strengthen: `very dark brown skin` instead of `dark skin`
- Add: `Nubian facial features`, specific hair texture
- Reduce ambiguity: remove any words that could be interpreted as western/European
- Simplify: fewer elements per shot = model focuses on character accuracy

## Cost

**0€** — NVIDIA Llama 3.2 11B Vision is free via NVIDIA_API_KEY. ~5s per frame.
No OpenRouter costs unless NVIDIA is down (automatic fallback).
