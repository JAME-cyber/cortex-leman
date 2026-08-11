# Extraction contenu YouTube pour analyse

**Méthode fiable éprouvée juillet 2026.**

## Problème

- `rag-web-browser` (Apify) **échoue sur YouTube** : la page rendue sans JS ne retourne
  que le footer générique de YouTube, pas le titre ni la description.
- Le scraping direct de YouTube ne fonctionne pas (SPA lourde, JS obligatoire).

## Solution : oEmbed + yt-dlp

### Étape 1 — Métadonnées via oEmbed (rapide, gratuit, pas de JS)

```python
import httpx

vid = "ciV-FH9zRnQ"  # extraire l'ID de l'URL
r = httpx.get(f"https://www.youtube.com/oembed?url=https://youtu.be/{vid}&format=json")
oembed = r.json()
# → title, author_name, author_url, thumbnail_url, html (iframe embed)
```

**Avantages :** pas d'auth, pas de quota, réponse instantanée.
**Limites :** pas de description longue, pas de transcript.

### Étape 2 — Transcript via yt-dlp

```bash
yt-dlp --write-auto-sub --sub-lang en --skip-download \
  --sub-format vtt -o "/tmp/yt_sub_%(id)s" "https://youtu.be/VIDEO_ID"
```

Puis nettoyage du VTT en Python :

```python
import re

with open("/tmp/yt_sub_VIDEO_ID.en.vtt", "r") as f:
    raw = f.read()

lines = raw.split("\n")
texts = []
seen = set()
for line in lines:
    line = line.strip()
    if not line or "-->" in line or line.startswith("WEBVTT") \
       or line.startswith("Kind:") or line.startswith("Language:") \
       or line.startswith("NOTE"):
        continue
    clean = re.sub(r'<[^>]+>', '', line)           # tags HTML
    clean = re.sub(r'\d{2}:\d{2}\.\d{3}', '', clean)  # timestamps résiduels
    clean = clean.strip()
    if clean and clean not in seen:
        texts.append(clean)
        seen.add(clean)

transcript = " ".join(texts)
transcript = re.sub(r'\s+', ' ', transcript).strip()
```

### Étape 3 (optionnelle) — Auto-sous-titres FR

```bash
yt-dlp --write-auto-sub --sub-lang fr --skip-download ...
```

⚠️ Peut retourner HTTP 429 (rate limit) si on demande FR juste après EN.
Soit attendre, soit utiliser `youtube-transcript-api` (pip) comme alternative.

## Contexte d'usage

Thierry envoie régulièrement des URLs YouTube brutes (sans contexte explicite).
**Ne pas verdict trop vite** — chercher le contexte projet avant d'évaluer la pertinence.

Méthode :
1. Extraire titre + transcript (oEmbed + yt-dlp)
2. Lire le transcript (synthèse en 3-4 piliers)
3. **Chercher le contexte projet** avant de donner un verdict de pertinence
4. Verdict honnête : ce qui est transferable vs ce qui ne s'applique pas

## Outils nécessaires

```bash
# Vérifier présence
which yt-dlp
pip list | grep youtube-transcript-api
```

Si absent : `pip install yt-dlp youtube-transcript-api`
