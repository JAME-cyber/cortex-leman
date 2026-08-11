# Brand Identity Alignment Workflow

Workflow complet pour réaligner les assets vidéo existants quand un client transmet
ses documents graphiques officiels en cours de projet.

## Contexte d'origine

Culture en Saveur (juil. 2026): 6 vidéos déjà produites avec palette approximative
(`#C65D3B`, `#E8A93C`, etc.). Linda transmet le roll-up Canva officiel + un flyer.
Extraction révèle une palette différente (`#A0392B`, `#B58761`, `#492E21`, `#F5E8D3`).
Taglines officielles absentes des vidéos: "DÉCOUVRIR · INSPIRER · TRANSMETTRE".

## Étapes du workflow

### 1. Extraction de l'identité officielle

**PDF → image:**
```bash
pdftoppm -png -r 200 "input.pdf" /tmp/page
# -r 200 = bonne résolution pour OCR + analyse couleur
```

**Image → palette:**
```python
from PIL import Image
img = Image.open("page.png").convert("RGB")
colors = img.getcolors(maxcolors=65536)
# Trier par count décroissant, filtrer background
top = sorted(colors, reverse=True)[:10]
```

**Image → texte (OCR):**
- Qwen 2.5 VL 72B via OpenRouter (gratuit, excellent OCR FR)
- Encodage: resize à 1600px max, base64 JPEG quality 85
- Alternative: OCR.space (apikey: helloworld, OCREngine 2)

### 2. Créer la source de vérité

Fichier `research/brand_identity.md` contenant:
- Nom, tagline, slogan, description
- Palette hex complète (avec noms descriptifs)
- Conversion: "pour prompts IA" (mots pas hex)
- Typographies (rôle + police + poids + fallback)
- Application: title cards, end cards, overlays, transitions
- Valeurs à projeter (tonalité visuelle)

### 3. Télécharger et installer les fonts

⚠️ **PITFALL: `curl github.com/google/fonts/raw/...` retourne du HTML (page 404/login), PAS le binaire TTF.** Toujours vérifier avec `file *.ttf` → doit afficher "TrueType Font data", pas "HTML document".

**Méthode fiable: Google Fonts CSS API → gstatic.com (binaire réel)**

```python
#!/usr/bin/env python3
"""Download Google Fonts as real TTF binaries via CSS API."""
import urllib.request, re, os

def download_google_font(family, weights, out_dir="assets/fonts"):
    """family: 'Montserrat', weights: ['400','600','700']"""
    css_url = f"https://fonts.googleapis.com/css2?family={family}:wght@{';'.join(weights)}&display=swap"
    req = urllib.request.Request(css_url, headers={"User-Agent": "Mozilla/5.0"})
    css = urllib.request.urlopen(req, timeout=10).read().decode()

    # Parse @font-face blocks to map weight → URL
    blocks = css.split("@font-face")
    for block in blocks:
        weight_m = re.search(r"font-weight:\s*(\d+)", block)
        url_m = re.search(r"src:\s*url\((https://[^)]+)\)", block)
        if weight_m and url_m:
            w = weight_m.group(1)
            if w in weights:
                fname = f"{family}-{{'400':'Regular','600':'SemiBold','700':'Bold'}.get(w,w)}.ttf"
                urllib.request.urlretrieve(url_m.group(1), os.path.join(out_dir, fname))
                print(f"  ✅ {fname} ({w})")

# Exemple: Montserrat 400/600/700
download_google_font("Montserrat", ["400", "600", "700"])
```

Pour PlayfairDisplay (variable font), utiliser le weight 400..900:
```python
css_url = "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400..900&display=swap"
```

**Vérification obligatoire:**
```bash
file assets/fonts/*.ttf  # doit afficher "TrueType Font data"
# Si "HTML document" → le téléchargement a échoué, revoir la méthode

# Installer pour fontconfig/libass
mkdir -p ~/.local/share/fonts
cp assets/fonts/*.ttf ~/.local/share/fonts/
fc-cache -f
fc-match "Poppins:style=Bold"  # vérifier disponibilité
```

### 4. Générateur de cartes unifié

Un seul script `scripts/gen_brand_cards.py` qui produit:
- `title_card.jpg` pour T1/T2/T3 (1080×1920)
- `cta_frame.jpg` pour T1/T2/T3 (1080×1920)
- `hook_card.jpg` pour V1 (1080×1920)
- `cta_card.jpg` pour V1 (1080×1920)
- `intro_card.png` + `end_card.png` pour promo (720×1280)

Toutes les cartes partagent:
- Gradient crème → sable
- Tagline footer "DÉCOUVRIR · INSPIRER · TRANSMETTRE"
- Coordonnées complètes (email, tél, réseaux)
- Dividers décoratifs (ligne + losange central)
- Médailions concentriques (motif africain)

### 5. Patcher les styles ASS

Format couleur ASS: `&HAABBGGRR` (alpha + BGR inversé)

```python
def to_ass(rgb):
    r, g, b = rgb
    return f"&H00{b:02X}{g:02X}{r:02X}"

# Exemples:
# Crème   (245,232,211) → &H00D3E8F5
# Cacao   (73,46,33)    → &H00212E49
# Deep red(122,30,30)   → &H001E1E7A
```

Ligne ASS à patcher dans chaque build script:
```
Style: Default,Poppins,52,&H00D3E8F5,&H001E1E7A,&H00212E49,&H80000A1A,-1,0,0,0,100,100,0,0,1,3,1,2,60,60,140,1
```

### 6. Reconstruire les vidéos

**Séquentiellement** (pas en parallèle — voir pitfall #16 du SKILL.md):

```bash
timeout 300 python3 scripts/build_t1_v3.py
timeout 300 python3 scripts/build_t2_visio.py
timeout 300 python3 scripts/build_t3_nil.py
timeout 300 python3 scripts/build_v1_presentation.py
```

Pour la promo (intro + seedance + end card assemblage manuel ffmpeg):
```bash
# Intro card → vidéo (1.5s)
ffmpeg -y -loop 1 -i renders/intro_card.png -t 1.5 \
  -vf scale=720:1280 -c:v libx264 -crf 18 -pix_fmt yuv420p -r 24 \
  renders/promo_intro.mp4

# End card → vidéo (2.5s)
ffmpeg -y -loop 1 -i renders/end_card.png -t 2.5 \
  -vf scale=720:1280 -c:v libx264 -crf 18 -pix_fmt yuv420p -r 24 \
  renders/promo_end.mp4

# Concat intro + seedance + end
ffmpeg -y -f concat -safe 0 -i concat.txt \
  -c:v libx264 -pix_fmt yuv420p -movflags +faststart \
  output/promo/promo_final_v2.mp4
```

### 7. Validation

**Technique:** ffprobe pour résolution, durée, taille
**Palette:** PIL getcolors() pour confirmer présence terracotta officielle
**Visuelle:** Qwen 2.5 VL 72B pour lire texte + confirmer couleurs + décrire mood

## Checklist finale

- [ ] Charte source créée (`research/brand_identity.md`)
- [ ] Fonts officiels téléchargés + installés + vérifiés
- [ ] Générateur de cartes unifié créé et exécuté
- [ ] Toutes les cartes régénérées (title + CTA + hook)
- [ ] Styles ASS patchés dans tous les build scripts
- [ ] Toutes les vidéos reconstruites (séquentiel)
- [ ] Promo reconstruite (intro + IA + end)
- [ ] Validation technique (ffprobe)
- [ ] Validation palette (PIL getcolors)
- [ ] Validation visuelle (Qwen VL ou contact sheet)
