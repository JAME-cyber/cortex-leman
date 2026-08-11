# kie.ai Seedream 5.0 Image Generation

Static image generation via Seedream 5.0 Pro on the same kie.ai platform used for Seedance video.
Shared credit pool, same API platform, different model.

## API: `kc.gen_image()`

The `KieClient` at `/home/tars/african-heroes/scripts/kie_client.py` handles both video and images.

```python
import sys
sys.path.insert(0, "/home/tars/african-heroes/scripts")
from kie_client import KieClient

kc = KieClient()  # reads KIE_API_KEY from env

kc.gen_image(
    prompt="...",
    out_path="/path/to/output.png",
    model="seedream_5_pro",      # or "seedream_5_lite", "seedream_4_5", "flux_2_pro"
    aspect_ratio="3:4",          # see supported ratios below
    quality="high",
    output_format="png",
)
```

## Model Registry

```python
MODELS = {
    "image": {
        "seedream_5_pro": "seedream/5-pro-text-to-image",
        "seedream_5_lite": "seedream/5-lite-text-to-image",
        "seedream_4_5": "seedream/4-5-text-to-image",
        "flux_2_pro": "flux2/pro-text-to-image",
    },
}
```

## Supported aspect ratios
`1:1`, `4:3`, `3:4`, `16:9`, `9:16`, `21:9`, `adaptive`

⚠️ **`4:5` is NOT supported** — returns "aspect_ratio not within allowed range". Use `3:4` for vertical poster formats.

## Negative prompts

**No `negative_prompt` parameter** on `gen_image()`. Unlike some image APIs, constraints must be woven into the main prompt text:

```python
# ❌ Won't work — gen_image has no negative_prompt kwarg
kc.gen_image(prompt=..., negative_prompt="no blue, no watermark")

# ✅ Embed in the prompt
prompt = "... Description ... no cold blue tones, no watermark, no logo, no border frame."
kc.gen_image(prompt=prompt)
```

## Cost & timing (observed Jul 2026)

| Image type | Credits | ~USD | Generation time |
|-----------|---------|------|-----------------|
| Seedream 5.0 Pro, 3:4, high quality | ~28 | ~$0.28 | ~150s |
| Seedream 5.0 Pro, 9:16, high quality | ~28 | ~$0.28 | ~120s |

Cheaper than video (~28 credits vs ~410-615 for 10-15s Seedance video).

## Polling timeout

A single image can take 2-3 minutes. The KieClient's internal polling may exceed the terminal 180s timeout. **Always run in background** with `notify_on_complete=true`:

```bash
# terminal(background=true, notify_on_complete=true)
python3 scripts/gen_images.py
```

## Patterns library integration

The project maintains a patterns library at `<project>/research/seedance_patterns_library.md` (or equivalent). Patterns that use static image generation (as opposed to video) should be catalogued with the `Registre IMAGE` label to distinguish from Seedance video patterns.

### Pattern #24 — Papercraft travel poster (Seedream 5.0)

Source: [@Naiknelofar788](https://x.com/Naiknelofar788/status/2081306869503799549)

Template-based: `{DESTINATION}` is a variable, the rest of the prompt is fixed → generates a coherent series by changing only the destination.

**Key tokens:**
- Medium: "3D paper quilling and layered papercraft" + "rolled paper coils" + "embossed paper textures" + "precision paper cutouts" + "layered cardstock"
- Composition: "storybook-like composition with a sense of depth and perspective" + "vertical poster"
- Local elements: "flowers, trees, waterways, mountains, traditional transportation, wildlife, cultural motifs unique to the destination"
- Lighting: "warm golden-hour lighting"
- Typography: "destination name in large bold vintage travel-poster typography at the top"
- Quality: "premium craftsmanship, whimsical, colorful, nostalgic, editorial-quality travel art, ultra-high resolution"

**Guardrail**: style illustratif = supports hors-feed uniquement (flyers, posters impression, cartes). Ne jamais substituer au feed photo authentique d'un client. Adapter la palette à la charte existante.

Working test script: `/home/tars/culture-en-saveur/scripts/test_papercraft_egypt.py`
