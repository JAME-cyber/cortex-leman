# Sous-titres, Format Vertical, Thumbnails (aout 2026, Amanirenas)

## 1. Sous-titres : SRT natif YouTube > brûlés

**Correction utilisateur majeure.** Brûler les sous-titres via ffmpeg `subtitles` filter produit un résultat systématiquement rejeté : texte trop grand, boîte noire envahissante (BorderStyle=3), rendu amateur. L'utilisateur a comparé avec un Short de référence (-AXbUY_J3yc, chaîne Scanderia) qui utilise les **sous-titres natifs YouTube** (SRT uploadé séparément, rendu par le player YouTube).

**Règle :** NE JAMAIS brûler les sous-titres dans la vidéo. Produire :
1. Une vidéo **clean** (sans texte incrusté)
2. Un fichier **SRT séparé** pour upload YouTube
3. YouTube gère le rendu natif (texte blanc, fond semi-transparent, taille discrète)

**Si brûlage exigé** (demande explicite), paramètres MINIMAUX :
```
force_style='FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=60'
```
- `BorderStyle=1` (outline only) PAS `BorderStyle=3` (box opaque)
- `FontSize=16` (très petit) PAS `FontSize=24+`
- `Alignment=2` (bottom center) PAS `Alignment=8` (top)

## 2. Landscape→vertical : zoom-crop, PAS blur background

La technique "blurred background + centered video" (scale + pad + boxblur) crée des **bandes floues visibles** en haut et en bas. L'utilisateur rejette immédiatement ("il y a une bande flou en haut et en bas").

**Solution validée : zoom-crop plein écran.**
```bash
ffmpeg -y -ss 0.5 -t 7.5 -i input_16x9.mp4 \
  -vf "scale=-1:1920,crop=1080:1920,fps=24" \
  -c:v libx264 -preset fast -crf 20 -an output_9x16.mp4
```

**Pourquoi pas `force_original_aspect_ratio=increase` ?** Ne fonctionne pas pour landscape→portrait car la hauteur source (720) < 1920. Utiliser `scale=-1:1920` (scale par hauteur) puis `crop=1080:1920` (crop center width).

**Vérification full-bleed** (via PIL/numpy) :
- Bords (y=0 et y=1919) doivent avoir `std > 25` = contenu réel
- Si `brightness < 15 AND std < 8` → bande noire/letterbox détectée

## 3. Thumbnail vertical style (série Sankofa)

Style validé par comparaison avec ref (-AXbUY_J3yc "VOIR SEVILLE — LE COEUR DE L'ANDALOUSIE").

| Élément | Spec |
|---|---|
| Format | 1080×1920 vertical |
| Titre | Blanc bold, ~85px, centré bas (~75% hauteur) |
| Sous-titre | Couleur accent (Sankofa: #E89560), ~38px, sous le titre |
| Gradient | Semi-transparent noir bas 40% pour lisibilité texte |
| Shadow | Text offset 2-3px noir semi-opaque (multi-offset: 4 directions) |
| Police | DejaVuSans-Bold.ttf (système) |

**Génération via PIL :**
```python
from PIL import Image, ImageDraw, ImageFont

def make_thumbnail(frame_path, title, subtitle, accent=(232,149,96)):
    src = Image.open(frame_path)
    sw, sh = src.size
    # Scale height→1920
    scale = 1920 / sh
    src_scaled = src.resize((int(sw*scale), 1920), Image.LANCZOS)
    # Crop center 1080
    left = (src_scaled.width - 1080) // 2
    thumb = src_scaled.crop((left, 0, left+1080, 1920)).convert('RGBA')
    
    # Gradient overlay bottom 40%
    overlay = Image.new('RGBA', (1080, 1920), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    for y in range(1100, 1920):
        alpha = int(((y-1100)/820)**1.5 * 180)
        draw.line([(0,y),(1080,y)], fill=(0,0,0,min(alpha,200)))
    thumb = Image.alpha_composite(thumb, overlay)
    
    draw = ImageDraw.Draw(thumb)
    # Title: white bold centered
    title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 85)
    # Subtitle: accent color centered below
    sub_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 38)
    # Shadow: 4-direction offset
    for dx,dy in [(3,3),(2,2),(-2,2),(2,-2)]:
        draw.text((tx+dx,ty+dy), title, font=title_font, fill=(0,0,0,200))
    draw.text((tx,ty), title, font=title_font, fill=(255,255,255))
    draw.text((sx,sy), subtitle, font=sub_font, fill=accent)
    
    return thumb.convert('RGB')
```

**Workflow thumbnail batch** (4 vidéos Sankofa) :
1. Télécharger vidéos existantes via `yt-dlp -f "137+140"`
2. Extract frames à intervalles réguliers (`ffmpeg -vf "fps=1/X"`)
3. QA frames via `or_vision.py` (chercher hero shot clair)
4. Générer thumbnail avec PIL (titre + sous-titre + gradient)
5. Valider via `or_vision.py` (lire le texte, impact 1-10)

**Style ref analysé** (-AXbUY_J3yc) :
- Pas de sous-titres brûlés dans la vidéo (VTT natif YouTube)
- Vidéo plein écran (pas de letterbox)
- Thumbnail avec gros titre + sous-titre contextuel
- Tons chauds, image frappante

## 4. Pipeline multi-clips landscape→vertical complet

**Contexte :** 9-11 clips IA générés en landscape (1280×720) à assembler en Short vertical 1080×1920 avec VO.

```bash
# Step 1: Convertir chaque clip (zoom-crop plein écran)
for clip in clips/*.mp4; do
  ffmpeg -y -ss 0.5 -t 8 -i "$clip" \
    -vf "scale=-1:1920,crop=1080:1920,fps=24" \
    -c:v libx264 -preset fast -crf 20 -an "work/v$(printf '%02d' $i).mp4"
done

# Step 2: Concat (demuxer, pas de re-encode)
cat > concat.txt << EOF
file 'v01.mp4'
file 'v02.mp4'
...
EOF
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy video_concat.mp4

# Step 3: Audio VO (edge-tts, delay 500ms + fadeout)
ffmpeg -y -i vo.mp3 \
  -af "adelay=500|500,apad=pad_dur=3,afade=t=out:st=78:d=3" \
  -t $VIDEO_DUR -c:a aac -b:a 192k vo_final.m4a

# Step 4: Mux
ffmpeg -y -i video_concat.mp4 -i vo_final.m4a \
  -c:v copy -c:a copy -shortest with_audio.mp4

# Step 5: SRT séparé (NE PAS brûler)
# Générer fichier SRT avec timing aligné sur la VO
```

**⚠ Pitfalls :**
- Le concat demuxer exige specs **identiques** (resolution, fps, codec, pix_fmt). Un clip manquant = exit 234.
- `libx264 -preset fast -crf 20` pour 9 clips × 8s = ~8 min. Lancer en `background=true` avec `notify_on_complete=true`.
- Le dernier clip peut échouer si le timeout arrive avant la fin du script. Vérifier `ls work/v*.mp4` et convertir manuellement les clips manquants.
