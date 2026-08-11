# Image-to-Video (I2V) with Identity Lock

## Workflow

1. **Host the reference image**: Kie.AI API requires a **public URL** for `first_frame_url`.
   - `catbox.moe` works: `curl -s -F "reqtype=fileupload" -F "fileToUpload=@/path/to/img.jpg" https://catbox.moe/user/api.php`
   - Returns a direct URL like `https://files.catbox.moe/xxxxx.jpg`
   - `0x0.st` is currently disabled (botnet spam)

2. **API call**: Use `hailuo/02-text-to-video-standard` with `first_frame_url` in `input`:
   ```python
   payload = {
       "model": "hailuo/02-text-to-video-standard",
       "input": {
           "prompt": prompt,
           "duration": "6",  # MUST be string, not int
           "first_frame_url": "https://files.catbox.moe/xxxxx.jpg",
       }
   }
   # POST to https://api.kie.ai/api/v1/jobs/createTask
   ```

3. **Identity lock prompt pattern** (from Pattern #14, validated):
   - Describe the person's features explicitly in the prompt
   - End with: `"Fully maintain facial features, skin texture, hair, [beard], [accessories] throughout."`
   - This is CRITICAL for I2V — without it, the model drifts from the reference photo

4. **Cost**: 30cr per 6s clip (same as T2V Standard)

5. **Limitations**:
   - 6s max on Hailuo Standard (vs 25-30s on Dreamina/Seedance 2.5 web)
   - Identity consistency is good but not perfect — expect minor drift
   - The `first_frame` constrains the opening shot; the model interprets the scene from there

## API Key Gotcha

The env var in `~/.bashrc` is **`KIEAI_API_KEY`** (no underscore between KIE and AI), NOT `KIE_AI_API_KEY`. Scripts that look for the wrong name will silently fail with "key not found".

## Example Script

See `scripts/i2v_tars_vintage.py` for a complete working example with:
- Key extraction from `.bashrc`
- Image upload to catbox.moe
- I2V task submission + polling
- Credit tracking before/after
