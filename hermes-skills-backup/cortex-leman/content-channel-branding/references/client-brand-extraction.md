# Client Brand Extraction — Workflow

Quand l'utilisateur a déjà un visuel existant (carousel Instagram, flyer, affiche, logo), extraire le code graphique réel plutôt que d'en inventer un nouveau. Utilise quand GLM-5.2 vision est KO (error 1210) et qu'on ne peut pas "voir" le visuel.

## Quand utiliser

- L'utilisateur envoie une photo d'un carousel/poster/flyer existant
- L'utilisateur demande un "code graphique" ou "identité visuelle" mais a déjà des supports
- L'utilisateur dit "on a déjà notre logo/couleurs, je veux juste les formaliser"

## Étape 1 — OCR (texte de marque)

Extraire mission, tagline, slogan, noms de services depuis le visuel client.

```bash
curl -s --max-time 30 -X POST 'https://api.ocr.space/parse/image' \
  -H 'apikey: helloworld' \
  -F 'language=fre' \
  -F 'OCREngine=2' \
  -F 'scale=true' \
  -F "file=@/path/to/client_visual.jpg"
```

- `apikey: helloworld` = free tier (25k req/mois, suffisant)
- `OCREngine=2` = neural engine, meilleur sur fontes stylisées
- `scale=true` = upscale avant OCR (meilleur précision sur petites images)
- **NE PAS utiliser `urllib.request`** — retourne 400/502 (voir pitfall #25 du SKILL.md)

Sortie : `ParsedText` contient tout le texte du visuel (mission, slogan, services, contact).

## Étape 2 — Color Analysis (palette de marque)

Identifier les couleurs dominantes et les couleurs saturées significatives.

```python
from PIL import Image, ImageStat
from collections import Counter

img = Image.open('client_visual.jpg').convert('RGB')

# 2a. Palette globale (top couleurs)
small = img.resize((150, 150))
colors = Counter(small.getdata())
top = colors.most_common(20)

# 2b. Couleurs saturées significatives (non-blanc, non-gris)
pixels = list(img.getdata())
saturated = [(r, g, b) for r, g, b in pixels
             if (max(r,g,b) - min(r,g,b) > 50)
             and not (r > 240 and g > 230 and b > 210)]

# Grouper en buckets de 30 pour éviter le bruit
bucketed = Counter()
for r, g, b in saturated:
    bucketed[(r//30*30, g//30*30, b//30*30)] += 1

for (r, g, b), count in bucketed.most_common(25):
    hex_c = '#{:02x}{:02x}{:02x}'.format(r, g, b)
    print(f'  {hex_c} RGB({r},{g},{b})  count={count}')
```

Patterns typiques à reconnaître :
- **Terracotta/ocre/crème** = marque cuisine/africaine/familiale (ex: Culture en Saveurs)
- **Bleu marine/blanc/or** = marque corporate/premium
- **Vert/marron/crème** = marque bio/nature/artisanat

## Étape 3 — Cross-check et alignement

Comparer la palette extraite avec ce qu'on propose :

1. Si les couleurs extraites correspondent à la proposition → ✅ aligné, utiliser les valeurs exactes extraites
2. Si mismatch → ajuster la proposition aux couleurs réelles du client
3. L'utilisateur ne devrait pas pouvoir distinguer le code graphique formalisé de son visuel original

## Exemple validé — Culture en Saveurs (juil. 2026)

**Input :** carousel Instagram envoyé par Thierry (591×1280px)

**OCR extrait :**
- Nom : CULTURE EN SAVEURS
- Tagline : "Découvrez les cultures africaines à travers la cuisine, le partage et des expériences inoubliables."
- Mission : "Transmettre, rassembler et valoriser la richesse des cultures africaines à travers des expériences gustatives, artistiques et humaines."
- Slogan : "Cuisiner. Partager. Découvrir. Ensemble."
- Services : Atelier cuisine · Créatif · Découverte du continent · Événements culturels · Catering/Street Food
- Zone : Genève et alentours

**Palette extraite (couleurs saturées top) :**
| Hex | RGB | Rôle dans le visuel |
|-----|-----|---------------------|
| `#5A1E00` | (90, 30, 0) | Brun profond — texte fort, titres |
| `#3C1E00` | (60, 30, 0) | Cacao — fond, accents |
| `#D2781E` | (210, 120, 30) | Ocre/orange — highlights, énergie |
| `#F0D2B4` | (240, 210, 180) | Crème/sable — fond, texte inverse |
| `#194104` | (25, 65, 4) | Vert foncé — accents nature |

**Résultat :** la palette proposée initialement (terracotta/ocre/cacao/crème/vert) était alignée. Les valeurs exactes extraites ont été utilisées pour les cards PIL (hook_card, cta_card).
