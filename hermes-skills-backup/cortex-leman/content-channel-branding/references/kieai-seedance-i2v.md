# Kie.ai Seedance 2.0 Fast — Image-to-Video Pipeline (validé juil. 2026)

Pipeline complet pour animer des images statiques (Seedream/FLUX) en clips vidéo via Seedance 2.0 Fast sur Kie.ai. Utilisé pour Culture en Saveur (Shorts marketing 9:16).

## Prérequis

- Clé API Kie.ai (`KIE_API_KEY` dans env)
- `kie_client.py` (`~/african-heroes/scripts/kie_client.py`) — client unifié image+vidéo
- Images sources en PNG/JPG (générées via Seedream, FLUX, ou photos réelles)

## Étape 1: Upload des images (File Upload API)

Seedance nécessite une **URL publique** pour `first_frame_url`. Les fichiers locaux doivent être uploadés d'abord sur `kieai.redpandaai.co`.

**Endpoint**: `POST https://kieai.redpandaai.co/api/file-stream-upload`

```python
import requests

with open("image.png", "rb") as f:
    r = requests.post(
        "https://kieai.redpandaai.co/api/file-stream-upload",
        headers={"Authorization": f"Bearer {api_key}"},
        files={"file": ("image.png", f, "image/png")},
        data={"uploadPath": "images/project", "fileName": "image.png"},
        timeout=60,
    )
# r.json()["data"]["downloadUrl"] → URL publique ( valide 24-72h)
```

**Pitfalls upload**:
- L'endpoint n'est PAS sous `/api/v1/` — c'est `/api/file-stream-upload` directement. Les anciens endpoints `/api/v1/files/upload`, `/api/v1/chat/upload` → 404.
- Upload gratuit, mais fichiers supprimés après 24h-72h
- Le champ à utiliser est `downloadUrl` (pas `fileUrl`)

## Étape 2: Génération vidéo (Seedance 2.0 Fast)

**Endpoint**: `POST https://api.kie.ai/api/v1/jobs/createTask`

```python
payload = {
    "model": "bytedance/seedance-2-fast",
    "input": {
        "prompt": "Children stirring a steaming pot. Steam rises. Natural hand movements. Warm lighting.",
        "first_frame_url": image_url,  # URL de l'étape 1
        "aspect_ratio": "9:16",
        "duration": 5,          # 4-15s
        "resolution": "720p",   # 720p suffit pour Shorts 9:16
        "generate_audio": False,
    }
}
r = requests.post("https://api.kie.ai/api/v1/jobs/createTask",
                  headers=headers, json=payload)
task_id = r.json()["data"]["taskId"]
```

## Étape 3: Polling et download

Même pattern async que Veo/Suno:

```python
# Poll via kie_client.py
task = kc._poll_task(task_id, timeout=600, interval=15)
# → task.result_urls[0] = URL MP3
```

Délai typique: **2-4 min/clip** (plus rapide que Veo 3.1).

## Pricing

| Modèle | Coût | Résolution max |
|---|---|---|
| Seedance 2.0 Fast | **165 crédits/clip** ($0.825) | 720p |
| Seedance 2.0 (Quality) | ~300 crédits | 1080p |

Batch type (5 clips image-to-video): **825 crédits** ($4.13).

## Prompts Seedance — bonnes pratiques

- Décrire le **mouvement** attendu, pas la composition (l'image source définit déjà la composition)
- Spécifier les éléments animés: mains, vapeur, expressions, objets
- Éviter "camera moves" complexes — Seedance excelle sur le mouvement organique (gens, mains, nature)
- Anglais recommandé pour les prompts

Exemples validés (Culture en Saveur):
```
"Children actively cooking. One child stirs a steaming pot of koshari, another sprinkles crispy onions. Steam rises. Hands move naturally. Warm golden lighting."
"Children waving and pointing excitedly at a laptop screen showing a video call. Joyful expressions, natural head and arm movements."
```

## Client unifié `kie_client.py`

Le module `~/african-heroes/scripts/kie_client.py` wrappe tout:

```python
from kie_client import KieClient
kc = KieClient()

# Upload image → get URL → generate video (manuel)
url = upload_image(Path("scene.png"))
kc.gen_video("prompt", out_path="clip.mp4",
             first_frame_url=url, aspect_ratio="9:16",
             duration=5, resolution="720p")
```

## Specs output

Tous les clips Seedance 2.0 Fast produisent:
- Codec: H264
- Résolution: 720×1280 (pour 9:16) ou 1280×720 (pour 16:9)
- FPS: 24
- Durée: configurable (4-15s)
- Pas d'audio par défaut (`generate_audio: false`)

Pour intégration dans un build Shorts, upscaler à 1080×1920 au moment du concat FFmpeg (`scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920`).
