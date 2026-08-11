# Brand Identity Integration in Build Scripts

## Context
Linda (Culture en Saveurs client) provided detailed brand identity feedback.
The build scripts (`build_funnel_all.py`, `build_t4_funnel.py`) had hook cards using:
- Wrong fonts (Montserrat instead of Playfair Display + Poppins)
- Dark background instead of cream (#F5E8D3)
- No logo, no dates, no contact info
- Missing tagline

## Brand Palette (from brand_identity.md)
| Role | Color | Hex |
|------|-------|-----|
| Terracotta primary | Titles, accents, CTA | `#A0392B` |
| Ocre/Cuivre | Subtitles, secondary | `#B58761` |
| Cacao | Text on light bg | `#492E21` |
| Crème ivoire | Main background | `#F5E8D3` |
| Beige sable | Gradients | `#E0C0A0` |

## Typography Rules
| Role | Font | Weight |
|------|------|--------|
| Titles | Playfair Display | Bold/SemiBold |
| Body/Subtitles | Poppins | Regular/Medium |
| Accents/CTA | Poppins | SemiBold, uppercase, +0.05em letter-spacing |

## Hook Card Layout (720×1280, 9:16)
```
[Logo CES — centered top, ~200px wide]
                                    
    [Playfair Display title lines]   
    (Terracotta for highlighted word)
    (Cacao for regular text)        
                                    
    ── DU 10 AU 14 AOÛT ──           
    AU PETIT-LANCY                   
    ─────────────────────            
    cultureensaveurs@gmail.com       
    +41 76 756 22 82                 
    @cultureensaveurs                
                                    
    DÉCOUVRIR · INSPIRER · TRANSMETTRE
```

## Pitfalls (VALIDATED Jul 30, 2026)

### 1. Corrupted font files
`PlayfairDisplay-Bold.ttf` and `PlayfairDisplay-SemiBold.ttf` were actually HTML files (failed downloads).
**Fix**: Use `PlayfairDisplay-Variable.ttf` which is a valid TTF.
**Diagnostic**: `file assets/fonts/PlayfairDisplay-Bold.ttf` → "HTML document" instead of "TrueType Font data".
**Always run this check before assuming a font works.**

### 2. PIL Image.LANCZOS deprecated
`Image.LANCZOS` raises `AttributeError` in modern Pillow.
**Fix**: `Image.Resampling.LANCZOS`

### 3. ASS subtitles font name
ASS subtitle Style line must use the font's **family name** as registered in the TTF,
not the filename. `Poppins-SemiBold.ttf` → font name `Poppins SemiBold`.
```
Style: Default,Poppins SemiBold,38,...
```

### 4. Cream background texture
The `draw_bg()` function must generate noise around the cream RGB values, not dark values.
Old code: `fill=(38+r, 30+r, 27+r)` (dark terracotta noise)
New code: parse hex → RGB → add noise: `fill=(r+n, g+n, b+n)` where (r,g,b) = cream

### 5. Subtitle color in ASS
ASS uses BGR hex format `&H00BBGGRR` (reversed from normal RGB hex).
- Cream `#F5E8D3` → `&H00D3E8F5`
- Cacao `#492E21` → `&00212E49`

## Key Correction: Don't Touch What's Already Done
When a client says text/music is "already changed", do NOT modify VO scripts, 
subtitle text, or music tracks. Only modify the VISUAL elements (clips, hook cards, 
font, layout). Modifying already-approved content wastes time and can introduce errors.

## Integration Checklist
- [ ] Check all font files with `file` command before using
- [ ] Use `Image.Resampling.LANCZOS` (not `Image.LANCZOS`)
- [ ] Update ASS subtitle Style fontname to match charte (Poppins SemiBold)
- [ ] Add logo PNG to hook card (centered top, 200px wide)
- [ ] Add dates bar (Poppins SemiBold, Terracotta)
- [ ] Add contact info (email, phone, Instagram)
- [ ] Add tagline at bottom
- [ ] Use cream background with cream-noise texture
- [ ] Titles in Playfair Display Variable, body in Poppins
