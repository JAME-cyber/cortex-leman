# Qualité vidéo & encodage — Leçons terrain (juil. 2026)

Référence consolidée pour tous les problèmes de qualité vidéo rencontrés sur le pipeline LEC.

## 1. Diagnostic rapide: bitrate et netteté

```bash
# Bitrate d'un MP4 (kbits/s) — en dessous de 800 kbps en 1080p = suspect
br=$(ffprobe -v quiet -show_entries format=bit_rate -of csv=p=0 clip.mp4)
echo "$((br/1000)) kbps"

# Sharpness proxy via PIL (comparer avant/après)
ffmpeg -y -ss 15 -i clip.mp4 -frames:v 1 -q:v 2 /tmp/frame.png 2>/dev/null
python3 -c "
from PIL import Image, ImageStat
img = Image.open('/tmp/frame.png')
stat = ImageStat.Stat(img)
print(f'Sharpness proxy: {sum(stat.stddev):.0f}')
"
```

**Seuils empiriques (Shorts 9:16 1080x1920):**
| Bitrate | Verdict | Action |
|---------|---------|--------|
| >2500 kbps | ✅ Bon | Publier |
| 1000-2500 kbps | ⚠️ Acceptable | OK pour livraison |
| 500-1000 kbps | ❌ Bas | Re-render |
| <500 kbps | ❌ Trop dégradé | Re-render obligatoire (source corrompue) |

## 2. Dégradation multi-pass dans `build_clips.py`

**Problème**: 4 encodages CRF 20 successifs → bitrate final dérisoire (332 kbps), slides texte floues.

**Pipeline original (4 passes lossy)**:
```
build_video_segment (CRF 21) → mux+audio (CRF 20) → subs+BGM (CRF 20) → concat intro/sig (CRF 20)
```

**Pipeline corrigé (3 passes, CRF 18 + stream copy)**:
```
build_video_segment (CRF 18) → mux+audio (-c:v copy) → subs+BGM (CRF 18) → concat intro/sig (CRF 18)
```

**Règle**: le `CRF` est trompeux pour les slides statiques (Ken Burns lent sur image fixe). Le compresseur alloue très peu de bits car il n'y a pas de mouvement → le texte devient flou même avec un CRF "raisonnable". **Surveiller le bitrate final, pas seulement le CRF.**

## 3. Compression Telegram (<50 MB)

### H.264 single-pass: À ÉVITER pour les slides texte
- `900 kbps` H.264 single-pass dégrade gravement les slides
- L'utilisateur le remarque immédiatement ("la netteté s'est dégradée")

### HEVC 2-pass: recommandé
```bash
# Pass 1 (analyse, pas d'output)
ffmpeg -y -i input.mp4 -c:v libx265 -preset medium -b:v 850k \
  -x265-params "pass=1" -an -f null /dev/null

# Pass 2 (encodage final)
ffmpeg -y -i input.mp4 -c:v libx265 -preset medium -b:v 850k \
  -x265-params "pass=2" -pix_fmt yuv420p -c:a aac -b:a 96k output_HEVC.mp4
```

- HEVC ~40% plus efficace que H.264 à qualité égale
- 850 kbps HEVC ≈ 1400 kbps H.264 en netteté perçue
- Temps: 15-20 min pour 7 min de 1080p (`preset medium`)
- Lancer en `background=true, notify_on_complete=true`

## 4. Règles générales d'encodage LEC

1. **Minimiser les re-encodages** intermédiaires: `-c:v copy` ou lossless (`-c:v ffv1`) entre étapes
2. **CRF 18** minimum pour tout passage lossy (pas 20-23)
3. **Vérifier le bitrate final**, pas seulement le CRF — surtout pour contenu statique
4. **HEVC pour livraison Telegram**, H.264 pour YouTube (compatibilité)
5. **2-pass** pour tout contenu >3 min où la taille compte
6. **Audio**: `aac -b:a 96k` suffit pour voix + BGM faible

## 5. Validation empirique (juil. 2026)

### Fix CRF 18 + stream copy (Clips B et C)
Appliqué sur `build_clips.py`. Mesures sharpness proxy avant/après:

| Clip | Bitrate avant | Bitrate après | Sharpness avant | Sharpness après |
|------|------------|------------|----------------|----------------|
| Clip B | 342 kbps | 368 kbps | 74 | **97** (+31%) |
| Clip C | 332 kbps | 364 kbps | 109 | 110 (stable) |

Le bitrate reste bas (~370 kbps) car les slides sont quasi-statiques, mais la netteté du texte s'améliore significativement grâce au CRF 18 + moins de passes lossy. **Le sharpness proxy confirme ce que l'œil voit** — ne pas se fier au bitrate seul pour juger la qualité des slides.

### Compression HEVC 2-pass (video2 CoreWeave)
- Source: 158 MB (H.264, 3065 kbps, 7min12s, 1080p)
- H.264 single-pass 900k: ~50 MB mais **rejeté par l'utilisateur** (texte flou)
- HEVC 2-pass 850k: **48 MB** (sous limite Telegram), netteté préservée
- Temps render: ~31 min (2-pass, preset medium, background)

**Conclusion**: HEVC 2-pass est le standard pour livraison Telegram de vidéos LEC longues. Le H.264 single-pass est inacceptable pour le contenu texte-heavy.

## 6. Batch QC: vérifier tous les shorts quand un problème est détecté

**Leçon** (juil. 2026, USER CORRECTION): quand l'utilisateur remarque un problème de qualité sur une vidéo (ex: "la netteté s'est dégradée"), **ne pas se limiter à cette vidéo**. L'utilisateur demande immédiatement: "il faut s'assurer que les shorts ne soient pas comme la video2". 

**Procédure de batch QC** — exécuter dès qu'un problème qualité est signalé:
```bash
# Vérifier bitrate de TOUS les shorts du catalogue
for f in /home/tars/crypto-project/CHANNEL/video*/renders/*.mp4 \
         /home/tars/crypto-project/CHANNEL/video3/clips/clip*_FINAL.mp4; do
  br=$(ffprobe -v quiet -show_entries format=bit_rate -of csv=p=0 "$f")
  echo "$((br/1000)) kbps | $(basename $f)"
done | sort -n
```

**Seuils d'alerte** (voir section 1):
- Tout Short <800 kbps doit être flaggé et investigué
- Comparer avec un clip de référence sain (ex: video5 ASML = 1714 kbps = bonne qualité validée par utilisateur)

Ne pas attendre que l'utilisateur signale chaque vidéo défectueuse — **proactivement scanner le batch entier** dès qu'un problème est confirmé sur une unité.
