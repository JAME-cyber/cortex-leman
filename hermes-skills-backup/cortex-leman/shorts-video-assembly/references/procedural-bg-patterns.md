# Backgrounds procéduraux avec PIL — Patterns africains

Génération de backgrounds/textures sans API IA, via PIL seule. Utile pour les hook cards, title cards, et overlays quand on veut un visuel brandé rapidement sans attendre une génération IA.

## Pattern wax / pan-africain (losanges)

Grille de losanges emboîtés avec palette terracotta. Validé sur Culture en Saveur (juil 2026).

```python
from PIL import Image, ImageDraw

W, H = 1080, 1920

# Palette Terracotta officielle Culture en Saveur
TERRACOTTA = (160, 0, 0)    # #a00000
OCRE = (181, 135, 97)       # #b58761
CACAO = (73, 46, 33)        # #492e21
CREME = (245, 232, 209)     # #f5e8d3
GOLD = (216, 138, 34)       # #d88a22

img = Image.new("RGB", (W, H), CACAO)
draw = ImageDraw.Draw(img)

tile = 120  # taille de la cellule
for row in range(-1, H // tile + 2):
    for col in range(-1, W // tile + 2):
        cx = col * tile + (tile // 2 if row % 2 else 0)
        cy = row * tile
        size = tile // 2 - 4
        # Grand losange
        pts = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]
        color = TERRACOTTA if (row + col) % 2 == 0 else OCRE
        draw.polygon(pts, fill=color, outline=GOLD)
        # Petit losange intérieur
        inner = size // 2
        pts2 = [(cx, cy - inner), (cx + inner, cy), (cx, cy + inner), (cx - inner, cy)]
        inner_color = CREME if (row + col) % 2 == 0 else CACAO
        draw.polygon(pts2, fill=inner_color)
        # Point central doré
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=GOLD)
```

### Overlay sombre pour lisibilité texte

Quand un texte va être posé sur le pattern, ajouter un gradient sombre:

```python
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
odraw = ImageDraw.Draw(overlay)
for y in range(H):
    alpha = int(max(0, min(150, (y - 600) / 4)))
    odraw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
img = Image.alpha_composite(img.convert("RGBA"), overlay)
```

### Texte avec ombre portée

Pour la lisibilité sur pattern chargé, toujours ajouter une ombre:

```python
# Shadow layer
overlay = Image.new("RGBA", (W, H), (0,0,0,0))
od = ImageDraw.Draw(overlay)
od.text((x + 3, y + 3), text, fill=(0,0,0,int(alpha*0.6)), font=f)
od.text((x, y), text, fill=(245,232,211,alpha), font=f)
img.paste(overlay, (0,0), overlay)
```

## Variantes de palette

| Projet | Base | Primaire | Accent | Highlight |
|--------|------|----------|--------|-----------|
| Culture en Saveur | CACAO | TERRACOTTA | OCRE | GOLD |
| African Heroes | CACAO | OCRE | GOLD | CREME |
| Cortex Leman (défaut) | (20,20,30) | (0,120,200) | (50,180,255) | (200,200,210) |

Adapter les couleurs à la charte du projet en gardant la structure du pattern.
