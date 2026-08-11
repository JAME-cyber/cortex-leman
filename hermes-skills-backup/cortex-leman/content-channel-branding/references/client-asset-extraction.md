# Client Asset Extraction — Linktree UGC CDN

## Le problème

Les pages Facebook et Instagram des associations/petites entreprises sont **login-gated**. Impossible de récupérer photos ou logo via curl ou navigateur sans session authentifiée. Le Canva link est protégé par Cloudflare.

## La solution : Linktree UGC CDN

Le Linktree d'une organisation expose dans son DOM :
- Le **logo officiel** (souvent en HD, PNG transparent)
- Des **photos réelles** d'événements/activités
- Liens vers Weezevent (billetterie), Canva, etc.

Le CDN Linktree (`ugc.production.linktr.ee`) est **accessible sans authentification**.

### Étapes d'extraction

1. **Naviguer le Linktree** : `browser_navigate("https://linktr.ee/<username>")`
2. **Lister les images du DOM** : `browser_get_images` retourne URLs + alt text
3. **Identifier les assets pertinents** :
   - Logo : généralement le plus grand fichier PNG, ratio carré
   - Photos : fichiers JPEG, souvent avec date dans le nom (`IMG-20251113-*`)
4. **Télécharger avec curl** : `curl -sL --max-time 25 "<url>" -o <output>`

### URLs avec suffixes de taille

Le CDN Linktree supporte les transformations via query params :

```
https://ugc.production.linktr.ee/<uuid>_<filename>.jpeg?io=true&size=thumbnail-feature-v1_0
```

| Suffixe | Usage |
|---------|-------|
| (aucun) | Full resolution (peut timeout sur gros fichiers) |
| `?io=true&size=thumbnail-feature-v1_0` | Thumbnail (75KB, rapide) |

**Stratégie :** télécharger d'abord le thumbnail pour valider le contenu, puis le full-res pour la production.

### Timeout curl

Les photos smartphone full-res (3-12MB) peuvent timeout à 30s. Utiliser `--max-time 25` et `--connect-timeout 10`. Si échec, réessayer avec le suffixe thumbnail.

## Format HEIC

Certains smartphones (HONOR TFY-LX1, iPhone récents) uploadent en **HEIC/HEIF**. Ces fichiers ont une extension `.jpeg` mais ne sont PAS des JPEG — PIL échoue avec une erreur obscure.

### Détection

```python
from PIL import Image
img = Image.open("photo.jpeg")
# OSError: cannot identify image file  ← c'est du HEIC déguisé
```

Ou via `file` :
```bash
file photo.jpeg
# photo.jpeg: data  ← pas "JPEG image data"
```

### Conversion

```bash
# Installer pillow-heif dans le venv Hermes
VIRTUAL_ENV=/home/tars/.hermes/hermes-agent/venv uv pip install pillow-heif
```

```python
import pillow_heif
pillow_heif.register_heif_opener()
from PIL import Image

img = Image.open("photo.heic.jpeg")  # PIL l'ouvre maintenant comme HEIF
img.convert("RGB").save("photo.jpg", "JPEG", quality=95)
```

**Note :** `uv pip install` par défaut cible Python 3.12. Pour le venv Hermes (3.11), utiliser `VIRTUAL_ENV=<path> uv pip install`.

## Logo : optimisation pour HTML/Playwright

Les logos PNG HD (1200×1200, RGBA) sont trop lourds pour embarquer dans un HTML d'intro animée :

| Format | Taille base64 (400×400) |
|--------|------------------------|
| PNG optimize | ~349 KB |
| JPEG q90 (flatten sur bg) | ~76 KB |

**Pipeline d'optimisation :**

```python
import base64
from PIL import Image
from io import BytesIO

img = Image.open("logo.png").convert("RGBA").resize((400, 400), Image.LANCZOS)

# Flatten sur background correspondant au design
bg = Image.new("RGB", (400, 400), (253, 246, 238))  # crème
bg.paste(img, mask=img.split()[3])

buf = BytesIO()
bg.save(buf, format="JPEG", quality=90, optimize=True)
b64 = f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"
```

## QA sans vision (GLM-5.2 erreur 1210)

GLM-5.2 ne supporte pas la vision (erreur 1210). Pour valider le contenu d'une frame vidéo ou d'un asset :

1. **PIL ImageStat** : brightness, stddev, extrema pour détecter les problèmes (frame noire, texte manquant)
2. **OCR.space API** : `curl -X POST https://api.ocr.space/parse/image` avec `apikey: helloworld`, `language: eng` (pas `fr`), `OCREngine: 2`. Gratuit, zero-install. Extrait le texte de n'importe quelle image.
3. **Livrer au user** : pour validation visuelle humaine finale.
