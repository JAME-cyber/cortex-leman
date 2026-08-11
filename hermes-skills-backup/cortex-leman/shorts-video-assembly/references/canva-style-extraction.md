# Extraction de style graphique Canva → reproduction vidéo

## Quand utiliser

Quand le client a une plaquette/flyer/affiche Canva existante et veut une **vidéo animée cohérente avec ce style** — sans réutiliser les éléments Canva directement (résolution trop faible + licence Canva).

## Contrainte clé: on ne peut PAS réutiliser les éléments Canva

- **Résolution**: une capture Canva typique (591×1280px, ~170KB JPEG) est inutilisable en vidéo 1080×1920 — flou/pixellisé.
- **Licence**: les illustrations et éléments graphiques d'un template Canva sont sous licence Canva (usage design Canva uniquement). Les extraire pour un autre support = violation de licence.

**Solution: reproduire le style, pas extraire les éléments.**

## Workflow (3 étapes)

### 1. Extraction de l'ADN graphique via Qwen 2.5 VL OCR

Envoyer la capture Canva à Qwen 2.5 VL 72B via OpenRouter avec un prompt exhaustif demandant:

- **Transcription exacte** de tous les textes (avec positions: haut/centre/bas)
- **Typographie**: pour chaque bloc → police probable (Montserrat, Poppins, League Spartan, Pacifico...), style (Bold/Regular/Light), taille relative, casse (MAJ/min/mixte), interlignage
- **Couleurs**: chaque couleur dominante avec son code hex approximatif (fond, titres, texte, formes, illustrations)
- **Éléments graphiques**: illustrations, icônes, formes géométriques, motifs décoratifs, avec position et couleurs
- **Structure de page**: grille de mise en page, nombre de zones, alignement, marges, espacement

### Prompt de référence (OCR précis)

```python
prompt = """Tu es un expert en design graphique et OCR. Analyse cette image avec une précision maximale.

1) TRANSCRIPTION EXACTE: Transcris TOUS les textes visibles, mot pour mot, en respectant la casse, la ponctuation et les accents. Indique la position de chaque bloc de texte (haut/centre/bas, gauche/droite).

2) TYPOGRAPHIE: Pour chaque bloc de texte, indique:
- Police probable (nom Canva si possible: Montserrat, Poppins, League Spartan, Pacifico, etc.)
- Style (Bold, Regular, Italic, Light)
- Approximation de la taille relative (très grand, moyen, petit)
- Lettrage (majuscules, minuscules, mixte)
- Interlignage serré ou aéré

3) COULEURS: Liste chaque couleur dominante avec son code hex approximatif.

4) ÉLÉMENTS GRAPHIQUES: Décris chaque illustration, icône, forme géométrique.

5) STRUCTURE DE LA PAGE: Décris la grille de mise en page.

6) NOM DU TEMPLATE CANVA: Si tu reconnais ce template, donne le nom ou les mots-clés.

Sois exhaustif et précis. Réponds en français."""
```

### 2. Validation du brief client

L'ADN graphique extrait doit être validé contre le brief client existant:

- Comparer la palette extraite avec `research/brand_identity.md` (si existe)
- Vérifier que les polices Montserrat + Poppins sont déjà dans `assets/fonts/`
- Le style global (minimaliste, flat, corporate, créatif) doit être noté pour guider les choix motion

### 3. Plan de reproduction (motion graphics + IA)

Reproduire le style en vidéo ne signifie PAS recréer le flyer en vidéo statique. C'est **transposer le langage graphique en motion design**:

| Élément Canva | Reproduction vidéo |
|---|---|
| Palette (#003366, #FF6600, #006600...) | Appliquer sur title cards, bandeaux, transitions, CTA |
| Typographie Montserrat Bold + Poppins | Déjà dans `assets/fonts/` — réutiliser directement |
| Logo circulaire | Animer en fade-in + scale sur intro/signature |
| Formes géométriques (cercles, rectangles) | Motion graphics en PIL ou moviepy (transitions, bandeaux) |
| Illustrations vectorielles | **Ne PAS extraire** — générer en flat vector via IA (GPT Image, Seedream) dans le même style, OU utiliser photos réelles du projet |
| Carte d'Afrique stylisée | Générer une version SVG vectorielle stylisée → animer |
| Bandeaux texte MAJUSCULES | `drawtext` ffmpeg ou PIL avec Montserrat Bold, casse identique |

### 3 critères de réussite

- **Cohérence chromatique**: palette vidéo = palette Canva exacte (mêmes hex)
- **Continuité typographique**: mêmes polices, mêmes casse/graisse que la plaquette
- **Régistre adapté**: si la plaquette est ludique/colorée (ex: Culture en Saveur), la vidéo ne doit pas devenir corporate/sobre — conserver le ton

## Pitfall: analyse visuelle GLM-5.2 KO

GLM-5.2 ne supporte pas la vision (error 1210). Pour l'extraction OCR d'une plaquette:

```python
# Envoyer via OpenRouter Qwen 2.5 VL 72B
import base64, requests, os

with open(img_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

resp = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
    json={
        "model": "qwen/qwen2.5-vl-72b-instruct",  # PAS de suffixe :free → 404
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
        ]}],
        "max_tokens": 4000,
        "temperature": 0.1  # précision OCR maximale
    },
    timeout=120
)
```

Voir aussi `scripts/vision_check.py` (wrapper CLI prêt à l'emploi).

## Référence cas validé

**Culture en Saveur** (juil. 2026):
- Plaquette Canva analysée: Montserrat Bold + Poppins Regular, palette #003366/#FF6600/#006600/#66CCFF, illustrations flat vector, carte Afrique stylisée
- Préférence utilisateur: reprendre le style graphique pour animer la V1 Pro
- Recommendation: reproduire en motion design (palette + fonts + bandeaux), générer nouvelles illustrations IA flat vector dans le même registre, ne pas extraire les éléments Canva
- **Option A validée**: palette swap du script `build_v1pro_final.py` → `build_canva_style.py` (bleu/orange/vert au lieu de terracotta/cream)
- **Priorité alignment**: utilisateur a souligné "c'est surtout l'alignement avec tous les personnages" — la cohérence des personnages entre clips prime sur les couleurs/fonts

## Mapping palette Terracotta → Canva (table de substitution)

| Rôle | Terracotta (avant) | Canva (après) | Usage |
|------|-------------------|---------------|-------|
| Titre principal | `0xA0392B` | `0x003366` | Bandeaux, titres cards |
| Accent/séparateur | `0xB58761` | `0xFF6600` | Lignes, boutons CTA, label box |
| Formes/logo | `0xA0392B` | `0x006600` | Cercles, formes géométriques |
| Fond clair | `0xF5E8D3` | `0xFFFFFF` | Background cards |
| Texte secondaire | `0x492E21` | `0x1A1A1A` | Corps de texte |
| Sous-titres | cream `0xF5E8D3` | `0x66CCFF` | drawtext subtitle color |
| Police titres | PlayfairDisplay | Montserrat Bold | Tous les titres |
| Police corps | Poppins | Poppins (inchangé) | Texte courant |

## Script de palette swap automatisé

```python
#!/usr/bin/env python3
"""Substitue les constantes de couleur dans un script de build vidéo."""
import re
from pathlib import Path

MAPPING = {
    # Anciennes valeurs (Terracotta) → Nouvelles (Canva)
    "0xA0392B": "0x003366",  # TERRA → BLEU_FONCE
    "0xB58761": "0xFF6600",  # OCHRE → ORANGE
    "0xF5E8D3": "0xFFFFFF",  # CREAM → BLANC (attention: blanc pur)
    "0x492E21": "0x1A1A1A",  # CACAO → NOIR
    "PlayfairDisplay": "Montserrat",  # Police titres
    # RGB tuples PIL
    "(0xA0, 0x39, 0x2B)": "(0x00, 0x33, 0x66)",
    "(0xB5, 0x87, 0x61)": "(0xFF, 0x66, 0x00)",
    "(0xF5, 0xE8, 0xD3)": "(0xFF, 0xFF, 0xFF)",
    "(0x49, 0x2E, 0x21)": "(0x1A, 0x1A, 0x1A)",
}

src = Path("scripts/build_v1pro_final.py").read_text()
for old, new in MAPPING.items():
    src = src.replace(old, new)
Path("scripts/build_canva_style.py").write_text(src)
```

⚠️ **Attention**: ce script ne couvre que les constantes de couleur/police. Les **overlays drawtext** (positions, font sizes, bandeau structure) peuvent nécessiter des ajustements manuels — le bleu foncé nécessite plus de contraste que la terracotta sur certains fonds. Toujours valider visuellement après swap.

## Template OCR Qwen pour extraction de style (prompt complet)

```python
prompt = """Tu es un expert en design graphique et OCR. Analyse cette image avec une précision maximale.

1) TRANSCRIPTION EXACTE: Transcris TOUS les textes visibles, mot pour mot, en respectant la casse, la ponctuation et les accents. Indique la position de chaque bloc de texte (haut/centre/bas, gauche/droite).

2) TYPOGRAPHIE: Pour chaque bloc de texte, indique:
- Police probable (nom Canva si possible: Montserrat, Poppins, League Spartan, Pacifico, etc.)
- Style (Bold, Regular, Italic, Light)
- Approximation de la taille relative (très grand, moyen, petit)
- Lettrage (majuscules, minuscules, mixte)
- Interlignage serré ou aéré

3) COULEURS: Liste chaque couleur dominante avec son code hex approximatif.

4) ÉLÉMENTS GRAPHIQUES: Décris chaque illustration, icône, forme géométrique.

5) STRUCTURE DE LA PAGE: Décris la grille de mise en page.

6) NOM DU TEMPLATE CANVA: Si tu reconnais ce template, donne le nom ou les mots-clés.

Sois exhaustif et précis. Réponds en français."""
```
