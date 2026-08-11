# FFmpeg zoompan centré + Sous-titres ASS lisibles

Deux pièges techniques récurrents dans l'assemblage vidéo 9:16, corrigés session juil. 2026 (T2 Visio, Culture en Saveur).

## 1. zoompan décentré (zoome en haut-gauche)

### Problème
Le filtre `zoompan` de FFmpeg zoome par défaut vers le coin **haut-gauche** (`x=0, y=0`). Sur une image 1080x1920, le résultat est un zoom qui "fuit" vers le coin supérieur gauche, laissant des zones vides en bas/droite et coupant le sujet centré.

### Solution: coordonnées x/y dynamiques centrées
```python
frames = int(target_dur * FPS)
vf = (
    f"scale=1188:2112:force_original_aspect_ratio=increase,crop=1080:1920,"
    f"zoompan=z='min(zoom+0.0012,1.12)':"
    f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
    f"d={frames}:s=1080x1920:fps={FPS},format=yuv420p"
)
```

**Points clés:**
- `x='iw/2-(iw/zoom/2)'` — centre horizontal dynamique qui suit le zoom
- `y='ih/2-(ih/zoom/2)'` — centre vertical dynamique
- `zoom+0.0012` par frame, plafonné à `1.12` — zoom subtil (12% max), pas agressif
- Toujours pré-scaler l'image plus grande que la cible (`1188x2112` pour `1080x1920`) avant zoompan, sinon pixels visibles

### Erreur classique: zoom trop rapide
```python
# ❌ TROP RAPIDE — zoom visible et agressif
zoompan=z='min(zoom+0.005,1.5)'

# ✅ SUBTLE — Ken Burns doux
zoompan=z='min(zoom+0.0012,1.12)'
```

---

## 2. Sous-titres ASS: débordement d'écran

### Problème
Les phrases VO longues (ex: 12s, 20+ mots) s'affichent sur une seule ligne en ASS et dépassent largement de l'écran 1080px de large. Texte illisible → rejet utilisateur.

### Solution A: Sauts de ligne manuels `\N`

ASS utilise `\N` (backslash-N majuscule) pour forcer un retour à la ligne. Découper les phrases longues en segments de ~30 caractères:

```python
# Texte TTS PROPRE (sans \N) pour edge-tts
VO_SEGMENTS = [
    ("vo_02", "Ici, chaque enfant a sa place. La petite Amina et son voile, le petit Maxime et sa curiosité."),
]

# Texte sous-titres avec \N pour ASS
SUB_TEXT = {
    "vo_02": r"Ici, chaque enfant a sa place.\N La petite Amina et son voile,\N le petit Maxime et sa curiosité.",
}
```

### ⚠️ Piège Python: `\N` est un escape Unicode
En Python, `\N{...}` est réservé aux caractères Unicode nommés. Pour utiliser `\N` littéral dans une string Python:

```python
# ❌ ERREUR: SyntaxError (unicode escape)
text = "ligne1\N ligne2"

# ✅ CORRECT: raw string
text = r"ligne1\N ligne2"
```

### Solution B: Séparer TTS et sous-titres
Le texte VO pour `edge-tts` doit être **propre** (pas de `\N`, pas de balises). Mais le texte ASS a besoin des `\N`. Maintenir **deux dictionnaires séparés**:

```python
# Pour TTS (clean)
for name, text in VO_SEGMENTS:
    edge_tts(text)

# Pour ASS (avec \N)
for name, text in VO_SEGMENTS:
    sub_text = SUB_TEXT.get(name, text)  # fallback: clean text
    subs_lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{sub_text}")
```

### Solution C: Réduire la taille de police
Pour les vidéos avec beaucoup de texte (ex: segment inclusion 12s), réduire la police ASS:
```
# ❌ Trop grand pour phrases longues
Fontsize: 44

# ✅ Lisible même avec 3-5 lignes
Fontsize: 38
```

---

## 3. Ancrage géographique des prompts Seedance (CRITIQUE)

### Problème
Les modèles vidéo IA (Seedance) **défault vers un décor générique correspondant au thème** du prompt. Un prompt décrivant "cuisine africaine" génère une rue africaine, même si l'événement se passe à Genève. L'utilisateur a corrigé explicitement: "C'était une street food africain mais au Petit-Lancy, Genève".

### Règle: TOUJOURS spécifier le lieu réel dans le prompt
Le prompt doit contenir:
1. **Le lieu réel** ("in Petit-Lancy, Geneva, Switzerland")
2. **Les marqueurs visuels du décor local** ("clean paved Swiss plaza", "Geneva-style residential buildings", "Swiss traffic signs")
3. **Le negative prompt anti-décor-générique** ("no African slum setting, no tropical background")

### Exemple corrigé (Petit-Lancy)
```python
# ❌ GÉNÉRIQUE — Seedance génère une rue africaine
prompt = "African street food kiosk with a woman preparing food..."

# ✅ ANCRÉ — décor suisse explicite
prompt = """Street food kiosk set up in a Swiss urban square in Petit-Lancy,
Geneva, Switzerland. Swiss-style residential buildings and trees visible
in the background. Clean paved plaza, Swiss traffic signs.
The kiosk is painted in warm terracotta red...
...No African slum setting, no tropical background."""
```

### Checklist avant soumission Seedance
- [ ] Le lieu physique réel est nommé dans le prompt
- [ ] Les marqueurs visuels du lieu (architecture, végétation, signalisation) sont décrits
- [ ] Le negative prompt exclut le décor générique alternatif

Testé Culture en Saveur Catering V3b (juil 2026): clips régénérés avec décor Genevois après correction utilisateur.

---

## 4. Alignement audio cross-vidéo

### Problème
Quand plusieurs vidéos d'une même campagne utilisent des musiques différentes, la cohérence sonore est rompue. L'utilisateur l'entend immédiatement.

### Règle
Toutes les vidéos d'une même campagne/brand doivent partager la **même musique de fond**. Identifier la piste de référence (ex: `afroswing_v2.mp3`) et l'utiliser partout.

### Workflow
1. Identifier la vidéo "maîtresse" (souvent la plus longue/complète)
2. Extraire le nom du fichier musique utilisé dans son build script
3. Remplacer dans tous les autres build scripts de la même campagne
4. Re-render

Testé Culture en Saveur (juil 2026): teaser aligné sur `afroswing_v2.mp3` après livraison T2.

---

## 5. Anti-loop: clips variés par segment

### Problème
Recycler le même clip N fois (ex: `visio_orphelinat.mp4` joué 3x avec setpts stretch) donne une impression de **vidéo qui tourne en boucle**. L'utilisateur le remarque immédiatement et le rejette.

### Règle
Chaque segment visuel doit avoir une source **différente**. Si pas assez de clips:
1. Générer de nouveaux clips via Seedance (prévoir le budget crédits)
2. Utiliser des clips existants d'autres thématiques (ex: `le_nil.mp4` pour un segment "pont culturel")
3. Créer des cartes illustrées (PIL ImageDraw) avec zoompan pour combler

### Template d'allocation clips
```python
segments = [
    ("intro",     3.0,  intro_steam_spice),        # asset existant
    ("title",     4.0,  wax_title_card),            # PIL généré
    ("visio",     6.0,  S/"visio_classroom.mp4"),   # Seedance nouveau
    ("inclusion", 12.0, S/"inclusion_cooking.mp4"), # Seedance nouveau
    ("pont",      5.0,  V/"le_nil.mp4"),            # asset existant différent
    ("cta",       9.0,  end_card_v2),               # PIL/image existant
]
# Règle: ZERO source en double dans cette liste
```

---

## 6. ffprobe `dur()` parsing — utiliser JSON, pas CSV

### Problème
La fonction `dur()` qui récupère la durée d'un fichier audio/vidéo via ffprobe peut retourner 0.0s silencieusement si le parsing échoue. Le format CSV (`-print_format csv`) parse `duration="X"` avec un split sur guillemets qui casse selon les versions ffprobe ou les conteneurs (MP3 notamment).

Conséquence : les segments VO sont générés (fichiers .mp3 présents avec la bonne taille) mais `durations[name]` retourne 0 → segments vidéo à durée nulle → crash ou vidéo blanche.

### Solution: toujours parser en JSON
```python
def dur(path):
    r = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json',
                        '-show_format', str(path)], capture_output=True, text=True)
    import json
    try:
        data = json.loads(r.stdout)
        return float(data['format']['duration'])
    except:
        return 0
```

Testé juil. 2026 (build_aout1.py) : les fichiers MP3 générés par edge-tts retournaient `0.0s` en CSV parsing mais `7.656s` en JSON parsing.

---

## 7. Compression TG adaptative selon durée

Règle empirique (testée juil. 2026, Culture en Saveur, 8 vidéos) :

| Durée vidéo | Strategy compression | Taille cible |
|-------------|----------------------|--------------|
| <30s | CRF 26, scale 720×1280, audio 128k | <4MB |
| 30-45s | CRF 28, scale 720×1280, audio 128k | <4MB |
| 45-55s | CRF 30, scale 540×960, audio 96k | <5MB |
| 55s+ | CRF 30, scale 540×960, audio 96k, maxrate 2000k | <5MB |

Commande heavy pour 50s+ :
```bash
ffmpeg -y -i input.mp4 -c:v libx264 -crf 30 -maxrate 2000k -bufsize 4000k \
  -preset fast -vf "scale=540:960" -c:a aac -b:a 96k \
  -movflags +faststart output_TG.mp4
```

Une vidéo de 55s à 17.4MB passe à 4.3MB avec cette recette, sans perte de lisibilité mobile.
