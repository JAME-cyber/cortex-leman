# Video Recutting Workflow — Long → Short (<60s)

Pattern validé août 2026 (Sankofa Histoire : 4 vidéos 79-124s → Shorts <60s).

## Principe

Recouper une vidéo existante (80-120s) en Short YouTube <60s en réassemblant les segments audio + visuels sélectionnés. Ne PAS ré-générer du contenu — réutiliser les assets existants (images, TTS, captions).

## Architecture

Chaque vidéo source a :
- `script_short.json` — segmentation narrative (beats/segments)
- `audio/` — un MP3 TTS par segment (edge-tts HenriNeural)
- `broll/` — images fixes (Seedream/PIL) pour Ken Burns
- `captions/` — PNG transparents (PIL burned, un par segment)
- `build.py` — build script original (80-120s)

Le `build_short.py` crée une version <60s en :
1. Sélectionnant les segments à garder (hook + cœur + CTA)
2. Régénérant un nouveau CTA si l'original contient des références temporelles
3. Réassemblant avec le même pipeline (Ken Burns + captions + BGM + watermark)

## Plan de coupe type (9-10 segments → 5-6)

| Type | Garder | Couper |
|------|--------|--------|
| Hook (seg 0) | ✅ Toujours | — |
| Transition (seg 1) | ⚠️ Si court (<5s) | ✅ Si >8s |
| Nom + contexte (seg 2) | ✅ Toujours | — |
| Détail/contexte (seg 3-4) | ⚠️ 1 seul max | ✅ Les autres |
| Action/climax (seg 5-6) | ✅ Le plus visuel | ✅ L'autre |
| Résolution (seg 7) | ✅ Si court | — |
| CTA (seg 8/9) | ✅ (régénéré) | — |

**Calcul :** Somme des durées audio des segments gardés. Si > 60s, couper un segment de plus.

## Génération nouveau CTA

L'CTA original peut contenir "Demain" ou "la semaine prochaine" — obsolète après recoupe.

```python
import asyncio, edge_tts

async def gen_cta():
    text = "Sankofa. Retourne la chercher. Abonne-toi."
    communicate = edge_tts.Communicate(text, "fr-FR-HenriNeural", rate="-5%")
    await communicate.save("audio/09_cta_short.mp3")

asyncio.run(gen_cta())
```

## build_short.py template

Structure du script de recoupe (voir Mansa Moussa build_short.py pour référence complète) :

```python
# 1. Définir SHORT_BEATS — liste des beats à garder avec mapping audio
SHORT_BEATS = [
    {"id": "01_hook", "image": "01_hook.png", "direction": "zoom_in", "caption_overlay": True},
    {"id": "03_context", "image": "03_context.png", "direction": "zoom_in"},
    # ... (segments sélectionnés)
    {"id": "09_cta", "image": "09_cta.png", "fullscreen": True},
]

AUDIO_MAP = {
    "01_hook": "01_hook.mp3",       # audio original
    "03_context": "03_context.mp3",  # audio original
    "09_cta": "09_cta_short.mp3",    # nouveau CTA régénéré
}

# 2. Pour chaque beat :
#    - ffprobe pour durée audio exacte
#    - Ken Burns sur l'image correspondante
#    - Overlay caption si flag caption_overlay
#    - Ou fullscreen caption si flag fullscreen

# 3. Concat vidéo (concat demuxer)
# 4. Concat audio (concat demuxer)
# 5. Merge vidéo + audio
# 6. BGM + watermark (filter_complex)

# Output: clips/<name>_short.mp4
```

## Délégation parallèle

Pour recouper N vidéos en parallèle, déléguer à des subagents (delegate_task). Chaque subagent :
1. Lit le script_short.json pour comprendre la segmentation
2. Applique le plan de coupe (quels segments garder/couper)
3. Génère le nouveau CTA TTS
4. Crée build_short.py (basé sur le template Mansa Moussa)
5. Exécute le build
6. Vérifie durée <60s et taille raisonnable

**Limite : 3 subagents parallèles** (delegation.max_concurrent_children).

## Validation

Après build :
```bash
ffprobe -v quiet -show_entries format=duration -of csv=p=0 clips/*_short.mp4
# Doit afficher < 60.0
```

QA visuel : extraire 3 frames (25%, 50%, 75%) et analyser via vision-analysis-fallback (Gemini via OpenRouter). Vérifier : captions lisibles, qualité image, watermark visible.

## SEO : titres pour Shorts

Patterns validés :
- **Curiosité + fait** : "Cette reine africaine a humilié l'empire portugais"
- **Question implicite** : "L'homme le plus riche de l'histoire (mythe ou réalité ?)"
- **Choc** : "Elle a sacrifié son enfant pour sauver son peuple"

Ne PAS utiliser `#Shorts` dans le titre (YouTube détecte automatiquement).
