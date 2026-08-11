# Sankofa Production Patterns — Infographics + Ken Burns + Caption Overlay

Patterns appris lors de la production de la chaîne YouTube "Sankofa Histoire" (août 2026).
Pipeline hybride : infographies PIL auto-portées + hero images Seedream + Ken Burns.

## ⚠ Doublon captions PIL ↔ sous-titres SRT : UN SEUL SYSTÈME

**Problème** : Le build pipeline générait des captions PIL (overlay PNG avec kicker + texte) ET des sous-titres SRT/ASS via ffmpeg `subtitles` filter. Résultat : textes dupliqués, chevauchements illisibles, score QA vision 4-6/10.

**Cause racine** : Deux systèmes de texte indépendants se superposent :
1. **Captions PIL** : overlay PNG avec gradient, kicker (franchise), barre accent, texte centré — brûlé dans l'image via `overlay_caption()`
2. **Sous-titres SRT/ASS** : générés depuis `generate_srt()` puis ajoutés via `subtitles='path.ass'` dans le filter_complex ffmpeg final

Les deux affichent le même texte narratif → l'utilisateur voit deux versions du même texte empilées.

**Règle absolue : UN seul système de texte à l'écran.**

| Situation | Système recommandé |
|-----------|-------------------|
| Broll = image décorative (hero shot, photo) | Captions PIL (gradient + kicker + texte) |
| Broll = infographie auto-portée (contient déjà tout le texte) | **AUCUN overlay** — l'image suffit |
| Vidéo long-form (podcast, 16:9) | SRT/ASS seulement (pas de PIL) |
| Mix infographies + images décoratives | PIL pour images décoratives, RIEN pour infographies |

### Pattern `caption_overlay` flag dans BEATS_CONFIG

```python
BEATS_CONFIG = [
    {"id": "01_hook",        "image": "hero.png",        "caption_overlay": True},   # image décorative → caption PIL
    {"id": "02_context",     "image": "infographic.png", "caption_overlay": False},  # infographie auto-portée → RIEN
    {"id": "03_chart",       "image": "chart.png",       "caption_overlay": False},  # graphique avec labels → RIEN
    {"id": "04_verdict",     "image": "decorative.png",  "caption_overlay": True},   # image décorative → caption PIL
    {"id": "05_cta",         "fullscreen": True},                                    # CTA PIL standalone
]

# Dans la boucle de build :
if beat.get("caption_overlay", False):
    overlay_caption(kb_vid, cap_png, dur, seg)    # Avec overlay PIL
else:
    seg = kb_vid                                    # Sans overlay (Ken Burns seul)
```

### Supprimer le SRT du filter_complex final

```python
# ❌ FAUTIF : PIL captions + SRT subtitles = doublon
f"[0:v][2:v]overlay=...,subtitles='{ass_escaped}'[vout]"

# ✅ CORRECT : PIL captions seulement, pas de SRT
f"[0:v][2:v]overlay=...[vout]"
```

Quand les broll sont des infographies complètes (contenant tout le texte narratif), supprimer entièrement la génération SRT/ASS du pipeline :

```python
# SUPPRIMER ces lignes quand les broll sont auto-portés :
# srt_path = TMP_DIR / "subs.srt"
# generate_srt(srt_data, str(srt_path))
# ass_path = TMP_DIR / "subs.ass"
# srt_to_ass(str(srt_path), str(ass_path))
```

## ⚠ QA vision obligatoire après chaque build

**Score QA cible : ≥7/10 sur chaque frame.**

Extraire 4 frames (début, 1/4, milieu, 3/4) et vérifier via `or_vision.py` (skill `vision-analysis-fallback`) :

```python
from hermes_tools import terminal
import os

script = os.path.expanduser("~/.hermes/skills/devops/vision-analysis-fallback/scripts/or_vision.py")

for t in [2, 15, 40, 60]:
    # Extract frame
    terminal(f"ffmpeg -y -i video.mp4 -ss {t} -frames:v 1 /tmp/qa_{t}s.png -loglevel quiet", timeout=30)
    # QA via OpenRouter Gemini
    r = terminal(f'python3 {script} "/tmp/qa_{t}s.png" "YouTube Short frame QA. Check: 1) Caption text readable? 2) Any duplicate/overlapping text? 3) Rate 1-10. Be concise (3-4 lines)."', timeout=45)
    print(r.get("output", "ERROR"))
```

Si une frame <7/10 : identifier la source du chevauchement (SRT vs PIL vs broll text), corriger, rebuilder.

## ⚠ Ken Burns `zoom_out` peut couper le texte en bordure

**Problème** : Direction `zoom_out` sur une infographie avec label de franchise en haut → le label sort du cadre pendant le zoom.

**Fix** : Pour les images contenant du texte critique en bordure (labels, kickers, titres) :
- Utiliser `zoom_in` (le crop commence large et se reserre → le texte reste visible)
- Ou réduire l'overscale à 1.04 (moins de marge de zoom → moins de déplacement)
- Ou pré-positionner le crop avec un offset Y pour garder le texte dans le safe area

## ⚠ Token OAuth YouTube : `broadcast.goauth` ne contient PAS `client_id`/`client_secret`

**Problème** : Le token OAuth stocké dans `~/.config/youtubeuploader/broadcast.goauth` contient uniquement `{access_token, refresh_token, token_type, expiry}`. Les credentials OAuth (`client_id`, `client_secret`) ne sont PAS inclus.

Le script `scripts/yt_upload.py` utilise `CLIENT_ID = os.environ.get("YT_CLIENT_ID")` qui est vide → le refresh token échoue avec :
```
RefreshError: The credentials do not contain the necessary fields need to refresh the access token.
You must specify refresh_token, token_uri, client_id, and client_secret.
```

**Fix 1 (recommandé) : Charger depuis `client_secret.json`** :

```python
import json
secret_path = "/path/to/client_secret.json"  # Google Cloud Console download
with open(secret_path) as f:
    secret = json.load(f)["installed"]
CLIENT_ID = secret["client_id"]
CLIENT_SECRET = secret["client_secret"]
```

**Fix 2 (googleapiclient — plus robuste pour le refresh automatique)** :

```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

with open(token_path) as f:
    token_data = json.load(f)
with open(secret_path) as f:
    secret = json.load(f)["installed"]

creds = Credentials(
    token=token_data["access_token"],
    refresh_token=token_data["refresh_token"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=secret["client_id"],
    client_secret=secret["client_secret"],
    scopes=["https://www.googleapis.com/auth/youtube.upload"]
)
creds.refresh(Request())  # Auto-refresh

youtube = build("youtube", "v3", credentials=creds)
```

**Approche `googleapiclient` avantage** : Le `MediaFileUpload(resumable=True)` gère automatiquement les retries et la progression. Le `MediaFileUpload` pour thumbnails fonctionne aussi (`youtube.thumbnails().set(videoId=..., media_body=...).execute()`).

## ⚠ Stratégie chaîne YouTube : différenciation concurrentiel

**Contexte** : Un concurrent direct utilise le même nom "Sankofa" avec 1810 abonnés et 22 vidéos. Stratégie de différenciation validée via GPT-5.6 contra-analyse (OpenRouter) :

### Architecture de différenciation
1. **Renommer** : "Sankofa" → "Sankofa Histoire — Archives d'Afrique"
2. **Positionnement** : "Le concurrent raconte, on démontre" (sources, cartes, preuves)
3. **3 franchises identifiables** :
   - LE DOSSIER (personnage complet)
   - MYTHE OU ARCHIVE ? (ce qu'on raconte vs ce que les sources prouvent)
   - LA CARTE RACONTE (géopolitique visuelle)
4. **Labels de transparence** sur chaque vidéo : 📄 ARCHIVE / 🗣️ TRADITION ORALE / 🎨 RECONSTITUTION IA
5. **Format** : 55-75s (plus court que ~120s pour l'algorithme Shorts)
6. **Cadence** : 1 Short/jour, heure fixe 19h30 Paris

### Pipeline budget-conscient (0 clips vidéo T2V)
Quand le budget Kie.ai est limité (<40 crédits) :
- **1 image Seedream** (28cr) pour le hero/hook
- **7+ infographies PIL** (0cr) pour les beats narratifs (cartes, graphiques, sources, verdicts)
- Ken Burns sur toutes les images
- Total : ~28cr par vidéo au lieu de ~200-700cr avec clips Seedance

### Structure narrative 55-75s (5 phases)
| Phase | Durée | Rôle |
|-------|-------|------|
| Hook | 0-8s | Phrase choc + hero image |
| Contexte | 8-25s | Carte + données |
| Renversement | 25-40s | Le détail inattendu |
| Preuve | 40-55s | Source + citation |
| Verdict + CTA | 55-70s | Conclusion + tease vidéo suivante |
