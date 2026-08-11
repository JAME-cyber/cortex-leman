# Playwright SVG `<image>` Data URI Gotcha

## The Bug

When building animated intros with Playwright (HTML SVG → frame capture → MP4), embedding a PNG/JPEG logo as a data URI inside an SVG `<image>` tag **fails silently** in headless Chromium. The image element exists in the DOM, the `href` attribute is set correctly, opacity is 1, but **zero pixels are rendered**.

This cost 4 build iterations on the Sankofa intro (July 2026).

## Reproduction

```html
<svg viewBox="0 0 1080 1920">
  <g transform="translate(540, 700)">
    <!-- This renders NOTHING in Playwright headless -->
    <image href="data:image/jpeg;base64,/9j/4AAQ..." 
           x="-380" y="-380" width="760" height="760" opacity="1"/>
  </g>
</svg>
```

## Diagnosis Methodology

```python
from playwright.sync_api import sync_playwright
from PIL import Image, ImageStat

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1920})
    page.goto("file:///path/to/intro.html")
    page.wait_for_load_state("networkidle")
    page.evaluate("window.render(2.5)")  # logo should be visible
    page.screenshot(path="test.png")
    
    img = Image.open("test.png")
    # Crop the area where the logo should be
    crop = img.crop((200, 470, 880, 1150))
    stat = ImageStat.Stat(crop)
    brightness = sum(stat.mean[:3]) / 3
    
    # Count amber/gold pixels (or whatever the logo's dominant color is)
    pixels = list(crop.getdata())
    amber = sum(1 for r,g,b,*_ in pixels if r > 100 and 60 < g < 180 and b < 100)
    pct = amber / len(pixels) * 100
    
    print(f"Brightness: {brightness:.1f}")  # ~30 = background only (BUG)
    print(f"Amber pixels: {pct:.1f}%")       # 0.0% = logo NOT rendering
```

**Key indicators:**
- `brightness ≈ 30` (background only) → logo NOT rendering
- `brightness ≈ 40` with `amber > 5%` → logo IS rendering
- The `opacity` attribute shows `1` but pixels are absent

## The Fix — HTML `<img>` Overlay

Replace the SVG `<image>` with an HTML `<img>` positioned absolutely on top of the SVG:

```html
<!-- SVG handles: circles, text, particles, animations -->
<svg viewBox="0 0 1080 1920">
  <g id="logo" transform="translate(540, 700)">
    <circle id="outerRing" cx="0" cy="0" r="240" .../>
    <!-- NO <image> here -->
  </g>
</svg>

<!-- HTML <img> overlay for the logo PNG — renders reliably -->
<img id="birdImg" src="data:image/jpeg;base64,..."
     style="position:absolute; top:470px; left:200px; width:680px; height:680px;
            opacity:0; filter:drop-shadow(0 0 20px rgba(232,163,61,0.4));
            z-index:10; pointer-events:none"/>
```

**JS animation update:**
```javascript
// For SVG elements: use setAttribute('opacity', val)
ring.setAttribute('opacity', val);  // ✅ works on SVG

// For HTML elements (the img): use style.opacity
bird.style.opacity = val;  // ✅ works on HTML img
```

## Base64 Embedding Strategy

When embedding a logo PNG as a data URI in HTML, size matters — a 2048×2048 PNG generates ~1.1MB base64 which bloats the HTML file. Optimization pipeline:

```python
import base64
from PIL import Image
from io import BytesIO

img = Image.open("logo_2048.png").convert("RGBA")

# 1. Resize to display size (500-760px is enough for 1080×1920 frame)
img = img.resize((500, 500), Image.LANCZOS)

# 2. Flatten onto background color (JPEG has no alpha)
#    Match the intro's background to avoid visible edges
bg = Image.new("RGB", (500, 500), (26, 26, 26))  # anthracite #1A1A1A
bg.paste(img, mask=img.split()[3])

# 3. JPEG q85 — 10x smaller than PNG
buf = BytesIO()
bg.save(buf, format="JPEG", quality=85, optimize=True)
b64 = base64.b64encode(buf.getvalue()).decode()

# Result: ~39 KB base64 (vs 465 KB PNG, vs 1142 KB original)
```

| Format | Size (base64) | Alpha | Use when |
|--------|--------------|-------|----------|
| PNG 760px | 465 KB | ✅ | Logo has transparency that must be preserved |
| PNG 500px | 465 KB | ✅ | Same, slightly smaller |
| JPEG q85 500px | **39 KB** | ❌ (flattened on bg) | Logo on solid-color background (preferred) |

**Rule:** If the intro background is a solid color (anthracite, navy, black), flatten the logo onto that color and use JPEG. The logo's edges blend invisibly and you save 10× on HTML size.
